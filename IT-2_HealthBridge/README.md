# IT-2: HealthBridge — Federated Learning for Multi-Hospital Diagnostics

## Overview

Implement a **federated learning system** for collaborative chest X-ray diagnosis across 5 hospitals without sharing patient data (HIPAA compliance).

## Hospital Data

| Hospital | X-rays | Equipment | Labels |
|---|---|---|---|
| Hospital A | 20,000 | GE Revolution | Standard |
| Hospital B | 15,000 | Siemens SOMATOM | Custom |
| Hospital C | 8,000 | Philips IQon | Standard |
| Hospital D | 12,000 | Canon Aquilion | Custom |
| Hospital E | 5,000 | Hitachi Scenaria | Standard |

## Diagnosis Classes

1. Normal
2. Pneumonia
3. COVID-19
4. Tuberculosis
5. Lung Cancer

## Requirements

| Requirement | Target |
|---|---|
| Model accuracy | >85% overall |
| Privacy guarantee | ε ≤ 3.0 differential privacy |
| Communication rounds | <100 for convergence |
| Straggler tolerance | 10x slower hospital |
| Poisoning robustness | Detect 1 malicious hospital |

## Task

### 1. Federated Learning Framework

Implement FedAvg or superior algorithm:
- Server aggregation
- Client training
- Communication protocol

### 2. Non-IID Data Handling

Different hospitals see different disease distributions:
- Data heterogeneity
- Label imbalance
- Feature shift

### 3. Differential Privacy

Add noise to gradients:
- Gaussian mechanism
- Privacy budget tracking
- Composition theorems

### 4. Secure Aggregation

Server never sees individual updates:
- Masked aggregation
- Cryptographic protocols

### 5. Robustness

Handle adversarial participants:
- Byzantine-robust aggregation
- Anomaly detection
- Reputation systems

## Key Concepts

### Federated Averaging (FedAvg)

```
Server:
    Initialize global model w_0
    for round t = 1 to T:
        Select subset of clients S_t
        for each client k in S_t (in parallel):
            w_k^t ← ClientUpdate(k, w_{t-1})
        w_t ← Σ (n_k / n) * w_k^t  # Weighted average

ClientUpdate(k, w):
    for local epoch e = 1 to E:
        for batch (x,y) in local_data:
            w ← w - η * ∇L(w; x, y)
    return w
```

### Differential Privacy

$$\mathcal{M}(D) = f(D) + \mathcal{N}(0, \sigma^2)$$

Privacy guarantee:
$$\Pr[\mathcal{M}(D) \in S] \leq e^\epsilon \cdot \Pr[\mathcal{M}(D') \in S] + \delta$$

### Secure Aggregation

1. Each client masks their update with random values
2. Masks cancel out when aggregated
3. Server only sees the sum, not individual updates

## Deliverables

1. **FL Framework**: Server + client code
2. **Training Results**: Convergence curves, accuracy per hospital
3. **Privacy Analysis**: ε-budget tracking across rounds
4. **Robustness Analysis**: Poisoning detection results
5. **Comparison**: vs. centralized training

## Project Structure

```
IT-2_HealthBridge/
├── README.md
├── data/
│   ├── hospital_a/
│   ├── hospital_b/
│   ├── hospital_c/
│   ├── hospital_d/
│   └── hospital_e/
├── server/
│   ├── aggregator.py
│   ├── secure_aggregation.py
│   └── robust_aggregation.py
├── client/
│   ├── trainer.py
│   ├── data_loader.py
│   └── privacy.py
├── models/
│   ├── cnn.py
│   └── resnet.py
├── evaluation/
│   ├── metrics.py
│   └── privacy_accountant.py
├── train.py
└── solution_template.py
```

## Tips

1. Start with FedAvg, then add complexity
2. Non-IID data is the biggest challenge - consider FedProx or SCAFFOLD
3. Privacy-utility tradeoff is real - tune noise carefully
4. Secure aggregation adds communication overhead
5. Test with 1 Byzantine client to validate robustness
