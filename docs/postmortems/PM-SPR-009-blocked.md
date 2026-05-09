# POSTMORTEM — 2026-05-09 — SPR-009 EventBus blocked (patrón canónico inviable en Verse moderno)

> **Status: 🟢 Resolved** — fase 1 (incidente) + fase 2 (resolución) ambas cerradas. Cierre F-C-5 = 2026-05-09 noche. Patrón canónico vigente: H4 (`event_bus_device := class<concrete>(creative_device)` + `@editable Bus:event_bus_device`). Decisión D-A11 (excepción a D-A7).
>
> **Postmortem en 2 fases.** **Fase 1** (hallazgo, causa raíz, bloqueo registrado, hipótesis fallidas, resolución temporal): redactada 2026-05-09 mañana. **Fase 2** (patrón final H4 + 8 commits refactor docs F-C-4 + lecciones de proceso): redactada 2026-05-09 noche tras F-B-investigación + F-C-2 implementación + F-C-3 tests + F-C-4 refactor 12 docs autoritativos.

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
- [x] Marcar BOOTSTRAP_PIPELINE.md §11.5 con banner ⚠️ "OBSOLETA post-SPR-009-blocked, ver patrón nuevo TBD post-F-B" — **resuelto F-C-4-L1a**: §11.5-§11.8 reescrito al patrón H4 (`event_bus_device := class<concrete>(creative_device)`) + warning ⚠️ explicativo en §11.5 cabecera. Banner obsolescencia innecesario tras refactor.
- [x] Marcar API_REFERENCE_GENERATED.md §3.5 con warning sobre patrón inviable — **resuelto F-C-4-L1b**: §3.5 reescrito completo con patrón device + sección "Funciones que NO existen" expandida (`.Subscribe`/`.Unsubscribe` documentados como inexistentes).
- [x] Marcar MODULES_DEPENDENCY_GRAPH.md §4.2 + §11.2 con warning idem — **resuelto F-C-4-L3 + L3-bonus**: §4.2 arquitectura device + §11.2 tabla `Bus.<Evento>` + §2.1 nota concrete excluyendo EventBus + cabecera doc actualizada.
- [x] CHANGELOG.md D-A8 entry "parcialmente revisada" — **resuelto F-C-4-L2**: nota retroactiva D-A8 añadida + nueva sección "Auditoría regresión bloque 5 — H4" + decisión D-A11 (excepción D-A7).
- [x] VERSE_SYNTAX_GUIDE.md §1 lección 11 ampliada (caso explícito event(t){} top-level propaga transacts) o lección 16 nueva — **resuelto F-C-4-L1b**: lección 16 nueva (`event(t){}` top-level falla 3512) + 4 sub-corolarios A-D (`event(t)` no subscribable / spawn+Await loop / Sleep(0.0) race fix / Signal síncrono) + 2 filas tabla anti-patrones §3 + contador 13→16.

### Acciones sistémicas (a aplicar tras F-B fase 2)

- [ ] **Validar plantillas Verse en BOOTSTRAP contra build UEFN real ANTES de cerrar decisión cerrada**. El patrón actual ("documentar y luego implementar 2 sprints después") dejó pasar este bug ~2 meses entre cierre D-A8 y validación real.
- [ ] **Test devices mínimos por patrón Verse arquitectónico nuevo** (~30 LOC) que validen sintaxis antes de transcribir a docs.
- [ ] **Proceso para "info de fuentes externas relevantes"** (foros Epic, tutoriales oficiales, ejemplos comunidad) que NO está en VERSE_SYNTAX_GUIDE — falta canal sistemático para incorporarla.

## ✅ Resolución final (2026-05-09 tarde-noche)

### Cronología completa

| Fase | Fecha | Acción | Resultado |
|---|---|---|---|
| **F-A** | 2026-05-09 mañana | Iteración fix1+fix2 sobre patrón canónico v0 (BOOTSTRAP §11.5 v0 + API §3.5 v0) | Bloqueado — err 3512 al instanciar `event(t){}` top-level. ~2.5h perdidas. PM fase 1 escrito. |
| **F-A-rollback** | 2026-05-09 tarde | Rollback a HEAD pre-SPR-009 + crear `Tests/test_event_bus_smoke.verse` placeholder | Repo limpio. |
| **F-B** | 2026-05-09 tarde | Investigación 5 hipótesis H1-H5 contra Verse moderno + `Verse.digest` + experimentos UEFN aislados | H1-H3 fail (descartadas). H5 viable solo con device parent → cristaliza H4. |
| **F-B-conclusión** | 2026-05-09 tarde | H4 = `event_bus_device := class<concrete>(creative_device):` instanciado en Main.umap, accedido vía `@editable Bus:event_bus_device` | Patrón canónico vigente. |
| **F-C-1** | 2026-05-09 tarde | Diseño post-H4 + decisión D-A11 (excepción a D-A7 — solo EventBus es device) | D-A11 documentada CHANGELOG. |
| **F-C-2** | 2026-05-09 tarde | Implementación `Generated/EventBusDevice.verse` + Main.umap actor + smoke runtime | Smoke test PASS in-session UEFN. Hash idempotencia EventBusDevice.verse: `A744E97185F1E913B0CFB33BA93CF181D236B793919C261E7DD0B56711B664A6`. |
| **F-C-3a** | 2026-05-09 tarde | Smoke runtime UEFN — `Tests/test_event_bus_smoke.verse` PASS con patrón `spawn{} + Sleep(0.0) + loop{Await()}` | Hash test_event_bus_smoke.verse: `61A441F77FEEE8C5C9649B572D9690B2070C2CCD028D398DBB1150D1E39B8224`. Lección 16 (`event(t)` no subscribable) emergió aquí. |
| **F-C-3b** | 2026-05-09 tarde | Golden contract Python — `scripts/build/tests/test_exporter_event_bus.py` (5 tests + fixture `event_bus_expected_contract.json` + idempotencia) | 5/5 PASS. Runtime ~0.13s. Sin deps externas. Patrón canónico TESTING_PROTOCOL §10 introducido. |
| **F-C-3c** | 2026-05-09 tarde | Anomalías capturadas: lista 6 Cores con excepción EventBus, plantilla Integration test obsoleta, gap §10 Python tests en plantilla "Crear test_device" | Capturado en handoff F-C-4. |
| **F-C-4** | 2026-05-09 tarde-noche | Refactor docs masivo — 7 sub-lotes (L1a + L1b + L1c + L2 + L3 + L4 + L5 + L3-bonus), 8 commits, 12 docs autoritativos modificados | Todo PASS, todo pusheado. HEAD master post-F-C-4. |
| **F-C-5** | 2026-05-09 noche | Postmortem fase 2 (este patch) | Pendiente cierre. |
| **F-C-6** | 2026-05-09 noche | Daily Log + commit cierre + tag `SPR-009-resolved` | Pendiente. |

### Patrón canónico vigente (post-H4)

```verse
# Content/Verse/Generated/EventBusDevice.verse (generado por SPR-004 ext)

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

event_bus_device<public> := class<concrete>(creative_device):

    LevelUp<public>:event(level_up_payload) = event(level_up_payload){}
    PlayerStatsChanged<public>:event(player_stats_changed_payload) = event(player_stats_changed_payload){}
    # ... una propiedad event(t) por evento del catálogo ...

    OnBegin<override>()<suspends>:void=
        # Device alive cuando UEFN instancia el actor del nivel.
        # Sin lógica adicional aquí — solo expone los event(t) builtin.
        Print("[EventBusDevice] Online")
```

### Patrón emisor canónico

```verse
# Cualquier device emisor (e.g., PlayerProgression dentro de un creative_device wrapper)

@editable Bus:event_bus_device = event_bus_device{}

OnLevelUpDetected(Player:player, Old:int, New:int):void=
    Payload := level_up_payload{ Player := Player, OldLevel := Old, NewLevel := New }
    Bus.LevelUp.Signal(Payload)  # Síncrono — handlers Await resumen aquí dentro
```

### Patrón consumer canónico

```verse
# Cualquier device consumer (e.g., HUDController dentro de creative_device wrapper)

@editable Bus:event_bus_device = event_bus_device{}

OnBegin<override>()<suspends>:void=
    spawn { ListenLevelUps() }
    Sleep(0.0)  # OBLIGATORIO — cede control al scheduler para que spawned task entre en Await
                # ANTES del primer Signal. Sin él: race silenciosa.

ListenLevelUps()<suspends>:void=
    loop:
        Payload := Bus.LevelUp.Await()
        Print("[HUD] Level up: {Payload.OldLevel} -> {Payload.NewLevel}")
```

### Decisión arquitectónica D-A11

**EventBus es excepción a D-A7**. Los 5 Cores restantes (Logger, TimeSync, PersistenceLayer, BigNumbers, AdminCommands) + ModuleRegistry siguen siendo singletons top-level. Solo EventBus migra a `creative_device` instanciado en Main.umap. Razón: `event(t){}` top-level falla con err 3512 (mismo patrón que lección 11 — structs literal top-level dentro de module). Detalle CHANGELOG sección "Auditoría regresión bloque 5".

### Refs commits

8 commits F-C-4 (todos en master, pusheados):

1. `acfecb0` — F-C-4-L1a BOOTSTRAP §11 post-H4
2. (SHA — humano busca) — F-C-4-L1b API_REFERENCE §3.5 + VERSE_SYNTAX_GUIDE lección 16
3. (SHA — humano busca) — F-C-4-L1c BOOTSTRAP cleanup residual
4. (SHA — humano busca) — F-C-4-L2 CHANGELOG D-A11 + GLOSSARY EventBus
5. (SHA — humano busca) — F-C-4-L3 SPRINTS_BACKLOG SPR-009 + CONCEPT done + MODULES §4.2/§2.1/§11.2
6. (SHA — humano busca) — F-C-4-L4 TESTING_PROTOCOL §2.1/§2.3 + PROMPT_TEMPLATES §12
7. (SHA — humano busca) — F-C-4-L5 FOLDER_STRUCTURE_TRUTH regex+naming + JSON_SCHEMAS §42
8. (SHA — humano busca) — F-C-4-L3-bonus drift residual MODULES (Bus.<Evento> + excepción D-A11 §2.1)

Para SHAs reales: `git log --oneline --grep="F-C-4"` post-cierre F-C-6.

## 📝 Cambios necesarios a docs

> Lista cerrada por F-C-4 (8 commits / 12 docs autoritativos). Todos los items marcados [x] tras refactor masivo.

- [x] `BOOTSTRAP_PIPELINE.md` §11.5 — patrón nuevo (H4 device) — **F-C-4-L1a**
- [x] `BOOTSTRAP_PIPELINE.md` §11.6 — transformer Python actualizado al patrón nuevo — **F-C-4-L1a**
- [x] `API_REFERENCE_GENERATED.md` §3.5 — actualizar firmas tras patrón nuevo — **F-C-4-L1b**
- [x] `MODULES_DEPENDENCY_GRAPH.md` §4.2 — actualizar arquitectura EventBus — **F-C-4-L3**
- [x] `MODULES_DEPENDENCY_GRAPH.md` §11.2 — actualizar lista de eventos según API nueva — **F-C-4-L3 + L3-bonus** (tabla columna `Bus.<Evento>` + convención + prosa cabecera)
- [x] `CHANGELOG.md` — entry D-A8 "parcialmente revisada" + entry patrón nuevo — **F-C-4-L2** (nota retroactiva D-A8 + sección "Auditoría regresión bloque 5" + D-A11)
- [x] `VERSE_SYNTAX_GUIDE.md` §1 — lección 16 nueva (`event(t){}` top-level) + 4 sub-corolarios — **F-C-4-L1b**
- [x] `SPRINTS_BACKLOG.md` — SPR-009 re-spec con patrón nuevo, deps recalibradas — **F-C-4-L3** (fila SPR-009 🟢 done + bullet Notas C1+C3 actualizado)
- [x] `CONCEPT.md` — SPR-009 done criteria reescrito — **F-C-4-L3** (bloque §13.3 reescrito con done [x])
- [x] `JSON_SCHEMAS.md` §42 — verificar si patrón nuevo cambia algo en el schema del catalog — **F-C-4-L5** (catalog inmutable; solo prosa cabecera + fila §42.2 `event_bus_device` actualizadas)
- [x] `GLOSSARY.md` — entradas EventBus + event(t) reescritas + nueva entrada "Await loop pattern" — **F-C-4-L2**
- [x] `TESTING_PROTOCOL.md` §2.1 (excepción D-A11) + §2.3 (plantilla Integration Await loop) — **F-C-4-L4**
- [x] `PROMPT_TEMPLATES.md` §12 (mención §10 Python tests + Done criteria adicional) — **F-C-4-L4**
- [x] `FOLDER_STRUCTURE_TRUTH.md` §1.1 tabla + nota + §4 árbol + §8.2 regex (`EventBusConstants` → `EventBusDevice`) — **F-C-4-L5**

## 🧠 Lecciones aprendidas

1. **Build real es la única fuente de verdad sintáctica**. PM-SPR-211 documentó esto hace 2 días. Patrón se repite — el postmortem PM-SPR-211 ya advertía "doc autoritativo puede tener drift". Aquí el drift fue arquitectónico, no superficial.
2. **`event(t){}` no inicializa top-level**. Lección probable nueva en VERSE_SYNTAX_GUIDE: archetype constructors de tipos nativos built-in propagan effects igual que archetype constructors custom.
3. **Decisiones arquitectónicas C-level (Auditoría 2 críticos) deben validarse contra build real ANTES de propagar a docs**, no después. Patrón actual: "doc primero, implementar luego" introduce ventana de drift de semanas-meses.
4. **Investigación previa Epic + foro confirmaba el problema** — pero esa info no estaba en VERSE_SYNTAX_GUIDE. Falta proceso para "info de fuentes externas relevantes que NO está en el guide" — tutoriales Epic, foros, ejemplos comunidad oficial.
5. **Tagear el estado bloqueado** (`SPR-009-blocked-2026-05-09`) + tag intermedio (`SPR-009-step3.5-fix1`) habilita rollback granular limpio. Política `tag pre-<SPR>` ya practicada da frutos cuando un sprint se bloquea a mitad.
6. **Trabajo bueno se preserva selectivamente**. Catalog JSON + validador + payloads son útiles bajo cualquier patrón final. Solo `export_event_bus()` y `EventBusConstants.verse` necesitan re-trabajo. Diferenciar "bloqueado" de "perdido" reduce coste de re-spec.

### Lecciones aprendidas — fase 2 (resolución)

#### Lecciones técnicas

| # | Lección | Documentada en |
|---|---|---|
| L1 | `event(t)` builtin Verse v1 = `class(signalable(t), awaitable(t))`. **NO implementa `subscribable`**. NO `.Subscribe()` ni `.Unsubscribe()`. | `VERSE_SYNTAX_GUIDE.md` §1 lección 16 sub-corolario A |
| L2 | `event(t){}` top-level dentro module/file scope falla con err 3512 (mismo patrón que lección 11 — structs literal top-level). | `VERSE_SYNTAX_GUIDE.md` §1 lección 16 |
| L3 | Patrón consumer canónico: `spawn { ListenerFn() } ; Sleep(0.0)` post-spawn + `ListenerFn()<suspends>:void= loop { Payload := Bus.<Evento>.Await() ; handler(Payload) }`. `Sleep(0.0)` post-spawn **obligatorio** (race fix Signal-antes-de-Await). | `VERSE_SYNTAX_GUIDE.md` §1 lección 16 sub-corolarios B + C |
| L4 | `Signal()` síncrono en Verse v1 — handlers Await resumen dentro de Signal antes de retornar al emisor. | `VERSE_SYNTAX_GUIDE.md` §1 lección 16 sub-corolario D |
| L5 | Tests Python complementan smoke devices Verse — golden contract para validadores/exporters/transformers en `scripts/build/`. Patrón canónico introducido SPR-009 F-C-3b: 5 tests cubriendo class declaration + count + contrato per-event + drift positivo + idempotencia. | `TESTING_PROTOCOL.md` §10 |
| L6 | Decisión arquitectónica D-A11: EventBus es excepción a D-A7. Solo EventBus migra a `creative_device` — los otros 5 Cores + Registry siguen siendo singletons top-level. | `CHANGELOG.md` sección "Auditoría regresión bloque 5" |

#### Lecciones de proceso

| # | Lección | Aplicación futura |
|---|---|---|
| P1 | Cuando un patrón canónico documentado falla en build real, **NO asumir que el patrón es correcto y el build erróneo** — investigar causa raíz contra `Verse.digest` + experimentos aislados. F-A perdió ~2.5h asumiendo el patrón v0 era válido. | Antes de iterar fix1+fix2 sobre un patrón canónico que falla, validar primero el patrón aislado en archivo throwaway. Si falla aislado, F-B (investigación) ANTES de F-A (intentar arreglar). |
| P2 | Refactor docs masivo (>10 docs) tras un cambio arquitectónico crítico → trocear en lotes pequeños (~250 líneas prompt CC, scope limitado por doc), **NO un solo prompt monolítico**. F-C-4 = 8 commits / 12 docs sin un solo error de localización. | Lotes ≤5 docs / lote. Cada lote con scope claro y validación PowerShell explícita. Lotes secuenciales (no paralelos) cuando hay cross-refs entre lotes. |
| P3 | Capturar drift residual durante ejecución de un lote (cuando CC reporta hallazgos fuera del scope original) — NO corregir en el momento, sino acumular para mini-lote bonus al final. F-C-4 capturó 2 drift en L3 → cerrados limpio en L3-bonus tras L5. | Procedimiento estándar: cada lote reporta "Drift residual capturado", se decide post-lote si va a mini-lote bonus o si el siguiente lote lo absorbe. |
| P4 | Hashes SHA-256 de archivos críticos (EventBusDevice.verse + test_event_bus_smoke.verse) registrados como anchors de idempotencia. Útil para verificar que regeneración futura del exporter produce bit-exact output. | Documentar hashes en cada cierre de SPR para artefactos generados críticos. |

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
