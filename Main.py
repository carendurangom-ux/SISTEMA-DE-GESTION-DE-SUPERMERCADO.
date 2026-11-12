"""Punto de entrada. Ejecutar desde la raíz del proyecto: python Main.py"""
import sys
import tkinter as tk
from tkinter import messagebox

from persistencia.archivos_json import ErrorPersistencia
from negocio.tienda import Tienda
from interfaz.Menu_principal import App
#Hello, este es un cambio de la señorita Elin, estoy agregando una función para probar el control de versiones.
# este es un cabio de la señorita elin :)
def funcion_eilin():
    print("Hola, soy la señorita Elin y estoy haciendo un cambio en el código.")

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
    
    
from Interfaz.Menu import iniciar

if __name__ == "__main__":
    iniciar()


if __name__ == "__main__":
    main()