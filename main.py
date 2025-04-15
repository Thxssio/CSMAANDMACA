import random
import matplotlib.pyplot as plt

# Parâmetros gerais da simulação
SIM_TIME = 1000  # tempo total de simulação (em unidades de tempo discretas)
NUM_NODES = 10   # número de nós
DISTANCE_THRESHOLD = 2  # distância máxima para um nó ser considerado "visível" (senão é oculto)
FRAME_DURATION = 5  # tempo de transmissão de um quadro
WAIT_MAX = 10       # tempo máximo de espera (backoff)

# Geração de eventos aleatórios de chegada de quadros
def generate_traffic(rate, sim_time):
    traffic = [[] for _ in range(NUM_NODES)]
    for t in range(sim_time):
        for i in range(NUM_NODES):
            if random.random() < rate:
                traffic[i].append(t)
    return traffic

# Checa se há colisão entre os transmissores ativos
def detect_collisions(active_nodes):
    if len(active_nodes) <= 1:
        return set(), active_nodes
    return set(active_nodes), []

# Define vizinhos visíveis de cada nó (para CSMA com nós ocultos)
def get_visible_nodes(index):
    return [i for i in range(NUM_NODES)
            if abs(i - index) <= DISTANCE_THRESHOLD and i != index]

# Simulação do CSMA com nós ocultos
def csma_simulation(rate):
    traffic = generate_traffic(rate, SIM_TIME)
    queue = [list(t) for t in traffic]
    backoff = [0] * NUM_NODES
    transmitting = [0] * NUM_NODES
    collisions = 0
    successes = 0

    for t in range(SIM_TIME):
        active_nodes = []

        for i in range(NUM_NODES):
            if backoff[i] > 0:
                backoff[i] -= 1
                continue

            if queue[i] and queue[i][0] <= t:
                visible = get_visible_nodes(i)
                medium_busy = any(transmitting[v] > 0 for v in visible)

                if not medium_busy:
                    active_nodes.append(i)

        collided, success = detect_collisions(active_nodes)

        for i in collided:
            backoff[i] = random.randint(1, WAIT_MAX)
            collisions += 1
            queue[i].pop(0)

        for i in success:
            transmitting[i] = FRAME_DURATION
            successes += 1
            queue[i].pop(0)

        for i in range(NUM_NODES):
            if transmitting[i] > 0:
                transmitting[i] -= 1

    return successes, collisions

# Simulação do MACA com RTS/CTS
def maca_simulation(rate):
    traffic = generate_traffic(rate, SIM_TIME)
    queue = [list(t) for t in traffic]
    transmitting = [0] * NUM_NODES
    rts_cts_wait = [0] * NUM_NODES
    collisions = 0
    successes = 0

    for t in range(SIM_TIME):
        for i in range(NUM_NODES):
            if transmitting[i] > 0:
                transmitting[i] -= 1
                continue

            if rts_cts_wait[i] > 0:
                rts_cts_wait[i] -= 1
                continue

            if queue[i] and queue[i][0] <= t:
                receiver = (i + 1) % NUM_NODES
                # Verifica se alguém nos arredores do receptor está transmitindo
                visible_to_receiver = get_visible_nodes(receiver)
                interference = any(transmitting[v] > 0 for v in visible_to_receiver)

                if not interference:
                    transmitting[i] = FRAME_DURATION
                    successes += 1
                    queue[i].pop(0)
                else:
                    collisions += 1
                    rts_cts_wait[i] = random.randint(1, WAIT_MAX)
                    queue[i].pop(0)

    return successes, collisions

# Coletar dados para diferentes taxas
rates = [i / 20 for i in range(1, 11)]
csma_results = [csma_simulation(r) for r in rates]
maca_results = [maca_simulation(r) for r in rates]

# Plotando os resultados
success_csma = [s for s, c in csma_results]
success_maca = [s for s, c in maca_results]

plt.plot(rates, success_csma, label='CSMA (nós ocultos)')
plt.plot(rates, success_maca, label='MACA (RTS/CTS)')
plt.xlabel('Taxa de chegada de quadros')
plt.ylabel('Quadros entregues com sucesso')
plt.title('Desempenho do CSMA vs MACA com nós ocultos')
plt.grid(True)
plt.legend()
plt.show()
