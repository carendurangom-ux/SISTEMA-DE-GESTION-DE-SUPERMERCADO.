from persistencia.archivos_json import leer_json, guardar_varios
from . import ErrorNegocio

_CACHE_PRODUCTOS = None


def _recargar():
    global _CACHE_PRODUCTOS
    _CACHE_PRODUCTOS = leer_json("productos.json", [])


def _guardar():
    guardar_varios([("productos.json", _CACHE_PRODUCTOS)])


def crear_producto(codigo, nombre, categoria, costo, precio_venta, stock, stock_minimo):
    """Registra un nuevo producto en el sistema."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()

    codigo = codigo.strip()
    nombre = nombre.strip()
    categoria = categoria.strip()

    if not codigo:
        raise ErrorNegocio("El código es obligatorio")
    if not nombre:
        raise ErrorNegocio("El nombre es obligatorio")
    if any(not isinstance(x, (int, float)) or x < 0 for x in [costo, precio_venta, stock, stock_minimo]):
        raise ErrorNegocio("Los valores numéricos deben ser positivos")
    if any(p["codigo"] == codigo for p in _CACHE_PRODUCTOS):
        raise ErrorNegocio(f"Ya existe un producto con código {codigo}")

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "costo": float(costo),
        "precio_venta": float(precio_venta),
        "stock": int(stock),
        "stock_minimo": int(stock_minimo),
        "activo": True
    }
    _CACHE_PRODUCTOS.append(producto)
    _guardar()
    return producto


def cargar_productos():
    """Devuelve la lista completa de productos."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    return list(_CACHE_PRODUCTOS)


def buscar_producto(codigo):
    """Busca un producto exacto por su código."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    for p in _CACHE_PRODUCTOS:
        if p["codigo"] == codigo:
            return p
    return None


def buscar_productos(termino, solo_activos=True):
    """Busca productos por código, nombre o categoría."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    termino = termino.lower()
    resultados = []
    for p in _CACHE_PRODUCTOS:
        if solo_activos and not p["activo"]:
            continue
        if (termino in p["codigo"].lower() or
            termino in p["nombre"].lower() or
            termino in p["categoria"].lower()):
            resultados.append(p)
    return resultados


def editar_producto(codigo, nombre, categoria, costo, precio_venta, stock_minimo):
    """Modifica los datos de un producto existente. No modifica el stock."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    for p in _CACHE_PRODUCTOS:
        if p["codigo"] == codigo:
            if not nombre.strip():
                raise ErrorNegocio("El nombre es obligatorio")
            p["nombre"] = nombre.strip()
            p["categoria"] = categoria.strip()
            p["costo"] = float(costo)
            p["precio_venta"] = float(precio_venta)
            p["stock_minimo"] = int(stock_minimo)
            _guardar()
            return p
    raise ErrorNegocio(f"Producto {codigo} no encontrado")


def cambiar_estado(codigo, activo):
    """Activa o desactiva un producto."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    for p in _CACHE_PRODUCTOS:
        if p["codigo"] == codigo:
            p["activo"] = bool(activo)
            _guardar()
            return p
    raise ErrorNegocio(f"Producto {codigo} no encontrado")


def _actualizar_stock(codigo, cantidad):
    """Función interna: suma o resta stock sin validar."""
    global _CACHE_PRODUCTOS
    if _CACHE_PRODUCTOS is None:
        _recargar()
    for p in _CACHE_PRODUCTOS:
        if p["codigo"] == codigo:
            p["stock"] += cantidad
            _guardar()
            return p
    raise ErrorNegocio(f"Producto {codigo} no encontrado")
