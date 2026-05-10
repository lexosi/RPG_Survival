# 📘 CONCEPT — Survival Tycoon Modular Map (UEFN)

> **Documento maestro del proyecto.**
> Concepto, sistemas, decisiones, sprints y arquitectura modular.
> **Agnóstico de modelo de IA.** Optimizado para sprints cortos (1–2 h) con presupuesto de tokens limitado.

---

## 🧭 Índice rápido

1. [Visión y filosofía](#1-visión-y-filosofía)
2. [Pilares del juego](#2-pilares-del-juego)
3. [Loop core y capas de progresión](#3-loop-core-y-capas-de-progresión)
4. [Arquitectura modular (motor de mapas)](#4-arquitectura-modular-motor-de-mapas)
5. [Restricciones reales de UEFN](#5-restricciones-reales-de-uefn)
6. [⭐ Python en UEFN (qué hace y qué NO)](#6-python-en-uefn-qué-hace-y-qué-no)
7. [⭐ Verse en UEFN (qué hace y qué NO)](#7-verse-en-uefn-qué-hace-y-qué-no)
8. [⭐ Mapping Python ↔ Verse por sistema](#8-mapping-python--verse-por-sistema)
9. [⭐ Pipeline de build completo](#9-pipeline-de-build-completo)
10. [Catálogo completo de sistemas](#10-catálogo-completo-de-sistemas)
11. [Estructura de carpetas y archivos](#11-estructura-de-carpetas-y-archivos)
12. [Plan por fases (roadmap)](#12-plan-por-fases-roadmap)
13. [Backlog de sprints (1–2 h cada uno)](#13-backlog-de-sprints-1-2-h-cada-uno)
14. [Decisiones cerradas (referencia)](#14-decisiones-cerradas-referencia)
15. [Convenciones técnicas](#15-convenciones-técnicas)
16. [Glosario](#16-glosario)

---

## 1. Visión y filosofía

### 1.1 Identidad del juego

**Survival Tycoon de exploración progresiva con coleccionismo de ayudantes.**

El jugador empieza con nada en una zona inicial pequeña. Farmea recursos, construye y mejora su base, recluta ayudantes coleccionables que mejoran sus stats y generan recursos pasivamente, sube de nivel, distribuye skill points en builds personalizadas, derrota bosses para desbloquear nuevas zonas, y eventualmente hace **rebirth** rápido y frecuente para acceder a meta-progresión permanente.

**Comparable a**: Stardew Valley + Palworld + Cookie Clicker + Don't Starve, fusionados, en Fortnite.

### 1.2 Objetivo del proyecto

**No es un juego, es una máquina de hacer juegos.**

Construimos UNA vez la lógica core en Verse. A partir de ahí, cualquier mapa nuevo se hace cambiando JSONs y assets. El segundo mapa cuesta ~10–20% del esfuerzo del primero.

**Mapas-objetivo de la misma máquina (ejemplos)**:
- Chocolate Tycoon Collectors (dulces, fábrica)
- Mythic Beasts (fantasy medieval, castillo)
- Galactic Pet Tycoon (sci-fi, estación espacial)
- Cursed Souls (horror, mansión gótica)
- Ocean Empire (marino, submarino)

### 1.3 Audiencia y plataforma

- **Plataforma principal**: Fortnite (PC, consola, móvil) vía UEFN
- **Optimización móvil obligatoria desde día 1**
- **Sesión típica objetivo**: 30–90 min
- **Idioma**: auto-localization a 14 idiomas de Fortnite (gratis vía UEFN)

### 1.4 Filosofía de diseño

1. **Modular real**: 90% del contenido nuevo entre mapas debe poder hacerse cambiando datos, sin tocar lógica.
2. **Regla universal de obtención**: casi todo lo comprable con V-Bucks/gemas también es ganable jugando. Nadie es "free-to-lose".
3. **Onboarding integrado**: el tutorial son las quests. Primer rebirth en 20–30 min para enseñar el loop completo.
4. **Profundidad gradual**: complejidad se desbloquea con progresión, no se vomita al inicio.
5. **Persistencia es el ADN**: todo se guarda. El jugador siempre vuelve a algo suyo.
6. **Honesto sobre limitaciones de UEFN**: nunca prometemos lo que la plataforma no permite.

---

## 2. Pilares del juego

| # | Pilar | Por qué |
|---|---|---|
| 1 | **Survival + Tycoon + Coleccionismo** fusionados | Identidad propia, no es clon de Brainrot |
| 2 | **Modular machine**: JSON → Python → Verse | Escalabilidad de portfolio |
| 3 | **Dual-currency**: Gemas (jugando) ⇄ V-Bucks (pagando) | Modelo F2P respetuoso |
| 4 | **Regla universal**: pagable = también ganable | Anti-P2W narrativo, mejor retention |
| 5 | **Rebirth rápido y frecuente** (primer rebirth ≤30 min) | Loop endgame mostrado pronto |
| 6 | **Quests = tutorial integrado** | Mejor onboarding del mercado |
| 7 | **PvE only** + interacción social same-session | Sin pay-to-grief, low conflict |
| 8 | **Coleccionismo masivo** (50+ ayudantes × variantes × rarezas) | Retention de largo plazo |
| 9 | **Death penalty leve** + protección comprable/ganable | Tensión sin frustración |
| 10 | **First minute hook** visual + acción inmediata | Reduce churn brutal del primer minuto |
| 11 | **Optimización móvil** desde día 1 | Audiencia mobile = 60%+ de Fortnite |
| 12 | **Base permanente** que sobrevive a rebirths | Eje de progresión global |

---

## 3. Loop core y capas de progresión

### 3.1 Loop core (sesión típica)

```
   SPAWN EN BASE PERSISTENTE
        │
        ▼
   FARMEAR RECURSOS ──────────► CONSTRUIR / MEJORAR BASE
        │                              │
        ▼                              ▼
   COMBATE / EXPLORACIÓN          RECLUTAR AYUDANTES
        │                              │
        ▼                              ▼
   SUBIR XP + DISTRIBUIR        COLECCIONAR / DEX
   SKILL POINTS                       │
        │                              ▼
        ▼                       COMPLETAR QUESTS
   DERROTAR BOSSES               (DAILY/WEEKLY)
        │                              │
        ▼                              ▼
   DESBLOQUEAR ZONAS ──► ACUMULAR GEMAS (lento)
        │                              │
        ▼                              ▼
   EVENTUAL REBIRTH ◄──────── COMPRAR / GACHA / TRADE
```

### 3.2 Cuatro relojes corriendo en paralelo

| Reloj | Ritmo | Qué siente el jugador |
|---|---|---|
| **Sesión** | 5–10 min | "Acabo de mejorar algo" |
| **Día** | 30–90 min | "Subí 3 niveles, encontré ayudante raro" |
| **Semana** | 5–10 h | "Completé zona, derroté boss" |
| **Mes** | 30–50 h | "Hice rebirth, todo cambia" |
| **Largo plazo** | 100 h+ | "Voy por mi rebirth 25, persigo el Secret" |

### 3.3 Tres ejes de progresión paralelos

| Eje | Se resetea al rebirth | Función |
|---|---|---|
| **Nivel jugador** | Sí (con bonus permanente) | Power ramping de cada run |
| **Rebirth count** | Nunca (acumula) | Meta-progresión exclusiva |
| **Base level** | **Nunca** | Spina dorsal + gate maestro de contenido |

---

## 4. Arquitectura modular (motor de mapas)

### 4.1 Las tres capas

```
┌─────────────────────────────────────────────────┐
│  CAPA 1: DATA LAYER                              │
│  archivos JSON con todo el contenido tematizable │
│  ► criaturas, items, quests, precios, biomas...  │
└────────────────┬────────────────────────────────┘
                 │ leídos por
                 ▼
┌─────────────────────────────────────────────────┐
│  CAPA 2: BUILD LAYER (PYTHON)                    │
│  scripts editor-time en UEFN editor              │
│  ► generan prefabs, pueblan mapa, exportan       │
│    constantes a archivos .verse                  │
└────────────────┬────────────────────────────────┘
                 │ produce
                 ▼
┌─────────────────────────────────────────────────┐
│  CAPA 3: RUNTIME LAYER (VERSE)                   │
│  lógica del juego en runtime                     │
│  ► lee constantes generadas, ejecuta gameplay    │
│  ► CÓDIGO ESTÁTICO, NO SE TOCA ENTRE MAPAS       │
└─────────────────────────────────────────────────┘
```

### 4.2 Filosofía clave

> **Para hacer un mapa nuevo: solo se editan JSONs y assets. Verse no se toca jamás (idealmente).**

El 80–90% del contenido entre mapas se intercambia con esto. El 10–20% restante (decoración fina, iluminación artística, audio mixing, importar meshes custom) requiere trabajo manual en UEFN editor.

### 4.3 Flujo de creación de un nuevo mapa

```
1. Copiar el repo template del proyecto
2. Editar /data/*.json con contenido nuevo
3. Importar assets (meshes, texturas, audio) en /Content/Assets/
4. Ejecutar scripts Python desde UEFN: Tools > Execute Python Script
5. Compilar Verse (Build Verse Code)
6. Push Changes en UEFN
7. Test en sesión live + Mobile Preview
8. Iterar JSON/assets si hace falta
9. Publish a Creator Portal
```

**Tiempo estimado para mapa #2 (con motor ya estable)**: 2–4 semanas.

---

## 5. Restricciones reales de UEFN

> **CRÍTICO LEER ANTES DE PROPONER NADA.** Estas son las paredes reales contra las que vamos a chocar.

### 5.1 Persistencia (Verse Persistence)

- **Máximo 4 weak_maps persistentes por isla**. Punto.
- **Tamaño máximo: 128 KB por persistable**.
- **Backwards compatibility OBLIGATORIA**: Epic bloquea publish si rompes estructura.
- **Solo añadir campos opcionales con default values**. Nunca renombrar, nunca eliminar.
- **Distribución obligada de los 4 weak_maps**:
  1. `PlayerCore` — gold, gemas, XP, level, rebirth count, skill points, stats
  2. `PlayerInventory` — inventario, equipo, ayudantes, Dex
  3. `PlayerProgress` — quests, achievements, BP progress, daily login streak, codes redeemed
  4. `PlayerEconomy` — compras V-Bucks, trade history, listings activas, base upgrades

### 5.2 Lo que NO se puede hacer (descartado de raíz)

| Imposible en UEFN | Por qué |
|---|---|
| Trade asíncrono cross-session | No hay base de datos compartida entre instancias |
| Auction House global | Misma razón |
| Snapshot/backup separado de datos | Solo 4 weak_maps; gastar 1 en backup es derrochar |
| Transaction log persistente extenso | 128 KB no llega |
| Admin recovery panel cross-session | No hay API para acceder a datos de jugadores fuera de su sesión |
| Detección automática de Epic friends | No expuesta en Verse |
| Códigos editables en runtime | Lista compilada en publish |
| Notificaciones push fuera de sesión | No existen |

### 5.3 Lo que YA HACE Fortnite (no implementar — solo configurar)

| Feature | Cómo |
|---|---|
| Anti-AFK | Kick automático a los 15 min de inactividad |
| Filtro de chat / nombres | Gestionado por Epic |
| Voice chat | Nativo, configurable en Island Settings |
| Telemetría básica | Creator Portal Analytics + Analytics Device gratis |
| Versioning de persistencia | Epic enforza compat al publicar |
| Matchmaking | Configurable en Island Settings |
| Localización a 14 idiomas | Auto-localization free |

### 5.4 Lo que sí se puede pero con trampas

| Sistema | Cómo se hace realmente |
|---|---|
| Trade entre jugadores | Solo same-session (mismos 1–8 jugadores conectados) |
| Auction local | NPC vendor con consignación same-session |
| Leaderboard global | `leaderboard_device` muestra rankings; **datos cross-session vienen de Verse Persistence (weak_map), no del device** — Epic no expone API para listar jugadores fuera de sesión actual. Top-N se reconstruye comparando entradas de jugadores presentes + caché persistente. |
| Notificaciones | `hud_message_device` (pool max 3, ver §7.4) + `popup_dialog_device` + custom widgets para overflow |
| Códigos canjeables | Pre-pool grande compilado, activar manualmente |
| Admin commands | `player_reference_device` configurado en UEFN editor con la cuenta admin + `AdminRef.IsReferenced[Agent]<transacts><decides>:void` en runtime (failable, llamar con `[]`). Verse NO expone identidad estable del jugador en su API pública (no existe `player.GetID()`/`GetName()`/`GetAccountID()` — fuente: dev.epicgames.com/documentation/en-us/fortnite/verse-api/versedotorg/simulation/player). Patrón canónico: `Core/AdminCommands` namespace stateless + `Devices/AdminPanel` device con `@editable AdminRefs` (cross-ref `VERSE_SYNTAX_GUIDE.md` §1 lección 17 + §2.4-bis). B1.1-fix SPR-010: la versión previa de esta fila mencionaba `IsRegistered` que era API ficticia; real es `IsReferenced`. |

### 5.5 Optimización móvil — reglas duras

- World Partition + HLODs activado
- Texturas máximo 512×512, potencias de 2
- Mesh LODs en TODO (sobre todo ayudantes que se instancian masivamente)
- HISM (Hierarchical Instanced Static Meshes) para droppers/decoración repetida
- 1 material por mesh siempre que se pueda
- Mobile Preview en flujo de testing desde día 1
- Spatial Profiler para detectar memory leaks
- Optimize Texture / Optimize Static Mesh tools (v39.00) usados activamente

### 5.6 Restricciones temporales

- Verse usa tiempo de servidor (UTC) consistente entre todos los jugadores de la sesión
- `GetSimulationElapsedTime()` es la fuente de verdad temporal (devuelve `float` segundos desde inicio de simulación; combinar con anchor capturado en `OnBegin` para epoch UTC absoluto)
- Eventos hora-en-punto se sincronizan vía UTC, NO hora local del cliente

### 5.7 Restricciones In-Island Transactions (V-Bucks)

> Política Epic vigente. Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/in-island-transactions-overview-in-fortnite + release notes v39.00.

- **API live desde 9 enero 2026.** Antes de esa fecha solo testing en proyectos no publicados.
- **Revenue split**: 100% del valor V-Bucks al creador **hasta 31 enero 2027**. Desde 1 febrero 2027 → 50%/50% con Epic.
- **Refund window**: Epic puede iniciar refunds masivos vía Creator Portal hasta **20 días tras la compra**. Items entregados **NO se revocan**. Implicación de diseño:
  - No diseñar mecánicas que asuman irreversibilidad antes de 20 días (ej: no permitir convertir un companion premium en gems no-revocables hasta pasados 20 días desde la compra).
  - Ofertas de alto valor: considerar entrega progresiva (parte ahora, parte tras 21 días) si la economía interna lo justifica.
  - El refund afecta solo a los V-Bucks del jugador, no a tu inventario interno.
- **`ConsequentialToGameplay = True`** obligatorio (en código Verse) para items que dan ventaja gameplay (companions premium, equipment, gem packs, BP). Cosméticos puros van con `false`. **Etiquetar mal = oferta rechazada en publish.** Regla a nivel JSON: `data/economy/vbucks_offers.json` lleva campo `consequential_to_gameplay: bool [REQUIRED]` (ver `JSON_SCHEMAS.md` §17).
- **Sales finales**: todas las transacciones son ventas definitivas para el jugador — solo Epic puede iniciar refunds desde Creator Portal.
- **Reporting**: tasa de denuncias por oferta visible en Creator Portal. Si supera la media del ecosistema, Epic notifica.
- **Renaming v39.10**: API antiguo `product` → `entitlement`. Toda la documentación del proyecto usa `entitlement`.

---

## 6. Python en UEFN (qué hace y qué NO)

> **⭐ ESTA SECCIÓN ES CRÍTICA. La IA no debe buscar info de Python en UEFN cada vez. Está toda aquí.**
> **Estado verificado: mayo 2026, UEFN v40.00.**

### 6.1 Estado actual de Python en UEFN

- **UEFN v40.00** (lanzada en abril 2026) liberó **Python Editor Scripting** en modo experimental.
- Hay que **activarlo manualmente** en `Project Settings > Plugins > Python Editor Script Plugin`.
- Versión: **Python 3.11**.
- Acceso al módulo `unreal` completo (mismo que Unreal Engine 5.7).
- Existe ecosistema de herramientas comunitarias maduras: **UEFN-TOOLBELT** (287+ tools open-source), **MCP servers** que conectan IA externa al editor.
- Documentación oficial: `dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python`.

### 6.2 Filosofía Python-first

> **Antes de proponer un paso manual, intenta automatizarlo con Python.**

Python en UEFN existe para **eliminar el "iteration tax"**: el coste enorme de tareas repetitivas en el editor. Si una tarea se hace más de 3 veces, debe ser un script Python.

**Esto NO es opcional**: es el pilar técnico que hace la "máquina de mapas" viable. Sin maximizar Python, cada mapa nuevo cuesta semanas de trabajo manual.

### 6.3 Lo que Python en UEFN SÍ puede hacer (build-time)

#### 🔹 Gestión de actors en escena
- `actor_subsystem.spawn_actor_from_class()` — spawn programático
- `actor_subsystem.destroy_actor()` — eliminación masiva
- `actor.set_actor_location()`, `set_actor_rotation()`, `set_actor_scale3d()` — transform
- `actor.set_actor_label()` — renombrar
- Acceder y modificar **propiedades editable** de actors (`set_editor_property()`)
- Detectar selección actual en viewport
- Agrupar/duplicar masivamente

#### 🔹 Gestión de assets en Content Browser
- `asset_subsystem.list_assets()` — listar todo
- `asset_subsystem.duplicate_asset()`, `rename_asset()`, `delete_asset()`
- `asset_subsystem.does_asset_exist()`, `save_asset()`
- Importación masiva de FBX, texturas, audio
- Generación de Materials desde código (MaterialEditingLibrary)
- Reasignación masiva de materiales en meshes
- Crear/modificar **Material Instances** programáticamente

#### 🔹 Gestión de niveles
- `level_subsystem.get_current_level()` — info del level actual
- `level_subsystem.load_level()` — cambiar de nivel
- World Partition queries (qué celdas existen, qué actors hay en cuál)

#### 🔹 Generación de archivos
- Crear/modificar archivos `.verse` en `Content/Verse/Generated/`
- Crear/modificar `.json` en `data/`
- Crear/modificar `.uplugin`, configs, manifests
- Generar **boilerplate Verse** desde JSONs (constantes, enums, estructuras)

#### 🔹 Generación procedural de contenido
- **Poisson-disk scattering** para distribuir props sin solapes
- Generación de arenas simétricas con un comando
- Procedural building generation
- Distribución algorítmica de resource nodes en biomas
- Replicación de prefabs (50 droppers idénticos con offsets)

#### 🔹 Validación y QA
- Validar JSONs contra schemas
- Verificar que cada `companion_id` en JSON tiene mesh asociado
- Comprobar que se respetan budgets de memoria
- Detectar referencias rotas a assets eliminados
- Lint de código Verse generado

#### 🔹 Ejecución
- **`init_unreal.py`**: ejecuta automáticamente al abrir el proyecto.
- **`Tools > Execute Python Script`**: ejecutar arbitrariamente desde menú.
- **MCP servers**: ejecución remota desde IA externa (Claude Code, Cursor).
- **Comandos de menú custom**: añadir botones al toolbar/dropdown del editor.

#### 🔹 Subsystems pre-poblados (vía init_unreal.py del proyecto)
**Importante**: estas variables NO son built-ins de UEFN. Las prepuebla `init_unreal.py` (convención de UEFN-TOOLBELT, UEFN-MCP-Server y similares). Si tu proyecto usa uno de estos frameworks, las tendrás. Si no, hay que instanciar manualmente.

```python
# Si init_unreal.py está configurado (recomendado), están disponibles:
unreal       # módulo completo (siempre disponible, ESTE sí es built-in)
actor_sub    # ActorSubsystem
asset_sub    # AssetSubsystem
level_sub    # LevelSubsystem

# Equivalentes manuales (sin init_unreal.py):
import unreal
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
```

**Convención del proyecto**: usar `init_unreal.py` (SPR-001 incluye scaffolding). Todos los scripts en `scripts/build/` y `scripts/tools/` asumen las 3 variables disponibles.

### 6.4 Lo que Python en UEFN NO puede hacer (limitaciones reales)

#### ❌ Python NO corre en runtime del juego
- Los scripts solo se ejecutan **dentro del editor UEFN abierto**.
- Cuando el mapa se publica y un jugador lo juega, **Python no existe ahí**.
- Toda la lógica de gameplay tiene que estar en Verse.

#### ❌ Python NO compila Verse
- UEFN compila Verse internamente (Build Verse Code, Ctrl+Shift+B).
- Python puede **generar** archivos `.verse`, pero no compilarlos.
- Workflow: Python genera → desarrollador o IA pulsa Build Verse Code.

#### ❌ Python NO accede a la persistencia
- Las `weak_map` persistentes son runtime de Verse.
- Python no puede leer/escribir datos de jugadores.
- Python no puede hacer "snapshot" de progresión de jugadores.

#### ❌ Python NO se ejecuta sin editor abierto
- No hay forma de programar tareas Python en CI/CD que toquen UEFN.
- Si quieres automatizar build, necesitas un humano (o un agente IA con UEFN abierto).
- **Excepción**: scripts puramente de filesystem (validar JSON, generar markdown) sí pueden correr sin UEFN.

#### ❌ Python NO modifica el código Verse en runtime
- Una vez compilado y publicado, Verse es estático. Python no puede "hot-reload" lógica de juego.

#### ❌ Limitaciones técnicas sutiles
- Algunos actors necesitan **refresh manual** tras spawn (construction scripts no siempre se ejecutan automáticamente).
- Operaciones grandes pueden bloquear el editor (usar batch processing y async patterns).
- No todos los devices de UEFN tienen API Python expuesta (priorizan los más usados).
- Las llamadas a `unreal.*` deben hacerse en main thread (UEFN-TOOLBELT y otros frameworks lo gestionan).

#### ❌ Python NO sustituye al diseño manual artístico
- Iluminación artística fina
- Audio mixing
- Decoración ambiental con sentido estético
- Importar y configurar meshes custom de Blender (paso inicial)

### 6.5 Reglas de oro Python en UEFN

1. **Idempotencia obligatoria**: cualquier script debe poder ejecutarse N veces con mismo resultado.
2. **Logging detallado**: usar `unreal.log()`, `unreal.log_warning()`, `unreal.log_error()` siempre.
3. **Try/except defensivo**: el editor no debe crashear si un script falla.
4. **No mutar el viewport sin avisar**: si el script va a borrar 500 actors, primero confirmar.
5. **Undo support**: usar `unreal.ScopedEditorTransaction` cuando se modifican actors → permite Ctrl+Z al user.
6. **Performance**: para operaciones masivas, agrupar en batches y mostrar progreso.
7. **Path resolution**: usar `unreal.SystemLibrary.get_project_directory()` para rutas, nunca hardcodear.
8. **Comentarios y docstrings**: cada función pública con docstring estilo Google.

### 6.6 Tooling externo aprovechable

- **UEFN-TOOLBELT** (open-source, 287+ tools): material presets, procedural generators, Verse code bridges, project scaffolding, MCP-ready. **Usar como base, no reinventar la rueda.**
- **Unreal MCP** (KirChuvakov, 22+ tools): control remoto desde Claude Code, Cursor.
- **VerseWithGPT / Verse Tool**: GPTs especializados que conocen las APIs Verse digestidas.

---

## 7. Verse en UEFN (qué hace y qué NO)

> **⭐ ESTA SECCIÓN ES CRÍTICA. La IA no debe buscar info de Verse en UEFN cada vez. Está toda aquí.**
> **Estado verificado: mayo 2026, UEFN v40.00.**

### 7.1 Estado actual de Verse

- Verse es el **lenguaje runtime oficial** de UEFN. Cualquier lógica de gameplay vive aquí.
- En modo **beta extendida**: las APIs siguen evolucionando, hay funciones experimentales y deprecaciones periódicas.
- Documentación oficial: `dev.epicgames.com/documentation/en-us/uefn/learn-programming-with-verse-in-unreal-editor-for-fortnite`.
- **No hay compilador standalone**: solo se compila dentro del editor UEFN (Build Verse Code).

### 7.2 Lo que Verse SÍ puede hacer

#### 🔹 Gameplay logic completa
- Reaccionar a eventos de jugadores (`PlayerJoinedEvent`, `EliminationEvent`, etc.)
- Controlar dispositivos UEFN (`button_device`, `trigger_device`, `teleporter_device`, `hud_message_device`, etc.)
- Crear devices custom (clases que extienden `creative_device`)
- Gestionar timers, cooldowns, state machines
- Spawn dinámico de props, items, mobs en runtime

#### 🔹 Persistencia de jugadores
- `var <Name>:weak_map(player, <T>) = map{}` para guardar progreso. `<T>` es típicamente una `class<final><persistable>` (los 4 buckets root del proyecto: PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy), aunque también se permite `struct<persistable>` (sin herencia) o tipos primitivos. Sintaxis canónica oficial: `weak_map(K, V)` con paréntesis — NO `weak_map[K]V` (esa es sintaxis de `map`, no de `weak_map`). Ver `PERSISTENCE_MAP.md` §3 y `API_REFERENCE_GENERATED.md` §3.4.
- **Máximo 4 weak_maps por isla** (subido de 2 a 4 en agosto 2025)
- **Máximo 128 KB por persistable**
- Backwards compatibility forzada por Epic al publicar
- Verse Persistence Best Practices: solo añadir campos opcionales con defaults

#### 🔹 Sistema temporal (UTC)
- `GetSimulationElapsedTime()` da simulation time consistente entre jugadores (módulo `/Verse.org/Simulation`, devuelve `float` con segundos desde inicio de simulación)
- Sleep, async, timers funcionan
- **Atención**: hay que calcular epoch UTC manualmente (combinando simulation time con momento de arranque)

#### 🔹 UI custom
- `widget_message_block`, `texture_block`, `button_widget`, `canvas` y derivados
- View Models para custom widgets en UEFN
- Asset reflection: exponer texturas/meshes a Verse desde UEFN
- **Localización**: `<localizes>` para strings, auto-localization a 14 idiomas

#### 🔹 Math y data
- Tipos: `int`, `float`, `string`, `logic`, `vector3`, `rotation`, `transform`
- Colecciones: `array`, `map`, `tuple`, `option`, `comparable`
- Failure context con `decides`, manejo de fallos elegante
- Estructuras y clases con herencia

#### 🔹 Concurrency
- `spawn{}` para fire-and-forget
- `race`, `rush`, `sync`, `branch` para combinar tareas async
- Cancelación elegante de tareas en curso

#### 🔹 Scene Graph (beta, publicable)
- Sistema Entity/Component/Prefab
- Prefabs reutilizables con lógica Verse incrustada
- **Limitación**: NO compatible con Static Meshes de Fortnite ni assets de FAB. Solo meshes custom .fbx o creados con modeling tools.

#### 🔹 Physics APIs (v39.50, feb 2026)
- Manipulación de props físicos
- Puzzles dinámicos
- Destrucción
- Add Physics, Chaos Visual Debugger

#### 🔹 Leaderboards globales
- `leaderboard_device` muestra UI de ranking; el dato global se construye **vía Verse Persistence** (campo `LeaderboardScore` en weak_map), no por el device en sí
- **Limitación dura de Epic**: no hay API para listar jugadores fuera de la sesión actual — el "global" se aproxima cacheando best-scores en persistencia de cada jugador y mostrando top-N de los presentes + snapshot histórico
- Limitado en cantidad de stats trackeadas (~6-8 por mapa según convención comunitaria)
- Fuente: https://dev.epicgames.com/documentation/en-us/fortnite/make-your-own-ingame-leaderboard-in-verse

#### 🔹 In-Island Transactions
- API live desde 9 enero 2026
- Detectar entitlements compradas con V-Bucks
- Otorgar items correspondientes
- API renamed product → entitlement en v39.10

#### 🔹 Procedural Building (template oficial)
- Shape Grammar para generación procedural
- Útil para variantes de mapa

#### 🔹 NPC AI mejorado
- Vía componentes Scene Graph
- Más granular y escalable que el viejo sistema de Guards

### 7.3 Lo que Verse NO puede hacer

#### ❌ Acceder a información cross-session
- No hay base de datos compartida entre instancias.
- **Trade asíncrono entre jugadores no conectados a la vez = imposible.**
- Auction House global = imposible.
- Ver "qué está pasando en otra sesión" = imposible.

#### ❌ Backup/rollback de persistencia
- No hay snapshots, ni rollback, ni export de datos.
- Solo 4 weak_maps × 128 KB. Gastar uno en backup es derroche.
- Si Epic borra datos por bug suyo, no hay recuperación.

#### ❌ Editar persistencia tras publicar
- Una vez publicada una estructura, NO se puede:
  - Renombrar campos
  - Eliminar campos
  - Cambiar tipos
- Solo se permite añadir campos opcionales con defaults.
- Mover archivos Verse con persistencia entre carpetas = romper compat.

#### ❌ Acceder a recursos del sistema operativo
- No file I/O, no network calls fuera de los APIs Epic-provided
- No HTTP requests a servicios externos
- No acceso a Epic Online Services directos (excepto vía devices Fortnite)

#### ❌ Detectar amistades de Epic Games
- No hay API para saber si dos jugadores son friends.
- No se pueden hacer mecánicas de "trae a un amigo" automáticas (excepto con códigos).

#### ❌ Modificar dinámicamente la lista de códigos canjeables
- Lista compilada en publish.
- Para añadir códigos nuevos = republish.
- Workaround: pre-pool grande activable manualmente.

#### ❌ Notificaciones push fuera de sesión
- No existen.
- Si alguien compra tu auction y no estás conectado, no te enteras hasta que vuelvas.

#### ❌ Detectar idioma del cliente programáticamente
- La auto-localization se aplica automáticamente, pero Verse no sabe en qué idioma está el jugador.
- No se puede personalizar lógica por idioma.

#### ❌ Acceder a la cámara/viewport del jugador
- Las APIs de cámara son limitadas (cinematic_sequence_device para cinemáticas)
- No se puede tomar screenshots desde Verse
- No se puede tracking de movimiento ratón en runtime

#### ❌ Modificar Island Settings en runtime
- Max players, modo de juego, configs base = solo en editor.

#### ❌ Compilarse fuera de UEFN
- No hay compilador standalone.
- No se puede usar Verse fuera del editor de UEFN.

### 7.4 Bugs y trampas conocidas (mayo 2026)

- **HUD Message Devices**: comportamiento inestable cuando hay >3 instancias activas simultáneas y/o cuando coexiste con custom UI canvas. Manifestación frecuente: tras los 3 primeros mensajes el resto deja de mostrar texto (sonido sí dispara). Bug confirmado en foros desde 2023 hasta 2025 con varias regresiones (v26.00, v31.00 con `Hide(Agent)` rompiendo código previo). **Estrategia obligatoria**: pool de máximo 3 hud_message_devices reusables + fallback a custom widgets cuando coexista con canvas. Fuentes: forums.unrealengine.com/t/hud-message-devices-not-showing-messagf/2280787 + .../major-verse-uefn-hud-message-device-will-not-function-when-custom-ui-is-being-displayed-to-the-player/747312.
- **Scene Events**: efectivamente experimentales por Live Edit session failure risk. Epic recomienda quitar referencias específicas si te toca.
- **Chapter 7 gallery assets**: cristales rompibles en UEFN no aparecen al publicar (bug conocido).
- **`weak_map` con `GetSession`**: roto en juegos con rondas, crashea 99% del tiempo. Usar solo en juegos sin rondas. Fuente literal: forums.unrealengine.com/t/weak-map-with-getsession-is-broken-and-does-not-persist-between-rounds-and-crashes/1263028 + bug v26.10 .../major-weak-map-getsession-broken-in-26-10/1292369. Decisión del proyecto: el juego es **sin rondas** (loop idle/RPG), por lo que esta limitación no nos afecta directamente; documentado para advertir si alguna feature futura introduce ronda.
- **`PlayerSpawnPad`** ocasionalmente spawn dentro del terreno al crear isla nueva (bug intermitente).

### 7.5 Reglas de oro Verse

1. **JSON-first siempre**: si una constante puede variar entre mapas, NUNCA hardcodear en Verse.
2. **Failure handling explícito**: tratar `decides` failures con `if`/`else`.
3. **Async correcto**: usar `spawn{}` para fire-and-forget; `await` para secuencial.
4. **Logger con prefix**: incluir módulo origen en cada log.
5. **Validación defensiva al cargar persistencia**: corregir valores imposibles (gold negativo, gemas > cap razonable).
6. **No hot-reload**: cualquier cambio Verse requiere Push Changes.
7. **Test en sesión live antes de publish**: el publish es lento y los rollback son dolorosos.
8. **Mobile Preview en cada feature visual**: lo que se ve bien en PC puede tener problemas en móvil.

---

## 8. Mapping Python ↔ Verse por sistema

> **⭐ Para cada SYS-xxx del catálogo, qué hace Python (build-time) y qué hace Verse (runtime).**
> Esta tabla evita que la IA dude sobre dónde implementar cada cosa.

### 8.1 Convenciones del mapping

- **🐍 Python**: build-time. Genera, valida, configura, escribe archivos.
- **⚡ Verse**: runtime. Ejecuta lógica de gameplay.
- **📋 JSON**: data layer. Editado por humanos.
- **🎨 Manual**: requiere intervención artística humana en UEFN editor.

### 8.2 Mapping completo

| Sistema | 🐍 Python (build) | ⚡ Verse (runtime) | 📋 JSON | 🎨 Manual |
|---|---|---|---|---|
| **SYS-001 PlayerStats** | Genera constantes (max HP, stats base) → `Generated/PlayerConstants.verse` | Lógica completa: HP, stamina, regen, daño, persistencia | `data/progression/player_stats_base.json` | — |
| **SYS-002 Inventory** | Genera definiciones de slots, categorías, stack sizes | Lógica de slots, drag&drop, persistencia | `data/items/*.json` | — |
| **SYS-003 Resource Gathering** | Genera tabla de recursos, drop rates, tools | Detectar interacción, dar drops, gestionar tool wear | `data/items/resources.json` | Colocar resource nodes en zonas (asisitido por Python: SYS-007) |
| **SYS-004 Crafting** | Genera todas las recetas como constantes | Validar requisitos, ejecutar craft, gestionar timers | `data/items/recipes.json` | — |
| **SYS-005 Base Building** | Genera definiciones de piezas modulares + costes por tier | Lógica de placement, snap, upgrades | `data/base/building_pieces.json` | Configurar prefabs físicos de cada pieza (UEFN editor) |
| **SYS-006 Combat** | Genera tablas de daño, fórmulas, modifiers | Damage calculator, hit detection, ability execution | `data/combat/damage_formulas.json` | Animaciones, VFX (UEFN) |
| **SYS-007 Zone Unlock** | **Genera el layout procedural de cada zona, distribuye resource nodes, populates con HISM**, exporta gates a Verse | Detectar pago/boss + hacer unlock, gestionar UI | `data/zones/zone_definitions.json`, `data/zones/unlock_gates.json` | Decoración fina, iluminación artística por zona |
| **SYS-008 Day/Night + Weather** | Genera ciclos y eventos asociados | Reloj interno, cambio de skybox, spawns nocturnos | `data/world/day_night_cycle.json` | Skybox, post-process volumes |
| **SYS-009 Death Penalty + Protection** | Genera config de penalty, precios protectores | Lógica al morir, aplicar/quitar protección | `data/economy/death_protection.json` | — |
| **SYS-010 Companion Core** | Genera todas las criaturas como constantes (300+ entradas) | Behavior, asignación, generación pasiva | `data/companions/companions_base.json`, `variants.json` | Importar meshes y rigs custom |
| **SYS-011 Rarity Tiers** | Genera enum de rarezas + colores + drop rates | Lógica de rareza en pulls, display | `data/companions/rarities.json` | — |
| **SYS-012 Variants** | Genera todas las variantes (Normal, Oro, Diamante, Arcoiris, Hacker, Lava…) | Aplicar multiplicadores, efectos visuales | `data/companions/variants.json` | Materiales/shaders por variante (UEFN) |
| **SYS-013 Evolution** | Genera curvas de evolution costs | Validar y ejecutar evolución | `data/companions/evolutions.json` | — |
| **SYS-014 Companion Behavior** | Genera tablas de behavior por tipo | NPC AI, follow, attack, gather | `data/companions/behaviors.json` | — |
| **SYS-015 Collection Dex** | Genera estructura de Dex con todas las entradas | UI, tracking, recompensas por completar | `data/companions/dex_rewards.json` | — |
| **SYS-016 XP & Levels** | Genera curva de XP por nivel | Ganancia XP, level up triggers | `data/progression/xp_curves.json` | — |
| **SYS-017 Skill Points** | Genera fórmula de skill points por nivel | Distribuir, aplicar | `data/progression/skill_points.json` | — |
| **SYS-018 Skill Trees** | **Genera estructura completa de los 5 trees con prerequisitos** | UI del tree, aplicar efectos | `data/progression/skill_trees.json` | — |
| **SYS-019 Active Abilities** | Genera definiciones de abilities | Cooldowns, ejecución, VFX triggers | `data/progression/abilities.json` | VFX (UEFN) |
| **SYS-020 Rebirth System** | Genera curva de requisitos + recompensas por rebirth count | Ejecutar rebirth, aplicar bonuses permanentes | `data/progression/rebirth_rewards.json` | — |
| **SYS-021 Achievements** | Genera lista de achievements con tracking criteria | Detectar criterios, otorgar | `data/progression/achievements.json` | — |
| **SYS-022 Battle Pass** | **Genera estructura completa de cada season** (100 niveles × free + premium tracks) | XP del BP, claim rewards, season management | `data/progression/battle_pass_seasons/season_XX.json` | — |
| **SYS-023 Equipment Slots** | Genera definiciones de 6 ranuras | Equip/unequip, validation | `data/items/equipment_slots.json` | — |
| **SYS-024 Equipment Stats** | Genera todos los items posibles con sus stats por rareza | Calcular stats efectivas, aplicar al jugador | `data/items/equipment.json` | — |
| **SYS-025 Equipment Leveling** | Genera fail-rates por tier | Roll de éxito/fallo, aplicar | `data/items/equipment_leveling.json` | — |
| **SYS-026 Protectors** | Genera definiciones y precios | Aplicar al fallo, consumir | `data/items/protectors.json` | — |
| **SYS-027 Set Bonuses** | Genera definiciones de sets | Detectar sets equipados, aplicar bonus | `data/items/sets.json` | — |
| **SYS-028 Reroll Stats** | Genera curva de coste exponencial por reroll | Ejecutar reroll, cobrar | `data/items/reroll.json` | — |
| **SYS-029 Gold** | Genera config inicial | Tracking, transacciones, persistencia | `data/economy/gold.json` | — |
| **SYS-030 Gems** | Genera config + ratios de generación | Tracking, transacciones, persistencia | `data/economy/gems.json` | — |
| **SYS-031 V-Bucks Integration** | Genera lista de entitlements esperadas | Detectar entitlements, otorgar items | `data/economy/vbucks_offers.json` | — |
| **SYS-032 Shop System** | **Genera todos los items del shop con todos sus precios** | UI del shop, validar y ejecutar compras | `data/economy/shop.json` | — |
| **SYS-033 Rotating Session Shop** | Genera tabla de rotación A/B + horarios | Sincronizar UTC, swap a HH:00 y HH:30 | `data/economy/shop_rotations.json` | — |
| **SYS-034 Lootboxes (Almas)** | Genera todas las almas con drop rates | Pull logic, distribución por rareza | `data/items/lootboxes.json` | — |
| **SYS-035 Pity System** | Genera config de pity por (alma, rareza) | Counter por jugador, garantías | `data/economy/pity_config.json` | — |
| **SYS-036 Trading Same-Session** | Genera flags de tradabilidad por item | UI de trade, lock 5s, double confirm, persistir histórico | (flags en JSONs de items) | — |
| **SYS-037 Auction Same-Session** | Genera config NPC vendor | Listings, compras, comisión | `data/economy/auction_config.json` | Modelo del NPC vendor |
| **SYS-038 Universal Obtainability Flag** | **Validador**: cada item declara TODAS sus fuentes correctamente | Verificar fuentes en runtime al otorgar | (flags en cada JSON de item) | — |
| **SYS-039 Quest System** | **Genera todas las quests** (tutorial + daily pool + weekly pool + story) | Engine de quests, tracking, claim rewards | `data/quests/*.json` | — |
| **SYS-040 Daily Login** | Genera calendario 28 días | Streak tracking, rescue logic | `data/progression/daily_login.json` | — |
| **SYS-041 Time Played Rewards** | Genera tabla de recompensas por tiempo | Tracking de session time, otorgar | `data/progression/time_played.json` | — |
| **SYS-042 Hourly Boss Event** | Genera config de requisitos + recompensas | Sincronización UTC, ventana 2 min, teleport masivo, fight | `data/events/hourly_boss.json` | Arena del boss (UEFN) |
| **SYS-043 Long Events** | Genera plantilla de evento largo | Activar/desactivar, contenido específico | `data/events/seasonal_events.json` | Contenido específico |
| **SYS-044 Short Events / Admin Abuse** | Genera comandos disponibles | Panel admin restringido por player ID, ejecutar comandos | `data/events/admin_commands.json` | — |
| **SYS-045 Code Redemption** | **Genera el pre-pool de N códigos** + sistema de activación | Validar código, otorgar recompensas, persistir redenciones | `data/events/codes_pool.json` | Activación manual de códigos por admin in-game |
| **SYS-046 Seasonal Content Framework** | **Genera season pack completo con un comando** (theme swap masivo) | Cargar season actual, aplicar | `data/seasons/season_XX.json` | Asset variants por season (Python ayuda con bulk swap) |
| **SYS-047 Leaderboards** | Genera config de stats trackeadas | `leaderboard_device` UI + sync vía Verse Persistence (campo `LeaderboardScore`) | `data/social/leaderboards.json` | PlayerProgress (LeaderboardScore_*) |
| **SYS-048 Social Display** | Genera definiciones de cosméticos sociales | Mostrar pet/aura/título en sesión | `data/social/displays.json` | Modelos/VFX (UEFN) |
| **SYS-049 Activity Log UI** | Genera config de categorías + colores | UI completa, fading, accumulation | `data/ui/activity_log.json` | — |
| **SYS-050 Notifications System** | Genera pool de devices a reusar | Queue, prioridades, cooldowns | `data/ui/notifications.json` | — |
| **SYS-051 Auto-Sell Filters** | Genera config de filtros disponibles | UI de filtros, ejecutar auto-sell | `data/ui/auto_sell_config.json` | — |
| **SYS-052 Pre-Inventory Filter** | Genera config | Aplicar filtro antes de añadir al inventario | `data/ui/pre_inventory_filter.json` | — |
| **SYS-053 Visual Compare** | — | Calcular deltas, mostrar UI | — | — |
| **SYS-054 Idle Summary** | — | Calcular producción offline + crafteos completados | — | — |
| **SYS-055 Search/Filter** | — | UI de búsqueda en inventario y Dex | — | — |
| **SYS-056 Hotkeys / Radial Menu** | Genera config de hotkeys | UI radial móvil + key bindings | `data/ui/hotkeys.json` | — |
| **SYS-057 Error Handling UI** | Genera mensajes de error localizables | Mostrar mensajes en context | `data/ui/error_messages.json` | — |
| **SYS-058 Rate Limiting** | Genera cooldowns por acción | Aplicar cooldowns en runtime | `data/ui/rate_limits.json` | — |
| **SYS-059 Base Level** | Genera curva de XP de base + gates por nivel | Tracking, level up triggers, gating | `data/base/base_levels.json` | — |
| **SYS-060 Base Upgrades** | **Genera todos los upgrades** posibles (categorías, tiers, costes, efectos) | UI, validar requisitos, aplicar efectos | `data/base/base_upgrades.json` | — |
| **SYS-061 Passive Generators** | Genera definiciones de generadores | Tick rate de generación, capping | `data/base/generators.json` | — |
| **SYS-062 Offline Production** | Genera caps + eficiencias por upgrade | Cálculo al login: delta × rate × eff capeado | `data/base/offline_config.json` | — |
| **SYS-063 Crafting Timers** | Genera tiempos por receta | Persistencia de timers, completion al volver | `data/items/crafting_timers.json` | — |
| **SYS-064 First Minute Hook** | Genera config del spawn inicial | Trigger del visual + acción | `data/onboarding/first_minute.json` | Visual de hook (boss lejano, ayudante Mythic flotando, etc.) |
| **SYS-065 Tutorial Chain** | Genera las 15 quests del tutorial | Engine de quests aplicado al chain | `data/quests/tutorial_chain.json` | — |
| **SYS-066 Contextual Tutorials** | Genera triggers + contenido | Mostrar tutorial al desbloquear feature | `data/onboarding/contextual_tutorials.json` | — |
| **SYS-067 BigNumbers Integration** | Wrap de la lib comunidad como módulo Verse | Aritmética grande, formatting | — | — |
| **SYS-068 Time Sync (UTC)** | — | `GetSimulationElapsedTime()` + cálculo de epoch | — | — |
| **SYS-069 Persistence Layer** | **Validador de schema** + generador de migration helpers | 4 weak_maps + load/save + validación defensiva | (schemas en código Verse) | — |
| **SYS-070 Admin Panel** | Genera lista de admin IDs y comandos | UI restringida + ejecutor de comandos | `data/admin/admin_config.json` | — |
| **SYS-071 Test/QA Framework** | **Genera utilidades de test + scaffolding de tests** | Flags admin para skip tutorial, dar gemas, spawn | `data/admin/test_flags.json` | — |
| **SYS-072 Module Registry** | — | Singleton top-level. Lookup runtime para Systems gameplay (no orquesta Core). | — | — |

### 8.3 Reglas de decisión rápida

Cuando dudes dónde implementar algo:

- **¿Es contenido (criatura, item, quest, precio)?** → JSON. Generated → Verse via Python.
- **¿Es lógica que reacciona a un evento de jugador?** → Verse.
- **¿Es validar/generar/exportar archivos?** → Python.
- **¿Es algo visual artístico irrepetible?** → Manual en UEFN.
- **¿Va a variar entre mapas?** → JSON, jamás Verse hardcoded.
- **¿Va a verse en runtime por el jugador?** → Verse o asset (UEFN).

---

## 9. Pipeline de build completo

> **El flujo completo desde "edito un JSON" hasta "el cambio está en el mapa".**

### 9.1 Pipeline canónico (orden de ejecución)

```
[1] DESARROLLADOR / IA
    edita data/*.json
         │
         ▼
[2] PYTHON: 01_validate_jsons.py
    valida formato, schemas, referencias
    ✓ pasa → continuar
    ✗ falla → reportar errores y stop
         │
         ▼
[3] PYTHON: 02_export_constants_to_verse.py
    genera Content/Verse/Generated/*.verse
    con todas las constantes derivadas de JSONs
         │
         ▼
[4] PYTHON: 03_generate_companion_prefabs.py
    crea/actualiza prefabs Scene Graph para
    cada companion definido
         │
         ▼
[5] PYTHON: 04_generate_zone_layouts.py
    para cada zona en zone_definitions.json:
    - distribuye resource nodes (Poisson-disk)
    - coloca props con HISM
    - configura volumes, triggers
         │
         ▼
[6] PYTHON: 05_apply_theme_pack.py
    si theme_config.json cambió:
    - bulk swap de meshes
    - bulk swap de materiales
    - regenerar Material Instances
         │
         ▼
[7] PYTHON: 06_check_memory_budget.py
    valida que el mapa cabe en presupuesto
    de memoria UEFN
    ⚠ si pasa de threshold, warning
         │
         ▼
[8] DESARROLLADOR / IA
    en UEFN: Build Verse Code (Ctrl+Shift+B)
         │
         ▼
[9] DESARROLLADOR / IA
    en UEFN: Push Changes
         │
         ▼
[10] DESARROLLADOR / IA
     en sesión live: testear in-session
     + Mobile Preview
         │
         ▼
[11] (si todo OK) Publish a Creator Portal
```

### 9.2 Script orquestador

Existe `scripts/build/07_run_full_pipeline.py` que ejecuta los pasos 2–7 en secuencia, con manejo de errores y rollback en caso de fallo. **Por defecto, este es el script que se ejecuta**, no los individuales.

### 9.3 Atajos clave

| Tarea | Comando |
|---|---|
| Validar JSONs | `python scripts/build/01_validate_jsons.py` |
| Pipeline completo | UEFN > Tools > Execute Python Script > `07_run_full_pipeline.py` |
| Cambiar theme entero | Editar `data/theme/theme_config.json` + ejecutar pipeline |
| Añadir nueva criatura | Editar `data/companions/companions_base.json` + pipeline |
| Nuevo mapa desde scratch | `python scripts/tools/new_map_scaffolder.py --name=NewMapName` |

### 9.4 Garantías del pipeline

1. **Idempotente**: ejecutar N veces da el mismo resultado.
2. **Reversible**: usa `unreal.ScopedEditorTransaction` → permite Ctrl+Z al user.
3. **Verboso**: logging detallado en cada paso.
4. **Fail-safe**: si un paso falla, no se ejecuta el siguiente.
5. **Reportable**: genera `build_report.md` al final con tiempos y warnings.

### 9.5 Lo que el pipeline NO hace (intervención humana requerida)

- ❌ Importar meshes custom de Blender por primera vez (FBX inicial)
- ❌ Iluminación artística fina
- ❌ Audio mixing
- ❌ Decoración estética del hub central
- ❌ Compilar Verse (lo hace UEFN)
- ❌ Push Changes (lo hace el desarrollador)
- ❌ Publish (lo hace el desarrollador)

**Estos son los pasos del 10–20% manual restante** mencionado en sección 4.

---

## 10. Catálogo completo de sistemas

> Cada sistema marcado con su **ID único** (`SYS-xxx`) para referenciar en sprints.

### 6.1 Core gameplay

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-001 | **Player Stats** | HP, stamina, fuerza, velocidad, inteligencia, suerte. Persistente. |
| SYS-002 | **Inventory** | Slots con expansión por upgrades. Categorías: recursos, equipo, ayudantes, consumibles, evento. Stack inteligente, drag & drop. |
| SYS-003 | **Resource Gathering** | Chop, mine, harvest. Tools que mejoran. |
| SYS-004 | **Crafting** | Recetas data-driven. |
| SYS-005 | **Base Building** | Piezas modulares por tier. Persistente. **Sobrevive al rebirth.** |
| SYS-006 | **Combat** | Melee, ranged, habilidades activas. |
| SYS-007 | **Zone Unlock** | Algunas por recursos, otras por boss + recursos. Gate basado en base level. |
| SYS-008 | **Day/Night + Weather** | Afecta a recursos y spawns. |
| SYS-009 | **Death Penalty + Protection** | % XP + % gold no depositado. Protector temporal/permanente comprable/ganable. |

### 6.2 Ayudantes (Companion System)

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-010 | **Companion Core** | Clase base. Stats + bonus que dan al jugador. Asignables a tareas. |
| SYS-011 | **Rarity Tiers** | Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Admin. |
| SYS-012 | **Variants** | Normal, Oro, Diamante, Arcoiris + variantes de evento (Hacker, Lava…). Cada una multiplicador y efecto único. |
| SYS-013 | **Evolution** | Subir tier con recursos. |
| SYS-014 | **Companion Behavior** | Generación de recursos pasiva, asignación a tareas, sigue al jugador. |
| SYS-015 | **Collection Dex** | 300+ entradas con silueta/ficha. Recompensas por completar. Visible socialmente. |

### 6.3 Progresión

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-016 | **XP & Levels** | Sube por jugar (farmeo, kills, quests, descubrimientos). |
| SYS-017 | **Skill Points** | Cada nivel da puntos para distribuir en 5 ramas. |
| SYS-018 | **Skill Trees** | Combate, Recolección, Supervivencia, Coleccionista, Economía. |
| SYS-019 | **Active Abilities** | Desbloqueables progresivamente por zonas (sprint, dash, special attacks). |
| SYS-020 | **Rebirth System** | Reset de progreso normal + recompensas permanentes. Primer rebirth gateado por quests. |
| SYS-021 | **Achievements** | Permanentes, hitos del juego. |
| SYS-022 | **Battle Pass** | Free + Premium track. XP separada del nivel jugador. 100% configurable JSON. |

### 6.4 Equipamiento

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-023 | **Equipment Slots** | 6 ranuras de equipo invisible (anillo, amuleto, pulsera, talismán...). |
| SYS-024 | **Equipment Stats** | Stats + skills desbloqueables por nivel/rareza. |
| SYS-025 | **Equipment Leveling** | Tiers 1–10 con fail-rate progresivo. |
| SYS-026 | **Protectors** | Bronce, Plata, Oro, Diamante. Cosumibles o permanentes. |
| SYS-027 | **Set Bonuses** | Llevar N piezas del mismo set = bonus. |
| SYS-028 | **Reroll Stats** | Coste escalable por reroll previo (curva exponencial). |

### 6.5 Economía

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-029 | **Gold (currency in-game)** | Recursos básicos. |
| SYS-030 | **Gems (currency premium-jugable)** | Difícil ganar, alternativa a V-Bucks. |
| SYS-031 | **V-Bucks Integration** | In-Island Transactions (entitlements). |
| SYS-032 | **Shop System** | Compras con gemas/V-Bucks. Vender items propios. |
| SYS-033 | **Rotating Session Shop** | Contenido A → HH:00, Contenido B → HH:30. Sincronizado UTC. |
| SYS-034 | **Lootboxes (Almas de Invocación)** | Solo gemas. Drop rates visibles. Pity por (alma_type, rarity_target). |
| SYS-035 | **Pity System** | Configurable por JSON: cada alma + cada rareza tiene su counter independiente. |
| SYS-036 | **Trading Same-Session** | Trade directo player-to-player con safeguards (lock 5s, double confirm). |
| SYS-037 | **Auction Same-Session** | NPC vendor con consignación. |
| SYS-038 | **Universal Obtainability Flag** | Cada item JSON declara TODAS sus fuentes (shop, lootbox, boss, event, BP, daily). |

### 6.6 Live Ops

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-039 | **Quest System** | Tutorial chain, daily, weekly, story, achievement, event. JSON-driven. |
| SYS-040 | **Daily Login** | Calendario 28 días con streak. Reset UTC. Rescue con gemas opcional. |
| SYS-041 | **Time Played Rewards** | Micro-recompensas cada 15/30/60 min de sesión. Reset diario. |
| SYS-042 | **Hourly Boss Event** | Cada HH:00, ventana 2 min, portal teleporta a arena cooperativa. Requisitos configurables. |
| SYS-043 | **Long Events** | Semanas/temporada. Boss world unique, zonas temporales, ayudantes exclusivos. |
| SYS-044 | **Short Events / Admin Abuse** | Panel admin (UI restringida por player ID). Spawn masivo, drop boost, boss invocable. |
| SYS-045 | **Code Redemption** | Pre-pool de códigos compilados. Tipos: público / único / limitado / por tiempo. |
| SYS-046 | **Seasonal Content Framework** | Re-skin del hub, eventos exclusivos, ayudantes limitados, BP nuevo. |

### 6.7 Social

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-047 | **Leaderboards** | UI vía `leaderboard_device`, datos vía Verse Persistence (`LeaderboardScore` en PlayerProgress). Cross-session aproximado: no hay API para jugadores fuera de sesión, se cachea best-score por jugador y se reconstruye ranking. |
| SYS-048 | **Social Display** | Pet siguiéndote / cosmético visible que muestra rebirth count, Dex %, título. |
| SYS-049 | **Activity Log UI** | 4 líneas en esquina, auto-fade configurable, colores por categoría, sin click action. |
| SYS-050 | **Notifications System** | Toast events, sound cues, animation. Reusa pool de hud_message_devices. |

### 6.8 Calidad de vida

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-051 | **Auto-Sell Filters** | Por rareza + por tipo + whitelist de protegidos. |
| SYS-052 | **Pre-Inventory Filter** | Vender antes de entrar al inventario. |
| SYS-053 | **Visual Compare** | "+10% atk / -5% spd" comparado con item actual. |
| SYS-054 | **Idle Summary** | Pantalla al entrar con producción offline + crafteos completados. |
| SYS-055 | **Search/Filter** | Inventario y Dex con filtros (rareza, tipo, missing-only, nombre). |
| SYS-056 | **Hotkeys / Radial Menu** | Acceso rápido a inventario, Dex, quests, shop. Móvil radial. |
| SYS-057 | **Error Handling UI** | Mensajes claros (sin gemas, item no existe...). Nunca silencio. |
| SYS-058 | **Rate Limiting** | Cooldowns en botones críticos (anti-spam-click). |

### 6.9 Base persistente

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-059 | **Base Level** | Eje global de progreso. Gate de zonas, quests, boss event. **Nunca se resetea.** |
| SYS-060 | **Base Upgrades** | Categorías: logística, pasivas, generadores, defensivas, estéticas. JSON configurable. |
| SYS-061 | **Passive Generators** | Producen recursos/gold/gemas (ratio bajo). Cap configurable por upgrades. |
| SYS-062 | **Offline Production** | Rate × tiempo capeado × eficiencia. Cap y eficiencia escalables por upgrades. |
| SYS-063 | **Crafting Timers** | Tiempo real corre 100% offline (NO se capea). Forja, alquimia, eclosión. |

### 6.10 Onboarding

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-064 | **First Minute Hook** | Spawn con visual impactante + acción interactiva en <10 seg + recompensa instantánea. |
| SYS-065 | **Tutorial Chain** | 15 quests forzadas que enseñan cada mecánica. Termina con primer rebirth. |
| SYS-066 | **Contextual Tutorials** | Mini-tutoriales al desbloquear features (auction, lootbox, trade). |

### 6.11 Sistemas técnicos transversales

| ID | Sistema | Descripción breve |
|---|---|---|
| SYS-067 | **BigNumbers Integration** | Lib comunidad para idle/tycoon (sextillones, notación científica). |
| SYS-068 | **Time Sync (UTC)** | Eventos sincronizados servidor (no cliente). Source of truth = `GetSimulationElapsedTime()`. |
| SYS-069 | **Persistence Layer** | 4 weak_maps distribuidos. Validación defensiva. Solo añadir campos opcionales con defaults. |
| SYS-070 | **Admin Panel** | UI restringida por player ID. Comandos de evento, spawning, drop boost. |
| SYS-071 | **Test/QA Framework** | Cuentas test con flags admin para saltar tutorial, dar gemas, spawnear. |
| SYS-072 | **Module Registry** | Servicio de lookup runtime para Systems gameplay (Capa 2+). NO orquesta los Core (son singletons top-level que Verse inicializa solos). Resuelve ciclos de import compile-time entre Systems. Detalle: `MODULES_DEPENDENCY_GRAPH.md` §4.7. |

**TOTAL: 72 sistemas identificados.**

---

## 11. Estructura de carpetas y archivos

### 11.1 Layout del proyecto UEFN

```
ProjectRoot/
├── Content/
│   ├── Assets/
│   │   ├── Meshes/         (.fbx custom)
│   │   ├── Textures/       (≤512×512, potencias de 2)
│   │   ├── Audio/
│   │   ├── Materials/
│   │   └── ScenegraphPrefabs/
│   ├── Maps/
│   │   └── Main.umap
│   └── Verse/
│       └── (ver sección 11.2)
│
├── Plugins/
│
├── data/                   ← JSONs editables
│   ├── companions/
│   │   ├── companions_base.json
│   │   ├── variants.json
│   │   └── evolutions.json
│   ├── items/
│   │   ├── resources.json
│   │   ├── consumables.json
│   │   ├── equipment.json
│   │   └── lootboxes.json
│   ├── quests/
│   │   ├── tutorial_chain.json
│   │   ├── daily_pool.json
│   │   ├── weekly_pool.json
│   │   └── achievements.json
│   ├── progression/
│   │   ├── skill_trees.json
│   │   ├── rebirth_rewards.json
│   │   └── battle_pass_seasons/
│   │       └── season_01.json
│   ├── economy/
│   │   ├── prices.json
│   │   ├── shop_rotations.json
│   │   ├── pity_config.json
│   │   └── currency_caps.json
│   ├── zones/
│   │   ├── zone_definitions.json
│   │   └── unlock_gates.json
│   ├── base/
│   │   ├── base_upgrades.json
│   │   └── base_levels.json
│   ├── events/
│   │   ├── hourly_boss.json
│   │   ├── seasonal_events.json
│   │   └── codes_pool.json
│   └── theme/
│       ├── theme_config.json   ← THE switch para cambiar el mapa entero
│       └── localization_keys.json
│
├── scripts/                ← Python scripts
│   ├── init_unreal.py     (auto-load al abrir UEFN)
│   ├── build/
│   │   ├── 01_validate_jsons.py
│   │   ├── 02_export_constants_to_verse.py
│   │   ├── 03_generate_companion_prefabs.py
│   │   ├── 04_generate_zone_layouts.py
│   │   ├── 05_apply_theme_pack.py
│   │   ├── 06_check_memory_budget.py
│   │   └── 07_run_full_pipeline.py
│   ├── tools/
│   │   ├── balance_curve_visualizer.py
│   │   ├── new_map_scaffolder.py
│   │   └── localization_exporter.py
│   └── utils/
│       └── unreal_helpers.py
│
├── docs/                  ← documentación markdown
│   ├── CONCEPT.md          ← este documento
│   ├── PROMPT.md           ← prompt agnóstico de modelo
│   ├── SYSTEMS_INDEX.md    ⭐ catálogo autoritativo de los 72 SYS-xxx
│   ├── SPRINTS_BACKLOG.md  ⭐ 203 sprints con dependencias (sustituye al fantasma `SPRINTS.md`)
│   ├── FOLDER_STRUCTURE_TRUTH.md ⭐ árbol único de carpetas
│   ├── MODULES_DEPENDENCY_GRAPH.md ⭐ deps Verse (sustituye al fantasma `ARCHITECTURE.md`)
│   ├── PERSISTENCE_MAP.md
│   ├── JSON_SCHEMAS.md
│   ├── BALANCE_FORMULAS.md
│   ├── BOOTSTRAP_PIPELINE.md
│   ├── API_REFERENCE_GENERATED.md
│   ├── WORKFLOW.md
│   ├── PROMPT_TEMPLATES.md
│   ├── DEEPSEEK_CAPSULE.md
│   ├── UI_UX_STYLE_GUIDE.md
│   ├── TESTING_PROTOCOL.md
│   ├── EMERGENCY_ROLLBACK.md
│   ├── GLOSSARY.md         ← OJO: SCREAMING_SNAKE en disco (Linux es case-sensitive)
│   ├── CHANGELOG.md
│   ├── DAILY_LOG.md
│   └── POSTMORTEMS_INDEX.md
│
└── README.md               ← top-level, apunta a docs/
```

> ⚠️ **Para listado canónico de carpetas y archivos del proyecto entero, ver `FOLDER_STRUCTURE_TRUTH.md`.** Ese doc es el autoritativo. Esta vista en §11.1 es resumida y puede quedar desactualizada.

### 11.2 Layout de carpeta Verse

```
Content/Verse/
├── Core/                       ← módulos transversales
│   ├── ModuleRegistry.verse
│   ├── PersistenceLayer.verse
│   ├── TimeSync.verse
│   ├── BigNumbers.verse        (lib externa wrapped)
│   ├── Logger.verse
│   ├── EventBus.verse          (pub-sub interno)
│   └── AdminCommands.verse
│
├── Generated/                  ← OUTPUT de Python, NO editar manualmente
│   ├── Companions_Generated.verse
│   ├── Items_Generated.verse
│   ├── Prices_Generated.verse
│   ├── Quests_Generated.verse
│   └── ThemeConstants_Generated.verse
│
├── Systems/
│   ├── Player/
│   │   ├── PlayerStats.verse
│   │   ├── PlayerInventory.verse
│   │   ├── PlayerProgression.verse
│   │   ├── PlayerSkillTree.verse
│   │   ├── PlayerRebirth.verse
│   │   └── PlayerDeathHandler.verse
│   ├── Companions/
│   │   ├── CompanionCore.verse
│   │   ├── CompanionBehavior.verse
│   │   ├── CompanionAssignment.verse
│   │   └── CollectionDex.verse
│   ├── Combat/
│   │   ├── CombatCore.verse
│   │   ├── DamageCalculator.verse
│   │   └── AbilityExecutor.verse
│   ├── Economy/
│   │   ├── CurrencyManager.verse
│   │   ├── ShopSystem.verse
│   │   ├── RotatingShop.verse
│   │   ├── PurchaseService.verse  (abstrae gems/vbucks/in-game)
│   │   ├── LootboxSystem.verse
│   │   ├── PitySystem.verse
│   │   ├── TradeSystem.verse
│   │   └── AuctionSystem.verse
│   ├── Equipment/
│   │   ├── EquipmentSlots.verse
│   │   ├── EquipmentLeveling.verse
│   │   ├── ProtectorService.verse
│   │   ├── SetBonuses.verse
│   │   └── RerollService.verse
│   ├── Quests/
│   │   ├── QuestEngine.verse
│   │   ├── DailyQuestRotator.verse
│   │   ├── WeeklyQuestRotator.verse
│   │   └── TutorialChain.verse
│   ├── Base/
│   │   ├── BaseLevelManager.verse
│   │   ├── BaseUpgrades.verse
│   │   ├── PassiveGenerators.verse
│   │   ├── OfflineCalculator.verse
│   │   └── CraftingTimers.verse
│   ├── World/
│   │   ├── ZoneManager.verse
│   │   ├── ResourceNodes.verse
│   │   ├── BossEncounters.verse
│   │   └── HourlyBossPortal.verse
│   ├── LiveOps/
│   │   ├── EventManager.verse
│   │   ├── DailyLoginRewards.verse
│   │   ├── TimePlayedRewards.verse
│   │   ├── BattlePass.verse
│   │   ├── CodeRedemption.verse
│   │   └── SeasonManager.verse
│   ├── Social/
│   │   ├── LeaderboardSync.verse
│   │   ├── SocialDisplay.verse
│   │   └── ActivityLogUI.verse
│   └── UI/
│       ├── HUDController.verse
│       ├── NotificationPool.verse
│       ├── InventoryUI.verse
│       ├── DexUI.verse
│       ├── ShopUI.verse
│       ├── BasePanelUI.verse
│       └── IdleSummaryUI.verse
│
└── Devices/                    ← Verse devices instanciables en UEFN editor
    ├── GameManager.verse       (root device, entry point: orquesta Init de Systems en OnBegin)
    ├── ZonePortal.verse
    ├── HourlyBossTrigger.verse
    ├── BasePlot.verse
    └── AdminPanel.verse
```

### 11.3 Naming conventions

- **Módulos Verse**: `PascalCase` para clases y archivos. Ej: `PlayerStats.verse`, `CompanionCore.verse`.
- **Archivos generados**: sufijo `_Generated.verse`. Nunca editar manualmente.
- **JSONs**: `snake_case`. Ej: `companions_base.json`.
- **IDs internos**: `snake_case`. Ej: `companion_dragon_fire_01`, `quest_tutorial_07`.
- **Sistemas (referencia documental)**: `SYS-xxx`.
- **Sprints (referencia documental)**: `SPR-xxx`.

---

## 12. Plan por fases (roadmap)

### 12.1 Filosofía del roadmap

- **Cada fase es un mapa publicable**. No hay que tener todo antes de lanzar.
- **Lanzar Fase 1 → ganar datos reales → ajustar → sumar Fase 2**.
- Los whales y la retención de largo plazo llegan en Fase 4–5.
- **Cada sistema se diseña pensando en encajar con los siguientes**, aunque no esté implementado aún.

### 12.2 Fases y alcance

| Fase | Nombre | Sistemas incluidos | Objetivo |
|---|---|---|---|
| **F0** | **Foundation** | SYS-067, 068, 069, 070, 071, 072 + scaffolding | Motor base, persistencia, time sync, admin panel, registry. Sin gameplay aún. |
| **F1** | **MVP playable** | SYS-001 a SYS-009 + SYS-016, 017, 020 + SYS-039 (parcial) + SYS-064, 065 | Loop core: farmear, construir, combatir, subir nivel, primer rebirth, tutorial. **Publicable.** |
| **F2** | **Companions & Collection** | SYS-010 a SYS-015 + SYS-018, 019 + SYS-021 + SYS-049, 050 | Ayudantes, Dex, skill trees, achievements, notif log. Profundidad core. |
| **F3** | **Economy & Equipment** | SYS-022 a SYS-038 + SYS-051 a SYS-058 | Battle Pass, equipo, shop, lootboxes, pity, trade, auction, todos los QoL. |
| **F4** | **Base persistente & Live Ops básicas** | SYS-040 a SYS-046 + SYS-059 a SYS-063 + SYS-066 | Daily login, time played, base, generadores offline, eventos, códigos, seasonal. |
| **F5** | **Hourly Boss + Social + Polish** | SYS-042, SYS-047, SYS-048 + polish global + segundo mapa con la máquina | Endgame, social display, leaderboards globales, optimización móvil deep. |

### 12.3 Tiempo estimado

| Fase | Tiempo estimado (horas-trabajo) | Sprints aprox. (1.5h) |
|---|---|---|
| F0 | 15 h | 10 |
| F1 | 60 h | 40 |
| F2 | 50 h | 33 |
| F3 | 80 h | 53 |
| F4 | 60 h | 40 |
| F5 | 40 h | 27 |
| **TOTAL** | **305 h** | **~203 sprints** |

> Estimaciones honestas, asumen que hay un humano + IA trabajando juntos. Pueden variar mucho según dominio del programador con Verse y agilidad de la IA.

---

## 13. Backlog de sprints (1–2 h cada uno)

### 13.1 Filosofía del backlog

- **Cada sprint cabe en 1–2 horas reales de trabajo**.
- **Cada sprint produce algo testeable o documentado**, no código a medias.
- **Tokens limitados**: cada sprint se diseña para que la IA pueda procesar **un solo sprint en una sesión**, sin necesitar contexto masivo de otros archivos.
- **Cada sprint tiene un ID `SPR-xxx`**, **dependencias** explícitas, **archivos a tocar**, y **criterio de done**.

### 13.2 Plantilla de sprint

```markdown
### SPR-XXX — Título del sprint

- **Fase**: F0 / F1 / ... / F5
- **Sistema(s)**: SYS-xxx, SYS-yyy
- **Dependencias**: SPR-aaa, SPR-bbb (deben estar terminados)
- **Tipo**: design / verse / python / json / asset / docs
- **Tiempo estimado**: 1h / 1.5h / 2h
- **Archivos a crear/modificar**:
  - `Content/Verse/Systems/Player/PlayerStats.verse` (crear)
  - `data/items/equipment.json` (modificar)
- **Contexto necesario** (para IA): qué archivos leer antes de empezar.
- **Done criteria**:
  - [ ] Compila sin warnings
  - [ ] Test in-session pasa
  - [ ] Persiste tras logout
- **Notas**: cualquier consideración especial.
```

### 13.3 Backlog Fase 0 — Foundation (10 sprints)

> **Decisión cerrada (Auditoría 2 — C1)**: los 6 Core son singletons top-level estáticos (no `creative_device`, no se auto-registran). Verse los inicializa antes de cualquier `OnBegin`. Por eso **SPR-006 desbloquea todo el resto de Core**, y SPR-005 (Registry) no es prerrequisito de los demás Core — solo sirve para Systems gameplay (Capa 2+) en F1+. Tras SPR-006, los sprints SPR-005/007/008/009 pueden paralelizarse. Detalle en `MODULES_DEPENDENCY_GRAPH.md` §2.1 + §4.7. Este orden de deps es **autoritativo en `SPRINTS_BACKLOG.md` §3** — si CONCEPT y SPRINTS_BACKLOG discrepan, gana SPRINTS_BACKLOG.

#### SPR-001 — Setup del repo y carpetas

- **Fase**: F0
- **Sistema(s)**: scaffolding
- **Dependencias**: ninguna
- **Tipo**: scaffolding
- **Tiempo**: 1h
- **Archivos**: estructura de carpetas según sección 11.
- **Done**:
  - [ ] Estructura `data/`, `scripts/`, `docs/`, `Content/Verse/` creada
  - [ ] `README.md` con quickstart
  - [ ] `.gitignore` para UEFN

#### SPR-002 — JSON schemas base

- **Fase**: F0
- **Sistema(s)**: data layer
- **Dependencias**: SPR-001
- **Tipo**: design + json
- **Tiempo**: 2h
- **Archivos**:
  - `data/companions/companions_base.json` (template vacío)
  - `data/items/equipment.json` (template vacío)
  - `data/quests/tutorial_chain.json` (template vacío)
  - `data/theme/theme_config.json` (con ejemplo)
- **Contexto necesario**: secciones 4 y 10 de CONCEPT.md
- **Done**:
  - [ ] Schemas tienen al menos 1 entry de ejemplo
  - [ ] Documentados en comentarios (`_comment` keys)

#### SPR-003 — Python: validador de JSONs

- **Fase**: F0
- **Sistema(s)**: build pipeline
- **Dependencias**: SPR-002
- **Tipo**: python
- **Tiempo**: 1.5h
- **Archivos**: `scripts/build/01_validate_jsons.py`
- **Done**:
  - [ ] Verifica formato JSON de todos los archivos en `data/`
  - [ ] Reporta errores con línea y archivo
  - [ ] Ejecutable desde terminal y desde UEFN

#### SPR-004 — Python: exporter a constantes Verse

- **Fase**: F0
- **Sistema(s)**: build pipeline
- **Dependencias**: SPR-002, SPR-003
- **Tipo**: python
- **Tiempo**: 3h
- **Archivos**: `scripts/build/02_export_constants_to_verse.py`
- **Done**:
  - [ ] Lee JSONs de `data/`
  - [ ] **Export de datos** (companions, items, prices, quests, theme): genera `Companions_Generated.verse`, `Items_Generated.verse`, `Prices_Generated.verse`, `Quests_Generated.verse`, `ThemeConstants_Generated.verse` en `Content/Verse/Generated/`
  - [ ] **Export de arquitectura — Registry** (`export_module_registry()`): lee `data/architecture/modules_manifest.json` y genera `Generated/ModuleRegistryConstants.verse` con getters tipados estáticos por sistema registrable. Plantilla en `BOOTSTRAP_PIPELINE.md` §10.5
  - [ ] **Export de arquitectura — EventBus** (`export_event_payloads()` + `export_event_bus()`): lee `data/architecture/events_catalog.json` y genera `Generated/EventPayloads_Generated.verse` (un struct por evento) + `Generated/EventBusConstants.verse` (singleton `EventBus` con propiedad `event(payload_t)` por evento). Plantilla en `BOOTSTRAP_PIPELINE.md` §11.6
  - [ ] Cada archivo generado incluye comentario warning "AUTO-GENERATED FILE. DO NOT EDIT MANUALLY." + ref al JSON fuente
  - [ ] Idempotente: re-ejecutar sin cambios en JSON no modifica los `.verse` (mismo hash)
  - [ ] CI rechaza merge si los `Generated/*` están desincronizados respecto al JSON (se cubre en SPR posterior — exporter debe exit 0/1 limpio)
- **Notas C1 + C3**: subió de 2h → 3h al absorber las 3 funciones export de arquitectura (Registry + EventBus). Rationale: alternativa era crear SPR-004b separado, pero los 3 transformers comparten infraestructura (path resolution, idempotencia, header generation) y conviene un único punto de entrada. Bloqueante para SPR-005 (Registry necesita su Generated) y SPR-009 (EventBus necesita los suyos).

> **⚠️ Sintaxis Verse (post-SPR-211)**: las menciones de "Singleton top-level (`X : x_module = x_module{}`)" en los sprints F0 abajo están **obsoletas para Cores sin state mutable**. Patrón vigente: `Module<public> := module:` namespace (sin class, sin archetype). SPR-006 (Logger) y SPR-007 (TimeSync) ya migrados. SPR-005 (Registry), SPR-008 (Persistence con weak_maps), SPR-009 (EventBus) y SPR-010 (Admin) son casos pendientes de re-evaluación — el patrón concreto debe validarse contra build UEFN real durante cada sprint. Autoridad sintáctica: `docs/VERSE_SYNTAX_GUIDE.md` §1+§2 + §2.4 (caso "Core con state mutable" = TBD).

#### SPR-005 — Verse: Module Registry

- **Fase**: F0
- **Sistema(s)**: SYS-072
- **Dependencias**: SPR-001, SPR-004, SPR-006
- **Tipo**: verse
- **Tiempo**: 1.5h
- **Archivos**:
  - `Content/Verse/Core/ModuleRegistry.verse` (source-controlled — declara el tipo `module_registry`)
  - `Content/Verse/Generated/ModuleRegistryConstants.verse` (**generado por SPR-004 ext** desde `data/architecture/modules_manifest.json` — contiene los getters tipados estáticos)
- **Done**:
  - [ ] Singleton top-level (`Registry : module_registry = module_registry{}`)
  - [ ] Getters tipados estáticos (no `<T>`) generados desde manifest — ver `MODULES_DEPENDENCY_GRAPH.md` §4.7
  - [ ] `RegisterPlayerStats(...)`, `GetPlayerStats():?player_stats_module` funcionan con módulo dummy de Systems
  - [ ] **Crítico**: Registry NO orquesta Core. Los Core son singletons top-level que Verse inicializa por sí mismo.
- **Notas C1 (Auditoría 2)**: depende de SPR-006 (Logger) porque Registry loguea sus operaciones, y de SPR-004 ext (que genera `ModuleRegistryConstants.verse`). Puede paralelizarse con SPR-007/008/009 una vez SPR-006 + SPR-004 estén done.

#### SPR-006 — Verse: Logger

- **Fase**: F0
- **Sistema(s)**: SYS-072 (logger)
- **Dependencias**: SPR-001
- **Tipo**: verse
- **Tiempo**: 1h
- **Archivos**: `Content/Verse/Core/Logger.verse`
- **Done**:
  - [x] Module namespace top-level: `Logger<public> := module:` (refactor SPR-211 — patrón legacy `class<concrete>` falla con err 3512)
  - [x] Niveles: Debug, Info, Warn, Error
  - [x] Logger sólo printea Debug si flag `DEBUG_ENABLED` está activa
  - [ ] Prefix con timestamp y módulo origen — **diferido** (requiere TimeSync, rompería Capa 0). Se hará en LoggerEnhanced o helper externo.
- **Notas C1 (Auditoría 2) + SPR-211**: Logger NO depende de Registry. Es Core module namespace — Verse lo inicializa antes de cualquier `OnBegin`. SPR-006 desbloquea SPR-005/007/008/009/010. Patrón canónico vigente en `VERSE_SYNTAX_GUIDE.md` §2.1.

#### SPR-007 — Verse: Time Sync (UTC)

- **Fase**: F0
- **Sistema(s)**: SYS-068
- **Dependencias**: SPR-006
- **Tipo**: verse
- **Tiempo**: 1.5h
- **Archivos**: `Content/Verse/Core/TimeSync.verse`
- **Done**:
  - [x] Module namespace top-level: `TimeSync<public> := module:` (refactor SPR-211 — class<concrete> falla con err 3512)
  - [x] `GetUTCNow()<decides>:int` devuelve simulation elapsed time como int (failable, llamada con `[]`)
  - [x] `GetSecondsUntilNextHour()<decides>:int` funciona
  - [x] `IsInWindow(StartEpoch, DurationSeconds)<decides>:void` funciona como predicado failable (lección 4 — condiciones-statement)
  - [ ] `GetSimulationStartTime()` para epoch UTC absoluto vía anchor diferido — pendiente cuando un consumidor lo necesite
- **Notas C1 + SPR-211**: paralelizable con SPR-005/008/009. Sin state mutable → namespace puro. Patrón canónico vigente en `VERSE_SYNTAX_GUIDE.md` §2.2.

#### SPR-008 — Verse: Persistence Layer

- **Fase**: F0
- **Sistema(s)**: SYS-069
- **Dependencias**: SPR-006
- **Tipo**: verse
- **Tiempo**: 2h
- **Archivos**:
  - `Content/Verse/Core/PersistenceLayer.verse`
  - 4 weak_maps definidos (PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy)
- **Done**:
  - [ ] Singleton top-level con 4 `weak_map` declarados a nivel módulo
  - [ ] Estructuras base con campos opcionales y defaults
  - [ ] 4 funciones individuales: `LoadPlayerCore/Inventory/Progress/Economy(player)` + 4 `SavePlayer<X>(player, data)` funcionan
  - [ ] Wrappers agregadores: `LoadPlayerData(player)` y `SavePlayerData(player)` invocan las 4 anteriores en secuencia (Auditoría 2 — M3)
  - [ ] Validación defensiva al cargar (incluso desde los wrappers)
  - [ ] Testeado entre sesiones
- **Notas C1 + M3**: paralelizable con SPR-005/007/009. Wrappers agregadores creados para DX (un único call desde `OnPlayerSpawn`) sin sacrificar las 4 funciones individuales para acceso lazy/selectivo. Detalle en `API_REFERENCE_GENERATED.md` §3.4.

#### SPR-009 — Verse: Event Bus interno

- **Fase**: F0
- **Sistema(s)**: SYS-072 (event bus)
- **Dependencias**: SPR-004, SPR-006
- **Tipo**: verse
- **Tiempo**: 1.5h estimado (~6h real con F-A rollback + F-B investigación H1-H5 + F-C refactor + F-C-3 tests)
- **Estado**: 🟢 done (cierre 2026-05-08, HEAD `6c90e45`)
- **Archivos**:
  - `Content/Verse/Core/EventBus.verse` (placeholder source-controlled — declara tipos auxiliares si se conserva, no contiene la instancia operativa)
  - `Content/Verse/Generated/EventBusDevice.verse` (**generado por SPR-004 ext** desde `events_catalog.json` — `event_bus_device := class<concrete>(creative_device)` con propiedad `event(payload_t)` por evento). NO singleton top-level — el device se instancia en Main.umap. Patrón H4 (post-F-C-2).
  - `Content/Verse/Generated/EventPayloads_Generated.verse` (**generado por SPR-004 ext** — un struct por evento)
  - `Content/Verse/Tests/test_event_bus_smoke.verse` (smoke test runtime — F-C-3a)
  - `scripts/build/tests/test_exporter_event_bus.py` + `scripts/build/tests/fixtures/event_bus_expected_contract.json` (golden contract Python — F-C-3b)
- **Done**:
  - [x] `Generated/EventBusDevice.verse` declara `event_bus_device<public> := class<concrete>(creative_device):` con una propiedad `<NombreEvento><public>:event(<nombre_evento>_payload) = event(<nombre_evento>_payload){}` por cada entrada de `data/architecture/events_catalog.json`
  - [x] La instancia operativa se coloca en Main.umap como actor del nivel; consumidores la referencian via `@editable Bus:event_bus_device = event_bus_device{}` (drag&drop en UEFN)
  - [x] `Generated/EventPayloads_Generated.verse` contiene un `struct` por cada evento del catálogo con campos planos tipados (no `any`)
  - [x] Patrón canónico funcional: `Bus.<Evento>.Signal(payload_struct)` (síncrono — handlers Await resumen dentro de Signal antes de retornar) y `Bus.<Evento>.Await()` (consumer suspende corutina hasta próximo Signal). **NO existe `.Subscribe(handler)` ni `.Unsubscribe(handler)`** en `event(t)` builtin Verse v1 (la primitiva implementa `signalable + awaitable` only, NO `subscribable`)
  - [x] Patrón consumer canónico: `spawn { ListenerFn() } ; Sleep(0.0)` post-spawn + `ListenerFn()<suspends>:void= loop { Payload := Bus.<Evento>.Await() ; <handler>(Payload) }`. `Sleep(0.0)` post-spawn es **obligatorio** para evitar race silenciosa Signal-antes-de-Await
  - [x] Type-safety compile-time verificada: cambiar un campo de un struct payload rompe compilación en todos los consumidores
  - [x] Sin strings, sin `Payload:any`, sin `Subscribe(EventName:string, ...)` — esas firmas están explícitamente prohibidas (ver `API_REFERENCE_GENERATED.md` §3.5)
  - [x] Smoke test runtime PASS in-session UEFN (test device `Tests/test_event_bus_smoke.verse`, 2026-05-08)
  - [x] Golden contract Python PASS — 5 tests cubren `02_export_constants_to_verse.py::export_event_bus()` (class declaration + count + contrato per-event + drift positivo + idempotencia)
- **Notas C1 + C3 + H4**: **C3 cerrado (Auditoría 2)**: payload type-safety resuelta con `event(payload_t)` nativo de Verse, no implementación custom. **H4 cerrado (SPR-009 F-C-2 post-investigación F-B)**: el patrón `event_bus_module := class<concrete>:` + singleton top-level (canonizado en BOOTSTRAP §11.5 v0 + API §3.5 v0) **NO compila** — `event(t){}` top-level falla con err 3512 (lección 16 VERSE_SYNTAX_GUIDE). Solución vigente: `event_bus_device := class<concrete>(creative_device)` instanciado en Main.umap, referenciado vía `@editable`. Decisión arquitectónica D-A11 en CHANGELOG (excepción a D-A7 — los otros 5 Cores siguen siendo singletons top-level). Spec completa del patrón en `BOOTSTRAP_PIPELINE.md` §11. Schema del catálogo en `JSON_SCHEMAS.md` §42. Catálogo de eventos en `MODULES_DEPENDENCY_GRAPH.md` §11.2. La generación de los 2 archivos en `Generated/` es responsabilidad del exporter Python de SPR-004 extendido. Tiempo subió 1h → 1.5h estimado por el coste de validar el catálogo + smoke del patrón emit/consume — **el real fue ~6h** porque la investigación F-B descartó 5 hipótesis (H1-H3 fail, H5 viable solo con device parent → H4) antes de converger en el patrón final. Postmortem fase 1: `docs/postmortems/PM-SPR-009-blocked.md`. Postmortem fase 2 (resolución): pendiente F-C-5 SPR-009.

#### SPR-010 — Verse: Admin Commands

- **Fase**: F0
- **Sistema(s)**: SYS-070
- **Dependencias**: SPR-006, SPR-008, SPR-009
- **Tipo**: verse + ui
- **Tiempo**: 2h estimado (real esperado 4-6h post-Step 0.5 investigación API)
- **Archivos**:
  - `Content/Verse/Core/AdminCommands.verse`
  - `Content/Verse/Devices/AdminPanel.verse`
- **Done**:
  - [ ] `Core/AdminCommands.verse` = namespace puro stateless (`AdminCommands<public> := module:`)
  - [ ] `IsAdmin<public>(Refs:[]player_reference_device, Agent:agent)<transacts><decides>:void` itera Refs + `if (Ref.IsReferenced[Agent]): return` / `fail` si ninguna match
  - [ ] `Devices/AdminPanel.verse` declara `admin_panel_device := class<concrete>(creative_device)` con `@editable AdminRefs:[]player_reference_device = array{}`
  - [ ] State (Refs) vive en device instance, NO top-level (lección 5: `var` top-level SOLO `weak_map`)
  - [ ] `AdminPanel.OnBegin` consume `AdminCommands.IsAdmin[AdminRefs, Agent]` con `if`/`<decides>` propagado
  - [ ] UI sólo visible si `IsAdmin[AdminRefs, Agent]` succeeds
  - [ ] Smoke test in-session PASS: admin Ref configurado → UI visible / sin Ref → UI invisible
  - [ ] Mobile Preview NO crashea
  - [ ] Build UEFN sin warnings
- **Notas C1 + Auditoría retro Bloque 1 + B1.1-fix (SPR-010 L1-L4)**:
  - Identificación admin via `player_reference_device` configurado en editor UEFN. NO existe device dedicado a auth/admin en API Fortnite vigente (build 40.30-CL-53276632) — único mecanismo posible.
  - API real `player_reference_device`: `IsReferenced[Agent]<transacts><decides>:void` (NO `IsRegistered` que era API ficticia canonizada en B1.1 original). `Register(Agent):void`, `Clear():void` (no unregister selectivo), `GetAgent():?agent`, `AgentUpdatedEvent:listenable(agent)` subscribable. Fuente empírica + cross-refs en `API_REFERENCE_GENERATED.md` §3.7 + `VERSE_SYNTAX_GUIDE.md` lección 17.
  - Patrón canónico: Core stateless + Device state-bearing (`VERSE_SYNTAX_GUIDE.md` §2.4-bis). NO `Init(Refs)` requirement — Refs se pasa como param a las funciones.
  - Trampa documentar: `Activate()` ends round/game, NO activate-reference.
  - Trampa documentar: `Clear()` limpia state device entero, NO unregister selectivo. Multi-admin → 1 device por admin permanente.
  - Lección de proceso P5 derivada: auditorías retroactivas DEBEN incluir validación empírica (build real + Verse.digest). B1.1 original falló porque "API_REFERENCE.md decía X" se asumió correcto sin verificar empíricamente. Canonizar P5 en CHANGELOG L3.

### 13.4 Backlog Fase 1 — MVP playable (extracto, ~40 sprints)

> Aquí van los sprints SPR-011 a SPR-050. Por brevedad, indico la estructura. El detalle pleno se genera en sesión técnica.

- **SPR-011 a SPR-018**: Player Stats + Inventory básico (8 sprints)
- **SPR-019 a SPR-024**: Resource Gathering + Tools (6 sprints)
- **SPR-025 a SPR-030**: Crafting básico (6 sprints)
- **SPR-031 a SPR-034**: Base Building piezas modulares (4 sprints)
- **SPR-035 a SPR-038**: Combat core (4 sprints)
- **SPR-039 a SPR-042**: Zone Unlock + 1 zona inicial (4 sprints)
- **SPR-043 a SPR-046**: XP, Levels, Skill Points básicos (4 sprints)
- **SPR-047 a SPR-050**: Rebirth básico + Tutorial chain + First Minute Hook (4 sprints)

### 13.5 Backlog Fases 2–5

> Se generan al cierre de cada fase anterior, basándose en aprendizaje real. **No tiene sentido detallarlas a 6 meses vista.**

---

## 14. Decisiones cerradas (referencia)

> Este es el log de TODAS las decisiones tomadas durante el diseño. Si algo no está aquí, no se ha decidido.

### 14.1 Concepto y géneros

- **Género**: Survival Tycoon con coleccionismo de ayudantes y exploración progresiva.
- **PvP**: Solo PvE. Sin robo de ayudantes con dinero real (Brainrot-style descartado).
- **Multiplayer**: 1–8 jugadores por sesión.
- **Plataforma**: Fortnite (PC, consola, móvil).

### 14.2 Monetización

- **Modelo dual-currency**: Gemas (ganando) + V-Bucks (pagando).
- **Regla universal**: casi todo lo comprable también es ganable. Excepciones: cosméticos limitados de evento, founder pack, boosts extremos cortos.
- **Gemas SE QUEMAN al gastarse**. No se convierten a V-Bucks ni viceversa.
- **Trading**: directo same-session + auction same-session (NPC vendor).
- **Items pagados con V-Bucks**: NUNCA tradables.
- **Lootboxes**: solo gemas. Drop rates visibles. Pity por (alma_type, rarity_target).
- **`consequential_to_gameplay`** declarado por entitlement en JSON. Companions, equipment, gems, BP → `true`. Cosméticos puros, títulos → `false`. Regla Epic v39.00, ver §5.7. Sin esto, el oferta no publica.
- **Entrega de entitlements de alto valor**: diseñar con la **refund window de 20 días** en mente. No permitir convertir/disolver/quemar entitlements gameplay-changing antes de 21 días desde la compra. Ver §5.7.

### 14.3 Progresión

- **Rebirth rápido**: primer rebirth en 20–30 min.
- **Curva de rebirth**: r1 ~30 min, r5 ~3-4 h, r10 ~10 h, r25 ~30 h, r50 ~80 h, r100 ~200 h.
- **Skill points**: distribuibles por jugador en 5 ramas (Combate, Recolección, Supervivencia, Coleccionista, Economía).
- **BP separado del nivel jugador**: XP independiente.
- **Primer rebirth gateado por quests** del tutorial chain.

### 14.4 Death penalty

- Respawn: jugador elige base o último checkpoint descubierto (menú).
- Ayudantes: spawnean donde respawnea el jugador.
- Pierdes: % XP del nivel actual + % gold no depositado. **NO** pierdes gemas, ayudantes, items, quests.
- Protección: comprable/ganable. Tiers: 1h, 24h, 7d, permanente.

### 14.5 Coleccionismo

- **Rarezas**: Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Admin (8 tiers).
- **Variantes**: Normal, Oro, Diamante, Arcoiris + variantes de evento (Hacker, Lava, ilimitado).
- **Cada variante = entrada propia en Dex** (300+ entradas potenciales).
- **Drop rates orientativos**: Common 60%, Uncommon 25%, Rare 10%, Epic 3.5%, Legendary 1%, Mythic 0.4%, Secret 0.09%, Admin 0.01%.

### 14.6 Equipamiento

- **6 ranuras** de equipo invisible.
- **Tiers 1–10** con fail-rate progresivo (T1→T2 100% éxito, T9→T10 5%).
- **Protectores**: Bronce, Plata, Oro, Diamante.
- **Sets con bonus** por N piezas iguales.
- **Reroll de stats**: cada reroll del mismo item es más caro (curva exponencial).
- **Fail-rate aplica también a equipos invisibles**, no solo al equipo principal.

### 14.7 Live ops

- **Daily quests**: 3.
- **Weekly quests**: 9.
- **Reset UTC** (consistente con eventos).
- **Recompensas**: gemas + XP del BP.
- **Hourly boss**: portal cada HH:00, ventana 2 min, teleport masivo a HH:02. Requisitos configurables (nivel + flags). 1 intento por hora. Recompensas también dropean en otras fuentes.
- **BP**: free + premium (gemas o V-Bucks). 100% configurable JSON.
- **Códigos**: pre-pool grande compilado, activar manualmente.
- **Eventos cortos / admin abuse**: panel admin restringido por player ID.
- **Shop session**: rotación cada 30 min sincronizada UTC.

### 14.8 Base persistente

- **Base level es eje global**: gate de zonas, quests, boss event.
- **Permanente**: NO se resetea al rebirth (único sistema 100% permanente).
- **Generadores offline**:
  - Cap configurable por upgrades (ej. base lvl 10 → 12h, base lvl 50 → 48h).
  - Eficiencia escalable por upgrades (ej. 30%–80%).
  - Producen TODOS los recursos (con ratio bajo para gemas).
- **Crafting timers**: tiempo real corre 100% offline (sin cap, sin reducción).

### 14.9 UI/UX

- **Activity Log UI** (no popups): 4 líneas, auto-fade configurable, colores por categoría, sin click action.
- **First Minute Hook**: visual + acción inmediata + recompensa (sin cinemática).
- **Idle Summary** al entrar.
- **Auto-sell**: por rareza + por tipo + whitelist.
- **Pre-inventory filter**: vender antes de entrar al inventario.
- **Visual compare**: deltas de stats al ver item nuevo.
- **Search/filter**: en inventario y Dex.
- **Hotkeys** + radial menu móvil.
- **Error handling UI**: mensajes claros, nunca silencio.
- **Rate limiting** en botones críticos.

### 14.10 Tecnología

- **Persistencia**: 4 weak_maps (PlayerCore, PlayerInventory, PlayerProgress, PlayerEconomy). 128 KB cada uno.
- **BigNumbers**: lib comunidad (a localizar en fase técnica).
- **Time sync**: UTC server-side via `GetSimulationElapsedTime()`.
- **Localización**: auto-localization a 14 idiomas (UEFN free).
- **Optimización móvil**: World Partition + HLODs + 512×512 max textures + LODs + HISM + 1 mat per mesh.

### 14.11 Sistema de daily logs (proceso)

- **Carpeta única**: `docs/dailylog/` (singular). Declarada en `FOLDER_STRUCTURE_TRUTH.md` §6 + §6.2.
- **Un archivo por día**: nombrado `DL_YYYY-MM-DD_SPR-<tokens>_<autor>.md` (regex `^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$`). Tokens unidos por `+` representan los SPR cerrados ese día (`001`, `002`, `FIX1` para hotfixes relativos al sprint base anterior). Ejemplo retroactivo: `DL_2026-05-06_SPR-001+FIX1_lexosi.md` cubre cierre de SPR-001 + tag `SPR-001-FIX-1`.
- **`docs/DAILY_LOG.md` raíz** = plantilla canónica + instructivo. **NO se rellena nunca.** Histórica referencia a `docs/daily_logs/` (plural) eliminada el 2026-05-06.
- **Generación**: única fuente válida es `scripts/tools/close_sprint.py` (formalizado en SPR-207, ver `SPRINTS_BACKLOG.md` §10). Cero edición manual de archivos en `docs/dailylog/` salvo el bloque `<!-- BEGIN MANUAL --> ... <!-- END MANUAL -->` al final de cada DL.
- **Trigger**: opción **B** (script Python invocado a mano por el humano tras crear el tag SPR-XXX). Razón: hooks `post-commit` no disparan al crear `git tag` (no hay hook git nativo local para creación de tags); opción C (comando aider) acopla a herramienta y es frágil ante cambios de runner. Trade-offs aceptados: el humano tiene que acordarse de ejecutar `python scripts/tools/close_sprint.py` después de cada `git tag` — contrato claro, idempotente, auditable. Mitigación al olvido: el script es idempotente (reejecutable sin daños) y barato (segundos), por lo que el humano puede ejecutarlo varias veces al día sin preocuparse.
- **Idempotencia obligatoria**: ejecutar el script 2× para el mismo SPR no duplica entradas, no reescribe el bloque MANUAL y solo refresca los bloques `<!-- BEGIN AUTO:... -->`.
- **Configuración local del autor**: archivo `.dailylog_user` en raíz del repo, gitignored. Primer arranque pide nickname una vez (regex `^[a-z0-9]+$`) y lo guarda. Flag `--reset-user` para sobrescribir.
- **Datos auto-extraídos**: fecha, tokens SPR, branch, commits desde medianoche, archivos por commit, tags del día, working tree status, último commit, título/tipo/estimación del SPR (parseando `SPRINTS_BACKLOG.md`). Lo no inferible (energía, bloqueos detallados, decisiones, notas para mañana) cae en el bloque MANUAL como placeholders.
- **Decisión cerrada el 2026-05-06** (cierre SPR-001 + hotfix `SPR-001-FIX-1`). Reflejada en `FOLDER_STRUCTURE_TRUTH.md` §1.1 + §5 + §6 + §6.2, `WORKFLOW.md` §3 Fase 4 + §5, `DAILY_LOG.md` (reescrito completo), `SPRINTS_BACKLOG.md` §10 (SPR-207).

---

## 15. Convenciones técnicas

### 15.1 Estilo Verse

- **Indentación**: 4 espacios (no tabs).
- **Naming**:
  - Clases: `PascalCase` (`PlayerStats`, `CompanionCore`)
  - Funciones: `PascalCase` (`GetCurrentXP()`, `AddGold()`)
  - Variables locales: `camelCase` (`currentLevel`, `goldEarned`)
  - Constantes: `UPPER_SNAKE_CASE` (`MAX_LEVEL`, `BASE_XP_PER_KILL`)
- **Persistence safety**: SOLO añadir campos opcionales con defaults. NUNCA renombrar/eliminar.
- **Async**: usar `spawn{}` para fire-and-forget; `await` para operaciones secuenciales.
- **Failure handling**: siempre tratar `decides` failures con `if`/`else` explícitos.
- **Comments**: docstring al inicio de cada función pública.

### 15.2 Estilo Python

- **Estilo**: PEP 8.
- **Type hints** obligatorios en funciones públicas.
- **Docstrings** Google-style.
- **Import order**: stdlib → third-party → local.
- **Sin lógica de runtime**: Python solo es build-time.
- **Idempotencia**: scripts se pueden ejecutar N veces, mismo resultado.

### 15.3 Estilo JSON

- **Indentación**: 2 espacios.
- **Comentarios**: clave `_comment` o `_doc`. JSON estricto no permite comentarios reales.
- **Schemas**: documentados en `docs/json_schemas.md` (a generar).
- **IDs**: nunca renumerar IDs existentes (rompería persistencia).
- **Validación**: pasar `01_validate_jsons.py` antes de cualquier commit.

### 15.4 Git workflow

- **Branches**: `main` (publicable), `dev` (integración), `feature/SPR-xxx-descripcion`.
- **Commits**: prefijo con SPR-ID. Ej: `SPR-007: implementar GetUTCNow()`.
- **PRs**: cada sprint = 1 PR ideal.
- **Tags**: tras cada fase (`v0.1-foundation`, `v1.0-mvp`, etc.).

---

## 16. Glosario

| Término | Definición |
|---|---|
| **UEFN** | Unreal Editor for Fortnite. La herramienta de Epic para crear islas. |
| **Verse** | Lenguaje de scripting de UEFN. Runtime del juego. |
| **Persistencia / weak_map** | Sistema de Verse para guardar datos del jugador entre sesiones. Limitado a 4 maps × 128 KB. |
| **Same-session** | Solo válido entre los 1–8 jugadores conectados a la misma instancia. |
| **In-Island Transactions** | API de Epic para vender items con V-Bucks dentro de islas. Live desde 9 enero 2026. |
| **Entitlement** | Item desbloqueado tras compra V-Bucks. Tu sistema lo detecta y otorga. |
| **Pity system** | Garantía de drop tras X intentos fallidos. Standard F2P. |
| **Rebirth** | Reset de progreso normal a cambio de meta-progresión permanente. |
| **Base level** | Eje de progresión permanente. NO se resetea con rebirth. Gate maestro. |
| **Theme pack** | JSON + assets que tematizan un mapa (medieval, sci-fi, horror...). Cambio = mapa nuevo. |
| **Activity Log UI** | Panel acumulativo de mensajes en esquina (no popups). |
| **Sprint** | Unidad de trabajo de 1–2 horas. Granularidad de planificación. |
| **SYS-xxx** | Identificador de sistema. Referencia entre docs. |
| **SPR-xxx** | Identificador de sprint. Referencia entre docs. |

---

## 📌 Notas finales

- Este documento es **vivo**. Se actualiza al cierre de cada fase con aprendizajes reales.
- Toda decisión nueva se añade a la sección 14.
- Toda restricción nueva descubierta se añade a la sección 5.
- El **prompt de IA** (PROMPT.md) referencia este doc como fuente de verdad.

**Fin del documento.**
