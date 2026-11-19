import tkinter as tk
from tkinter import ttk, messagebox
from NEGOCIO import productos, ErrorNegocio
from INTERFAZ.datos_ui import TablaDatos


class VentanaProductos(tk.Toplevel):
    def __init__(self, parent, tienda):
        super().__init__(parent)
        self.tienda = tienda
        self.title("Gestión de Productos")
        self.geometry("850x550")
        self.crear_widgets()
        self.cargar_lista()

    def crear_widgets(self):
        marco_form = ttk.LabelFrame(self, text="Datos del Producto", padding="10")
        marco_form.pack(fill=tk.X, padx=10, pady=5)

        campos = [
            ("Código:", "codigo"),
            ("Nombre:", "nombre"),
            ("Categoría:", "categoria"),
            ("Costo:", "costo"),
            ("Precio Venta:", "precio"),
            ("Stock:", "stock"),
            ("Stock Mínimo:", "stock_minimo"),
        ]
        self.entries = {}
        for i, (etiqueta, nombre) in enumerate(campos):
            fila = i // 2
            col = (i % 2) * 2
            ttk.Label(marco_form, text=etiqueta).grid(row=fila, column=col, sticky="w", padx=5, pady=3)
            self.entries[nombre] = ttk.Entry(marco_form, width=25)
            self.entries[nombre].grid(row=fila, column=col+1, padx=5, pady=3)

        marco_btn = ttk.Frame(self, padding="10")
        marco_btn.pack(fill=tk.X)
        ttk.Button(marco_btn, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=2)
        ttk.Button(marco_btn, text="Editar", command=self.editar).pack(side=tk.LEFT, padx=2)
        ttk.Button(marco_btn, text="Desactivar/Activar", command=self.cambiar_estado).pack(side=tk.LEFT, padx=2)
        ttk.Button(marco_btn, text="Buscar", command=self.buscar).pack(side=tk.LEFT, padx=2)
        ttk.Button(marco_btn, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=2)

        columnas = ["codigo", "nombre", "categoria", "costo", "precio_venta", "stock", "stock_minimo", "activo"]
        self.tabla = TablaDatos(self, columnas, "Lista de Productos")
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def cargar_lista(self, lista=None):
        if lista is None:
            lista = productos.cargar_productos()
        self.tabla.cargar_datos(lista)

    def guardar(self):
        try:
            codigo = self.entries["codigo"].get().strip()
            nombre = self.entries["nombre"].get().strip()
            categoria = self.entries["categoria"].get().strip()
            costo = float(self.entries["costo"].get())
            precio = float(self.entries["precio"].get())
            stock = int(self.entries["stock"].get())
            stock_min = int(self.entries["stock_minimo"].get())

            productos.crear_producto(codigo, nombre, categoria, costo, precio, stock, stock_min)
            messagebox.showinfo("Éxito", "Producto registrado")
            self.limpiar()
            self.cargar_lista()
        except ValueError:
            messagebox.showerror("Error", "Verifique que los campos numéricos sean correctos")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def editar(self):
        seleccion = self.tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un producto de la lista")
            return
        try:
            codigo = self.entries["codigo"].get().strip() or seleccion[0]
            nombre = self.entries["nombre"].get().strip() or seleccion[1]
            categoria = self.entries["categoria"].get().strip() or seleccion[2]
            costo = float(self.entries["costo"].get()) if self.entries["costo"].get() else seleccion[3]
            precio = float(self.entries["precio"].get()) if self.entries["precio"].get() else seleccion[4]
            stock_min = int(self.entries["stock_minimo"].get()) if self.entries["stock_minimo"].get() else seleccion[6]

            productos.editar_producto(codigo, nombre, categoria, costo, precio, stock_min)
            messagebox.showinfo("Éxito", "Producto actualizado")
            self.limpiar()
            self.cargar_lista()
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos incorrectos")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def cambiar_estado(self):
        seleccion = self.tabla.obtener_seleccion()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un producto")
            return
        codigo = seleccion[0]
        producto = productos.buscar_producto(codigo)
        nuevo_estado = not producto["activo"]
        productos.cambiar_estado(codigo, nuevo_estado)
        estado_texto = "activado" if nuevo_estado else "desactivado"
        messagebox.showinfo("Éxito", f"Producto {estado_texto}")
        self.cargar_lista()

    def buscar(self):
        termino = self.entries["nombre"].get().strip()
        if not termino:
            self.cargar_lista()
        else:
            resultados = productos.buscar_productos(termino)
            self.tabla.cargar_datos(resultados)

    def limpiar(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.cargar_lista()
