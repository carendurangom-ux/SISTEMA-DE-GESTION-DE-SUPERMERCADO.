from PERSISTENCIA.archivos_json import cargar_datos, guardar_datos


RUTA_CAJA = "datos/caja.json"


def obtener_caja():

    datos = cargar_datos(RUTA_CAJA)

    if not datos:
        return {
            "abierta": False,
            "saldo_inicial": 0,
            "movimientos": []
        }

    return datos


def abrir_caja(saldo_inicial):

    caja = obtener_caja()

    if caja["abierta"]:
        return False, "La caja ya está abierta."

    caja["abierta"] = True
    caja["saldo_inicial"] = saldo_inicial
    caja["movimientos"] = []

    guardar_datos(RUTA_CAJA, caja)

    return True, "Caja abierta correctamente."


def registrar_movimiento(tipo, valor, descripcion):

    caja = obtener_caja()

    if not caja["abierta"]:
        return False, "La caja está cerrada."

    movimiento = {
        "tipo": tipo,
        "valor": valor,
        "descripcion": descripcion
    }

    caja["movimientos"].append(movimiento)

    guardar_datos(RUTA_CAJA, caja)

    return True, "Movimiento registrado."


def cerrar_caja(valor_declarado):

    caja = obtener_caja()

    if not caja["abierta"]:
        return False, "La caja ya está cerrada."

    efectivo_esperado = caja["saldo_inicial"]

    for movimiento in caja["movimientos"]:

        if movimiento["tipo"] == "ingreso":
            efectivo_esperado += movimiento["valor"]

        elif movimiento["tipo"] == "egreso":
            efectivo_esperado -= movimiento["valor"]

    diferencia = valor_declarado - efectivo_esperado

    caja["abierta"] = False
    caja["valor_esperado"] = efectivo_esperado
    caja["valor_declarado"] = valor_declarado
    caja["diferencia"] = diferencia

    guardar_datos(RUTA_CAJA, caja)

    return True, caja