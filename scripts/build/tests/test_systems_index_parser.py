"""Golden contract tests para _systems_index_parser.

Patrón fixture-based. F-CLEAN-P2a (2026-05-11).
Cubre edge cases enumerados en spec: multi-path JSON, skip cells "(parte de)"
/ "(TBD)", fase con marker ⚙️, escalación "F4 → F5", warning ⚠️ tras backtick,
fase inválida raise ValueError.
"""
import sys
from pathlib import Path

import pytest

# Imports relativos al directorio padre (scripts/build/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _systems_index_parser import parse_systems_index, get_phase_for_path, parse_truth_exemptions


@pytest.fixture
def parser_fixture():
    """Carga fixture mínimo SYSTEMS_INDEX y devuelve mapping parseado."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "systems_index_minimal.md"
    return parse_systems_index(fixture_path)


def test_parse_basic_row(parser_fixture):
    """SYS-001 PlayerStats → F1 con prefijo Content/Verse/ para verse, JSON raw."""
    assert parser_fixture.get("Content/Verse/Systems/Player/PlayerStats.verse") == "F1"
    assert parser_fixture.get("data/progression/player_stats_base.json") == "F1"


def test_parse_multi_path_json(parser_fixture):
    """SYS-002 Inventory tiene 3 JSON paths; cada uno capturado."""
    assert parser_fixture.get("data/items/equipment.json") == "F1"
    # paths relativos del split sin prefijo
    assert parser_fixture.get("resources.json") == "F1"
    assert parser_fixture.get("consumables.json") == "F1"


def test_skip_parte_de_x(parser_fixture):
    """SYS-004 Crafting Verse cell '(parte de Inventory)' no produce path. JSON sí."""
    assert parser_fixture.get("data/items/recipes.json") == "F1"
    keys = [k for k in parser_fixture.keys() if "parte de" in k]
    assert keys == []


def test_skip_tbd(parser_fixture):
    """SYS-008 Verse cell '(TBD)' no produce path."""
    keys = [k for k in parser_fixture.keys() if "TBD" in k]
    assert keys == []


def test_phase_with_marker(parser_fixture):
    """SYS-029 Gold Fase 'F1 ⚙️' → canónico 'F1'."""
    assert parser_fixture.get("data/economy/gold.json") == "F1"


def test_phase_escalation(parser_fixture):
    """SYS-042 Fase 'F4 → F5 ⚙️' → 'F4' (primera fase = donde entra)."""
    assert parser_fixture.get("Content/Verse/Systems/World/HourlyBossPortal.verse") == "F4"


def test_warning_marker_stripped(parser_fixture):
    """`data/economy/gold.json` ⚠️ → key sin ⚠️ ni espacios trailing."""
    # Key debe ser exactamente el path entre backticks, no incluir el marker.
    assert "data/economy/gold.json" in parser_fixture
    leftover = [k for k in parser_fixture.keys() if "⚠️" in k or k.endswith(" ")]
    assert leftover == []


def test_invalid_phase_raises(tmp_path):
    """Fila con Fase 'NOT_A_PHASE' → ValueError."""
    bad_fixture = tmp_path / "bad.md"
    bad_fixture.write_text(
        "### 2.1 Test\n\n"
        "| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| SYS-X | Bad | Core | NOT_A_PHASE | `x.json` | `Systems/X.verse` | TBD | — | ⚫ |\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        parse_systems_index(bad_fixture)


def test_get_phase_lookup(parser_fixture):
    """get_phase_for_path lookup correcto + None para path inexistente."""
    assert get_phase_for_path("Content/Verse/Systems/Player/PlayerStats.verse", parser_fixture) == "F1"
    assert get_phase_for_path("nonexistent/path.verse", parser_fixture) is None


def test_parse_truth_exemptions(tmp_path):
    """parse_truth_exemptions captura paths backtick de §10 + termina en siguiente sección."""
    fixture = tmp_path / "TRUTH_minimal.md"
    fixture.write_text(
        "## 9. Reglas\n\n"
        "Algun texto.\n\n"
        "---\n\n"
        "## 10. Paths exentos de SYSTEMS_INDEX\n\n"
        "Criterio: infraestructura.\n\n"
        "| Path | Categoría | Razón | Origen |\n"
        "|---|---|---|---|\n"
        "| `scripts/build/07_run_full_pipeline.py` | Build orquestador | Tooling | SPR-174 |\n"
        "| `scripts/utils/json_helpers.py` | Util lib | Helper library | sin SPR |\n\n"
        "**Criterios**: bla bla.\n\n"
        "---\n\n"
        "## 11. Otra sección\n\n"
        "| `should_not_capture.py` | algo |\n",
        encoding="utf-8",
    )
    exemptions = parse_truth_exemptions(fixture)
    assert "scripts/build/07_run_full_pipeline.py" in exemptions
    assert "scripts/utils/json_helpers.py" in exemptions
    assert "should_not_capture.py" not in exemptions


def test_absolute_path_no_prefix(tmp_path):
    """Paths con prefix repo-root (Content/, docs/, etc.) NO se prefijan con Content/Verse/."""
    fixture = tmp_path / "absolute.md"
    fixture.write_text(
        "### 2.12 Cross-cutting\n\n"
        "| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| — | Main Map | Maps | F0 | — | `Content/Maps/Main.umap` | TBD | — | ⚫ |\n"
        "| — | HOWTO | Docs | F5 | — | `docs/HOWTO_NEW_MAP.md` | SPR-203 | — | ⚫ |\n",
        encoding="utf-8",
    )
    mapping = parse_systems_index(fixture)
    # As-is, NO doble-prefix
    assert mapping.get("Content/Maps/Main.umap") == "F0"
    assert mapping.get("docs/HOWTO_NEW_MAP.md") == "F5"
    assert "Content/Verse/Content/Maps/Main.umap" not in mapping
    assert "Content/Verse/docs/HOWTO_NEW_MAP.md" not in mapping
