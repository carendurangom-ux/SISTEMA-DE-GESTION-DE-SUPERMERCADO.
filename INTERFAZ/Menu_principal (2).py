import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from NEGOCIO import ErrorNegocio


class App(tk.Tk):
    def __init__(self, tienda):
        super().__init__()
        self.tienda = tienda
        self.title("Sistema de Gestión de Supermercado")
        self.geometry("900x650")

        self.crear_menu()
        self.crear_contenido()

    def crear_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

    def crear_contenido(self):
        marco = ttk.Frame(self, padding="20")
        marco.pack(fill=tk.BOTH, expand=True)

        # Imagen en la MISMA carpeta que Menu_principal.py
        try:
            ruta_imagen = os.path.join(os.path.dirname(__file__), "tienda.png")
            imagen_original = Image.open(ruta_imagen)
            imagen_redimensionada = imagen_original.resize((400, 250), Image.Resampling.LANCZOS)
            self.imagen = ImageTk.PhotoImage(imagen_redimensionada)
            ttk.Label(marco, image=self.imagen).pack(pady=(0, 20))
        except Exception as e:
            ttk.Label(marco, text=f"No se pudo cargar la imagen: {e}", foreground="red").pack(pady=10)

        ttk.Label(marco, text="¡Bienvenido al Sistema de Supermercado!",
                  font=("Arial", 20, "bold")).pack(pady=(0, 20))

        botones = [
            ("Gestión de Productos", self.abrir_productos),
            ("Control de Inventario", self.abrir_inventario),
            ("Módulo de Caja", self.abrir_caja),
            ("Punto de Ventas", self.abrir_ventas),
        ]

        for texto, comando in botones:
            ttk.Button(marco, text=texto, command=comando, width=40).pack(pady=8)

    def abrir_productos(self):
        from INTERFAZ.productos import VentanaProductos
        VentanaProductos(self, self.tienda)

    def abrir_inventario(self):
        from INTERFAZ.inventario import VentanaInventario
        VentanaInventario(self, self.tienda)

    def abrir_caja(self):
        from INTERFAZ.caja import VentanaCaja
        VentanaCaja(self, self.tienda)

    def abrir_ventas(self):
        from INTERFAZ.ventas import VentanaVentas
        VentanaVentas(self, self.tienda)

    def acerca_de(self):
        messagebox.showinfo("Acerca de",
                            "Sistema de Gestión de Supermercado\n"
                            "Versión 1.0\n© 2026")
