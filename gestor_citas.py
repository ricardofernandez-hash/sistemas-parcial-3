from cliente import Cliente
from profesional import Profesional
from servicio import Servicio
from consultorio import Consultorio
from cita import Cita
from factura import Factura
from historial_cliente import HistorialCliente
from excepciones import ConflictoHorarioError


class GestorCitas:
    """Lógica principal del negocio: coordina entidades y delega persistencia al BackendExcel."""

    def __init__(self, backend_excel):
        self._backend = backend_excel
        self._clientes = []
        self._profesionales = []
        self._servicios = []
        self._consultorios = [
            Consultorio(1, "Consultorio 1", "Piso 1"),
            Consultorio(2, "Consultorio 2", "Piso 1"),
            Consultorio(3, "Sala VIP", "Piso 2"),
        ]
        self._citas = []
        self._facturas = []

        self._sig_cliente = 1
        self._sig_profesional = 1
        self._sig_servicio = 1
        self._sig_cita = 1
        self._sig_factura = 1

    def get_backend(self):
        return self._backend

    # ---- Carga y sincronización con BackendExcel ----
    def cargar_desde_excel(self):
        datos_clientes = self._backend.leer_hoja("Clientes")
        datos_prof = self._backend.leer_hoja("Profesionales")
        datos_serv = self._backend.leer_hoja("Servicios")
        datos_citas = self._backend.leer_hoja("Citas")
        datos_fact = self._backend.leer_hoja("Facturas")

        self._clientes = [
            Cliente(d["id_cliente"], d["nombre"], str(d["telefono"]), bool(d.get("vip", False)))
            for d in datos_clientes
        ]
        self._profesionales = [
            Profesional(d["nombre"], str(d["telefono"]), d["especialidad"], d["id_profesional"])
            for d in datos_prof
        ]
        self._servicios = [
            Servicio(d["id_servicio"], d["nombre"], int(d["duracion_min"]), float(d["precio"]))
            for d in datos_serv
        ]

        # Datos semilla si el Excel está recién creado y vacío
        if not self._profesionales:
            self.registrar_profesional("Carlos Gomez", "3101234567", "General")
        if not self._servicios:
            self.registrar_servicio("Consulta General", 30, 30000)
            self.registrar_servicio("Atención Especializada", 45, 50000)
            self.registrar_servicio("Control / Seguimiento", 20, 20000)

        self._citas = []
        for d in datos_citas:
            cli = self.buscar_cliente(int(d["id_cliente"]))
            prof = self.buscar_profesional(int(d.get("id_profesional", 1)))
            if cli:
                fecha_str = str(d["fecha"])[:10]  # Toma solo AAAA-MM-DD
                hora_str = str(d["hora"])[:5]     # Toma solo HH:MM
                cita = Cita(
                    d["id_cita"], cli, fecha_str, hora_str,
                    d["servicio"], int(d["duracion_min"]), d["estado"],
                    prof, d.get("consultorio", "Consultorio 1"), float(d.get("precio", 25000))
                )
                self._citas.append(cita)

        self._facturas = []
        for d in datos_fact:
            cita = self.buscar_cita(int(d["id_cita"]))
            if cita:
                fact = Factura(
                    d["id_factura"], cita, d["metodo_pago"], descuemto aplicado, str(d["fecha_emision"])
                )
                self._facturas.append(fact)

        self._sig_cliente = max([c.get_id() for c in self._clientes], default=0) + 1
        self._sig_profesional = max([p.get_id() for p in self._profesionales], default=0) + 1
        self._sig_servicio = max([s.get_id() for s in self._servicios], default=0) + 1
        self._sig_cita = max([c.get_id() for c in self._citas], default=0) + 1
        self._sig_factura = max([f.get_id() for f in self._facturas], default=0) + 1

    def guardar_en_excel(self):
        self._backend.guardar_todo(
            self._clientes, self._profesionales, self._servicios, self._citas, self._facturas
        )

    # ---- Gestión de Clientes ----
    def registrar_cliente(self, nombre, telefono, vip=False):
        cliente = Cliente(self._sig_cliente, nombre, telefono, vip)
        self._clientes.append(cliente)
        self._sig_cliente += 1
        self._backend.insertar_registro("Clientes", cliente.a_diccionario())
        return cliente

    def buscar_cliente(self, id_cliente):
        for c in self._clientes:
            if c.get_id() == int(id_cliente):
                return c
        return None

    def eliminar_cliente(self, id_cliente):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise ValueError("Cliente no encontrado.")
        self._clientes.remove(cliente)
        self._backend.eliminar_registro("Clientes", "id_cliente", int(id_cliente))

    def listar_clientes(self):
        return list(self._clientes)

    def obtener_historial_cliente(self, id_cliente):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise ValueError("Cliente no encontrado.")
        return HistorialCliente(cliente, self._citas)

    # ---- Gestión de Profesionales ----
    def registrar_profesional(self, nombre, telefono, especialidad):
        prof = Profesional(nombre, telefono, especialidad, self._sig_profesional)
        self._profesionales.append(prof)
        self._sig_profesional += 1
        self._backend.insertar_registro("Profesionales", prof.a_diccionario())
        return prof

    def buscar_profesional(self, id_profesional):
        for p in self._profesionales:
            if p.get_id() == int(id_profesional):
                return p
        return None

    def listar_profesionales(self):
        return list(self._profesionales)

    # ---- Gestión de Servicios y Consultorios ----
    def registrar_servicio(self, nombre, duracion_min, precio):
        serv = Servicio(self._sig_servicio, nombre, duracion_min, precio)
        self._servicios.append(serv)
        self._sig_servicio += 1
        self._backend.insertar_registro("Servicios", serv.a_diccionario())
        return serv

    def listar_servicios(self):
        return list(self._servicios)

    def listar_consultorios(self):
        return list(self._consultorios)

    # ---- Gestión de Citas (CRUD Completo) ----
    def validar_disponibilidad(self, cita_nueva, ignorar_id=None):
        for c in self._citas:
            if ignorar_id is not None and c.get_id() == ignorar_id:
                continue
            if c.ocupa_horario(cita_nueva.get_inicio(), cita_nueva.get_fin()):
                # Si es el mismo consultorio o el mismo profesional, hay conflicto
                mismo_prof = (
                    c.get_profesional() and cita_nueva.get_profesional()
                    and c.get_profesional().get_id() == cita_nueva.get_profesional().get_id()
                )
                mismo_cons = c.get_consultorio() == cita_nueva.get_consultorio()
                if mismo_prof or mismo_cons:
                    return False
        return True

    def agendar(self, id_cliente, fecha, hora, servicio, duracion=30,
                id_profesional=1, consultorio="Consultorio 1", precio=25000.0):
        cliente = self.buscar_cliente(id_cliente)
        if cliente is None:
            raise ValueError("No existe un cliente con ese ID.")
        profesional = self.buscar_profesional(id_profesional)
        cita = Cita(
            self._sig_cita, cliente, fecha, hora, servicio,
            duracion, "pendiente", profesional, consultorio, precio
        )
        if not self.validar_disponibilidad(cita):
            raise ConflictoHorarioError("El profesional o consultorio ya está ocupado en ese horario.")
        self._citas.append(cita)
        self._sig_cita += 1
        self._backend.insertar_registro("Citas", cita.a_diccionario())
        return cita

    def actualizar_cita(self, id_cita, fecha, hora, servicio, duracion, id_profesional, consultorio, precio):
        cita = self.buscar_cita(id_cita)
        if cita is None:
            raise ValueError("No existe una cita con ese ID.")
        profesional = self.buscar_profesional(id_profesional)
        # Crear cita temporal para validar cruce sin afectar la original aún
        temporal = Cita(
            id_cita, cita.get_cliente(), fecha, hora, servicio,
            duracion, cita.get_estado(), profesional, consultorio, precio
        )
        if not self.validar_disponibilidad(temporal, ignorar_id=id_cita):
            raise ConflictoHorarioError("Conflicto de horario con otra cita activa.")

        cita.reprogramar(fecha, hora, duracion)
        cita.set_servicio(servicio)
        cita.set_profesional(profesional)
        cita.set_consultorio(consultorio)
        cita.set_precio(precio)
        self._backend.actualizar_registro("Citas", "id_cita", id_cita, cita.a_diccionario())
        return cita

    def eliminar_cita(self, id_cita):
        cita = self.buscar_cita(id_cita)
        if cita is None:
            raise ValueError("No existe una cita con ese ID.")
        self._citas.remove(cita)
        self._backend.eliminar_registro("Citas", "id_cita", id_cita)

    def buscar_cita(self, id_cita):
        for c in self._citas:
            if c.get_id() == int(id_cita):
                return c
        return None

    def confirmar(self, id_cita):
        cita = self.buscar_cita(id_cita)
        if cita is None:
            raise ValueError("No existe una cita con ese ID.")
        cita.confirmar()
        self._backend.actualizar_registro("Citas", "id_cita", id_cita, {"estado": cita.get_estado()})
        return cita

    def cancelar(self, id_cita):
        cita = self.buscar_cita(id_cita)
        if cita is None:
            raise ValueError("No existe una cita con ese ID.")
        cita.cancelar()
        self._backend.actualizar_registro("Citas", "id_cita", id_cita, {"estado": cita.get_estado()})
        return cita

    def completar_y_facturar(self, id_cita, metodo_pago="Efectivo"):
        cita = self.buscar_cita(id_cita)
        if cita is None:
            raise ValueError("No existe una cita con ese ID.")
        cita.completar()
        self._backend.actualizar_registro("Citas", "id_cita", id_cita, {"estado": cita.get_estado()})
        factura = Factura(self._sig_factura, cita, metodo_pago)
        self._facturas.append(factura)
        self._sig_factura += 1
        self._backend.insertar_registro("Facturas", factura.a_diccionario())
        return factura

    def listar_agenda(self, fecha=None, filtro_estado="Todos"):
        resultado = []
        for c in self._citas:
            coincide_fecha = (fecha is None or c.get_inicio().strftime("%Y-%m-%d") == fecha)
            coincide_estado = (filtro_estado == "Todos" or c.get_estado() == filtro_estado.lower())
            if coincide_fecha and coincide_estado:
                resultado.append(c)
        return sorted(resultado, key=lambda c: c.get_inicio())

    def listar_facturas(self):
        return list(self._facturas)
