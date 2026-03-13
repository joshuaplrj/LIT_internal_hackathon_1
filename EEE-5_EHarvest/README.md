# EEE-5: E-Harvest — High-Efficiency RF Energy Harvesting System

## Overview

Design an **RF energy harvesting system** that captures ambient RF energy (900 MHz – 2.4 GHz) and converts it to 100 μW at 1.8V for an IoT sensor.

## Requirements

| Parameter | Requirement |
|---|---|
| Frequency band | 900 MHz – 2.4 GHz |
| Input power | -20 dBm to -10 dBm |
| Efficiency | > 40% @ -10 dBm |
| Output voltage | 1.8V ± 5% |
| Antenna size | 50 mm × 50 mm |
| Storage | Capacitor only (no battery) |

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Antenna                               │
│              (Patch / Dipole / Fractal)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Matching Network                          │
│              (Conjugate match to rectifier)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Rectifier                               │
│         (Dickson Multiplier / Greinacher)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Voltage Regulator                          │
│              (LDO / MPPT / Buck-Boost)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Energy Storage                             │
│                    (Supercapacitor)                          │
└─────────────────────────────────────────────────────────────┘
```

## Antenna Design

### Patch Antenna

```python
import numpy as np

class PatchAntenna:
    def __init__(self, frequency, er=4.4, h=1.6e-3):
        self.f = frequency
        self.er = er
        self.h = h
        self.c = 3e8
    
    def calculate_dimensions(self):
        """Calculate patch antenna dimensions"""
        # Effective dielectric constant
        er_eff = (self.er + 1) / 2 + (self.er - 1) / 2 * (
            1 + 12 * self.h / self.W
        )**(-0.5)
        
        # Width
        W = self.c / (2 * self.f) * np.sqrt(2 / (self.er + 1))
        
        # Length extension
        delta_L = 0.412 * self.h * (er_eff + 0.3) * (W/self.h + 0.264) / (
            (er_eff - 0.258) * (W/self.h + 0.8)
        )
        
        # Effective length
        L_eff = self.c / (2 * self.f * np.sqrt(er_eff))
        L = L_eff - 2 * delta_L
        
        return {'W': W * 1000, 'L': L * 1000}  # mm
    
    def bandwidth(self):
        """Calculate bandwidth"""
        Q = 1  # Simplified
        return self.f / Q
    
    def gain(self):
        """Typical patch antenna gain"""
        return 6  # dBi
```

### Fractal Antenna (Multiband)

```python
class FractalAntenna:
    """Koch fractal antenna for multiband operation"""
    
    def __init__(self, base_length, iterations=3):
        self.base_length = base_length
        self.iterations = iterations
    
    def koch_curve(self, length, iteration):
        """Generate Koch curve points"""
        if iteration == 0:
            return [(0, 0), (length, 0)]
        
        points = []
        sub_length = length / 3
        sub_points = self.koch_curve(sub_length, iteration - 1)
        
        # Transform and concatenate
        # ... (implementation details)
        
        return points
    
    def resonant_frequencies(self):
        """Calculate resonant frequencies"""
        # Fractal reduces effective length
        effective_length = self.base_length * (4/3)**self.iterations
        
        # Multiple resonances due to self-similarity
        f0 = 3e8 / (2 * effective_length)
        return [f0, 2*f0, 3*f0]
```

## Matching Network

```python
class MatchingNetwork:
    def __init__(self, z_antenna, z_rectifier, frequency):
        self.z_antenna = z_antenna
        self.z_rectifier = z_rectifier
        self.f = frequency
    
    def l_network(self):
        """
        Design L-section matching network
        
        For Z_antenna > Z_rectifier:
        ┌───┬───┐
        │   L   │
        ├───┤   │
        │   C   │
        └───┴───┘
        """
        R1 = np.real(self.z_antenna)
        R2 = np.real(self.z_rectifier)
        X1 = np.imag(self.z_antenna)
        X2 = np.imag(self.z_rectifier)
        
        Q = np.sqrt(R1/R2 - 1)
        
        L = Q * R2 / (2 * np.pi * self.f)
        C = Q / (2 * np.pi * self.f * R1)
        
        return {'L': L, 'C': C, 'Q': Q}
    
    def pi_network(self, bandwidth):
        """Design Pi-network for wider bandwidth"""
        # Higher Q, narrower bandwidth
        # Lower Q, wider bandwidth
        pass
```

## Rectifier Design

```python
class Rectifier:
    def __init__(self, stages=3, diode_model='HSMS-2850'):
        self.stages = stages
        self.diode = self.load_diode_model(diode_model)
    
    def load_diode_model(self, model):
        """Load Schottky diode parameters"""
        models = {
            'HSMS-2850': {
                'Vf': 0.25,      # Forward voltage
                'Cj': 0.18e-12,  # Junction capacitance
                'Rs': 25,        # Series resistance
                'Bv': 3.8        # Breakdown voltage
            },
            'SMS7630': {
                'Vf': 0.14,
                'Cj': 0.14e-12,
                'Rs': 20,
                'Bv': 2
            }
        }
        return models.get(model, models['HSMS-2850'])
    
    def voltage_multiplier(self, v_in, n_stages):
        """
        Dickson voltage multiplier
        
        V_out = n * (V_in - V_diode) - I_load / (2 * f * C)
        """
        v_out = n_stages * (v_in - self.diode['Vf'])
        return v_out
    
    def efficiency(self, p_in, frequency):
        """
        Rectifier efficiency
        
        η = P_DC / P_RF
        
        Limited by diode losses at low power
        """
        # Simplified model
        v_in = np.sqrt(p_in * 50)  # Assuming 50 ohm
        
        # Diode conduction loss
        p_diode = self.diode['Vf'] * v_in / self.diode['Rs']
        
        # Capacitive loss
        p_cap = 2 * np.pi * frequency * self.diode['Cj'] * v_in**2
        
        p_dc = p_in - p_diode - p_cap
        return max(0, p_dc / p_in)
    
    def optimal_stages(self, p_in, frequency):
        """Find optimal number of stages for maximum efficiency"""
        best_efficiency = 0
        best_stages = 1
        
        for n in range(1, 10):
            eff = self.efficiency(p_in, frequency) / n  # Efficiency decreases with stages
            if eff > best_efficiency:
                best_efficiency = eff
                best_stages = n
        
        return best_stages, best_efficiency
```

## Voltage Regulator

```python
class VoltageRegulator:
    def __init__(self, v_out=1.8, i_quiescent=1e-6):
        self.v_out = v_out
        self.iq = i_quiescent
    
    def ldo_regulator(self, v_in, i_load):
        """
        Low Dropout Regulator
        
        Efficiency = V_out / V_in
        """
        if v_in < self.v_out + 0.1:  # Dropout voltage
            return None, 0
        
        efficiency = self.v_out / v_in
        power_loss = (v_in - self.v_out) * i_load + v_in * self.iq
        
        return self.v_out, efficiency
    
    def mppt(self, v_in_array, i_in_array):
        """
        Maximum Power Point Tracking
        
        P = V * I
        Find operating point for maximum power
        """
        power = v_in_array * i_in_array
        max_idx = np.argmax(power)
        
        return v_in_array[max_idx], i_in_array[max_idx], power[max_idx]
```

## Energy Storage

```python
class EnergyStorage:
    def __init__(self, capacitance, v_min=1.6, v_max=2.0):
        self.C = capacitance
        self.v_min = v_min
        self.v_max = v_max
    
    def stored_energy(self, voltage):
        """E = 0.5 * C * V²"""
        return 0.5 * self.C * voltage**2
    
    def discharge_time(self, p_load, v_start):
        """
        t = 0.5 * C * (V_start² - V_min²) / P_load
        """
        energy = self.stored_energy(v_start) - self.stored_energy(self.v_min)
        return energy / p_load
    
    def charge_time(self, p_harvest, v_start):
        """
        Time to charge from v_start to v_max
        """
        energy_needed = self.stored_energy(self.v_max) - self.stored_energy(v_start)
        return energy_needed / p_harvest
    
    def size_for_duty_cycle(self, p_load, t_active, t_sleep, p_harvest):
        """
        Size capacitor for given duty cycle
        
        Must store enough energy during sleep to power active period
        """
        energy_per_cycle = p_load * t_active
        energy_harvested = p_harvest * (t_active + t_sleep)
        
        if energy_harvested < energy_per_cycle:
            return None  # Not enough energy
        
        # Extra capacity for margin
        C_min = 2 * energy_per_cycle / (self.v_max**2 - self.v_min**2)
        return C_min
```

## System Simulation

```python
class RFHarvestingSystem:
    def __init__(self):
        self.antenna = PatchAntenna(frequency=2.4e9)
        self.rectifier = Rectifier(stages=3)
        self.regulator = VoltageRegulator(v_out=1.8)
        self.storage = EnergyStorage(capacitance=100e-6)
    
    def simulate(self, p_rf_dbm, duration):
        """Simulate complete system"""
        p_rf = 10**(p_rf_dbm/10) * 1e-3  # Convert to watts
        
        # Antenna efficiency
        p_antenna = p_rf * 0.7  # 70% antenna efficiency
        
        # Matching network loss
        p_matched = p_antenna * 0.9  # 10% matching loss
        
        # Rectification
        eff_rect = self.rectifier.efficiency(p_matched, 2.4e9)
        p_dc = p_matched * eff_rect
        
        # Regulation
        v_rect = self.rectifier.voltage_multiplier(
            np.sqrt(p_matched * 50), 
            self.rectifier.stages
        )
        v_out, eff_reg = self.regulator.ldo_regulator(v_rect, 100e-6)
        
        p_out = p_dc * eff_reg if v_out else 0
        
        return {
            'p_rf': p_rf,
            'p_antenna': p_antenna,
            'p_dc': p_dc,
            'v_rect': v_rect,
            'v_out': v_out,
            'p_out': p_out,
            'efficiency_total': p_out / p_rf if p_rf > 0 else 0
        }
```

## Deliverables

1. **Antenna Design**: Geometry, S11, radiation pattern
2. **Circuit Schematic**: Complete with component values
3. **Simulation Results**: Efficiency vs. frequency and power
4. **Efficiency Analysis**: End-to-end system efficiency
5. **PCB Layout**: 2-layer, 50mm × 50mm

## Project Structure

```
EEE-5_EHarvest/
├── README.md
├── antenna/
│   ├── patch.py
│   ├── fractal.py
│   └── simulation.py
├── circuit/
│   ├── matching.py
│   ├── rectifier.py
│   └── regulator.py
├── system/
│   ├── energy_storage.py
│   └── simulation.py
├── simulation/
│   └── ltspice_circuit.net
├── run_design.py
└── solution_template.py
```

## Tips

1. At -20 dBm, every dB matters - minimize all losses
2. Schottky diodes with low Vf are essential
3. Matching network is critical for efficiency
4. Fewer rectifier stages = higher efficiency at low power
5. Supercapacitor sizing depends on duty cycle
