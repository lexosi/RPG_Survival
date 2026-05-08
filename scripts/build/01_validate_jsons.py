#!/usr/bin/env python3
"""
01_validate_jsons.py — valida formato, schema y reglas inquebrantables
de los JSONs en data/.

Implementa las reglas declaradas en docs/JSON_SCHEMAS.md:
- §1.4 Header obligatorio (_schema_version, _doc, _validation)
- §2 Reglas inquebrantables (encoding, indentacion, JSON estricto)
- §3 Schema companions_base.json
- §6 Schema equipment.json
- §21 Schema tutorial_chain.json (hereda de §20 quests)
- §38 Schema theme_config.json
- §45.2 Reglas de integridad global (no duplicados, drop rates, etc.)

Cross-file (companion ID -> quest target_id, set_id -> sets.json, etc.)
queda como TODO. Solo hay 4 JSONs en SPR-002 sin refs cruzadas
significativas que validar hoy.

Uso:
    python scripts/build/01_validate_jsons.py [--strict] [--file PATH]

Exit codes:
    0 = todos validos
    1 = error de formato JSON (parsing falla)
    2 = error de schema (campos REQUIRED faltantes, tipos incorrectos)
    3 = error de regla inquebrantable (tradabilidad, naming, etc.)
    4 = error de integridad cruzada (duplicados de id/name)
    5 = warning con --strict
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Defensa encoding PowerShell (lección operacional SPR-001-FIX-3).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"
UPPER_SNAKE = re.compile(r"^[A-Z][A-Z0-9_]*$")

SEV_ORDER = {"parse": 1, "schema": 2, "rule": 3, "integrity": 4, "warn": 5}
SEV_PREFIX = {"parse": "[FAIL]", "schema": "[FAIL]", "rule": "[FAIL]",
              "integrity": "[FAIL]", "warn": "[WARN]"}


class Report:
    def __init__(self):
        self.issues = []  # (file, rule, msg, severity)

    def add(self, file, rule, msg, severity):
        self.issues.append((file, rule, msg, severity))

    def has(self, sev):
        return any(i[3] == sev for i in self.issues)

    def exit_code(self, strict):
        for sev in ("parse", "schema", "rule", "integrity"):
            if self.has(sev):
                return SEV_ORDER[sev]
        if strict and self.has("warn"):
            return 5
        return 0

    def print(self):
        if not self.issues:
            return
        for file, rule, msg, sev in sorted(self.issues, key=lambda x: SEV_ORDER[x[3]]):
            print(f"{SEV_PREFIX[sev]} {file}")
            print(f"  Regla violada: {rule}")
            print(f"  Mensaje: {msg}")


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_file(path: Path, rep: Report):
    """Lee UTF-8 sin BOM y parsea JSON. Devuelve (text, data) o (text|None, None)."""
    rel = _rel(path)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        rep.add(rel, "JSON_SCHEMAS.md §2.10", "archivo tiene BOM UTF-8 (debe ser UTF-8 sin BOM)", "schema")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        rep.add(rel, "JSON_SCHEMAS.md §2.10", f"no es UTF-8 valido: {e}", "schema")
        return None, None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        rep.add(rel, "JSON_SCHEMAS.md §2.9 (JSON estricto)",
                f"linea {e.lineno} col {e.colno}: {e.msg}", "parse")
        return text, None
    return text, data


def validate_header(file: str, data: dict, rep: Report):
    rule = "JSON_SCHEMAS.md §1.4"
    if not isinstance(data, dict):
        rep.add(file, rule, "raiz no es objeto JSON", "schema")
        return
    for fld in ("_schema_version", "_doc", "_validation"):
        if fld not in data:
            rep.add(file, rule, f"falta header obligatorio '{fld}'", "schema")
    if "_schema_version" in data and not isinstance(data["_schema_version"], int):
        rep.add(file, rule, "_schema_version debe ser int", "schema")


def validate_indentation(file: str, text: str, rep: Report):
    if "\t" in text:
        rep.add(file, "JSON_SCHEMAS.md §2.11", "archivo contiene tabs (debe usar 2 espacios)", "warn")
        return
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent == 0 or stripped == "":
            continue
        if indent % 2 != 0:
            rep.add(file, "JSON_SCHEMAS.md §2.11",
                    f"linea {n}: indentacion {indent} no es multiplo de 2", "warn")
            return


def require(rep, file, parent, key, types, rule, optional=False):
    if not isinstance(parent, dict) or key not in parent:
        if not optional:
            rep.add(file, rule, f"falta campo REQUIRED '{key}'", "schema")
        return None
    v = parent[key]
    if not isinstance(v, types):
        names = types.__name__ if isinstance(types, type) else "/".join(t.__name__ for t in types)
        rep.add(file, rule, f"campo '{key}' tipo {type(v).__name__}, esperado {names}", "schema")
        return None
    return v


def check_range(rep, file, val, key, lo, hi, rule):
    if val is None:
        return
    if val < lo or val > hi:
        rep.add(file, rule, f"'{key}'={val} fuera de rango [{lo}..{hi}]", "schema")


# ----------------------------------------------------------------------
# Validators por archivo
# ----------------------------------------------------------------------

def validate_companions_base(file: str, data: dict, rep: Report):
    rule = "JSON_SCHEMAS.md §3.1"
    companions = require(rep, file, data, "companions", list, rule)
    if companions is None:
        return
    seen_ids, seen_names = set(), set()
    for i, c in enumerate(companions):
        ctx = f"companions[{i}]"
        if not isinstance(c, dict):
            rep.add(file, rule, f"{ctx} no es objeto", "schema")
            continue
        cid = require(rep, file, c, "id", int, rule)
        if cid is not None:
            check_range(rep, file, cid, f"{ctx}.id", 1, 9999, rule)
            if cid in seen_ids:
                rep.add(file, "JSON_SCHEMAS.md §2.2", f"id={cid} duplicado en {ctx}", "integrity")
            seen_ids.add(cid)
        name = require(rep, file, c, "name", str, rule)
        if name is not None:
            if not UPPER_SNAKE.match(name):
                rep.add(file, "JSON_SCHEMAS.md §1.3", f"{ctx}.name='{name}' no es UPPER_SNAKE_CASE", "rule")
            if not (3 <= len(name) <= 40):
                rep.add(file, rule, f"{ctx}.name length={len(name)} fuera de [3..40]", "schema")
            if name in seen_names:
                rep.add(file, "JSON_SCHEMAS.md §3.2", f"name='{name}' duplicado en {ctx}", "integrity")
            seen_names.add(name)
        dnk = require(rep, file, c, "display_name_key", str, rule)
        if dnk is not None and not re.match(r"^companion\..+\.name$", dnk):
            rep.add(file, rule, f"{ctx}.display_name_key='{dnk}' no matchea pattern 'companion.*.name'", "schema")
        desk = require(rep, file, c, "description_key", str, rule)
        if desk is not None and not re.match(r"^companion\..+\.description$", desk):
            rep.add(file, rule, f"{ctx}.description_key='{desk}' no matchea pattern 'companion.*.description'", "schema")
        rarity = require(rep, file, c, "rarity", int, rule)
        check_range(rep, file, rarity, f"{ctx}.rarity", 1, 8, rule)
        for stat, lo, hi in (("base_hp", 1, 100000), ("base_atk", 1, 100000),
                              ("base_def", 0, 100000), ("base_speed", 1, 1000)):
            v = require(rep, file, c, stat, int, rule)
            check_range(rep, file, v, f"{ctx}.{stat}", lo, hi, rule)
        cat = require(rep, file, c, "category", str, rule)
        if cat is not None and cat not in {"gather", "combat", "support", "hybrid"}:
            rep.add(file, rule, f"{ctx}.category='{cat}' no en {{gather,combat,support,hybrid}}", "schema")
        of = require(rep, file, c, "obtainable_from", dict, rule)
        if of is not None and not any(k for k in of if not k.startswith("_")):
            rep.add(file, "JSON_SCHEMAS.md §3.2", f"{ctx} sin fuente en obtainable_from (regla SYS-038)", "rule")
        mesh = require(rep, file, c, "mesh_path", str, rule)
        if mesh is not None and not re.match(r"^Content/Assets/Meshes/Companions/.+\.fbx$", mesh):
            rep.add(file, rule, f"{ctx}.mesh_path no matchea 'Content/Assets/Meshes/Companions/*.fbx'", "schema")
        icon = require(rep, file, c, "icon_path", str, rule)
        if icon is not None and not re.match(r"^Content/Assets/Icons/Companions/.+\.png$", icon):
            rep.add(file, rule, f"{ctx}.icon_path no matchea 'Content/Assets/Icons/Companions/*.png'", "schema")
        tradable = require(rep, file, c, "tradable", bool, rule)
        vbucks_only = c.get("vbucks_only", False)
        if not isinstance(vbucks_only, bool):
            rep.add(file, rule, f"{ctx}.vbucks_only no es bool", "schema")
        elif vbucks_only and tradable is True:
            rep.add(file, "JSON_SCHEMAS.md §2.7", f"{ctx} vbucks_only=true requiere tradable=false", "rule")
        # TODO SPR-XXX cross-file: evolution_chain[i] in companions, boss_drops[i] in bosses.json,
        # battle_pass.season en battle_pass_seasons/, display_name_key en localization_keys.json.


def validate_equipment(file: str, data: dict, rep: Report):
    rule = "JSON_SCHEMAS.md §6.1"
    eq = require(rep, file, data, "equipment", list, rule)
    if eq is None:
        return
    seen_ids, seen_names = set(), set()
    for i, item in enumerate(eq):
        ctx = f"equipment[{i}]"
        if not isinstance(item, dict):
            rep.add(file, rule, f"{ctx} no es objeto", "schema")
            continue
        iid = require(rep, file, item, "id", int, rule)
        if iid is not None:
            check_range(rep, file, iid, f"{ctx}.id", 10000, 99999, rule)
            if iid in seen_ids:
                rep.add(file, "JSON_SCHEMAS.md §2.2", f"id={iid} duplicado en {ctx}", "integrity")
            seen_ids.add(iid)
        name = require(rep, file, item, "name", str, rule)
        if name is not None:
            if not UPPER_SNAKE.match(name):
                rep.add(file, "JSON_SCHEMAS.md §1.3", f"{ctx}.name='{name}' no es UPPER_SNAKE_CASE", "rule")
            if name in seen_names:
                rep.add(file, "JSON_SCHEMAS.md §2.2", f"name='{name}' duplicado en {ctx}", "integrity")
            seen_names.add(name)
        dnk = require(rep, file, item, "display_name_key", str, rule)
        if dnk is not None and not re.match(r"^equipment\..+\.name$", dnk):
            rep.add(file, rule, f"{ctx}.display_name_key='{dnk}' no matchea 'equipment.*.name'", "schema")
        desk = require(rep, file, item, "description_key", str, rule)
        if desk is not None and not re.match(r"^equipment\..+\.description$", desk):
            rep.add(file, rule, f"{ctx}.description_key='{desk}' no matchea 'equipment.*.description'", "schema")
        slot = require(rep, file, item, "slot", str, rule)
        if slot is not None and slot not in {"ring", "amulet", "bracelet", "talisman", "charm", "relic"}:
            rep.add(file, rule, f"{ctx}.slot='{slot}' invalido", "schema")
        rarity = require(rep, file, item, "rarity", int, rule)
        check_range(rep, file, rarity, f"{ctx}.rarity", 1, 8, rule)
        bs = require(rep, file, item, "base_stats", dict, rule)
        if bs is not None:
            positive = sum(1 for k, v in bs.items()
                           if not k.startswith("_") and isinstance(v, (int, float)) and v > 0)
            if positive == 0:
                rep.add(file, "JSON_SCHEMAS.md §6.2", f"{ctx}.base_stats sin stat > 0", "rule")
        of = require(rep, file, item, "obtainable_from", dict, rule)
        if of is not None and not any(k for k in of if not k.startswith("_")):
            rep.add(file, "JSON_SCHEMAS.md §45.2", f"{ctx} sin fuentes en obtainable_from", "rule")
        tradable = require(rep, file, item, "tradable", bool, rule)
        vbucks_only = item.get("vbucks_only", False)
        if isinstance(vbucks_only, bool) and vbucks_only and tradable is True:
            rep.add(file, "JSON_SCHEMAS.md §2.7", f"{ctx} vbucks_only=true requiere tradable=false", "rule")
        require(rep, file, item, "icon_path", str, rule)
        # TODO SPR-XXX cross-file: set_id -> sets.json, slot -> equipment_slots.json,
        # obtainable_from refs (boss_drops, events).


def validate_tutorial_chain(file: str, data: dict, rep: Report):
    rule_s = "JSON_SCHEMAS.md §21.1"
    rule_t = "JSON_SCHEMAS.md §21.2"
    rule_q = "JSON_SCHEMAS.md §20.2"
    tq = require(rep, file, data, "tutorial_quests", list, rule_s)
    cfg = require(rep, file, data, "config", dict, rule_s)
    if cfg is not None:
        if not isinstance(cfg.get("skippable_for_admins"), bool):
            rep.add(file, rule_s, "config.skippable_for_admins ausente o no bool", "schema")
        if cfg.get("completion_unlocks_first_rebirth") is not True:
            rep.add(file, rule_s, "config.completion_unlocks_first_rebirth debe ser true", "schema")
    if tq is None:
        return
    # length=15 al cierre del epic; relajado a warning durante seed (SPR-002 dejo 1 placeholder).
    if len(tq) != 15:
        rep.add(file, rule_t,
                f"tutorial_quests tiene {len(tq)} entradas (esperado 15 al cierre del epic)", "warn")
    seen_ids, seen_names = set(), set()
    for i, q in enumerate(tq):
        ctx = f"tutorial_quests[{i}]"
        if not isinstance(q, dict):
            rep.add(file, rule_s, f"{ctx} no es objeto", "schema")
            continue
        qid = require(rep, file, q, "id", int, rule_s)
        if qid is not None:
            if qid in seen_ids:
                rep.add(file, "JSON_SCHEMAS.md §2.2", f"id={qid} duplicado en {ctx}", "integrity")
            seen_ids.add(qid)
        name = require(rep, file, q, "name", str, rule_s)
        if name is not None:
            if not UPPER_SNAKE.match(name):
                rep.add(file, "JSON_SCHEMAS.md §1.3", f"{ctx}.name='{name}' no es UPPER_SNAKE_CASE", "rule")
            if name in seen_names:
                rep.add(file, "JSON_SCHEMAS.md §2.2", f"name='{name}' duplicado en {ctx}", "integrity")
            seen_names.add(name)
        dnk = require(rep, file, q, "display_name_key", str, rule_s)
        if dnk is not None and not re.match(r"^quest\..+\.name$", dnk):
            rep.add(file, rule_s, f"{ctx}.display_name_key='{dnk}' no matchea 'quest.*.name'", "schema")
        desk = require(rep, file, q, "description_key", str, rule_s)
        if desk is not None and not re.match(r"^quest\..+\.description$", desk):
            rep.add(file, rule_s, f"{ctx}.description_key no matchea 'quest.*.description'", "schema")
        cat = require(rep, file, q, "category", str, rule_s)
        if cat is not None and cat != "tutorial":
            rep.add(file, rule_t, f"{ctx}.category='{cat}' debe ser 'tutorial'", "rule")
        prereqs = require(rep, file, q, "prerequisites", list, rule_s)
        if prereqs is not None and i == 0 and len(prereqs) != 0:
            rep.add(file, rule_t, f"{ctx} (primera quest) debe tener prerequisites=[]", "rule")
        obj = require(rep, file, q, "objective", dict, rule_s)
        if obj is not None:
            otype = obj.get("type")
            if otype not in {"gather", "kill", "craft", "level_up", "collect_companion",
                              "complete_zone", "spend_gold", "spend_gems", "login", "time_played", "custom"}:
                rep.add(file, rule_s, f"{ctx}.objective.type='{otype}' invalido", "schema")
            amount = obj.get("amount")
            if not isinstance(amount, int) or amount < 1:
                rep.add(file, rule_s, f"{ctx}.objective.amount invalido (debe ser int >=1)", "schema")
        rewards = require(rep, file, q, "rewards", list, rule_s)
        if rewards is not None:
            for j, r in enumerate(rewards):
                if not isinstance(r, dict):
                    rep.add(file, rule_s, f"{ctx}.rewards[{j}] no es objeto", "schema")
                    continue
                rt = r.get("reward_type")
                if rt not in {"gold", "gems", "xp", "bp_xp", "item", "companion", "lootbox"}:
                    rep.add(file, rule_s, f"{ctx}.rewards[{j}].reward_type='{rt}' invalido", "schema")
                if not isinstance(r.get("amount"), int):
                    rep.add(file, rule_s, f"{ctx}.rewards[{j}].amount no es int", "schema")
        if "repeatable" in q and q.get("repeatable") is not False:
            rep.add(file, rule_q, f"{ctx}.repeatable debe ser false (tutorial)", "rule")
        if "reset_period" in q and q.get("reset_period") != "none":
            rep.add(file, rule_q, f"{ctx}.reset_period='{q.get('reset_period')}' debe ser 'none' (tutorial)", "rule")
        # TODO SPR-XXX cross-file: prerequisites IDs en quests/*.json, objective.target_id segun type,
        # cadena lineal de prereqs (DAG).


def validate_theme_config(file: str, data: dict, rep: Report):
    rule = "JSON_SCHEMAS.md §38.1"
    active = require(rep, file, data, "active_theme", str, rule)
    themes = require(rep, file, data, "themes", dict, rule)
    if themes is None:
        return
    if active is not None and active not in themes:
        rep.add(file, "JSON_SCHEMAS.md §38.2",
                f"active_theme='{active}' no existe en themes", "integrity")
    for tname, tdef in themes.items():
        ctx = f"themes.{tname}"
        if not isinstance(tdef, dict):
            rep.add(file, rule, f"{ctx} no es objeto", "schema")
            continue
        for fld in ("display_name_key", "hub_mesh_path", "skybox_material_path", "ambient_track_key"):
            if not isinstance(tdef.get(fld), str):
                rep.add(file, rule, f"{ctx}.{fld} ausente o no string", "schema")
        rules = tdef.get("asset_swap_rules")
        if not isinstance(rules, list):
            rep.add(file, rule, f"{ctx}.asset_swap_rules ausente o no array", "schema")
        else:
            for j, r in enumerate(rules):
                if not isinstance(r, dict):
                    rep.add(file, rule, f"{ctx}.asset_swap_rules[{j}] no es objeto", "schema")
                    continue
                if not isinstance(r.get("pattern"), str):
                    rep.add(file, rule, f"{ctx}.asset_swap_rules[{j}].pattern ausente o no string", "schema")
                if not isinstance(r.get("replacement_folder"), str):
                    rep.add(file, rule, f"{ctx}.asset_swap_rules[{j}].replacement_folder ausente o no string", "schema")
        for arr_name in ("exclusive_companions", "exclusive_items"):
            arr = tdef.get(arr_name)
            if arr is None:
                continue
            if not isinstance(arr, list):
                rep.add(file, rule, f"{ctx}.{arr_name} no es array", "schema")
                continue
            for j, x in enumerate(arr):
                if not isinstance(x, int) or isinstance(x, bool):
                    rep.add(file, rule, f"{ctx}.{arr_name}[{j}]={x!r} no es int", "schema")
        # TODO SPR-XXX cross-file: exclusive_companions/exclusive_items deben existir,
        # replacement_folder existe en disco, color_palette_overrides matchea UI_UX_STYLE_GUIDE.


# ----------------------------------------------------------------------
# Dispatcher
# ----------------------------------------------------------------------

SCHEMA_VALIDATORS = {
    "data/companions/companions_base.json": validate_companions_base,
    "data/items/equipment.json": validate_equipment,
    "data/quests/tutorial_chain.json": validate_tutorial_chain,
    "data/theme/theme_config.json": validate_theme_config,
}


def validate_path(path: Path, validator, rep: Report):
    rel = _rel(path)
    if not path.exists():
        rep.add(rel, "filesystem", "archivo no existe", "schema")
        return
    text, data = read_file(path, rep)
    if data is None:
        return
    validate_header(rel, data, rep)
    validate_indentation(rel, text, rep)
    if validator is not None:
        validator(rel, data, rep)


def _resolve_file_arg(arg: str) -> Path:
    p = Path(arg)
    if p.is_absolute():
        return p
    cand_root = ROOT / arg
    if cand_root.exists():
        return cand_root
    cand_data = DATA_ROOT / arg
    return cand_data


def main():
    ap = argparse.ArgumentParser(
        description="Valida formato, schema y reglas inquebrantables de los JSONs en data/. "
                    "Implementa docs/JSON_SCHEMAS.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes:\n"
               "  0 = todos validos\n"
               "  1 = error de formato JSON\n"
               "  2 = error de schema\n"
               "  3 = error de regla inquebrantable\n"
               "  4 = error de integridad (duplicados)\n"
               "  5 = warning con --strict",
    )
    ap.add_argument("--strict", action="store_true",
                    help="trata warnings como errores (exit 5)")
    ap.add_argument("--file", help="valida solo un archivo (relativo a repo o a data/, o absoluto)")
    args = ap.parse_args()

    rep = Report()

    if args.file:
        target = _resolve_file_arg(args.file)
        rel = _rel(target)
        validator = None
        for k, v in SCHEMA_VALIDATORS.items():
            if rel == k or rel.endswith("/" + k.split("/")[-1]):
                validator = v
                break
        if validator is None:
            print(f"[INFO] sin validator schema-specifico para '{rel}', solo checks universales")
        validate_path(target, validator, rep)
    else:
        print(f"[INFO] validando {len(SCHEMA_VALIDATORS)} archivos declarados")
        for relkey, validator in SCHEMA_VALIDATORS.items():
            validate_path(ROOT / relkey, validator, rep)

    rep.print()
    code = rep.exit_code(strict=args.strict)
    print()
    if code == 0:
        print("[OK] todos los JSONs validos")
    else:
        print(f"[FAIL] exit {code} ({len(rep.issues)} issue(s))")
    sys.exit(code)


if __name__ == "__main__":
    main()
