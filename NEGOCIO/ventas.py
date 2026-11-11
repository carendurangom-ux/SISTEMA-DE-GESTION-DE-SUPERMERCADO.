from datetime import datetime

from Persistencia.Archivos_json import leer_json, guardar_json
from Negocio import Productos, Inventario, Caja

ARCHIVO = "Ventas.json"


def listar_ventas():
    datos = leer_json(ARCHIVO, [])
    return datos if isinstance(datos, list) else []


def registrar_venta(items):
    """items: lista de tuplas (codigo, cantidad)."""
    if not items:
        raise ValueError("La venta no tiene productos.")

    # Unir códigos repetidos para validar bien el stock
    acumulado = {}
    for codigo, cantidad in items:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        acumulado[codigo] = acumulado.get(codigo, 0) + cantidad

    # Validar todo antes de modificar nada
    detalle = []
    total = 0
    for codigo, cantidad in acumulado.items():
        producto = Productos.buscar_producto(codigo)
        if producto is None:
            raise ValueError(f"No existe el producto {codigo}.")
        if producto["cantidad"] < cantidad:
            raise ValueError(
                f"Stock insuficiente de {producto['nombre']} "
                f"(disponible: {producto['cantidad']})."
            )
        subtotal = round(producto["precio"] * cantidad, 2)
        total += subtotal
        detalle.append({
            "codigo": codigo,
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "precio": producto["precio"],
            "subtotal": subtotal,
        })

    # Aplicar cambios
    for linea in detalle:
        Inventario.descontar_stock(linea["codigo"], linea["cantidad"])
    total = round(total, 2)
    if total > 0:
        Caja.registrar_ingreso(total)

    ventas = listar_ventas()
    venta = {
        "id": len(ventas) + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detalle": detalle,
        "total": total,
    }
    ventas.append(venta)
    guardar_json(ARCHIVO, ventas)
    return venta