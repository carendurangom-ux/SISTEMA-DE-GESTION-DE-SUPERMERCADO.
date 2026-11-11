from Negocio import Productos


def agregar_stock(codigo, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    productos = Productos.listar_productos()
    for producto in productos:
        if producto["codigo"] == codigo:
            producto["cantidad"] += cantidad
            Productos.guardar_productos(productos)
            return
    raise ValueError(f"No existe el producto {codigo}.")


def descontar_stock(codigo, cantidad):
    productos = Productos.listar_productos()
    for producto in productos:
        if producto["codigo"] == codigo:
            if producto["cantidad"] < cantidad:
                raise ValueError(f"Stock insuficiente de {producto['nombre']}.")
            producto["cantidad"] -= cantidad
            Productos.guardar_productos(productos)
            return
    raise ValueError(f"No existe el producto {codigo}.")


def productos_bajo_stock(minimo=5):
    return [p for p in Productos.listar_productos() if p["cantidad"] <= minimo]