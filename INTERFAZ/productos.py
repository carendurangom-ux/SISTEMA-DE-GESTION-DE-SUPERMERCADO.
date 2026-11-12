import tkinter as tk
from tkinter import ttk, messagebox
from .datos_ui import productos, guardar_productos, dinero

class ProductosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Page.TFrame", padding=22)
        self._construir()
        self.actualizar()

    def _construir(self):
        ttk.Label(self, text="Productos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Administra el catálogo y los precios de venta.",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 18))

        barra = ttk.Frame(self, style="Page.TFrame")
        barra.pack(fill="x", pady=(0, 12))
        ttk.Button(barra, text="+ Agregar producto", style="Accent.TButton",
                   command=self.agregar).pack(side="left")
        ttk.Button(barra, text="Editar seleccionado", command=self.editar).pack(side="left", padx=8)
        ttk.Button(barra, text="Eliminar", style="Danger.TButton",
                   command=self.eliminar).pack(side="left")
        ttk.Button(barra, text="Actualizar", command=self.actualizar).pack(side="right")

        columnas = ("codigo", "nombre", "categoria", "compra", "venta", "stock")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=17)
        titulos = {
            "codigo":"Código", "nombre":"Nombre", "categoria":"Categoría",
            "compra":"Precio compra", "venta":"Precio venta", "stock":"Existencias"
        }
        anchos = {"codigo":100, "nombre":220, "categoria":150, "compra":130, "venta":130, "stock":100}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w")
        self.tabla.pack(fill="both", expand=True)

    def actualizar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in productos():
            self.tabla.insert("", "end", values=(
                p.get("codigo", ""), p.get("nombre", ""), p.get("categoria", ""),
                dinero(p.get("precio_compra", 0)), dinero(p.get("precio_venta", 0)),
                p.get("stock", 0)
            ))

    def _formulario(self, titulo, inicial=None):
        inicial = inicial or {}
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.geometry("390x470")
        ventana.configure(bg="#171d23")
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        campos = [
            ("codigo", "Código"), ("nombre", "Nombre"),
            ("categoria", "Categoría"), ("precio_compra", "Precio de compra"),
            ("precio_venta", "Precio de venta"), ("stock", "Existencias"),
            ("stock_minimo", "Stock mínimo")
        ]
        entradas = {}
        tk.Label(ventana, text=titulo, bg="#171d23", fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(20, 12))
        cuerpo = tk.Frame(ventana, bg="#171d23")
        cuerpo.pack(fill="both", expand=True, padx=22)
        for clave, etiqueta in campos:
            tk.Label(cuerpo, text=etiqueta, bg="#171d23", fg="#b9c4ce",
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 2))
            entrada = tk.Entry(cuerpo, bg="#252e37", fg="white", insertbackground="white",
                               relief="flat", font=("Segoe UI", 10))
            entrada.pack(fill="x", ipady=7)
            entrada.insert(0, str(inicial.get(clave, "")))
            entradas[clave] = entrada

        def guardar():
            valores = {k: e.get().strip() for k, e in entradas.items()}
            if not valores["codigo"] or not valores["nombre"]:
                messagebox.showwarning("Datos incompletos", "El código y el nombre son obligatorios.", parent=ventana)
                return
            try:
                for k in ("precio_compra", "precio_venta", "stock", "stock_minimo"):
                    valores[k] = float(valores[k] or 0)
                valores["stock"] = int(valores["stock"])
                valores["stock_minimo"] = int(valores["stock_minimo"])
            except ValueError:
                messagebox.showerror("Dato inválido", "Los precios y existencias deben ser números.", parent=ventana)
                return
            lista = productos()
            indice = next((i for i, p in enumerate(lista) if str(p.get("codigo")) == str(inicial.get("codigo"))), None) if inicial else None
            if indice is None:
                if any(str(p.get("codigo")) == valores["codigo"] for p in lista):
                    messagebox.showerror("Código repetido", "Ya existe un producto con ese código.", parent=ventana)
                    return
                valores["activo"] = True
                lista.append(valores)
            else:
                valores["activo"] = lista[indice].get("activo", True)
                lista[indice] = valores
            guardar_productos(lista)
            self.actualizar()
            ventana.destroy()

        tk.Button(ventana, text="Guardar producto", command=guardar,
                  bg="#16a36a", fg="white", activebackground="#128454",
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=22, pady=18, ipady=9)

    def agregar(self):
        self._formulario("Nuevo producto")

    def editar(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showinfo("Selecciona un producto", "Elige un producto de la tabla.")
            return
        codigo = str(self.tabla.item(seleccionado[0], "values")[0])
        item = next((p for p in productos() if str(p.get("codigo")) == codigo), None)
        if item:
            self._formulario("Editar producto", item)

    def eliminar(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showinfo("Selecciona un producto", "Elige un producto de la tabla.")
            return
        codigo = str(self.tabla.item(seleccionado[0], "values")[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto {codigo}?"):
            guardar_productos([p for p in productos() if str(p.get("codigo")) != codigo])
            self.actualizar()
