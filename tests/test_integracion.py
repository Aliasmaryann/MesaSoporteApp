import sys
import unittest
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import database as db

class TestDobleAplicacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.inicializar()

    def test_catalogos(self):
        c = db.catalogos()
        self.assertGreaterEqual(len(c["solicitantes"]), 1)
        self.assertGreaterEqual(len(c["responsables"]), 1)

    def test_crear_y_gestionar_ticket(self):
        ticket_id = db.crear_ticket(
            1,
            "Ticket de prueba",
            "Prueba de integración entre usuario y equipo TI.",
            1,
            3
        )
        ticket = db.obtener_ticket(ticket_id)
        self.assertEqual(ticket["estado"], "Nuevo")

        db.asignar_responsable(ticket_id, 6)
        ticket = db.obtener_ticket(ticket_id)
        self.assertEqual(ticket["responsable"], "Ankatu Sanchez")

        db.cambiar_estado(ticket_id, "En proceso")
        ticket = db.obtener_ticket(ticket_id)
        self.assertEqual(ticket["estado"], "En proceso")

        hist = db.historial(ticket_id)
        self.assertGreaterEqual(len(hist), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
