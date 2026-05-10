# 🐤 CANARY_VALIDATION_LOG — Pre-validación de primitivas Verse

> Log de throwaways usados para validar primitivas canónicas ANTES de canonizarlas en sprints reales. Aplicación directa Lección P1 SPR-009.

## Estructura por entry

| # | Primitiva | Sprint origen | Hipótesis | Build result | Smoke result | Decisión | Lección derivada |
|---|---|---|---|---|---|---|---|

## Entries

### 001 — `var top-level []player_reference_device` (SPR-010 Step 0) — RESUELTA

- **Sprint origen**: SPR-010 (AdminCommands + Panel)
- **Fecha inicial**: 2026-05-10 mañana
- **Fecha resolución**: 2026-05-10 (cascade L1-L4 completo)
- **Build final PASS**: UEFN ++Fortnite+Release-40.30-CL-53276632, throwaway v5

#### Cadena de iteraciones (5 versiones contra build real)

| Versión | Hash SHA-256 | Build | Causa fail | Lección derivada |
|---|---|---|---|---|
| v1 | `508bd8e5e178b2acecc74b6147aa8e26c581a209551b3828ad89183a179ae62d` | ❌ | err 3502 (var top-level no-weak_map) + err 3506 (IsRegistered ficticio) | Lección 5 confirmada empíricamente. API real es IsReferenced (lección 17) |
| v2 | `d47a0ae7ba50c13561e78793e551bbfb5fc95d7d3a7dbbddd3e384da9c328170` | ❌ | err 3535 + 3506 (return/fail prohibidos en `<decides>`) | Lección 18 nueva: return/fail no existen en `<decides>` |
| v3 | `c1f8ad3cc39eb2204e201ef81a83947f71be295f7aaaf6cc2c1ff03ab261f46e` | ❌ | err 3512 (`IsAdminLogic` var/set genera no_rollback, llamado desde `<transacts>`) | Lección 20 nueva: funciones `:logic` que mutan var propagan no_rollback |
| v4 | `c2cd567dc6e6c028dfc6018187de566b3235fe80667a40144e30241e44fceaa2` | ❌ | err 3512 (`Print()` dentro de failure context = no_rollback) | Lección 19 nueva: Print() es no_rollback, NO usable en failure contexts |
| v5 | `7c8d437ba5e2614cdde0219a4f25420e034fbbed843caef654b58f2d4a37b1fd` | ✅ PASS | — | Patrón canónico §2.4-bis confirmado empíricamente |

#### Hipótesis original

Lección 5 VERSE_SYNTAX_GUIDE ("var top-level SOLO weak_map") puede ser demasiado restrictiva. Array de device refs podría compilar.

#### Resultado

Lección 5 era exacta. Top-level var SOLO weak_map. **Patrón canónico para Core con state mutable no-weak_map**: §2.4-bis "Core stateless + Device state-bearing". Confirmado empíricamente con v5 PASS.

#### Investigación Step 0.5 (paralela a iteraciones throwaway)

- Verse.digest 40.30-CL-53276632 cache UEFN local (`%LOCALAPPDATA%\UnrealEditorFortnite\Saved\VerseProject\<project>\Fortnite\Fortnite.digest.verse` línea 2300+).
- Cross-validación con foro Epic Nov 2024 (player_reference_device thread).
- Cross-validación con foro Epic May 2023 (Has anyone successfully written a failable function — UltimateLambda Epic staff confirma return/fail prohibidos en decides).
- Cross-validación con foro Epic Apr 2023 (Use Print in function that uses specifiers — Incredulous_Hulk Epic staff confirma Print no_rollback, solución log_channel).

#### Lecciones canonizadas (todas en VERSE_SYNTAX_GUIDE.md L4 final)

| # | Contenido | Origen |
|---|---|---|
| 17 | API real player_reference_device + corolario `listenable(t)` subscribable | L1 (commit 7617b73) |
| 18 | `return`/`fail` NO existen en `<decides>` (lenient eval reordering compatibility) | L4 v2→v3 debug |
| 19 | `Print()` tiene `no_rollback` effect — NO usable en failure contexts; usar `log_channel` + `log.Print()` | L4 v4→v5 debug |
| 20 | Funciones `:logic` que muten `var` propagan `no_rollback`; wrapper trivial sobre failable es preferible | L4 v3 debug |

#### §2.4-bis confirmado

Patrón canónico "Core stateless + Device state-bearing" empíricamente validado. Segundo precedente §2.4 tras PersistenceLayer SPR-008. Aplicación inmediata: SPR-010 implementación real (Core/AdminCommands.verse + Devices/AdminPanel.verse) procede con firmas confirmadas.

#### Cascade B1.1-fix commits (audit trail completo)

- `012f6ac` — pre-flight TRUTH-fix (validador path-aware + drift estructural)
- `7617b73` — L1: API_REFERENCE §3.7 + VERSE_GUIDE lección 17 + §2.4-bis
- `d61d2df` — L2: CONCEPT §13.3 + GLOSSARY "Admin (player ID)"
- `3b97558` — L3: MODULES §4.6 + CHANGELOG B1.1-fix entry + JSON_SCHEMAS §37
- L4 final (este commit): CANARY_LOG entry 001 + lecciones 18/19/20 + throwaway v5 PASS

#### D-A11.1 confirmado vigente

Patrón "Core stateless + Device state-bearing" es la respuesta canónica del proyecto a "Core que necesita state mutable no-weak_map". Aplicado a SPR-010 AdminCommands. Aplicable a futuros Cores con state similar.

#### P5 funcionando

Lección de proceso P5 (validación empírica obligatoria en auditorías retroactivas) detectó y resolvió el drift B1.1 que ningún auditor previo capturó. Adicionalmente: P5 aplicada al propio Claude (web) en iteraciones v2/v3/v4 — cada FAIL forzó investigación contra Verse.digest + foros oficiales antes de prescribir nuevo patrón. Coste 4 iteraciones build UEFN; beneficio 3 lecciones nuevas canonizadas + patrón confirmado empíricamente.

#### Notas operativas

- Tiempo total cascade B1.1-fix: ~5h (pre-flight 45min + Step 0/0.5 1.5h + L1 30min + L2 30min + L3 30min + L4 v1-v5 1h + L4 final 30min).
- Tiempo SPR-010 implementación real (post-L4): pendiente, esperado 1-1.5h con spec confirmada empírica + patrón v5 reutilizable.
- Diferencial estimado vs estimado original SPR-010 (2h): ~3.5h atribuible a P5 ausente en auditoría B1 original. ROI P5 visible: docs B1.1-fix vivirán SPR-010..SPR-211+ sin tener que re-investigar.
- Material handbook directo: entry 001 + lecciones 17/18/19/20 + §2.4-bis = recipe completo "admin commands pattern + failable functions in Verse".