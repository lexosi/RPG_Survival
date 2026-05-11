# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Survival Tycoon Modular Map** — UEFN (Unreal Editor for Fortnite) engine. Reusable map factory: nuevos mapas se generan editando JSONs + assets, sin tocar Verse. Single-player up to 8, dual-currency (Gemas + V-Bucks), Verse path root `/lexosi@fortnite.com/RPG_Survival/Verse/...`.

## Documentación autoritativa (orden de prioridad)

`docs/` contiene 22 docs. Cuando dos discrepan, **gana el más específico**:

| Tema | Doc autoritativo |
|---|---|
| Visión, decisiones cerradas, fases | `docs/CONCEPT.md` |
| Catálogo 72 `SYS-xxx` | `docs/SYSTEMS_INDEX.md` |
| 203 sprints `SPR-xxx` | `docs/SPRINTS_BACKLOG.md` |
| Rutas, naming, estructura carpetas | `docs/FOLDER_STRUCTURE_TRUTH.md` |
| Deps entre módulos Verse, capas | `docs/MODULES_DEPENDENCY_GRAPH.md` |
| Sintaxis Verse moderna (21 lecciones) | `docs/VERSE_SYNTAX_GUIDE.md` |
| Schemas weak_maps, bytes, migración | `docs/PERSISTENCE_MAP.md` |
| Schemas JSON `data/` | `docs/JSON_SCHEMAS.md` |
| Pipeline JSON → Python → Verse | `docs/BOOTSTRAP_PIPELINE.md` |
| Test_devices Verse + pytest Python | `docs/TESTING_PROTOCOL.md` |
| Curvas, drops, caps numéricos | `docs/BALANCE_FORMULAS.md` |
| Funciones públicas Verse | `docs/API_REFERENCE_GENERATED.md` |

`docs/PROMPT.md` es el system-prompt agnóstico para cualquier IA del proyecto — léelo al iniciar.

## Arquitectura — 3 capas

```
data/*.json  ──►  scripts/build/*.py  ──►  Content/Verse/Generated/*.verse  ──►  runtime UEFN
   (edita humano)    (transformer)        (NUNCA editar a mano)               (lógica estática)
```

**Regla de oro**: nunca hardcodear data en Verse. DeepSeek/IA crea el script Python que genera el `.verse`, no el `.verse` directamente.

**Capas Verse** (acíclicas, `MODULES_DEPENDENCY_GRAPH.md`):

| # | Carpeta | Regla |
|---|---|---|
| 0 | `Content/Verse/Core/` | No importa nada. Logger, TimeSync, PersistenceLayer, BigNumbers, AdminCommands, ModuleRegistry. Singletons top-level (`Module<public> := module:`). |
| 1 | `Content/Verse/Generated/` | Solo importa Capa 0. AUTO-GENERATED — no editar. |
| 2 | `Content/Verse/Systems/{Base,Combat,Companions,Economy,Equipment,LiveOps,Player,Quests,Social,UI,World}/` | Importa 0–1. |
| 3 | (mismo) | Importa 0–2. |
| 4 | `Systems/UI`, `Systems/LiveOps`, `Systems/Social` | Importa 0–3. |
| 5 | `Content/Verse/Devices/` | Importa todo. Nadie lo importa. |

**Excepción D-A11**: `EventBus` es `creative_device` (no singleton top-level) — `event(t){}` top-level falla con `err 3512`. Se referencia vía `@editable Bus:event_bus_device`.

## Comandos comunes

**Shell**: PowerShell 5.1 exclusivo (no WSL, no bash, no cmd). Ver `docs/PROMPT.md` §6 para prohibidos (no `&&`, no `python -c`, no heredocs bash). Usa `;` o `if ($LASTEXITCODE -eq 0) { ... }`.

### Pipeline build (Python)

```powershell
python scripts/build/00_validate_structure.py              # filesystem vs FOLDER_STRUCTURE_TRUTH
python scripts/build/00_validate_structure.py --allow-missing  # tolera archivos declarados ausentes
python scripts/build/01_validate_jsons.py                  # schemas + reglas inquebrantables data/
python scripts/build/01_validate_jsons.py --strict         # warnings = error
python scripts/build/01_validate_jsons.py --file data/companions/companions_base.json  # único archivo
python scripts/build/02_export_constants_to_verse.py       # genera 12 .verse en Generated/
python scripts/build/02_export_constants_to_verse.py --only export_companions --dry-run
```

Exit codes documentados en docstring de cada script.

### Tests Python (scripts/build/tests/)

```powershell
python -m pytest scripts/build/tests/                                  # full
python -m pytest scripts/build/tests/test_close_sprint.py              # un archivo
python -m pytest scripts/build/tests/test_close_sprint.py::TestX::test_y  # un test
python -m unittest scripts.build.tests.test_exporter_event_bus         # tests con unittest
```

Fixtures en `scripts/build/tests/fixtures/` (json o md según input bajo test).

### Cierre de sprint

```powershell
python scripts/tools/close_sprint.py SPR-XXX           # genera/actualiza docs/dailylog/DL_*.md
python scripts/tools/close_sprint.py SPR-XXX-FIX-1     # variante FIX
python scripts/tools/close_sprint.py --reset-user      # repreguntar nick
```

Ejecuta 3 checks anti-drift (CHANGELOG / SPRINTS_BACKLOG / SYSTEMS_INDEX). Exit 4 = drift detectado. Ver `docs/CONCEPT.md` §5 TRUTH §5.

### Mantenimiento

```powershell
pwsh scripts/maintenance/check_orphan_files.ps1        # detecta archivos huérfanos
```

### UEFN (manual)

Build Verse Code + Push Changes solo desde el editor UEFN. No hay headless build CLI.

## Naming rules (enforced por `00_validate_structure.py`)

| Tipo | Regex |
|---|---|
| `data/**/*.json` | `^[a-z][a-z0-9_]*\.json$` |
| `Content/Verse/**/*.verse` (Core/Systems/Devices) | `^[A-Z][A-Za-z0-9]*\.verse$` |
| `Content/Verse/Generated/*.verse` | `^[A-Z][A-Za-z0-9]*_Generated\.verse$` o excepciones `ModuleRegistryConstants.verse`, `EventBusDevice.verse` |
| `Content/Verse/Tests/test_*.verse` | `^test_[A-Za-z0-9_]+\.verse$` |
| `Content/Verse/Tests/canary/throwaway_*.verse` | `^throwaway_[A-Za-z0-9_]+\.verse$` |
| `scripts/build/NN_*.py` | `^\d{2}_[a-z][a-z0-9_]*\.py$` (pipeline numerado) |
| `scripts/build/_*.py` | helpers sibling (no pipeline) |
| `scripts/build/tests/test_*.py` | pytest/unittest |
| `docs/*.md` | `SCREAMING_SNAKE.md` |
| `docs/dailylog/DL_*.md` | `^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$` |
| `docs/postmortems/PM-*.md` | `^PM-[A-Za-z0-9_-]+\.md$` |

`IGNORED_DIRS` durante scan: `__pycache__/`, cualquier raíz empezando con `_` (e.g. `_throwaway/`).

## Restricciones UEFN (inquebrantables)

- **4 weak_maps persistentes / isla, ≤128 KB c/u**. Backwards-compat OBLIGATORIA: solo añadir campos opcionales con defaults; NUNCA renombrar/eliminar.
- **No backup/rollback persistencia** — Epic gestiona versioning.
- **No cross-session async, no auction global, no DB compartida.**
- **Mobile-first**: texturas ≤512×512 potencia 2, LODs en todos los meshes, HISM para repetidos.
- **Códigos canjeables**: compilados en publish, no editables runtime → workaround pre-pool grande.

## Sintaxis Verse — gotchas críticos

Autoridad: `docs/VERSE_SYNTAX_GUIDE.md` (21 lecciones). Resumen mínimo:

- `using { Verse.Core.Logger }` (dotted relative) preferido — VS Code Quick Fix la ofrece.
- Path canónico incluye `Verse/`: `/lexosi@fortnite.com/RPG_Survival/Verse/Core/Logger`.
- `return` no existe — última expresión del bloque es retorno.
- `<decides>` cambia tipo a failable. `return`/`fail` con efectos `no_rollback` vs propagación: lecciones 18–20.
- `event(t){}` top-level falla `err 3512` → EventBus debe ser `creative_device`.
- Patrón generado canónico (post-SPR-211): `struct<public>` + `module<public>` + funciones `Get{Singular}{PascalCase}`. Patrón legacy `NAME := struct_def{...}` top-level rompe.

## Workflow de IA recomendado

Cuando se pide implementar `SPR-xxx`:

1. Lee el sprint en `SPRINTS_BACKLOG.md` (no en `CONCEPT.md`).
2. Identifica `SYS-xxx` afectados en `SYSTEMS_INDEX.md`.
3. Verifica rutas exactas en `FOLDER_STRUCTURE_TRUTH.md` **antes** de crear archivos.
4. Si toca Verse → consulta `MODULES_DEPENDENCY_GRAPH.md` (capas + imports).
5. Si toca persistencia → bucket correcto en `PERSISTENCE_MAP.md` §3–§6.
6. Implementa solo el sprint. **Atómicos.** No te excedas.
7. Al cerrar: `python scripts/tools/close_sprint.py SPR-XXX` (genera dailylog + valida drift).

Si el usuario prefija mensaje con `ooda` → estructura respuesta como OODA loop (Observe / Orient / Decide / Act).

## Decisiones cerradas relevantes (no re-debatir)

- **D-A7**: 5/6 Cores son singletons top-level estáticos (Logger, TimeSync, PersistenceLayer, BigNumbers, AdminCommands).
- **D-A10**: 2 excepciones de naming en `Generated/`: `ModuleRegistryConstants.verse`, `EventBusDevice.verse`.
- **D-A11**: EventBus es `creative_device`, no singleton.
- **D-A14**: `_throwaway/` = scratch ad-hoc local, gitignored (excepto `.gitkeep`).
- **JSON-first**: cualquier dato variable entre mapas vive en JSON, no Verse.
