# EEE-1: GridBrain — AI-Optimized Microgrid Energy Management

## Overview

Design an **optimal energy management system** for a remote island microgrid that minimizes cost over a 20-year horizon while ensuring reliability and extending battery life.

## System Components

| Component | Capacity | Details |
|---|---|---|
| Solar PV | 500 kW peak | Variable output based on irradiance |
| Wind Turbines | 2 × 250 kW | Variable output based on wind speed |
| Battery Storage | 2 MWh Li-ion | SOC: 10%–90%, degradation: 0.01%/cycle |
| Diesel Generator | 300 kW backup | Fuel cost: $1.50/L, consumption: 0.25 L/kWh |
| Community Load | 400 kW avg, 800 kW peak | Variable demand pattern |

## Data Provided

- **1 year of hourly data** (8760 hours):
  - Solar irradiance (W/m²)
  - Wind speed (m/s)
  - Temperature (°C)
  - Load demand (kW)

## Task

Design an optimization system that:

1. **Minimizes total cost** over 20 years:
   - Fuel costs
   - Battery replacement costs
   - Maintenance costs

2. **Ensures reliability**:
   - No more than 10 hours of load shedding per year
   - Maintain voltage and frequency within limits

3. **Extends battery life**:
   - Optimize charge/discharge cycles
   - Minimize depth of discharge
   - Avoid extreme SOC levels

4. **Adapts in real-time**:
   - Use 24-hour weather forecasts
   - Adjust schedule hourly

## Approach Options

### Option 1: Mixed-Integer Linear Programming (MILP)
- Formulate as optimization problem
- Use solvers like Gurobi, CPLEX, or open-source alternatives
- Guarantees optimality (within linearization)

### Option 2: Dynamic Programming
- Discretize state space
- Handle stochastic inputs
- Good for sequential decision problems

### Option 3: Reinforcement Learning
- Train agent on historical data
- Handle uncertainty naturally
- May find non-obvious strategies

### Option 4: Rule-Based + Optimization
- Simple rules for normal operation
- Optimization for scheduling
- Hybrid approach

## Deliverables

1. **Mathematical Formulation**: Clear problem statement with objective, constraints, variables
2. **Implementation**: Working code for your chosen approach
3. **Simulation Results**: 20-year simulation with key metrics
4. **Sensitivity Analysis**: How solution changes with parameters

## Scoring

| Criterion | Points |
|---|---|
| Total cost (lower is better) | 30 |
| Reliability (hours of load shedding) | 25 |
| Battery degradation | 20 |
| Computational efficiency | 15 |
| Code quality and documentation | 10 |

## Getting Started

1. **Explore the data:**
   ```bash
   python explore_data.py
   ```

2. **Run baseline:**
   ```bash
   python baseline.py
   ```

3. **Implement your solution:**
   ```bash
   python solution.py
   ```

4. **Evaluate:**
   ```bash
   python evaluate.py --solution your_solution.json
   ```

## Project Structure

```
EEE-1_GridBrain/
├── README.md
├── data/
│   ├── solar_irradiance.csv
│   ├── wind_speed.csv
│   ├── temperature.csv
│   ├── load_demand.csv
│   └── equipment_specs.json
├── models/
│   ├── battery.py
│   ├── solar.py
│   ├── wind.py
│   ├── diesel.py
│   └── load.py
├── optimization/
│   ├── milp_solver.py
│   ├── dp_solver.py
│   ├── rl_agent.py
│   └── rule_based.py
├── simulation/
│   ├── simulator.py
│   └── metrics.py
├── baseline.py
├── solution_template.py
└── evaluate.py
```

## Tips

1. Start with the baseline rule-based approach
2. Understand the battery degradation model deeply
3. Consider the trade-off between fuel savings and battery wear
4. Weather forecast uncertainty matters - build in robustness
5. Profile your code - 20-year simulation can be slow
