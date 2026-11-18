from datetime import datetime, timedelta


class Cita:
    """Turno agendado con su estado de atención, profesional y consultorio."""

    ESTADOS = ("pendiente", "confirmada", "cancelada", "completada")

    def __init__(self, id_cita, cliente, fecha, hora, servicio, duracion_min=30,
                 estado="pendiente", profesional=None, consultorio="Sala 1", precio=25000.0):
        self._id_cita = int(id_cita)
        self._cliente = cliente
        self._servicio = str(servicio).strip()
        self._duracion = int(duracion_min)
        self._estado = estado if estado in Cita.ESTADOS else "pendiente"
        self._profesional = profesional
        self._consultorio = str(consultorio).strip() if consultorio else "Sala 1"
        self._precio = float(precio)
        # Validamos fecha y hora; si el formato es incorrecto, datetime lanza ValueError
        self._inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

    # ---- Consultas ----
    def get_id(self):
        return self._id_cita

    def get_cliente(self):
        return self._cliente

    def get_profesional(self):
        return self._profesional

    def set_profesional(self, profesional):
        self._profesional = profesional

    def get_consultorio(self):
        return self._consultorio

    def set_consultorio(self, consultorio):
        self._consultorio = str(consultorio).strip()

    def get_estado(self):
        return self._estado

    def get_inicio(self):
        return self._inicio

    def get_fin(self):
        return self._inicio + timedelta(minutes=self._duracion)

    def get_servicio(self):
        return self._servicio

    def set_servicio(self, servicio):
        self._servicio = str(servicio).strip()

    def get_duracion(self):
        return self._duracion

    def get_precio(self):
        return self._precio

    def set_precio(self, precio):
        self._precio = float(precio)

    def reprogramar(self, nueva_fecha, nueva_hora, nueva_duracion=None):
        if self._estado in ("cancelada", "completada"):
            raise ValueError(f"No se puede reprogramar una cita {self._estado}.")
        self._inicio = datetime.strptime(f"{nueva_fecha} {nueva_hora}", "%Y-%m-%d %H:%M")
        if nueva_duracion is not None:
            self._duracion = int(nueva_duracion)

    # ---- Cambios de estado ----
    def _cambiar_estado(self, nuevo):
        if nuevo not in Cita.ESTADOS:
            raise ValueError(f"Estado inválido: {nuevo}")
        if self._estado in ("cancelada", "completada"):
            raise ValueError(f"La cita ya está {self._estado} y no se puede modificar.")
        self._estado = nuevo

    def confirmar(self):
        self._cambiar_estado("confirmada")

    def cancelar(self):
        self._cambiar_estado("cancelada")

    def completar(self):
        self._cambiar_estado("completada")

    # ---- Lógica de horarios ----
    def esta_activa(self):
        return self._estado in ("pendiente", "confirmada")

    def ocupa_horario(self, inicio, fin):
        """True si esta cita está activa y se cruza con el rango [inicio, fin)."""
        return self.esta_activa() and self._inicio < fin and inicio < self.get_fin()

    def resumen(self):
        prof = self._profesional.get_nombre() if self._profesional else "Sin asignar"
        return (f"#{self._id_cita} | {self._inicio.strftime('%Y-%m-%d %H:%M')} | "
                f"{self._cliente.get_nombre()} | {self._servicio} | Prof: {prof} | {self._estado}")

    def a_diccionario(self):
        return {
            "id_cita": self._id_cita,
            "id_cliente": self._cliente.get_id(),
            "cliente_nombre": self._cliente.get_nombre(),
            "id_profesional": self._profesional.get_id() if self._profesional else 0,
            "profesional_nombre": self._profesional.get_nombre() if self._profesional else "General",
            "fecha": self._inicio.strftime("%Y-%m-%d"),
            "hora": self._inicio.strftime("%H:%M"),
            "servicio": self._servicio,
            "duracion_min": self._duracion,
            "consultorio": self._consultorio,
            "precio": self._precio,
            "estado": self._estado,
        }