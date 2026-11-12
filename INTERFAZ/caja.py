import tkinter as tk
from tkinter import ttk, messagebox
from .datos_ui import caja, guardar_caja, fecha_hora, dinero

class CajaFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Page.TFrame", padding=22)
        ttk.Label(self, text="Caja", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Controla la apertura y el cierre de caja.",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 18))

        self.estado = ttk.Label(self, text="", style="Section.TLabel")
        self.estado.pack(anchor="w", pady=(0, 12))

        panel = ttk.Frame(self, style="Page.TFrame")
        panel.pack(anchor="w", fill="x")
        ttk.Label(panel, text="Monto inicial / monto de cierre").grid(row=0, column=0, sticky="w")
        self.monto = ttk.Entry(panel, width=25)
        self.monto.grid(row=1, column=0, padx=(0, 10), pady=8, ipady=6)
        ttk.Button(panel, text="Abrir caja", style="Accent.TButton",
                   command=self.abrir).grid(row=1, column=1, padx=4)
        ttk.Button(panel, text="Cerrar caja", style="Danger.TButton",
                   command=self.cerrar).grid(row=1, column=2, padx=4)

        ttk.Label(self, text="Historial de sesiones", style="Section.TLabel").pack(anchor="w", pady=(25, 10))
        cols = ("apertura", "monto_inicial", "cierre", "monto_final", "estado")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=13)
        titulos = ("Apertura", "Monto inicial", "Cierre", "Monto final", "Estado")
        for c, t in zip(cols, titulos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=160, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.actualizar()

    def _sesiones(self):
        return caja().get("sesiones", [])

    def actualizar(self):
        sesiones = self._sesiones()
        abierta = next((s for s in reversed(sesiones) if s.get("estado") == "Abierta"), None)
        self.estado.configure(text="● Caja abierta" if abierta else "● Caja cerrada")
        self.estado.configure(foreground="#22c783" if abierta else "#f08a83")
        self.tabla.delete(*self.tabla.get_children())
        for s in reversed(sesiones):
            self.tabla.insert("", "end", values=(
                s.get("apertura", ""), dinero(s.get("monto_inicial", 0)),
                s.get("cierre", "—"), dinero(s.get("monto_final", 0)), s.get("estado", "")
            ))

    def abrir(self):
        try:
            monto = float(self.monto.get())
            if monto < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Monto inválido", "Escribe un monto válido.")
            return
        datos = caja()
        if any(s.get("estado") == "Abierta" for s in datos["sesiones"]):
            messagebox.showwarning("Caja abierta", "Ya existe una sesión de caja abierta.")
            return
        datos["sesiones"].append({
            "apertura": fecha_hora(), "monto_inicial": monto,
            "cierre": None, "monto_final": 0, "estado": "Abierta"
        })
        guardar_caja(datos)
        self.monto.delete(0, "end")
        self.actualizar()

    def cerrar(self):
        try:
            monto = float(self.monto.get())
            if monto < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Monto inválido", "Escribe el monto contado al cerrar.")
            return
        datos = caja()
        abierta = next((s for s in reversed(datos["sesiones"]) if s.get("estado") == "Abierta"), None)
        if not abierta:
            messagebox.showwarning("Caja cerrada", "No hay una sesión abierta.")
            return
        abierta["cierre"] = fecha_hora()
        abierta["monto_final"] = monto
        abierta["estado"] = "Cerrada"
        guardar_caja(datos)
        self.monto.delete(0, "end")
        self.actualizar()
