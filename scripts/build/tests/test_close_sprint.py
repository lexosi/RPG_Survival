"""Tests para los 3 checks enforcement de close_sprint.py (F-CLEAN-P3).

Tests directos sobre funciones check_changelog_done, check_backlog_status,
check_systems_index_paths via monkeypatch de CHANGELOG/BACKLOG/SYSTEMS_INDEX paths.

Fixtures = strings markdown inline (no archivos en fixtures/ — los checks parsean
texto crudo, fixtures inline más legible para test simple).
"""
import sys
from pathlib import Path

import pytest

# close_sprint.py vive en scripts/tools/, tests en scripts/build/tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import close_sprint  # noqa: E402


# ─── Check 1: CHANGELOG ─────────────────────────────────────────────────────

def test_changelog_done_match_base(tmp_path, monkeypatch):
    """SPR-001 marcado [x] → PASS."""
    fix = tmp_path / "CHANGELOG.md"
    fix.write_text("- [x] SPR-001 — Setup del repo\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "CHANGELOG", fix)
    passed, msg = close_sprint.check_changelog_done("SPR-001", None)
    assert passed
    assert "OK" in msg


def test_changelog_done_unchecked(tmp_path, monkeypatch):
    """SPR-001 marcado [ ] (sin x) → FAIL con mensaje específico."""
    fix = tmp_path / "CHANGELOG.md"
    fix.write_text("- [ ] SPR-001 — Setup pendiente\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "CHANGELOG", fix)
    passed, msg = close_sprint.check_changelog_done("SPR-001", None)
    assert not passed
    assert "FAIL" in msg
    assert "SPR-001" in msg
    assert r"^- \[x\] SPR-001 —" in msg  # regex literal en error


def test_changelog_done_match_fix(tmp_path, monkeypatch):
    """SPR-010-FIX-1 marcado [x] → PASS (busca FIX-N primero)."""
    fix = tmp_path / "CHANGELOG.md"
    fix.write_text("- [x] SPR-010-FIX-1 — Hotfix x\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "CHANGELOG", fix)
    passed, msg = close_sprint.check_changelog_done("SPR-010", 1)
    assert passed
    assert "SPR-010-FIX-1" in msg


def test_changelog_done_fix_falls_back_to_base(tmp_path, monkeypatch):
    """FIX-N no encontrado pero base sí → PASS via base."""
    fix = tmp_path / "CHANGELOG.md"
    fix.write_text("- [x] SPR-010 — Admin Commands\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "CHANGELOG", fix)
    passed, msg = close_sprint.check_changelog_done("SPR-010", 1)
    assert passed
    assert "SPR-010" in msg


# ─── Check 2: BACKLOG ───────────────────────────────────────────────────────

def test_backlog_done_with_green(tmp_path, monkeypatch):
    """Fila SPR-001 con 🟢 → pass."""
    fix = tmp_path / "BACKLOG.md"
    fix.write_text(
        "| SPR-001 | Setup | core | inicial | — | TBD | 1h | 🟢 |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(close_sprint, "BACKLOG", fix)
    status, msg = close_sprint.check_backlog_status("SPR-001")
    assert status == "pass"
    assert "🟢" in msg


def test_backlog_pending_no_green(tmp_path, monkeypatch):
    """Fila SPR-001 sin 🟢 → fail."""
    fix = tmp_path / "BACKLOG.md"
    fix.write_text(
        "| SPR-001 | Setup | core | inicial | — | TBD | 1h | ⚫ |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(close_sprint, "BACKLOG", fix)
    status, msg = close_sprint.check_backlog_status("SPR-001")
    assert status == "fail"
    assert "SIN emoji 🟢" in msg


def test_backlog_not_found_warn(tmp_path, monkeypatch):
    """SPR no en backlog → warn (¿hotfix ad-hoc?)."""
    fix = tmp_path / "BACKLOG.md"
    fix.write_text("# backlog vacío\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "BACKLOG", fix)
    status, msg = close_sprint.check_backlog_status("SPR-999")
    assert status == "warn"
    assert "hotfix ad-hoc" in msg


# ─── Check 3: SYSTEMS_INDEX ─────────────────────────────────────────────────

def test_systems_index_paths_skip_no_verse():
    """Sin archivos .verse en prefijos regulados → skip."""
    status, msg = close_sprint.check_systems_index_paths([
        "docs/CHANGELOG.md",
        "scripts/tools/something.py",
    ])
    assert status == "skip"
    assert "omitido" in msg


def test_systems_index_paths_pass(tmp_path, monkeypatch):
    """Archivo .verse declarado en SYSTEMS_INDEX → pass."""
    fix = tmp_path / "SYSTEMS_INDEX.md"
    fix.write_text(
        "### 2.1 Core\n\n"
        "| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| SYS-001 | Player Stats | Core | F1 | `data/x.json` | `Systems/Player/PlayerStats.verse` | TBD | Core | ⚫ |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(close_sprint, "SYSTEMS_INDEX", fix)
    status, msg = close_sprint.check_systems_index_paths([
        "Content/Verse/Systems/Player/PlayerStats.verse",
    ])
    assert status == "pass"
    assert "1 archivo" in msg


def test_systems_index_paths_warn(tmp_path, monkeypatch):
    """Archivo .verse NO declarado → warn con listado."""
    fix = tmp_path / "SYSTEMS_INDEX.md"
    fix.write_text(
        "### 2.1 Core\n\n"
        "| ID | Sistema | Cat | Fase | JSON principal | Verse principal | Sprint | Persist | Estado |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| SYS-001 | Player Stats | Core | F1 | `data/x.json` | `Systems/Player/PlayerStats.verse` | TBD | Core | ⚫ |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(close_sprint, "SYSTEMS_INDEX", fix)
    status, msg = close_sprint.check_systems_index_paths([
        "Content/Verse/Systems/Player/PlayerStats.verse",
        "Content/Verse/Systems/Combat/CombatCore.verse",  # NO declarado
    ])
    assert status == "warn"
    assert "1 archivo" in msg
    assert "CombatCore.verse" in msg


def test_systems_index_paths_excludes_tests_generated(tmp_path, monkeypatch):
    """Tests/ y Generated/ excluidos del check positive (no requieren SYS entry)."""
    fix = tmp_path / "SYSTEMS_INDEX.md"
    fix.write_text("# empty\n", encoding="utf-8")
    monkeypatch.setattr(close_sprint, "SYSTEMS_INDEX", fix)
    status, msg = close_sprint.check_systems_index_paths([
        "Content/Verse/Tests/test_admin_smoke.verse",
        "Content/Verse/Generated/Foo_Generated.verse",
        "Content/Verse/Tests/canary/throwaway_x.verse",
    ])
    assert status == "skip"  # ningún archivo en Core/Systems/Devices
