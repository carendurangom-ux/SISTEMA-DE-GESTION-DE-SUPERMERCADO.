from Negocio import Productos, Inventario, Venta, Caja
import tkinter as tk
from tkinter import ttk


def pedir_numero(mensaje, tipo=float):
    while True:
        try:
            return tipo(input(mensaje))
        except ValueError:
            print("Valor no válido, intenta de nuevo.")


def mostrar_productos(productos):
    if not productos:
        print("No hay productos registrados.")
        return
    print(f"\n{'Código':<10}{'Nombre':<25}{'Precio':>10}{'Stock':>8}")
    for p in productos:
        print(f"{p['codigo']:<10}{p['nombre']:<25}{p['precio']:>10.2f}{p['cantidad']:>8}")


def menu_productos():
    while True:
        print("\n--- PRODUCTOS ---")
        print("1. Listar\n2. Agregar\n3. Editar\n4. Eliminar\n0. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                mostrar_productos(Productos.listar_productos())
            elif opcion == "2":
                codigo = input("Código: ").strip()
                nombre = input("Nombre: ").strip()
                precio = pedir_numero("Precio: ")
                cantidad = pedir_numero("Cantidad: ", int)
                Productos.agregar_producto(codigo, nombre, precio, cantidad)
                print("Producto agregado.")
            elif opcion == "3":
                codigo = input("Código del producto a editar: ").strip()
                nombre = input("Nuevo nombre (Enter para dejar igual): ").strip()
                texto = input("Nuevo precio (Enter para dejar igual): ").strip()
                precio = float(texto) if texto else None
                Productos.editar_producto(codigo, nombre or None, precio)
                print("Producto actualizado.")
            elif opcion == "4":
                codigo = input("Código del producto a eliminar: ").strip()
                Productos.eliminar_producto(codigo)
                print("Producto eliminado.")
            elif opcion == "0":
                return
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Error: {error}")


def menu_inventario():
    while True:
        print("\n--- INVENTARIO ---")
        print("1. Agregar stock\n2. Ver productos con poco stock\n0. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                codigo = input("Código: ").strip()
                cantidad = pedir_numero("Cantidad a agregar: ", int)
                Inventario.agregar_stock(codigo, cantidad)
                print("Stock actualizado.")
            elif opcion == "2":
                mostrar_productos(Inventario.productos_bajo_stock())
            elif opcion == "0":
                return
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Error: {error}")


def nueva_venta():
    items = []
    while True:
        codigo = input("Código del producto (Enter para terminar): ").strip()
        if not codigo:
            break
        producto = Productos.buscar_producto(codigo)
        if not producto:
            print("Producto no encontrado.")
            continue
        cantidad = pedir_numero(f"Cantidad de {producto['nombre']}: ", int)
        items.append((codigo, cantidad))
    if not items:
        print("Venta cancelada.")
        return
    try:
        venta = Venta.registrar_venta(items)
        print(f"Venta registrada. Total: ${venta['total']:.2f}")
    except ValueError as error:
        print(f"Error: {error}")


def menu_ventas():
    while True:
        print("\n--- VENTAS ---")
        print("1. Nueva venta\n2. Historial de ventas\n0. Volver")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            nueva_venta()
        elif opcion == "2":
            ventas = Venta.listar_ventas()
            if not ventas:
                print("No hay ventas registradas.")
            for v in ventas:
                print(f"#{v['id']} | {v['fecha']} | Total: ${v['total']:.2f}")
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


def iniciar():
    while True:
        print("\n===== SISTEMA DE GESTIÓN DE SUPERMERCADO =====")
        print("1. Productos\n2. Inventario\n3. Ventas\n4. Caja\n0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_inventario()
        elif opcion == "3":
            menu_ventas()
        elif opcion == "4":
            print(f"Saldo en caja: ${Caja.obtener_saldo():.2f}")
        elif opcion == "0":
            print("¡Hasta pronto!")
            break
        else:
            print("Opción no válida.")


"""Componente reutilizable para mostrar tablas de datos en la interfaz"""


class TablaDatos(ttk.Frame):
    def __init__(self, parent, columnas, titulo=""):
        super().__init__(parent)
        self.columnas = columnas
        self.titulo = titulo
        self.crear_widgets()

    def crear_widgets(self):
        if self.titulo:
            ttk.Label(self, text=self.titulo, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))

        marco_tabla = ttk.Frame(self)
        marco_tabla.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(marco_tabla, columns=self.columnas, show="headings", height=8)

        for col in self.columnas:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")

        scrollbar = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_datos(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for fila in filas:
            valores = [fila.get(col, "") for col in self.columnas]
            self.tree.insert("", tk.END, values=valores)

    def obtener_seleccion(self):
        seleccion = self.tree.selection()
        if seleccion:
            return self.tree.item(seleccion[0])["values"]
        return None

    def limpiar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
