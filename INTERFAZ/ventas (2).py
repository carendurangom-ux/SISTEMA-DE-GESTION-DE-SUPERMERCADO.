import tkinter as tk
from tkinter import ttk, messagebox
from NEGOCIO import ventas, productos, caja, ErrorNegocio
from INTERFAZ.datos_ui import TablaDatos


class VentanaVentas(tk.Toplevel):
    def __init__(self, parent, tienda):
        super().__init__(parent)
        self.tienda = tienda
        self.title("Punto de Ventas")
        self.geometry("900x600")
        self.carrito = []
        self.crear_widgets()

    def crear_widgets(self):
        marco_buscar = ttk.LabelFrame(self, text="Agregar Producto", padding="10")
        marco_buscar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(marco_buscar, text="Código:").grid(row=0, column=0, sticky="w")
        self.codigo_entry = ttk.Entry(marco_buscar, width=20)
        self.codigo_entry.grid(row=0, column=1, padx=5)

        ttk.Label(marco_buscar, text="Cantidad:").grid(row=0, column=2, sticky="w")
        self.cantidad_entry = ttk.Entry(marco_buscar, width=10)
        self.cantidad_entry.grid(row=0, column=3, padx=5)

        ttk.Button(marco_buscar, text="Agregar", command=self.agregar_item).grid(row=0, column=4, padx=5)

        marco_carrito = ttk.LabelFrame(self, text="Carrito de Compras", padding="10")
        marco_carrito.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columnas = ["codigo", "nombre", "precio_venta", "cantidad", "subtotal"]
        self.tabla = TablaDatos(marco_carrito, columnas)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        ttk.Button(marco_carrito, text="Eliminar Seleccionado",
                   command=self.eliminar_item).pack(anchor="w", pady=5)

        marco_total = ttk.Frame(self, padding="10")
        marco_total.pack(fill=tk.X, padx=10)

        ttk.Label(marco_total, text="Descuento (%):").grid(row=0, column=0, sticky="w")
        self.descuento_entry = ttk.Entry(marco_total, width=10)
        self.descuento_entry.insert(0, "0")
        self.descuento_entry.grid(row=0, column=1, padx=5)

        self.subtotal_label = ttk.Label(marco_total, text="Subtotal: $0.00", font=("Arial", 11))
        self.subtotal_label.grid(row=0, column=2, padx=15)

        self.impuesto_label = ttk.Label(marco_total, text="IVA: $0.00", font=("Arial", 11))
        self.impuesto_label.grid(row=0, column=3, padx=15)

        self.total_label = ttk.Label(marco_total, text="TOTAL: $0.00",
                                      font=("Arial", 14, "bold"), foreground="#c0392b")
        self.total_label.grid(row=0, column=4, padx=15)

        marco_pago = ttk.Frame(self, padding="10")
        marco_pago.pack(fill=tk.X, padx=10)

        ttk.Label(marco_pago, text="Pago con:").pack(side=tk.LEFT)
        self.pago_entry = ttk.Entry(marco_pago, width=15)
        self.pago_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_pago, text="Confirmar Venta",
                   command=self.confirmar_venta).pack(side=tk.LEFT, padx=10)

        self.cambio_label = ttk.Label(marco_pago, text="", font=("Arial", 11))
        self.cambio_label.pack(side=tk.LEFT)

        self.actualizar_totales()

    def agregar_item(self):
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            return
        try:
            cantidad = int(self.cantidad_entry.get()) if self.cantidad_entry.get() else 1
            ventas.agregar_al_carrito(self.carrito, codigo, cantidad)
            self.codigo_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
            self.actualizar_tabla()
            self.actualizar_totales()
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def eliminar_item(self):
        seleccion = self.tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un ítem")
            return
        codigo = seleccion[0]
        self.carrito = [i for i in self.carrito if i["codigo"] != codigo]
        self.actualizar_tabla()
        self.actualizar_totales()

    def actualizar_tabla(self):
        filas = []
        for item in self.carrito:
            filas.append({
                "codigo": item["codigo"],
                "nombre": item["nombre"],
                "precio_venta": f"${item['precio_venta']:.2f}",
                "cantidad": item["cantidad"],
                "subtotal": f"${item['precio_venta'] * item['cantidad']:.2f}"
            })
        self.tabla.cargar_datos(filas)

    def actualizar_totales(self):
        try:
            descuento = float(self.descuento_entry.get()) if self.descuento_entry.get() else 0
        except ValueError:
            descuento = 0
        totales = ventas.calcular_totales(self.carrito, descuento)
        self.subtotal_label.config(text=f"Subtotal: ${totales['subtotal']:.2f}")
        self.impuesto_label.config(text=f"IVA: ${totales['impuestos']:.2f}")
        self.total_label.config(text=f"TOTAL: ${totales['total']:.2f}")
        self.cambio_label.config(text="")

    def confirmar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Aviso", "El carrito está vacío")
            return
        if caja.sesion_abierta() is None:
            messagebox.showwarning("Aviso", "Debe abrir la caja antes de vender")
            return
        try:
            descuento = float(self.descuento_entry.get()) if self.descuento_entry.get() else 0
            pago = float(self.pago_entry.get()) if self.pago_entry.get() else 0
            totales = ventas.calcular_totales(self.carrito, descuento)
            cambio = ventas.calcular_cambio(totales["total"], pago)
            factura = ventas.confirmar_venta(self.carrito, descuento, pago)

            msg = f"""✅ Venta confirmada
Factura N°: {factura['numero']}
Fecha: {factura['fecha']}
---
Subtotal: ${totales['subtotal']:.2f}
Descuento: ${totales['descuento']:.2f}
IVA: ${totales['impuestos']:.2f}
TOTAL: ${totales['total']:.2f}
Pago con: ${pago:.2f}
CAMBIO: ${cambio:.2f}
"""
            messagebox.showinfo("Factura Generada", msg)
            # Reiniciar
            self.carrito = []
            self.actualizar_tabla()
            self.actualizar_totales()
            self.pago_entry.delete(0, tk.END)
            self.descuento_entry.delete(0, tk.END)
            self.descuento_entry.insert(0, "0")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto de pago válido")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))
