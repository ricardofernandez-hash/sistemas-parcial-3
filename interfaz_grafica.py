import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from excepciones import ConflictoHorarioError


class InterfazSistemaCitas:
    """Capa de Frontend: Interfaz gráfica completa en Tkinter/ttk."""

    def __init__(self, gestor):
        self._gestor = gestor
        self._gestor.cargar_desde_excel()

        self._root = tk.Tk()
        self._root.title("Sistema Integral de Gestión de Citas y Turnos - Parcial III")
        self._root.geometry("1120x680")
        self._root.minsize(980, 620)
        self._root.configure(bg="#F0F4F8")

        self._cita_seleccionada_id = None
        self._configurar_estilos()
        self._crear_menu()
        self._construir_interfaz_principal()
        self._refrescar_combos()
        self._refrescar_tabla_citas()
        self._refrescar_tabla_clientes()
        self._refrescar_tabla_facturas()

    def iniciar(self):
        self._root.mainloop()

    # ---- ESTILOS VISUALES ----
    def _configurar_estilos(self):
        style = ttk.Style(self._root)
        style.theme_use("clam")
        style.configure("TFrame", background="#F0F4F8")
        style.configure("Card.TFrame", background="#FFFFFF", relief="groove", borderwidth=1)
        style.configure("TLabel", background="#F0F4F8", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#FFFFFF", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#1F4E78", foreground="white", font=("Segoe UI", 14, "bold"))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#D9E1F2")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))

    # ---- BARRA DE MENÚ SUPERIOR (Menu) ----
    def _crear_menu(self):
        barra_menu = tk.Menu(self._root)

        # Menú Archivo (filedialog + persistencia Excel)
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        menu_archivo.add_command(label="Guardar todo en Excel", command=self._accion_guardar_excel)
        menu_archivo.add_command(label="Exportar copia de Excel...", command=self._accion_exportar_excel)
        menu_archivo.add_command(label="Cargar otro archivo Excel...", command=self._accion_abrir_excel)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self._root.quit)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Gestión (Ventanas Toplevel)
        menu_gestion = tk.Menu(barra_menu, tearoff=0)
        menu_gestion.add_command(label="Registrar Nuevo Cliente...", command=self._abrir_ventana_cliente)
        menu_gestion.add_command(label="Registrar Nuevo Profesional...", command=self._abrir_ventana_profesional)
        menu_gestion.add_command(label="Registrar Nuevo Servicio...", command=self._abrir_ventana_servicio)
        barra_menu.add_cascade(label="Gestión", menu=menu_gestion)

        # Menú Ayuda
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca del Sistema", command=self._mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        self._root.config(menu=barra_menu)

    # ---- CONSTRUCCIÓN DE LA INTERFAZ PRINCIPAL ----
    def _construir_interfaz_principal(self):
        # Encabezado superior
        frame_header = tk.Frame(self._root, bg="#1F4E78", height=52)
        frame_header.pack(fill="x")
        tk.Label(
            frame_header,
            text="  SISTEMA DE GESTIÓN DE CITAS, TURNOS Y FACTURACIÓN",
            bg="#1F4E78", fg="white", font=("Segoe UI", 13, "bold")
        ).pack(side="left", pady=12)

        self._lbl_archivo_activo = tk.Label(
            frame_header,
            text=f"BD Excel: {self._gestor.get_backend().get_ruta_archivo()}  ",
            bg="#1F4E78", fg="#D9E1F2", font=("Segoe UI", 9)
        )
        self._lbl_archivo_activo.pack(side="right", pady=12)

        # ELEMENTO ADICIONAL INVESTIGADO: ttk.Notebook (Pestañas)
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self._tab_agenda = ttk.Frame(self._notebook)
        self._tab_clientes = ttk.Frame(self._notebook)
        self._tab_facturas = ttk.Frame(self._notebook)

        self._notebook.add(self._tab_agenda, text="  📅 Agenda y Turnos  ")
        self._notebook.add(self._tab_clientes, text="  👥 Clientes y Profesionales  ")
        self._notebook.add(self._tab_facturas, text="  💳 Facturación e Ingresos  ")

        self._construir_tab_agenda()
        self._construir_tab_clientes()
        self._construir_tab_facturas()

    # ---- PESTAÑA 1: AGENDA Y TURNOS ----
    def _construir_tab_agenda(self):
        # Panel Izquierdo: Formulario de Agendamiento / Edición
        frame_izq = ttk.Frame(self._tab_agenda, style="Card.TFrame", padding=14)
        frame_izq.pack(side="left", fill="y", padx=(0, 10), pady=5)

        ttk.Label(frame_izq, text="Gestión de Cita", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Cliente (Combobox + Botón rápido Toplevel)
        ttk.Label(frame_izq, text="Cliente:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        frame_cli_row = ttk.Frame(frame_izq, style="Card.TFrame")
        frame_cli_row.grid(row=1, column=1, sticky="ew", pady=4)
        self._combo_cliente = ttk.Combobox(frame_cli_row, state="readonly", width=22)
        self._combo_cliente.pack(side="left")
        ttk.Button(frame_cli_row, text="+", width=3, command=self._abrir_ventana_cliente).pack(side="left", padx=(4, 0))

        # Profesional (Combobox)
        ttk.Label(frame_izq, text="Profesional:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self._combo_profesional = ttk.Combobox(frame_izq, state="readonly", width=26)
        self._combo_profesional.grid(row=2, column=1, sticky="ew", pady=4)

        # Servicio (Combobox con evento .bind)
        ttk.Label(frame_izq, text="Servicio:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=4)
        self._combo_servicio = ttk.Combobox(frame_izq, state="readonly", width=26)
        self._combo_servicio.grid(row=3, column=1, sticky="ew", pady=4)
        self._combo_servicio.bind("<<ComboboxSelected>>", self._on_servicio_seleccionado)

        # Fecha (Entry)
        ttk.Label(frame_izq, text="Fecha (AAAA-MM-DD):", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        self._entry_fecha = ttk.Entry(frame_izq, width=28)
        self._entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self._entry_fecha.grid(row=4, column=1, sticky="ew", pady=4)

        # Hora (Entry)
        ttk.Label(frame_izq, text="Hora (HH:MM):", style="Card.TLabel").grid(row=5, column=0, sticky="w", pady=4)
        self._entry_hora = ttk.Entry(frame_izq, width=28)
        self._entry_hora.insert(0, "09:00")
        self._entry_hora.grid(row=5, column=1, sticky="ew", pady=4)

        # Duración y Precio (Entry)
        ttk.Label(frame_izq, text="Duración (min):", style="Card.TLabel").grid(row=6, column=0, sticky="w", pady=4)
        self._entry_duracion = ttk.Entry(frame_izq, width=28)
        self._entry_duracion.insert(0, "30")
        self._entry_duracion.grid(row=6, column=1, sticky="ew", pady=4)

        ttk.Label(frame_izq, text="Tarifa ($):", style="Card.TLabel").grid(row=7, column=0, sticky="w", pady=4)
        self._entry_precio = ttk.Entry(frame_izq, width=28)
        self._entry_precio.insert(0, "30000")
        self._entry_precio.grid(row=7, column=1, sticky="ew", pady=4)

        # Consultorio (Radiobutton)
        ttk.Label(frame_izq, text="Consultorio:", style="Card.TLabel").grid(row=8, column=0, sticky="nw", pady=6)
        frame_radios = ttk.Frame(frame_izq, style="Card.TFrame")
        frame_radios.grid(row=8, column=1, sticky="w", pady=4)
        self._var_consultorio = tk.StringVar(value="Consultorio 1")
        for sala in ("Consultorio 1", "Consultorio 2", "Sala VIP"):
            tk.Radiobutton(
                frame_radios, text=sala, variable=self._var_consultorio, value=sala,
                bg="#FFFFFF", font=("Segoe UI", 9)
            ).pack(anchor="w")

        # Checkbutton (Recordatorio / Prioridad)
        self._var_recordatorio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame_izq, text="Enviar recordatorio SMS al cliente",
            variable=self._var_recordatorio, bg="#FFFFFF", font=("Segoe UI", 9)
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=6)

        # Botones CRUD del Formulario
        frame_btns = ttk.Frame(frame_izq, style="Card.TFrame")
        frame_btns.grid(row=10, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame_btns, text="Agendar Cita", command=self._accion_agendar_cita).pack(fill="x", pady=2)
        ttk.Button(frame_btns, text="Actualizar Seleccionada", command=self._accion_actualizar_cita).pack(fill="x", pady=2)
        ttk.Button(frame_btns, text="Limpiar Formulario", command=self._limpiar_formulario_cita).pack(fill="x", pady=2)

        # Panel Derecho: Filtros, Treeview de Citas, Acciones de Estado y Progressbar
        frame_der = ttk.Frame(self._tab_agenda, style="Card.TFrame", padding=12)
        frame_der.pack(side="right", fill="both", expand=True, pady=5)

        # Barra de Filtros con .bind()
        frame_filtros = ttk.Frame(frame_der, style="Card.TFrame")
        frame_filtros.pack(fill="x", pady=(0, 8))

        ttk.Label(frame_filtros, text="Filtrar Fecha:", style="Card.TLabel").pack(side="left")
        self._entry_filtro_fecha = ttk.Entry(frame_filtros, width=13)
        self._entry_filtro_fecha.pack(side="left", padx=5)
        self._entry_filtro_fecha.bind("<KeyRelease>", lambda e: self._refrescar_tabla_citas())

        ttk.Label(frame_filtros, text="Estado:", style="Card.TLabel").pack(side="left", padx=(8, 0))
        self._combo_filtro_estado = ttk.Combobox(
            frame_filtros, state="readonly", width=13,
            values=["Todos", "pendiente", "confirmada", "completada", "cancelada"]
        )
        self._combo_filtro_estado.set("Todos")
        self._combo_filtro_estado.pack(side="left", padx=5)
        self._combo_filtro_estado.bind("<<ComboboxSelected>>", lambda e: self._refrescar_tabla_citas())

        ttk.Button(frame_filtros, text="Ver Todas", command=self._resetear_filtros).pack(side="left", padx=5)

        # Treeview de Citas
        columnas = ("ID", "Fecha", "Hora", "Cliente", "Servicio", "Profesional", "Sala", "Tarifa", "Estado")
        self._tree_citas = ttk.Treeview(frame_der, columns=columnas, show="headings", height=14)
        anchos = {"ID": 40, "Fecha": 85, "Hora": 60, "Cliente": 130, "Servicio": 130,
                  "Profesional": 115, "Sala": 90, "Tarifa": 75, "Estado": 85}
        for col in columnas:
            self._tree_citas.heading(col, text=col)
            self._tree_citas.column(col, width=anchos[col], anchor="center")

        self._tree_citas.pack(fill="both", expand=True)
        # Evento .bind() al seleccionar o hacer doble clic en una cita
        self._tree_citas.bind("<<TreeviewSelect>>", self._on_seleccionar_cita_tabla)
        self._tree_citas.bind("<Double-1>", lambda e: self._on_seleccionar_cita_tabla(e, notificar=True))

        # Botonera de Gestión de Estados y Eliminación
        frame_acciones = ttk.Frame(frame_der, style="Card.TFrame")
        frame_acciones.pack(fill="x", pady=8)

        ttk.Button(frame_acciones, text="✔ Confirmar Cita", command=self._accion_confirmar_cita).pack(side="left", padx=3)
        ttk.Button(frame_acciones, text="💰 Completar y Facturar", command=self._abrir_ventana_facturar).pack(side="left", padx=3)
        ttk.Button(frame_acciones, text="✖ Cancelar Cita", command=self._accion_cancelar_cita).pack(side="left", padx=3)
        ttk.Button(frame_acciones, text="🗑 Eliminar Registro", command=self._accion_eliminar_cita).pack(side="right", padx=3)

        # Segundo widget adicional: ttk.Progressbar (Indicador de ocupación de agenda)
        frame_prog = ttk.Frame(frame_der, style="Card.TFrame")
        frame_prog.pack(fill="x", pady=(4, 0))
        self._lbl_ocupacion = ttk.Label(frame_prog, text="Capacidad diaria ocupada: 0%", style="Card.TLabel")
        self._lbl_ocupacion.pack(side="left")
        self._progress_ocupacion = ttk.Progressbar(frame_prog, orient="horizontal", length=250, mode="determinate")
        self._progress_ocupacion.pack(side="right", fill="x", expand=True, padx=(10, 0))

    # ---- PESTAÑA 2: CLIENTES Y PROFESIONALES ----
    def _construir_tab_clientes(self):
        frame_top = ttk.Frame(self._tab_clientes, padding=8)
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="+ Nuevo Cliente", command=self._abrir_ventana_cliente).pack(side="left", padx=4)
        ttk.Button(frame_top, text="+ Nuevo Profesional", command=self._abrir_ventana_profesional).pack(side="left", padx=4)
        ttk.Button(frame_top, text="📊 Ver Historial del Cliente Seleccionado",
                   command=self._accion_ver_historial_cliente).pack(side="left", padx=4)
        ttk.Button(frame_top, text="🗑 Eliminar Cliente", command=self._accion_eliminar_cliente).pack(side="right", padx=4)

        cols_cli = ("ID", "Nombre Completo", "Teléfono", "Categoría / Rol")
        self._tree_clientes = ttk.Treeview(self._tab_clientes, columns=cols_cli, show="headings", height=16)
        for c in cols_cli:
            self._tree_clientes.heading(c, text=c)
            self._tree_clientes.column(c, anchor="center", width=180)
        self._tree_clientes.pack(fill="both", expand=True, padx=8, pady=5)

    # ---- PESTAÑA 3: FACTURACIÓN E INGRESOS ----
    def _construir_tab_facturas(self):
        frame_resumen = ttk.Frame(self._tab_facturas, padding=10)
        frame_resumen.pack(fill="x")
        self._lbl_total_ingresos = ttk.Label(
            frame_resumen, text="Total Ingresos Facturados: $0", font=("Segoe UI", 12, "bold")
        )
        self._lbl_total_ingresos.pack(side="left")

        cols_fac = ("ID Factura", "ID Cita", "Cliente", "Servicio", "Método de Pago", "Total Pagado", "Fecha Emisión")
        self._tree_facturas = ttk.Treeview(self._tab_facturas, columns=cols_fac, show="headings", height=16)
        for c in cols_fac:
            self._tree_facturas.heading(c, text=c)
            self._tree_facturas.column(c, anchor="center", width=140)
        self._tree_facturas.pack(fill="both", expand=True, padx=8, pady=5)

    # ---- EVENTOS Y ACTUALIZACIONES DE UI ----
    def _refrescar_combos(self):
        clientes = self._gestor.listar_clientes()
        self._combo_cliente["values"] = [f"{c.get_id()} - {c.get_nombre()}" for c in clientes]
        if clientes and not self._combo_cliente.get():
            self._combo_cliente.current(0)

        profs = self._gestor.listar_profesionales()
        self._combo_profesional["values"] = [f"{p.get_id()} - {p.get_nombre()} ({p.get_especialidad()})" for p in profs]
        if profs and not self._combo_profesional.get():
            self._combo_profesional.current(0)

        servs = self._gestor.listar_servicios()
        self._combo_servicio["values"] = [f"{s.get_nombre()} | {s.get_duracion()} min | ${s.get_precio():.0f}" for s in servs]
        if servs and not self._combo_servicio.get():
            self._combo_servicio.current(0)

    def _on_servicio_seleccionado(self, _event=None):
        texto = self._combo_servicio.get()
        if "|" in texto:
            partes = [p.strip() for p in texto.split("|")]
            dur = partes[1].replace("min", "").strip()
            precio = partes[2].replace("$", "").strip()
            self._entry_duracion.delete(0, tk.END)
            self._entry_duracion.insert(0, dur)
            self._entry_precio.delete(0, tk.END)
            self._entry_precio.insert(0, precio)

    def _refrescar_tabla_citas(self):
        for item in self._tree_citas.get_children():
            self._tree_citas.delete(item)

        filtro_fecha = self._entry_filtro_fecha.get().strip() or None
        filtro_estado = self._combo_filtro_estado.get() or "Todos"

        citas = self._gestor.listar_agenda(filtro_fecha, filtro_estado)
        activas = 0
        for c in citas:
            if c.esta_activa():
                activas += 1
            prof = c.get_profesional().get_nombre() if c.get_profesional() else "General"
            self._tree_citas.insert("", "end", values=(
                c.get_id(),
                c.get_inicio().strftime("%Y-%m-%d"),
                c.get_inicio().strftime("%H:%M"),
                c.get_cliente().get_nombre(),
                c.get_servicio(),
                prof,
                c.get_consultorio(),
                f"${c.get_precio():,.0f}",
                c.get_estado().upper(),
            ))

        # Actualizar barra de progreso (base 16 turnos diarios máximos)
        porcentaje = min(100, int((activas / 16) * 100))
        self._progress_ocupacion["value"] = porcentaje
        self._lbl_ocupacion.config(text=f"Citas activas mostradas: {activas} ({porcentaje}% de capacidad)")

    def _refrescar_tabla_clientes(self):
        for item in self._tree_clientes.get_children():
            self._tree_clientes.delete(item)
        for c in self._gestor.listar_clientes():
            self._tree_clientes.insert("", "end", values=(
                c.get_id(), c.get_nombre(), c.get_telefono(), c.obtener_rol()
            ))

    def _refrescar_tabla_facturas(self):
        for item in self._tree_facturas.get_children():
            self._tree_facturas.delete(item)
        total = 0.0
        for f in self._gestor.listar_facturas():
            d = f.a_diccionario()
            total += d["total"]
            self._tree_facturas.insert("", "end", values=(
                d["id_factura"], d["id_cita"], d["cliente"], d["servicio"],
                d["metodo_pago"], f"${d['total']:,.0f}", d["fecha_emision"]
            ))
        self._lbl_total_ingresos.config(text=f"Total Ingresos Facturados: ${total:,.0f}")

    def _on_seleccionar_cita_tabla(self, _event=None, notificar=False):
        seleccion = self._tree_citas.selection()
        if not seleccion:
            return
        valores = self._tree_citas.item(seleccion[0], "values")
        id_cita = int(valores[0])
        cita = self._gestor.buscar_cita(id_cita)
        if not cita:
            return

        self._cita_seleccionada_id = id_cita
        self._entry_fecha.delete(0, tk.END)
        self._entry_fecha.insert(0, cita.get_inicio().strftime("%Y-%m-%d"))
        self._entry_hora.delete(0, tk.END)
        self._entry_hora.insert(0, cita.get_inicio().strftime("%H:%M"))
        self._entry_duracion.delete(0, tk.END)
        self._entry_duracion.insert(0, str(cita.get_duracion()))
        self._entry_precio.delete(0, tk.END)
        self._entry_precio.insert(0, str(int(cita.get_precio())))
        self._var_consultorio.set(cita.get_consultorio())

        if notificar:
            messagebox.showinfo("Detalle de Cita", cita.resumen())

    def _limpiar_formulario_cita(self):
        self._cita_seleccionada_id = None
        self._entry_fecha.delete(0, tk.END)
        self._entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self._entry_hora.delete(0, tk.END)
        self._entry_hora.insert(0, "09:00")

    def _resetear_filtros(self):
        self._entry_filtro_fecha.delete(0, tk.END)
        self._combo_filtro_estado.set("Todos")
        self._refrescar_tabla_citas()

    # ---- ACCIONES CRUD DE CITAS (con try / except) ----
    def _obtener_datos_formulario_cita(self):
        if not self._combo_cliente.get():
            raise ValueError("Debe registrar y seleccionar un cliente primero.")
        id_cliente = int(self._combo_cliente.get().split("-")[0].strip())
        id_prof = int(self._combo_profesional.get().split("-")[0].strip()) if self._combo_profesional.get() else 1
        servicio_txt = self._combo_servicio.get().split("|")[0].strip() if self._combo_servicio.get() else "Consulta General"
        fecha = self._entry_fecha.get().strip()
        hora = self._entry_hora.get().strip()
        duracion = int(self._entry_duracion.get().strip())
        precio = float(self._entry_precio.get().strip())
        consultorio = self._var_consultorio.get()
        return id_cliente, fecha, hora, servicio_txt, duracion, id_prof, consultorio, precio

    def _accion_agendar_cita(self):
        try:
            datos = self._obtener_datos_formulario_cita()
            cita = self._gestor.agendar(*datos)
            self._refrescar_tabla_citas()
            aviso = " (Recordatorio SMS activado)" if self._var_recordatorio.get() else ""
            messagebox.showinfo("Cita Agendada", f"Cita #{cita.get_id()} guardada en Excel correctamente.{aviso}")
        except ConflictoHorarioError as e:
            messagebox.showwarning("Conflicto de Horario", str(e))
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"No se pudo agendar la cita: {e}")

    def _accion_actualizar_cita(self):
        try:
            if self._cita_seleccionada_id is None:
                raise ValueError("Seleccione primero una cita en la tabla para actualizarla.")
            _, fecha, hora, servicio, duracion, id_prof, consultorio, precio = self._obtener_datos_formulario_cita()
            cita = self._gestor.actualizar_cita(
                self._cita_seleccionada_id, fecha, hora, servicio, duracion, id_prof, consultorio, precio
            )
            self._refrescar_tabla_citas()
            messagebox.showinfo("Actualizada", f"Cita #{cita.get_id()} actualizada en Excel.")
        except ConflictoHorarioError as e:
            messagebox.showwarning("Conflicto de Horario", str(e))
        except Exception as e:
            messagebox.showerror("Error al Actualizar", str(e))

    def _accion_confirmar_cita(self):
        try:
            if self._cita_seleccionada_id is None:
                raise ValueError("Seleccione una cita de la tabla.")
            cita = self._gestor.confirmar(self._cita_seleccionada_id)
            self._refrescar_tabla_citas()
            messagebox.showinfo("Confirmada", f"Cita #{cita.get_id()} confirmada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _accion_cancelar_cita(self):
        try:
            if self._cita_seleccionada_id is None:
                raise ValueError("Seleccione una cita de la tabla.")
            if messagebox.askyesno("Confirmar Cancelación", "¿Seguro que desea cancelar esta cita?"):
                cita = self._gestor.cancelar(self._cita_seleccionada_id)
                self._refrescar_tabla_citas()
                messagebox.showinfo("Cancelada", f"Cita #{cita.get_id()} cancelada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _accion_eliminar_cita(self):
        try:
            if self._cita_seleccionada_id is None:
                raise ValueError("Seleccione una cita de la tabla para eliminar.")
            if messagebox.askyesno("Eliminar Registro", "¿Eliminar definitivamente esta cita del archivo Excel?"):
                self._gestor.eliminar_cita(self._cita_seleccionada_id)
                self._cita_seleccionada_id = None
                self._refrescar_tabla_citas()
                messagebox.showinfo("Eliminada", "El registro fue eliminado de Excel.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- VENTANAS SECUNDARIAS (Toplevel) ----
    def _abrir_ventana_cliente(self):
        win = tk.Toplevel(self._root)
        win.title("Registrar Nuevo Cliente")
        win.geometry("350x220")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Nombre completo:").pack(pady=(12, 2))
        ent_nombre = ttk.Entry(win, width=32)
        ent_nombre.pack()

        ttk.Label(win, text="Teléfono (7 a 10 dígitos):").pack(pady=(8, 2))
        ent_tel = ttk.Entry(win, width=32)
        ent_tel.pack()

        var_vip = tk.BooleanVar(value=False)
        tk.Checkbutton(win, text="Cliente VIP (10% descuento en facturación)", variable=var_vip).pack(pady=8)

        def guardar():
            try:
                cli = self._gestor.registrar_cliente(ent_nombre.get(), ent_tel.get(), var_vip.get())
                self._refrescar_combos()
                self._refrescar_tabla_clientes()
                messagebox.showinfo("Éxito", f"Registrado: {cli.describir()}", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Dato Inválido", str(e), parent=win)

        ttk.Button(win, text="Guardar Cliente", command=guardar).pack(pady=8)

    def _abrir_ventana_profesional(self):
        win = tk.Toplevel(self._root)
        win.title("Registrar Nuevo Profesional")
        win.geometry("350x240")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Nombre del profesional:").pack(pady=(10, 2))
        ent_nombre = ttk.Entry(win, width=32)
        ent_nombre.pack()

        ttk.Label(win, text="Teléfono:").pack(pady=(8, 2))
        ent_tel = ttk.Entry(win, width=32)
        ent_tel.pack()

        ttk.Label(win, text="Especialidad:").pack(pady=(8, 2))
        ent_esp = ttk.Entry(win, width=32)
        ent_esp.pack()

        def guardar():
            try:
                prof = self._gestor.registrar_profesional(ent_nombre.get(), ent_tel.get(), ent_esp.get())
                self._refrescar_combos()
                messagebox.showinfo("Éxito", f"Registrado: {prof.describir()}", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ttk.Button(win, text="Guardar Profesional", command=guardar).pack(pady=12)

    def _abrir_ventana_servicio(self):
        win = tk.Toplevel(self._root)
        win.title("Registrar Nuevo Servicio")
        win.geometry("350x240")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Nombre del servicio:").pack(pady=(10, 2))
        ent_nombre = ttk.Entry(win, width=32)
        ent_nombre.pack()

        ttk.Label(win, text="Duración estándar (minutos):").pack(pady=(8, 2))
        ent_dur = ttk.Entry(win, width=32)
        ent_dur.insert(0, "30")
        ent_dur.pack()

        ttk.Label(win, text="Tarifa ($):").pack(pady=(8, 2))
        ent_precio = ttk.Entry(win, width=32)
        ent_precio.insert(0, "35000")
        ent_precio.pack()

        def guardar():
            try:
                serv = self._gestor.registrar_servicio(ent_nombre.get(), ent_dur.get(), ent_precio.get())
                self._refrescar_combos()
                messagebox.showinfo("Éxito", f"Servicio creado: {serv.describir()}", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ttk.Button(win, text="Guardar Servicio", command=guardar).pack(pady=12)

    def _abrir_ventana_facturar(self):
        if self._cita_seleccionada_id is None:
            messagebox.showwarning("Atención", "Seleccione primero una cita en la tabla.")
            return

        cita = self._gestor.buscar_cita(self._cita_seleccionada_id)
        if not cita or not cita.esta_activa():
            messagebox.showwarning("Atención", "Solo se pueden facturar citas pendientes o confirmadas.")
            return

        win = tk.Toplevel(self._root)
        win.title(f"Facturar Cita #{cita.get_id()}")
        win.geometry("340x210")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text=f"Cliente: {cita.get_cliente().get_nombre()}", font=("Segoe UI", 10, "bold")).pack(pady=(12, 4))
        ttk.Label(win, text=f"Servicio: {cita.get_servicio()} | Base: ${cita.get_precio():,.0f}").pack(pady=4)

        ttk.Label(win, text="Método de pago:").pack(pady=(8, 2))
        combo_pago = ttk.Combobox(win, state="readonly", values=["Efectivo", "Transferencia", "Tarjeta"])
        combo_pago.set("Efectivo")
        combo_pago.pack()

        def confirmar_pago():
            try:
                factura = self._gestor.completar_y_facturar(cita.get_id(), combo_pago.get())
                self._refrescar_tabla_citas()
                self._refrescar_tabla_facturas()
                messagebox.showinfo(
                    "Factura Generada",
                    f"Factura #{factura.get_id()} emitida.\nTotal cobrado: ${factura.calcular_total():,.0f}",
                    parent=win
                )
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ttk.Button(win, text="Emitir Factura y Completar Cita", command=confirmar_pago).pack(pady=14)

    # ---- ACCIONES DE CLIENTES Y ARCHIVOS (filedialog) ----
    def _accion_ver_historial_cliente(self):
        sel = self._tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente en la lista.")
            return
        id_cli = int(self._tree_clientes.item(sel[0], "values")[0])
        historial = self._gestor.obtener_historial_cliente(id_cli)
        messagebox.showinfo("Historial del Cliente", historial.generar_reporte())

    def _accion_eliminar_cliente(self):
        try:
            sel = self._tree_clientes.selection()
            if not sel:
                raise ValueError("Seleccione un cliente de la lista.")
            id_cli = int(self._tree_clientes.item(sel[0], "values")[0])
            if messagebox.askyesno("Confirmar", "¿Eliminar este cliente de Excel?"):
                self._gestor.eliminar_cliente(id_cli)
                self._refrescar_combos()
                self._refrescar_tabla_clientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _accion_guardar_excel(self):
        try:
            self._gestor.guardar_en_excel()
            messagebox.showinfo("Sincronizado", "Todos los datos han sido guardados en Excel.")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _accion_exportar_excel(self):
        try:
            ruta = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")],
                title="Exportar copia de respaldo en Excel"
            )
            if ruta:
                ruta_original = self._gestor.get_backend().get_ruta_archivo()
                self._gestor.get_backend().set_ruta_archivo(ruta)
                self._gestor.guardar_en_excel()
                self._gestor.get_backend().set_ruta_archivo(ruta_original)
                messagebox.showinfo("Exportado", f"Copia guardada exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al Exportar", str(e))

    def _accion_abrir_excel(self):
        try:
            ruta = filedialog.askopenfilename(
                filetypes=[("Archivos Excel", "*.xlsx")],
                title="Seleccionar base de datos Excel"
            )
            if ruta:
                self._gestor.get_backend().set_ruta_archivo(ruta)
                self._gestor.cargar_desde_excel()
                self._lbl_archivo_activo.config(text=f"BD Excel: {ruta}  ")
                self._refrescar_combos()
                self._refrescar_tabla_citas()
                self._refrescar_tabla_clientes()
                self._refrescar_tabla_facturas()
                messagebox.showinfo("Cargado", "Base de datos Excel cargada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al Abrir", str(e))

    def _mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca del Sistema",
            "Sistema de Gestión de Citas y Turnos v3.0\n"
            "Programación II - Tercer Parcial\n"
            "Arquitectura POO (12 Clases) + Tkinter + OpenPyXL"
        )