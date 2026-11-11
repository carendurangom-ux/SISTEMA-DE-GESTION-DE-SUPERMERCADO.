import json
import os


def cargar_datos(ruta):
    """Carga los datos de un archivo JSON."""

    try:
        if not os.path.exists(ruta):
            return []

        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except json.JSONDecodeError:
        return []

    except Exception as error:
        print(f"Error al cargar los datos: {error}")
        return []


def guardar_datos(ruta, datos):
    """Guarda información en un archivo JSON."""

    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        return True

    except Exception as error:
        print(f"Error al guardar los datos: {error}")
        return False