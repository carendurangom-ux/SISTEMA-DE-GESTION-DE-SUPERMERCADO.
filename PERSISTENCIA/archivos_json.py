import json
import os

CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "Datos")


def _ruta(nombre):
    return os.path.join(CARPETA_DATOS, nombre)


def leer_json(nombre, valor_por_defecto):
    """Lee un archivo JSON. Si no existe o está vacío, devuelve el valor por defecto."""
    ruta = _ruta(nombre)
    if not os.path.exists(ruta):
        return valor_por_defecto
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return valor_por_defecto


def guardar_json(nombre, datos):
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    with open(_ruta(nombre), "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)