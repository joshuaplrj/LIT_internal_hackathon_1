# EEE-3: MotorForge — Design and Simulation of a 10 kW BLDC Motor

## Overview

Design a **10 kW brushless DC motor** for an electric scooter application with strict size and weight constraints.

## Requirements

| Parameter | Requirement |
|---|---|
| Rated power | 10 kW @ 4000 RPM |
| Peak torque | 40 Nm (0-2000 RPM) |
| Efficiency | > 92% @ rated |
| Voltage | 72V DC bus |
| Cooling | Air-cooled |
| Outer diameter | ≤ 200 mm |
| Axial length | ≤ 150 mm |
| Weight | ≤ 12 kg |

## Design Process

### 1. Electromagnetic Design

#### Pole/Slot Selection

For BLDC motors, common configurations:
- 8 poles / 12 slots
- 10 poles / 12 slots
- 12 poles / 18 slots

```python
def select_pole_slot(rated_speed, switching_freq):
    """
    Select pole/slot combination
    
    Electrical frequency: f_e = (P/2) * n / 60
    where P = poles, n = speed in RPM
    """
    configs = [
        {'poles': 8, 'slots': 12, 'slot_per_pole_per_phase': 0.5},
        {'poles': 10, 'slots': 12, 'slot_per_pole_per_phase': 0.4},
        {'poles': 12, 'slots': 18, 'slot_per_pole_per_phase': 0.5},
    ]
    
    for config in configs:
        f_e = (config['poles'] / 2) * rated_speed / 60
        if f_e < switching_freq / 10:  # Rule of thumb
            return config
    
    return configs[-1]
```

#### Winding Configuration

```python
class WindingDesign:
    def __init__(self, poles, slots):
        self.poles = poles
        self.slots = slots
    
    def back_emf(self, speed_rpm, flux_per_pole, turns_per_coil):
        """
        Back-EMF: E = k_e * ω
        k_e = N * P * φ / (60 * a)
        """
        omega = 2 * np.pi * speed_rpm / 60
        k_e = turns_per_coil * self.poles * flux_per_pole / 60
        return k_e * omega
    
    def torque_constant(self, flux_per_pole, turns_per_coil):
        """
        Torque constant: k_t = N * P * φ / (2π * a)
        For BLDC: k_t ≈ k_e (in SI units)
        """
        return turns_per_coil * self.poles * flux_per_pole / (2 * np.pi)
```

### 2. Magnetic Circuit Analysis

```python
class MagneticCircuit:
    def __init__(self, geometry, material):
        self.geometry = geometry
        self.material = material
    
    def calculate_flux(self, mmf):
        """
        Flux = MMF / Reluctance
        
        Reluctance = l / (μ * A)
        """
        # Air gap reluctance (dominates)
        R_gap = self.geometry['gap_length'] / (
            4 * np.pi * 1e-7 * self.geometry['gap_area']
        )
        
        # Iron reluctance
        R_iron = self.geometry['iron_length'] / (
            self.material['permeability'] * self.geometry['iron_area']
        )
        
        R_total = R_gap + R_iron
        return mmf / R_total
    
    def flux_density(self, flux, area):
        """B = φ / A"""
        return flux / area
```

### 3. Loss Estimation

```python
class LossCalculator:
    def __init__(self, motor_params):
        self.params = motor_params
    
    def copper_loss(self, current, resistance):
        """P_cu = I² * R"""
        return current**2 * resistance
    
    def hysteresis_loss(self, flux_density, frequency, volume):
        """P_h = k_h * f * B^α * V"""
        k_h = self.params['hysteresis_coefficient']
        alpha = 1.6  # Steinmetz exponent
        return k_h * frequency * flux_density**alpha * volume
    
    def eddy_current_loss(self, flux_density, frequency, thickness, volume):
        """P_e = k_e * f² * B² * d² * V"""
        k_e = self.params['eddy_coefficient']
        return k_e * frequency**2 * flux_density**2 * thickness**2 * volume
    
    def total_loss(self, current, flux_density, frequency):
        copper = self.copper_loss(current, self.params['resistance'])
        hysteresis = self.hysteresis_loss(
            flux_density, frequency, self.params['core_volume']
        )
        eddy = self.eddy_current_loss(
            flux_density, frequency,
            self.params['lamination_thickness'],
            self.params['core_volume']
        )
        
        return copper + hysteresis + eddy
```

### 4. Thermal Analysis

```python
class ThermalModel:
    def __init__(self, motor_geometry):
        self.geometry = motor_geometry
    
    def steady_state_temp(self, losses, ambient_temp=25):
        """
        T_junction = T_ambient + P_loss * R_th
        
        R_th = R_conduction + R_convection + R_radiation
        """
        # Thermal resistances
        R_cond = self.geometry['housing_thickness'] / (
            self.geometry['housing_conductivity'] * self.geometry['surface_area']
        )
        
        R_conv = 1 / (
            self.geometry['convection_coeff'] * self.geometry['surface_area']
        )
        
        R_rad = 1 / (
            self.geometry['emissivity'] * 5.67e-8 * 
            self.geometry['surface_area'] * (ambient_temp + 273)**3
        )
        
        R_th = R_cond + 1 / (1/R_conv + 1/R_rad)
        
        return ambient_temp + losses * R_th
    
    def transient_response(self, losses, time, thermal_capacitance):
        """
        T(t) = T_ambient + P * R_th * (1 - exp(-t/τ))
        τ = R_th * C_th
        """
        R_th = self.calculate_thermal_resistance()
        tau = R_th * thermal_capacitance
        
        return 25 + losses * R_th * (1 - np.exp(-time / tau))
```

### 5. FOC Controller

```python
class FOCController:
    """Field-Oriented Control for BLDC motor"""
    
    def __init__(self, motor_params):
        self.params = motor_params
        self.current_pi = PIController(kp=0.5, ki=100)
        self.speed_pi = PIController(kp=10, ki=200)
    
    def park_transform(self, i_alpha, i_beta, theta):
        """abc → dq transformation"""
        i_d = i_alpha * np.cos(theta) + i_beta * np.sin(theta)
        i_q = -i_alpha * np.sin(theta) + i_beta * np.cos(theta)
        return i_d, i_q
    
    def inverse_park(self, v_d, v_q, theta):
        """dq → αβ transformation"""
        v_alpha = v_d * np.cos(theta) - v_q * np.sin(theta)
        v_beta = v_d * np.sin(theta) + v_q * np.cos(theta)
        return v_alpha, v_beta
    
    def current_control(self, i_d_ref, i_q_ref, i_d, i_q):
        """Current control loop"""
        v_d = self.current_pi.update(i_d_ref - i_d)
        v_q = self.current_pi.update(i_q_ref - i_q)
        return v_d, v_q
    
    def speed_control(self, speed_ref, speed_actual):
        """Speed control loop → generates i_q_ref"""
        return self.speed_pi.update(speed_ref - speed_actual)
```

## Deliverables

1. **Design Document**: All calculations
2. **Motor Parameters Table**: Complete specifications
3. **Simulation Model**: Python/MATLAB implementation
4. **Performance Verification**: Against all requirements

## Project Structure

```
EEE-3_MotorForge/
├── README.md
├── design/
│   ├── electromagnetic.py
│   ├── magnetic_circuit.py
│   ├── losses.py
│   └── thermal.py
├── control/
│   └── foc_controller.py
├── simulation/
│   ├── motor_model.py
│   └── drive_cycle.py
├── data/
│   └── materials.json
├── run_design.py
└── solution_template.py
```

## Tips

1. Start with power requirement and work backwards
2. Air gap is critical - smaller gap = higher efficiency but harder to manufacture
3. Lamination thickness affects eddy current losses
4. Thermal management often limits continuous power
5. FOC provides smooth torque control
