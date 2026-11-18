class HistorialCliente:
    """Analiza el comportamiento y métricas de atención de un cliente específico."""

    def __init__(self, cliente, citas):
        self._cliente = cliente
        self._citas_cliente = [c for c in citas if c.get_cliente().get_id() == cliente.get_id()]

    def total_citas(self):
        return len(self._citas_cliente)

    def citas_completadas(self):
        return sum(1 for c in self._citas_cliente if c.get_estado() == "completada")

    def citas_canceladas(self):
        return sum(1 for c in self._citas_cliente if c.get_estado() == "cancelada")

    def inversion_total(self):
        return sum(c.get_precio() for c in self._citas_cliente if c.get_estado() == "completada")

    def generar_reporte(self):
        return (
            f"Cliente: {self._cliente.get_nombre()} ({self._cliente.obtener_rol()})\n"
            f"Total citas registradas: {self.total_citas()}\n"
            f"Completadas: {self.citas_completadas()} | Canceladas: {self.citas_canceladas()}\n"
            f"Total facturado: ${self.inversion_total():,.0f}"
        )