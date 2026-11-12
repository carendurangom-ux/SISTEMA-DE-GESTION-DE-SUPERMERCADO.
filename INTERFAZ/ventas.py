import tkinter as tk
from tkinter import ttk, messagebox
from .datos_ui import productos, guardar_productos, ventas, guardar_ventas, fecha_hora, dinero

class VentasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Page.TFrame", padding=22)
        ttk.Label(self, text="Ventas", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Registra una venta y descuenta automáticamente las existencias.",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 18))

        form = ttk.Frame(self, style="Page.TFrame")
        form.pack(fill="x", pady=(0, 16))
        ttk.Label(form, text="Código del producto").grid(row=0, column=0, sticky="w")
        self.codigo = ttk.Entry(form, width=22)
        self.codigo.grid(row=1, column=0, padx=(0, 12), pady=6, ipady=5)
        ttk.Label(form, text="Cantidad").grid(row=0, column=1, sticky="w")
        self.cantidad = ttk.Entry(form, width=12)
        self.cantidad.grid(row=1, column=1, padx=(0, 12), pady=6, ipady=5)
        ttk.Button(form, text="Registrar venta", style="Accent.TButton",
                   command=self.registrar).grid(row=1, column=2, pady=6)

        ttk.Label(self, text="Historial reciente", style="Section.TLabel").pack(anchor="w", pady=(4, 10))
        cols = ("fecha", "codigo", "producto", "cantidad", "total")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=13)
        for c, t, w in zip(cols, ("Fecha", "Código", "Producto", "Cantidad", "Total"), (170, 100, 210, 100, 140)):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=w, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.actualizar()

    def registrar(self):
        codigo = self.codigo.get().strip()
        try:
            cantidad = int(self.cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Cantidad inválida", "Escribe una cantidad entera mayor que cero.")
            return
        lista = productos()
        item = next((p for p in lista if str(p.get("codigo")) == codigo), None)
        if not item:
            messagebox.showerror("Producto no encontrado", "No existe un producto con ese código.")
            return
        stock = int(item.get("stock", 0) or 0)
        if cantidad > stock:
            messagebox.showwarning("Stock insuficiente", f"Solo hay {stock} unidades disponibles.")
            return
        precio = float(item.get("precio_venta", 0) or 0)
        total = precio * cantidad
        item["stock"] = stock - cantidad
        guardar_productos(lista)
        registro = {
            "fecha": fecha_hora(), "codigo": codigo,
            "producto": item.get("nombre", ""), "cantidad": cantidad,
            "precio_unitario": precio, "total": total
        }
        historial = ventas()
        historial.append(registro)
        guardar_ventas(historial)
        self.codigo.delete(0, "end")
        self.cantidad.delete(0, "end")
        self.actualizar()
        messagebox.showinfo("Venta registrada", f"Total de la venta: {dinero(total)}")

    def actualizar(self):
        self.tabla.delete(*self.tabla.get_children())
        for v in reversed(ventas()[-100:]):
            self.tabla.insert("", "end", values=(
                v.get("fecha", ""), v.get("codigo", ""), v.get("producto", ""),
                v.get("cantidad", ""), dinero(v.get("total", 0))
            ))
