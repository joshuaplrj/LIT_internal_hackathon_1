# MBA-2: PricingGenius — Dynamic Pricing Strategy for Ride-Hailing

## Overview

Design a **dynamic pricing strategy** for GoRide, a ride-hailing company processing 5M rides/day across 50 cities.

## Company Profile

| Metric | Value |
|---|---|
| Market Position | #3 (behind Uber + local competitor) |
| Monthly Burn Rate | $50M |
| Path to Profitability | 18 months |
| Daily Rides | 5 million |
| Average Ride Price | $12 |
| Cities | 50 (across 5 countries) |

## Constraints

- Cannot exceed competitor prices by >15%
- Some cities cap surge at 2×
- Must maintain market share
- Regulatory scrutiny on pricing

## Data Provided

- 6 months of ride data (500M rides)
- Competitor price samples (30% coverage)
- Weather data, event calendars, traffic data

## Task

### 1. Demand Forecasting

Predict ride demand at zone-level (500m × 500m grid):
- 15-minute intervals
- 1 hour ahead
- Account for time, weather, events

### 2. Price Elasticity Estimation

Estimate elasticity for:
- Different customer segments
- Different times of day
- Different cities
- Different ride types

### 3. Pricing Engine Design

Components:
- **Base price**: Distance + time calculation
- **Surge multiplier**: Supply/demand balancing
- **Personalized discounts**: Segment-specific
- **Driver incentives**: Supply optimization

### 4. A/B Testing Framework

Design for safe experimentation:
- Metrics to track
- Statistical significance
- Regulatory compliance

### 5. Financial Impact

Quantify vs. current approach:
- Revenue impact
- Profit impact
- Market share impact
- 3-year projection

## Key Concepts

### Price Elasticity of Demand

$$E_d = \frac{\% \Delta Q_d}{\% \Delta P}$$

Where:
- $E_d$ = price elasticity
- $\Delta Q_d$ = change in quantity demanded
- $\Delta P$ = change in price

### Surge Pricing Formula

$$P_{surge} = P_{base} \times \max(1, \alpha \times \frac{D}{S})$$

Where:
- $D$ = demand
- $S$ = supply
- $\alpha$ = calibration factor

### Revenue Optimization

$$\max_{p} R(p) = p \times D(p)$$

Subject to:
- $p \leq 1.15 \times p_{competitor}$
- $p \leq p_{max}$ (regulatory cap)

## Deliverables

1. **Demand Forecasting Model**: Accuracy metrics
2. **Price Elasticity Analysis**: By segment/time/city
3. **Pricing Engine**: Algorithm design
4. **A/B Testing Plan**: Experimental design
5. **Financial Impact**: 3-year projection
6. **Simulation Results**: Revenue, utilization, market share

## Getting Started

1. **Explore the data:**
   ```bash
   python explore_data.py
   ```

2. **Build demand model:**
   ```bash
   python demand_forecasting.py
   ```

3. **Estimate elasticity:**
   ```bash
   python elasticity.py
   ```

4. **Design pricing engine:**
   ```bash
   python pricing_engine.py
   ```

5. **Simulate:**
   ```bash
   python simulate.py
   ```

## Project Structure

```
MBA-2_PricingGenius/
├── README.md
├── data/
│   ├── rides.csv
│   ├── competitor_prices.csv
│   ├── weather.csv
│   └── events.csv
├── models/
│   ├── demand_forecast.py
│   ├── elasticity.py
│   └── pricing.py
├── optimization/
│   ├── surge.py
│   ├── personalization.py
│   └── incentives.py
├── testing/
│   ├── ab_test.py
│   └── metrics.py
├── simulation/
│   ├── simulator.py
│   └── scenarios.py
└── solution_template.py
```

## Tips

1. Demand is highly seasonal and event-driven
2. Elasticity varies significantly by segment
3. Driver supply is also price-sensitive
4. Consider network effects (more drivers → shorter ETAs → more demand)
5. Regulatory constraints vary by city - build flexibility
