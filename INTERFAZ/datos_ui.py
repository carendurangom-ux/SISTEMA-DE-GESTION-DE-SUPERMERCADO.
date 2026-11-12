import json
from pathlib import Path
from datetime import datetime

# Los datos están en la carpeta DATOS, al mismo nivel que INTERFAZ.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "DATOS"

def leer_json(nombre, defecto):
    ruta = DATA_DIR / nombre
    try:
        if not ruta.exists():
            ruta.parent.mkdir(parents=True, exist_ok=True)
            guardar_json(nombre, defecto)
            return defecto
        with ruta.open("r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return defecto

def guardar_json(nombre, datos):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ruta = DATA_DIR / nombre
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
    temporal.replace(ruta)

def productos():
    datos = leer_json("productos.json", [])
    return datos if isinstance(datos, list) else []

def guardar_productos(datos):
    guardar_json("productos.json", datos)

def ventas():
    datos = leer_json("ventas.json", [])
    return datos if isinstance(datos, list) else []

def guardar_ventas(datos):
    guardar_json("ventas.json", datos)

def caja():
    datos = leer_json("caja.json", {"sesiones": []})
    if not isinstance(datos, dict):
        datos = {"sesiones": []}
    datos.setdefault("sesiones", [])
    return datos

def guardar_caja(datos):
    guardar_json("caja.json", datos)

def dinero(valor):
    try:
        return "$ {:,.0f}".format(float(valor)).replace(",", ".")
    except (TypeError, ValueError):
        return "$ 0"

def fecha_hora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
