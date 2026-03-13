# EEE-4: PowerShield — Solid-State Circuit Breaker for DC Microgrids

## Overview

Design a **solid-state circuit breaker (SSCB)** for a 400V DC microgrid with ultra-fast fault interruption capability.

## Requirements

| Parameter | Requirement |
|---|---|
| Rated voltage | 400V DC |
| Rated current | 200A continuous |
| Breaking capacity | 10 kA |
| Breaking time | < 100 μs |
| Direction | Bidirectional |
| Voltage clamping | < 600V |
| Switching cycles | 10,000 |

## Topology Options

### 1. Series-Connected MOSFETs

```
        ┌──────┐
   +────┤      ├────+
        │ MOS  │
        │ FET  │
   -────┤      ├────-
        └──────┘
           │
        ┌──┴──┐
        │Gate │
        │Driver│
        └─────┘
```

### 2. Full-Bridge Configuration (Bidirectional)

```
        ┌──────┐    ┌──────┐
   +────┤ Q1   ├────┤ Q3   ├────+
        │      │    │      │
        └──────┘    └──────┘
             │          │
             └────┬─────┘
                  │
             ┌────┴────┐
             │  Load   │
             └────┬────┘
                  │
        ┌──────┐    ┌──────┐
   -────┤ Q2   ├────┤ Q4   ├────-
        │      │    │      │
        └──────┘    └──────┘
```

## Semiconductor Selection

### SiC MOSFET vs IGBT

| Parameter | SiC MOSFET | IGBT |
|---|---|---|
| Switching speed | Very fast (< 100 ns) | Slow (μs) |
| Conduction loss | Low at high voltage | Low at high current |
| Temperature | Higher capability | Limited |
| Cost | Higher | Lower |
| **Verdict** | **Selected** | Rejected |

### Selected Device: C3M0075120K

- Voltage: 1200V
- Current: 300A (pulsed)
- Rds(on): 75 mΩ
- Switching time: < 50 ns

## Snubber/Clamping Circuit

```python
class SnubberDesign:
    def __init__(self, voltage, current, di_dt):
        self.V = voltage
        self.I = current
        self.di_dt = di_dt
    
    def design_rc_snubber(self):
        """
        RC snubber for voltage clamping
        
        C = I² * L / (V_clamp² - V_bus²)
        R = V_clamp / I_peak
        """
        L_parasitic = 100e-9  # 100 nH typical
        
        V_clamp = 600  # Maximum allowed
        I_peak = 10000  # 10 kA fault
        
        C = I_peak**2 * L_parasitic / (V_clamp**2 - self.V**2)
        R = V_clamp / I_peak
        
        return {'C': C, 'R': R}
    
    def design_mov(self):
        """
        Metal Oxide Varistor selection
        
        V_mov = 1.2 * V_rated (continuous)
        """
        V_mov = 1.2 * self.V
        energy_rating = 0.5 * self.I**2 * 100e-6  # 100 μs interruption
        
        return {
            'voltage': V_mov,
            'energy': energy_rating,
            'part': 'MOV-400V-10kJ'
        }
```

## Gate Driver Design

```python
class GateDriver:
    def __init__(self, mosfet_params):
        self.params = mosfet_params
    
    def calculate_gate_charge(self, v_gs, i_peak):
        """
        Q_g = C_iss * V_gs
        t_rise = Q_g / I_gate
        """
        C_iss = self.params['input_capacitance']
        Q_g = C_iss * v_gs
        
        # Gate driver current for < 100 ns switching
        I_gate = Q_g / 100e-9
        
        return {
            'gate_charge': Q_g,
            'driver_current': I_gate,
            'driver_voltage': v_gs
        }
    
    def design_driver_circuit(self):
        """Isolated gate driver with fast turn-off"""
        return {
            'driver_ic': 'UCC21710',
            'isolation': 'Capacitive',
            'propagation_delay': '50 ns',
            'peak_source': '10A',
            'peak_sink': '10A'
        }
```

## Fault Detection

```python
class FaultDetector:
    def __init__(self, rated_current, sampling_rate=10e6):
        self.I_rated = rated_current
        self.fs = sampling_rate
        self.dt = 1 / sampling_rate
    
    def detect_overcurrent(self, current, threshold=1.5):
        """Fast overcurrent detection"""
        return current > threshold * self.I_rated
    
    def detect_di_dt(self, current_history, threshold=1e9):
        """
        di/dt detection for fast faults
        
        di/dt > 1 A/ns indicates short circuit
        """
        di_dt = np.diff(current_history) / self.dt
        return np.any(di_dt > threshold)
    
    def detect_fault_type(self, voltage, current):
        """Classify fault type"""
        if current > 10 * self.I_rated:
            return 'short_circuit'
        elif current > 2 * self.I_rated:
            return 'overload'
        elif voltage < 0.8 * 400:
            return 'undervoltage'
        else:
            return 'normal'
```

## Thermal Design

```python
class ThermalDesign:
    def __init__(self, power_loss, ambient=40):
        self.P_loss = power_loss
        self.T_ambient = ambient
    
    def heatsink_selection(self, max_junction_temp=150):
        """
        R_th_ja = (T_j - T_a) / P_loss
        
        R_th_ja = R_th_jc + R_th_cs + R_th_sa
        """
        R_th_jc = 0.5  # Junction to case (°C/W)
        R_th_cs = 0.1  # Case to sink (°C/W)
        
        R_th_ja_max = (max_junction_temp - self.T_ambient) / self.P_loss
        R_th_sa = R_th_ja_max - R_th_jc - R_th_cs
        
        return {
            'thermal_resistance': R_th_sa,
            'heatsink_type': 'Forced air' if R_th_sa < 1 else 'Natural convection'
        }
    
    def transient_thermal(self, fault_energy, fault_duration):
        """
        Temperature rise during fault
        
        ΔT = E_fault / (m * c_p)
        """
        m = 0.01  # 10g silicon die
        c_p = 700  # J/(kg·K) for silicon
        
        delta_T = fault_energy / (m * c_p)
        return delta_T
```

## Simulation (LTSpice Netlist)

```
* Solid-State Circuit Breaker Simulation
* 400V DC, 200A rated, 10kA breaking

V1 N001 0 400
R1 N001 N002 0.01 ; Line resistance
L1 N002 N003 100nH ; Parasitic inductance

* SiC MOSFET model
M1 N003 N004 N005 N005 SiC_MOSFET

* Gate driver
V_gate N004 0 PULSE(0 20 0 10n 10n 100u 200u)

* Load
R_load N005 0 2 ; 200A at 400V

* Snubber
R_snub N003 N006 0.1
C_snub N006 0 1u

* MOV
D_mov N003 0 MOV_model

* Fault (short circuit at t=50us)
S_fault N005 0 N007 0 SW_fault
.model SW_fault SW(Vt=2.5 Ron=0.01)
V_fault_trigger N007 0 PULSE(0 5 50u 1n 1n 10u 100u)

.tran 200u
.end
```

## Deliverables

1. **Complete Schematic**: With component values
2. **Design Calculations**: All engineering analysis
3. **Simulation Waveforms**: Fault interruption sequence
4. **Loss Analysis**: Conduction and switching losses
5. **Thermal Analysis**: Steady-state and transient
6. **BOM**: With estimated cost

## Project Structure

```
EEE-4_PowerShield/
├── README.md
├── design/
│   ├── semiconductor_selection.py
│   ├── snubber_design.py
│   ├── gate_driver.py
│   └── thermal.py
├── simulation/
│   ├── sscb_ltspice.net
│   └── analyze_results.py
├── fault_detection/
│   └── detector.py
├── schematics/
│   └── sscb_schematic.pdf
├── run_design.py
└── solution_template.py
```

## Tips

1. SiC MOSFETs are essential for < 100 μs switching
2. Parasitic inductance is your enemy - minimize loop area
3. Snubber design is critical for voltage clamping
4. Gate driver must be isolated and very fast
5. Thermal management during fault is challenging
