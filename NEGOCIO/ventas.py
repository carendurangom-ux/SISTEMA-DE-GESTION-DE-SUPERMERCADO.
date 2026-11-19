from datetime import datetime
from persistencia.archivos_json import leer_json, guardar_varios
from NEGOCIO import productos, caja
from . import ErrorNegocio

_IVA = 0.19
_DESCUENTO_MAXIMO = 50
_CACHE_VENTAS = None


def ahora():
    """Fecha y hora actual en formato ISO."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _recargar():
    global _CACHE_VENTAS
    _CACHE_VENTAS = leer_json("ventas.json", {"contador": 0, "facturas": []})


def _guardar():
    guardar_varios([("ventas.json", _CACHE_VENTAS)])


def cargar_ventas():
    """Devuelve el historial completo de facturas."""
    global _CACHE_VENTAS
    if _CACHE_VENTAS is None:
        _recargar()
    return list(_CACHE_VENTAS["facturas"])


def agregar_al_carrito(carrito, codigo, cantidad):
    """Agrega un producto al carrito de compras con validación de stock."""
    cantidad = int(cantidad)
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad debe ser mayor a cero")

    p = productos.buscar_producto(codigo)
    if not p:
        raise ErrorNegocio(f"Producto {codigo} no encontrado")
    if not p["activo"]:
        raise ErrorNegocio(f"Producto {codigo} está desactivado")

    existe_en_carrito = next((item for item in carrito if item["codigo"] == codigo), None)
    cantidad_total = cantidad
    if existe_en_carrito:
        cantidad_total += existe_en_carrito["cantidad"]

    if cantidad_total > p["stock"]:
        raise ErrorNegocio(f"Existencias insuficientes para {p['nombre']}: hay {p['stock']}")

    if existe_en_carrito:
        existe_en_carrito["cantidad"] = cantidad_total
    else:
        carrito.append({
            "codigo": codigo,
            "nombre": p["nombre"],
            "precio_venta": p["precio_venta"],
            "cantidad": cantidad
        })
    return carrito


def quitar_del_carrito(carrito, indice):
    """Elimina una línea del carrito por su posición."""
    if 0 <= indice < len(carrito):
        del carrito[indice]
    return carrito


def calcular_totales(carrito, descuento_porcentaje=0):
    """Calcula subtotal, descuento, impuestos y total de venta."""
    descuento_porcentaje = float(descuento_porcentaje)
    if descuento_porcentaje < 0 or descuento_porcentaje > _DESCUENTO_MAXIMO:
        raise ErrorNegocio(f"El descuento debe estar entre 0 y {_DESCUENTO_MAXIMO}%")

    subtotal = sum(item["precio_venta"] * item["cantidad"] for item in carrito)
    descuento = subtotal * (descuento_porcentaje / 100.0)
    base_impuesto = subtotal - descuento
    impuestos = base_impuesto * _IVA
    total = base_impuesto + impuestos

    return {
        "subtotal": round(subtotal, 2),
        "descuento": round(descuento, 2),
        "impuestos": round(impuestos, 2),
        "total": round(total, 2)
    }


def calcular_cambio(total, pago):
    """Calcula el cambio a devolver al cliente."""
    total = float(total)
    pago = float(pago)
    if pago < total:
        raise ErrorNegocio("Pago insuficiente")
    return round(pago - total, 2)


def confirmar_venta(carrito, descuento_porcentaje=0, pago_recibido=None):
    """Procesa la venta: valida caja abierta, baja stock, genera factura y registra en caja."""
    global _CACHE_VENTAS
    if _CACHE_VENTAS is None:
        _recargar()

    if caja.sesion_abierta() is None:
        raise ErrorNegocio("Debe abrir la caja antes de vender")

    if not carrito:
        raise ErrorNegocio("El carrito está vacío")

    totales = calcular_totales(carrito, descuento_porcentaje)
    if pago_recibido is not None and float(pago_recibido) < totales["total"]:
        raise ErrorNegocio("Pago insuficiente")

    # Baja de stock
    for item in carrito:
        productos._actualizar_stock(item["codigo"], -item["cantidad"])

    # Generar número de factura
    _CACHE_VENTAS["contador"] += 1
    numero = _CACHE_VENTAS["contador"]

    factura = {
        "numero": numero,
        "fecha": ahora(),
        "detalle": [dict(item) for item in carrito],
        "descuento_porcentaje": descuento_porcentaje,
        "subtotal": totales["subtotal"],
        "descuento": totales["descuento"],
        "impuestos": totales["impuestos"],
        "total": totales["total"],
        "estado": "Pagada",
        "devoluciones": []
    }

    _CACHE_VENTAS["facturas"].append(factura)
    _guardar()

    # Registrar ingreso en caja
    caja.registrar_efectivo("ingreso", f"Venta F-{numero:06d}", totales["total"])

    return factura


def buscar_factura(numero):
    """Busca una factura por su número."""
    global _CACHE_VENTAS
    if _CACHE_VENTAS is None:
        _recargar()
    for f in _CACHE_VENTAS["facturas"]:
        if f["numero"] == numero:
            return f
    return None


def registrar_devolucion(numero_factura, items_a_devolver, motivo="Devolución del cliente"):
    """Registra devoluciones: suma stock, resta dinero de caja y actualiza estado de factura."""
    global _CACHE_VENTAS
    if _CACHE_VENTAS is None:
        _recargar()

    factura = buscar_factura(numero_factura)
    if not factura:
        raise ErrorNegocio(f"Factura {numero_factura} no encontrada")
    if factura["estado"] == "Devuelta":
        raise ErrorNegocio("La factura ya está totalmente devuelta")

    # Calcular cuántas unidades ya se devolvieron por producto
    ya_devueltas = {}
    for dev in factura["devoluciones"]:
        for cod, cant in dev["items"].items():
            ya_devueltas[cod] = ya_devueltas.get(cod, 0) + cant

    # Validar y aplicar cada devolución
    valor_total_dev = 0.0
    for codigo, cantidad in items_a_devolver.items():
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ErrorNegocio("Cantidad a devolver debe ser mayor a cero")

        # Buscar en detalle de factura
        item_factura = next((i for i in factura["detalle"] if i["codigo"] == codigo), None)
        if not item_factura:
            raise ErrorNegocio(f"El producto {codigo} no aparece en esta factura")

        vendido = item_factura["cantidad"]
        devuelto_antes = ya_devueltas.get(codigo, 0)
        disponible = vendido - devuelto_antes

        if cantidad > disponible:
            raise ErrorNegocio(f"Solo se pueden devolver {disponible} unidades de {codigo}")

        # Devolver stock
        productos._actualizar_stock(codigo, cantidad)

        # Calcular valor proporcional
        precio_unitario = item_factura["precio_venta"]
        valor_dev = precio_unitario * cantidad
        valor_total_dev += valor_dev

    # Registrar movimiento de caja
    caja.registrar_efectivo("egreso", f"Devolución F-{numero_factura:06d}", valor_total_dev)

    # Agregar registro de devolución a la factura
    devolucion = {
        "fecha": ahora(),
        "motivo": motivo,
        "items": dict(items_a_devolver),
        "valor": round(valor_total_dev, 2)
    }
    factura["devoluciones"].append(devolucion)

    # Actualizar estado de la factura
    total_vendido = sum(i["cantidad"] for i in factura["detalle"])
    total_devuelto = 0
    for dev in factura["devoluciones"]:
        total_devuelto += sum(dev["items"].values())

    if total_devuelto >= total_vendido:
        factura["estado"] = "Devuelta"
    elif total_devuelto > 0:
        factura["estado"] = "Devolución parcial"

    _guardar()
    return factura, round(valor_total_dev, 2)


def reporte_ventas(fecha_inicio, fecha_fin):
    """Genera reporte de ventas y devoluciones en un rango de fechas."""
    global _CACHE_VENTAS
    if _CACHE_VENTAS is None:
        _recargar()

    # Validar formato de fechas
    try:
        from datetime import datetime as dt
        dt.strptime(fecha_inicio, "%Y-%m-%d")
        dt.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise ErrorNegocio("Formato de fecha inválido. Use AAAA-MM-DD")

    if fecha_inicio > fecha_fin:
        raise ErrorNegocio("Fecha de inicio no puede ser posterior a fecha de fin")

    facturas = _CACHE_VENTAS["facturas"]
    filtradas = []
    for f in facturas:
        fecha_factura = f["fecha"][:10]
        if fecha_inicio <= fecha_factura <= fecha_fin:
            filtradas.append(f)

    # Calcular totales
    num_facturas = len(filtradas)
    unidades_vendidas = 0
    ventas_brutas = 0.0
    total_devoluciones = 0.0
    productos_vendidos = {}

    for f in filtradas:
        ventas_brutas += f["total"]
        for item in f["detalle"]:
            unidades_vendidas += item["cantidad"]
            cod = item["codigo"]
            productos_vendidos[cod] = productos_vendidos.get(cod, 0) + item["cantidad"]
        for dev in f["devoluciones"]:
            total_devoluciones += dev["valor"]

    ingresos_netos = ventas_brutas - total_devoluciones

    # Productos más vendidos
    mas_vendidos = sorted(
        [{"codigo": c, "cantidad": k} for c, k in productos_vendidos.items()],
        key=lambda x: x["cantidad"],
        reverse=True
    )

    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "num_facturas": num_facturas,
        "unidades_vendidas": unidades_vendidas,
        "ventas_brutas": round(ventas_brutas, 2),
        "devoluciones": round(total_devoluciones, 2),
        "ingresos_netos": round(ingresos_netos, 2),
        "mas_vendidos": mas_vendidos
    }