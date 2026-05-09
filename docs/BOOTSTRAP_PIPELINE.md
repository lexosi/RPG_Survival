# 🏗️ BOOTSTRAP_PIPELINE — Pipeline de generación

> **El flujo Data → Build → Runtime explicado para que DeepSeek nunca cree datos en Verse, sino el script Python que los genera.**
>
> **Decisión cerrada (Auditoría 2 — C1, C3)**: el pipeline cubre dos categorías de artifacts Verse:
> 1. **Datos** (`Companions_Generated.verse`, `Items_Generated.verse`, etc.) — generados desde JSONs de contenido.
> 2. **Arquitectura** — generados desde JSONs declarativos en `data/architecture/`:
>    - `ModuleRegistryConstants.verse` — desde `modules_manifest.json` para lookup runtime entre Systems gameplay sin reflexión Verse. Patrón completo en §10.
>    - `EventPayloads_Generated.verse` + `EventBusDevice.verse` — desde `events_catalog.json` para EventBus type-safe sobre `event(t)` nativo de Verse. `EventBusDevice` es un `creative_device` (patrón H4 post-SPR-009 F-C-2 — `event(t){}` top-level falla con err 3512, ver `VERSE_SYNTAX_GUIDE.md` §1 lección 16). Patrón completo en §11.
>
> ⚠️ **Sintaxis Verse moderna (post-SPR-211)**: las plantillas de Verse generado en este doc fueron reescritas a Patrón 3 (struct `<public>` + module `<public>` + funciones getter `Get{Singular}{PascalCase}`). El patrón legacy `NAME := struct_def{...}` top-level falla con err 3512. Autoridad sintáctica vigente: `docs/VERSE_SYNTAX_GUIDE.md`. §10 (ModuleRegistry) usa archetype constructor top-level que probablemente requiera refactor a getter pattern; queda pendiente para SPR-005 implementación. **§11 (EventBus/EventPayloads) ya refactorizada (SPR-009 F-C-4-L1a, post-H4)**: el EventBus operativo es ahora `event_bus_device := class<concrete>(creative_device)` instanciado en Main.umap (`Generated/EventBusDevice.verse`), NO singleton top-level. Razón canonizada en `VERSE_SYNTAX_GUIDE.md` §1 lección 16.

---

## 🧭 Índice

1. [La filosofía: Source → Transformer → Artifact](#1-la-filosofía-source--transformer--artifact)
2. [Source of Truth: los JSONs](#2-source-of-truth-los-jsons)
3. [Transformers: scripts Python](#3-transformers-scripts-python)
4. [Artifacts: archivos Verse generados](#4-artifacts-archivos-verse-generados)
5. [Inyección en runtime: cómo Verse usa los artifacts](#5-inyección-en-runtime-cómo-verse-usa-los-artifacts)
6. [Anti-patrones (lo que DeepSeek NUNCA debe hacer)](#6-anti-patrones-lo-que-deepseek-nunca-debe-hacer)
7. [Pipeline completo paso a paso](#7-pipeline-completo-paso-a-paso)
8. [Plantillas de scripts Python](#8-plantillas-de-scripts-python)
9. [Plantillas de Verse generado](#9-plantillas-de-verse-generado)
10. [Patrón Core estático vs Systems registrables (C1)](#10-patrón-core-estático-vs-systems-registrables-c1)
11. [EventBus tipado generado (C3)](#11-eventbus-tipado-generado-c3)

---

## 1. La filosofía: Source → Transformer → Artifact

### 1.1 La regla de oro

> **DeepSeek NUNCA crea datos hardcoded en Verse.**
> **DeepSeek crea el SCRIPT que GENERA esos datos en Verse desde JSON.**

### 1.2 Diagrama mental

```
┌──────────────────┐        ┌────────────────────┐       ┌──────────────────────┐
│ SOURCE OF TRUTH  │  ─────►│ TRANSFORMER        │ ─────►│ ARTIFACT             │
│ JSONs en /data/  │        │ Python scripts     │       │ .verse en Generated/ │
│ Editado por      │        │ Editado por DS/Opus│       │ NUNCA editado        │
│ humanos+IA       │        │ Genera artifacts   │       │ manualmente          │
└──────────────────┘        └────────────────────┘       └──────────┬───────────┘
                                                                     │
                                                                     ▼
                                                         ┌──────────────────────┐
                                                         │ RUNTIME              │
                                                         │ Verse importa el     │
                                                         │ artifact y lo usa    │
                                                         └──────────────────────┘
```

### 1.3 Ejemplo concreto

**❌ MAL**: DeepSeek escribe directamente en Verse:

```verse
# Content/Verse/Generated/Companions_Generated.verse
# Editado a mano por DeepSeek - ESTÁ MAL
GetCompanionDragonFire():companion_def= companion_def{ID := 1, BaseHP := 100, ...}
GetCompanionPixieForest():companion_def= companion_def{ID := 2, BaseHP := 50, ...}
# ... 300 entries más a mano
```

**✅ BIEN**: DeepSeek crea el script Python que genera ese archivo:

```python
# scripts/build/02_export_constants_to_verse.py
# Patrón canónico (post-SPR-211): struct<public> + module<public> + getters
# Ver docs/VERSE_SYNTAX_GUIDE.md §2.3.
import json

def to_pascal(name): return "".join(p.capitalize() for p in name.split("_"))

with open("data/companions/companions_base.json") as f:
    companions = json.load(f)["companions"]

with open("Content/Verse/Generated/Companions_Generated.verse", "w") as f:
    f.write("# AUTO-GENERATED. DO NOT EDIT MANUALLY.\n\n")
    f.write("companion_def<public> := struct:\n")
    f.write("    ID:int\n    BaseHP:int\n    BaseAtk:int\n\n")
    f.write("Companions_Generated<public> := module:\n")
    for c in companions:
        f.write(f"\n    GetCompanion{to_pascal(c['name'])}<public>():companion_def=\n")
        f.write(f"        companion_def{{ID := {c['id']}, BaseHP := {c['base_hp']}, BaseAtk := {c['base_atk']}}}\n")
```

Y luego se editan los JSONs:

```json
{
  "companions": [
    { "id": 1, "name": "DRAGON_FIRE", "base_hp": 100, "base_atk": 25 },
    { "id": 2, "name": "PIXIE_FOREST", "base_hp": 50, "base_atk": 15 }
  ]
}
```

**Resultado**: para añadir 100 criaturas más, **solo se edita el JSON**. El Verse se regenera con un comando.

---

## 2. Source of Truth: los JSONs

### 2.1 Estructura de carpeta `data/`

Ver `FOLDER_STRUCTURE_TRUTH.md` §3 para el árbol canónico de `data/`. Ese doc es el autoritativo para toda la estructura del proyecto (declarado así en `CONCEPT.md:1018`). El árbol legacy en `CONCEPT.md` §11.1 está marcado como obsoleto y NO debe usarse como fuente para transformers Python.

### 2.2 Reglas de oro de los JSONs

1. **Source of truth absoluto**. Si hay conflicto entre JSON y Verse generado, **el JSON gana** y se regenera.
2. **Validados antes de cada build** con `01_validate_jsons.py`.
3. **IDs nunca se renumeran**. Una vez que un companion tiene ID 5, siempre es ID 5.
4. **Esquema documentado** en `_comment` keys.
5. **Editables por humanos directamente** sin necesidad de IA.

### 2.3 Plantilla de JSON con esquema

```json
{
  "_schema_version": 1,
  "_doc": "Definición de companions base. Ver CONCEPT.md SYS-010.",
  "_validation": "scripts/build/01_validate_jsons.py debe pasar antes de commit.",

  "companions": [
    {
      "_comment_id": "ID único, no renumerar. Range 1-9999.",
      "id": 1,

      "_comment_name": "Nombre interno. UPPER_SNAKE_CASE. No cambiar tras publish.",
      "name": "DRAGON_FIRE",

      "_comment_display": "Nombre mostrado al jugador. Localizable.",
      "display_name_key": "companion.dragon_fire.name",

      "_comment_rarity": "1=Common, 2=Uncommon, 3=Rare, 4=Epic, 5=Legendary, 6=Mythic, 7=Secret, 8=Admin",
      "rarity": 5,

      "_comment_stats": "Stats base. Multiplicadores por variante en variants.json.",
      "base_hp": 100,
      "base_atk": 25,
      "base_def": 15,
      "base_speed": 12,

      "_comment_obtainable": "Todas las fuentes posibles. Ver SYS-038 Universal Obtainability Flag.",
      "obtainable_from": {
        "lootbox_premium": { "drop_rate": 0.05 },
        "boss_drops": ["FOREST_DRAGON"],
        "events": ["FIRE_FESTIVAL_2026"],
        "battle_pass": { "premium_level": 50 }
      },

      "_comment_mesh": "Path al mesh en Content/Assets/Meshes/Companions/",
      "mesh_path": "Content/Assets/Meshes/Companions/dragon_fire.fbx",

      "_comment_tradable": "Si false, NUNCA tradable (ej: items de V-Bucks).",
      "tradable": true
    }
  ]
}
```

---

## 3. Transformers: scripts Python

### 3.1 Categorías de transformers

| Categoría | Carpeta | Ejemplos |
|---|---|---|
| **Validators** | `scripts/build/0X_validate_*.py` | Validar JSON schemas, validar referencias entre archivos |
| **Generators** | `scripts/build/0X_export_*.py` | Generar `.verse` desde `.json` |
| **Procedural** | `scripts/build/0X_generate_*.py` | Generar layouts proceduralmente |
| **Theme** | `scripts/build/0X_apply_theme_*.py` | Aplicar theme pack masivo |
| **Memory** | `scripts/build/0X_check_*.py` | Validar memory budget |
| **Orchestrator** | `scripts/build/07_run_full_pipeline.py` | Ejecutar todo en orden |
| **Tools** | `scripts/tools/` | Helpers no críticos (visualizers, scaffolders) |

### 3.2 Reglas obligatorias para transformers Python

1. **Idempotencia**: ejecutar N veces da el mismo resultado.
2. **Sin lógica de gameplay**: solo transformar/generar.
3. **Logging detallado**: cada paso con `unreal.log()` o `print()` claro.
4. **Try/except** defensivo: el editor no crashea si el script falla.
5. **Argumentos vía argparse** si es ejecutable standalone.
6. **Type hints obligatorios** en funciones públicas.
7. **Docstrings Google-style** en funciones públicas.
8. **No hardcodear paths**: usar `unreal.SystemLibrary.get_project_directory()` o argumentos.

### 3.3 Estructura estándar de un transformer

```python
# scripts/build/02_export_constants_to_verse.py

"""
Export companions JSON to Verse constants.

Reads:  data/companions/companions_base.json
Writes: Content/Verse/Generated/Companions_Generated.verse

Idempotent: safe to run N times.
"""

import json
import sys
from pathlib import Path
from typing import Any

# === Constants ===
SOURCE_JSON = "data/companions/companions_base.json"
OUTPUT_VERSE = "Content/Verse/Generated/Companions_Generated.verse"

WARNING_HEADER = """\
# ============================================================
# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.
# Source: {source}
# Generated by: {script}
# ============================================================

"""


def load_companions(json_path: str) -> dict[str, Any]:
    """Load and validate companions JSON.

    Args:
        json_path: path to companions_base.json

    Returns:
        Parsed JSON dict.

    Raises:
        FileNotFoundError: if json doesn't exist.
        json.JSONDecodeError: if json is malformed.
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Source JSON not found: {json_path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def to_pascal_case(name: str) -> str:
    """snake/SNAKE → Pascal. Ej: DRAGON_FIRE -> DragonFire."""
    return "".join(p.capitalize() for p in name.split("_") if p)


def companion_getter_to_verse(companion: dict) -> str:
    """Convert one companion dict to Verse getter function (Patrón 3, post-SPR-211)."""
    pascal = to_pascal_case(companion["name"])
    return (
        f"    GetCompanion{pascal}<public>():companion_def=\n"
        f"        companion_def{{"
        f"ID := {companion['id']}, "
        f"Rarity := {companion['rarity']}, "
        f"BaseHP := {companion['base_hp']}, "
        f"BaseAtk := {companion['base_atk']}, "
        f"BaseDef := {companion['base_def']}, "
        f"BaseSpeed := {companion['base_speed']}"
        f"}}"
    )


def generate_verse_file(data: dict, output_path: str) -> None:
    """Generate the Verse output file (Patrón 3 — struct<public> + module<public> + getters)."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(WARNING_HEADER.format(
        source=SOURCE_JSON,
        script=Path(__file__).name
    ))
    lines.append("")
    lines.append("companion_def<public> := struct:")
    lines.append("    ID:int")
    lines.append("    Rarity:int")
    lines.append("    BaseHP:int")
    lines.append("    BaseAtk:int")
    lines.append("    BaseDef:int")
    lines.append("    BaseSpeed:int")
    lines.append("")
    lines.append("Companions_Generated<public> := module:")

    getter_names = []
    for companion in data["companions"]:
        getter_names.append(f"GetCompanion{to_pascal_case(companion['name'])}")
        lines.append("")
        lines.append(companion_getter_to_verse(companion))

    lines.append("")
    lines.append("    GetAllCompanions<public>():[]companion_def=")
    if getter_names:
        calls = ", ".join(f"{n}()" for n in getter_names)
        lines.append(f"        array{{ {calls} }}")
    else:
        lines.append("        array{}")

    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated: {output_path} ({len(data['companions'])} companions)")


def main() -> int:
    """Main entry point."""
    try:
        data = load_companions(SOURCE_JSON)
        generate_verse_file(data, OUTPUT_VERSE)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## 4. Artifacts: archivos Verse generados

### 4.1 Carpeta `Content/Verse/Generated/`

**Reglas**:
- ❌ **NUNCA editar manualmente**.
- ❌ **NUNCA refactorizar**.
- ✅ **Solo regenerar** ejecutando el transformer.
- ✅ **Cada archivo lleva header de warning** (ver plantilla 3.3).

### 4.2 Cuándo se regenera

- Cada vez que cambia el JSON fuente.
- Antes de cada `Build Verse Code`.
- Tras cualquier rama Git que toque `data/`.

### 4.3 Tipos de artifacts esperados

> **Decisión cerrada (v2.0)**: el export de constantes vive en **un único script** `scripts/build/02_export_constants_to_verse.py`. Internamente puede tener funciones modulares (`export_companions()`, `export_items()`, `export_quests()`, ...) pero el orquestador (`07_run_full_pipeline.py`) lo invoca **una vez**.
>
> **Por qué uno y no varios**: alineamiento con `FOLDER_STRUCTURE_TRUTH.md` §5 (script `02_export_constants_to_verse.py` único en `scripts/build/`) y SPR-004 ext. Más simple para el MVP, mismo tiempo total (los exports son operaciones I/O ligeras de segundos), refactorizable más adelante si es necesario.
>
> **Cuándo refactorizar a múltiples scripts**: si en F4–F5 el export tarda **>30 s** consistentemente, dividir en `02a_export_companions.py`, `02b_export_items.py`, etc. Hasta entonces, **un solo script con funciones internas**. Decisión a re-evaluar en cierre de F3.

| Archivo | Source | Generado por |
|---|---|---|
| `Companions_Generated.verse` | `data/companions/companions_base.json` | `02_export_constants_to_verse.py` (función `export_companions()`) |
| `Items_Generated.verse` | `data/items/*.json` | `02_export_constants_to_verse.py` (función `export_items()`) |
| `Quests_Generated.verse` | `data/quests/*.json` | `02_export_constants_to_verse.py` (función `export_quests()`) |
| `Prices_Generated.verse` | `data/economy/shop.json`, `pity_config.json`, `gold.json`, `gems.json` (precios y caps) | `02_export_constants_to_verse.py` (función `export_prices()`) |
| `BattlePass_Generated.verse` | `data/progression/battle_pass_seasons/season_XX.json` | `02_export_constants_to_verse.py` (función `export_battle_pass()`) |
| `PlayerStats_Generated.verse` | `data/progression/player_stats_base.json` | `02_export_constants_to_verse.py` (función `export_player_stats()`) |
| `SkillTree_Generated.verse` | `data/progression/skill_trees.json` | `02_export_constants_to_verse.py` (función `export_skill_tree()`) |
| `Achievements_Generated.verse` | `data/progression/achievements.json` | `02_export_constants_to_verse.py` (función `export_achievements()`) |
| `Localization_Generated.verse` | `data/theme/localization_keys.json` | `02_export_constants_to_verse.py` (función `export_localization()`) |
| `ModuleRegistryConstants.verse` ⚙️ | `data/architecture/modules_manifest.json` | `02_export_constants_to_verse.py` (función `export_module_registry()` — ver §10 para spec completa) |
| `EventBusDevice.verse` ⚙️ | `data/architecture/events_catalog.json` | `02_export_constants_to_verse.py` (función `export_event_bus()` — device generado (creative_device) que expone propiedades event(t) tipadas; ver §11 para spec completa) |
| `EventPayloads_Generated.verse` ⚙️ | `data/architecture/events_catalog.json` | `02_export_constants_to_verse.py` (función `export_event_payloads()` — ver §11 para spec completa) |
| `BalanceCurves_Generated.verse` 📐 | `BALANCE_FORMULAS.md` (curvas tabuladas) | `02_export_constants_to_verse.py` (función `export_balance_curves()` — SPR-134) |
| `Zones_Generated.verse` | `data/zones/zone_definitions.json` | `04_generate_zone_layouts.py` |
| `ThemeConstants_Generated.verse` | `data/theme/theme_config.json` | `05_apply_theme_pack.py` |

> **Leyenda**: ⚙️ artifacts arquitectónicos (Auditoría 2 — C1+C3; nombre semántico sin sufijo `_Generated` por excepción canónica — ver §4.4). 📐 artifact derivado de markdown autoritativo en lugar de JSON, único caso (SPR-134).
>
> **15 artifacts totales** = 12 generados por `02_export_constants_to_verse.py` (el script "central") + 1 por `04_generate_zone_layouts.py` (procedural) + 1 por `05_apply_theme_pack.py` (theme) + 1 caso especial (BalanceCurves desde markdown). Coherente con `FOLDER_STRUCTURE_TRUTH.md` §4 árbol Generated/ (15 archivos) y §4.1 resumen.

### 4.4 Patrón de naming

**Decisión cerrada (v2.0)**: todos los archivos generados llevan sufijo `_Generated.verse`.

```
Content/Verse/Generated/{Nombre}_Generated.verse
```

**Reglas**:
- `{Nombre}` = `PascalCase`, generalmente plural si agrupa entidades (`Companions`, `Items`) o singular si es un dato único (`Localization`, `BattlePass`).
- Sufijo `_Generated` **obligatorio** — comunica visualmente "no editar manualmente".
- El **nombre del módulo Verse coincide con el del archivo**: `Companions_Generated.verse` ⇒ `Companions_Generated := module:`.

Ejemplos canónicos (ver `FOLDER_STRUCTURE_TRUTH.md` §4):
- `Companions_Generated.verse`
- `Items_Generated.verse`
- `Quests_Generated.verse`
- `BalanceCurves_Generated.verse`
- `BattlePass_Generated.verse`

**Excepciones** (sufijo distinto justificado — coherente con regex validador en `FOLDER_STRUCTURE_TRUTH.md` §8.2 línea 522):
- `ModuleRegistryConstants.verse` — workaround del SPR-005 (Auditoría 2 — C1). Genera getters tipados estáticos para Systems registrables (Verse no soporta `<T>` runtime). Spec completa en §10. Decisión D-A10 en `CHANGELOG.md`.
- `EventBusDevice.verse` — workaround del SPR-009 (Auditoría 2 — C3 + H4 SPR-009 F-C-2). `class<concrete>(creative_device)` con propiedades `event(payload_t)` tipadas, una por entrada del catálogo. NO usa sufijo `_Generated` ni sufijo `Constants` (el archivo es un device, no constantes — naming refleja la naturaleza arquitectónica). Spec completa en §11. Decisiones D-A10 + D-A11 en `CHANGELOG.md`.

> **Nota (Auditoría 3 — H3.5)**: solo estos 2 archivos son excepciones reales. `ThemeConstants_Generated.verse` **NO es excepción** — sí lleva sufijo `_Generated`; el prefijo `ThemeConstants` es solo el nombre semántico del contenido (constantes de tema). Pertenece a la regla normal `<Nombre>_Generated.verse`. La lista de excepciones canónica son ÚNICAMENTE los 2 de arriba.

---

## 5. Inyección en runtime: cómo Verse usa los artifacts

### 5.1 Patrón estándar

El Verse manual (en `Systems/`) **importa** el módulo generado y **usa los datos**:

```verse
# Content/Verse/Systems/Companions/CompanionCore.verse
# Editado manualmente - lógica de runtime.

# Path Verse: <ProjectName> = root del proyecto UEFN.
# La carpeta Content/Verse/ NO aparece en el path; el root Verse se mapea
# directo. Separadores SIEMPRE `/`, nunca `.`.
using { /<ProjectName>/Generated }

companion_core := module:

    GetCompanionDefinition<public>(ID:int):?companion_def=
        # Búsqueda en las constantes generadas
        for (Companion : Companions_Generated.GetAllCompanions()):
            if (Companion.ID = ID):
                return option{Companion}
        return false

    SpawnCompanion<public>(InPlayer:player, ID:int)<suspends>:logic=
        # Usar definición desde el JSON
        Def := GetCompanionDefinition[ID]?
        # ... lógica con Def.BaseHP, Def.BaseAtk, etc.
```

### 5.2 Las constantes son inmutables en runtime

- Se cargan en compile-time.
- No se pueden modificar mientras el juego corre.
- Si necesitas cambios dinámicos: usar variables Verse separadas, **no tocar el módulo Generated**.

---

## 6. Anti-patrones (lo que DeepSeek NUNCA debe hacer)

### 6.1 ❌ Anti-patrón 1: hardcodear datos en Verse manual

**MAL**:
```verse
# Systems/Companions/CompanionCore.verse
companion_core := module:

    DRAGON_DEFAULT_HP := 100  # ❌ Hardcoded
    DRAGON_DEFAULT_ATK := 25  # ❌ Hardcoded
```

**BIEN**:
```verse
# Systems/Companions/CompanionCore.verse
using { Verse.Generated.Companions_Generated }

companion_core := module:

    GetDragonDefaults():companion_def=
        Companions_Generated.GetCompanionDragonFire()  # ✅ Desde generated (Patrón 3 SPR-211)
```

### 6.2 ❌ Anti-patrón 2: editar archivos de `Generated/`

**MAL**:
```verse
# Generated/Companions_Generated.verse
# DeepSeek edita aquí para "ajustar" un valor.  ← ❌ NO
GetCompanionDragonFire():companion_def= companion_def{ID := 1, BaseHP := 150, ...}
```

**BIEN**:
```json
// data/companions/companions_base.json
// Editar el valor aquí
{ "id": 1, "name": "DRAGON_FIRE", "base_hp": 150, ... }
```

Y luego ejecutar el transformer.

### 6.3 ❌ Anti-patrón 3: lógica de gameplay en Python

**MAL**:
```python
# scripts/build/...py
# Python decidiendo gameplay  ← ❌
if player_level > 50:
    give_special_reward()
```

Python **NO** corre en runtime. Esto solo afectaría al build, no al juego.

**BIEN**:
```python
# Python solo genera datos
config = {"reward_threshold": 50, "reward_type": "special"}
generate_verse_constant("RewardConfig", config)
```

```verse
# Verse aplica la lógica en runtime
if (PlayerLevel > RewardConfig.Threshold):
    GiveReward(Player, RewardConfig.Type)
```

### 6.4 ❌ Anti-patrón 4: leer JSONs en Verse runtime

Verse **NO PUEDE leer archivos JSON en runtime**. Solo en compile-time vía artifacts generados.

**MAL** (no compila siquiera):
```verse
companion_core := module:
    LoadCompanions():void=
        # ❌ Esto no existe en Verse runtime
        Json := File.Read("data/companions/companions_base.json")
```

**BIEN**:
- Python genera `Companions_Generated.verse` desde el JSON al hacer build.
- Verse importa el módulo Generated.

### 6.5 ❌ Anti-patrón 5: bypass del transformer

**MAL**: editar JSON y luego copiar valores a mano al .verse generated.

**BIEN**: editar JSON → ejecutar transformer → automáticamente regenera el .verse.

---

## 7. Pipeline completo paso a paso

### 7.1 Diagrama del pipeline

```
   ┌─────────────────────┐
   │ EDITAR JSON         │
   │ data/...json        │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ VALIDAR ESTRUCTURA  │
   │ 00_validate_structure│
   └──────────┬──────────┘
              │ pass
              ▼
   ┌─────────────────────┐
   │ VALIDAR JSONS       │
   │ 01_validate_jsons   │
   └──────────┬──────────┘
              │ pass
              ▼
   ┌─────────────────────┐
   │ EXPORT TO VERSE     │
   │ 02_export_constants │ ──► Generated/*_Generated.verse
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ PROCEDURAL CONTENT  │ (si aplica al cambio)
   │ 03_generate_*       │ ──► spawns/places actors
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ THEME APPLY         │ (si cambió theme_config)
   │ 05_apply_theme      │ ──► swaps assets bulk
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ MEMORY CHECK        │
   │ 06_check_memory     │ ──► report o error
   └──────────┬──────────┘
              │ pass
              ▼
   ┌─────────────────────┐
   │ BUILD VERSE         │ ◄── manual en UEFN (Ctrl+Shift+B)
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ PUSH CHANGES        │ ◄── manual en UEFN
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ TEST IN-SESSION     │
   │ + Mobile Preview    │
   └─────────────────────┘
```

### 7.2 Script orquestador

`scripts/build/07_run_full_pipeline.py` ejecuta los pasos 0-6 en secuencia con manejo de errores.

```python
# scripts/build/07_run_full_pipeline.py
"""Full build pipeline orchestrator. Run this for any data change."""

import subprocess
import sys
from pathlib import Path

STEPS = [
    "00_validate_structure.py",
    "01_validate_jsons.py",
    "02_export_constants_to_verse.py",
    "03_generate_companion_prefabs.py",
    "04_generate_zone_layouts.py",
    "05_apply_theme_pack.py",
    "06_check_memory_budget.py",
]

def run_step(script_name: str) -> bool:
    """Run a build step. Returns True if successful."""
    script_path = Path(__file__).parent / script_name
    print(f"\n=== Running {script_name} ===")
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        print(f"❌ Step failed: {script_name}")
        return False
    return True

def main() -> int:
    for step in STEPS:
        if not run_step(step):
            print("\n💥 Pipeline aborted.")
            return 1
    print("\n✅ Pipeline complete. Now: Build Verse Code → Push Changes.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 8. Plantillas de scripts Python

### 8.1 Plantilla validador

```python
# scripts/build/01_validate_jsons.py
"""Validate all JSONs in data/ against expected schemas."""

import json
import sys
from pathlib import Path

ERRORS = []

def validate_companions(data: dict) -> None:
    """Validate companions_base.json schema."""
    if "companions" not in data:
        ERRORS.append("Missing 'companions' key")
        return

    seen_ids = set()
    for c in data["companions"]:
        # Required fields
        for field in ["id", "name", "rarity", "base_hp", "base_atk"]:
            if field not in c:
                ERRORS.append(f"Companion missing field: {field}")

        # ID uniqueness
        if c["id"] in seen_ids:
            ERRORS.append(f"Duplicate ID: {c['id']}")
        seen_ids.add(c["id"])

        # Rarity range
        if not 1 <= c["rarity"] <= 8:
            ERRORS.append(f"Invalid rarity for {c['name']}: {c['rarity']}")

def validate_all() -> int:
    """Run all validators. Returns exit code."""
    json_files = {
        "data/companions/companions_base.json": validate_companions,
        # ... más validators ...
    }

    for path, validator in json_files.items():
        try:
            with open(path) as f:
                data = json.load(f)
            validator(data)
        except FileNotFoundError:
            ERRORS.append(f"File not found: {path}")
        except json.JSONDecodeError as e:
            ERRORS.append(f"JSON parse error in {path}: {e}")

    if ERRORS:
        print("❌ Validation failed:")
        for err in ERRORS:
            print(f"  - {err}")
        return 1
    else:
        print("✅ All JSONs valid.")
        return 0

if __name__ == "__main__":
    sys.exit(validate_all())
```

### 8.2 Plantilla generator (procedural)

```python
# scripts/build/04_generate_zone_layouts.py
"""Generate zone layouts: distribute resource nodes, place props."""

import json
import math
import random
from typing import Any

try:
    import unreal
    UEFN_AVAILABLE = True
except ImportError:
    UEFN_AVAILABLE = False
    print("⚠️ Running outside UEFN - asset spawning skipped.")


def poisson_disk_sampling(width: float, height: float, min_dist: float, k: int = 30) -> list[tuple[float, float]]:
    """Generate Poisson disk distribution of points."""
    # ... algoritmo Bridson ...
    pass


def populate_zone_with_nodes(zone_def: dict) -> None:
    """Spawn resource nodes in a zone using Poisson distribution."""
    if not UEFN_AVAILABLE:
        return

    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    points = poisson_disk_sampling(
        width=zone_def["width"],
        height=zone_def["height"],
        min_dist=zone_def["min_node_distance"]
    )

    for x, y in points:
        location = unreal.Vector(x, y, 0)
        # Spawn the node actor
        actor_sub.spawn_actor_from_class(
            unreal.Actor,  # placeholder
            location
        )


def main() -> int:
    with open("data/zones/zone_definitions.json") as f:
        zones = json.load(f)

    for zone in zones["zones"]:
        print(f"Generating zone: {zone['name']}")
        populate_zone_with_nodes(zone)

    return 0


if __name__ == "__main__":
    main()
```

---

## 9. Plantillas de Verse generado

### 9.1 Plantilla básica (Patrón 3 — post-SPR-211)

> **Sintaxis Verse moderna**: ver `docs/VERSE_SYNTAX_GUIDE.md` §2.3. Las constantes legacy `NAME := companion_def{...}` top-level fallan con err 3512 (lecciones 11+12). API canónica = funciones getter, no constantes nombradas.

```verse
# Content/Verse/Generated/Companions_Generated.verse
# ============================================================
# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.
# Source: data/companions/companions_base.json
# Generated by: 02_export_constants_to_verse.py (export_companions)
# Refactor SPR-211: structs literales top-level propagan transacts
# (err 3512). API canonica = funciones getter, no constantes nombradas.
# ============================================================

companion_def<public> := struct:
    ID:int
    Rarity:int
    BaseHP:int
    BaseAtk:int
    BaseDef:int
    BaseSpeed:int

Companions_Generated<public> := module:

    GetCompanionDragonFire<public>():companion_def=
        companion_def{ID := 1, Rarity := 5, BaseHP := 100, BaseAtk := 25, BaseDef := 15, BaseSpeed := 12}

    GetCompanionPixieForest<public>():companion_def=
        companion_def{ID := 2, Rarity := 3, BaseHP := 50, BaseAtk := 15, BaseDef := 8, BaseSpeed := 18}

    # ... un getter por entrada ...

    GetAllCompanions<public>():[]companion_def=
        array{ GetCompanionDragonFire(), GetCompanionPixieForest() }

    GetCompanionByID<public>(ID:int):?companion_def=
        for (C : GetAllCompanions()):
            if (C.ID = ID):
                option{C}
        false
```

### 9.2 Plantilla con enums

```verse
# Content/Verse/Generated/Rarity_Generated.verse
# AUTO-GENERATED. DO NOT EDIT.

Rarity_Generated := module:

    rarity := enum:
        Common
        Uncommon
        Rare
        Epic
        Legendary
        Mythic
        Secret
        Admin

    GetRarityColor<public>(R:rarity):int=  # color hex
        case (R):
            rarity.Common => 0x9CA3AF
            rarity.Uncommon => 0x22C55E
            rarity.Rare => 0x3B82F6
            rarity.Epic => 0xA855F7
            rarity.Legendary => 0xF97316
            rarity.Mythic => 0xEF4444
            rarity.Secret => 0x000000
            rarity.Admin => 0xFCD34D
```

---

## 10. Patrón Core estático vs Systems registrables (C1)

> **Sección añadida en Auditoría 2 — C1.** Resuelve la pregunta: si Verse no tiene reflexión runtime, ¿cómo orquestamos la comunicación entre módulos?

### 10.1 Dos clases de módulos del proyecto

| Clase | Quiénes | Cómo se accede | Se registra en Registry |
|---|---|---|---|
| **Core estáticos** | `Logger`, `EventBus`, `TimeSync`, `PersistenceLayer`, `BigNumbers`, `AdminCommands`, `ModuleRegistry` | `using { /<ProjectName>/Core/<X> }` directo | ❌ No |
| **Systems registrables** | `PlayerStats`, `PlayerInventory`, `PlayerProgression`, `CompanionCore`, `CurrencyManager`, `BattlePass`, etc. (Capa 2+) | `Registry.Get<X>():?<x>_module` | ✅ Sí |

**Regla**: si dos Systems se necesitan mutuamente y un `using {}` cruzado crearía ciclo de import → ambos pasan por Registry. Si la dep es unidireccional → `using {}` directo es suficiente.

### 10.2 Por qué hace falta el manifest JSON

Verse **no soporta reflexión runtime** (no hay `typeof`, no hay `GetModule<T>()` genérico). La solución es:

1. Declarar en JSON qué Systems se registran.
2. Python lee el JSON y **genera código Verse estático** con un getter tipado por sistema.
3. Verse compila el código generado con tipos concretos — sin genéricos runtime.

### 10.3 JSON manifest spec

**Path**: `data/architecture/modules_manifest.json`

```json
{
  "_schema_version": 1,
  "_doc": "Lista de Systems registrables en ModuleRegistry. SOLO Systems Capa 2+. Los Core no van aquí.",
  "_validation": "scripts/build/01_validate_jsons.py debe pasar antes de commit.",

  "registrable_systems": [
    {
      "id": "player_stats",
      "module_name": "player_stats_module",
      "verse_path": "/<ProjectName>/Systems/Player/PlayerStats",
      "layer": 2,
      "phase": "F1",
      "_comment": "Stats base del jugador. Se registra en GameManager.OnBegin."
    },
    {
      "id": "player_inventory",
      "module_name": "player_inventory_module",
      "verse_path": "/<ProjectName>/Systems/Player/PlayerInventory",
      "layer": 2,
      "phase": "F1"
    },
    {
      "id": "currency_manager",
      "module_name": "currency_manager_module",
      "verse_path": "/<ProjectName>/Systems/Economy/CurrencyManager",
      "layer": 2,
      "phase": "F3"
    }
  ]
}
```

**Reglas del schema**:

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | string | snake_case único, inmutable. Usado para nombrar getter (`GetPlayerStats`). |
| `module_name` | string | `<id>_module`. Tipo Verse del Systems. Debe coincidir con declaración en `.verse` real. |
| `verse_path` | string | Path Verse completo. Validador `dependency_cycle_check.py` lo verifica. |
| `layer` | int | 2, 3 o 4. Capa 0/1/5 prohibido (Core/Generated/Devices no se registran). |
| `phase` | string | F1–F5. Sirve para que el generador comente en qué fase aparece. |

**Validaciones cruzadas**:
- `id` único en todo el manifest.
- `module_name` único.
- Si `layer == 2`, `phase` debe ser F1 o F2.
- Si `layer == 3`, `phase` debe ser F1, F2 o F3.
- Si `layer == 4`, `phase` puede ser F2–F5.

### 10.4 Plantilla del Verse generado

```verse
# Content/Verse/Generated/ModuleRegistryConstants.verse
# ============================================================
# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.
# Source: data/architecture/modules_manifest.json
# Generated by: 02_export_constants_to_verse.py (función export_module_registry())
# Date: <timestamp>
# ============================================================

# Forward declarations de los module types — los .verse de cada Systems
# definen el tipo real. Aquí solo se referencian.
using { /<ProjectName>/Systems/Player/PlayerStats }
using { /<ProjectName>/Systems/Player/PlayerInventory }
using { /<ProjectName>/Systems/Economy/CurrencyManager }
# ... un using por Systems registrable ...

module_registry := class<concrete>:
    # === Slots de cada Systems registrable ===
    var MaybePlayerStats:?player_stats_module = false
    var MaybePlayerInventory:?player_inventory_module = false
    var MaybeCurrencyManager:?currency_manager_module = false
    # ... un slot por sistema ...

    # === Setters (uno por sistema) ===
    RegisterPlayerStats<public>(M:player_stats_module):void=
        set MaybePlayerStats = option{M}

    RegisterPlayerInventory<public>(M:player_inventory_module):void=
        set MaybePlayerInventory = option{M}

    RegisterCurrencyManager<public>(M:currency_manager_module):void=
        set MaybeCurrencyManager = option{M}

    # === Getters tipados (uno por sistema) ===
    GetPlayerStats<public>():?player_stats_module=
        MaybePlayerStats

    GetPlayerInventory<public>():?player_inventory_module=
        MaybePlayerInventory

    GetCurrencyManager<public>():?currency_manager_module=
        MaybeCurrencyManager

# Singleton top-level. Verse lo inicializa antes de cualquier OnBegin.
Registry<public> : module_registry = module_registry{}
```

### 10.5 Plantilla del transformer Python

```python
# scripts/build/02_export_constants_to_verse.py (función export_module_registry)
"""
Generate ModuleRegistryConstants.verse from modules_manifest.json.
Idempotent.
"""

import json
from pathlib import Path
from typing import Any

MANIFEST_PATH = "data/architecture/modules_manifest.json"
OUTPUT_PATH = "Content/Verse/Generated/ModuleRegistryConstants.verse"


def export_module_registry() -> None:
    with open(MANIFEST_PATH) as f:
        manifest: dict[str, Any] = json.load(f)

    systems = manifest["registrable_systems"]

    lines: list[str] = []
    lines.append("# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.")
    lines.append(f"# Source: {MANIFEST_PATH}")
    lines.append("# See BOOTSTRAP_PIPELINE.md §10 for rationale.\n")

    # using {} statements
    for s in systems:
        lines.append(f"using {{ {s['verse_path']} }}")
    lines.append("")

    # class definition
    lines.append("module_registry := class<concrete>:")
    for s in systems:
        pascal = _to_pascal(s["id"])
        lines.append(f"    var Maybe{pascal}:?{s['module_name']} = false")
    lines.append("")

    # Register* setters
    for s in systems:
        pascal = _to_pascal(s["id"])
        lines.append(f"    Register{pascal}<public>(M:{s['module_name']}):void=")
        lines.append(f"        set Maybe{pascal} = option{{M}}")
        lines.append("")

    # Get* getters
    for s in systems:
        pascal = _to_pascal(s["id"])
        lines.append(f"    Get{pascal}<public>():?{s['module_name']}=")
        lines.append(f"        Maybe{pascal}")
        lines.append("")

    # singleton top-level
    lines.append("Registry<public> : module_registry = module_registry{}")

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_PATH).write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT_PATH} with {len(systems)} systems")


def _to_pascal(snake: str) -> str:
    return "".join(part.capitalize() for part in snake.split("_"))
```

### 10.6 Patrón de uso runtime

**Registrarse (en `OnBegin` del device que arranca el Systems)**:

```verse
# En Devices/GameManager.verse o similar
using { /<ProjectName>/Generated/ModuleRegistryConstants }
using { /<ProjectName>/Systems/Player/PlayerStats }

game_manager := class(creative_device):
    PlayerStatsInstance:player_stats_module = player_stats_module{}

    OnBegin<override>()<suspends>:void=
        # Init de cada Systems
        PlayerStatsInstance.Init()
        # Registro
        Registry.RegisterPlayerStats(PlayerStatsInstance)
        # ... resto de Systems ...
```

**Consumir (desde otro Systems sin import compile-time)**:

```verse
# En Systems/Quests/QuestEngine.verse
using { /<ProjectName>/Generated/ModuleRegistryConstants }

quest_engine := class:
    ValidateQuestRequirements<public>(InPlayer:player, QuestID:int):logic=
        if (PStats := Registry.GetPlayerStats()?):
            return PStats.GetLevel(InPlayer) >= GetMinLevel(QuestID)
        return false  # Systems aún no registrado → bloqueo silencioso
```

### 10.7 Cuándo añadir un sistema al manifest

Añadir un sistema a `modules_manifest.json` cuando se cumpla **al menos una** de estas condiciones:

1. Otro sistema lo necesita pero un `using {}` crearía ciclo de import.
2. Múltiples sistemas lo consumen y queremos un punto único de acceso.
3. El sistema mantiene estado runtime que distintos consumidores deben compartir.

**No añadir** al manifest si:
- Es un Core (siempre acceso directo).
- Solo un consumidor único lo usa (mejor `using {}` directo).
- Es un módulo de funciones puras sin estado (BigNumbers-style).

### 10.8 Validación y CI

`scripts/build/01_validate_jsons.py` debe verificar:

- Schema de `modules_manifest.json` correcto.
- `id`, `module_name`, `verse_path` únicos.
- Cada `verse_path` apunta a un `.verse` que existe.
- Cada `module_name` declarado en el manifest aparece en el `.verse` correspondiente.
- Layer correcto según fase (reglas §10.3).

Drift entre manifest y código real → exit 1 → no merge.

---

## 11. EventBus tipado generado (C3)

> **Sección añadida en Auditoría 2 — C3.** Resuelve la pregunta: ¿cómo emitimos/escuchamos eventos cross-system con type-safety compile-time, sin string-magic ni `Payload:any`?

### 11.1 Por qué `event(t)` nativo de Verse cambia el plan original

El plan inicial (auditoría) proponía construir un EventBus custom con `map<string, []handler>` interno y validación runtime de payloads. **Re-verificación contra `Verse.digest`**: Verse YA tiene parametric type nativo:

```verse
event<native><public>(t:type)<computes> := class(signalable(t), awaitable(t))
listenable<public>(payload:type) := interface(awaitable(payload), subscribable(payload))
signalable<public>(payload:type) := interface
awaitable<public>(payload:type) := interface
subscribable<public>(t:type) := interface
```

Fuente: [forums.unrealengine.com — Multicast Delegate Equivalent in UEFN Verse](https://forums.unrealengine.com/t/multicast-delegate-equivalent-in-uefn-verse/1232137).

**Implicación**: el EventBus del proyecto se construye **componiendo** instancias de `event(payload_t)` nativas, una por cada evento del catálogo. Type-safety garantizada por el compilador. Sin strings, sin runtime checks, sin `any`.

### 11.2 Dos archivos generados desde un único JSON

| Generado | Contenido | Quién lo importa |
|---|---|---|
| `Generated/EventPayloads_Generated.verse` | Structs de payloads (uno por evento) | Tanto emisores como suscriptores (importan el struct para construir/leer payload) |
| `Generated/EventBusDevice.verse` | `event_bus_device := class<concrete>(creative_device)` con propiedades `event(payload_t)` | Cualquier device que emita o escuche eventos cross-system, vía `@editable Bus:event_bus_device` (NO singleton top-level — patrón H4) |

**Por qué dos archivos**: separación de responsabilidades. Los structs son datos puros, el bus es la composición de eventos. Un Systems puede importar solo los payloads que necesita sin arrastrar todo el bus si no quiere.

### 11.3 JSON catalog spec

**Path**: `data/architecture/events_catalog.json`

Schema completo en `JSON_SCHEMAS.md` §42. Ejemplo mínimo:

```json
{
  "_schema_version": 1,
  "events": [
    {
      "id": "level_up",
      "verse_struct_name": "level_up_payload",
      "verse_event_name": "LevelUp",
      "emitters": ["PlayerProgression"],
      "subscribers": ["HUDController", "Notifications", "BattlePass", "AchievementEngine"],
      "payload_fields": [
        {"name": "Player", "type": "player"},
        {"name": "OldLevel", "type": "int"},
        {"name": "NewLevel", "type": "int"}
      ]
    }
  ]
}
```

### 11.4 Plantilla `EventPayloads_Generated.verse`

```verse
# Content/Verse/Generated/EventPayloads_Generated.verse
# ============================================================
# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.
# Source: data/architecture/events_catalog.json
# Generated by: 02_export_constants_to_verse.py (función export_event_payloads())
# ============================================================

# Un struct por cada evento del catálogo.
# Persistencia NO requerida — los payloads viven en RAM durante el ciclo del evento.

level_up_payload<public> := struct:
    Player<public>:player
    OldLevel<public>:int = 0
    NewLevel<public>:int = 0

player_stats_changed_payload<public> := struct:
    Player<public>:player
    Stat<public>:string = ""
    OldValue<public>:int = 0
    NewValue<public>:int = 0

# ... un struct por cada entrada del catálogo ...
# NOTA (Auditoría retro B1.2): el campo Player:player NO tiene default literal — Verse no permite
# default para tipos no-construibles vacíos. Es campo obligatorio en construcción del struct.
# El generador Python (TYPE_MAP en §11.6) trata "player" y "agent" como sin default y omite el "= ...".
```

### 11.5 Plantilla `EventBusDevice.verse`

> **⚠️ Patrón H4 (post-SPR-009 F-C-2)**: el EventBus operativo NO es singleton top-level. Es un `creative_device` que se instancia en Main.umap y se referencia desde otros devices vía `@editable`. Razón: `event(t){}` top-level falla con err 3512 (propaga `<transacts>` al contexto top-level `<computes>` puro, mismo patrón que lección 11 VERSE_SYNTAX_GUIDE — formalizado como lección 16 post-F-C-4-L1b). Solución vigente: encapsular las propiedades `event(t)` dentro de `class<concrete>(creative_device)`. Detalle del descubrimiento + lección canónica en `VERSE_SYNTAX_GUIDE.md` §1 lección 16.

```verse
# Content/Verse/Generated/EventBusDevice.verse
# ============================================================
# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.
# Source: data/architecture/events_catalog.json
# Generated by: 02_export_constants_to_verse.py (función export_event_bus())
# ============================================================

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /<ProjectName>/Generated/EventPayloads_Generated }

event_bus_device<public> := class<concrete>(creative_device):
    # Una propiedad event(t) por cada entrada del catálogo.
    # Cada event(t) builtin Verse v1 = class(signalable(t), awaitable(t)).
    # NO implementa subscribable — patrón consumer = spawn{} + Await loop (ver §11.7).
    LevelUp<public>:event(level_up_payload) = event(level_up_payload){}
    PlayerStatsChanged<public>:event(player_stats_changed_payload) = event(player_stats_changed_payload){}
    InventoryChanged<public>:event(inventory_changed_payload) = event(inventory_changed_payload){}
    # ... una por cada entrada ...

# NOTA: NO hay singleton top-level. La instancia operativa se coloca en Main.umap como
# actor del nivel y se referencia desde otros devices vía @editable Bus:event_bus_device.
```

### 11.6 Plantilla del transformer Python

```python
# scripts/build/02_export_constants_to_verse.py (funciones export_event_payloads + export_event_bus)
"""
Generate EventPayloads_Generated.verse and EventBusDevice.verse from events_catalog.json.
Idempotent.

Patrón H4 (post-SPR-009 F-C-2): EventBusDevice es class<concrete>(creative_device).
Razón en VERSE_SYNTAX_GUIDE §1 lección 16.
"""

import json
from pathlib import Path
from typing import Any

CATALOG_PATH = "data/architecture/events_catalog.json"
PAYLOADS_OUT = "Content/Verse/Generated/EventPayloads_Generated.verse"
BUS_OUT = "Content/Verse/Generated/EventBusDevice.verse"

# Mapping JSON type → Verse type
TYPE_MAP: dict[str, str] = {
    "int": "int",
    "float": "float",
    "string": "string",
    "logic": "logic",
    "player": "player",
    "agent": "agent",
    "int_array": "[]int",
    "string_array": "[]string",
}

DEFAULT_MAP: dict[str, str] = {
    "int": "0",
    "float": "0.0",
    "string": '""',
    "logic": "false",
    "int_array": "array{}",
    "string_array": "array{}",
}


def export_event_payloads() -> None:
    with open(CATALOG_PATH) as f:
        catalog: dict[str, Any] = json.load(f)

    lines: list[str] = [
        "# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.",
        f"# Source: {CATALOG_PATH}",
        "# See BOOTSTRAP_PIPELINE.md §11 for rationale.\n",
    ]

    for ev in catalog["events"]:
        struct_name = ev["verse_struct_name"]
        lines.append(f"{struct_name}<public> := struct:")
        for field in ev["payload_fields"]:
            verse_type = TYPE_MAP[field["type"]]
            default = DEFAULT_MAP.get(field["type"], "")
            if default:
                lines.append(f"    {field['name']}<public>:{verse_type} = {default}")
            else:
                # player/agent no tienen default literal — campo obligatorio en construcción
                lines.append(f"    {field['name']}<public>:{verse_type}")
        lines.append("")

    Path(PAYLOADS_OUT).parent.mkdir(parents=True, exist_ok=True)
    Path(PAYLOADS_OUT).write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {PAYLOADS_OUT} with {len(catalog['events'])} payloads")


def export_event_bus() -> None:
    with open(CATALOG_PATH) as f:
        catalog: dict[str, Any] = json.load(f)

    lines: list[str] = [
        "# AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.",
        f"# Source: {CATALOG_PATH}",
        "# See BOOTSTRAP_PIPELINE.md §11 for rationale.\n",
        "using { /Fortnite.com/Devices }",
        "using { /Verse.org/Simulation }",
        "using { /<ProjectName>/Generated/EventPayloads_Generated }\n",
        "event_bus_device<public> := class<concrete>(creative_device):",
    ]

    for ev in catalog["events"]:
        ev_name = ev["verse_event_name"]
        struct_name = ev["verse_struct_name"]
        lines.append(
            f"    {ev_name}<public>:event({struct_name}) = event({struct_name}){{}}"
        )

    lines.append("")
    lines.append("# NO singleton top-level — el device se instancia en Main.umap.")

    Path(BUS_OUT).parent.mkdir(parents=True, exist_ok=True)
    Path(BUS_OUT).write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {BUS_OUT} with {len(catalog['events'])} events")
```

### 11.7 Patrón de uso runtime

> **Patrón H4 (post-SPR-009 F-C-2)**: el `event_bus_device` se referencia desde otros devices vía `@editable`. **NO existe `.Subscribe()`** en `event(t)` builtin Verse v1 (la primitiva implementa `signalable + awaitable` only, NO `subscribable`). El consumer canónico es `spawn{}` + `Await()` loop. Detalle en `VERSE_SYNTAX_GUIDE.md` §1 lección 16.

**Referenciar el bus desde otro device**:

```verse
# En cualquier creative_device consumidor (Systems gameplay, etc.)
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /<ProjectName>/Generated/EventBusDevice }
using { /<ProjectName>/Generated/EventPayloads_Generated }

player_progression_device := class(creative_device):
    # Drag & drop la instancia de EventBusDevice en UEFN al editar este device.
    @editable Bus:event_bus_device = event_bus_device{}

    OnBegin<override>()<suspends>:void=
        # Producer y consumer setup van aquí.
```

**Producer — emitir un evento (Signal síncrono)**:

```verse
# Dentro de PlayerProgression cuando el jugador sube de nivel.
# Player es la referencia nativa Verse (la que ya pasa por las APIs de Fortnite y es key de weak_map).
#
# IMPORTANTE: Signal() es SÍNCRONO en Verse v1 — los Await suspendidos resumen DENTRO de la
# llamada Signal antes de que Signal retorne. NO es fire-and-forget asíncrono.
Bus.LevelUp.Signal(level_up_payload{
    Player := InPlayer
    OldLevel := OldLevel
    NewLevel := NewLevel
})
```

**Consumer — escuchar un evento (Await loop)**:

```verse
# Dentro de AchievementEngine.OnBegin del device.
# Patrón canónico: spawn{} encapsula la corutina, loop{} mantiene el listener vivo,
# Await() suspende hasta el próximo Signal.
#
# IMPORTANTE: Sleep(0.0) post-spawn es OBLIGATORIO para que el task entre en Await
# ANTES del primer Signal. Sin él, race condition: si Signal ocurre antes de que el
# spawned task alcance Await, el evento se pierde silenciosamente.

OnBegin<override>()<suspends>:void=
    spawn { ListenLevelUp() }
    Sleep(0.0)  # cede control al scheduler — el spawned task entra en Await ahora.
    # ... resto de OnBegin ...

ListenLevelUp()<suspends>:void=
    loop:
        Payload := Bus.LevelUp.Await()
        # Notar: Payload.Player es player (no int) — usable directamente como key de weak_map.
        Logger.LogInfo("AchievementEngine", "Player reached lvl {Payload.NewLevel}")
        CheckLevelMilestones(Payload.Player, Payload.NewLevel)
```

**Consumer — esperar UN solo evento (sin loop)**:

```verse
# Caso de uso minoritario: bloquear hasta primera ocurrencia, luego salir.
# La corutina termina tras el Await; no hay loop.
WaitFirstLevelUp()<suspends>:void=
    Payload := Bus.LevelUp.Await()
    # Verse garantiza compile-time que Payload es level_up_payload
    Logger.LogInfo("X", "First level up: {Payload.NewLevel}")
```

### 11.8 Ventajas vs el plan original

| Aspecto | Plan original (`Subscribe(string, any)`) | Plan final (`event(t)` nativo) |
|---|---|---|
| Type-safety | ❌ runtime, fallable | ✅ compile-time, garantizado |
| String-magic | ❌ "level_up" como string | ✅ `EventBus.LevelUp` con autocompletado |
| Rename de evento | ❌ rompe silenciosamente | ✅ compile error inmediato |
| Cambio de campo en payload | ❌ runtime crash | ✅ compile error en suscriptores |
| Soporte `await` | ❌ requiere implementación custom | ✅ nativo (`event(t)` es `awaitable` — primitivo único de subscripción en Verse v1) |
| Patrón consumer | ❌ `Subscribe(handler)` callback runtime | ✅ `spawn{}` + `Await()` loop (canónico Verse, validado SPR-009 F-C-3a) |
| Líneas de código del bus | ~200 líneas custom | ~9 líneas declarativas (resto generado) |
| Dependencia de string match | ❌ sí | ✅ no |

### 11.9 Cuándo añadir un evento nuevo al catálogo

Añadir entrada a `events_catalog.json` cuando se cumpla **al menos una**:

1. Múltiples Systems necesitan reaccionar al mismo cambio (≥2 subscribers).
2. El emisor y los subscribers están en capas distintas y un import compile-time crearía acoplamiento no deseado.
3. El evento es una primitiva del dominio del juego que probablemente tenga más consumidores en el futuro.

**No añadir** si:
- Hay un único consumidor → llamada directa, no event.
- Es comunicación local dentro de un mismo Systems → método interno, no event.
- Es comunicación de UI → `creative_device.SomeEvent` propio del device, no event cross-system.

### 11.10 Validación y CI

`scripts/build/01_validate_jsons.py` debe verificar (ver `JSON_SCHEMAS.md` §42.3):

- Schema correcto de `events_catalog.json`.
- `id`, `verse_struct_name`, `verse_event_name` únicos en el catálogo.
- Cada `emitters[i]` existe en `modules_manifest.json` o es Core conocido.
- `payload_fields[i].type` está en lista permitida.
- Sin duplicados de `name` dentro del mismo `payload_fields`.

Drift entre catálogo y código → exit 1 → no merge.

---

## 📌 Resumen ejecutivo

```
🎯 LA REGLA: DeepSeek NUNCA escribe datos hardcoded en Verse.
              DeepSeek escribe el SCRIPT que GENERA esos datos.

🔄 EL FLUJO:
   1. Editor edita JSON (humano o IA)
   2. Python valida + transforma
   3. Verse Generated se regenera
   4. Verse manual usa el Generated
   5. Build + Push + Test

🚫 NUNCA:
   - Editar archivos en Generated/ a mano
   - Hardcodear datos en Verse manual
   - Lógica de gameplay en Python
   - Leer JSON en runtime Verse

✅ SIEMPRE:
   - JSON = source of truth
   - Python = transformer idempotente
   - Verse Generated = inmutable, regenerado
   - Verse manual = importa Generated y usa
```

---

**Fin del documento.**
