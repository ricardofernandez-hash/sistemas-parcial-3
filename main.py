from backend_excel import BackendExcel
from gestor_citas import GestorCitas
from interfaz_grafica import InterfazSistemaCitas

backend = BackendExcel("datos_sistema_citas.xlsx")
gestor = GestorCitas(backend)
app = InterfazSistemaCitas(gestor)
app.iniciar()