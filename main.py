import simpy
import random

# Parámetros de la simulación
RANDOM_SEED = 21  # Semilla para reproducibilidad (asi tenemos siempre el mismo random)
NUM_CLIENTES = 10  # Número total de clientes a simular
TIEMPO_ENTRE_LLEGADAS = 2.0  # Tiempo promedio entre llegadas
TIEMPO_SERVICIO = 5.0  # Tiempo promedio de servicio
NUM_SERVIDORES = 3  # Número de servidores disponibles

#Proceso que representa a un cliente que llega y es atendido.
def cliente(env, nombre, servidor):
    llegada = env.now
    print(f"{nombre} llega a las {llegada:.2f}")

    # Solicita un servidor
    with servidor.request() as solicitud:
        yield solicitud
        espera = env.now - llegada
        print(f"{nombre} comienza a ser atendido a las {env.now:.2f} después de esperar {espera:.2f}")

        # Simula el tiempo de servicio
        tiempo_atencion = random.expovariate(1.0 / TIEMPO_SERVICIO)
        yield env.timeout(tiempo_atencion)
        print(f"{nombre} finaliza el servicio a las {env.now:.2f}")

# Genera la llegada de clientes al sistema.
def llegada_clientes(env, servidor):
    for i in range(NUM_CLIENTES):
        env.process(cliente(env, f"Cliente {i + 1}", servidor))
        # Tiempo entre llegadas (distribución exponencial)
        tiempo_llegada = random.expovariate(1.0 / TIEMPO_ENTRE_LLEGADAS)
        yield env.timeout(tiempo_llegada)


def main():
    print("Simulación de un sistema de colas (Teoría de colas)")
    random.seed(RANDOM_SEED)

    # Crea el entorno de simulación
    env = simpy.Environment()
    # Crea el recurso que representa los servidores (cajeros, agentes, etc.)
    servidor = simpy.Resource(env, capacity=NUM_SERVIDORES)

    # Inicia el proceso de generación de clientes
    env.process(llegada_clientes(env, servidor))

    # Ejecuta la simulación hasta que se atiendan todos los clientes
    env.run()


if __name__ == "__main__":
    main()
