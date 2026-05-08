# 📅 DAILY_LOG — Plantilla canónica + instructivo del flujo

> **Este archivo NO es un log vivo.** Es la **plantilla de referencia** y el **instructivo** del sistema dailylog.
>
> Los daily logs reales viven en `docs/dailylog/`, un archivo por día, generados por `scripts/tools/close_sprint.py`. Este doc explica cómo funciona el sistema y muestra qué pinta tienen los archivos generados (para que humanos e IA entiendan el formato sin tener que ejecutar el script).
>
> **Sin Daily Log = sin memoria entre días = repetir errores y perder contexto.**

---

## 🧭 Índice

1. [Filosofía del sistema](#1-filosofía-del-sistema)
2. [Cómo funciona el flujo](#2-cómo-funciona-el-flujo)
3. [Naming canónico de los archivos](#3-naming-canónico-de-los-archivos)
4. [Comando: `close_sprint.py`](#4-comando-close_sprintpy)
5. [Configuración local: `.dailylog_user`](#5-configuración-local-dailylog_user)
6. [Bloque AUTO vs bloque MANUAL](#6-bloque-auto-vs-bloque-manual)
7. [Plantilla de referencia (qué genera el script)](#7-plantilla-de-referencia-qué-genera-el-script)
8. [Casos especiales](#8-casos-especiales)
9. [Reglas duras](#9-reglas-duras)

---

## 1. Filosofía del sistema

- **Honesto sobre tiempo, decisiones y bloqueos**: subestimar es mentirse.
- **Bloqueos van AL MOMENTO**, no al cierre (se olvidan). El bloque MANUAL del día se va rellenando durante el día, no al final.
- **Notas para mañana son sagradas**: el "yo de mañana" depende de los detalles concretos.
- **TDAH-friendly**: secciones cortas, bullets, sin párrafos largos.
- **Cero archivos a mantener manualmente**: el script extrae todo lo automatizable de git + `SPRINTS_BACKLOG.md`. Solo rellenas a mano lo que NO se puede inferir (energía, notas, decisiones, bloqueos).

---

## 2. Cómo funciona el flujo

### 2.1 Diagrama mental

```
[ DeepSeek/aider commitea ]
         │
         ▼
[ Humano taggea SPR-XXX al commit final del sprint ]
         │
         ▼
[ Humano corre `python scripts/tools/close_sprint.py` ]
         │
         ▼
[ Script extrae: SPR meta del backlog · commits del día · archivos · branch · status ]
         │
         ▼
[ ¿Existe ya DL_<hoy>_*_<autor>.md ? ]
   │ NO                              │ SÍ
   ▼                                 ▼
[ Crea DL_<hoy>_SPR-NNN_<autor>.md ] [ Renombra añadiendo nuevo segmento ]
   │                                 │
   └──────────────┬──────────────────┘
                  ▼
[ Abre el archivo en VS Code · humano completa bloque MANUAL ]
```

### 2.2 Fases reales de un día

1. **Briefing matinal** (humano + Opus): plan del día, objetivos, sprints a tocar. NO hay Daily Log activo todavía: el primer DL del día se crea cuando se cierre el primer sprint.
2. **Durante el día**: DeepSeek implementa, humano testea, commits con mensaje convencional. El humano va anotando bloqueos y decisiones en un scratch (post-it, nota local) — NO en `docs/dailylog/` todavía.
3. **Al cerrar un sprint** (humano taggea + ejecuta `close_sprint.py`):
   - Si es el primer sprint del día → crea el DL.
   - Si ya hay DL del día → lo renombra y refresca bloques AUTO.
   - El bloque MANUAL recibe (o conserva) el scratch acumulado del humano.
4. **Al cerrar el día**: el último DL del día queda persistido. NO hay paso de "archivar". El archivo ya está en su carpeta definitiva (`docs/dailylog/`) con su nombre definitivo.

---

## 3. Naming canónico de los archivos

Regex: `^DL_\d{4}-\d{2}-\d{2}_SPR-[\w+\-]+_[a-z0-9]+\.md$`

| Componente | Reglas | Ejemplo |
|---|---|---|
| Prefijo | literal `DL_` | `DL_` |
| Fecha | `YYYY-MM-DD` (ISO, día actual al ejecutar el script) | `2026-05-06` |
| Separador | `_` | `_` |
| Tokens SPR | `SPR-` + segmentos unidos por `+`. Cada segmento es un número de sprint (`001`, `002`) o un marcador de hotfix (`FIX1`, `FIX2`) relativo al sprint base anterior | `SPR-001+FIX1+002` |
| Separador | `_` | `_` |
| Autor | nickname lowercase (`^[a-z0-9]+$`), de `.dailylog_user` | `lexosi` |
| Extensión | `.md` | `.md` |

**Ejemplos válidos**:

- `DL_2026-05-06_SPR-001_lexosi.md` — solo SPR-001 cerrado.
- `DL_2026-05-06_SPR-001+FIX1_lexosi.md` — SPR-001 + hotfix `SPR-001-FIX-1`.
- `DL_2026-05-07_SPR-002+003_lexosi.md` — dos sprints cerrados el mismo día.
- `DL_2026-05-07_SPR-002+003+FIX1_lexosi.md` — SPR-002, SPR-003 y hotfix `SPR-003-FIX-1` en el mismo día.

**Renombrado al añadir segmentos**: cuando se cierra un sprint nuevo el mismo día, el script renombra el archivo (vía `git mv` para preservar historial). Idempotente: ejecutar 2× para el mismo SPR no añade el segmento dos veces ni reescribe el bloque MANUAL.

---

## 4. Comando: `close_sprint.py`

**Path**: `scripts/tools/close_sprint.py`. Declarado en `FOLDER_STRUCTURE_TRUTH.md` §5.

### 4.1 Uso

```bash
# Después de hacer commit final del sprint y crear el tag SPR-XXX:
python scripts/tools/close_sprint.py SPR-001

# Sin argumento → usa el último tag SPR del HEAD:
python scripts/tools/close_sprint.py

# Hotfix:
python scripts/tools/close_sprint.py SPR-001-FIX-1

# Resetear nickname:
python scripts/tools/close_sprint.py SPR-001 --reset-user

# Sin abrir VS Code:
python scripts/tools/close_sprint.py SPR-001 --no-open

# Output mínimo:
python scripts/tools/close_sprint.py SPR-001 --quiet
```

### 4.2 Origen de datos (auto al máximo)

| Dato | Fuente |
|---|---|
| Fecha | `date.today()` |
| SPR cerrado | argumento o último tag SPR-NNN[-FIX-K] |
| Título SPR | parsing fila `SPR-NNN` en `SPRINTS_BACKLOG.md` |
| Estimación, tipo, deps, archivos | columnas de la fila del backlog |
| Commits del día | `git log --since=<medianoche local>` |
| Archivos por commit | `git show --name-only` |
| Tags del día | `git for-each-ref refs/tags` filtrado por `creatordate:short = hoy` |
| Branch | `git branch --show-current` |
| Working tree | `git status --porcelain` |
| Último commit | `git log -1 --pretty=%h — %s` |
| Autor del DL | `.dailylog_user` (gitignored) |

**Datos que NO infiere → placeholders en bloque MANUAL**:

- Tiempo real trabajado.
- Energía, foco, satisfacción subjetivos.
- Bloqueos del día.
- Bugs encontrados (más allá de los inferibles).
- Decisiones tomadas.
- Notas para mañana.
- Notas misceláneas.

**Cero preguntas interactivas en CLI** salvo el alta inicial del autor.

### 4.3 Códigos de salida

| Exit | Significado |
|---|---|
| 0 | OK (creado o actualizado) |
| 1 | SPR no encontrado en backlog (cuando aplica) o error git |
| 2 | argumentos inválidos (formato SPR-NNN[-FIX-K] no encajó) |
| 3 | autor inválido en `.dailylog_user` (usar `--reset-user`) |

---

## 5. Configuración local: `.dailylog_user`

- **Path**: raíz del repo. **Gitignored** (ver `.gitignore`).
- **Contenido**: una línea con el nickname lowercase. Regex `^[a-z0-9]+$`.
- **Primer arranque**: si el archivo no existe, el script pregunta una vez y lo guarda. Próximas veces lo lee silenciosamente.
- **Reset**: `python scripts/tools/close_sprint.py --reset-user [SPR-XXX]`.

> **Por qué local**: cada humano que toca el repo se identifica con su propio nickname; el archivo NO se commitea para que clones limpios no arrastren un nickname ajeno y para que cada máquina mantenga el suyo.

---

## 6. Bloque AUTO vs bloque MANUAL

Cada daily log tiene dos zonas:

### 6.1 Zona AUTO (regenerable)

Marcadores `<!-- BEGIN AUTO:<sección> -->` ... `<!-- END AUTO:<sección> -->`.

Secciones AUTO:

- `sprints` — bloques por sprint cerrado (título, tipo, deps, estimación, tag, done criteria).
- `commits` — tabla `SHA | Mensaje` con commits desde medianoche.
- `files` — lista de archivos tocados con SHAs que los referencian.
- `status` — branch, último commit, working tree, tags creados hoy, push remoto.

Cada ejecución del script regenera estas secciones con datos frescos. **NO editar a mano** lo que está dentro de marcadores AUTO: la próxima ejecución sobrescribe.

### 6.2 Zona MANUAL (preservada)

Marcadores `<!-- BEGIN MANUAL -->` ... `<!-- END MANUAL -->` al final del archivo.

Contenido editado por el humano (energía, bloqueos, decisiones, notas para mañana, etc.). **El script NUNCA toca esta zona** entre ejecuciones; solo la inicializa con la plantilla por defecto cuando crea el archivo por primera vez.

---

## 7. Plantilla de referencia (qué genera el script)

> Este es exactamente el formato que produce `close_sprint.py`. Pegado aquí solo como referencia visual; el script lo construye desde código en `scripts/tools/close_sprint.py`. Para ver un ejemplo real, leer cualquier archivo de `docs/dailylog/`.

```markdown
<!-- AUTO-GENERATED. Actualizable con scripts/tools/close_sprint.py.
     No edites entre marcadores AUTO. Bloque MANUAL al final sí. -->

# Daily Log — YYYY-MM-DD — autor: <nickname>

**Sprints cerrados (segmentos)**: SPR-<tokens>
**Branch**: `<branch>`
**Último commit**: <sha7> — <subject>
**Generado**: YYYY-MM-DD HH:MM:SS

---

## 🎯 Sprints cerrados

<!-- BEGIN AUTO:sprints -->
### SPR-XXX — <título del backlog>
- **Tipo**: <tipo>
- **SYS**: <sys>
- **Deps**: <deps>
- **Estimación**: <Xh>
- **Tag git**: `SPR-XXX`
- **Done universal**: ✅ compila + ✅ test + ✅ commit con tag
- **Done criteria sprint**: ver `docs/SPRINTS_BACKLOG.md` (fila SPR-XXX y bloque Done de la fase)
- **Archivos clave declarados**: <archivos>
<!-- END AUTO:sprints -->

## 📦 Commits del día

<!-- BEGIN AUTO:commits -->
| SHA | Mensaje |
|---|---|
| `<sha7>` | <subject> |
<!-- END AUTO:commits -->

## 🗂️ Archivos tocados hoy

<!-- BEGIN AUTO:files -->
- `<path>` (`<sha7>`)
<!-- END AUTO:files -->

## 🔁 Estado del repo al cerrar

<!-- BEGIN AUTO:status -->
- **Branch**: `<branch>`
- **Último commit**: <sha7> — <subject>
- **Working tree**: limpio | sucio (N entradas)
- **Tags creados hoy**: `SPR-XXX`, `SPR-XXX-FIX-1`
- **Push remoto**: _ (rellenar manual)
<!-- END AUTO:status -->

---

<!-- BEGIN MANUAL -->
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
<!-- END MANUAL -->
```

---

## 8. Casos especiales

### 8.1 Cerrar un sprint sin tag

El script exige un identificador SPR válido. Si todavía no se ha creado el tag, el flujo correcto es: `git tag SPR-XXX` antes de ejecutar `close_sprint.py`. Si se invoca `close_sprint.py SPR-XXX` y no existe ese tag aún, el script igualmente genera el daily log (no exige existencia del tag, solo formato válido), pero queda como deuda taggear.

### 8.2 Hotfix posterior al cierre del día

Si el hotfix se cierra al día SIGUIENTE del sprint base, el script crea un DL nuevo para ese día con segmento `FIX1`. Ejemplo: SPR-002 cerrado el `2026-05-07`, hotfix `SPR-002-FIX-1` cerrado el `2026-05-08` → archivos:

- `DL_2026-05-07_SPR-002_<autor>.md`
- `DL_2026-05-08_SPR-FIX1_<autor>.md` *(token de fix sin base ese día)*

> **Caveat**: el segmento heurístico para hotfix sin sprint base ese día queda como `FIX1` "huérfano". Si esto incomoda, taggear `SPR-002-FIX-1` y usar `python scripts/tools/close_sprint.py SPR-002-FIX-1 ` aún funciona; el DL del día siguiente arranca con `SPR-FIX1` (heurística simple). Mejora pendiente: si el script detectase que el último DL conocido tiene token base, podría arrastrarlo.

### 8.3 Día sin sprint cerrado

No se crea daily log. El sistema no es un journal libre; es un cierre de sprints. Si se trabaja sin cerrar nada, no hay log automático y eso es intencional.

### 8.4 Múltiples humanos

Cada humano tiene su propio `.dailylog_user` local. Si dos humanos trabajan el mismo día sobre el repo, cada uno generará su propio archivo (sufijo `_<autor>` distinto). No hay merge automático; conviven en `docs/dailylog/`.

---

## 9. Reglas duras

1. **No editar bloques AUTO a mano**. Cada ejecución del script los regenera.
2. **El bloque MANUAL es sagrado**: el script lo preserva. Si necesitas borrar un manual antiguo, hazlo a mano.
3. **No mover archivos** de `docs/dailylog/` a otra carpeta. La estructura está declarada en TRUTH §6.2 y movimientos rompen el script.
4. **No commitear `.dailylog_user`**. Está en `.gitignore`. Si se commitea por accidente, `git rm --cached .dailylog_user`.
5. **Coherencia con TRUTH**: cualquier cambio al naming pattern o a la ruta `docs/dailylog/` exige actualizar `FOLDER_STRUCTURE_TRUTH.md` §1.1 + §6.2 + §5 ANTES.
6. **Idempotencia**: el script DEBE poder correrse 2× para el mismo SPR sin efectos laterales (más allá de un refresh de los bloques AUTO).

---

**Fin del documento.**

> Este archivo es plantilla + instructivo. Los datos reales viven en `docs/dailylog/`. Generación: `scripts/tools/close_sprint.py`.
