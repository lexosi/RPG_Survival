# POSTMORTEM — 2026-05-09 — SPR-009 EventBus blocked (patrón canónico inviable en Verse moderno)

> ⚠️ **Postmortem en 2 fases.** Esta es **fase 1**: hallazgo, causa raíz, bloqueo registrado, hipótesis fallidas y resolución temporal. La **fase 2** (patrón final + edición de docs autoritativos) se redacta tras `F-B-investigación` cuando se decida el patrón sustituto. Las secciones "Cambios necesarios a docs" y partes de "Cómo prevenirlo" quedan como pendientes [ ] hasta entonces.

## 📋 Resumen ejecutivo (TL;DR)

Sprint SPR-009 (EventBus tipado generado, cierre Auditoría 2 — C3) bloqueado al intentar build UEFN del archivo `Generated/EventBusConstants.verse`. Dos patrones probados (canónico BOOTSTRAP §11.5 con `class<concrete>` + refactor a `module:` namespace) fallan con err 3512 (transacts effect). Causa raíz: `event(t){}` archetype empty constructor propaga `<transacts>` independientemente del wrapper. Patrón canónico documentado en BOOTSTRAP §11.5 + decisión cerrada D-A8 son **inviables en Verse moderno**. Resolución temporal: `export_event_bus()` revertido a stub `SPR-009-BLOCKED`, trabajo bueno preservado (catalog JSON + validador §42.3 + payloads reales generados). Commit `e5e499f` + tag `SPR-009-blocked-2026-05-09`. Resolución final pendiente F-B-investigación.

## 🔥 Síntoma

### Intento 1 — patrón canónico BOOTSTRAP §11.5 (`class<concrete>` + singleton top-level)

Build UEFN sobre `Content/Verse/Generated/EventBusConstants.verse` (regenerado por `02_export_constants_to_verse.py` paso 3.5) emitió 2 errores en `EventBus<public> : event_bus_module = event_bus_module{}`:

```
Line 21, col 1-57: Script error 3593:
  Definition EventBus is accessible from subpaths of /lexosi@fortnite.com/RPG_Survival/Verse,
  but depends on event_bus_module, which is only accessible from subpaths of /Verse/Generated.
  The definition should be no more accessible than its dependencies.

Line 21, col 39-57: Script error 3512:
  This archetype instantiation constructs a class that has the 'transacts' effect,
  which is not allowed by its context.
```

### Intento 2 — refactor `module:` namespace (fix2)

Tras decisión humana de eliminar `event_bus_module := class<concrete>:` y emitir `EventBus<public> := module:` con propiedades event(t) directamente dentro del module: build UEFN reportó **9× err 3512**, uno por cada propiedad `<EventName><public>:event(payload_t) = event(payload_t){}` dentro del module.

## 🔍 Causa raíz

`event(t){}` archetype empty constructor **siempre propaga `<transacts>`** independientemente del wrapper que lo contenga (`class<concrete>:`, `module:`, struct literal). Esto invalida la inicialización top-level de instancias `event(t)` en cualquier patrón estático.

VERSE_SYNTAX_GUIDE §1 lección 11 documenta que `NAME<public>:type = type{...}` top-level dentro de un module **falla con err 3512 igual que classes** y **cambiar visibility NO resuelve** (validado). El caso `event(t)` es coherente con esa lección — el archetype constructor de un tipo nativo built-in propaga effects igual que un struct/class custom.

Confirmación cruzada con docs Epic externos (consultados en F-B preliminar):
- Foro Epic — *Multicast Delegate Equivalent in UEFN Verse?*: comunidad confirma `event(t)` no se inicializa top-level fuera de `class(creative_device)` instanciado en runtime.
- Tutorial Epic *countdown_timer* + ejemplo *game_manager* (verse_inf comunidad): patrón canónico es `RoundEndEvent: event() = event(){}` **dentro de** `class(creative_device)`, NO top-level.

El patrón canónico documentado en proyecto (BOOTSTRAP_PIPELINE.md §11.5: `event_bus_module := class<concrete>:` + propiedades `event(t){}` + singleton `EventBus : event_bus_module = event_bus_module{}`) **es inviable en Verse moderno**. La decisión cerrada D-A8 (Auditoría 2 — C3 EventBus tipado) queda **parcialmente invalidada**: la idea conceptual (catálogo JSON declarativo + payloads tipados generados + API tipada) sigue válida, pero el patrón Verse propuesto NO compila.

## ⏱️ Timeline

- **2026-05-08 — paso 1 SPR-009**: catálogo `data/architecture/events_catalog.json` creado y validado (9 eventos, JSON OK).
- **2026-05-08 — paso 3 SPR-009**: validador `01_validate_jsons.py` extendido con 8 reglas §42.3. Tests V1-V4 OK.
- **2026-05-09 — paso 3.5 SPR-009 (intento 1)**: `export_event_bus()` implementado real siguiendo BOOTSTRAP §11.5. EventBus 1286 bytes, 9 events, idempotente. Commit + tag intermedio `SPR-009-step3.5-fix1`.
- **2026-05-09 — paso 7 SPR-009 build UEFN (intento 1)**: humano corre Build Verse Code → err 3593 + err 3512 en línea 21 (`EventBus<public> : event_bus_module = event_bus_module{}`).
- **2026-05-09 — diagnóstico humano**: identificada lección 7 (visibility) + lección 11 (transacts top-level). Decisión: refactor a `module:` namespace.
- **2026-05-09 — paso 3.5-fix2**: `export_event_bus()` refactoreado. Eliminado `event_bus_module := class<concrete>:` + singleton bottom. Sustituido por `EventBus<public> := module:` con propiedades event(t) directas. EventBus 1318 bytes. py_compile + idempotencia OK.
- **2026-05-09 — build UEFN (intento 2)**: 9× err 3512 (uno por propiedad event(t){} dentro del module).
- **2026-05-09 — bloqueo registrado**: `export_event_bus()` revertido a stub `SPR-009-BLOCKED`, archivo regenerado a placeholder coherente. Commit `e5e499f` + tag `SPR-009-blocked-2026-05-09`. Trabajo bueno preservado (catalog + validador + EventPayloads_Generated.verse real).
- **Tiempo total iteración fix1+fix2 hasta bloqueo**: ~2.5h.
- **F-B-investigación**: pendiente. Postmortem fase 2 se redacta tras decidir patrón final.

## 🛠️ Resolución (fase 1 — temporal, no resuelve)

### Hipótesis probadas

| # | Patrón | Resultado | Errores |
|---|---|---|---|
| H1 | Canónico BOOTSTRAP §11.5: `event_bus_module := class<concrete>:` + propiedades event(t) + singleton top-level `EventBus<public> : event_bus_module = event_bus_module{}` | ❌ Falla | err 3593 (visibility) + err 3512 (transacts) en línea singleton |
| H2 | Refactor `module:`: `EventBus<public> := module:` con propiedades event(t) directas dentro | ❌ Falla | 9× err 3512, uno por propiedad event(t){} |
| H3 | Funciones getter `Get<X>():event(t) = event(t){}` | ❌ Descartado antes de probar | Semánticamente inviable: cada call retorna instancia nueva, suscriptores no persisten entre calls |

### Acciones aplicadas (fase 1)

- `02_export_constants_to_verse.py` `export_event_bus()` revertido a stub `SPR-009-BLOCKED` (placeholder con header AUTO-GENERATED + comentario explicando bloqueo).
- `Content/Verse/Generated/EventBusConstants.verse` regenerado a placeholder coherente.
- **Trabajo bueno preservado** (NO revertido):
  - `data/architecture/events_catalog.json` (9 eventos, validado §42.3).
  - `scripts/build/01_validate_jsons.py` extensión §42.3 (8 reglas, regla 8 BLOCKING B1.2).
  - `scripts/build/02_export_constants_to_verse.py` `export_event_payloads()` real.
  - `Content/Verse/Generated/EventPayloads_Generated.verse` real (9 structs, sintaxis válida — los payloads son `struct:`, no propagan transacts top-level).
- Commit `e5e499f` con tag `SPR-009-blocked-2026-05-09`.
- Tag intermedio `SPR-009-step3.5-fix1` (último estado con patrón class<concrete>) preservado para rollback granular.
- Tag inicio `pre-SPR-009` preservado.

### Hipótesis pendientes F-B-investigación

| # | Hipótesis | Riesgo |
|---|---|---|
| H4 | EventBus dentro de `class(creative_device)` instanciable en mapa (patrón Epic oficial documentado en countdown_timer tutorial) | Garantizado funciona, pero rompe modelo singleton "import desde cualquier sitio" — requiere referenciar el device desde cada Systems |
| H5 | Custom `multicast(t)` class top-level con `var Handlers:[]handler = array{}` (patrón comunidad foro Epic) | Mantiene API singleton. Riesgo: si construcción `multicast(t){}` también propaga transacts → falla idéntica |
| H6 | Investigación adicional de variantes raras (specifiers exóticos, `external{}` en `.digest`, otros wrappers) | Bajo retorno esperado — `external{}` ya documentado lección 8 como inválido fuera de `.digest` (err 3558) |

## ⏳ Tiempo perdido

~2.5h iteración fix1 + fix2 + diagnóstico hasta bloqueo registrado (FASE 1).
FASE 2 (F-B-investigación + decisión patrón final + edición docs autoritativos): pendiente.

## 💔 Impacto

- **A jugadores**: ninguno (F0, sin publish).
- **A datos**: ninguno (no hay persistencia afectada).
- **A workflow**:
  - SPR-009 cerrado parcial. Decisión cerrada D-A8 marcada como "parcialmente revisada" (concepto válido, patrón Verse propuesto inviable).
  - Sprints downstream que dependían de EventBus runtime (cualquier sistema que iba a `Subscribe`/`Signal`) bloqueados hasta F-B fase 2.
  - Docs autoritativos potencialmente afectados: BOOTSTRAP_PIPELINE.md §11, API_REFERENCE_GENERATED.md §3.5, MODULES_DEPENDENCY_GRAPH.md §4.2/§11.2, CHANGELOG.md D-A8, VERSE_SYNTAX_GUIDE.md §1 lección 11. Todos pendientes edición tras F-B fase 2.

## ✅ Cómo prevenirlo (accionable)

### Acciones inmediatas (fase 1)

- [x] Commit del bloqueo + tag rollback granular (`SPR-009-blocked-2026-05-09`) — permite restaurar estado preciso si futuro replanteo necesita.
- [x] Stub `export_event_bus()` con etiqueta `SPR-009-BLOCKED` clara para que cualquier consumidor del exporter detecte el estado.
- [x] EventPayloads preservado (estructura de datos válida, reusable bajo cualquier patrón final).
- [ ] Marcar BOOTSTRAP_PIPELINE.md §11.5 con banner ⚠️ "OBSOLETA post-SPR-009-blocked, ver patrón nuevo TBD post-F-B" — **pendiente F-B fase 2**.
- [ ] Marcar API_REFERENCE_GENERATED.md §3.5 con warning sobre patrón inviable — **pendiente F-B fase 2**.
- [ ] Marcar MODULES_DEPENDENCY_GRAPH.md §4.2 + §11.2 con warning idem — **pendiente F-B fase 2**.
- [ ] CHANGELOG.md D-A8 entry "parcialmente revisada" — **pendiente F-B fase 2**.
- [ ] VERSE_SYNTAX_GUIDE.md §1 lección 11 ampliada (caso explícito event(t){} top-level propaga transacts) o lección 16 nueva — **pendiente F-B fase 2 con plantilla validada**.

### Acciones sistémicas (a aplicar tras F-B fase 2)

- [ ] **Validar plantillas Verse en BOOTSTRAP contra build UEFN real ANTES de cerrar decisión cerrada**. El patrón actual ("documentar y luego implementar 2 sprints después") dejó pasar este bug ~2 meses entre cierre D-A8 y validación real.
- [ ] **Test devices mínimos por patrón Verse arquitectónico nuevo** (~30 LOC) que validen sintaxis antes de transcribir a docs.
- [ ] **Proceso para "info de fuentes externas relevantes"** (foros Epic, tutoriales oficiales, ejemplos comunidad) que NO está en VERSE_SYNTAX_GUIDE — falta canal sistemático para incorporarla.

## 📝 Cambios necesarios a docs

> Lista pendiente — completar tras F-B fase 2 con docs concretos a editar y patrón final decidido.

- [ ] `BOOTSTRAP_PIPELINE.md` §11.5 — banner ⚠️ obsoleto + patrón nuevo (TBD)
- [ ] `BOOTSTRAP_PIPELINE.md` §11.6 — transformer Python actualizado al patrón nuevo
- [ ] `API_REFERENCE_GENERATED.md` §3.5 — actualizar firmas tras patrón nuevo
- [ ] `MODULES_DEPENDENCY_GRAPH.md` §4.2 — actualizar arquitectura EventBus
- [ ] `MODULES_DEPENDENCY_GRAPH.md` §11.2 — actualizar lista de eventos según API nueva
- [ ] `CHANGELOG.md` — entry D-A8 "parcialmente revisada" + entry SPR-009-blocked + entry patrón nuevo
- [ ] `VERSE_SYNTAX_GUIDE.md` §1 — lección 11 ampliada O lección 16 nueva (event(t){} top-level)
- [ ] `SPRINTS_BACKLOG.md` — SPR-009 re-spec con patrón nuevo, deps recalibradas
- [ ] `CONCEPT.md` — SPR-009 done criteria reescrito
- [ ] `JSON_SCHEMAS.md` §42 — verificar si patrón nuevo cambia algo en el schema del catalog

## 🧠 Lecciones aprendidas

1. **Build real es la única fuente de verdad sintáctica**. PM-SPR-211 documentó esto hace 2 días. Patrón se repite — el postmortem PM-SPR-211 ya advertía "doc autoritativo puede tener drift". Aquí el drift fue arquitectónico, no superficial.
2. **`event(t){}` no inicializa top-level**. Lección probable nueva en VERSE_SYNTAX_GUIDE: archetype constructors de tipos nativos built-in propagan effects igual que archetype constructors custom.
3. **Decisiones arquitectónicas C-level (Auditoría 2 críticos) deben validarse contra build real ANTES de propagar a docs**, no después. Patrón actual: "doc primero, implementar luego" introduce ventana de drift de semanas-meses.
4. **Investigación previa Epic + foro confirmaba el problema** — pero esa info no estaba en VERSE_SYNTAX_GUIDE. Falta proceso para "info de fuentes externas relevantes que NO está en el guide" — tutoriales Epic, foros, ejemplos comunidad oficial.
5. **Tagear el estado bloqueado** (`SPR-009-blocked-2026-05-09`) + tag intermedio (`SPR-009-step3.5-fix1`) habilita rollback granular limpio. Política `tag pre-<SPR>` ya practicada da frutos cuando un sprint se bloquea a mitad.
6. **Trabajo bueno se preserva selectivamente**. Catalog JSON + validador + payloads son útiles bajo cualquier patrón final. Solo `export_event_bus()` y `EventBusConstants.verse` necesitan re-trabajo. Diferenciar "bloqueado" de "perdido" reduce coste de re-spec.

## 🔗 Referencias

- **Sprint afectado**: SPR-009 (parcial — pasos 1, 3 OK; pasos 3.5, 6, 7, 8 bloqueados)
- **Commit del bloqueo**: `e5e499f`
- **Tag bloqueo**: `SPR-009-blocked-2026-05-09`
- **Tag rollback intermedio**: `SPR-009-step3.5-fix1` (último estado patrón `class<concrete>` antes de fix2)
- **Tag rollback inicio**: `pre-SPR-009`
- **Postmortems relacionados**:
  - [PM-SPR-211.md](PM-SPR-211.md) — drift sintáctico Verse moderno (causa similar: docs autoritativos con patrones obsoletos validados solo contra docs, no contra build real)
  - [PM-RECOVERY-2026-05-08.md](PM-RECOVERY-2026-05-08.md) — recovery git tras pérdida `.git` local (referencia operativa, no causal)
- **Decisiones cerradas afectadas**: D-A8 (Auditoría 2 — C3 EventBus tipado) — marcada parcialmente revisada
- **Docs autoritativos potencialmente afectados** (edición pendiente F-B fase 2):
  - `BOOTSTRAP_PIPELINE.md` §11.4-§11.6
  - `API_REFERENCE_GENERATED.md` §3.5
  - `MODULES_DEPENDENCY_GRAPH.md` §4.2 + §11.2
  - `CHANGELOG.md` D-A8 + entry SPR-009-blocked
  - `VERSE_SYNTAX_GUIDE.md` §1 lección 11+
  - `SPRINTS_BACKLOG.md` SPR-009
  - `CONCEPT.md` SPR-009 done criteria
- **Fuentes externas con confirmación independiente**:
  - Foro Epic — *Multicast Delegate Equivalent in UEFN Verse?*: https://forums.unrealengine.com/t/multicast-delegate-equivalent-in-uefn-verse/1232137
  - Tutorial Epic *countdown_timer* (patrón event(t) dentro de creative_device): https://dev.epicgames.com/documentation/en-us/fortnite/making-a-custom-countdown-timer-using-verse
