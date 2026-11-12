"""Pruebas del sistema (capa de negocio y persistencia).

Ejecutar desde la raíz del proyecto:
    python -m unittest Test_sistema.test_sistema -v
"""
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from PERSISTENCIA import archivos_json
from PERSISTENCIA.archivos_json import ErrorPersistencia
from NEGOCIO.validaciones import ErrorNegocio
from NEGOCIO import productos, inventario, caja, ventas


class BasePrueba(unittest.TestCase):
    def setUp(self):
        self.original = archivos_json.obtener_directorio()
        self.tmp = tempfile.mkdtemp()
        archivos_json.configurar_directorio(self.tmp)

    def tearDown(self):
        archivos_json.configurar_directorio(self.original)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def crear(self, codigo="P001", stock=10, minimo=3, precio=2500):
        return productos.crear_producto(codigo, "Arroz", "Granos", 1800, precio, stock, minimo)

    def vender(self, codigo="P001", cantidad=2, descuento=0, pago=100000):
        carrito = []
        ventas.agregar_al_carrito(carrito, codigo, cantidad)
        return ventas.confirmar_venta(carrito, descuento, pago)


class PruebasProductos(BasePrueba):
    def test_01_crear_producto_valido(self):
        """CP-01: registrar producto válido -> queda guardado y activo."""
        self.crear()
        guardados = productos.cargar_productos()
        self.assertEqual(len(guardados), 1)
        self.assertTrue(guardados[0]["activo"])

    def test_02_codigo_duplicado_rechazado(self):
        """CP-02: código repetido -> error y datos sin alterar."""
        self.crear()
        with self.assertRaises(ErrorNegocio):
            productos.crear_producto("p001", "Otro", "X", 1, 2, 5, 1)
        self.assertEqual(len(productos.cargar_productos()), 1)

    def test_03_valores_negativos_rechazados(self):
        """CP-03: precio o stock negativo -> error."""
        with self.assertRaises(ErrorNegocio):
            productos.crear_producto("P9", "X", "Y", -1, 5, 1, 1)
        with self.assertRaises(ErrorNegocio):
            productos.crear_producto("P9", "X", "Y", 1, 5, -4, 1)
        self.assertEqual(productos.cargar_productos(), [])

    def test_04_campos_obligatorios_y_tipos(self):
        """CP-04: nombre vacío y texto en campo numérico -> error."""
        with self.assertRaises(ErrorNegocio):
            productos.crear_producto("P9", "  ", "Y", 1, 5, 1, 1)
        with self.assertRaises(ErrorNegocio):
            productos.crear_producto("P9", "X", "Y", "abc", 5, 1, 1)

    def test_05_editar_y_desactivar(self):
        """CP-05: editar precio y desactivar -> no aparece en búsquedas activas."""
        self.crear()
        productos.editar_producto("P001", "Arroz Premium", "Granos", 1900, 2800, 4)
        self.assertEqual(productos.buscar_producto("P001")["precio_venta"], 2800)
        productos.cambiar_estado("P001", False)
        self.assertEqual(productos.buscar_productos("arroz"), [])
        self.assertEqual(len(productos.buscar_productos("arroz", solo_activos=False)), 1)


class PruebasInventario(BasePrueba):
    def test_06_entrada_aumenta_stock(self):
        """CP-06: entrada de 5 unidades -> stock 15 y movimiento registrado."""
        self.crear()
        producto, _ = inventario.registrar_movimiento("P001", "entrada", 5, "Compra")
        self.assertEqual(producto["stock"], 15)
        self.assertEqual(len(inventario.listar_movimientos("P001")), 1)

    def test_07_salida_mayor_al_stock_rechazada(self):
        """CP-07: salida superior a existencias -> error sin cambiar stock."""
        self.crear()
        with self.assertRaises(ErrorNegocio):
            inventario.registrar_movimiento("P001", "salida", 11)
        self.assertEqual(productos.buscar_producto("P001")["stock"], 10)

    def test_08_alerta_stock_minimo(self):
        """CP-08: stock <= mínimo genera alerta."""
        self.crear(stock=5, minimo=3)
        _, alerta = inventario.registrar_movimiento("P001", "salida", 2)
        self.assertTrue(alerta)
        self.assertEqual(len(inventario.productos_en_alerta()), 1)


class PruebasVentas(BasePrueba):
    def setUp(self):
        super().setUp()
        self.crear(stock=10)

    def test_09_venta_sin_caja_abierta(self):
        """CP-09: vender sin caja abierta -> error y sin factura."""
        with self.assertRaises(ErrorNegocio):
            self.vender()
        self.assertEqual(ventas.cargar_ventas(), [])

    def test_10_venta_exitosa(self):
        """CP-10: venta válida -> factura consecutiva, stock y caja actualizados."""
        caja.abrir_caja(100000)
        f1 = self.vender(cantidad=2)
        f2 = self.vender(cantidad=1)
        self.assertEqual((f1["numero"], f2["numero"]), (1, 2))
        self.assertEqual(productos.buscar_producto("P001")["stock"], 7)
        self.assertEqual(caja.calcular_esperado(caja.sesion_abierta()), 100000 + f1["total"] + f2["total"])

    def test_11_venta_supera_existencias(self):
        """CP-11: pedir más que el stock -> sin factura y stock intacto."""
        caja.abrir_caja(0)
        with self.assertRaises(ErrorNegocio):
            ventas.agregar_al_carrito([], "P001", 11)
        self.assertEqual(ventas.cargar_ventas(), [])
        self.assertEqual(productos.buscar_producto("P001")["stock"], 10)

    def test_12_pago_insuficiente(self):
        """CP-12: pago menor al total -> error y sin cambios."""
        caja.abrir_caja(0)
        with self.assertRaises(ErrorNegocio):
            self.vender(cantidad=2, pago=1000)
        self.assertEqual(productos.buscar_producto("P001")["stock"], 10)

    def test_13_descuento_e_impuesto(self):
        """CP-13: 2 x 2500, 10 % desc., 19 % IVA -> total 5355 y cambio correcto."""
        carrito = []
        ventas.agregar_al_carrito(carrito, "P001", 2)
        t = ventas.calcular_totales(carrito, 10)
        self.assertEqual((t["subtotal"], t["descuento"], t["impuestos"], t["total"]),
                         (5000.0, 500.0, 855.0, 5355.0))
        self.assertEqual(ventas.calcular_cambio(t["total"], 6000), 645.0)

    def test_14_descuento_excesivo_o_cantidad_invalida(self):
        """CP-14: descuento > máximo y cantidad 0 / texto -> error."""
        carrito = []
        ventas.agregar_al_carrito(carrito, "P001", 1)
        with self.assertRaises(ErrorNegocio):
            ventas.calcular_totales(carrito, 80)
        for invalida in (0, -2, "dos"):
            with self.assertRaises(ErrorNegocio):
                ventas.agregar_al_carrito(carrito, "P001", invalida)

    def test_15_devolucion_parcial(self):
        """CP-15: devolver 1 de 2 -> estado parcial, stock +1, caja -valor."""
        caja.abrir_caja(100000)
        factura = self.vender(cantidad=2)
        actualizada, valor = ventas.registrar_devolucion(factura["numero"], {"P001": 1})
        self.assertEqual(actualizada["estado"], "Devolución parcial")
        self.assertEqual(valor, 2975.0)
        self.assertEqual(productos.buscar_producto("P001")["stock"], 9)
        self.assertEqual(caja.calcular_esperado(caja.sesion_abierta()), 100000 + 5950 - 2975)

    def test_16_devolucion_excede_vendido(self):
        """CP-16: devolver más de lo vendido o factura inexistente -> error."""
        caja.abrir_caja(100000)
        factura = self.vender(cantidad=2)
        with self.assertRaises(ErrorNegocio):
            ventas.registrar_devolucion(factura["numero"], {"P001": 3})
        with self.assertRaises(ErrorNegocio):
            ventas.registrar_devolucion(99, {"P001": 1})
        self.assertEqual(productos.buscar_producto("P001")["stock"], 8)

    def test_17_devolucion_total_cuadra_con_total_factura(self):
        """CP-17: devolución en dos pasos suma exactamente el total de la factura."""
        caja.abrir_caja(100000)
        factura = self.vender(cantidad=3, descuento=7)
        ventas.registrar_devolucion(factura["numero"], {"P001": 1})
        final, _ = ventas.registrar_devolucion(factura["numero"], {"P001": 2})
        self.assertEqual(final["estado"], "Devuelta")
        self.assertEqual(round(sum(d["valor"] for d in final["devoluciones"]), 2), final["total"])

    def test_18_reporte_por_fechas(self):
        """CP-18: reporte de hoy y validación de fechas."""
        caja.abrir_caja(100000)
        self.vender(cantidad=2)
        hoy = ventas.ahora()[:10]
        rep = ventas.reporte_ventas(hoy, hoy)
        self.assertEqual((rep["num_facturas"], rep["unidades_vendidas"]), (1, 2))
        self.assertEqual(rep["mas_vendidos"][0]["codigo"], "P001")
        with self.assertRaises(ErrorNegocio):
            ventas.reporte_ventas("2026/01/01", hoy)
        with self.assertRaises(ErrorNegocio):
            ventas.reporte_ventas(hoy, "2020-01-01")


class PruebasCaja(BasePrueba):
    def test_19_no_abrir_dos_cajas(self):
        """CP-19: abrir caja con otra abierta -> error."""
        caja.abrir_caja(50000)
        with self.assertRaises(ErrorNegocio):
            caja.abrir_caja(10000)

    def test_20_cierre_muestra_diferencia_exacta(self):
        """CP-20: declarar menos efectivo -> diferencia exacta negativa."""
        self.crear()
        caja.abrir_caja(100000)
        self.vender(cantidad=2)                       # +5950
        caja.registrar_efectivo("egreso", "Compra de bolsas", 1000)
        sesion = caja.cerrar_caja(104000)
        self.assertEqual(sesion["valor_esperado"], 104950.0)
        self.assertEqual(sesion["diferencia"], -950.0)
        self.assertEqual(sesion["estado"], "Cerrada")
        self.assertIsNone(caja.sesion_abierta())

    def test_21_egreso_mayor_al_efectivo(self):
        """CP-21: egreso superior al efectivo disponible -> error."""
        caja.abrir_caja(1000)
        with self.assertRaises(ErrorNegocio):
            caja.registrar_efectivo("egreso", "Pago", 5000)


class PruebasPersistencia(BasePrueba):
    def test_22_datos_se_conservan_al_reabrir(self):
        """CP-22: tras 'reiniciar' (releer archivos) todo sigue guardado."""
        self.crear()
        caja.abrir_caja(100000)
        self.vender(cantidad=2)
        self.assertEqual(len(productos.cargar_productos()), 1)
        self.assertEqual(len(ventas.cargar_ventas()), 1)
        self.assertEqual(len(caja.cargar_caja()["sesiones"]), 1)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "ventas.json")))

    def test_23_archivo_corrupto(self):
        """CP-23: JSON dañado -> ErrorPersistencia informativo."""
        with open(os.path.join(self.tmp, "productos.json"), "w", encoding="utf-8") as f:
            f.write("{{ no es json")
        with self.assertRaises(ErrorPersistencia):
            productos.cargar_productos()

    def test_24_escritura_fallida_conserva_original(self):
        """CP-24: si la escritura falla, el archivo original no se daña ni quedan temporales."""
        self.crear()
        with self.assertRaises(ErrorPersistencia):
            archivos_json.guardar("productos", {1, 2, 3})   # un set no es serializable
        self.assertEqual(len(productos.cargar_productos()), 1)
        self.assertEqual([a for a in os.listdir(self.tmp) if a.endswith(".tmp")], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
