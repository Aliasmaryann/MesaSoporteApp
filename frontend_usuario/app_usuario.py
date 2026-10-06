import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import database as db

BG = "#0f172a"
PANEL = "#1e293b"
CARD = "#334155"
TEXT = "#f8fafc"
MUTED = "#cbd5e1"
ACCENT = "#38bdf8"
GREEN = "#22c55e"

class UsuarioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        db.inicializar()
        self.catalogos = db.catalogos()

        self.title("Mesa de Soporte TI - Usuario")
        self.geometry("920x700")
        self.minsize(820, 620)
        self.configure(bg=BG)

        self.solicitantes = {
            u["nombre"]: u["id"] for u in self.catalogos["solicitantes"]
        }
        self.categorias = {
            x["nombre"]: x["id"] for x in self.catalogos["categorias"]
        }
        self.prioridades = {
            x["nombre"]: x["id"] for x in self.catalogos["prioridades"]
        }

        self.configurar_estilo()
        self.construir()

    def configurar_estilo(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=34, borderwidth=0)
        style.configure("Treeview.Heading", background=CARD, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#0369a1")],
                  foreground=[("selected", "#ffffff")])

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
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief="flat", padx=16, pady=9, cursor="hand2"
        )

    def construir(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 14))

        self.label(header, "Mesa de Soporte TI", 22, True, bg=BG).pack(anchor="w")
        self.label(
            header,
            "Portal de usuario · Crear y consultar tickets",
            10, False, MUTED, BG
        ).pack(anchor="w", pady=(3, 0))

        card = tk.Frame(self, bg=PANEL, padx=22, pady=20)
        card.pack(fill="x", padx=28, pady=(0, 18))

        self.label(card, "Crear nueva solicitud", 15, True, bg=PANEL).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        self.cb_solicitante = self.combo(
            card, "Solicitante *", list(self.solicitantes), 1
        )

        self.ent_titulo = self.entry(card, "Título *", 2)

        self.label(card, "Descripción *", 10, True, bg=PANEL).grid(
            row=3, column=0, sticky="w", pady=(10, 4)
        )
        self.txt_descripcion = tk.Text(
            card, height=5, bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Segoe UI", 10), padx=10, pady=8
        )
        self.txt_descripcion.grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(0, 4)
        )

        self.cb_categoria = self.combo(
            card, "Categoría *", list(self.categorias), 5
        )
        self.cb_prioridad = self.combo(
            card, "Prioridad *", list(self.prioridades), 6
        )

        self.button(
            card, "Enviar ticket", self.enviar_ticket, primary=True
        ).grid(row=7, column=1, sticky="e", pady=(18, 0))

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        bottom = tk.Frame(self, bg=PANEL, padx=18, pady=16)
        bottom.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        topbar = tk.Frame(bottom, bg=PANEL)
        topbar.pack(fill="x")

        self.label(
            topbar, "Mis tickets", 14, True, bg=PANEL
        ).pack(side="left")

        self.button(
            topbar, "Actualizar", self.cargar_mis_tickets
        ).pack(side="right")

        cols = ("id", "titulo", "prioridad", "estado", "responsable", "fecha")
        self.tree = ttk.Treeview(bottom, columns=cols, show="headings")

        headers = {
            "id": "ID",
            "titulo": "Título",
            "prioridad": "Prioridad",
            "estado": "Estado",
            "responsable": "Responsable",
            "fecha": "Fecha",
        }
        widths = {
            "id": 60,
            "titulo": 250,
            "prioridad": 100,
            "estado": 120,
            "responsable": 170,
            "fecha": 150,
        }

        for col in cols:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="w")

        self.tree.pack(fill="both", expand=True, pady=(12, 0))

        self.cb_solicitante.bind(
            "<<ComboboxSelected>>", lambda e: self.cargar_mis_tickets()
        )

    def entry(self, parent, text, row):
        self.label(parent, text, 10, True, bg=PANEL).grid(
            row=row, column=0, sticky="w", pady=(10, 4)
        )
        ent = tk.Entry(
            parent, bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Segoe UI", 10)
        )
        ent.grid(row=row, column=1, sticky="ew", padx=(16, 0), pady=(10, 4), ipady=8)
        return ent

    def combo(self, parent, text, values, row):
        self.label(parent, text, 10, True, bg=PANEL).grid(
            row=row, column=0, sticky="w", pady=(10, 4)
        )
        cb = ttk.Combobox(parent, values=values, state="readonly")
        cb.grid(row=row, column=1, sticky="ew", padx=(16, 0), pady=(10, 4), ipady=4)
        return cb

    def enviar_ticket(self):
        try:
            solicitante_id = self.solicitantes.get(self.cb_solicitante.get())
            categoria_id = self.categorias.get(self.cb_categoria.get())
            prioridad_id = self.prioridades.get(self.cb_prioridad.get())

            ticket_id = db.crear_ticket(
                solicitante_id,
                self.ent_titulo.get(),
                self.txt_descripcion.get("1.0", "end").strip(),
                categoria_id,
                prioridad_id
            )

            messagebox.showinfo(
                "Ticket enviado",
                f"Tu solicitud fue registrada correctamente.\n\nID del ticket: #{ticket_id}"
            )

            self.ent_titulo.delete(0, "end")
            self.txt_descripcion.delete("1.0", "end")
            self.cb_categoria.set("")
            self.cb_prioridad.set("")
            self.cargar_mis_tickets()

        except Exception as e:
            messagebox.showerror("No se pudo enviar", str(e))

    def cargar_mis_tickets(self):
        for x in self.tree.get_children():
            self.tree.delete(x)

        solicitante_id = self.solicitantes.get(self.cb_solicitante.get())
        if not solicitante_id:
            return

        tickets = db.tickets_de_solicitante(solicitante_id)
        for t in tickets:
            self.tree.insert("", "end", values=(
                f"#{t['id']}",
                t["titulo"],
                t["prioridad"],
                t["estado"],
                t["responsable"],
                t["fecha_creacion"],
            ))

if __name__ == "__main__":
    UsuarioApp().mainloop()
