"""Punto de entrada. Ejecutar desde la raíz del proyecto: python Main.py"""
import sys
import tkinter as tk
from tkinter import messagebox

from persistencia.archivos_json import ErrorPersistencia
from NEGOCIO.tienda import Tienda
from INTERFAZ.Menu_principal import App

def funcion_eilin():
    print("Hola, soy la señorita Elin y estoy haciendo un cambio en el código.")

def main():
    try:
        tienda = Tienda()
    except ErrorPersistencia as error:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("No se pudieron cargar los datos", str(error))
        raiz.destroy()
        sys.exit(1)
    App(tienda).mainloop()

if __name__ == "__main__":
    main()
