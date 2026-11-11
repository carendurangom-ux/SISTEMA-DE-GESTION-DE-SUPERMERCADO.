from PERSISTENCIA.archivos_json import cargar_datos, guardar_datos


RUTA_PRODUCTOS = "datos/productos.json"


def obtener_productos():
    return cargar_datos(RUTA_PRODUCTOS)


def registrar_producto(codigo, nombre, categoria,
                    precio_compra, precio_venta,
                    stock, stock_minimo):

    # Normalizar texto
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    categoria = str(categoria).strip()

    # Validar campos obligatorios
    if not codigo or not nombre or not categoria:
        return False, "Código, nombre y categoría son obligatorios."

    # Validar tipos numéricos
    try:
        precio_compra = float(precio_compra)
        precio_venta = float(precio_venta)
        stock = int(stock)
        stock_minimo = int(stock_minimo)
    except (TypeError, ValueError):
        return False, "Precios y stock deben ser valores numéricos."

    productos = obtener_productos()

    # Validar código duplicado
    for producto in productos:
        if producto.get("codigo", "").upper() == codigo:
            return False, "El código del producto ya existe."

    # Validar valores
    if precio_compra < 0 or precio_venta < 0:
        return False, "Los precios no pueden ser negativos."

    if precio_venta < precio_compra:
        return False, "El precio de venta no puede ser menor al de compra."

    if stock < 0 or stock_minimo < 0:
        return False, "El stock no puede ser negativo."

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "stock": stock,
        "stock_minimo": stock_minimo,
        "activo": True,
    }

    productos.append(nuevo_producto)
    guardar_datos(RUTA_PRODUCTOS, productos)

    return True, "Producto registrado correctamente."


def buscar_producto(codigo):
    codigo = str(codigo).strip().upper()

    for producto in obtener_productos():
        if producto.get("codigo", "").upper() == codigo:
            return producto

    return None