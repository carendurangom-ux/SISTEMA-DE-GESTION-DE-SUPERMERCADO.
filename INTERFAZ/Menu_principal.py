import tkinter as tk


def crear_menu():

    ventana = tk.Tk()

    ventana.title("Sistema de Gestión de Supermercado")

    ventana.geometry("600x400")

    titulo = tk.Label(
        ventana,
        text="SISTEMA DE GESTIÓN DE SUPERMERCADO",
        font=("Arial", 18, "bold")
    )

    titulo.pack(pady=30)

    boton_productos = tk.Button(
        ventana,
        text="Productos",
        width=25
    )

    boton_productos.pack(pady=5)

    boton_inventario = tk.Button(
        ventana,
        text="Inventario",
        width=25
    )

    boton_inventario.pack(pady=5)

    boton_ventas = tk.Button(
        ventana,
        text="Ventas",
        width=25
    )

    boton_ventas.pack(pady=5)

    boton_caja = tk.Button(
        ventana,
        text="Caja",
        width=25
    )

    boton_caja.pack(pady=5)

    ventana.mainloop()