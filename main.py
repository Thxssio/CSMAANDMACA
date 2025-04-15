import numpy as np
import random
import matplotlib.pyplot as plt

SIM_TIME = 1000
NUM_NODES = 6
VISIBILITY_RANGE = 1  
FRAME_DURATION = 5
BACKOFF_MAX = 10
random.seed(42)

def generate_traffic(rate, sim_time):
    traffic = [[] for _ in range(NUM_NODES)]
    for t in range(sim_time):
        for i in range(NUM_NODES):
            if random.random() < rate:
                traffic[i].append(t)
    return traffic

def get_visible_nodes(index):
    return [i for i in range(NUM_NODES)
            if abs(i - index) <= VISIBILITY_RANGE and i != index]

def csma_sim(rate):
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
                busy = any(transmitting[v] > 0 for v in visible)
                if not busy:
                    active_nodes.append(i)

        if len(active_nodes) > 1:
            collisions += len(active_nodes)
            for i in active_nodes:
                backoff[i] = random.randint(1, BACKOFF_MAX)
                queue[i].pop(0)
        elif len(active_nodes) == 1:
            i = active_nodes[0]
            transmitting[i] = FRAME_DURATION
            successes += 1
            queue[i].pop(0)

        for i in range(NUM_NODES):
            if transmitting[i] > 0:
                transmitting[i] -= 1

    return successes

def maca_sim(rate):
    traffic = generate_traffic(rate, SIM_TIME)
    queue = [list(t) for t in traffic]
    transmitting = [0] * NUM_NODES
    backoff = [0] * NUM_NODES
    collisions = 0
    successes = 0

    for t in range(SIM_TIME):
        for i in range(NUM_NODES):
            if transmitting[i] > 0:
                transmitting[i] -= 1
                continue
            if backoff[i] > 0:
                backoff[i] -= 1
                continue
            if queue[i] and queue[i][0] <= t:
                receiver = (i + 1) % NUM_NODES
                interferers = [j for j in get_visible_nodes(receiver) if j != i and transmitting[j] > 0]
                if not interferers:
                    transmitting[i] = FRAME_DURATION
                    successes += 1
                    queue[i].pop(0)
                else:
                    backoff[i] = random.randint(1, BACKOFF_MAX)
                    collisions += 1
                    queue[i].pop(0)
    return successes

arrival_rates = np.linspace(0.05, 0.5, 10)
csma_successes = [csma_sim(r) for r in arrival_rates]
maca_successes = [maca_sim(r) for r in arrival_rates]

plt.figure(figsize=(8, 5))
plt.plot(arrival_rates, csma_successes, marker='o', label="CSMA (nós ocultos)")
plt.plot(arrival_rates, maca_successes, marker='s', label="MACA (RTS/CTS)")
plt.title("Desempenho do CSMA vs MACA com nós ocultos")
plt.xlabel("Taxa de chegada de quadros")
plt.ylabel("Quadros entregues com sucesso")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
