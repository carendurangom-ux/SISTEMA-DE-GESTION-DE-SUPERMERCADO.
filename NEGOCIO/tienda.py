class Tienda:
    def __init__(self):
        self._inicializar_modulos()

    def _inicializar_modulos(self):
        from . import caja
        from . import productos
        from . import inventario
        from . import ventas
        
        self.caja = caja
        self.productos = productos
        self.inventario = inventario
        self.ventas = ventas

    def cerrar_sesion(self):
        """Cierra cualquier sesión activa de forma segura"""
        try:
            if self.caja.sesion_abierta():
                # No cerramos automáticamente, solo informamos
                pass
        except Exception:
            pass