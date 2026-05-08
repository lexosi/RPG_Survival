# 📚 Survival Tycoon Modular Map — Índice de documentación

> **Orden de lectura recomendado para alguien que llega nuevo al proyecto.**

---

## 🎯 Lo primero que tienes que leer (orden)

1. **[CONCEPT.md](./CONCEPT.md)** — visión, sistemas, arquitectura, plan por fases, decisiones cerradas. **El doc maestro.**
2. **[SYSTEMS_INDEX.md](./SYSTEMS_INDEX.md)** — tabla autoritativa de los 72 sistemas. Resuelve dudas sobre `SYS-xxx`.
3. **[FOLDER_STRUCTURE_TRUTH.md](./FOLDER_STRUCTURE_TRUTH.md)** — árbol único de carpetas. Resuelve dudas sobre rutas. **Gana ante cualquier discrepancia.**
4. **[WORKFLOW.md](./WORKFLOW.md)** — cómo trabajamos cada día (Opus + Tú + DeepSeek).
5. **[PROMPT.md](./PROMPT.md)** — prompt agnóstico para cualquier modelo de IA.

---

## 🗂️ Docs autoritativos (single source of truth)

| Doc | Para qué | Gana ante conflicto |
|---|---|---|
| **[SYSTEMS_INDEX.md](./SYSTEMS_INDEX.md)** | Catálogo de los 72 `SYS-xxx` con JSON, Verse, sprint, persistencia | sí, sobre CONCEPT §8 y §10 |
| **[SPRINTS_BACKLOG.md](./SPRINTS_BACKLOG.md)** | 203 sprints `SPR-xxx` distribuidos por fase | sí, sobre CONCEPT §13 |
| **[FOLDER_STRUCTURE_TRUTH.md](./FOLDER_STRUCTURE_TRUTH.md)** | Árbol de `data/`, `Content/Verse/`, `scripts/`, `docs/` | sí, sobre CONCEPT §11 |
| **[MODULES_DEPENDENCY_GRAPH.md](./MODULES_DEPENDENCY_GRAPH.md)** | Quién depende de quién entre los 83 módulos Verse | sí, sobre imports en código |
| **[JSON_SCHEMAS.md](./JSON_SCHEMAS.md)** | Schemas formales de los JSONs | sí, sobre ejemplos en CONCEPT |
| **[BALANCE_FORMULAS.md](./BALANCE_FORMULAS.md)** | Curvas de XP, drop rates, rebirth, etc. | sí, sobre números en CONCEPT |
| **[PERSISTENCE_MAP.md](./PERSISTENCE_MAP.md)** | Diccionario de los 4 weak_maps. Bytes, schemas, migración | sí, sobre cualquier estructura inventada |

---

## 🔧 Docs operativos del día a día

| Doc | Para qué | Cuándo lo lees |
|---|---|---|
| **[PROMPT_TEMPLATES.md](./PROMPT_TEMPLATES.md)** | Plantillas listas para copiar | Cada vez que vas a pedir algo a Opus o DeepSeek |
| **[DEEPSEEK_CAPSULE.md](./DEEPSEEK_CAPSULE.md)** | Cápsula de 5 líneas | Al inicio de CADA chat con DeepSeek |
| **[API_REFERENCE_GENERATED.md](./API_REFERENCE_GENERATED.md)** | Funciones públicas del proyecto | Cualquier IA antes de llamar a una función |
| **[DAILY_LOG.md](./DAILY_LOG.md)** | Log diario de avance | Cada día al cerrar sesión |
| **[CHANGELOG.md](./CHANGELOG.md)** | Histórico de cambios entre versiones | Al cerrar fase o release |

---

## 🏗️ Docs de arquitectura

| Doc | Para qué |
|---|---|
| **[BOOTSTRAP_PIPELINE.md](./BOOTSTRAP_PIPELINE.md)** | JSON → Python → Verse Generated. Pipeline completo |
| **[PERSISTENCE_MAP.md](./PERSISTENCE_MAP.md)** | 4 weak_maps × 128 KB. Bytes, schemas, migración |
| **[MODULES_DEPENDENCY_GRAPH.md](./MODULES_DEPENDENCY_GRAPH.md)** | Capas + grafo de imports. Anti-rotura |

---

## 🎨 Docs de calidad

| Doc | Para qué |
|---|---|
| **[UI_UX_STYLE_GUIDE.md](./UI_UX_STYLE_GUIDE.md)** | Colores, fuentes, tamaños, mobile rules, Activity Log |
| **[TESTING_PROTOCOL.md](./TESTING_PROTOCOL.md)** | Test_devices temporales (lo más cerca de unit tests en Verse) |
| **[GLOSSARY.md](./GLOSSARY.md)** | Términos del proyecto (rebirth, alma, pity, etc.) |

---

## 🚨 Docs de emergencia

| Doc | Para qué |
|---|---|
| **[EMERGENCY_ROLLBACK.md](./EMERGENCY_ROLLBACK.md)** | Qué hacer cuando algo se rompe. **Léelo ANTES de necesitarlo.** |
| **[POSTMORTEMS_INDEX.md](./POSTMORTEMS_INDEX.md)** | Histórico de incidencias y lecciones |

---

## 📊 Mapa mental del proyecto

```
                    ┌────────────────────────────────────┐
                    │          CONCEPT.md                │
                    │  (qué hacemos, por qué, en orden)  │
                    └─────────────────┬──────────────────┘
                                      │
          ┌───────────────────────────┼─────────────────────────────┐
          │                           │                             │
          ▼                           ▼                             ▼
   ┌────────────────┐       ┌──────────────────┐         ┌──────────────────┐
   │ SYSTEMS_INDEX  │       │ SPRINTS_BACKLOG  │         │ FOLDER_STRUCTURE │
   │ 72 sistemas    │       │ 203 sprints      │         │ _TRUTH           │
   │ autoritativo   │       │ por fase         │         │ rutas únicas     │
   └────────┬───────┘       └────────┬─────────┘         └────────┬─────────┘
            │                        │                            │
            └────────────────────────┼────────────────────────────┘
                                     │
              ┌──────────────────────┼─────────────────────┐
              ▼                      ▼                     ▼
       ┌─────────────┐       ┌──────────────┐      ┌────────────────┐
       │  WORKFLOW   │       │   PROMPT     │      │ PROMPT         │
       │  cómo       │       │   instr.     │      │ TEMPLATES      │
       │  trabajo    │       │   IAs        │      │ ready-to-copy  │
       └─────────────┘       └──────────────┘      └────────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
┌──────────────┐            ┌─────────────────┐            ┌─────────────┐
│ PERSISTENCE  │            │ BOOTSTRAP       │            │ MODULES_DEP │
│ MAP          │            │ PIPELINE        │            │ _GRAPH      │
│ 4 weak_maps  │            │ JSON→Py→Verse   │            │ 83 módulos  │
└──────────────┘            └─────────────────┘            └─────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
┌──────────────┐            ┌──────────────────┐            ┌──────────────┐
│ JSON_SCHEMAS │            │ BALANCE_FORMULAS │            │ API_REFERENCE│
│ formato      │            │ curvas, drops    │            │ _GENERATED   │
│ data         │            │ rebirth          │            │ funciones    │
└──────────────┘            └──────────────────┘            └──────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
┌──────────────┐            ┌──────────────────┐            ┌──────────────┐
│ UI_UX_STYLE  │            │ TESTING_PROTOCOL │            │ EMERGENCY    │
│ _GUIDE       │            │ test_devices     │            │ ROLLBACK     │
│ visual       │            │                  │            │ + POSTMORTEM │
└──────────────┘            └──────────────────┘            └──────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
┌──────────────┐            ┌──────────────────┐            ┌──────────────┐
│ DAILY_LOG    │            │ CHANGELOG        │            │ GLOSSARY     │
│ log diario   │            │ versiones        │            │ términos     │
└──────────────┘            └──────────────────┘            └──────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │ DEEPSEEK_CAPSULE │
                            │ 5 líneas pegar   │
                            │ siempre          │
                            └──────────────────┘
```

---

## 🚀 Quick start: tu primer día con este sistema

### 1. Setup inicial (una vez, ~30 min)

1. Crear proyecto en claude.ai con `PROMPT.md` como instructions.
2. Subir TODOS los docs como knowledge files (22 archivos `.md`).
3. Configurar acceso a DeepSeek V4-Pro (ver `WORKFLOW.md` §2.1).
4. Git init en el proyecto UEFN, branch por fase.
5. Probar que DeepSeek responde con cápsula.

### 2. Tu primer briefing matinal con Opus

- Usa plantilla `PROMPT_TEMPLATES.md` §1.
- Pega `CONCEPT.md` + `SYSTEMS_INDEX.md` + `SPRINTS_BACKLOG.md` y di "primer día".
- Opus te dará el plan con SPR-001 a SPR-010 (Fase 0).

### 3. Tu primer sprint con DeepSeek

- Usa plantilla `PROMPT_TEMPLATES.md` §8.
- Empieza por **SPR-001** (Setup repo + carpetas según `FOLDER_STRUCTURE_TRUTH.md`).
- Cuando termine, copia archivos a UEFN, Build Verse Code, Push Changes.

### 4. Test

- Crea `test_device_SPR001.verse` siguiendo `TESTING_PROTOCOL.md`.
- Instancia en level, ejecuta, verifica HUD muestra ✅.
- **Si SPR-001 incluye crear `scripts/tools/folder_structure_validator.py`** (recomendado): copia el código de referencia de `FOLDER_STRUCTURE_TRUTH.md` §8.2 al disco, ejecútalo → debe dar exit 0. **Si aún no lo has creado, sáltate este paso** — el código existe solo como spec en el doc, no como archivo en `scripts/tools/` hasta que un sprint lo materialice.

### 5. Cierra el día

- Daily log según `PROMPT_TEMPLATES.md` §18.
- Git commit + tag `SPR-001`.
- Mañana repites el ciclo.

---

## 📊 Métricas del sistema de docs

- **22 documentos**
- **~9.500 líneas totales**
- **~440 KB de documentación**
- **Cobertura**: arquitectura, workflow, persistencia, UI, testing, emergencias, plantillas, APIs, sistemas, sprints, estructura, dependencias

---

## 🔄 Mantenimiento de los docs

| Doc | Quién lo actualiza | Frecuencia |
|---|---|---|
| **CONCEPT.md** | Opus (cuando hay decisión nueva) | cada cierre de fase mínimo |
| **SYSTEMS_INDEX.md** | Opus (cuando se cierra un sprint que toca un SYS) | cada sprint relevante |
| **SPRINTS_BACKLOG.md** | Tú (al cerrar sprint actualizas Estado) + Opus (al añadir nuevos) | continuo |
| **FOLDER_STRUCTURE_TRUTH.md** | Opus (cuando se crea carpeta/archivo nuevo) | cada vez que crece la estructura |
| **MODULES_DEPENDENCY_GRAPH.md** | Opus (cuando se añade módulo Verse o cambia firma) | cada sprint Verse |
| **PROMPT.md** | Opus | solo si cambia el modelo o reglas globales |
| **WORKFLOW.md** | Opus | solo si cambia el workflow base |
| **PROMPT_TEMPLATES.md** | Tú + Opus | cuando una plantilla se usa 3+ veces |
| **API_REFERENCE_GENERATED.md** | DeepSeek reporta + Tú actualizas (o `generate_api_reference.py`) | cada SPR que añade API pública |
| **PERSISTENCE_MAP.md** | Opus (review obligatorio) | cada vez que cambia un schema |
| **JSON_SCHEMAS.md** | Opus | cada vez que se añade un schema |
| **BALANCE_FORMULAS.md** | Opus + Tú | cada cierre de fase + tras hipótesis validadas |
| **BOOTSTRAP_PIPELINE.md** | Opus | si cambia el pipeline build |
| **UI_UX_STYLE_GUIDE.md** | Opus | si decisión visual nueva |
| **TESTING_PROTOCOL.md** | Opus | si patrón de testing cambia |
| **EMERGENCY_ROLLBACK.md** | Tú (al hacer postmortem) | tras cada crisis significativa |
| **POSTMORTEMS_INDEX.md** | Tú | tras cada postmortem |
| **DEEPSEEK_CAPSULE.md** | Opus | solo si DeepSeek cambia comportamiento |
| **GLOSSARY.md** | Opus | cuando se introduce término nuevo |
| **DAILY_LOG.md** | Tú | cada día |
| **CHANGELOG.md** | Tú | cada release/cierre de fase |

---

## 📋 Lista completa de docs (alfabética)

1. `API_REFERENCE_GENERATED.md`
2. `BALANCE_FORMULAS.md`
3. `BOOTSTRAP_PIPELINE.md`
4. `CHANGELOG.md`
5. `CONCEPT.md`
6. `DAILY_LOG.md`
7. `DEEPSEEK_CAPSULE.md`
8. `EMERGENCY_ROLLBACK.md`
9. `FOLDER_STRUCTURE_TRUTH.md` ⭐ nuevo
10. `GLOSSARY.md`
11. `JSON_SCHEMAS.md`
12. `MODULES_DEPENDENCY_GRAPH.md` ⭐ nuevo
13. `PERSISTENCE_MAP.md`
14. `POSTMORTEMS_INDEX.md`
15. `PROMPT.md`
16. `PROMPT_TEMPLATES.md`
17. `README.md` (este archivo)
18. `SPRINTS_BACKLOG.md` ⭐ nuevo
19. `SYSTEMS_INDEX.md` ⭐ nuevo
20. `TESTING_PROTOCOL.md`
21. `UI_UX_STYLE_GUIDE.md`
22. `WORKFLOW.md`

---

**¿Algo que falta? Reporta para añadirlo al sistema de docs.**
