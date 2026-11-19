from datetime import datetime
from persistencia.archivos_json import leer_json, guardar_varios
from . import ErrorNegocio

_SESION_ACTIVA = None


def cargar_caja():
    """Carga el historial de sesiones de caja desde el archivo."""
    return leer_json("caja.json", {"sesiones": []})


def _guardar_caja(datos_caja):
    """Guarda el estado de caja."""
    guardar_varios([("caja.json", datos_caja)])


def sesion_abierta():
    """Devuelve los datos de la sesión actual si hay una abierta, o None."""
    global _SESION_ACTIVA
    return _SESION_ACTIVA


def abrir_caja(saldo_inicial):
    """Abre una nueva sesión de caja con el saldo inicial indicado."""
    global _SESION_ACTIVA
    if _SESION_ACTIVA is not None:
        raise ErrorNegocio("Ya hay una caja abierta")
    if saldo_inicial < 0:
        raise ErrorNegocio("El saldo inicial no puede ser negativo")

    _SESION_ACTIVA = {
        "fecha_apertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "saldo_inicial": float(saldo_inicial),
        "movimientos": [],
        "estado": "Abierta"
    }
    return _SESION_ACTIVA


def registrar_efectivo(tipo, concepto, monto):
    """Registra un ingreso o egreso en la sesión activa."""
    global _SESION_ACTIVA
    if _SESION_ACTIVA is None:
        raise ErrorNegocio("No hay caja abierta")

    monto = float(monto)
    if monto <= 0:
        raise ErrorNegocio("El monto debe ser mayor a cero")

    efectivo_actual = _calcular_total_efectivo()

    if tipo == "egreso" and monto > efectivo_actual:
        raise ErrorNegocio("El egreso supera el efectivo disponible en caja")
    if tipo not in ("ingreso", "egreso"):
        raise ErrorNegocio("Tipo de movimiento inválido")

    movimiento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "concepto": concepto,
        "monto": monto
    }
    _SESION_ACTIVA["movimientos"].append(movimiento)
    return movimiento


def _calcular_total_efectivo():
    """Calcula cuánto dinero hay en caja actualmente."""
    global _SESION_ACTIVA
    total = _SESION_ACTIVA["saldo_inicial"]
    for m in _SESION_ACTIVA["movimientos"]:
        if m["tipo"] == "ingreso":
            total += m["monto"]
        else:
            total -= m["monto"]
    return total


def calcular_esperado(sesion=None):
    """Calcula cuánto dinero debería haber en caja al cierre."""
    if sesion is None:
        sesion = _SESION_ACTIVA
    return sum(
        m["monto"] if m["tipo"] == "ingreso" else -m["monto"]
        for m in sesion["movimientos"]
    ) + sesion["saldo_inicial"]


def cerrar_caja(efectivo_declarado):
    """Cierra la caja y registra el corte con la diferencia."""
    global _SESION_ACTIVA
    if _SESION_ACTIVA is None:
        raise ErrorNegocio("No hay caja abierta")

    valor_esperado = calcular_esperado()
    efectivo_declarado = float(efectivo_declarado)
    diferencia = efectivo_declarado - valor_esperado

    _SESION_ACTIVA["fecha_cierre"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _SESION_ACTIVA["valor_esperado"] = valor_esperado
    _SESION_ACTIVA["efectivo_declarado"] = efectivo_declarado
    _SESION_ACTIVA["diferencia"] = diferencia
    _SESION_ACTIVA["estado"] = "Cerrada"

    datos = cargar_caja()
    datos["sesiones"].append(_SESION_ACTIVA)
    _guardar_caja(datos)

    cerrada = _SESION_ACTIVA
    _SESION_ACTIVA = None
    return cerrada