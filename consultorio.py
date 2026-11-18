class Consultorio:
    """Representa el espacio físico, cabina o puesto donde se atiende una cita."""

    def __init__(self, id_consultorio, nombre, ubicacion="Piso 1", disponible=True):
        self._id_consultorio = int(id_consultorio)
        self._nombre = str(nombre).strip()
        self._ubicacion = str(ubicacion).strip()
        self._disponible = bool(disponible)

    def get_id(self):
        return self._id_consultorio

    def get_nombre(self):
        return self._nombre

    def get_ubicacion(self):
        return self._ubicacion

    def esta_disponible(self):
        return self._disponible

    def set_disponible(self, estado):
        self._disponible = bool(estado)

    def describir(self):
        estado = "Disponible" if self._disponible else "En mantenimiento"
        return f"{self._nombre} ({self._ubicacion}) - {estado}"

    def a_diccionario(self):
        return {
            "id_consultorio": self._id_consultorio,
            "nombre": self._nombre,
            "ubicacion": self._ubicacion,
            "disponible": self._disponible,
        }