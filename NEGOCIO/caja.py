from Persistencia.Archivos_json import leer_json, guardar_json

ARCHIVO = "Caja.json"


def obtener_saldo():
    datos = leer_json(ARCHIVO, {"saldo": 0})
    if not isinstance(datos, dict):
        return 0
    return datos.get("saldo", 0)


def registrar_ingreso(monto):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    saldo = round(obtener_saldo() + monto, 2)
    guardar_json(ARCHIVO, {"saldo": saldo})


def registrar_egreso(monto):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    saldo = round(obtener_saldo() - monto, 2)
    guardar_json(ARCHIVO, {"saldo": saldo})
    
