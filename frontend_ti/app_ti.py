import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import database as db

BG = "#0b1220"
SIDEBAR = "#111827"
PANEL = "#172033"
CARD = "#1f2a3d"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"

class EquipoTIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        db.inicializar()
        self.catalogos = db.catalogos()

        self.title("Mesa de Soporte TI - Equipo TI")
        self.geometry("1260x760")
        self.minsize(1050, 650)
        self.configure(bg=BG)

        self.responsables = {
            u["nombre"]: u["id"] for u in self.catalogos["responsables"]
        }

        self.configurar_estilos()
        self.construir()
        self.actualizar()

        self.after(5000, self.auto_actualizar)

    def configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=CARD,
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#0369a1")],
            foreground=[("selected", "#ffffff")]
        )

    def label(self, parent, text, size=10, bold=False, fg=TEXT, bg=None):
        return tk.Label(
            parent, text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            fg=fg, bg=bg or parent.cget("bg")
        )

    def button(self, parent, text, command, primary=False):
        bg = ACCENT if primary else CARD
        fg = "#06202b" if primary else TEXT
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 10, "bold"),
            bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg,
            relief="flat", padx=16, pady=9, cursor="hand2"
        )

    def construir(self):
        sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.label(
            sidebar, "Mesa de\nSoporte TI", 20, True, bg=SIDEBAR
        ).pack(anchor="w", padx=22, pady=(28, 8))

        self.label(
            sidebar, "Panel del equipo TI", 10, False, MUTED, SIDEBAR
        ).pack(anchor="w", padx=22, pady=(0, 30))

        self.button(
            sidebar, "Actualizar tickets", self.actualizar, primary=True
        ).pack(fill="x", padx=18, pady=5)

        self.button(
            sidebar, "Ver detalle", self.abrir_detalle
        ).pack(fill="x", padx=18, pady=5)

        self.label(
            sidebar,
            "La aplicación revisa\nnuevos tickets cada\n5 segundos.",
            9, False, MUTED, SIDEBAR
        ).pack(side="bottom", anchor="w", padx=22, pady=24)

        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 12))

        self.label(
            header, "Panel de atención TI", 22, True, bg=BG
        ).pack(side="left")

        self.label(
            header, "Tickets compartidos en SQLite", 10, False, MUTED, BG
        ).pack(side="right")

        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x", padx=28, pady=(0, 14))

        self.card_labels = {}
        for key in ["Total", "Nuevo", "En proceso", "Resuelto", "Cerrado"]:
            card = tk.Frame(cards, bg=PANEL, padx=16, pady=12)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))

            self.label(
                card, key, 9, False, MUTED, PANEL
            ).pack(anchor="w")

            value = self.label(
                card, "0", 20, True, TEXT, PANEL
            )
            value.pack(anchor="w")
            self.card_labels[key] = value

        body = tk.Frame(main, bg=PANEL)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        bar = tk.Frame(body, bg=PANEL)
        bar.pack(fill="x", padx=16, pady=14)

        self.label(
            bar, "Solicitudes recibidas", 14, True, bg=PANEL
        ).pack(side="left")

        self.button(
            bar, "Abrir ticket", self.abrir_detalle, primary=True
        ).pack(side="right")

        cols = ("id", "solicitante", "titulo", "prioridad", "estado", "responsable", "fecha")
        self.tree = ttk.Treeview(body, columns=cols, show="headings")

        headers = {
            "id": "ID",
            "solicitante": "Solicitante",
            "titulo": "Título",
            "prioridad": "Prioridad",
            "estado": "Estado",
            "responsable": "Responsable",
            "fecha": "Fecha",
        }
        widths = {
            "id": 60,
            "solicitante": 150,
            "titulo": 250,
            "prioridad": 100,
            "estado": 120,
            "responsable": 160,
            "fecha": 150,
        }

        for col in cols:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="w")

        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.bind("<Double-1>", lambda e: self.abrir_detalle())

    def actualizar(self):
        seleccion = self.tree.selection()
        actual_id = seleccion[0] if seleccion else None

        for x in self.tree.get_children():
            self.tree.delete(x)

        tickets = db.listar_tickets()
        for t in tickets:
            self.tree.insert("", "end", iid=str(t["id"]), values=(
                f"#{t['id']}",
                t["solicitante"],
                t["titulo"],
                t["prioridad"],
                t["estado"],
                t["responsable"],
                t["fecha_creacion"],
            ))

        if actual_id and self.tree.exists(actual_id):
            self.tree.selection_set(actual_id)

        total, resumen = db.resumen()
        self.card_labels["Total"].config(text=str(total))
        for estado in ["Nuevo", "En proceso", "Resuelto", "Cerrado"]:
            self.card_labels[estado].config(text=str(resumen.get(estado, 0)))

    def auto_actualizar(self):
        try:
            self.actualizar()
        finally:
            self.after(5000, self.auto_actualizar)

    def abrir_detalle(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo(
                "Equipo TI", "Selecciona un ticket del listado."
            )
            return
        DetalleTicket(self, int(sel[0]))

class DetalleTicket(tk.Toplevel):
    def __init__(self, app, ticket_id):
        super().__init__(app)
        self.app = app
        self.ticket_id = ticket_id

        self.title(f"Ticket #{ticket_id}")
        self.geometry("780x700")
        self.configure(bg=BG)
        self.transient(app)

        self.panel = tk.Frame(self, bg=PANEL, padx=24, pady=22)
        self.panel.pack(fill="both", expand=True, padx=20, pady=20)

        self.cargar()

    def limpiar(self):
        for w in self.panel.winfo_children():
            w.destroy()

    def cargar(self):
        self.limpiar()
        t = db.obtener_ticket(self.ticket_id)

        if not t:
            messagebox.showerror("Error", "Ticket no encontrado.")
            self.destroy()
            return

        top = tk.Frame(self.panel, bg=PANEL)
        top.pack(fill="x")

        self.app.label(
            top, f"Ticket #{t['id']}: {t['titulo']}", 17, True, bg=PANEL
        ).pack(side="left")

        self.app.label(
            top, t["estado"], 10, True, ACCENT, PANEL
        ).pack(side="right")

        for k, v in [
            ("Solicitante", t["solicitante"]),
            ("Creado", t["fecha_creacion"]),
            ("Categoría", t["categoria"]),
            ("Prioridad", t["prioridad"]),
            ("Responsable", t["responsable"]),
        ]:
            row = tk.Frame(self.panel, bg=PANEL)
            row.pack(fill="x", pady=3)

            self.app.label(
                row, k + ":", 10, True, MUTED, PANEL
            ).pack(side="left")

            self.app.label(
                row, str(v), 10, False, TEXT, PANEL
            ).pack(side="left", padx=(8, 0))

        self.app.label(
            self.panel, "Descripción", 11, True, bg=PANEL
        ).pack(anchor="w", pady=(16, 5))

        tk.Message(
            self.panel,
            text=t["descripcion"],
            bg=CARD, fg=TEXT,
            font=("Segoe UI", 10),
            width=690, padx=12, pady=10
        ).pack(fill="x")

        if t["estado"] != "Cerrado":
            self.app.label(
                self.panel, "Asignar responsable", 10, True, bg=PANEL
            ).pack(anchor="w", pady=(18, 5))

            self.cb_resp = ttk.Combobox(
                self.panel,
                values=list(self.app.responsables),
                state="readonly"
            )

            if t["responsable"] in self.app.responsables:
                self.cb_resp.set(t["responsable"])

            self.cb_resp.pack(fill="x", ipady=5)

            controles = tk.Frame(self.panel, bg=PANEL)
            controles.pack(fill="x", pady=(10, 0))

            self.app.button(
                controles, "Asignar responsable", self.asignar
            ).pack(side="left")

            permitidos = db.TRANSICIONES_VALIDAS.get(t["estado"], [])
            if permitidos:
                self.cb_estado = ttk.Combobox(
                    controles,
                    values=permitidos,
                    state="readonly",
                    width=20
                )
                self.cb_estado.pack(side="left", padx=(18, 8), ipady=5)

                self.app.button(
                    controles, "Cambiar estado", self.cambiar_estado, primary=True
                ).pack(side="left")

        else:
            self.app.label(
                self.panel,
                "Ticket cerrado. No admite nuevas modificaciones.",
                10, True, MUTED, PANEL
            ).pack(anchor="w", pady=(18, 0))

        self.app.label(
            self.panel, "Historial de cambios", 12, True, bg=PANEL
        ).pack(anchor="w", pady=(22, 8))

        hist = tk.Frame(self.panel, bg=CARD)
        hist.pack(fill="both", expand=True)

        historial = db.historial(self.ticket_id)

        if not historial:
            self.app.label(
                hist, "Sin cambios registrados.", 10, False, MUTED, CARD
            ).pack(anchor="w", padx=12, pady=12)
        else:
            for h in historial:
                texto = (
                    f"{h['fecha_cambio']} · {h['tipo_cambio']}: "
                    f"{h['valor_anterior']} → {h['valor_nuevo']}"
                )
                self.app.label(
                    hist, texto, 10, False, TEXT, CARD
                ).pack(anchor="w", padx=12, pady=5)

    def asignar(self):
        nombre = self.cb_resp.get()
        if not nombre:
            messagebox.showwarning(
                "Responsable", "Selecciona un responsable TI."
            )
            return

        try:
            db.asignar_responsable(
                self.ticket_id,
                self.app.responsables[nombre]
            )
            self.app.actualizar()
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cambiar_estado(self):
        nuevo = self.cb_estado.get()
        if not nuevo:
            messagebox.showwarning(
                "Estado", "Selecciona el nuevo estado."
            )
            return

        try:
            db.cambiar_estado(self.ticket_id, nuevo)
            self.app.actualizar()
            self.cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    EquipoTIApp().mainloop()
