#!/usr/bin/env python3
"""
00_validate_structure.py — valida que el filesystem coincide con
docs/FOLDER_STRUCTURE_TRUTH.md.

Uso:
    python scripts/build/00_validate_structure.py [--strict]

Exit codes:
    0 — OK
    1 — archivos declarados ausentes
    2 — naming incorrecto detectado
"""

import re
import sys
from pathlib import Path

# SPR-F-CLEAN-P2a: parser SYSTEMS_INDEX para mapping path→fase.
# sys.path.insert garantiza que el sibling module resuelve sin importar desde
# qué cwd se invoque el validador.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _systems_index_parser import parse_systems_index, parse_truth_exemptions

# SPR-001-FIX-3: forzar UTF-8 en stdout/stderr para que el validador imprima
# limpio en cualquier consola Windows (cp1252 por defecto) sin requerir
# `chcp 65001` ni `PYTHONIOENCODING=utf-8`. Defensivo: si reconfigure no
# aplica (pipe, entorno raro) ignoramos.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
TRUTH = ROOT / "docs" / "FOLDER_STRUCTURE_TRUTH.md"

# Regex de naming
NAMING_RULES = {
    "data": re.compile(r"^[a-z][a-z0-9_]*\.json$"),
    "Verse": re.compile(r"^[A-Z][A-Za-z0-9]*\.verse$"),
    # SPR-009-PRE-010: smoke tests Verse en Content/Verse/Tests/ con naming snake_case test_*.verse
    "Verse_tests": re.compile(r"^test_[A-Za-z0-9_]+\.verse$"),
    # SPR-010-TRUTH-FIX: throwaways canary en Content/Verse/Tests/canary/ con naming throwaway_*.verse
    # (TRUTH §1.1 fila "Throwaways canary" + §4.2.1). Audit trail empírico P5 (CHANGELOG B1.1-fix L4).
    "Verse_canary": re.compile(r"^throwaway_[A-Za-z0-9_]+\.verse$"),
    "Generated": re.compile(r"^[A-Z][A-Za-z0-9]*_Generated\.verse$|^ModuleRegistryConstants\.verse$|^EventBusDevice\.verse$"),
    "scripts_build": re.compile(r"^\d{2}_[a-z][a-z0-9_]*\.py$"),
    # SPR-F-CLEAN-P2a: helpers sibling en scripts/build/ con prefijo "_" (módulos
    # importados por scripts NN_*, no son pipeline steps numerados).
    "scripts_build_helper": re.compile(r"^_[a-z][a-z0-9_]*\.py$"),
    # SPR-009-PRE-010: subdir scripts/build/tests/ con naming pytest (test_*.py + __init__.py)
    "scripts_build_tests": re.compile(r"^test_[a-z][a-z0-9_]*\.py$|^__init__\.py$"),
    # SPR-F-CLEAN-P2a: fixtures markdown para tests parser SYSTEMS_INDEX.
    "scripts_build_tests_fixtures_md": re.compile(r"^[a-z][a-z0-9_]*\.md$"),
    "docs": re.compile(r"^[A-Z][A-Z0-9_]*\.md$|^README\.md$"),
    # SPR-207-FIX-1: daily logs en docs/dailylog/ siguen su propia regla
    # (TRUTH §1.1 fila "Daily logs" + §6.2). DL_<fecha>_SPR-<tokens>_<autor>.md
    "docs_dailylog": re.compile(r"^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$"),
    # SPR-009-PRE-010: postmortems en docs/postmortems/ siguen naming PM-<id>.md
    # (TRUTH §1.1 fila "Postmortems" + §6.3). Formato commiteado, referenciado por POSTMORTEMS_INDEX.md.
    "docs_postmortems": re.compile(r"^PM-[A-Za-z0-9_-]+\.md$"),
}

# SPR-009-PRE-010: ignore patterns para rglob — bytecode Python no source-controlled
# (.gitignore L29-30 cubre __pycache__/ y *.pyc, pero rglob escanea filesystem).
# SPR-F-CLEAN-P2a: añadido "_throwaway" — carpeta gitignored para verificadores
# ad-hoc (D-A14, WORKFLOW §3.5). El validador estructural debe ignorarla.
IGNORED_DIRS = {"__pycache__", "_throwaway"}
IGNORED_SUFFIXES = {".pyc"}


def _is_ignored(p: Path) -> bool:
    if p.suffix in IGNORED_SUFFIXES:
        return True
    return any(part in IGNORED_DIRS for part in p.parts)


def docs_rule_for(rel_posix: str) -> str:
    """Selecciona regla aplicable a un archivo dentro de docs/.
    docs/dailylog/* → regla DL. docs/postmortems/* → regla PM. docs/* raíz → regla SCREAMING_SNAKE."""
    if rel_posix.startswith("docs/dailylog/"):
        return "docs_dailylog"
    if rel_posix.startswith("docs/postmortems/"):
        return "docs_postmortems"
    return "docs"


def scripts_build_rule_for(rel_posix: str) -> str:
    """Selecciona regla aplicable a un archivo dentro de scripts/build/.
    scripts/build/tests/fixtures/*.json → regla data (snake_case JSON).
    scripts/build/tests/fixtures/*.md → regla scripts_build_tests_fixtures_md.
    scripts/build/tests/*.py → scripts_build_tests.
    scripts/build/_*.py → scripts_build_helper (módulos sibling importados).
    scripts/build/*.py raíz → scripts_build (NN_*.py)."""
    if rel_posix.startswith("scripts/build/tests/fixtures/"):
        if rel_posix.endswith(".md"):
            return "scripts_build_tests_fixtures_md"
        return "data"
    if rel_posix.startswith("scripts/build/tests/"):
        return "scripts_build_tests"
    # SPR-F-CLEAN-P2a: helper sibling con prefijo "_" (no NN_ pipeline step).
    name = rel_posix.rsplit("/", 1)[-1]
    if name.startswith("_") and name.endswith(".py"):
        return "scripts_build_helper"
    return "scripts_build"


def verse_tests_rule_for(rel_posix: str) -> str:
    """Selecciona regla aplicable a un archivo dentro de Content/Verse/Tests/.
    Tests/canary/throwaway_*.verse → regla Verse_canary. Tests/test_*.verse → Verse_tests."""
    if rel_posix.startswith("Content/Verse/Tests/canary/"):
        return "Verse_canary"
    return "Verse_tests"


def parse_truth_paths(md_text: str) -> list[str]:
    """Extrae paths de los bloques ``` SIN lenguaje de §3, §4, §5, §6.

    Estado del parser (SPR-001-FIX-2):
    - State machine de 3 estados: ``outside`` / ``in_tree`` / ``in_other``.
      Antes había un único bool ``in_tree`` que confundía el cierre de un bloque
      con lenguaje (p. ej. ``` ```python ... ``` ```) con la apertura de un
      bloque tree bare, porque ambos cierres son `` ``` `` desnudo. Resultado:
      las líneas tras el cierre de un bloque python se procesaban como árbol
      (causaba falsos positivos `1.`, `2.`, ... de listas numeradas en §9).
    - Filtros adicionales en el registro:
      * Línea con name == ``ProjectRoot`` → marcador pedagógico del árbol §2,
        se hace transparente (no se push al stack ni se registra).
      * Names con ``<`` o ``>`` → placeholders (ej. `DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md`).
      * Names que solo son numeración de lista (regex ``\\d+\\.``) - defensa adicional.
    """
    paths = set()
    state = "outside"  # outside | in_tree | in_other
    current_indent: list[tuple[int, str]] = []  # stack de (indent, name)
    for line in md_text.splitlines():
        if line.startswith("```"):
            fence_lang = line[3:].strip()
            if state == "outside":
                state = "in_tree" if fence_lang == "" else "in_other"
                current_indent = []
            else:
                # cualquier fence (bare o con lenguaje) cierra el bloque actual
                state = "outside"
                current_indent = []
            continue
        if state != "in_tree":
            continue
        cleaned = re.sub(r"^[│├└─\s]+", "", line)
        if not cleaned or cleaned.startswith("#") or cleaned.startswith("←"):
            continue
        indent = len(line) - len(line.lstrip("│├└─ "))
        name = cleaned.split()[0].rstrip("/")
        # ProjectRoot = marcador del árbol §2; transparente en stack y registro
        if name == "ProjectRoot":
            continue
        # Numeración suelta (`1.`, `2.`, ...) — defensa contra listas numeradas
        # mal-encerradas en bloques code (cubierto por el state machine ya, pero
        # belt-and-braces).
        if re.fullmatch(r"\d+\.", name):
            continue
        # Placeholders con angle brackets — no son rutas reales
        if "<" in name or ">" in name:
            continue
        while current_indent and current_indent[-1][0] >= indent:
            current_indent.pop()
        full = "/".join(p[1] for p in current_indent) + ("/" if current_indent else "") + name
        current_indent.append((indent, name))
        if "." in name:
            paths.add(full)
    # SPR-F-CLEAN-P2b-fix: orden determinista (drift #11 §2.4) — set() iteration
    # no-determinista entre runs causa output validador inestable.
    return sorted(paths)

def validate(strict: bool = False, allow_missing: bool = False, phase: str | None = None, no_truncate: bool = False) -> int:
    if not TRUTH.exists():
        print(f"[FAIL] No existe {TRUTH}", file=sys.stderr)
        return 1

    declared = parse_truth_paths(TRUTH.read_text(encoding="utf-8"))
    print(f"[INFO] {len(declared)} paths declarados en TRUTH")

    missing, bad_naming, undeclared = [], [], []
    missing_future_phase: list[str] = []
    missing_unmapped: list[str] = []

    # 1) MISSING: declarados que no existen
    for rel in declared:
        if not (ROOT / rel).exists():
            missing.append(rel)

    # SPR-F-CLEAN-P2a: filtro por fase via SYSTEMS_INDEX mapping
    # SPR-F-CLEAN-P2b: además filtro exenciones de TRUTH §10 (infra tooling).
    if phase is not None:
        try:
            systems_mapping = parse_systems_index(ROOT / "docs" / "SYSTEMS_INDEX.md")
        except Exception as e:
            print(f"[FAIL] No se pudo parsear SYSTEMS_INDEX.md: {e}", file=sys.stderr)
            return 4
        try:
            truth_exemptions = parse_truth_exemptions(TRUTH)
        except Exception as e:
            print(f"[FAIL] No se pudo parsear TRUTH §10 exemptions: {e}", file=sys.stderr)
            return 4
        filtered_missing: list[str] = []
        for m in missing:
            if m in truth_exemptions:
                # Path exento de SYSTEMS_INDEX (§10 TRUTH) — no entra ni en MISSING ni UNMAPPED.
                continue
            path_phase = systems_mapping.get(m)
            if path_phase is None:
                missing_unmapped.append(m)
            elif path_phase == phase:
                filtered_missing.append(m)
            else:
                missing_future_phase.append(m)
        missing = filtered_missing

    # 2) BAD_NAMING: archivos del repo en zonas reguladas
    for folder, rule_key in [
        ("data", "data"),
        ("Content/Verse/Systems", "Verse"),
        ("Content/Verse/Core", "Verse"),
        ("Content/Verse/Devices", "Verse"),
        ("Content/Verse/Generated", "Generated"),
        ("Content/Verse/Tests", "Verse_tests"),
        ("scripts/build", "scripts_build"),
        ("docs", "docs"),
    ]:
        base = ROOT / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                if p.name == '.gitkeep':
                    continue
                if _is_ignored(p):
                    continue
                rel_posix = p.relative_to(ROOT).as_posix()
                # SPR-207-FIX-1: en docs/, regla por path (raíz vs dailylog/ vs postmortems/)
                # SPR-009-PRE-010: en scripts/build/, regla por path (raíz vs tests/ vs tests/fixtures/)
                if folder == "docs":
                    key = docs_rule_for(rel_posix)
                elif folder == "scripts/build":
                    key = scripts_build_rule_for(rel_posix)
                elif folder == "Content/Verse/Tests":
                    key = verse_tests_rule_for(rel_posix)
                else:
                    key = rule_key
                if not NAMING_RULES[key].match(p.name):
                    bad_naming.append(rel_posix)

    # 3) UNDECLARED: warning
    for folder in ["data", "Content/Verse", "scripts", "docs"]:
        base = ROOT / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                if p.name == '.gitkeep':
                    continue
                if _is_ignored(p):
                    continue
                rel = p.relative_to(ROOT).as_posix()
                # SPR-207-FIX-1: docs/dailylog/DL_*.md están implícitamente declarados
                # vía pattern (TRUTH §6.2 los trata como "contenedor de DL_*").
                if rel.startswith("docs/dailylog/") and NAMING_RULES["docs_dailylog"].match(p.name):
                    continue
                # SPR-009-PRE-010: docs/postmortems/PM-*.md están implícitamente declarados
                # vía pattern (TRUTH §6.3 los trata como "contenedor de PM-*").
                if rel.startswith("docs/postmortems/") and NAMING_RULES["docs_postmortems"].match(p.name):
                    continue
                # SPR-009-PRE-010: scripts/build/tests/test_*.py + __init__.py + fixtures/*.json
                # implícitamente declarados (TRUTH §5.2 los trata como "contenedor de tests pytest").
                # SPR-F-CLEAN-P2a: fixtures/*.md también implícitos (fixtures markdown para
                # tests que parsean docs, ej. SYSTEMS_INDEX).
                if rel.startswith("scripts/build/tests/"):
                    if rel.startswith("scripts/build/tests/fixtures/"):
                        if NAMING_RULES["data"].match(p.name):
                            continue
                        if NAMING_RULES["scripts_build_tests_fixtures_md"].match(p.name):
                            continue
                    if NAMING_RULES["scripts_build_tests"].match(p.name):
                        continue
                # SPR-F-CLEAN-P2a: helpers sibling scripts/build/_*.py implícitos
                # (consumed by NN_*.py pipeline steps — internal modules).
                if rel.startswith("scripts/build/") and "/" not in rel[len("scripts/build/"):]:
                    if NAMING_RULES["scripts_build_helper"].match(p.name):
                        continue
                # SPR-009-PRE-010: Content/Verse/Tests/test_*.verse implícitamente declarados
                # (TRUTH §4.2 los trata como "contenedor de smoke tests Verse").
                # SPR-010-TRUTH-FIX: Content/Verse/Tests/canary/throwaway_*.verse también
                # implícitamente declarados (TRUTH §4.2.1 audit trail P5).
                if rel.startswith("Content/Verse/Tests/"):
                    if rel.startswith("Content/Verse/Tests/canary/") and NAMING_RULES["Verse_canary"].match(p.name):
                        continue
                    if NAMING_RULES["Verse_tests"].match(p.name):
                        continue
                if rel not in declared:
                    undeclared.append(rel)

    # Reporte
    # SPR-F-CLEAN-P2a-fix: helper para truncado condicional (drift #10 §2.4).
    # Sin --no-truncate, comportamiento idéntico al previo (20/10 entries).
    def _print_list(items: list[str], default_limit: int) -> None:
        limit = None if no_truncate else default_limit
        shown = items if limit is None else items[:limit]
        for item in shown:
            print(f"   {item}")
        if limit is not None and len(items) > limit:
            print(f"   ... y {len(items) - limit} mas")

    if missing:
        label = "[WARN] MISSING (ignorado por --allow-missing)" if allow_missing else "[FAIL] MISSING"
        print(f"\n{label} ({len(missing)}):")
        _print_list(missing, 20)
    if bad_naming:
        print(f"\n[FAIL] BAD_NAMING ({len(bad_naming)}):")
        for b in bad_naming:
            print(f"   {b}")
    if undeclared:
        print(f"\n[WARN] UNDECLARED ({len(undeclared)}):")
        _print_list(undeclared, 20)
    if missing_future_phase:
        print(f"\n[INFO] MISSING en fases futuras (ignorado por --phase={phase}) ({len(missing_future_phase)}):")
        _print_list(missing_future_phase, 10)
    if missing_unmapped:
        print(f"\n[WARN] MISSING UNMAPPED (sin fase asignada, P2b pendiente) ({len(missing_unmapped)}):")
        _print_list(missing_unmapped, 20)

    if missing and not allow_missing:
        return 1
    if bad_naming:
        return 2
    if strict and undeclared:
        return 3
    if missing and allow_missing:
        print(f"\n[OK] (relajado: {len(missing)} missing ignorados -- uso F0 / scaffolding)")
    else:
        ok_msg = "[OK] estructura coincide con TRUTH"
        if phase is not None:
            ok_msg += f" (fase {phase})"
        print(f"\n{ok_msg}")
    return 0

if __name__ == "__main__":
    phase_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("--phase="):
            phase_arg = arg.split("=", 1)[1]
    sys.exit(validate(
        strict="--strict" in sys.argv,
        allow_missing="--allow-missing" in sys.argv,
        phase=phase_arg,
        no_truncate="--no-truncate" in sys.argv,
    ))
