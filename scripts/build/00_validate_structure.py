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
    "Generated": re.compile(r"^[A-Z][A-Za-z0-9]*_Generated\.verse$|^ModuleRegistryConstants\.verse$|^EventBusConstants\.verse$"),
    "scripts_build": re.compile(r"^\d{2}_[a-z][a-z0-9_]*\.py$"),
    "docs": re.compile(r"^[A-Z][A-Z0-9_]*\.md$|^README\.md$"),
    # SPR-207-FIX-1: daily logs en docs/dailylog/ siguen su propia regla
    # (TRUTH §1.1 fila "Daily logs" + §6.2). DL_<fecha>_SPR-<tokens>_<autor>.md
    "docs_dailylog": re.compile(r"^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$"),
}


def docs_rule_for(rel_posix: str) -> str:
    """Selecciona regla aplicable a un archivo dentro de docs/.
    docs/dailylog/* → regla DL. docs/* raíz → regla SCREAMING_SNAKE."""
    if rel_posix.startswith("docs/dailylog/"):
        return "docs_dailylog"
    return "docs"

def parse_truth_paths(md_text: str) -> set[str]:
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
    return paths

def validate(strict: bool = False, allow_missing: bool = False) -> int:
    if not TRUTH.exists():
        print(f"[FAIL] No existe {TRUTH}", file=sys.stderr)
        return 1

    declared = parse_truth_paths(TRUTH.read_text(encoding="utf-8"))
    print(f"[INFO] {len(declared)} paths declarados en TRUTH")

    missing, bad_naming, undeclared = [], [], []

    # 1) MISSING: declarados que no existen
    for rel in declared:
        if not (ROOT / rel).exists():
            missing.append(rel)

    # 2) BAD_NAMING: archivos del repo en zonas reguladas
    for folder, rule_key in [
        ("data", "data"),
        ("Content/Verse/Systems", "Verse"),
        ("Content/Verse/Core", "Verse"),
        ("Content/Verse/Devices", "Verse"),
        ("Content/Verse/Generated", "Generated"),
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
                rel_posix = p.relative_to(ROOT).as_posix()
                # SPR-207-FIX-1: en docs/, regla por path (raíz vs dailylog/)
                key = docs_rule_for(rel_posix) if folder == "docs" else rule_key
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
                rel = p.relative_to(ROOT).as_posix()
                # SPR-207-FIX-1: docs/dailylog/DL_*.md están implícitamente declarados
                # vía pattern (TRUTH §6.2 los trata como "contenedor de DL_*").
                if rel.startswith("docs/dailylog/") and NAMING_RULES["docs_dailylog"].match(p.name):
                    continue
                if rel not in declared:
                    undeclared.append(rel)

    # Reporte
    if missing:
        label = "[WARN] MISSING (ignorado por --allow-missing)" if allow_missing else "[FAIL] MISSING"
        print(f"\n{label} ({len(missing)}):")
        for m in missing[:20]:
            print(f"   {m}")
        if len(missing) > 20:
            print(f"   ... y {len(missing) - 20} mas")
    if bad_naming:
        print(f"\n[FAIL] BAD_NAMING ({len(bad_naming)}):")
        for b in bad_naming:
            print(f"   {b}")
    if undeclared:
        print(f"\n[WARN] UNDECLARED ({len(undeclared)}):")
        for u in undeclared[:20]:
            print(f"   {u}")
        if len(undeclared) > 20:
            print(f"   ... y {len(undeclared) - 20} mas")

    if missing and not allow_missing:
        return 1
    if bad_naming:
        return 2
    if strict and undeclared:
        return 3
    if missing and allow_missing:
        print(f"\n[OK] (relajado: {len(missing)} missing ignorados -- uso F0 / scaffolding)")
    else:
        print("\n[OK] estructura coincide con TRUTH")
    return 0

if __name__ == "__main__":
    sys.exit(validate(
        strict="--strict" in sys.argv,
        allow_missing="--allow-missing" in sys.argv,
    ))
