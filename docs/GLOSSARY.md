# 📖 GLOSSARY — Glosario del proyecto

> **Definiciones canónicas de todos los términos del proyecto.**
>
> Pegar este archivo a IAs ejecutoras (DeepSeek) cuando no quieras pegar CONCEPT.md entero.
> **Los términos aquí son los oficiales. Si encuentras discrepancia con otro doc, este es la fuente de verdad de naming.**

---

## 🧭 Índice por categoría

- [A. Plataforma y tecnología](#a-plataforma-y-tecnología)
- [B. Arquitectura del proyecto](#b-arquitectura-del-proyecto)
- [C. Conceptos de juego](#c-conceptos-de-juego)
- [D. Sistemas (referencia rápida)](#d-sistemas-referencia-rápida)
- [E. Persistencia y datos](#e-persistencia-y-datos)
- [F. Workflow y proceso](#f-workflow-y-proceso)
- [G. Roles e identificadores](#g-roles-e-identificadores)
- [H. Acrónimos y abreviaturas](#h-acrónimos-y-abreviaturas)

---

## A. Plataforma y tecnología

### UEFN
**Unreal Editor for Fortnite.** Herramienta de Epic para crear islas (mapas) en Fortnite, basada en Unreal Engine 5.

### Verse
Lenguaje de scripting de UEFN. Es el **runtime del juego**: la lógica que ejecuta gameplay en tiempo real. Tipado estático, paradigma funcional con efectos. **Código estático del proyecto.**

### Python (en UEFN)
Disponible desde UEFN v40.00 en modo experimental. **Build-time only**, NO corre en runtime. Se usa para scripts del editor: validar JSONs, generar Verse, automatizar tareas repetitivas. Acceso al módulo `unreal` completo.

### Build Verse Code
Acción manual del editor (Ctrl+Shift+B) que compila el código Verse. Necesaria tras cualquier cambio en `.verse`.

### Push Changes
Acción del editor que sincroniza los cambios al servidor de Epic para que la sesión live los vea. Sin Push Changes, los cambios solo existen en el editor local.

### Mobile Preview
Modo de UEFN que simula el dispositivo móvil. **Test obligatorio** dado que ~60% de la audiencia Fortnite es móvil.

### Spatial Profiler
Herramienta de UEFN para detectar memory leaks y problemas de performance. Usar en cada testing pass.

### HISM
**Hierarchical Instanced Static Meshes.** Técnica de optimización para repetir meshes (decoración, droppers) sin coste por instancia.

### HLOD
**Hierarchical Level of Detail.** Sistema de UE para optimizar lejanía: meshes lejanos se simplifican automáticamente.

### LOD
**Level of Detail.** Versiones simplificadas de un mesh según distancia a la cámara. Obligatorio en todo mesh, especialmente companions instanciados masivamente.

### Creator Portal
Panel de Epic donde se publica el mapa, se gestionan entitlements V-Bucks, se ve analytics.

### In-Island Transactions
API de Epic (live desde 9 enero 2026) para vender items con V-Bucks dentro de islas. Devuelve "entitlements". **Refund window de 20 días** desde la compra: Epic puede iniciar refunds masivos sin revertir items entregados. **Revenue split 100% al creador hasta 31 enero 2027**, después 50%/50%. Ver `CONCEPT.md` §5.7.

### Entitlement
Item desbloqueado tras compra V-Bucks. Tu sistema lo detecta vía API y otorga el item correspondiente al jugador. Lleva flag obligatorio `consequential_to_gameplay` (true si da ventaja gameplay, false si solo cosmético). Antes de v39.10 se llamaba `product`.

### ConsequentialToGameplay
Flag obligatorio (regla Epic v39.00) en cada entitlement publicada. `true` para items que dan ventaja gameplay (companions premium, equipment, gems, BP). `false` solo para cosméticos puros. Etiquetar mal = oferta rechazada en publish. En el proyecto: campo `consequential_to_gameplay: bool` en `data/economy/vbucks_offers.json`.

---

## B. Arquitectura del proyecto

### Modular Map Machine
La filosofía central del proyecto: **una sola codebase Verse** que produce **múltiples mapas distintos** cambiando solo JSONs y assets. El segundo mapa cuesta ~10–20% del esfuerzo del primero.

### Theme pack
Conjunto de JSON + assets que tematizan un mapa entero: meshes, texturas, audio, paleta de colores. Cambiar theme pack = cambiar mapa.

### Data Layer
Capa 1 de la arquitectura. Todos los JSONs en `data/`. **Source of truth** del contenido.

### Build Layer
Capa 2 de la arquitectura. Scripts Python en `scripts/`. **Editor-time only**: validan, generan, exportan.

### Runtime Layer
Capa 3 de la arquitectura. Código Verse en `Content/Verse/`. **Lógica del juego**, código estático no debe tocarse entre mapas.

### Generated/
Carpeta `Content/Verse/Generated/`. **Output de scripts Python**. NUNCA editar manualmente. Se regenera al ejecutar pipeline.

### Pipeline (build pipeline)
Secuencia ordenada de scripts Python que validan JSONs → generan Verse → procesan assets. Se ejecuta tras editar cualquier JSON. Orquestador: `07_run_full_pipeline.py`.

### Source of Truth
El JSON. Si hay discrepancia entre JSON y código Verse generado, **el JSON gana** y se regenera el Verse.

### Idempotente
Propiedad de los scripts Python: ejecutar N veces da el mismo resultado. **Obligatorio** para todo transformer del pipeline.

### JSON-first
Regla de modularidad: si una decisión va a variar entre mapas, va en JSON, **nunca hardcoded en Verse**. Es el corolario directo de "Modular Map Machine".

### SYSTEMS_INDEX (doc autoritativo)
`SYSTEMS_INDEX.md`. **Catálogo único** de los 72 `SYS-xxx` con fase, JSON principal, Verse principal, sprint asignado, bucket de persistencia. **Gana sobre CONCEPT** en descripciones de catálogo.

### SPRINTS_BACKLOG (doc autoritativo)
`SPRINTS_BACKLOG.md`. **Backlog completo** `SPR-001` → `SPR-203` distribuido en F0–F5 con dependencias declaradas, archivos a tocar y tiempos. **Gana sobre CONCEPT §13** en detalle de sprints.

### FOLDER_STRUCTURE_TRUTH (doc autoritativo)
`FOLDER_STRUCTURE_TRUTH.md`. **Árbol único** de carpetas y archivos del proyecto. **Gana sobre CONCEPT §11** en rutas. Incluye spec del validador `scripts/build/00_validate_structure.py` (primer step del orquestador, ver BOOTSTRAP §7.2).

### MODULES_DEPENDENCY_GRAPH (doc autoritativo)
`MODULES_DEPENDENCY_GRAPH.md`. **Grafo de dependencias** entre los 83 módulos Verse organizado en capas (0→5). Lista deps `📤` y consumidores `📥` por módulo. Catálogo de eventos runtime. Valida ciclos.

### Capa (Layer)
Nivel arquitectónico de un módulo Verse según `MODULES_DEPENDENCY_GRAPH`. **0=Core**, **1=Generated**, **2=Systems base**, **3=Systems gameplay**, **4=UI/LiveOps/Social**, **5=Devices**. Regla: capa N solo importa de capas <N.

### EventBus
`creative_device` **generado** que expone instancias `event(payload_t)` nativas de Verse v1, una por cada evento del catálogo `data/architecture/events_catalog.json`. Archivo source manual: `Content/Verse/Core/EventBus.verse` (placeholder/legacy si se conserva). Archivo operativo: `Content/Verse/Generated/EventBusDevice.verse` (generado por Python). SYS-072. SPR-009. **Patrón H4 (post-F-C-2)**: `event_bus_device := class<concrete>(creative_device)`. NO singleton top-level — el patrón top-level falla con err 3512 (ver `VERSE_SYNTAX_GUIDE.md` §1 lección 16). Excepción a D-A7 documentada en D-A11. Acceso desde otros devices vía `@editable Bus:event_bus_device = event_bus_device{}` (drag&drop en UEFN). Producer: `Bus.<Evento>.Signal(payload)` (síncrono — handler resume dentro de Signal). Consumer: `spawn { loop { Payload := Bus.<Evento>.Await() ; ... } }` con `Sleep(0.0)` post-spawn (NO existe `.Subscribe()` en `event(t)` builtin Verse v1, solo `.Signal()` y `.Await()`). Type-safety compile-time vía structs payloads en `Generated/EventPayloads_Generated.verse`. Decisiones cerradas: D-A8 (Auditoría 2 — C3, type-safety) + D-A11 (Auditoría regresión bloque 5 — H4, device pattern). Detalle en `BOOTSTRAP_PIPELINE.md` §11 + `JSON_SCHEMAS.md` §42 + `MODULES_DEPENDENCY_GRAPH.md` §11.2 + `API_REFERENCE_GENERATED.md` §3.5 + `VERSE_SYNTAX_GUIDE.md` §1 lección 16.

### events_catalog.json
JSON catálogo declarativo en `data/architecture/events_catalog.json` que lista los eventos cross-system (id, verse_struct_name, verse_event_name, emitters, subscribers, payload_fields). Source of truth del EventBus tipado. Schema en `JSON_SCHEMAS.md` §42. Genera `EventPayloads_Generated.verse` (structs payloads) + `EventBusConstants.verse` (instancias `event(t)` en `event_bus_module`). Validado por `01_validate_jsons.py`. Drift entre catálogo y código → CI rechaza merge.

### event(t) — primitiva nativa Verse
Tipo parametric definido en `Verse.digest`: `event<native><public>(t:type)<computes> := class(signalable(t), awaitable(t))`. **NO implementa `subscribable`** en Verse v1 (validado runtime SPR-009 F-C-3a). Métodos disponibles sobre una instancia: `.Signal(payload)` (emitir, síncrono — handlers Await suspendidos resumen DENTRO de Signal antes de retornar) y `.Await()` (consumer, suspende corutina hasta próximo Signal). **NO existen `.Subscribe(handler)` ni `.Unsubscribe(handler)`** — son APIs imaginarias que no aparecen en builtin Verse v1. Patrón consumer canónico = `spawn{}` + `Await()` loop con `Sleep(0.0)` post-spawn (ver entrada `Await loop pattern` y `VERSE_SYNTAX_GUIDE.md` §1 lección 16 sub-corolarios A-D). Es el equivalente Verse de un multicast delegate de Unreal C++, pero con superficie API más limitada. Usado como bloque de construcción del EventBus tipado del proyecto (decisión D-A8 + D-A11). Fuente: [forums.unrealengine.com — Multicast Delegate Equivalent in UEFN Verse](https://forums.unrealengine.com/t/multicast-delegate-equivalent-in-uefn-verse/1232137).

### Await loop pattern
Patrón consumer canónico para escuchar eventos `event(t)` en Verse v1, dado que la primitiva builtin NO implementa `subscribable` (no existen `.Subscribe()` ni `.Unsubscribe()`). Estructura: `spawn { ListenerFn() }` + `Sleep(0.0)` post-spawn + `ListenerFn()<suspends>:void= loop { Payload := Bus.<Evento>.Await() ; <handler>(Payload) }`. El `spawn{}` encapsula la corutina, el `loop{}` mantiene el listener vivo, `Await()` suspende hasta el próximo `Signal()`. El `Sleep(0.0)` post-spawn es **obligatorio** — cede control al scheduler para que el spawned task entre en `Await` ANTES del primer Signal; sin él, race condition silenciosa (Signal antes de Await → evento perdido sin warning). `Signal()` es síncrono en Verse v1 (handler resume dentro de Signal antes de retornar). Para "desuscribir": salir del loop con `break` o terminar el `spawn` con condición de salida. Para escuchar UN solo evento (sin loop persistente): `Payload := Bus.<Evento>.Await()` directo en una corutina spawneada que termina tras el Await. Validado runtime SPR-009 F-C-3a. Detalle completo en `VERSE_SYNTAX_GUIDE.md` §1 lección 16 sub-corolarios B (loop pattern) + C (Sleep(0.0) race fix) + D (Signal síncrono). Plantilla canónica en `BOOTSTRAP_PIPELINE.md` §11.7.

### ModuleRegistry
Módulo Core que sirve de **lookup runtime para Systems gameplay** (Capa 2+). NO orquesta los Core (los Core son singletons top-level que Verse inicializa solos). Resuelve dependencias circulares de import compile-time entre Systems. Archivo: `Content/Verse/Core/ModuleRegistry.verse`. SYS-072. SPR-005. **Decisión cerrada (Auditoría 2 — C1)**: por limitación de Verse (no soporta reflexión runtime), expone **getters tipados estáticos** generados desde `data/architecture/modules_manifest.json` por Python. Detalle en `MODULES_DEPENDENCY_GRAPH.md` §4.7 + `BOOTSTRAP_PIPELINE.md` §10.

### Logger
Módulo Core de logging con niveles Debug/Info/Warn/Error. Archivo: `Content/Verse/Core/Logger.verse`. SYS-072. SPR-006. **Es dependencia de TODOS los demás módulos** (~83 consumidores). Cambiar firma rompe todo. **Arquitectura (post-SPR-211)**: `Logger<public> := module:` (namespace top-level, sin class, sin archetype), NO `creative_device`, NO se registra en ModuleRegistry. Acceso por `using { Verse.Core.Logger }`. Patrón legacy `Logger : logger_module = logger_module{}` falla con err 3512 — ver `VERSE_SYNTAX_GUIDE.md` §1 lección 8 + §2.1.

### TimeSync
Módulo Core de tiempo UTC server-side. Archivo: `Content/Verse/Core/TimeSync.verse`. SYS-068. SPR-007. Source of truth temporal vía `GetSimulationElapsedTime()`. Usado por shop rotation, daily login, hourly boss, BP, etc. **Arquitectura (post-SPR-211)**: `TimeSync<public> := module:` (namespace top-level). Funciones failable expuestas con `<decides>:int=` (GetUTCNow, GetSecondsUntilNextHour) o `<decides>:void=` con condiciones-statement (IsInWindow). Llamadas con `[]`: `TimeSync.GetUTCNow[]`. Ver `VERSE_SYNTAX_GUIDE.md` §2.2.

### BigNumbers
Wrapper Verse de librería de comunidad para aritmética grande (sextillones, notación científica). Archivo: `Content/Verse/Core/BigNumbers.verse`. SYS-067. Se usa cuando un valor puede exceder int64 (~9.2 quintillones). **Arquitectura (C1)**: módulo de funciones puras (sin estado, no requiere singleton). Acceso por `using { /<ProjectName>/Core/BigNumbers }`.

### PersistenceLayer
Módulo Core que gestiona los 4 weak_maps (load/save/validación defensiva). Archivo: `Content/Verse/Core/PersistenceLayer.verse`. SYS-069. SPR-008. **Dependencia de 24 módulos**. Cambiar schema = bump de Schema Version + entrada en CHANGELOG. **Arquitectura (C1)**: singleton top-level con `weak_map` declarados a nivel de módulo (requerido por Verse para persistencia).

### Module namespace pattern (post-SPR-211)
Patrón canónico vigente para Cores SIN state mutable (Logger, TimeSync, BigNumbers): `Module<public> := module:`. Es un **namespace de funciones**, no una class instanciada. No requiere archetype `{}`. Se declaran funciones top-level dentro del module y los consumidores acceden por `Module.Func(...)`. Ejemplo en `VERSE_SYNTAX_GUIDE.md` §2.1.

> **Reemplaza al patrón legacy** "Singleton top-level (Verse)" descrito previamente como `<x>_module := class<concrete>:` + `Singleton : x_module = x_module{}`. Ese patrón **falla con err 3512** en Verse moderno (UEFN ≥40.30): los métodos `<decides>` propagan `<transacts>` al class instance, y la construcción top-level es contexto `<computes>` puro. Validado durante SPR-007 build UEFN. Decisión Auditoría 3 — H3.1 (specifier `<concrete>`) queda **obsoleta** para Cores sin state. Caso "Core con state mutable" (PersistenceLayer SPR-008) queda TBD — ver `VERSE_SYNTAX_GUIDE.md` §2.4.

### Generated data getter pattern (post-SPR-211)
Patrón canónico vigente para archivos generados de constantes (Companions, Items, Quests, etc.): `struct<public>` top-level + module `<public>` + funciones getter `Get{Singular}{PascalCaseName}<public>():struct_t= struct_t{...}` + función agregadora `GetAll<Plural>():[]struct_t= array{ ... }`. Ejemplo en `VERSE_SYNTAX_GUIDE.md` §2.3. Reemplaza al patrón legacy `NAME := struct_def{...}` top-level que falla con err 3512 (lección 11+12). Aplica a los 3 archivos generados activos: `Companions_Generated.verse`, `Items_Generated.verse`, `Quests_Generated.verse`. Generador: `scripts/build/02_export_constants_to_verse.py`.

### Systems registrables
Subconjunto de Systems gameplay (Capa 2+) que se inscriben en `ModuleRegistry` para ser accesibles via lookup runtime. Solo se registran sistemas con estado runtime que múltiples consumidores comparten o cuya import compile-time crearía ciclo. Sistemas de funciones puras o consumo único NO se registran. Lista declarativa en `data/architecture/modules_manifest.json`. Genera el `Generated/ModuleRegistryConstants.verse` con un par `RegisterX/GetX` tipado por sistema. Detalle en `BOOTSTRAP_PIPELINE.md` §10.

### modules_manifest.json
JSON manifest declarativo en `data/architecture/modules_manifest.json` que lista los Systems registrables (id, module_name, verse_path, layer, phase). Source of truth del Registry. Schema en `BOOTSTRAP_PIPELINE.md` §10.3. Se valida con `01_validate_jsons.py`. Drift entre manifest y código real → CI rechaza merge.

---

## C. Conceptos de juego

### Survival Tycoon
Género del proyecto: fusión de Survival (recursos, construcción, exploración) + Tycoon (gestión, generadores, escalado idle) + Coleccionismo de ayudantes.

### Loop core
Ciclo principal de gameplay: **farmear recursos → mejorar base → reclutar ayudantes → subir nivel → derrotar bosses → desbloquear zonas → eventual rebirth**.

### Ayudante (Companion)
Criatura coleccionable que asiste al jugador. Genera recursos pasivamente, mejora stats, asignable a tareas. ~50+ tipos × variantes × rarezas = 300+ entradas.

### Rebirth
**Reset del progreso normal a cambio de meta-progresión permanente.** El jugador resetea XP, level, gold, pero gana bonuses permanentes. Primer rebirth en 20–30 min como onboarding del loop endgame.

### Rebirth count
Número de veces que el jugador ha hecho rebirth. **Nunca se resetea.** Acumula bonuses permanentes.

### Base Level
Eje de progresión **PERMANENTE** que NO se resetea con rebirth. Es el **gate maestro** del juego: zonas, quests, eventos requieren base level mínimo.

### Skill Points
Puntos que el jugador gana al subir nivel y distribuye en 5 ramas de skill trees. Se resetean con rebirth (excepto bonuses permanentes).

### Skill Trees (5 ramas)
Las 5 ramas son: **Combate, Recolección, Supervivencia, Coleccionista, Economía**. Decisión cerrada (CONCEPT 14.3).

### Battle Pass (BP)
Pase de temporada con **track free + track premium**. 100 niveles. XP separada del nivel jugador. Premium se compra con gemas o V-Bucks.

### Daily / Weekly Quests
3 dailies + 9 weeklies. Reset UTC. Recompensan gemas + BP XP. (Decisiones cerradas CONCEPT 14.7.)

### Hourly Boss Event
Cada hora en punto (HH:00) abre portal con ventana de 2 minutos. Los jugadores entran al portal, teleport masivo a HH:02 a arena cooperativa. 1 intento por hora.

### Almas (Lootboxes)
Sistema de gacha del juego. **Solo gemas, nunca V-Bucks** (regla cerrada). Drop rates visibles. Pity por (alma_type, rarity_target).

### Pity system
Garantía de drop tras X intentos fallidos. Counter por (alma, rareza objetivo). Se resetea al obtener la rareza objetivo.

### Variantes (sub-rareza)
Versiones especiales de un companion: Normal, Oro, Diamante, Arcoiris + variantes de evento (Hacker, Lava, etc). Cada variante = entrada propia en Dex.

### Rareza (8 tiers)
Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Admin.

### Dex (Collection Dex)
Libro de colección. 300+ entradas potenciales (companions × variantes principales). Recompensas por % completado.

### Universal Obtainability Rule
**Regla universal**: casi todo lo comprable con V-Bucks/gemas también es ganable jugando. Excepciones: cosméticos limitados de evento, founder pack, boosts extremos cortos.

### Same-session
Solo válido entre los 1–8 jugadores conectados a la misma instancia de servidor. Trade y Auction son same-session por limitación UEFN.

### Death penalty (leve)
Al morir: pierdes % XP del nivel actual + % gold no depositado. **NO pierdes**: gemas, ayudantes, items, quests, equipment.

### Protector
Item que mitiga la death penalty o protege equipo de fail. Tiers: Bronce, Plata, Oro, Diamante.

### First Minute Hook
Primer minuto de juego: visual impactante + acción interactiva en <10s + recompensa instantánea. **Reduce churn** del primer minuto crítico.

### Tutorial Chain
15 quests forzadas que enseñan cada mecánica. Termina desbloqueando el primer rebirth.

### Activity Log UI
Panel acumulativo de mensajes en esquina inferior-izquierda. 4 líneas, auto-fade configurable, **sin click action**.

### Idle Summary
Pantalla al volver al juego que resume producción offline + crafteos completados durante la ausencia.

### Dual-currency
Modelo monetización del proyecto: **Gemas** (premium currency jugable) + **V-Bucks** (moneda real de Fortnite). Las gemas NO se convierten a V-Bucks. Coexisten para items de shop con la regla universal de obtainability.

### Gemas
Premium currency jugable. Difícil de ganar pero ganable (drops de boss, achievements, BP). Alternativa a V-Bucks para items pagables. Persistido en `PlayerCore.Gems`.

### V-Bucks
Moneda real de Fortnite gestionada por Epic vía In-Island Transactions. **Items pagados con V-Bucks NUNCA son tradables** (anti-cashout). Detectados como entitlements vía bitfields en PlayerEconomy.

### Trading same-session
Trade directo player-to-player **dentro de la misma sesión**. Safeguards: lock de 5s tras inicial, double confirm, items con `tradable=false` bloqueados. SYS-036. F3.

### Auction same-session
NPC vendor con sistema de consignación **dentro de la misma sesión**. 5% comisión estándar. SYS-037. F3. **No hay auction global cross-session** (UEFN no lo permite).

### Rate limiting
Cooldowns en botones críticos para anti-spam-click. Configurado en `data/ui/rate_limits.json`. SYS-058. **Cross-cutting**: aplicado por todos los sistemas que lo necesitan.

### Live Edit
Modo de UEFN que permite editar el mapa con jugadores conectados. **Riesgo de session failure** si se modifica un Scene Event en uso. Epic recomienda quitar referencias específicas si te toca.

---

## D. Sistemas (referencia rápida)

> Lista canónica en CONCEPT.md sección 10. Aquí solo IDs y nombres.

| ID | Sistema |
|---|---|
| SYS-001 | Player Stats |
| SYS-002 | Inventory |
| SYS-003 | Resource Gathering |
| SYS-004 | Crafting |
| SYS-005 | Base Building |
| SYS-006 | Combat |
| SYS-007 | Zone Unlock |
| SYS-008 | Day/Night + Weather |
| SYS-009 | Death Penalty + Protection |
| SYS-010 | Companion Core |
| SYS-011 | Rarity Tiers |
| SYS-012 | Variants |
| SYS-013 | Evolution |
| SYS-014 | Companion Behavior |
| SYS-015 | Collection Dex |
| SYS-016 | XP & Levels |
| SYS-017 | Skill Points |
| SYS-018 | Skill Trees |
| SYS-019 | Active Abilities |
| SYS-020 | Rebirth System |
| SYS-021 | Achievements |
| SYS-022 | Battle Pass |
| SYS-023 | Equipment Slots |
| SYS-024 | Equipment Stats |
| SYS-025 | Equipment Leveling |
| SYS-026 | Protectors |
| SYS-027 | Set Bonuses |
| SYS-028 | Reroll Stats |
| SYS-029 | Gold |
| SYS-030 | Gems |
| SYS-031 | V-Bucks Integration |
| SYS-032 | Shop System |
| SYS-033 | Rotating Session Shop |
| SYS-034 | Lootboxes (Almas) |
| SYS-035 | Pity System |
| SYS-036 | Trading Same-Session |
| SYS-037 | Auction Same-Session |
| SYS-038 | Universal Obtainability Flag |
| SYS-039 | Quest System |
| SYS-040 | Daily Login |
| SYS-041 | Time Played Rewards |
| SYS-042 | Hourly Boss Event |
| SYS-043 | Long Events |
| SYS-044 | Short Events / Admin Abuse |
| SYS-045 | Code Redemption |
| SYS-046 | Seasonal Content Framework |
| SYS-047 | Leaderboards |
| SYS-048 | Social Display |
| SYS-049 | Activity Log UI |
| SYS-050 | Notifications System |
| SYS-051 | Auto-Sell Filters |
| SYS-052 | Pre-Inventory Filter |
| SYS-053 | Visual Compare |
| SYS-054 | Idle Summary |
| SYS-055 | Search/Filter |
| SYS-056 | Hotkeys / Radial Menu |
| SYS-057 | Error Handling UI |
| SYS-058 | Rate Limiting |
| SYS-059 | Base Level |
| SYS-060 | Base Upgrades |
| SYS-061 | Passive Generators |
| SYS-062 | Offline Production |
| SYS-063 | Crafting Timers |
| SYS-064 | First Minute Hook |
| SYS-065 | Tutorial Chain |
| SYS-066 | Contextual Tutorials |
| SYS-067 | BigNumbers Integration |
| SYS-068 | Time Sync (UTC) |
| SYS-069 | Persistence Layer |
| SYS-070 | Admin Panel |
| SYS-071 | Test/QA Framework |
| SYS-072 | Module Registry |

---

## E. Persistencia y datos

### Persistence (Verse Persistence)
Sistema de Verse para guardar datos del jugador entre sesiones. **Limitado a 4 weak_maps × 128 KB** por isla.

### Weak_map (persistable)
Estructura de datos persistente en Verse. El proyecto usa exactamente 4: PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy. Ver PERSISTENCE_MAP.md.

### PlayerCore
Weak_map #1. Contiene: gold, gemas, XP, level, rebirth count, skill points, stats. Frecuencia de escritura: alta.

### PlayerInventory
Weak_map #2. Contiene: items, equipped, companions, Dex, bank. **El más pesado**, vigilar siempre.

### PlayerProgress
Weak_map #3. Contiene: quests, achievements, BP progress, daily login, codes redeemed, time played, tutorial state, **leaderboard scores (8 slots de 8 B)**.

### PlayerEconomy
Weak_map #4. Contiene: V-Bucks entitlements, base upgrades, pity counters, trade history, active crafts.

### SkillPointEntry
Struct `<persistable>` definido en PlayerCore (`PERSISTENCE_MAP.md` §3.1). Campos: `SkillID:int` (id global del skill, ver `skill_trees.json`) + `Rank:int` (1..max_rank del skill). Un entry por cada skill con rank≥1 — skills no aprendidos no aparecen en el array. Decisión cerrada Auditoría 2 — C4 (sustituye al `[]int` plano del modelo viejo, que era ambiguo). Tamaño: 8 B por entry. Worst-case ~80 entries × 8 B = 640 B (jugador end-game). Convención: si un patch reduce `max_rank` de un skill, el load defensivo clampa el rank persistido al nuevo máximo.

### LeaderboardScore
Campo persistente en PlayerProgress (`LeaderboardScore_0` ... `LeaderboardScore_7`) que cachea el best-score de cada jugador por stat trackeada. Necesario porque Epic **no expone API para listar jugadores fuera de la sesión actual** — el ranking "global" se aproxima comparando estos valores entre jugadores presentes + snapshot histórico. Ver SYS-047 y `CONCEPT.md` §7.2.

### Schema Version
Campo `Version:int` al inicio de cada persistable. Se incrementa al añadir campos. Permite migración futura.

### Backwards Compatibility (UEFN)
**Obligatoria por Epic.** No se puede renombrar, eliminar ni cambiar tipo de un campo persistente publicado. Romperla = bloqueo de publish + corrupción de datos.

### Validación defensiva
Patrón obligatorio al cargar persistencia: verificar que los valores estén en rango razonable, corregir si no, loggear warning. Nunca crashear por datos corruptos.

### Bitfield
Optimización de tamaño: usar 1 int (32 o 64 bits) para representar N flags booleanos. Usado en achievements (256 con 32 B), Dex variants (32 con 4 B), BP rewards claimed (192 con 24 B). **Regla canónica del proyecto**: cualquier campo persistente que represente un conjunto de booleanos debe empaquetarse en bitfield si N ≤ 1024. Ver `PERSISTENCE_MAP.md` §7.4 para helpers, aplicaciones y anti-patrones.

---

## F. Workflow y proceso

### Sprint
Unidad de trabajo de **1–2 horas reales**. Granularidad de planificación. Cada sprint produce algo testeable o documentado.

### SPR-xxx
Identificador de sprint. Ej: `SPR-005` (Module Registry). Cada sprint tiene archivo, dependencias, done criteria.

### SPR-xxx-T
Sprint de test asociado al SPR-xxx principal. Crea `test_device_SPRxxx.verse`. (Ver TESTING_PROTOCOL.md.)

### Done Criteria
Lista de checkboxes que define cuándo un sprint está completo. Sin done criteria = sin alcance = scope creep.

### test_device
Device temporal de Verse que instancia clases nuevas y valida comportamiento. Lo más cerca de unit tests posible en UEFN. Se borra del level antes de publish.

### smoke_test_master
Device permanente que ejecuta todos los smoke tests al iniciar. Se queda en producción (es safe, solo loggea).

### Daily Log
Registro diario del trabajo: sprints completados, bloqueos, decisiones, tokens consumidos. (Plantilla en PROMPT_TEMPLATES.md.)

### Postmortem
Documento corto tras una crisis (>30 min de recuperación). Identifica causa raíz, resolución, prevención futura. (Carpeta `docs/postmortems/`.)

### Briefing matinal
Sesión de 15-30 min con Opus al inicio del día. Define los 5–7 sprints del día con sus specs.

### Cápsula (DEEPSEEK_CAPSULE)
5 líneas mínimas que se pegan al inicio de CADA chat con DeepSeek. Recuerda las reglas inquebrantables.

### Escalar (a Opus)
Acción de DeepSeek (o tú) cuando hay decisión arquitectónica, schema de persistencia, conflicto entre docs, o bloqueo serio. **Mejor 5 min de pregunta que 2h de recuperación.**

### Build budget / Token budget
Tokens que se gastan en cada acción con IAs. Tracking obligatorio en Daily Log. Optimizaciones en WORKFLOW.md sección 6.

---

## G. Roles e identificadores

### Opus (Director / Arquitecto)
Claude Opus 4.7. Diseña arquitectura, planifica sprints, valida persistencia, resuelve dudas complejas. **1-2 veces al día**, sesiones de 30-60 min.

### DeepSeek (Ejecutor)
DeepSeek V4-Pro/Flash. Escribe código Verse/Python rutinario, JSONs masivos, corrige errores, refactors mecánicos. **La mayor parte del día.**

### Tú (Puente / Filtro / Tester)
El humano. Mueve archivos entre IAs y UEFN, ejecuta Build/Push, testea in-session, decide cuándo escalar, mantiene Daily Log.

### Admin (player ID)
Jugador autorizado a comandos admin. **La API Verse de `player` NO expone getter de identidad estable** — no existen `GetID()`, `GetName()` ni `GetAccountID()` (fuente oficial: [dev.epicgames.com — verse-api/versedotorg/simulation/player](https://dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player), único método público documentado: `IsActive[]`). Identificación se hace vía uno o varios `player_reference_device` configurados en editor UEFN con las cuentas admin, comprobando `AdminRef.IsRegistered[Agent]` en runtime. `data/admin/admin_config.json` lleva el catálogo de comandos y metadata; **NO** lleva la lista de IDs de jugador. Decisión cerrada Auditoría retrospectiva Bloque 1 (sustituye al patrón previo `player.GetID() == ADMIN_ID` que era inválido).

### Cuenta-test
Cuenta de Epic dedicada a testear cambios de schema o features delicadas. Tener al menos UNA cuenta-test con datos previos para validar updates.

---

## H. Acrónimos y abreviaturas

| Acrónimo | Significado |
|---|---|
| **AFK** | Away From Keyboard. Anti-AFK = sistema que kickea inactivos. |
| **API** | Application Programming Interface. |
| **BP** | Battle Pass. |
| **CTA** | Call To Action. Botón principal de una UI. |
| **DAG** | Directed Acyclic Graph. Estructura sin ciclos (prerequisites de quests/skills). |
| **DEX** | Index/Dex de companions coleccionados. |
| **F0–F5** | Fases del roadmap. F0=Foundation, F1=MVP playable, F2=Companions & Collection, F3=Economy & Equipment, F4=Base persistente & Live Ops, F5=Hourly Boss + Social + Polish. (CONCEPT §12.2) |
| **F2P** | Free To Play. |
| **HUD** | Heads-Up Display. UI overlay durante gameplay. |
| **IDE** | Integrated Development Environment (VS Code, Cursor). |
| **JSON** | JavaScript Object Notation. Formato de datos. |
| **MVP** | Minimum Viable Product. La Fase 1. |
| **NPC** | Non-Player Character. |
| **OODA** | Observe-Orient-Decide-Act. Loop de toma de decisiones. |
| **P2W** | Pay To Win. |
| **PvE** | Player vs Environment. |
| **PvP** | Player vs Player. **No hay PvP en este proyecto.** |
| **QoL** | Quality of Life. SYS-051 a SYS-058. |
| **SDK** | Software Development Kit. |
| **SPR** | Sprint identifier (SPR-xxx). |
| **SSO** | Single Sign-On. |
| **SYS** | System identifier (SYS-xxx). |
| **TDAH** | Trastorno por Déficit de Atención e Hiperactividad. |
| **UEFN** | Unreal Editor for Fortnite. |
| **UI** | User Interface. |
| **UTC** | Coordinated Universal Time. Source of truth temporal. |
| **UX** | User Experience. |
| **V-Bucks** | Moneda real de Fortnite. |
| **VFX** | Visual Effects. |
| **XP** | Experience Points. |

---

## 📌 Resumen ejecutivo

```
🎯 ESTE DOCUMENTO ES LA REFERENCIA RÁPIDA de naming oficial.

🔑 USO TÍPICO:
   - DeepSeek pregunta "¿qué es BP?" → busca aquí
   - Confusión entre Player Level y Base Level → busca aquí
   - SPR-xxx vs SYS-xxx → busca aquí
   - Acrónimo no conocido → busca aquí

⚠️ JERARQUÍA DE FUENTES (en caso de conflicto):
   - Naming → este doc gana
   - Catálogo de SYS-xxx → SYSTEMS_INDEX.md gana
   - Backlog SPR-xxx → SPRINTS_BACKLOG.md gana
   - Rutas de archivos → FOLDER_STRUCTURE_TRUTH.md gana
   - Deps módulos Verse → MODULES_DEPENDENCY_GRAPH.md gana
   - Decisiones de diseño → CONCEPT.md §14 gana
   - Reglas de persistencia → PERSISTENCE_MAP.md gana
   - Schemas JSON → JSON_SCHEMAS.md gana
   - Balance/números → BALANCE_FORMULAS.md gana
   - Pipeline build → BOOTSTRAP_PIPELINE.md gana

📚 ESTE DOC NO REEMPLAZA a CONCEPT.md u otros docs especializados.
   Es una capa rápida de consulta para "¿qué significa X?".
```

---

**Fin del documento.**

> Este documento se actualiza cada vez que se introduce un término nuevo o cambia un naming.
