from datetime import datetime


class Factura:
    """Comprobante de pago asociado a una cita completada."""

    METODOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta")

    def __init__(self, id_factura, cita, metodo_pago="Efectivo", descuento=0.0, fecha_emision=None):
        if metodo_pago not in Factura.METODOS_PAGO:
            raise ValueError(f"Método de pago no válido: {metodo_pago}")
        self._id_factura = int(id_factura)
        self._cita = cita
        self._metodo_pago = metodo_pago
        self._descuento = float(descuento)
        self._fecha_emision = fecha_emision or datetime.now().strftime("%Y-%m-%d %H:%M")

    def get_id(self):
        return self._id_factura

    def get_cita(self):
        return self._cita

    def get_metodo_pago(self):
        return self._metodo_pago

    def calcular_total(self):
        subtotal = self._cita.get_precio()
        # Clientes VIP reciben 10% adicional si no hay descuento manual
        desc = self._descuento
        if desc == 0 and self._cita.get_cliente().es_vip():
            desc = subtotal * 0.10
        return max(0.0, subtotal - desc)

    def a_diccionario(self):
        return {
            "id_factura": self._id_factura,
            "id_cita": self._cita.get_id(),
            "cliente": self._cita.get_cliente().get_nombre(),
            "servicio": self._cita.get_servicio(),
            "metodo_pago": self._metodo_pago,
            "total": round(self.calcular_total(), 2),
            "fecha_emision": self._fecha_emision,
        }