#!/usr/bin/env python3
"""close_sprint.py — generador de daily log al cerrar un sprint.

Uso:
    python scripts/tools/close_sprint.py [SPR-XXX | SPR-XXX-FIX-N] [opciones]

Si no se pasa SPR explícito, usa el último tag creado en HEAD.

Crea o actualiza el archivo `docs/dailylog/DL_YYYY-MM-DD_SPR-...+..._<autor>.md`
correspondiente al día actual. Si ya existe daily log para hoy y se cierra otro
sprint, renombra el archivo añadiendo el nuevo segmento (idempotente).

Opciones:
    --reset-user    Vuelve a preguntar el nickname y sobrescribe `.dailylog_user`.
    --no-open       No abre el archivo en VS Code al terminar.
    --quiet         Output mínimo.

Exit codes:
    0  OK
    1  SPR no encontrado en SPRINTS_BACKLOG (cuando aplica) o git error
    2  argumentos inválidos
    3  autor inválido
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
DAILYLOG_DIR = DOCS / "dailylog"
USER_FILE = ROOT / ".dailylog_user"
BACKLOG = DOCS / "SPRINTS_BACKLOG.md"

TAG_RE = re.compile(r"^SPR-(\d{3})(?:-FIX-(\d+))?$")
USER_RE = re.compile(r"^[a-z0-9]+$")
FILENAME_RE = re.compile(r"^DL_(\d{4}-\d{2}-\d{2})_SPR-([\w+\-]+)_([a-z0-9]+)\.md$")

AUTO_SECTIONS = ("header", "sprints", "commits", "files", "status")
MANUAL_BEGIN = "<!-- BEGIN MANUAL -->"
MANUAL_END = "<!-- END MANUAL -->"


# ─── utilidades ────────────────────────────────────────────────────────────

def log(msg: str, *, quiet: bool = False) -> None:
    if not quiet:
        print(msg)


def err(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def run_git(args: list[str], *, check: bool = True) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} → exit {res.returncode}: {res.stderr.strip()}")
    return res.stdout


# ─── autor ─────────────────────────────────────────────────────────────────

def load_or_prompt_user(reset: bool = False) -> str:
    if not reset and USER_FILE.exists():
        nick = USER_FILE.read_text(encoding="utf-8").strip()
        if USER_RE.match(nick):
            return nick
        err(f".dailylog_user contiene valor inválido: {nick!r}. Usa --reset-user.")
        sys.exit(3)
    print("Configura tu nickname de daily log (lowercase, sin espacios, regex ^[a-z0-9]+$).")
    while True:
        nick = input("Nickname: ").strip().lower()
        if USER_RE.match(nick):
            USER_FILE.write_text(nick, encoding="utf-8")
            log(f"✅ Guardado en {USER_FILE.relative_to(ROOT)}")
            return nick
        print("  Inválido. Solo a-z y 0-9. Reintenta.")


# ─── tags / SPR ────────────────────────────────────────────────────────────

@dataclass
class SprintTag:
    raw: str          # "SPR-001-FIX-1"
    base: str         # "001"
    fix: int | None   # 1 o None
    token: str        # segmento usado en filename: "001" o "FIX1"
    is_fix: bool

    @property
    def base_id(self) -> str:
        return f"SPR-{self.base}"


def parse_tag(tag: str) -> SprintTag:
    m = TAG_RE.match(tag)
    if not m:
        err(f"Tag {tag!r} no encaja con SPR-NNN o SPR-NNN-FIX-K.")
        sys.exit(2)
    base, fix = m.group(1), m.group(2)
    if fix is None:
        return SprintTag(raw=tag, base=base, fix=None, token=base, is_fix=False)
    return SprintTag(raw=tag, base=base, fix=int(fix), token=f"FIX{fix}", is_fix=True)


def latest_tag() -> str | None:
    out = run_git(["tag", "--points-at", "HEAD"], check=False).strip()
    if out:
        tags = [t for t in out.splitlines() if TAG_RE.match(t.strip())]
        if tags:
            return sorted(tags)[-1]
    out = run_git(["tag", "--sort=-creatordate"], check=False).strip()
    for line in out.splitlines():
        if TAG_RE.match(line.strip()):
            return line.strip()
    return None


# ─── backlog parser ────────────────────────────────────────────────────────

@dataclass
class SprintMeta:
    spr_id: str
    title: str
    sys: str
    tipo: str
    deps: str
    files: str
    tiempo: str

    @classmethod
    def placeholder(cls, spr_id: str, *, hotfix: bool = False) -> "SprintMeta":
        title = f"Hotfix de {spr_id}" if hotfix else f"(no encontrado en SPRINTS_BACKLOG.md)"
        return cls(
            spr_id=spr_id, title=title, sys="—", tipo="hotfix" if hotfix else "—",
            deps="—", files="—", tiempo="—",
        )


def parse_backlog_row(line: str) -> list[str] | None:
    if not line.startswith("|") or "SPR-" not in line:
        return None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells:
        return None
    m = re.match(r"^(SPR-\d{3})\b", cells[0])
    if not m:
        return None
    cells[0] = m.group(1)
    return cells


def find_sprint_meta(spr_base_id: str) -> SprintMeta | None:
    """Busca fila de SPR-NNN en SPRINTS_BACKLOG.md. Soporta tablas con 7 u 8 columnas
    (las de §10 incluyen `Fase` extra)."""
    if not BACKLOG.exists():
        return None
    for line in BACKLOG.read_text(encoding="utf-8").splitlines():
        cells = parse_backlog_row(line)
        if not cells or cells[0] != spr_base_id:
            continue
        # 7 columnas: ID, Título, SYS, Tipo, Deps, Archivos, Tiempo
        # 8 columnas: ID, Título, SYS, Fase, Tipo, Deps, Archivos, Tiempo
        # 9 columnas (§10): ID, Título, SYS, Fase, Tipo, Deps, Archivos, Tiempo, Motivo
        if len(cells) >= 9 and cells[3].startswith("F"):
            return SprintMeta(cells[0], cells[1], cells[2], cells[4], cells[5], cells[6], cells[7])
        if len(cells) >= 8 and cells[3].startswith("F"):
            return SprintMeta(cells[0], cells[1], cells[2], cells[4], cells[5], cells[6], cells[7])
        if len(cells) >= 7:
            return SprintMeta(cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], cells[6])
    return None


# ─── git data del día ──────────────────────────────────────────────────────

def today_str() -> str:
    return _dt.date.today().isoformat()


def midnight_iso() -> str:
    return _dt.datetime.combine(_dt.date.today(), _dt.time.min).isoformat()


def commits_today() -> list[tuple[str, str]]:
    """[(sha, subject), ...] de commits desde medianoche local."""
    out = run_git(["log", f"--since={midnight_iso()}", "--pretty=format:%h|%s"], check=False)
    rows = []
    for line in out.splitlines():
        if "|" in line:
            sha, _, subj = line.partition("|")
            rows.append((sha.strip(), subj.strip()))
    return rows


def files_for_commit(sha: str) -> list[str]:
    out = run_git(["show", "--name-only", "--pretty=format:", sha], check=False)
    return [l.strip() for l in out.splitlines() if l.strip()]


def files_today() -> dict[str, list[str]]:
    """{sha: [archivos]} para commits del día."""
    return {sha: files_for_commit(sha) for sha, _ in commits_today()}


def tags_today() -> list[str]:
    """Tags cuya fecha de creación es hoy (creatordate)."""
    out = run_git(["for-each-ref", "--format=%(refname:short) %(creatordate:short)", "refs/tags"], check=False)
    today = today_str()
    res = []
    for line in out.splitlines():
        parts = line.strip().rsplit(" ", 1)
        if len(parts) == 2 and parts[1] == today and TAG_RE.match(parts[0]):
            res.append(parts[0])
    return res


def current_branch() -> str:
    return run_git(["branch", "--show-current"], check=False).strip() or "(detached)"


def working_tree_status() -> str:
    out = run_git(["status", "--porcelain"], check=False).strip()
    return "limpio" if not out else f"sucio ({len(out.splitlines())} entradas)"


def last_commit_oneline() -> str:
    return run_git(["log", "-1", "--pretty=format:%h — %s"], check=False).strip()


# ─── nombrado de archivo ───────────────────────────────────────────────────

def find_today_log(date_str: str, author: str) -> Path | None:
    if not DAILYLOG_DIR.exists():
        return None
    for p in DAILYLOG_DIR.glob(f"DL_{date_str}_*_{author}.md"):
        m = FILENAME_RE.match(p.name)
        if m and m.group(1) == date_str and m.group(3) == author:
            return p
    return None


def tokens_from_filename(path: Path) -> list[str]:
    m = FILENAME_RE.match(path.name)
    if not m:
        return []
    return m.group(2).split("+")


def merge_tokens(existing: list[str], new_token: str) -> list[str]:
    if new_token in existing:
        return existing
    return existing + [new_token]


def filename_for(date_str: str, tokens: list[str], author: str) -> str:
    return f"DL_{date_str}_SPR-{'+'.join(tokens)}_{author}.md"


# ─── render markdown ───────────────────────────────────────────────────────

DEFAULT_MANUAL_BLOCK = f"""{MANUAL_BEGIN}
## 🧠 Notas (rellenar a mano)

### Energía / foco subjetivo (1–10)
- Foco: _
- Satisfacción con resultados: _
- Energía al cerrar: _

### Tiempo real
- Total trabajado: _ (compara con la suma de estimaciones de los SPR cerrados)

### Bloqueos del día
- (ninguno reportado · describir si los hubo, hora + sprint afectado + tiempo perdido)

### Bugs encontrados
- (rellenar)

### Decisiones tomadas
- (rellenar si aplica · referenciar CONCEPT.md §14 si entra en docs autoritativos)

### Notas para mañana (LO MÁS IMPORTANTE)
- Contexto crítico para retomar: _
- Tareas pendientes inmediatas: _
- Cosas a verificar al empezar: _
- Riesgos a vigilar mañana: _

### Notas misceláneas
-
{MANUAL_END}
"""


def render_sprints(metas: list[tuple[SprintTag, SprintMeta]]) -> str:
    blocks = []
    for tag, meta in metas:
        blocks.append(
            f"### {tag.raw} — {meta.title}\n"
            f"- **Tipo**: {meta.tipo}\n"
            f"- **SYS**: {meta.sys}\n"
            f"- **Deps**: {meta.deps}\n"
            f"- **Estimación**: {meta.tiempo}\n"
            f"- **Tag git**: `{tag.raw}`\n"
            f"- **Done universal**: ✅ compila + ✅ test + ✅ commit con tag\n"
            f"- **Done criteria sprint**: ver `docs/SPRINTS_BACKLOG.md` (fila {meta.spr_id} y bloque Done de la fase)\n"
            f"- **Archivos clave declarados**: {meta.files}\n"
        )
    return "\n".join(blocks).rstrip()


def render_commits(commits: list[tuple[str, str]]) -> str:
    if not commits:
        return "_(sin commits hoy)_"
    rows = ["| SHA | Mensaje |", "|---|---|"]
    for sha, subj in commits:
        rows.append(f"| `{sha}` | {subj.replace('|', '/')} |")
    return "\n".join(rows)


def render_files(files_map: dict[str, list[str]]) -> str:
    seen: dict[str, set[str]] = {}
    for sha, files in files_map.items():
        for f in files:
            seen.setdefault(f, set()).add(sha)
    if not seen:
        return "_(ningún archivo tocado hoy)_"
    rows = []
    for f in sorted(seen):
        shas = ", ".join(sorted(seen[f]))
        rows.append(f"- `{f}` ({shas})")
    return "\n".join(rows)


def render_status(branch: str, last_c: str, status: str, today_tags: list[str]) -> str:
    tags_s = ", ".join(f"`{t}`" for t in today_tags) if today_tags else "_(sin tags hoy)_"
    return (
        f"- **Branch**: `{branch}`\n"
        f"- **Último commit**: {last_c}\n"
        f"- **Working tree**: {status}\n"
        f"- **Tags creados hoy**: {tags_s}\n"
        f"- **Push remoto**: _ (rellenar manual)\n"
    )


def render_full(
    *,
    date_str: str,
    author: str,
    tokens: list[str],
    metas: list[tuple[SprintTag, SprintMeta]],
    commits: list[tuple[str, str]],
    files_map: dict[str, list[str]],
    branch: str,
    last_c: str,
    status: str,
    today_tags: list[str],
    manual_block: str,
) -> str:
    spr_label = "+".join(tokens)
    generated_at = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"<!-- AUTO-GENERATED. Actualizable con scripts/tools/close_sprint.py. "
        f"No edites entre marcadores AUTO. -->\n\n"
        f"# Daily Log — {date_str} — autor: {author}\n\n"
        f"**Sprints cerrados (segmentos)**: SPR-{spr_label}\n"
        f"**Branch**: `{branch}`\n"
        f"**Último commit**: {last_c}\n"
        f"**Generado**: {generated_at}\n\n"
        f"---\n\n"
        f"## 🎯 Sprints cerrados\n\n"
        f"<!-- BEGIN AUTO:sprints -->\n"
        f"{render_sprints(metas)}\n"
        f"<!-- END AUTO:sprints -->\n\n"
        f"## 📦 Commits del día\n\n"
        f"<!-- BEGIN AUTO:commits -->\n"
        f"{render_commits(commits)}\n"
        f"<!-- END AUTO:commits -->\n\n"
        f"## 🗂️ Archivos tocados hoy\n\n"
        f"<!-- BEGIN AUTO:files -->\n"
        f"{render_files(files_map)}\n"
        f"<!-- END AUTO:files -->\n\n"
        f"## 🔁 Estado del repo al cerrar\n\n"
        f"<!-- BEGIN AUTO:status -->\n"
        f"{render_status(branch, last_c, status, today_tags)}\n"
        f"<!-- END AUTO:status -->\n\n"
        f"---\n\n"
        f"{manual_block}\n"
    )


def extract_manual_block(existing: str) -> str:
    if MANUAL_BEGIN in existing and MANUAL_END in existing:
        start = existing.index(MANUAL_BEGIN)
        end = existing.index(MANUAL_END) + len(MANUAL_END)
        return existing[start:end] + "\n"
    return DEFAULT_MANUAL_BLOCK


# ─── editor ────────────────────────────────────────────────────────────────

def open_in_editor(path: Path) -> bool:
    for cmd in ("code", "code-insiders"):
        exe = shutil.which(cmd)
        if exe:
            try:
                subprocess.Popen([exe, str(path)], cwd=ROOT)
                return True
            except OSError:
                continue
    return False


# ─── main ──────────────────────────────────────────────────────────────────

def cli() -> int:
    parser = argparse.ArgumentParser(description="Cierra un sprint y crea/actualiza daily log.")
    parser.add_argument("spr", nargs="?", help="SPR-XXX o SPR-XXX-FIX-N. Si se omite, usa el último tag de HEAD.")
    parser.add_argument("--reset-user", action="store_true")
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    quiet = args.quiet

    # 1) autor
    author = load_or_prompt_user(reset=args.reset_user)

    # 2) SPR a cerrar
    raw = args.spr
    if not raw:
        raw = latest_tag()
        if not raw:
            err("No se pasó SPR y no hay tags en el repo.")
            return 1
        log(f"📌 SPR no especificado · uso último tag: {raw}", quiet=quiet)
    tag = parse_tag(raw)

    # 3) metadata del sprint (backlog)
    if tag.is_fix:
        meta = SprintMeta.placeholder(tag.base_id, hotfix=True)
        meta.spr_id = tag.raw
    else:
        m = find_sprint_meta(tag.base_id)
        if m is None:
            err(f"{tag.base_id} no encontrado en SPRINTS_BACKLOG.md.")
            return 1
        meta = m

    # 4) carpeta dailylog
    DAILYLOG_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = DAILYLOG_DIR / ".gitkeep"
    if not gitkeep.exists() and not any(DAILYLOG_DIR.iterdir()):
        gitkeep.write_text("", encoding="utf-8")

    # 5) resolver archivo destino
    date_str = today_str()
    existing = find_today_log(date_str, author)
    existing_metas: list[tuple[SprintTag, SprintMeta]] = []
    manual_block = DEFAULT_MANUAL_BLOCK
    if existing:
        tokens = tokens_from_filename(existing)
        # Reconstruir metas previos a partir de tokens existentes (best effort)
        for tok in tokens:
            if tok.startswith("FIX"):
                # Necesitamos saber base sprint para hotfixes previos. Heurística: usar la base
                # más reciente conocida (último número de sprint en tokens anteriores).
                base = next((t for t in tokens if not t.startswith("FIX")), tag.base)
                fixn = int(tok[3:]) if tok[3:].isdigit() else 1
                fake_raw = f"SPR-{base}-FIX-{fixn}"
                fake_tag = SprintTag(raw=fake_raw, base=base, fix=fixn, token=tok, is_fix=True)
                existing_metas.append((fake_tag, SprintMeta.placeholder(f"SPR-{base}", hotfix=True)))
            else:
                fake_tag = SprintTag(raw=f"SPR-{tok}", base=tok, fix=None, token=tok, is_fix=False)
                m = find_sprint_meta(f"SPR-{tok}") or SprintMeta.placeholder(f"SPR-{tok}")
                existing_metas.append((fake_tag, m))
        manual_block = extract_manual_block(existing.read_text(encoding="utf-8"))
    else:
        tokens = []

    # 6) idempotencia
    new_tokens = merge_tokens(tokens, tag.token)
    if new_tokens == tokens and existing:
        log(f"ℹ️  {tag.raw} ya estaba registrado en {existing.relative_to(ROOT)}. Regenero solo bloques AUTO.", quiet=quiet)
        metas_to_render = existing_metas
    else:
        metas_to_render = existing_metas + [(tag, meta)] if existing else [(tag, meta)]

    # 7) gather git
    commits = commits_today()
    files_map = files_today()
    branch = current_branch()
    last_c = last_commit_oneline()
    status = working_tree_status()
    today_tag_list = tags_today()

    # 8) render
    content = render_full(
        date_str=date_str,
        author=author,
        tokens=new_tokens,
        metas=metas_to_render,
        commits=commits,
        files_map=files_map,
        branch=branch,
        last_c=last_c,
        status=status,
        today_tags=today_tag_list,
        manual_block=manual_block,
    )

    # 9) escribir / renombrar
    target = DAILYLOG_DIR / filename_for(date_str, new_tokens, author)
    if existing and existing != target:
        run_git(["mv", str(existing.relative_to(ROOT)), str(target.relative_to(ROOT))], check=False)
        if existing.exists():  # git mv falló o archivo no estaba trackeado todavía
            existing.rename(target)
        log(f"📝 Renombrado: {existing.name} → {target.name}", quiet=quiet)
    target.write_text(content, encoding="utf-8")
    log(f"✅ Daily log: {target.relative_to(ROOT)}", quiet=quiet)

    # 10) abrir editor
    if not args.no_open:
        if open_in_editor(target):
            log("🚀 Abierto en VS Code.", quiet=quiet)
        else:
            log("ℹ️  VS Code (`code`) no encontrado en PATH. Abre el archivo manualmente.", quiet=quiet)

    return 0


if __name__ == "__main__":
    sys.exit(cli())
