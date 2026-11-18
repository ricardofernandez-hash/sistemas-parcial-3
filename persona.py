class Persona:
    """Clase base para clientes y profesionales."""

    def __init__(self, nombre, telefono):
        self._nombre = ""
        self._telefono = ""
        self.set_nombre(nombre)
        self.set_telefono(telefono)

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        if not isinstance(nombre, str) or len(nombre.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = nombre.strip().title()

    def get_telefono(self):
        return self._telefono

    def set_telefono(self, telefono):
        telefono = str(telefono).strip()
        if not telefono.isdigit() or not (7 <= len(telefono) <= 10):
            raise ValueError("El teléfono debe tener entre 7 y 10 dígitos numéricos.")
        self._telefono = telefono

    def obtener_rol(self):
        return "Persona"

    def describir(self):
        return f"{self.obtener_rol()}: {self._nombre} (Tel: {self._telefono})"

    def a_diccionario(self):
        return {"nombre": self._nombre, "telefono": self._telefono}
