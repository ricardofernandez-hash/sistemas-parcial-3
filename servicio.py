class Servicio:
    """Representa un servicio ofrecido en el establecimiento con su duración y tarifa."""

    def __init__(self, id_servicio, nombre, duracion_min=30, precio=25000.0):
        self._id_servicio = int(id_servicio)
        self._nombre = ""
        self._duracion_min = 30
        self._precio = 0.0
        self.set_nombre(nombre)
        self.set_duracion(duracion_min)
        self.set_precio(precio)

    def get_id(self):
        return self._id_servicio

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        if not nombre or len(str(nombre).strip()) < 2:
            raise ValueError("El nombre del servicio debe tener al menos 2 caracteres.")
        self._nombre = str(nombre).strip().capitalize()

    def get_duracion(self):
        return self._duracion_min

    def set_duracion(self, duracion_min):
        dur = int(duracion_min)
        if dur <= 0 or dur > 480:
            raise ValueError("La duración debe estar entre 1 y 480 minutos.")
        self._duracion_min = dur

    def get_precio(self):
        return self._precio

    def set_precio(self, precio):
        val = float(precio)
        if val < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = val

    def describir(self):
        return f"{self._nombre} ({self._duracion_min} min - ${self._precio:,.0f})"

    def a_diccionario(self):
        return {
            "id_servicio": self._id_servicio,
            "nombre": self._nombre,
            "duracion_min": self._duracion_min,
            "precio": self._precio,
        }