"""Punto de entrada. Ejecutar desde la raíz del proyecto: python Main.py"""
import sys
import tkinter as tk
from tkinter import messagebox

from persistencia.archivos_json import ErrorPersistencia
from negocio.tienda import Tienda
from interfaz.Menu_principal import App


def main():
    try:
        tienda = Tienda()
    except ErrorPersistencia as error:
        # Si un JSON está dañado no se arranca, para no sobrescribirlo.
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("No se pudieron cargar los datos", str(error))
        raiz.destroy()
        sys.exit(1)
    App(tienda).mainloop()


if __name__ == "__main__":
    main()