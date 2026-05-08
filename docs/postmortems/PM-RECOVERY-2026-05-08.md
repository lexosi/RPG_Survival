# PM-RECOVERY-2026-05-08 — Pérdida de `.git` local

## Resumen

Pérdida total del directorio `.git` local del proyecto `RPG_Survival` durante limpieza de archivos temporales del PC el 2026-05-07. Sin remote configurado, sin sync cloud, sin backup. Historial completo + 6 tags creados día 2026-05-07 (`day-2026-05-07-mañana/tarde/final`, `SPR-006`, `SPR-007`, `SPR-211`) perdidos localmente. Tags previos SPR-001..SPR-005 + auditorías + dailies también perdidos.

## Línea de tiempo

- **2026-05-07 ~tarde**: cierre SPR-006 + SPR-007 + SPR-211 con build UEFN limpio. Tag `SPR-211` creado en SHA `1c9f801`. Working tree limpio. Push pendiente (no había remote configurado).
- **2026-05-07 noche**: UEFN deja de abrir. Diagnóstico: archivos temporales corruptos.
- **2026-05-07 noche**: limpieza temps PC. `.git` borrado en el proceso (causa exacta no identificada — probable confusión entre temps Windows y carpeta proyecto, o herramienta de limpieza demasiado agresiva).
- **2026-05-08 mañana**: inicio sesión SPR-008. Pre-check `git status` falla con `fatal: not a git repository`.
- **2026-05-08 mañana**: diagnóstico búsqueda `.git` en disco — 0 resultados. Papelera vaciada. Sin VSS shadow copies. Sin backup externo.
- **2026-05-08 mañana**: decisión recovery: reinit repo desde working tree actual + setup remote GitHub para prevenir reincidencia.
- **2026-05-08 mañana**: ejecutado reinit. Commit inicial `1be2690` creado. Tags `SPR-211-recovered` y `pre-SPR-008` aplicados. Push a `https://github.com/lexosi/RPG_Survival.git`.

## Causa raíz

**Acumulación de 2 fallos**:

1. **Fallo de proceso operativo**: tras ~210 commits + ~10 tags acumulados, nunca se configuró remote git. El repo era 100% local. Decisión implícita "ya lo hago luego" mantenida durante toda Fase 0.
2. **Fallo de juicio durante limpieza temps**: borrado de carpeta proyecto sin verificar contenido. Posible que herramienta de limpieza incluyera carpetas ocultas (`.git` es hidden) en su scope.

Sin (1), (2) hubiera sido recuperable. El fallo crítico es (1).

## Impacto

| Categoría | Pérdida | Recuperable |
|---|---|---|
| Código `.verse` | Cero | N/A |
| Docs autoritativos | Cero | N/A |
| JSONs `data/` | Cero | N/A |
| Python scripts | Cero | N/A |
| Working tree state | Cero | N/A |
| Git history (commits) | Total local | No |
| Git tags (SPR-001..SPR-211 + dailies) | Total local | No (referencia simbólica vía `SPR-211-recovered`) |
| `git blame` capability | Total | No |
| Rollback a versiones previas | Total | No |
| Daily Logs `docs/dailylog/*.md` | Cero | Conservados como narrativa histórica |
| CHANGELOG.md | Cero | Conservado |

**Continuidad SPR-008**: 100%. Ningún bloqueo. SPR-008 depende del estado actual del working tree, no del historial.

## Acciones correctivas (aplicadas)

1. ✅ Reinit repo en `F:\Noobs\RPG_Survival\.git` con commit inicial `1be2690` preservando estado post-SPR-211.
2. ✅ Tags virtuales:
   - `SPR-211-recovered` → equivalente simbólico al perdido `SPR-211`.
   - `pre-SPR-008` → marca punto de partida SPR-008.
3. ✅ Remote `origin` configurado: `https://github.com/lexosi/RPG_Survival.git` (privado).
4. ✅ Push commit + tags a GitHub.

## Acciones preventivas (políticas vigentes desde hoy)

1. **Push remote obligatorio al cerrar cada sprint**. Tras `git tag SPR-XXX`, ejecutar `git push origin master --tags` antes de continuar al siguiente sprint. Documentar en `WORKFLOW.md` Fase 4.
2. **Push remote también al cerrar cada day** tras tag `day-YYYY-MM-DD-final`.
3. **Limpieza temps PC**: nunca tocar `F:\Noobs\` ni subcarpetas con herramientas automáticas. Limpieza manual y selectiva solo.
4. **Backup secundario opcional**: considerar mirror a GitLab o copia manual mensual a drive externo si el proyecto crece.
5. **Pre-check `git remote -v` añadido** a `WORKFLOW.md` Fase 1 (briefing matinal): verificar remote configurado y reachable antes de empezar el día.

## Lecciones

- **Proyectos solo-locales son frágiles**. La regla "no remote hasta tener algo presentable" es contraproducente en proyectos personales de >1 mes con commits diarios. El coste de configurar remote es 5 min, el coste de perderlo todo es horas de re-trabajo más historial perdido para siempre.
- **`.git` es hidden por defecto en Windows**. Cualquier "limpieza recursiva con borrado de hidden" puede destruir repos sin warning visible.
- **Reinit + recovery del working tree es viable**. SPR-008 no se ha bloqueado. La pérdida duele pero no es catastrófica si los archivos de trabajo siguen vivos.

## Referencias

- Daily Logs preservados: `docs/dailylog/DL_2026-05-06_*.md`, `docs/dailylog/DL_2026-05-07_*.md` — narrativa de qué se hizo en sprints perdidos.
- Tag virtual: `SPR-211-recovered` (commit `1be2690` nuevo repo).
- CHANGELOG entry: ver `docs/CHANGELOG.md` sección [Unreleased] entrada `RECOVERY-2026-05-08`.
