import numpy as np
import networkx as nx
import random
import sys

np.random.seed(42)
random.seed(42)

if len(sys.argv) in (3, 4):
    simulations_number = int(sys.argv[1])

    transmission_rule = sys.argv[2]

    r = float(sys.argv[3]) if len(sys.argv) == 4 else None

else:
    simulations_number = int(input('Simulations number: '))

    transmission_rule = input('Transmission rule: ')

    r_input = input('r: ').strip()

    r = float(r_input) if r_input else None

A = nx.Graph([(1, 2), (1, 6), (1, 15), (2, 3), (2, 7), (3, 4), (3, 12), (4, 5), (4, 16), (5, 6), (5, 13), (6, 14), (7, 8), (7, 14), (8, 9), (8, 15), (9, 10), (9, 13), (10, 11), (10, 14), (11, 12), (11, 16), (12, 13), (15, 16)])

B = nx.Graph([(1, 2), (1, 11), (1, 14), (2, 3), (2, 4), (3, 5), (3, 14), (4, 15), (4, 16), (5, 6), (5, 15), (6, 7), (6, 8), (7, 13), (7, 16), (8, 9), (8, 16), (9, 10), (9, 11), (10, 12), (10, 13), (11, 12), (12, 15), (13, 14)])

C = nx.Graph([(1, 2), (1, 10), (1, 14), (2, 3), (2, 12), (3, 4), (3, 16), (4, 5), (4, 6), (5, 6), (5, 16), (6, 7), (7, 8), (7, 13), (8, 9), (8, 12), (9, 10), (9, 13), (10, 11), (11, 12), (11, 14), (13, 15), (14, 15), (15, 16)])

D = nx.Graph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 14), (5, 6), (5, 15), (6, 7), (6, 13), (7, 8), (7, 16), (8, 9), (8, 10), (9, 10), (9, 11), (10, 11), (11, 12), (12, 13), (12, 15), (13, 14), (14, 16), (15, 16)])

E = nx.Graph([(1, 2), (1, 15), (1, 16), (2, 3), (2, 16), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (6, 7), (7, 8), (7, 9), (8, 9), (8, 10), (9, 10), (10, 11), (11, 13), (11, 12), (12, 13), (12, 14), (13, 14), (14, 15), (15, 16)])

F = nx.Graph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (6, 7), (6, 12), (7, 8), (7, 11), (8, 9), (8, 10), (9, 10), (9, 11), (10, 11), (12, 13), (12, 14), (13, 15), (13, 16), (14, 15), (14, 16), (15, 16)])

G = nx.Graph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (6, 7), (6, 8), (7, 8), (7, 10), (8, 9), (9, 10), (9, 11), (10, 11), (11, 12), (12, 13), (12, 14), (13, 15), (13, 16), (14, 15), (14, 16), (15, 16)])

H = nx.Graph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9), (8, 10), (9, 10), (9, 11), (10, 11), (11, 12), (12, 13), (12, 14), (13, 15), (13, 16), (14, 15), (14, 16), (15, 16)])

communication_patterns = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G, 'H': H}

# Trait fitness generation

def generate_trait_fitness(X):
    raw = np.random.exponential(scale = 1.0, size = X)

    trait_fitness = np.round(2 * (raw ** 2)).astype(int)

    return trait_fitness

# Population initialization

def initialize_population(G):
    return {node: {'traits': {}, 'individual_fitness': 0} for node in G.nodes()}

# Individual fitness calculation

def calculate_individual_fitness(population, trait_fitness):
    for node in population.keys():
        individual_fitness = 0

        for s, x in population[node]['traits'].items():
            individual_fitness += trait_fitness[x]

        population[node]['individual_fitness'] = int(individual_fitness)

# Population efforts initialization

def initialize_efforts(G, initial_effort):
    return {node: initial_effort for node in G.nodes()}

# Transmission rules

def unbiased_transmission(G, population):
    traits_to_copy = {}

    for node in list(G.nodes()):
        neighbors = list(nx.neighbors(G, node))

        if not neighbors:
            traits_to_copy[node] = {}

        else:
            node_to_copy = random.choice(neighbors)

            traits_to_copy[node] = population[node_to_copy]['traits'].copy()

    return traits_to_copy

def indirect_bias_transmission(G, population):
    traits_to_copy = {}

    for node in list(G.nodes()):
        neighbors = list(nx.neighbors(G, node))

        if not neighbors:
            traits_to_copy[node] = {}

        else:
            node_to_copy = max(neighbors, key = lambda n: population[n]['individual_fitness'])

            traits_to_copy[node] = population[node_to_copy]['traits'].copy()

    return traits_to_copy

def direct_bias_transmission(G, population, trait_fitness):
    traits_to_copy = {}

    for node in list(G.nodes()):
        neighbors = list(nx.neighbors(G, node))

        if not neighbors:
            traits_to_copy[node] = {}

            continue

        max_s = 1

        for neighbor in neighbors:
            if population[neighbor]['traits']:
                max_s = max(max_s, max(population[neighbor]['traits'].keys()))

        node_traits = {}

        for s in range(1, max_s + 1):
            possible_traits = []

            for neighbor in neighbors:
                if s in population[neighbor]['traits']:
                    x = population[neighbor]['traits'][s]

                    possible_traits.append((x, trait_fitness[x]))

            if possible_traits:
                best_trait = max(possible_traits, key=lambda t: t[1])[0]

                node_traits[s] = best_trait

        traits_to_copy[node] = node_traits

    return traits_to_copy

# Innovation

def innovation(node, trait_fitness, effort_left, c_i, X):
    s = max(node['traits'].keys()) + 1 if node['traits'] else 1

    while effort_left >= c_i:
        x = random.randrange(X)

        if trait_fitness[x] > 0:
            node['traits'][s] = x

            effort_left -= c_i

            s += 1

        else:
            effort_left -= c_i

    return effort_left

# Simulation

def run_model(G, T, X, l_0, c_s, c_i, transmission_rule, r = None, l_max = None):
    mean_cultural_complexities = []

    trait_fitness = generate_trait_fitness(X)

    # First generation

    population = initialize_population(G)

    efforts = initialize_efforts(G, l_0)

    for node in population:
        efforts[node] = innovation(population[node], trait_fitness, efforts[node], c_i, X)

    calculate_individual_fitness(population, trait_fitness)

    mean_cultural_complexity = np.mean([population[node]['individual_fitness'] for node in population])

    mean_cultural_complexities.append(mean_cultural_complexity)

    # Next generations

    for t in range(1, T):
        if r is not None:
            l = l_0 + (l_max - l_0) * (1 - np.exp(-r * mean_cultural_complexity))

        else:
            l = l_0

        new_population = initialize_population(G)

        efforts = initialize_efforts(G, l)

        if transmission_rule == 'unbiased':
            traits_to_copy = unbiased_transmission(G, population)

        elif transmission_rule == 'indirect_bias':
            traits_to_copy = indirect_bias_transmission(G, population)

        elif transmission_rule == 'direct_bias':
            traits_to_copy = direct_bias_transmission(G, population, trait_fitness)

        for node in new_population:
            for s, x in traits_to_copy[node].items():
                if efforts[node] >= c_s:

                    new_population[node]['traits'][s] = x

                    efforts[node] -= c_s

        for node in new_population:
            efforts[node] = innovation(new_population[node], trait_fitness, efforts[node], c_i, X)

        calculate_individual_fitness(new_population, trait_fitness)

        mean_cultural_complexity = np.mean([new_population[node]['individual_fitness'] for node in new_population])

        mean_cultural_complexities.append(mean_cultural_complexity)

        population = new_population

    return mean_cultural_complexities

# Parameters

X = 100

c_s = 5

c_i = 10

if r is None:
    T = 20

    l_0 = 1000

    l_max = None

else:
    T = 40

    l_0 = 100

    l_max = 1000

# Run simulations

for label, graph in communication_patterns.items():
    mean_cultural_complexities = []

    for s in range(simulations_number):
        mean_cultural_complexities.append(run_model(graph, T, X, l_0, c_s, c_i, transmission_rule, r = r, l_max = l_max))

    output_filename = f'{label}_{transmission_rule}.npz' if r is None else f'{label}_{transmission_rule}_r{r}.npz'

    save_data = dict(
        T = T, X = X, l_0 = l_0, c_s = c_s, c_i = c_i,

        simulations_number = simulations_number,

        mean_cultural_complexities = np.mean(mean_cultural_complexities, axis = 0)
    )

    if r is not None:
        save_data['r'] = r

        save_data['l_max'] = l_max

    np.savez(output_filename, **save_data)
