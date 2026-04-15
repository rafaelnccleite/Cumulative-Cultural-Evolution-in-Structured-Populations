import numpy as np
import matplotlib.pyplot as plt

topologies = ['ER', 'BA', 'WS']

transmission_rules = ['unbiased', 'indirect_bias', 'direct_bias']

topologie_labels = {'ER': 'Random networks', 'BA': 'Scale-free networks', 'WS': 'Small-world networks'}

# Saturation detection parameters

window_size = 4

threshold = 0.01

# Saturation time detection

def detect_equilibrium_time(curve, window_size, threshold):
    for i in range(3, len(curve) - window_size + 1):
        segment = curve[i : i + window_size]

        max_value = np.max(segment)

        min_value = np.min(segment)

        if max_value == 0:
            continue

        variation = (max_value - min_value) / max_value

        if variation < threshold:
            return i

    return None

# Filter saturated curves

def saturated_curves(entries):
    saturated = []

    for d in sorted(entries.keys()):
        equilibrium_time, _ = entries[d]

        if equilibrium_time is not None:
            saturated.append((d, equilibrium_time))

    return saturated

# Equilibrium time computation

all_data = {}

for topologie in topologies:
    for transmission_rule in transmission_rules:

        filename = f'{topologie}_{transmission_rule}.npz'

        data = np.load(filename, allow_pickle = True)

        average_degrees = list(data['average_degrees'])

        key = (topologie, transmission_rule)

        all_data[key] = {}

        for i, average_degree in enumerate(average_degrees):
            curve = np.array(data['average_degree_mean_cultural_complexities'][i], dtype = float)

            equilibrium_time = detect_equilibrium_time(curve, window_size, threshold)

            all_data[key][average_degree] = (equilibrium_time, curve)

markers = ['o', 's', '^']

fig, ax = plt.subplots(1, 3, figsize = (7, 2.5), constrained_layout = True, sharey = False)

for j, topologie in enumerate(topologies):
    for i, transmission_rule in enumerate(transmission_rules):
        key = (topologie, transmission_rule)

        if not all_data[key]:
            continue

        saturated = saturated_curves(all_data[key])

        if not saturated:
            continue

        average_degrees, times = zip(*saturated)

        ax[j].plot(average_degrees, times, linestyle = '-', marker = markers[i], label = transmission_rule.replace('_', ' ').capitalize())

    ax[j].set_title(topologie_labels[topologie])
    ax[j].set_xlabel(r'$\langle k \rangle$')
    ax[j].xaxis.get_major_locator().set_params(integer = True)
    ax[j].grid(alpha = 0.15, linewidth = 0.5)

    if j == 0:
        ax[j].set_ylabel('Time for equilibrium')

    if j == len(topologies) - 1:
        ax[j].legend(frameon = False, loc = 'upper right')

fig.savefig('equilibrium_time.pdf', dpi = 300, bbox_inches = 'tight')
