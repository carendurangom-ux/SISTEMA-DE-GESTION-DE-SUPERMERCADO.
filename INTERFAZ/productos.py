import tkinter as tk
from tkinter import ttk, messagebox
from NEGOCIO import inventario, ErrorNegocio
from INTERFAZ.datos_ui import TablaDatos


class VentanaInventario(tk.Toplevel):
    def __init__(self, parent, tienda):
        super().__init__(parent)
        self.tienda = tienda
        self.title("Control de Inventario")
        self.geometry("800x500")
        self.crear_widgets()
        self.actualizar_alerta()

    def crear_widgets(self):
        marco_mov = ttk.LabelFrame(self, text="Registrar Movimiento", padding="10")
        marco_mov.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(marco_mov, text="Código:").grid(row=0, column=0, sticky="w")
        self.codigo_entry = ttk.Entry(marco_mov)
        self.codigo_entry.grid(row=0, column=1, padx=5)

        ttk.Label(marco_mov, text="Tipo:").grid(row=0, column=2, sticky="w")
        self.tipo_var = tk.StringVar(value="entrada")
        ttk.Radiobutton(marco_mov, text="Entrada", variable=self.tipo_var,
                        value="entrada").grid(row=0, column=3, padx=5)
        ttk.Radiobutton(marco_mov, text="Salida", variable=self.tipo_var,
                        value="salida").grid(row=0, column=4, padx=5)

        ttk.Label(marco_mov, text="Cantidad:").grid(row=1, column=0, sticky="w", pady=5)
        self.cantidad_entry = ttk.Entry(marco_mov)
        self.cantidad_entry.grid(row=1, column=1, padx=5)

        ttk.Label(marco_mov, text="Motivo:").grid(row=1, column=2, sticky="w")
        self.motivo_entry = ttk.Entry(marco_mov, width=30)
        self.motivo_entry.grid(row=1, column=3, columnspan=2, padx=5)

        ttk.Button(marco_mov, text="Registrar", command=self.registrar).grid(row=0, column=5, rowspan=2, padx=10)

        self.alerta_label = ttk.Label(self, text="", foreground="red")
        self.alerta_label.pack(pady=5)

        columnas = ["fecha", "codigo", "tipo", "cantidad", "motivo"]
        self.tabla = TablaDatos(self, columnas, "Historial de Movimientos")
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.cargar_historial()

    def actualizar_alerta(self):
        alertas = inventario.productos_en_alerta()
        if alertas:
            nombres = ", ".join(p["nombre"] for p in alertas)
            self.alerta_label.config(text=f"⚠️ Productos con stock bajo: {nombres}")
        else:
            self.alerta_label.config(text="✅ Todos los productos tienen stock suficiente")

    def registrar(self):
        try:
            codigo = self.codigo_entry.get().strip()
            tipo = self.tipo_var.get()
            cantidad = int(self.cantidad_entry.get())
            motivo = self.motivo_entry.get().strip() or "Sin especificar"

            producto, alerta = inventario.registrar_movimiento(codigo, tipo, cantidad, motivo)
            messagebox.showinfo("Éxito",
                                f"Movimiento registrado.\nStock actual: {producto['stock']}")
            self.codigo_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
            self.motivo_entry.delete(0, tk.END)
            self.cargar_historial()
            self.actualizar_alerta()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def cargar_historial(self):
        movimientos = inventario.listar_movimientos()
        self.tabla.cargar_datos(movimientos)
