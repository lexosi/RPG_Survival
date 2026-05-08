# 🚨 EMERGENCY_ROLLBACK — Protocolos de emergencia

> **Qué hacer cuando algo se rompe.**
> Léelo ANTES de que lo necesites. Cuando lo necesites no tendrás tiempo de leerlo.

---

## 🧭 Índice

1. [Filosofía: prevenir > recuperar](#1-filosofía-prevenir--recuperar)
2. [Estrategia Git obligatoria](#2-estrategia-git-obligatoria)
3. [Escenario 1: DeepSeek genera código que crashea editor](#3-escenario-1-deepseek-genera-código-que-crashea-editor)
4. [Escenario 2: Push Changes corrompe la sesión live](#4-escenario-2-push-changes-corrompe-la-sesión-live)
5. [Escenario 3: Verse no compila tras cambio masivo](#5-escenario-3-verse-no-compila-tras-cambio-masivo)
6. [Escenario 4: Persistencia corrupta en cuenta de testing](#6-escenario-4-persistencia-corrupta-en-cuenta-de-testing)
7. [Escenario 5: Pierdes 2h+ de trabajo sin commit](#7-escenario-5-pierdes-2h-de-trabajo-sin-commit)
8. [Escenario 6: Epic bloquea publish por backwards-compat](#8-escenario-6-epic-bloquea-publish-por-backwards-compat)
9. [Escenario 7: UEFN editor no abre el proyecto](#9-escenario-7-uefn-editor-no-abre-el-proyecto)
10. [Escenario 8: DeepSeek se queda en bucle infinito de errores](#10-escenario-8-deepseek-se-queda-en-bucle-infinito-de-errores)
11. [Postmortems: aprender de cada crisis](#11-postmortems-aprender-de-cada-crisis)
12. [Hábitos preventivos diarios](#12-hábitos-preventivos-diarios)

---

## 1. Filosofía: prevenir > recuperar

### 1.1 Las 3 reglas absolutas

1. **COMMIT FRECUENTE**: cada sprint completado = 1 commit. Sin excepciones.
2. **BRANCHES POR FASE**: cada fase F0-F5 vive en su propia rama. Master solo recibe merges probados.
3. **NUNCA EDITAR PERSISTENCIA EN VIERNES**: o cuando estás cansado. Persistencia rota = juego roto.

### 1.2 El coste real de cada tipo de fallo

| Fallo | Tiempo de recuperación si tienes commits frecuentes | Tiempo si no |
|---|---|---|
| Crash de editor | 2 min (revert) | 30 min-2h |
| Verse no compila | 5 min (revert sprint) | 1-3h |
| Persistencia corrupta | 10 min (limpiar cuenta test, revertir schema) | irrecuperable en algunos casos |
| Editor no abre proyecto | 15 min (clean rebuild) | día perdido |

**Conclusión**: 30 segundos de `git commit -m "..."` ahorran horas.

---

## 2. Estrategia Git obligatoria

### 2.1 Setup inicial (una vez)

```bash
cd <ruta-proyecto-uefn>
git init
git add .
git commit -m "🎬 Initial commit"

# Branches por fase
git branch f0-foundation
git branch f1-mvp
git branch f2-companions
git branch f3-economy
git branch f4-base
git branch f5-events

# Trabajamos en la rama de la fase activa
git checkout f0-foundation
```

### 2.2 .gitignore mínimo

```gitignore
# UEFN auto-generated
Saved/
Intermediate/
Build/
DerivedDataCache/
.vs/
*.user

# Logs
*.log

# Backup files
*.bak
*~

# OS
.DS_Store
Thumbs.db

# Secrets
.env
secrets.json
```

### 2.3 Commits diarios obligatorios

```bash
# Tras cada sprint completado:
git add .
git commit -m "✅ SPR-XXX: <descripción breve>"

# Al final del día:
git tag day-YYYY-MM-DD
git push origin <branch-actual>
```

### 2.4 Tags por fase

Cuando termines una fase:

```bash
git checkout f0-foundation
git tag -a v0.1-foundation-complete -m "Fase 0 terminada"
git checkout master
git merge f0-foundation
git push origin master --tags
```

### 2.5 Tags antes de cambios delicados

**ANTES de hacer un cambio que toca persistencia, schema, o multi-archivo grande**:

```bash
git tag -a pre-persistence-refactor-$(date +%Y%m%d) -m "Antes de refactor"
```

Si algo va mal:

```bash
git reset --hard pre-persistence-refactor-20260515
```

### 2.6 Git para UEFN: peculiaridades

- **Archivos `.uasset` y `.umap`** son binarios. Git LFS recomendado si superan 50MB.
- **No mover archivos `.verse` con persistencia** sin protocolo (ver PERSISTENCE_MAP sección 8.6).
- **Conflicts en .uasset**: imposibles de mergear manualmente. Coordinar con colaboradores.

---

## 3. Escenario 1: DeepSeek genera código que crashea editor

### 3.1 Síntomas

- UEFN editor cierra sin warning al abrir el proyecto
- Crash al hacer Build Verse Code
- Crash al spawnear actor o instanciar device
- Errores rojos en consola sobre `verse.dll` o `nullref`

### 3.2 Procedimiento

#### Paso 1: Identifica el archivo culpable
```bash
git status                      # ¿qué cambió desde el último commit estable?
git diff HEAD~1                 # ¿qué cambió en el último commit?
```

#### Paso 2: Revert quirúrgico
```bash
# Si fue un sprint específico:
git log --oneline               # encuentra el SHA del commit malo
git revert <sha>                # revierte ese commit creando uno nuevo
```

O si no hiciste commit aún del cambio malo:
```bash
git checkout -- <archivo-afectado.verse>
# o si afectó varios:
git checkout -- Content/Verse/Systems/<carpeta>/
```

#### Paso 3: Confirma que el editor abre

1. Cierra UEFN totalmente
2. Borra `Saved/`, `Intermediate/`, `DerivedDataCache/`:
   ```bash
   rm -rf Saved Intermediate DerivedDataCache
   ```
3. Abre UEFN
4. Build Verse Code (Ctrl+Shift+B)
5. Si compila, sigue funcionando ✅

#### Paso 4: Diagnóstico
- Lee el código revertido con DeepSeek pidiéndole que diagnostique POR QUÉ crasheó
- Si no es obvio → escala a Opus
- Documenta el patrón en este archivo (sección 11 Postmortems)

### 3.3 Cómo prevenirlo

- **Compila tras cada archivo nuevo**, no esperes a tener 5 archivos
- **Tras cada SPR de DeepSeek, Build Verse antes de hacer commit**
- **Plantillas de pull request mental**: ¿este código tiene loops infinitos? ¿tiene NULLs sin checkear?

---

## 4. Escenario 2: Push Changes corrompe la sesión live

### 4.1 Síntomas

- Tras Push Changes, los jugadores conectados quedan congelados
- Errores en pantalla rojos durante gameplay
- HUD desaparece o queda en estado raro
- Persistencia no se guarda

### 4.2 Procedimiento

#### Paso 1: Stop de inmediato

1. **NO hagas otro Push Changes** (empeora el estado)
2. **Cierra la sesión live** (todos los jugadores salen)
3. Vuelve al editor

#### Paso 2: Revierte el cambio
```bash
git log --oneline -10
git revert HEAD
```

O recovery desde tag:
```bash
git reset --hard day-YYYY-MM-DD-mañana
```

#### Paso 3: Build Verse Code limpio

```bash
# Cierra UEFN
rm -rf Saved Intermediate DerivedDataCache
# Reabre UEFN
# Ctrl+Shift+B
```

#### Paso 4: Re-publica versión estable

1. Push Changes con versión revertida
2. Espera 2-3 minutos para que Epic propague
3. Inicia sesión nueva
4. Verifica que persistencia de cuenta-test siga viva

### 4.3 Si la persistencia se corrompió

Ver Escenario 4 más abajo.

---

## 5. Escenario 3: Verse no compila tras cambio masivo

### 5.1 Síntomas

- 50+ errores rojos en consola tras Build Verse
- Errores cascada (uno → 30 errores derivados)
- Editor cuelga durante Build

### 5.2 Procedimiento

#### Paso 1: Lee el PRIMER error
- Casi siempre, los errores 2-50 son derivados del 1
- Arregla el primero antes de mirar los siguientes

#### Paso 2: Si los errores son demasiados → revert
```bash
git status
git checkout -- <ruta>          # archivo a archivo
# o nuclear:
git reset --hard HEAD
```

#### Paso 3: Re-aplicar cambio en pasos pequeños
1. Aplica solo 1 archivo del cambio
2. Build → ¿compila?
3. Sí → siguiente archivo
4. No → diagnostica, fix, retry

### 5.3 Diagnóstico común

| Error | Causa típica |
|---|---|
| "Module not found" | Falta `using { ... }` o el módulo no está exportado |
| "Cannot resolve name X" | Typo o función no existe (consultar API_REFERENCE_GENERATED.md) |
| "Type mismatch" | Tipo cambiado en alguna struct/class |
| "Persistable expected" | Falta `<persistable>` en un campo |
| "Persistable class must be final" / warning de subclase potencial en `class<persistable>` | Falta `<final>` en una `class<persistable>`. Patrón canónico: `<Bucket> := class<final><persistable>:`. Aplica solo a `class`, NO a `struct<persistable>` (los structs no soportan herencia). Spec en `PERSISTENCE_MAP.md` §3 cabecera. |
| "Effect specifier mismatch" | Falta `<suspends>`, `<transacts>`, etc. |

---

## 6. Escenario 4: Persistencia corrupta en cuenta de testing

### 6.1 Síntomas

- Tu cuenta-test entra al juego con datos extraños (gold negativo, level 0, etc.)
- LoadPlayer*() devuelve valores raros
- Errores tipo "field X expected int, got string" en consola

### 6.2 Realidad cruda

> **Si la persistencia se corrompió en cuentas de jugadores REALES, normalmente es irrecuperable.**
> **Por eso la regla #1: cuenta-test SIEMPRE para probar cambios de schema.**

### 6.3 Procedimiento (cuenta-test)

#### Paso 1: Identifica si fue tu fault o de Epic

- ¿Cambiaste schema sin protocolo? → tu fault
- ¿Renombraste un campo? → tu fault, cuenta corrupta
- ¿Push Changes durante sesión? → posible corrupción intermitente

#### Paso 2: Reseteo de cuenta-test

UEFN sí ofrece vía oficial para borrar persistencia (Opción 0). Las opciones A/B/C quedan como fallback si la vía oficial no aplica:

**Opción 0 (oficial, recomendada)**: UEFN Content Service → tu Project → Persistence → Delete (o Export para conservar copia previa al borrado).
- Vía documentada por Epic en el anuncio oficial de UEFN Persistence (ver `https://forums.unrealengine.com/t/uefn-persistence-announcement/709423`).
- Borra los datos persistentes de tu Project en el lado servidor de Epic.
- Soporta Export antes de Delete si necesitas conservar el estado previo.
- Es la primera opción a probar antes de cualquier hack.

**Opción A (fallback no verificado)**: Cambiar el `island_id` temporalmente (cambia el contexto persistente)
- En `Content/_Game.umap`, cambia algún parámetro persistente del root
- Tu cuenta verá "primera vez" otra vez
- ⚠️ Esto resetea TODA la persistencia, no solo tu cuenta
- ⚠️ No documentado oficialmente por Epic — validar empíricamente antes de usar. Preferir Opción 0.

**Opción B (fallback)**: Usar AdminCommands para reset
- Si tienes el sistema SYS-072 implementado, comando admin tipo `/admin reset_my_data`
- Limpia las 4 weak_maps de tu cuenta

**Opción C (fallback)**: Editor admin override
- Modifica temporalmente PersistenceLayer para forzar `Version = 0` y trate todo como nuevo
- Aplica solo a cuenta-test
- Revertir tras limpiar

#### Paso 3: Implementa validación defensiva

Si esto pasó, **es señal de que falta validación defensiva**. Ver PERSISTENCE_MAP sección 10.

#### Paso 4: Audita schema

```bash
# Compara el schema antes y después
git diff <commit-anterior> Content/Verse/Core/PersistenceLayer.verse
```

Verifica que **NO** hayas:
- Renombrado campos
- Eliminado campos
- Cambiado tipos
- Movido archivos `.verse` con persistencia

### 6.4 Si la persistencia se corrompió en cuentas REALES de jugadores

**Esto es grave**. Procedimiento:

1. **Para de publicar updates inmediatamente**
2. **Identifica el cambio que rompió** (probablemente schema rename/delete)
3. **Revierte el cambio en código** y publica el rollback
4. ⚠️ **Los datos de jugadores afectados pueden estar perdidos**: depende de cómo Epic los guardó
5. **Comunica con la comunidad** vía Discord: "hay un issue, lo estamos arreglando"
6. **Postmortem detallado** para no repetir

---

## 7. Escenario 5: Pierdes 2h+ de trabajo sin commit

### 7.1 Realidad

Si no hiciste commit Y el archivo se corrompió Y UEFN crashed sin guardar...

**El trabajo está perdido**.

### 7.2 Last resort

#### Auto-save de UEFN
- UEFN guarda cada 10 min en `Saved/AutoSaves/`
- Mira si hay `.verse` recientes ahí
- Copia a tu carpeta y compáralos con el actual

#### Auto-save de VS Code / Cursor
- VS Code mantiene historial local
- File > Time Travel (en algunas versiones) o extensión Local History
- Cursor tiene similar

#### Buffers de DeepSeek
- Si el código que se perdió fue generado por DeepSeek, **el chat de DeepSeek aún tiene la respuesta**
- Vuelve al chat y copia el código de nuevo

### 7.3 Lección a aprender

**Configura auto-commit cada hora**:

```bash
# Crea un script auto_commit.sh:
#!/bin/bash
cd /ruta/proyecto
git add .
git commit -m "🤖 Auto-commit $(date +%H:%M)"

# Cron cada hora:
0 * * * * /ruta/auto_commit.sh
```

O usa una extensión de VS Code tipo "Git Auto Commit".

---

## 8. Escenario 6: Epic bloquea publish por backwards-compat

### 8.1 Síntoma

Al hacer Push Changes en versión publicada (no preview), Epic responde:
```
ERROR: You can't publish this version because your Verse persistable data is not backward compatible with your current active version.
  Field 'PlayerCore.Gold' was renamed/removed/retyped.
  Publish blocked.
```

### 8.2 Procedimiento

#### Paso 1: NO fuerces el publish
Aunque encuentres workaround, **no lo hagas**. Epic enforza esto por una buena razón.

#### Paso 2: Audita el cambio

```bash
git diff <ultima-version-publicada> Content/Verse/Core/PersistenceLayer.verse
```

Identifica EXACTAMENTE qué campo cambió.

#### Paso 3: Revierte ese cambio específico

Si renombraste:
```verse
# REVERTIR:
NewName:int = 0  # ← cambiado
# A:
OldName:int = 0  # ← original publicado
```

Si eliminaste:
```verse
# AÑADIR DE NUEVO:
DeprecatedField:int = 0  # DEPRECATED, mantenido para compat
```

Si cambiaste tipo:
```verse
# REVERTIR el tipo, añadir campo nuevo:
OldField:int = 0
NewField:string = ""  # ← campo nuevo aparte
```

#### Paso 4: Publica de nuevo

Build → Push Changes. Si Epic acepta, problema resuelto.

### 8.3 Cómo prevenirlo

- **Antes de cualquier cambio en `PersistenceLayer.verse`**, lee PERSISTENCE_MAP sección 8 entero
- **Pide review a Opus** ANTES de publicar cambios de schema
- **Usa la cuenta-test con datos viejos** para probar antes de publicar

---

## 9. Escenario 7: UEFN editor no abre el proyecto

### 9.1 Síntomas

- Editor lanza, intenta cargar el proyecto, crashea
- Pantalla negra infinita
- "Project failed to load" sin más detalle

### 9.2 Procedimiento

#### Paso 1: Limpia caches
```bash
cd <proyecto>
rm -rf Saved/
rm -rf Intermediate/
rm -rf DerivedDataCache/
rm -rf .vs/
```

#### Paso 2: Abre UEFN

1. Si abre → 80% de los casos resuelto
2. Si no → siguiente paso

#### Paso 3: Genera archivos de proyecto desde cero

- Click derecho en `.uproject` → "Generate Visual Studio project files"
- Cierra todo, vuelve a abrir UEFN

#### Paso 4: Revert al último commit estable

```bash
git log --oneline | head -20    # busca el último commit "estable"
git checkout <commit-sha>       # checkout temporal
```

Si abre con ese commit, el problema está en commits posteriores.

```bash
# Bisect para encontrar exactamente qué commit lo rompió:
git bisect start
git bisect bad HEAD              # ahora rompe
git bisect good <commit-estable> # antes funcionaba
# Git te lleva al medio. Compila → marca good/bad.
git bisect reset                 # cuando encuentres el culpable
```

#### Paso 5: Reinstala UEFN

Si nada de lo anterior funciona:
1. Cierra Epic Games Launcher
2. Desinstala UEFN
3. Reinstala
4. Abre el proyecto

### 9.3 Si nada funciona

- Crea proyecto nuevo
- Copia `Content/`, `Config/`, `data/`, `scripts/` al nuevo proyecto
- Re-importa assets

**Lección**: backups offsite (GitHub) son tu salvación.

---

## 10. Escenario 8: DeepSeek se queda en bucle infinito de errores

### 10.1 Síntomas

- DeepSeek genera código → error de compilación
- Le pides corregir → genera otra cosa que también falla
- Repetido 3-5 veces, no llega a solución

### 10.2 Procedimiento

#### Paso 1: STOP. Cierra ese chat.
- Cada turno empeora el contexto
- Cada error nuevo "contamina" la memoria del modelo

#### Paso 2: Resetea con cápsula

Abre chat nuevo. Pega:
1. DEEPSEEK_CAPSULE.md (cápsula corta)
2. El problema **simplificado al máximo**

```
SPR-XXX en error.

Error de compilación:
[pegar SOLO el primer error]

Archivo afectado:
[pegar archivo entero ACTUAL, no historial]

Tu tarea: diagnosticar y arreglar SOLO ese error.
NO refactorices nada más.
NO añadas código nuevo.
SI no estás seguro de la causa, di STOP y escala a Opus.
```

#### Paso 3: Si sigue fallando → Opus

Tras 2 intentos fallidos del chat fresco, **escala a Opus**.

```
🚨 ESCALADO

DeepSeek bloqueado en SPR-XXX.

Error persistente:
[pegar error]

Lo que ha probado DeepSeek:
- Intento 1: <descripción>
- Intento 2: <descripción>

Archivo en estado actual:
[pegar archivo]

Por favor diagnostica.
```

### 10.3 Cómo prevenirlo

- **No le des contexto sucio a DeepSeek**: si el chat tiene 10 turnos de errores, ciérralo
- **Sprints más pequeños**: si SPR-XXX da problemas, divídelo
- **Más Done Criteria explícitas** en spec original

---

## 11. Postmortems: aprender de cada crisis

### 11.1 Cuándo escribir postmortem

Cualquier crisis que cueste >30 min recuperar.

### 11.2 Plantilla

```markdown
# POSTMORTEM — YYYY-MM-DD — <título>

## Síntoma
[Qué viste]

## Causa raíz
[Qué causó realmente]

## Resolución
[Cómo se solucionó]

## Tiempo perdido
[Cuánto]

## Cómo prevenirlo
[Cambios al workflow / documentación / hábitos]

## Cambios al doc
[Si esto requiere actualizar este archivo o WORKFLOW.md]
```

### 11.3 Carpeta para postmortems

```
docs/postmortems/
  2026-05-15_persistence_corrupted_test_account.md
  2026-05-22_editor_wouldnt_open.md
  ...
```

### 11.4 Postmortem mensual

Una vez al mes, revisa la carpeta. Identifica patrones:
- ¿3 postmortems sobre el mismo tipo de error? → cambio sistémico necesario
- ¿Siempre los mismos archivos? → refactor o más tests

---

## 12. Hábitos preventivos diarios

### 12.1 Checklist matinal (5 min)

```
[ ] git status (¿hay cambios sin commit de ayer?)
[ ] git pull (si hay rama remota)
[ ] Abrir UEFN, Build Verse Code → ¿compila?
[ ] Abrir Mobile Preview → ¿no crashea?
[ ] Verificar cuenta-test sigue con datos válidos
```

### 12.2 Tras cada sprint (1 min)

```
[ ] Build Verse Code OK
[ ] Push Changes OK
[ ] Test in-session OK
[ ] git add . && git commit -m "✅ SPR-XXX: ..."
```

### 12.3 Al final del día (5 min)

```
[ ] git tag day-YYYY-MM-DD
[ ] git push origin <branch>
[ ] Daily Log actualizado (ver WORKFLOW.md)
[ ] Notas para mañana en Daily Log
```

### 12.4 Antes de cualquier cambio "delicado"

Cambios delicados:
- Toca persistencia
- Toca >5 archivos
- Refactor masivo
- Migración de schema

```
[ ] git tag pre-<descripcion>-YYYYMMDD
[ ] Pegar el cambio en chat con Opus para review
[ ] Confirmar que tienes Build Verse Code OK ANTES del cambio
[ ] Ejecutar el cambio
[ ] Build Verse OK → commit. Si fail → git reset --hard <tag>.
```

### 12.5 Antes de publicar update (publish, no Push Changes)

```
[ ] Backwards compat checklist (PERSISTENCE_MAP sección 11)
[ ] Smoke test master pasa
[ ] Mobile Preview OK
[ ] Cuenta-test sigue con datos válidos tras update
[ ] Memory budget dentro de threshold
[ ] git tag v0.X.Y
[ ] Push Changes con versión publicada
[ ] Esperar feedback comunidad 24h antes de siguiente publish
```

---

## 📌 Resumen ejecutivo

```
🛡️ TU MEJOR DEFENSA:
   - git commit cada sprint
   - branches por fase
   - tags antes de cambios delicados
   - cuenta-test SIEMPRE para probar persistencia
   - rm -rf Saved/Intermediate/DerivedDataCache/ resuelve el 60% de crashes

🚨 SI ALGO SE ROMPE:
   1. STOP de hacer cambios
   2. Identifica qué cambió
   3. Revert (git checkout o git reset)
   4. Verifica que vuelve a funcionar
   5. Re-aplica cambios en pasos pequeños

⚠️ NUNCA HACER:
   - Push Changes sin Build Verse OK previo
   - Cambios de schema sin leer PERSISTENCE_MAP sección 8
   - Renombrar/eliminar campos persistentes
   - Continuar con DeepSeek que está en bucle de errores
   - Trabajar 4h sin commit

💡 SI DUDAS, ESCALA A OPUS.
   Mejor 5 min de pregunta que 2h de recuperación.
```

---

**Fin del documento.**
