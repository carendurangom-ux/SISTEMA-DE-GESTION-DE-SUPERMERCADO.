import tkinter as tk
from tkinter import ttk
from .productos import ProductosFrame
from .inventario import InventarioFrame
from .ventas import VentasFrame
from .caja import CajaFrame
from .datos_ui import productos, ventas, caja, dinero

class App:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("NEXUS | Gestión de supermercado")
        self.root.geometry("1180x720")
        self.root.minsize(980, 620)
        self.root.configure(bg="#11171d")
        self._estilos()
        self._interfaz()
        self.mostrar("Inicio")

    def _estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Page.TFrame", background="#171f27")
        estilo.configure("TFrame", background="#171f27")
        estilo.configure("TLabel", background="#171f27", foreground="#e8edf2", font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", background="#171f27", foreground="#f4f7fa",
                         font=("Segoe UI", 23, "bold"))
        estilo.configure("Muted.TLabel", background="#171f27", foreground="#9aa8b5",
                         font=("Segoe UI", 10))
        estilo.configure("Section.TLabel", background="#171f27", foreground="#e8edf2",
                         font=("Segoe UI", 13, "bold"))
        estilo.configure("TButton", background="#2a3540", foreground="#eaf0f5",
                         borderwidth=0, padding=(13, 9), font=("Segoe UI", 9, "bold"))
        estilo.map("TButton", background=[("active", "#3a4855")])
        estilo.configure("Accent.TButton", background="#16a36a", foreground="white")
        estilo.map("Accent.TButton", background=[("active", "#128454")])
        estilo.configure("Danger.TButton", background="#813e45", foreground="white")
        estilo.map("Danger.TButton", background=[("active", "#a94b55")])
        estilo.configure("Treeview", background="#202a33", fieldbackground="#202a33",
                         foreground="#e7edf2", rowheight=32, borderwidth=0,
                         font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", background="#2a3742", foreground="#dce5ec",
                         font=("Segoe UI", 9, "bold"), relief="flat")
        estilo.map("Treeview", background=[("selected", "#176b4b")])

    def _interfaz(self):
        contenedor = tk.Frame(self.root, bg="#11171d")
        contenedor.pack(fill="both", expand=True)

        lateral = tk.Frame(contenedor, bg="#101820", width=220)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)

        tk.Label(lateral, text="NEXUS", bg="#101820", fg="#20c982",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=23, pady=(28, 0))
        tk.Label(lateral, text="SUPERMARKET SYSTEM", bg="#101820", fg="#82919e",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 30))

        self.botones = {}
        for nombre, icono in [("Inicio", "⌂"), ("Productos", "▦"), ("Inventario", "▤"),
                              ("Ventas", "$"), ("Caja", "◷")]:
            b = tk.Button(lateral, text=f"   {icono}   {nombre}", anchor="w",
                          command=lambda n=nombre: self.mostrar(n),
                          bg="#101820", fg="#bdc8d1", activebackground="#1c2b33",
                          activeforeground="#20c982", relief="flat", bd=0,
                          font=("Segoe UI", 10, "bold"), padx=15, pady=13, cursor="hand2")
            b.pack(fill="x", padx=12, pady=2)
            self.botones[nombre] = b

        tk.Label(lateral, text="Panel administrativo\nVersión de escritorio",
                 justify="left", bg="#101820", fg="#71808c",
                 font=("Segoe UI", 8)).pack(side="bottom", anchor="w", padx=24, pady=22)

        principal = tk.Frame(contenedor, bg="#171f27")
        principal.pack(side="left", fill="both", expand=True)
        barra = tk.Frame(principal, bg="#171f27", height=58)
        barra.pack(fill="x", padx=22, pady=(13, 0))
        barra.pack_propagate(False)
        self.titulo = tk.Label(barra, text="Panel general", bg="#171f27", fg="#f4f7fa",
                               font=("Segoe UI", 11, "bold"))
        self.titulo.pack(side="left", anchor="center")
        tk.Label(barra, text="● Sistema activo", bg="#171f27", fg="#20c982",
                 font=("Segoe UI", 9, "bold")).pack(side="right", anchor="center")
        self.area = tk.Frame(principal, bg="#171f27")
        self.area.pack(fill="both", expand=True)

    def _limpiar(self):
        for widget in self.area.winfo_children():
            widget.destroy()

    def mostrar(self, pagina):
        self._limpiar()
        for nombre, boton in self.botones.items():
            boton.configure(bg="#1b2b32" if nombre == pagina else "#101820",
                            fg="#20c982" if nombre == pagina else "#bdc8d1")
        self.titulo.configure(text=pagina)
        if pagina == "Inicio":
            self._inicio()
        else:
            clase = {"Productos": ProductosFrame, "Inventario": InventarioFrame,
                     "Ventas": VentasFrame, "Caja": CajaFrame}[pagina]
            clase(self.area).pack(fill="both", expand=True)

    def _inicio(self):
        frame = ttk.Frame(self.area, style="Page.TFrame", padding=25)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Panel de control", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Resumen general de la operación del supermercado.",
                  style="Muted.TLabel").pack(anchor="w", pady=(3, 22))

        lista = productos()
        total_stock = sum(int(p.get("stock", 0) or 0) for p in lista)
        bajo = sum(1 for p in lista if int(p.get("stock", 0) or 0) <= int(p.get("stock_minimo", 0) or 0))
        total_ventas = sum(float(v.get("total", 0) or 0) for v in ventas())
        tarjetas = tk.Frame(frame, bg="#171f27")
        tarjetas.pack(fill="x", pady=(0, 22))
        datos = [
            ("PRODUCTOS REGISTRADOS", str(len(lista))),
            ("UNIDADES EN INVENTARIO", str(total_stock)),
            ("STOCK BAJO", str(bajo)),
            ("VENTAS ACUMULADAS", dinero(total_ventas))
        ]
        for titulo, valor in datos:
            tarjeta = tk.Frame(tarjetas, bg="#222d37", padx=18, pady=18)
            tarjeta.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(tarjeta, text=titulo, bg="#222d37", fg="#9eacb8",
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(tarjeta, text=valor, bg="#222d37", fg="#20c982",
                     font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(8, 0))

        ttk.Label(frame, text="Accesos rápidos", style="Section.TLabel").pack(anchor="w", pady=(8, 12))
        accesos = ttk.Frame(frame, style="Page.TFrame")
        accesos.pack(anchor="w")
        for nombre in ("Productos", "Inventario", "Ventas", "Caja"):
            ttk.Button(accesos, text=nombre, command=lambda n=nombre: self.mostrar(n)).pack(side="left", padx=(0, 9))

        ttk.Label(frame, text="Estado del sistema", style="Section.TLabel").pack(anchor="w", pady=(35, 10))
        ttk.Label(frame, text="Los datos se guardan localmente en la carpeta DATOS.",
                  style="Muted.TLabel").pack(anchor="w")
        sesiones = caja().get("sesiones", [])
        abierta = any(s.get("estado") == "Abierta" for s in sesiones)
        ttk.Label(frame, text="Caja: " + ("Abierta" if abierta else "Cerrada"),
                  foreground="#20c982" if abierta else "#e89a91").pack(anchor="w", pady=(8, 0))

    def run(self):
        self.root.mainloop()

def iniciar():
    App().run()

if __name__ == "__main__":
    iniciar()
