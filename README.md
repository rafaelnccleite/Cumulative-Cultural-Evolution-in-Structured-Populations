# Cumulative Cultural Evolution in Structured Populations

This repository contains code to simulate cumulative cultural evolution in structured populations. The model explores how network topology and transmission rules affect cultural accumulation.

---

## 📁 Scripts

### `networks_cumulative_cultural_evolution.py`
Runs simulations on synthetic networks:
- ER (random)
- BA (scale-free)
- WS (small-world)

**Usage:**
`python networks_cumulative_cultural_evolution.py <average_degree> <simulations_number> <topology> <transmission_rule> [r]`

**Outputs:**
- `.npz` files containing mean trajectories and final cultural complexity

---

### `communication_patterns_cumulative_cultural_evolution.py`
Runs simulations on fixed communication networks (A–H).

**Usage:**
`python communication_patterns_cumulative_cultural_evolution.py <simulations_number> <transmission_rule> [r]`

**Outputs:**
- `.npz` files containing mean cultural complexity over time

---

### `equilibrium_time.py`
Computes equilibrium time from simulation outputs and generates an example figure.

**Outputs:**
- `equilibrium_time.pdf`

---

## ⚙️ Model Overview

- Individuals possess a set of cultural traits  
- Each trait has a fitness value (drawn from an exponential distribution)  
- Individual fitness is the sum of trait fitness values  

### Dynamics per generation:
1. **Transmission** (social learning)  
2. **Innovation** (costly trait discovery)  

### Transmission rules:
- **unbiased** → random neighbor  
- **indirect_bias** → highest-fitness neighbor  
- **direct_bias** → best trait per position  

### Costs:
- Social learning cost: `c_s`  
- Innovation cost: `c_i`  

### Optional feedback (if `r` is provided):

Effort increases with cultural complexity:

`l = l₀ + (l_max - l₀) * (1 - exp(-rC))`
