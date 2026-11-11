

from persistencia.archivos_json import cargar_datos, guardar_datos

RUTA_PRODUCTOS = "datos/productos.json"


def agregar_stock(codigo, cantidad):

    productos = cargar_datos(RUTA_PRODUCTOS)

    for producto in productos:

        if producto["codigo"] == codigo:

            if cantidad <= 0:
                return False, "La cantidad debe ser mayor que cero."

            producto["stock"] += cantidad

            guardar_datos(RUTA_PRODUCTOS, productos)

            return True, "Stock actualizado correctamente."

    return False, "Producto no encontrado."


def retirar_stock(codigo, cantidad):

    productos = cargar_datos(RUTA_PRODUCTOS)

    for producto in productos:

        if producto["codigo"] == codigo:

            if cantidad <= 0:
                return False, "Cantidad inválida."

            if cantidad > producto["stock"]:
                return False, "No hay suficiente stock."

            producto["stock"] -= cantidad

            guardar_datos(RUTA_PRODUCTOS, productos)

            return True, "Salida de inventario registrada."

    return False, "Producto no encontrado."


def verificar_stock_minimo():

    productos = cargar_datos(RUTA_PRODUCTOS)

    productos_bajos = []

    for producto in productos:

        if producto["stock"] <= producto["stock_minimo"]:
            productos_bajos.append(producto)

    return productos_bajos