from persona import Persona


class Cliente(Persona):
    """Clase hija: persona que solicita citas."""

    def __init__(self, id_cliente, nombre, telefono, vip=False):
        super().__init__(nombre, telefono)
        self._id_cliente = int(id_cliente)
        self._vip = bool(vip)

    def get_id(self):
        return self._id_cliente

    def es_vip(self):
        return self._vip

    def set_vip(self, vip):
        self._vip = bool(vip)

    def obtener_rol(self):
        return "Cliente VIP" if self._vip else "Cliente"

    def describir(self):
        return f"[{self._id_cliente}] {super().describir()}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["id_cliente"] = self._id_cliente
        datos["vip"] = self._vip
        return datos
