# ============================================================
# EventBus.verse — Core module (placeholder F-CLEAN-P1, 2026-05-11)
# Arquitectura: module namespace placeholder.
# REALIDAD OPERATIVA: el EventBus operativo es un creative_device generado
# por SPR-004 ext desde data/architecture/events_catalog.json, ubicado en
# Generated/EventBusDevice.verse. Decisión D-A11 (CHANGELOG L78).
#
# Razón D-A11: event(t){} top-level falla con err 3512 (propaga <transacts>
# al contexto top-level <computes> puro — lección 16 VERSE_SYNTAX_GUIDE).
# El parent class creative_device absorbe la propagación, permitiendo
# instanciar las propiedades event(t) en runtime UEFN.
#
# Acceso desde callers: NO usar este Core/EventBus directo. Usar:
#   @editable Bus:event_bus_device = event_bus_device{}
# (drag&drop la instancia generada al editar el device consumidor en UEFN).
#
# Spec: docs/SPRINTS_BACKLOG.md SPR-009 (🟢 done F-C-4 cierre)
# Patrón canónico: docs/BOOTSTRAP_PIPELINE.md §11 (post-H4)
# API consumer: docs/API_REFERENCE_GENERATED.md §3.5
#
# ESTADO PLACEHOLDER (F-CLEAN-P1 2026-05-11):
# CHANGELOG L622 declaró criterio "[x] Content/Verse/Core/EventBus.verse
# placeholder source-controlled" como Done SPR-009 — pero el archivo nunca
# se creó en disco. F-CLEAN-P1 lo materializa para que F0 cierre limpio.
#
# Este placeholder NO se importa desde ningún consumer (todos usan
# event_bus_device generado). Existe únicamente como anchor source-controlled
# del namespace Core/EventBus declarado en TRUTH §4.
# ============================================================

using { /Verse.org/Simulation }

EventBus<public> := module:

    # Marker que confirma que este placeholder está cargado.
    # NO usar para lógica — operativo vive en Generated/EventBusDevice.verse (D-A11).
    IsPlaceholder<public>():logic=
        true
