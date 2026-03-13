# MBA-3: SupplyZen — Supply Chain Resilience Optimization

## Overview

Design a **resilient supply chain strategy** for ElectraTech, a $10B consumer electronics company facing multiple simultaneous disruptions.

## Company Profile

| Metric | Value |
|---|---|
| Annual Revenue | $10B |
| Components | 2,000 from 500 suppliers |
| Countries | 20 (suppliers), 5 (manufacturing) |
| Distribution Centers | 50 globally |
| Products | 3 SKUs (smartphone, tablet, laptop) |
| Annual Volume | 100M units |
| Current Inventory | 3 weeks (target: 8 weeks) |

## Current Disruptions

| Disruption | Impact |
|---|---|
| Semiconductor shortage | 40% of components affected |
| Red Sea shipping | Costs up 300%, transit +40% |
| Factory fire | 6-month recovery at critical supplier |
| Tariff uncertainty | 25% tariffs (50% probability) |

## Task

### 1. Risk Assessment

- Map supply chain (Tier 1, 2, 3 suppliers)
- Identify single points of failure
- Calculate probability and impact
- Build risk heat map

### 2. Mitigation Strategies

Evaluate each:

| Strategy | Description |
|---|---|
| Dual sourcing | Qualify alternative suppliers |
| Nearshoring | Move manufacturing closer to markets |
| Inventory buffering | Increase safety stock |
| Product redesign | Substitute hard-to-source components |
| Vertical integration | Acquire/invest in critical suppliers |
| Digital twin | Real-time simulation for planning |

### 3. Optimization Model

Minimize total cost subject to:
- Service level > 95%
- Lead time < 4 weeks
- Quality defect rate < 0.1%

Decisions:
- Supplier allocation
- Manufacturing allocation
- Inventory levels
- Transportation modes

### 4. Financial Analysis

- Cost of each strategy
- Expected value (factoring disruption probability)
- ROI and payback period
- Impact on gross margin

### 5. Implementation Roadmap

- Prioritized 18-month plan
- Milestones and KPIs

## Key Concepts

### Risk Quantification

$$Risk = Probability \times Impact \times Exposure$$

### Safety Stock Calculation

$$SS = Z \times \sigma_{demand} \times \sqrt{L}$$

Where:
- $Z$ = service level factor
- $\sigma_{demand}$ = demand variability
- $L$ = lead time

### Total Cost of Ownership

$$TCO = P + S + O + Q + R$$

Where:
- $P$ = purchase cost
- $S$ = shipping cost
- $O$ = ordering cost
- $Q$ = quality cost
- $R$ = risk cost

## Deliverables

1. **Risk Assessment Report**: Heat map and analysis
2. **Optimization Model**: Mathematical formulation + solution
3. **Financial Analysis**: Strategy comparison
4. **Implementation Roadmap**: 18-month plan
5. **Executive Presentation**: Board-ready slides

## Getting Started

1. **Map the supply chain:**
   ```bash
   python map_supply_chain.py
   ```

2. **Assess risks:**
   ```bash
   python risk_assessment.py
   ```

3. **Build optimization model:**
   ```bash
   python optimization.py
   ```

4. **Analyze strategies:**
   ```bash
   python strategy_analysis.py
   ```

## Project Structure

```
MBA-3_SupplyZen/
├── README.md
├── data/
│   ├── suppliers.csv
│   ├── components.csv
│   ├── logistics.csv
│   └── disruptions.csv
├── risk/
│   ├── assessment.py
│   ├── heat_map.py
│   └── scenarios.py
├── optimization/
│   ├── model.py
│   ├── solver.py
│   └── constraints.py
├── strategies/
│   ├── dual_sourcing.py
│   ├── nearshoring.py
│   └── inventory.py
├── financial/
│   ├── analysis.py
│   └── roi.py
└── solution_template.py
```

## Tips

1. Start with risk quantification - you can't manage what you don't measure
2. Consider correlation between disruptions
3. Inventory is expensive but stockouts are more expensive
4. Nearshoring has higher unit cost but lower risk
5. Digital twin enables scenario planning
