import tkinter as tk
from tkinter import ttk
from .datos_ui import productos, dinero

class InventarioFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Page.TFrame", padding=22)
        ttk.Label(self, text="Inventario", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Consulta existencias y detecta productos por debajo del mínimo.",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 18))
        ttk.Button(self, text="Actualizar inventario", command=self.actualizar).pack(anchor="w", pady=(0, 12))
        cols = ("codigo", "nombre", "stock", "minimo", "estado", "valor")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=18)
        titulos = ("Código", "Producto", "Existencias", "Stock mínimo", "Estado", "Valor en venta")
        for c, t in zip(cols, titulos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=140, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.actualizar()

    def actualizar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in productos():
            stock = int(p.get("stock", 0) or 0)
            minimo = int(p.get("stock_minimo", 0) or 0)
            estado = "BAJO" if stock <= minimo else "Disponible"
            self.tabla.insert("", "end", values=(
                p.get("codigo", ""), p.get("nombre", ""), stock, minimo, estado,
                dinero(stock * float(p.get("precio_venta", 0) or 0))
            ), tags=("bajo",) if estado == "BAJO" else ())
        self.tabla.tag_configure("bajo", foreground="#ff7777")
