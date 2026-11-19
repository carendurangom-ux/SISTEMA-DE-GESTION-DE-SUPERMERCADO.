import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from NEGOCIO import caja, ErrorNegocio
from INTERFAZ.datos_ui import TablaDatos


class VentanaCaja(tk.Toplevel):
    def __init__(self, parent, tienda):
        super().__init__(parent)
        self.tienda = tienda
        self.title("Control de Caja")
        self.geometry("700x500")
        self.crear_widgets()
        self.actualizar_estado()

    def crear_widgets(self):
        marco_estado = ttk.LabelFrame(self, text="Estado Actual", padding="10")
        marco_estado.pack(fill=tk.X, padx=10, pady=5)

        self.estado_label = ttk.Label(marco_estado, text="", font=("Arial", 12, "bold"))
        self.estado_label.pack()

        marco_abrir = ttk.Frame(marco_estado)
        marco_abrir.pack(fill=tk.X, pady=5)
        ttk.Label(marco_abrir, text="Saldo inicial:").pack(side=tk.LEFT)
        self.saldo_entry = ttk.Entry(marco_abrir, width=15)
        self.saldo_entry.pack(side=tk.LEFT, padx=5)
        self.abrir_btn = ttk.Button(marco_abrir, text="Abrir Caja", command=self.abrir_caja)
        self.abrir_btn.pack(side=tk.LEFT, padx=5)
        self.cerrar_btn = ttk.Button(marco_abrir, text="Cerrar Caja", command=self.cerrar_caja)
        self.cerrar_btn.pack(side=tk.LEFT, padx=5)

        marco_mov = ttk.LabelFrame(self, text="Movimientos de Efectivo", padding="10")
        marco_mov.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(marco_mov, text="Tipo:").grid(row=0, column=0, sticky="w")
        self.tipo_var = tk.StringVar(value="ingreso")
        ttk.Radiobutton(marco_mov, text="Ingreso", variable=self.tipo_var,
                        value="ingreso").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(marco_mov, text="Egreso", variable=self.tipo_var,
                        value="egreso").grid(row=0, column=2, padx=5)

        ttk.Label(marco_mov, text="Concepto:").grid(row=1, column=0, sticky="w", pady=5)
        self.concepto_entry = ttk.Entry(marco_mov, width=30)
        self.concepto_entry.grid(row=1, column=1, columnspan=2, padx=5)

        ttk.Label(marco_mov, text="Monto:").grid(row=2, column=0, sticky="w")
        self.monto_entry = ttk.Entry(marco_mov, width=30)
        self.monto_entry.grid(row=2, column=1, columnspan=2, padx=5)

        ttk.Button(marco_mov, text="Registrar Movimiento",
                   command=self.registrar_movimiento).grid(row=3, column=0, columnspan=3, pady=10)

        columnas = ["fecha", "tipo", "concepto", "monto"]
        self.tabla = TablaDatos(self, columnas, "Historial de Sesiones")
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.cargar_historial()

    def actualizar_estado(self):
        sesion = caja.sesion_abierta()
        if sesion:
            self.estado_label.config(text="✅ CAJA ABIERTA", foreground="green")
            self.abrir_btn.state(["disabled"])
            self.cerrar_btn.state(["!disabled"])
        else:
            self.estado_label.config(text="❌ CAJA CERRADA", foreground="red")
            self.abrir_btn.state(["!disabled"])
            self.cerrar_btn.state(["disabled"])

    def abrir_caja(self):
        try:
            saldo = float(self.saldo_entry.get())
            caja.abrir_caja(saldo)
            messagebox.showinfo("Éxito", "Caja abierta correctamente")
            self.saldo_entry.delete(0, tk.END)
            self.actualizar_estado()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def cerrar_caja(self):
        respuesta = messagebox.askyesno("Confirmar", "¿Desea cerrar la caja?")
        if not respuesta:
            return
        declarado = simpledialog.askfloat("Cerrar Caja",
                                          "Ingrese el efectivo que hay en caja:")
        if declarado is None:
            return
        try:
            sesion = caja.cerrar_caja(declarado)
            diferencia = sesion["diferencia"]
            msg = f"""Caja cerrada:
Esperado: ${sesion['valor_esperado']:.2f}
Declarado: ${sesion['efectivo_declarado']:.2f}
Diferencia: ${diferencia:.2f}
"""
            if abs(diferencia) < 0.01:
                msg += "✅ Cuadre exacto"
            elif diferencia > 0:
                msg += "⚠️ Sobrante de dinero"
            else:
                msg += "⚠️ Faltante de dinero"
            messagebox.showinfo("Caja Cerrada", msg)
            self.actualizar_estado()
            self.cargar_historial()
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def registrar_movimiento(self):
        try:
            tipo = self.tipo_var.get()
            concepto = self.concepto_entry.get().strip()
            monto = float(self.monto_entry.get())

            if not concepto:
                messagebox.showwarning("Aviso", "Ingrese un concepto")
                return

            caja.registrar_efectivo(tipo, concepto, monto)
            messagebox.showinfo("Éxito", "Movimiento registrado")
            self.concepto_entry.delete(0, tk.END)
            self.monto_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
        except ErrorNegocio as e:
            messagebox.showerror("Error", str(e))

    def cargar_historial(self):
        datos = caja.cargar_caja()
        filas = []
        for sesion in datos["sesiones"]:
            filas.append({
                "fecha": sesion.get("fecha_apertura", ""),
                "tipo": sesion.get("estado", ""),
                "concepto": f"Saldo inicial: ${sesion.get('saldo_inicial', 0):.2f}",
                "monto": f"${sesion.get('valor_esperado', 0):.2f}"
            })
        self.tabla.cargar_datos(filas)
