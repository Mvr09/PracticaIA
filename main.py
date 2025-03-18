import simpy
import random
import statistics

# Clase que representa la simulación del canal.
class CanalSimulation:
    def __init__(self, env, num_locks, tiempo_servicio):
        self.env = env
        self.lock = simpy.Resource(env, capacity=num_locks)
        self.tiempo_servicio = tiempo_servicio  # tiempo que tarda en pasar un barco
        self.esperas = []  #tiempos de espera de cada barco
        self.num_barcos = 0

    def procesar_barco(self, nombre):
        tiempo_llegada = self.env.now
        print(f"{tiempo_llegada:.2f}: {nombre} llega al canal.")
        # El barco solicita acceso al canal
        with self.lock.request() as request:
            yield request
            tiempo_entrada = self.env.now
            espera = tiempo_entrada - tiempo_llegada
            self.esperas.append(espera)
            print(f"{tiempo_entrada:.2f}: {nombre} entra en el canal después de esperar {espera:.2f}.")
            servicio = random.expovariate(1.0 / self.tiempo_servicio)
            yield self.env.timeout(servicio)
            tiempo_salida = self.env.now
            print(f"{tiempo_salida:.2f}: {nombre} sale del canal.")
            self.num_barcos += 1

# Metdo de la llegada de barcos
def proceso_llegadas(env, tasa_llegada, canal):
    barco_id = 0
    while True:
        # Usamos una distribucion exponencial para simular el tiempo de las llamadas
        tiempo_entre_llegadas = random.expovariate(tasa_llegada)
        yield env.timeout(tiempo_entre_llegadas)
        barco_id += 1
        env.process(canal.procesar_barco(f"Barco {barco_id}"))

# Metodo para ejecutar la simulación
def run_simulation(tiempo_simulacion, tasa_llegada, tiempo_servicio, num_locks):
    random.seed(42)  # Para reproducibilidad
    env = simpy.Environment()
    canal = CanalSimulation(env, num_locks, tiempo_servicio)
    env.process(proceso_llegadas(env, tasa_llegada, canal))
    env.run(until=tiempo_simulacion)
    promedio_espera = statistics.mean(canal.esperas) if canal.esperas else 0
    print("\nResumen de la simulación:")
    print(f"Tiempo de simulación: {tiempo_simulacion}")
    print(f"Número total de barcos procesados: {canal.num_barcos}")
    print(f"Tiempo de espera promedio: {promedio_espera:.2f}\n")
    return canal

# Función main
def main():
    tiempo_simulacion = 1000  # tiempo total de la simulación
    # Difernetes posibles escenarios
    escenarios = [
        {"nombre": "Tráfico ligero", "tasa_llegada": 0.1, "tiempo_servicio": 5, "num_locks": 2},
        {"nombre": "Tráfico moderado", "tasa_llegada": 0.2, "tiempo_servicio": 5, "num_locks": 2},
        {"nombre": "Tráfico intenso", "tasa_llegada": 0.5, "tiempo_servicio": 5, "num_locks": 2},
    ]

    for escenario in escenarios:
        print("="*50)
        print(f"Escenario: {escenario['nombre']}")
        print("="*50)
        run_simulation(tiempo_simulacion, escenario["tasa_llegada"], escenario["tiempo_servicio"], escenario["num_locks"])

if __name__ == "__main__":
    main()
