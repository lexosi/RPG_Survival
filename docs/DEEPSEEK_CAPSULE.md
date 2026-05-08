# 💊 DEEPSEEK_CAPSULE — Cápsula de contexto para DeepSeek

> **Pegar esta cápsula al inicio de CADA chat con DeepSeek V4-Pro/Flash.**
> Es la salvaguarda mínima para que DeepSeek no pierda contexto crítico al ejecutar.

---

## ⚡ Cápsula corta (pegar al inicio de cada chat)

```
🎯 PROYECTO: UEFN Survival Tycoon Modular Map.

🔒 REGLAS INNEGOCIABLES:
1. Verse: SOLO 4 weak_maps persistentes, máx 128 KB c/u. NUNCA renombrar/eliminar/cambiar tipo de campos publicados.
2. Datos en JSON, nunca hardcoded en Verse. Verse = lógica. Python = build/config. JSON = contenido.
3. Mobile-first: optimizar siempre. Texturas ≤512×512, LODs, HISM, 1 mat/mesh.
4. NO inventar APIs. Si no está en API_REFERENCE_GENERATED.md, STOP y reporta.
5. Si toca arquitectura/persistencia/UI no especificada → STOP y escala a Opus.
6. Shell: PowerShell. NO `python -c`, NO `&&`, NO heredocs. Verificadores en `scripts/tools/_throwaway/`.

📚 CONSULTA OBLIGATORIA antes de implementar:
- CONCEPT.md secciones 5 (restricciones UEFN), 6 (Python), 7 (Verse), 8 (mapping)
- PERSISTENCE_MAP.md si tocas persistencia
- API_REFERENCE_GENERATED.md si tocas Core/
- UI_UX_STYLE_GUIDE.md si tocas UI

🛠️ AL TERMINAR:
Reporta archivos con path absoluto + estado de cada Done Criteria (✅/❌/⚠️).

🌐 IDIOMA: Responde en español (España).
```

---

## ⚡ Cápsula extra-corta (5 líneas mínimas, si tienes prisa)

```
UEFN Modular Map. Reglas: 4 weak_maps máx 128KB. Datos en JSON, no hardcoded en Verse.
Mobile-first siempre. NO inventar APIs Verse/Python: usa API_REFERENCE_GENERATED.md.
Si toca arquitectura/persistencia/UI no specificada, STOP y escala. Reporta Done Criteria al final.
Verse = lógica gameplay. Python = config build-time. NO mezclar.
Idioma: español.
```

---

## 🧪 Cuándo cada cápsula

| Situación | Cápsula |
|---|---|
| Sprint complejo (300+ líneas, sistema nuevo) | **Cápsula corta** completa |
| Corrección de error simple | **Cápsula extra-corta** |
| JSON/data work | **Cápsula extra-corta** |
| Refactor amplio | **Cápsula corta** |
| Cualquier cosa que toque Core/persistencia/UI | **Cápsula corta** SIEMPRE |

---

## 📋 Plantilla completa de mensaje a DeepSeek

```
[CÁPSULA AQUÍ]

📦 SPRINT: SPR-XXX — [Título]

## Contexto necesario (lee antes de empezar)
[Pegar aquí los archivos relevantes]

## Especificación del sprint
[Pegar lo que dijo Opus en briefing]

## Done Criteria
- [ ] ...
- [ ] ...

## Tu tarea
1. Lee el contexto
2. Implementa el sprint completo
3. Reporta archivos creados/modificados con path absoluto
4. Marca cada Done Criteria como ✅/❌/⚠️ con justificación
5. Si hay decisión arquitectónica no clara → STOP y reporta
6. Si necesitas API no documentada → STOP y reporta

GO.
```

---

## ❗ Recordatorios para ti (humano)

1. **NO confíes en que DeepSeek "se acuerda" de cosas de chats anteriores.** Cada chat es nuevo. Pegar siempre cápsula.
2. **Si DeepSeek empieza a inventar APIs**, reinicia chat con cápsula + nota explícita: "API_REFERENCE_GENERATED.md no contiene XXX, reporta STOP."
3. **Si DeepSeek se pone "creativo" con arquitectura**, reinicia chat. La cápsula lo recuerda de las reglas.
4. **Cierra chats al terminar cada sprint**. Evita el bug de `reasoning_content` (ver WORKFLOW.md sección 9.1).

---

**Fin del documento.**
