from persona import Persona


class Profesional(Persona):
    """Clase hija: persona que atiende las citas (barbero, médico, especialista...)."""

    def __init__(self, nombre, telefono, especialidad, id_profesional=1):
        super().__init__(nombre, telefono)
        self._id_profesional = int(id_profesional)
        self._especialidad = ""
        self.set_especialidad(especialidad)

    def get_id(self):
        return self._id_profesional

    def get_especialidad(self):
        return self._especialidad

    def set_especialidad(self, especialidad):
        if not especialidad or not str(especialidad).strip():
            raise ValueError("La especialidad no puede estar vacía.")
        self._especialidad = str(especialidad).strip().title()

    def obtener_rol(self):
        return "Profesional"

    def describir(self):
        return f"[{self._id_profesional}] {super().describir()} - Especialidad: {self._especialidad}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["id_profesional"] = self._id_profesional
        datos["especialidad"] = self._especialidad
        return datos