"""Componente reutilizable para mostrar tablas de datos en la interfaz"""
import tkinter as tk
from tkinter import ttk


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

