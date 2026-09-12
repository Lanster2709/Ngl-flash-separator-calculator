from scipy.optimize import brentq
import numpy as np
import matplotlib.pyplot as plt
# Inputs dictionary
feed = {
    "Methane": 0.40, #fraction
    "Ethane": 0.25, #fraction
    "Propane": 0.20, #fraction
    "n-Butane": 0.15 #fraction
}

antoine = {
    "Methane": {"A": 3.9895, "B": 443.028, "C": -0.49},
    "Ethane": {"A": 4.50706, "B": 791.3, "C": -6.422},
    "Propane": {"A": 4.53678, "B": 1149.36, "C": 24.906},
    "n-Butane": {"A": 4.35576, "B": 1175.581, "C": -2.071}
}
conditions = {
    "Temperature": -30, #C
    "Pressure":5 #bar
}

# Antoine equation function
def antoine_pressure(temperature, constants):
    A = constants["A"]
    B = constants["B"]
    C = constants["C"]
    T_kelvin = temperature + 273.15
    P_sat = 10 ** (A - B / (T_kelvin + C))
    return P_sat

# K-value function
def calculate_k_values(temperature, pressure, antoine):
    k_values = {}
    for component in antoine:
        P_sat = antoine_pressure(temperature, antoine[component])
        K = P_sat / pressure
        k_values[component] = K
    return k_values
k_values = calculate_k_values(conditions["Temperature"], conditions["Pressure"], antoine)

# Rachford-Rice solver
def rachford_rice(V, feed, k_values):
    total = 0
    for component in feed:
        z = feed[component]
        K = k_values[component]
        total += z * (K - 1) / (1 + V * (K - 1))
    return total

# Composition calculations 
def calculate_compositions(V, feed, k_values):
    liquid_composition = {}
    vapor_composition = {}
    for component in feed:
        z = feed[component]
        K = k_values[component]
        x = z / (1 + V * (K - 1))
        y = K * x 
        liquid_composition[component] = x
        vapor_composition[component] = y
    return liquid_composition, vapor_composition

# Bubble point and dew point validation
def check_two_phase(feed, k_values):
    rachford_rice_at_zero = rachford_rice(0, feed, k_values)
    rachford_rice_at_one = rachford_rice(1, feed, k_values)
    rachford_rice_product = rachford_rice_at_zero * rachford_rice_at_one
    if rachford_rice_product < 0:
        return True
    else:
        return False

# Phase validation
two_phase = check_two_phase(feed, k_values)
if two_phase:
    V = brentq(rachford_rice, 0, 1, args=(feed, k_values))
    x , y = calculate_compositions(V, feed, k_values)
    print("Two-phase region confirmed, proceed with flash calculation.")
    print(f"Flash vapor fraction (V): {V:.4f}")
    print("\n Vapor-Liquid Composition ")    
    for component in x:
        print(f"{component}: x = {x[component]:.4f}, y = {y[component]:.4f}")

# Vapor vs Liquid composition bar chart
    components_list = list(x.keys())
    x_values = list(x.values())
    y_values = list(y.values())

    bar_width = 0.35
    positions = np.arange(len(components_list)) # [0, 1, 2, 3]

    plt.figure(figsize=(8, 6))
    bars_liquid = plt.bar(positions - bar_width/2, x_values, bar_width, label="Liquid (x)", color="#4C72B0")
    bars_vapor = plt.bar(positions + bar_width/2, y_values, bar_width, label="Vapor (y)", color="#DD8452")

    for bar, val in zip(bars_liquid, x_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    for bar, val in zip(bars_vapor, y_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    plt.xlabel("Component")
    plt.ylabel("Mole Fraction")
    plt.title("Vapor vs Liquid Composition")
    plt.xticks(positions, components_list)
    plt.legend()
    plt.tight_layout()
    plt.savefig("Flash_Composition_Comparison.png", dpi=200)
    plt.show()
else:
    print("Conditions outside two-phase region so cannot proceed with flash calculation..")

# Bubble point and dew point pressure calculations
def bubble_point_pressure(temperautre, feed, antoine):
    P_bubble = 0
    for component in feed:
        z = feed[component]
        P_sat = antoine_pressure(temperautre, antoine[component])
        P_bubble += z * P_sat
    return P_bubble

def dew_point_pressure(temperature, feed, antoine):
    sum_term = 0
    for component in feed:
        z = feed[component]
        P_sat = antoine_pressure(temperature, antoine[component])
        sum_term += z / P_sat
        P_dew = 1 / sum_term
    return P_dew

P_bub = bubble_point_pressure(conditions["Temperature"], feed, antoine)
P_dew = dew_point_pressure(conditions["Temperature"], feed, antoine)
print(f"Bubble point pressure at {conditions['Temperature']}°C: {P_bub:.2f} bar")
print(f"Dew point pressure at {conditions['Temperature']}°C: {P_dew:.2f} bar")

# Range of temperatures 
temperatures = np.linspace(-50, 50, 21)

bubble_pressure = []
dew_pressure = []

for T in temperatures:
    P_bub = bubble_point_pressure(T, feed, antoine)
    P_dew = dew_point_pressure(T, feed, antoine)
    bubble_pressure.append(P_bub)
    dew_pressure.append(P_dew)

# Plot
plt.figure(figsize=(8, 6))
plt.plot(temperatures, bubble_pressure, label="Bubble Point", color="#4C72B0")  
plt.plot(temperatures, dew_pressure, label="Dew Point", color="#DD8452")
plt.fill_between(temperatures, dew_pressure, bubble_pressure, color="grey", alpha=0.15, label="Two-phase region")
plt.scatter([conditions["Temperature"]], [conditions["Pressure"]], 
            color="red", zorder=5, s=80, label="Selected operating point")
plt.annotate(f"({conditions['Temperature']}°C, {conditions['Pressure']} bar)",
             (conditions["Temperature"], conditions["Pressure"]),
             textcoords="offset points", xytext=(10, 10))

plt.xlabel("Temperature (°C)")
plt.ylabel("Pressure (bar)")
plt.title("Bubble and Dew Point Curves")
plt.legend()
plt.tight_layout()
plt.savefig("Bubble_Dew_Point_Curves.png", dpi=200)
plt.show()

