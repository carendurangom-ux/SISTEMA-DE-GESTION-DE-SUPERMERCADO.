from Persistencia.Archivos_json import leer_json, guardar_json

ARCHIVO = "Productos.json"


def listar_productos():
    datos = leer_json(ARCHIVO, [])
    return datos if isinstance(datos, list) else []


def guardar_productos(productos):
    guardar_json(ARCHIVO, productos)


def buscar_producto(codigo):
    for producto in listar_productos():
        if producto["codigo"] == codigo:
            return producto
    return None


def agregar_producto(codigo, nombre, precio, cantidad):
    if not codigo or not nombre:
        raise ValueError("El código y el nombre son obligatorios.")
    if precio < 0 or cantidad < 0:
        raise ValueError("El precio y la cantidad no pueden ser negativos.")
    if buscar_producto(codigo):
        raise ValueError(f"Ya existe un producto con el código {codigo}.")
    productos = listar_productos()
    productos.append({
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "cantidad": cantidad,
    })
    guardar_productos(productos)


def editar_producto(codigo, nombre=None, precio=None):
    productos = listar_productos()
    for producto in productos:
        if producto["codigo"] == codigo:
            if nombre:
                producto["nombre"] = nombre
            if precio is not None:
                if precio < 0:
                    raise ValueError("El precio no puede ser negativo.")
                producto["precio"] = precio
            guardar_productos(productos)
            return
    raise ValueError(f"No existe el producto {codigo}.")


def eliminar_producto(codigo):
    productos = listar_productos()
    nuevos = [p for p in productos if p["codigo"] != codigo]
    if len(nuevos) == len(productos):
        raise ValueError(f"No existe el producto {codigo}.")
    guardar_productos(nuevos)