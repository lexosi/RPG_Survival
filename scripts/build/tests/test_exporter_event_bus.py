"""
Test estático del exporter event_bus_device generado.

Valida que `02_export_constants_to_verse.py::export_event_bus()` emite
`Content/Verse/Generated/EventBusDevice.verse` con el contrato semántico
esperado: 9 propiedades event con nombres + tipos payload + visibility correctos,
class declaration intacta, idempotencia.

NO valida formato cosmético (header comments, spacing) — eso es ortogonal.
NO valida compilación Verse — eso es F-C-3a runtime test in-session.
NO valida schema catalog — eso es 01_validate_jsons.py.

Ejecutar:
    cd F:\\Noobs\\RPG_Survival
    python -m unittest scripts.build.tests.test_exporter_event_bus

Asociado a SPR-009. Sub-paso F-C-3b.
"""
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

# Anchor relativo al repo root (test vive en scripts/build/tests/).
REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATED_FILE = REPO_ROOT / "Content" / "Verse" / "Generated" / "EventBusDevice.verse"
FIXTURE_FILE = Path(__file__).parent / "fixtures" / "event_bus_expected_contract.json"
EXPORTER_SCRIPT = REPO_ROOT / "scripts" / "build" / "02_export_constants_to_verse.py"


class TestExporterEventBus(unittest.TestCase):
    """Tests contractuales del archivo Generated/EventBusDevice.verse."""

    @classmethod
    def setUpClass(cls):
        """Carga fixture + archivo generado una vez por test class."""
        if not FIXTURE_FILE.exists():
            raise FileNotFoundError(f"Fixture no encontrado: {FIXTURE_FILE}")
        if not GENERATED_FILE.exists():
            raise FileNotFoundError(
                f"Generated file no encontrado: {GENERATED_FILE}. "
                f"Ejecuta primero el exporter: python scripts/build/02_export_constants_to_verse.py"
            )
        cls.fixture = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
        cls.generated_text = GENERATED_FILE.read_text(encoding="utf-8")

    def test_class_declaration_present(self):
        """Class declaration `event_bus_device<public> := class<concrete>(creative_device):` debe existir."""
        expected = self.fixture["_class_declaration"]
        self.assertIn(
            expected,
            self.generated_text,
            f"Class declaration faltante o alterada. Esperado: '{expected}'",
        )

    def test_expected_event_count(self):
        """Número de eventos generados debe coincidir con contrato."""
        expected_count = len(self.fixture["expected_events"])
        # Match propiedades event(...) — patrón: `Name<public>:event(payload) = event(payload){}`
        pattern = re.compile(r"^\s*\w+<public>\s*:\s*event\(", re.MULTILINE)
        actual_count = len(pattern.findall(self.generated_text))
        self.assertEqual(
            actual_count,
            expected_count,
            f"Esperados {expected_count} eventos, encontrados {actual_count}",
        )

    def test_each_event_present_with_correct_signature(self):
        """Cada evento del contrato debe estar presente con nombre + payload + visibility correctos."""
        for event in self.fixture["expected_events"]:
            name = event["name"]
            payload_type = event["payload_type"]
            visibility = event["visibility"]
            # Patrón completo: `Name<public>:event(payload_type) = event(payload_type){}`
            pattern = re.compile(
                rf"\b{re.escape(name)}<{re.escape(visibility)}>\s*:\s*event\({re.escape(payload_type)}\)\s*=\s*event\({re.escape(payload_type)}\)\s*\{{\s*\}}",
                re.MULTILINE,
            )
            self.assertRegex(
                self.generated_text,
                pattern,
                f"Evento '{name}' con payload '{payload_type}' visibility '{visibility}' "
                f"no encontrado o malformado en {GENERATED_FILE.name}",
            )

    def test_no_unexpected_events(self):
        """No debe haber eventos generados fuera del contrato (detecta drift positivo)."""
        expected_names = {e["name"] for e in self.fixture["expected_events"]}
        # Extrae nombres de eventos generados.
        pattern = re.compile(r"^\s*(\w+)<public>\s*:\s*event\(", re.MULTILINE)
        actual_names = set(pattern.findall(self.generated_text))
        unexpected = actual_names - expected_names
        self.assertFalse(
            unexpected,
            f"Eventos no declarados en contrato: {unexpected}. "
            f"Si son legítimos, actualiza fixture event_bus_expected_contract.json.",
        )

    def test_idempotency(self):
        """Ejecutar exporter 2× consecutivas produce mismo hash SHA256 (idempotencia)."""
        if not EXPORTER_SCRIPT.exists():
            self.skipTest(f"Exporter no encontrado: {EXPORTER_SCRIPT}")

        # Hash inicial.
        hash1 = hashlib.sha256(GENERATED_FILE.read_bytes()).hexdigest()

        # Re-ejecuta exporter.
        result = subprocess.run(
            [sys.executable, str(EXPORTER_SCRIPT)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            self.fail(
                f"Exporter falló (returncode {result.returncode}).\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

        # Hash post-re-ejecución.
        hash2 = hashlib.sha256(GENERATED_FILE.read_bytes()).hexdigest()

        self.assertEqual(
            hash1,
            hash2,
            f"Exporter NO idempotente. Hash pre: {hash1}, hash post: {hash2}. "
            f"Causa probable: orden no determinista en iteración (dict, set), timestamp en header, etc.",
        )


if __name__ == "__main__":
    unittest.main()
