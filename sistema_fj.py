import logging
import time
from abc import ABC, abstractmethod
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

# Configuración de interfaz dinámica
console = Console()

# 1. Configuración de Logs
logging.basicConfig(filename='sistema_fj.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Excepciones Personalizadas
class SistemaFJError(Exception): pass
class DatosInvalidosError(SistemaFJError): pass
class ServicioNoDisponibleError(SistemaFJError): pass

# 3. Clases Base y Cliente
class Entidad(ABC):
    @abstractmethod
    def mostrar_detalle(self): pass

class Cliente(Entidad):
    def __init__(self, cedula, nombre):
        if not isinstance(cedula, int) or cedula <= 0:
            raise DatosInvalidosError("La cédula debe ser un número entero positivo.")
        if not nombre or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente no puede estar vacío.")
        self.__cedula = cedula
        self.__nombre = nombre

    def get_nombre(self): return self.__nombre
    def get_cedula(self): return self.__cedula
    def mostrar_detalle(self): return f"{self.__nombre} (ID: {self.__cedula})"

# 4. Servicios (Polimorfismo)
class Servicio(Entidad):
    def __init__(self, id_servicio, nombre, costo_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = True

    @abstractmethod
    def calcular_costo_total(self, cantidad=1, extra=False): pass

class ServicioSala(Servicio):
    def calcular_costo_total(self, horas=1, aplicar_descuento=False):
        costo = self.costo_base * horas
        return costo * 0.9 if aplicar_descuento else costo
    def mostrar_detalle(self): return f"[cyan]Sala:[/cyan] {self.nombre}"

class ServicioEquipo(Servicio):
    def calcular_costo_total(self, dias=1, seguro_extra=False):
        costo = self.costo_base * dias
        return costo + 50000 if seguro_extra else costo
    def mostrar_detalle(self): return f"[green]Equipo:[/green] {self.nombre}"

class ServicioAsesoria(Servicio):
    def calcular_costo_total(self, horas=1, nivel_experto=False):
        costo = self.costo_base * horas
        return costo * 1.5 if nivel_experto else costo
    def mostrar_detalle(self): return f"[magenta]Asesoría:[/magenta] {self.nombre}"

# 5. Reserva con Manejo Robusto de Excepciones
class Reserva:
    def __init__(self, cliente, servicio, duracion):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        
    def procesar_reserva(self):
        try:
            logging.info(f"Procesando reserva: {self.cliente.get_nombre()} -> {self.servicio.nombre}")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' ya está ocupado.")
            
            # Simular tiempo de proceso
            time.sleep(0.5) 
            self.servicio.disponible = False
            self.estado = "Confirmada"
            
        except ServicioNoDisponibleError as e:
            logging.error(f"Error de disponibilidad: {e}")
            self.estado = "Fallida"
            raise SistemaFJError("Reserva rechazada por conflicto de disponibilidad.") from e
            
        except Exception as e:
            logging.error(f"Error crítico en reserva: {e}")
            self.estado = "Fallida"
            raise
            
        else:
            logging.info("Reserva procesada exitosamente.")
            
        finally:
            logging.info(f"Finalizado proceso para {self.cliente.get_nombre()}. Estado: {self.estado}")

# 6. Simulador Dinámico
def ejecutar_simulaciones():
    console.print(Panel.fit("[bold blue]SOFTWARE FJ - SISTEMA DE GESTIÓN (MODO SIMULACIÓN)[/bold blue]"))
    
    # Datos de prueba
    clientes = []
    servicios = [
        ServicioSala("S1", "Sala de Juntas (Auditoría ISO 45001)", 120000),
        ServicioEquipo("E1", "Servidor Local (Migración ERP)", 250000),
        ServicioAsesoria("A1", "Asesoría Proyecto SMART-IIS", 180000)
    ]
    resultados = []

    # Animación de carga para hacerlo dinámico
    for _ in track(range(100), description="[yellow]Inicializando módulos y cargando logs..."):
        time.sleep(0.01)

    console.print("\n[bold]1. Fase de Validación de Clientes[/bold]")
    try:
        c1 = Cliente(102030, "El Doc")
        clientes.append(c1)
        console.print(f"[green]✔ Cliente creado:[/green] {c1.mostrar_detalle()}")
        
        c2 = Cliente(102031, "Carlos Larrota")
        clientes.append(c2)
        console.print(f"[green]✔ Cliente creado:[/green] {c2.mostrar_detalle()}")
        
        # Simulación de error
        console.print("[yellow]Intentando crear cliente con datos corruptos...[/yellow]")
        c_err = Cliente("NoCedula", "")
    except DatosInvalidosError as e:
        console.print(f"[red]✖ Error capturado:[/red] {e}")
        logging.warning(f"Intento de cliente inválido: {e}")

    console.print("\n[bold]2. Fase de Procesamiento de Reservas[/bold]")
    
    # Reserva 1: Exitosa
    try:
        r1 = Reserva(clientes[0], servicios[0], 4)
        r1.procesar_reserva()
        resultados.append(("El Doc", servicios[0].nombre, "Aprobada", str(servicios[0].calcular_costo_total(4))))
        console.print(f"[green]✔ Reserva confirmada para {clientes[0].get_nombre()}[/green]")
    except Exception as e:
        console.print(f"[red]✖ Fallo:[/red] {e}")

    # Reserva 2: Fallo por disponibilidad (El Doc ya tomó la sala)
    try:
        r2 = Reserva(clientes[1], servicios[0], 2)
        r2.procesar_reserva()
    except SistemaFJError as e:
        resultados.append(("Carlos Larrota", servicios[0].nombre, "Rechazada", "N/A"))
        console.print(f"[red]✖ Reserva denegada para {clientes[1].get_nombre()}:[/red] {e}")

    # Reserva 3: Exitosa
    try:
        r3 = Reserva(clientes[1], servicios[1], 5)
        r3.procesar_reserva()
        resultados.append(("Carlos Larrota", servicios[1].nombre, "Aprobada", str(servicios[1].calcular_costo_total(5, True))))
        console.print(f"[green]✔ Reserva confirmada para {clientes[1].get_nombre()}[/green]")
    except Exception as e:
        pass

    # Imprimir Reporte Final Dinámico
    console.print("\n[bold]Reporte Final de Operaciones[/bold]")
    tabla = Table(show_header=True, header_style="bold magenta")
    tabla.add_column("Cliente")
    tabla.add_column("Servicio Solicitado")
    tabla.add_column("Estado")
    tabla.add_column("Costo Total Estimado ($)")

    for res in resultados:
        color_estado = "green" if res[2] == "Aprobada" else "red"
        tabla.add_row(res[0], res[1], f"[{color_estado}]{res[2]}[/{color_estado}]", res[3])

    console.print(tabla)
    console.print(f"\n[dim]Todos los eventos y excepciones han sido guardados en 'sistema_fj.log' según los requerimientos.[/dim]")

if __name__ == "__main__":
    ejecutar_simulaciones()