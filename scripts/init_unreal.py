# Ejecutado automáticamente al abrir el proyecto UEFN.
# Prepuebla los subsistemas del editor según la convención UEFN-TOOLBELT.
# Ver CONCEPT.md §6.3 y D-A6.

import unreal

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
