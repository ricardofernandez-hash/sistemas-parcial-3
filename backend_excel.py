import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment


class BackendExcel:
    """Capa de Backend encargada exclusivamente de la persistencia CRUD en Excel."""

    HOJAS = {
        "Clientes": ["id_cliente", "nombre", "telefono", "vip"],
        "Profesionales": ["id_profesional", "nombre", "telefono", "especialidad"],
        "Servicios": ["id_servicio", "nombre", "duracion_min", "precio"],
        "Citas": [
            "id_cita", "id_cliente", "cliente_nombre", "id_profesional",
            "profesional_nombre", "fecha", "hora", "servicio",
            "duracion_min", "consultorio", "precio", "estado"
        ],
        "Facturas": [
            "id_factura", "id_cita", "cliente", "servicio",
            "metodo_pago", "total", "fecha_emision"
        ],
    }

    def __init__(self, ruta_archivo="datos_sistema_citas.xlsx"):
        self._ruta_archivo = ruta_archivo
        if not os.path.exists(self._ruta_archivo):
            self.crear_archivo()

    def get_ruta_archivo(self):
        return self._ruta_archivo

    def set_ruta_archivo(self, nueva_ruta):
        self._ruta_archivo = nueva_ruta
        if not os.path.exists(self._ruta_archivo):
            self.crear_archivo()

    # ---- CREACIÓN DEL ARCHIVO ----
    def crear_archivo(self):
        """Crea el libro Excel con todas las hojas y encabezados formateados."""
        wb = Workbook()
        # Eliminar hoja por defecto
        wb.remove(wb.active)

        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)

        for nombre_hoja, columnas in self.HOJAS.items():
            ws = wb.create_sheet(title=nombre_hoja)
            ws.append(columnas)
            for col_idx in range(1, len(columnas) + 1):
                celda = ws.cell(row=1, column=col_idx)
                celda.fill = header_fill
                celda.font = header_font
                celda.alignment = Alignment(horizontal="center")
                ws.column_dimensions[celda.column_letter].width = 18

        wb.save(self._ruta_archivo)

    # ---- LECTURA DE DATOS ----
    def leer_hoja(self, nombre_hoja):
        """Lee todos los registros de una hoja y los retorna como lista de diccionarios."""
        if not os.path.exists(self._ruta_archivo):
            self.crear_archivo()

        wb = load_workbook(self._ruta_archivo)
        if nombre_hoja not in wb.sheetnames:
            return []

        ws = wb[nombre_hoja]
        filas = list(ws.iter_rows(values_only=True))
        if len(filas) <= 1:
            return []

        encabezados = filas[0]
        registros = []
        for fila in filas[1:]:
            if all(v is None for v in fila):
                continue
            registro = dict(zip(encabezados, fila))
            registros.append(registro)
        return registros

    # ---- ESCRITURA DE DATOS ----
    def insertar_registro(self, nombre_hoja, diccionario_datos):
        """Agrega una nueva fila al final de la hoja indicada."""
        if not os.path.exists(self._ruta_archivo):
            self.crear_archivo()

        wb = load_workbook(self._ruta_archivo)
        if nombre_hoja not in wb.sheetnames:
            raise ValueError(f"La hoja '{nombre_hoja}' no existe en el Excel.")

        ws = wb[nombre_hoja]
        columnas = self.HOJAS[nombre_hoja]
        fila = [diccionario_datos.get(col, "") for col in columnas]
        ws.append(fila)
        wb.save(self._ruta_archivo)

    def guardar_todo(self, clientes, profesionales, servicios, citas, facturas):
        """Sincroniza el estado completo de las entidades hacia el archivo Excel."""
        self.crear_archivo()
        wb = load_workbook(self._ruta_archivo)

        mapeo = {
            "Clientes": [c.a_diccionario() for c in clientes],
            "Profesionales": [p.a_diccionario() for p in profesionales],
            "Servicios": [s.a_diccionario() for s in servicios],
            "Citas": [ct.a_diccionario() for ct in citas],
            "Facturas": [f.a_diccionario() for f in facturas],
        }

        for nombre_hoja, lista_dicts in mapeo.items():
            ws = wb[nombre_hoja]
            columnas = self.HOJAS[nombre_hoja]
            for item in lista_dicts:
                ws.append([item.get(col, "") for col in columnas])

        wb.save(self._ruta_archivo)

    # ---- ACTUALIZACIÓN DE DATOS ----
    def actualizar_registro(self, nombre_hoja, campo_id, valor_id, nuevos_datos):
        """Busca un registro por su ID y actualiza sus columnas en Excel."""
        wb = load_workbook(self._ruta_archivo)
        ws = wb[nombre_hoja]
        columnas = self.HOJAS[nombre_hoja]
        idx_id = columnas.index(campo_id)

        actualizado = False
        for row_idx in range(2, ws.max_row + 1):
            if ws.cell(row=row_idx, column=idx_id + 1).value == valor_id:
                for clave, valor in nuevos_datos.items():
                    if clave in columnas:
                        col_idx = columnas.index(clave) + 1
                        ws.cell(row=row_idx, column=col_idx, value=valor)
                actualizado = True
                break

        if actualizado:
            wb.save(self._ruta_archivo)
        return actualizado

    # ---- ELIMINACIÓN DE REGISTROS ----
    def eliminar_registro(self, nombre_hoja, campo_id, valor_id):
        """Elimina una fila de la hoja según el ID suministrado."""
        wb = load_workbook(self._ruta_archivo)
        ws = wb[nombre_hoja]
        columnas = self.HOJAS[nombre_hoja]
        idx_id = columnas.index(campo_id)

        eliminado = False
        for row_idx in range(2, ws.max_row + 1):
            if ws.cell(row=row_idx, column=idx_id + 1).value == valor_id:
                ws.delete_rows(row_idx, 1)
                eliminado = True
                break

        if eliminado:
            wb.save(self._ruta_archivo)
        return eliminado