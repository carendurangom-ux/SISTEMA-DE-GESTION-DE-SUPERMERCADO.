from datetime import datetime
from persistencia.archivos_json import cargar_datos, guardar_datos

RUTA_PRODUCTOS = "datos/productos.json"
RUTA_VENTAS = "datos/ventas.json"


def calcular_subtotal(carrito):

    subtotal = 0

    for producto in carrito:
        subtotal += producto["precio"] * producto["cantidad"]

    return subtotal


def realizar_venta(carrito, pago, descuento=0, impuesto=0):

    productos = cargar_datos(RUTA_PRODUCTOS)
    ventas = cargar_datos(RUTA_VENTAS)

    # Verificar stock
    for item in carrito:

        encontrado = False

        for producto in productos:

            if producto["codigo"] == item["codigo"]:

                encontrado = True

                if item["cantidad"] > producto["stock"]:
                    return False, "No hay suficiente inventario."

        if not encontrado:
            return False, "Producto no encontrado."

    subtotal = calcular_subtotal(carrito)

    valor_descuento = subtotal * descuento

    subtotal_con_descuento = subtotal - valor_descuento

    valor_impuesto = subtotal_con_descuento * impuesto

    total = subtotal_con_descuento + valor_impuesto

    if pago < total:
        return False, "El pago es insuficiente."

    # Actualizar inventario
    for item in carrito:

        for producto in productos:

            if producto["codigo"] == item["codigo"]:
                producto["stock"] -= item["cantidad"]

    numero_factura = len(ventas) + 1

    factura = {
        "numero_factura": numero_factura,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detalle": carrito,
        "descuento": valor_descuento,
        "impuesto": valor_impuesto,
        "total": total,
        "pago": pago,
        "cambio": pago - total,
        "estado": "Activa"
    }

    ventas.append(factura)

    guardar_datos(RUTA_PRODUCTOS, productos)
    guardar_datos(RUTA_VENTAS, ventas)

    return True, factura