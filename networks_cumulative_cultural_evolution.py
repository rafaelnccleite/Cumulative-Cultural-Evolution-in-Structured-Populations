import numpy as np
import networkx as nx
import random
import sys

np.random.seed(42)
random.seed(42)

if len(sys.argv) in (5, 6):
    average_degree = int(sys.argv[1])

    simulations_number = int(sys.argv[2])

    topologie = sys.argv[3]

    transmission_rule = sys.argv[4]

    r = float(sys.argv[5]) if len(sys.argv) == 6 else None

else:
    average_degree = int(input('Average degree: '))

    simulations_number = int(input('Simulations number: '))

    topologie = input('Topologie: ')

    transmission_rule = input('Transmission rule: ')

    r_input = input('r: ').strip()

    r = float(r_input) if r_input else None

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
                best_trait = max(possible_traits, key = lambda t: t[1])[0]

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
    N = 100

    T = 20

    l_0 = 1000

    l_max = None

else:
    N = 50

    T = 50

    l_0 = 100

    l_max = 1000

# Run simulations

mean_cultural_complexities, maximum_cultural_complexities = [], []

for s in range(simulations_number):
    if topologie == 'ER':
        p = average_degree / (N - 1)

        G = nx.erdos_renyi_graph(N, p)

    elif topologie == 'BA':
        m = max(1, average_degree // 2)

        G = nx.barabasi_albert_graph(N, m)

    elif topologie == 'WS':
        p = 0.1

        G = nx.watts_strogatz_graph(N, average_degree, p)

    result = run_model(G, T, X, l_0, c_s, c_i, transmission_rule, r = r, l_max = l_max)

    mean_cultural_complexities.append(result)

    maximum_cultural_complexities.append(result[-1])

# Save results

output_filename = (f'{topologie}_{transmission_rule}_{average_degree}.npz' if r is None else f'{topologie}_{transmission_rule}_{average_degree}_r{r}.npz')

save_data = dict(
    N = N, T = T, X = X, l_0 = l_0, c_s = c_s, c_i = c_i,

    simulations_number = simulations_number,

    average_degree = average_degree,

    average_degree_mean_cultural_complexities = np.mean(mean_cultural_complexities, axis = 0),

    average_degree_maximum_cultural_complexity = np.mean(maximum_cultural_complexities, axis = 0)
)

if r is not None:
    save_data['r'] = r

    save_data['l_max'] = l_max

np.savez(output_filename, **save_data)
