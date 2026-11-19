from datetime import datetime
from persistencia.archivos_json import leer_json, guardar_varios
from NEGOCIO import productos
from . import ErrorNegocio

_CACHE_MOVIMIENTOS = None


def _recargar():
    global _CACHE_MOVIMIENTOS
    _CACHE_MOVIMIENTOS = leer_json("inventario.json", [])


def _guardar():
    guardar_varios([("inventario.json", _CACHE_MOVIMIENTOS)])


def registrar_movimiento(codigo, tipo, cantidad, motivo=""):
    """Registra una entrada o salida de inventario con validaciones."""
    global _CACHE_MOVIMIENTOS
    if _CACHE_MOVIMIENTOS is None:
        _recargar()

    p = productos.buscar_producto(codigo)
    if not p:
        raise ErrorNegocio(f"Producto {codigo} no encontrado")

    cantidad = int(cantidad)
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad debe ser mayor a cero")

    if tipo == "salida":
        if cantidad > p["stock"]:
            raise ErrorNegocio(f"Existencias insuficientes: hay {p['stock']}, se quieren sacar {cantidad}")
        productos._actualizar_stock(codigo, -cantidad)
    elif tipo == "entrada":
        productos._actualizar_stock(codigo, cantidad)
    else:
        raise ErrorNegocio("Tipo de movimiento inválido: use 'entrada' o 'salida'")

    movimiento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "codigo": codigo,
        "tipo": tipo,
        "cantidad": cantidad,
        "motivo": motivo
    }
    _CACHE_MOVIMIENTOS.append(movimiento)
    _guardar()

    p_actualizado = productos.buscar_producto(codigo)
    alerta = p_actualizado["stock"] <= p_actualizado["stock_minimo"]
    return p_actualizado, alerta


def listar_movimientos(codigo=None):
    """Devuelve el historial de movimientos, opcionalmente filtrado por producto."""
    global _CACHE_MOVIMIENTOS
    if _CACHE_MOVIMIENTOS is None:
        _recargar()
    if codigo:
        return [m for m in _CACHE_MOVIMIENTOS if m["codigo"] == codigo]
    return list(_CACHE_MOVIMIENTOS)


def productos_en_alerta():
    """Devuelve productos con stock igual o por debajo del mínimo."""
    resultado = []
    for p in productos.cargar_productos():
        if p["activo"] and p["stock"] <= p["stock_minimo"]:
            resultado.append(p)
    return resultado
