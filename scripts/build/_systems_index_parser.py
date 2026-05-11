#!/usr/bin/env python3
"""
_systems_index_parser.py — parser SYSTEMS_INDEX.md → mapping path→fase.

Producido por F-CLEAN-P2a (2026-05-11). Consumido por 00_validate_structure.py
via flag --phase=Fn para filtrar MISSING por fase del sistema asociado.

Underscore prefix marca "internal use by validator" — NO importar desde
scripts gameplay.

Spec: ver docs/CHANGELOG.md entrada F-CLEAN-P2a + docs/SYSTEMS_INDEX.md
§2.1-§2.11 (single source of truth para path→fase).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Header markdown estándar de subtablas SYSTEMS_INDEX §2.x:
# | ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |
# Tras split por "|" e ignorar primer y último vacío:
#   index 0 → ID, 1 → Sistema, 2 → Cat, 3 → Fase, 4 → JSON, 5 → Verse, ...
# Spec mantiene "índice 4 contando leading |" (raw split); para claridad uso
# strip + descarte de extremos vacíos primero, luego índices semánticos.

_SUBTABLE_HEADER_RE = re.compile(r"^### 2\.\d+ ")
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
_FASE_RE = re.compile(r"^F(\d+)")
_BACKTICK_RE = re.compile(r"`([^`]+)`")


def _extract_paths_from_cell(cell: str) -> list[str]:
    """Captura todos los paths backtick-quoted en una celda.

    Cells como `(parte de Inventory)`, `(TBD)`, `—`, `(validado en Python)`
    no contienen backticks → devuelven lista vacía. Cells con `path ⚠️`
    capturan solo el path (el marker queda fuera de los backticks).
    """
    return _BACKTICK_RE.findall(cell)


def _parse_phase(cell: str, row_context: str) -> str:
    """Extrae fase canónica del valor en columna Fase.

    Acepta: "F0", "F1", "F1 ⚙️", "F4 → F5", "F4 → F5 ⚙️".
    Devuelve "Fn" donde n es el primer dígito tras F (la fase donde entra
    primero, no donde escala).

    Raises:
        ValueError: si el cell no matchea formato Fn.
    """
    stripped = cell.strip()
    m = _FASE_RE.match(stripped)
    if m is None:
        raise ValueError(
            f"Formato de Fase no reconocible: '{stripped}' (esperado 'Fn' o 'Fn ⚙️' o "
            f"'Fn → Fm'). Contexto: {row_context}"
        )
    return f"F{m.group(1)}"


def parse_systems_index(md_path: Path) -> dict[str, str]:
    """Parsea SYSTEMS_INDEX.md §2.1-§2.11 → dict {relative_path: fase}.

    Cubre paths Verse y JSON declarados en columnas "JSON principal" y
    "Verse principal". Paths Verse se prefijan con `Content/Verse/`.

    Returns:
        dict mapping relative path → fase string ("F0", "F1", ..., "F5").
        Paths con valor "(parte de X)", "(TBD)", "(validado en Python)" no
        producen entradas (no son archivos reales).

    Raises:
        ValueError: si encuentra fila con Fase no reconocible.
        FileNotFoundError: si md_path no existe.
    """
    if not md_path.exists():
        raise FileNotFoundError(f"SYSTEMS_INDEX no encontrado: {md_path}")

    mapping: dict[str, str] = {}
    in_subtable = False
    header_seen = False

    text = md_path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _SUBTABLE_HEADER_RE.match(line):
            in_subtable = True
            header_seen = False
            continue
        if not in_subtable:
            continue
        if line.startswith("### ") or line.startswith("## "):
            in_subtable = False
            continue
        if not line.startswith("|"):
            continue
        if _SEPARATOR_RE.match(line):
            header_seen = True
            continue
        if not header_seen:
            # Header row (| ID | Sistema | ...) — skip
            continue

        # Data row
        parts = [p.strip() for p in line.split("|")]
        # parts[0] y parts[-1] son strings vacíos por leading/trailing "|"
        if len(parts) < 9:
            continue
        cells = parts[1:-1]
        if len(cells) < 6:
            continue

        row_id = cells[0]
        fase_cell = cells[3]
        json_cell = cells[4]
        verse_cell = cells[5]

        row_context = f"line {lineno} ({row_id})"
        phase = _parse_phase(fase_cell, row_context)

        for json_path in _extract_paths_from_cell(json_cell):
            _register(mapping, json_path, phase, row_context)

        for verse_path in _extract_paths_from_cell(verse_cell):
            full = f"Content/Verse/{verse_path}"
            _register(mapping, full, phase, row_context)

    return mapping


def _register(mapping: dict[str, str], path: str, phase: str, ctx: str) -> None:
    """Añade path→phase si no existe. Si duplicate con phase distinto, warning stderr."""
    existing = mapping.get(path)
    if existing is None:
        mapping[path] = phase
        return
    if existing != phase:
        print(
            f"[WARN] _systems_index_parser: path '{path}' duplicado con fases distintas "
            f"({existing} vs {phase} en {ctx}). Primera fase gana ({existing}).",
            file=sys.stderr,
        )


def get_phase_for_path(path: str, mapping: dict[str, str]) -> str | None:
    """Lookup fase para un path. Devuelve None si no está en mapping."""
    return mapping.get(path)
