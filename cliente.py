from persona import Persona

class Cliente(Persona):
    """Clase hija: persona que solicita las citas."""

    def __init__(self, id_clinete, nombre, telefono, vip=False):
        super().__init__(nombre, telefono)
        self._id_clinete = int(id_clinete)
        self._vip = bool(vip)

    def get_id(self):
        return self._id_clinete

    def es_vip(self):
        return self._vip

    def set_vip(self, vip):
        self._vip = bool(vip)

    def obtener_rol(self):
        return "cliente VIP" if self._vip else "cliente"

    def descripcion(self):
        return f"[{self._id_clinete}] {super().describir()}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["id_clinete"] = self._id_clinete
        datos["vip"] = self._vip
        return datos