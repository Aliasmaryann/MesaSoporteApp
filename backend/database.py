from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "mesa_soporte.db"
SCHEMA_PATH = ROOT / "database" / "schema.sql"
SEED_PATH = ROOT / "database" / "seed.sql"

TRANSICIONES_VALIDAS = {
    "Nuevo": ["En proceso"],
    "En proceso": ["Resuelto"],
    "Resuelto": ["En proceso", "Cerrado"],
    "Cerrado": [],
}

def conectar():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def inicializar():
    with conectar() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executescript(SEED_PATH.read_text(encoding="utf-8"))

def catalogos():
    with conectar() as conn:
        solicitantes = conn.execute("""
            SELECT u.id, u.nombre, u.correo
            FROM usuarios u
            JOIN roles r ON r.id=u.rol_id
            WHERE u.activo=1 AND r.nombre='Solicitante'
            ORDER BY u.nombre
        """).fetchall()

        responsables = conn.execute("""
            SELECT u.id, u.nombre, u.correo
            FROM usuarios u
            JOIN roles r ON r.id=u.rol_id
            WHERE u.activo=1 AND r.nombre='Responsable TI'
            ORDER BY u.nombre
        """).fetchall()

        categorias = conn.execute(
            "SELECT id,nombre FROM categorias WHERE activa=1 ORDER BY nombre"
        ).fetchall()
        prioridades = conn.execute(
            "SELECT id,nombre FROM prioridades ORDER BY orden"
        ).fetchall()
        estados = conn.execute(
            "SELECT id,nombre FROM estados ORDER BY orden"
        ).fetchall()

    return {
        "solicitantes": [dict(x) for x in solicitantes],
        "responsables": [dict(x) for x in responsables],
        "categorias": [dict(x) for x in categorias],
        "prioridades": [dict(x) for x in prioridades],
        "estados": [dict(x) for x in estados],
    }

def crear_ticket(solicitante_id, titulo, descripcion, categoria_id, prioridad_id):
    titulo = (titulo or "").strip()
    descripcion = (descripcion or "").strip()

    if not solicitante_id:
        raise ValueError("Debes seleccionar un solicitante.")
    if not titulo:
        raise ValueError("El título es obligatorio.")
    if not descripcion:
        raise ValueError("La descripción es obligatoria.")
    if not categoria_id:
        raise ValueError("Debes seleccionar una categoría.")
    if not prioridad_id:
        raise ValueError("Debes seleccionar una prioridad.")

    with conectar() as conn:
        estado = conn.execute(
            "SELECT id FROM estados WHERE nombre='Nuevo'"
        ).fetchone()

        cur = conn.execute("""
            INSERT INTO tickets
            (titulo, descripcion, solicitante_id, categoria_id, prioridad_id, estado_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titulo, descripcion, solicitante_id, categoria_id, prioridad_id, estado["id"]))

        return cur.lastrowid

def tickets_de_solicitante(solicitante_id):
    with conectar() as conn:
        rows = conn.execute("""
            SELECT
                t.id,
                t.titulo,
                t.fecha_creacion,
                c.nombre AS categoria,
                p.nombre AS prioridad,
                e.nombre AS estado,
                COALESCE(r.nombre,'Sin asignar') AS responsable
            FROM tickets t
            JOIN categorias c ON c.id=t.categoria_id
            JOIN prioridades p ON p.id=t.prioridad_id
            JOIN estados e ON e.id=t.estado_id
            LEFT JOIN usuarios r ON r.id=t.responsable_id
            WHERE t.solicitante_id=?
            ORDER BY t.id DESC
        """, (solicitante_id,)).fetchall()
    return [dict(x) for x in rows]

def listar_tickets():
    with conectar() as conn:
        rows = conn.execute("""
            SELECT
                t.id,
                t.titulo,
                t.descripcion,
                t.fecha_creacion,
                c.nombre AS categoria,
                p.nombre AS prioridad,
                e.nombre AS estado,
                COALESCE(r.nombre,'Sin asignar') AS responsable,
                s.nombre AS solicitante
            FROM tickets t
            JOIN categorias c ON c.id=t.categoria_id
            JOIN prioridades p ON p.id=t.prioridad_id
            JOIN estados e ON e.id=t.estado_id
            JOIN usuarios s ON s.id=t.solicitante_id
            LEFT JOIN usuarios r ON r.id=t.responsable_id
            ORDER BY t.id DESC
        """).fetchall()
    return [dict(x) for x in rows]

def obtener_ticket(ticket_id):
    with conectar() as conn:
        row = conn.execute("""
            SELECT
                t.id,
                t.titulo,
                t.descripcion,
                t.fecha_creacion,
                t.fecha_cierre,
                t.solicitante_id,
                s.nombre AS solicitante,
                t.responsable_id,
                COALESCE(r.nombre,'Sin asignar') AS responsable,
                t.categoria_id,
                c.nombre AS categoria,
                t.prioridad_id,
                p.nombre AS prioridad,
                t.estado_id,
                e.nombre AS estado
            FROM tickets t
            JOIN usuarios s ON s.id=t.solicitante_id
            LEFT JOIN usuarios r ON r.id=t.responsable_id
            JOIN categorias c ON c.id=t.categoria_id
            JOIN prioridades p ON p.id=t.prioridad_id
            JOIN estados e ON e.id=t.estado_id
            WHERE t.id=?
        """, (ticket_id,)).fetchone()
    return dict(row) if row else None

def historial(ticket_id):
    with conectar() as conn:
        rows = conn.execute("""
            SELECT tipo_cambio,valor_anterior,valor_nuevo,fecha_cambio
            FROM historial_cambios
            WHERE ticket_id=?
            ORDER BY id DESC
        """, (ticket_id,)).fetchall()
    return [dict(x) for x in rows]

def asignar_responsable(ticket_id, responsable_id):
    with conectar() as conn:
        ticket = conn.execute("""
            SELECT t.responsable_id,e.nombre estado
            FROM tickets t
            JOIN estados e ON e.id=t.estado_id
            WHERE t.id=?
        """, (ticket_id,)).fetchone()

        if not ticket:
            raise ValueError("Ticket no encontrado.")
        if ticket["estado"] == "Cerrado":
            raise ValueError("Un ticket cerrado no se puede modificar.")

        nuevo = conn.execute("""
            SELECT u.nombre
            FROM usuarios u
            JOIN roles r ON r.id=u.rol_id
            WHERE u.id=? AND u.activo=1 AND r.nombre='Responsable TI'
        """, (responsable_id,)).fetchone()

        if not nuevo:
            raise ValueError("Responsable TI no válido.")

        anterior = "Sin asignar"
        if ticket["responsable_id"]:
            row = conn.execute(
                "SELECT nombre FROM usuarios WHERE id=?",
                (ticket["responsable_id"],)
            ).fetchone()
            if row:
                anterior = row["nombre"]

        conn.execute(
            "UPDATE tickets SET responsable_id=? WHERE id=?",
            (responsable_id, ticket_id)
        )

        if anterior != nuevo["nombre"]:
            conn.execute("""
                INSERT INTO historial_cambios
                (ticket_id,tipo_cambio,valor_anterior,valor_nuevo)
                VALUES (?, 'RESPONSABLE', ?, ?)
            """, (ticket_id, anterior, nuevo["nombre"]))

def cambiar_estado(ticket_id, nuevo_estado):
    with conectar() as conn:
        ticket = conn.execute("""
            SELECT e.nombre AS estado
            FROM tickets t
            JOIN estados e ON e.id=t.estado_id
            WHERE t.id=?
        """, (ticket_id,)).fetchone()

        if not ticket:
            raise ValueError("Ticket no encontrado.")

        actual = ticket["estado"]

        if actual == nuevo_estado:
            return

        permitidos = TRANSICIONES_VALIDAS.get(actual, [])
        if nuevo_estado not in permitidos:
            raise ValueError(
                f"No se permite cambiar de '{actual}' a '{nuevo_estado}'."
            )

        estado = conn.execute(
            "SELECT id FROM estados WHERE nombre=?",
            (nuevo_estado,)
        ).fetchone()

        if not estado:
            raise ValueError("Estado no válido.")

        if nuevo_estado == "Cerrado":
            conn.execute("""
                UPDATE tickets
                SET estado_id=?, fecha_cierre=datetime('now','localtime')
                WHERE id=?
            """, (estado["id"], ticket_id))
        else:
            conn.execute(
                "UPDATE tickets SET estado_id=? WHERE id=?",
                (estado["id"], ticket_id)
            )

        conn.execute("""
            INSERT INTO historial_cambios
            (ticket_id,tipo_cambio,valor_anterior,valor_nuevo)
            VALUES (?, 'ESTADO', ?, ?)
        """, (ticket_id, actual, nuevo_estado))

def resumen():
    with conectar() as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS total FROM tickets"
        ).fetchone()["total"]

        rows = conn.execute("""
            SELECT e.nombre, COUNT(t.id) AS cantidad
            FROM estados e
            LEFT JOIN tickets t ON t.estado_id=e.id
            GROUP BY e.id,e.nombre,e.orden
            ORDER BY e.orden
        """).fetchall()

    return total, {r["nombre"]: r["cantidad"] for r in rows}
