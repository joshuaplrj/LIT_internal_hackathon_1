# ECE-4: ChipCraft — Mixed-Signal ASIC Design for Biomedical Sensing

## Overview

Design an **analog front-end (AFE) ASIC** for a wearable ECG and PPG sensor with extremely tight power budget.

## Requirements

### ECG Channel

| Parameter | Requirement |
|---|---|
| Input signal | 0.5–5 mV differential |
| Bandwidth | 0.05–150 Hz |
| Input noise | < 5 μVrms |
| CMRR | > 100 dB |
| Input impedance | > 10 GΩ |

### PPG Channel

| Parameter | Requirement |
|---|---|
| Input current | 100 pA – 10 μA |
| LED drive | 20 mA pulse |
| Pulse width | 10 μs – 1 ms |
| SNR | > 60 dB |
| Ambient rejection | > 80 dB |

### ADC

| Parameter | Requirement |
|---|---|
| Resolution | 16-bit |
| Sampling rate | 1 kSPS/channel |
| Channels | 8 |
| ENOB | ≥ 14 bits |
| Power | < 50 μW/channel |

### Total Power Budget

**< 500 μW for entire AFE**

## ECG Front-End Design

### Instrumentation Amplifier

```python
class InstrumentationAmplifier:
    def __init__(self, gain=100, bandwidth=150):
        self.gain = gain
        self.bw = bandwidth
    
    def noise_analysis(self, r_source=1000):
        """
        Input-referred noise
        
        V_n = sqrt(4kTR + V_n_amp² + V_n_1/f²)
        """
        k = 1.38e-23
        T = 300
        
        # Thermal noise from source resistance
        v_n_thermal = np.sqrt(4 * k * T * r_source * self.bw)
        
        # Amplifier voltage noise (typical CMOS)
        v_n_amp = 20e-9  # 20 nV/√Hz
        
        # 1/f noise corner
        f_corner = 10  # Hz
        v_n_1f = v_n_amp * np.sqrt(f_corner / self.bw)
        
        # Total input-referred noise
        v_n_total = np.sqrt(v_n_thermal**2 + (v_n_amp * np.sqrt(self.bw))**2 + v_n_1f**2)
        
        return v_n_total * 1e6  # Convert to μV
    
    def cmrr_analysis(self, resistor_mismatch=0.001):
        """
        CMRR limited by resistor matching
        
        CMRR ≈ 1 / (4 * ΔR/R)
        """
        cmrr_linear = 1 / (4 * resistor_mismatch)
        cmrr_db = 20 * np.log10(cmrr_linear)
        return cmrr_db
    
    def power_consumption(self, gain_bandwidth_product=1e6):
        """
        Power estimation for given GBW
        
        P = V_dd * I_bias
        I_bias ≈ GBW * C_load / (gm/Id)
        """
        V_dd = 1.8  # Supply voltage
        gm_id = 15  # gm/Id for moderate inversion (V⁻¹)
        C_load = 10e-12  # 10 pF
        
        I_bias = gain_bandwidth_product * C_load / gm_id
        power = V_dd * I_bias
        
        return power * 1e6  # Convert to μW
```

### High-Pass Filter (DC Offset Removal)

```python
class HighPassFilter:
    def __init__(self, cutoff=0.05, order=1):
        self.fc = cutoff
        self.order = order
    
    def component_values(self):
        """
        RC high-pass filter
        
        fc = 1 / (2πRC)
        
        For 0.05 Hz with practical component values:
        R = 10 MΩ, C = 330 nF
        """
        # Large R, large C for low cutoff frequency
        R = 10e6  # 10 MΩ
        C = 1 / (2 * np.pi * self.fc * R)
        
        return {'R': R, 'C': C}
    
    def noise_contribution(self, R):
        """
        Resistor thermal noise
        
        V_n = sqrt(4kTRB)
        """
        k = 1.38e-23
        T = 300
        B = self.fc * 10  # Bandwidth of interest
        
        return np.sqrt(4 * k * T * R * B) * 1e6  # μV
```

## PPG Front-End Design

### Transimpedance Amplifier

```python
class TransimpedanceAmplifier:
    def __init__(self, gain=1e6, bandwidth=10e3):
        self.Rf = gain  # Feedback resistance
        self.bw = bandwidth
    
    def noise_analysis(self):
        """
        Input-referred current noise
        
        I_n = sqrt(4kT/Rf + I_n_amp²)
        """
        k = 1.38e-23
        T = 300
        
        # Thermal noise from feedback resistor
        i_n_Rf = np.sqrt(4 * k * T / self.Rf * self.bw)
        
        # Amplifier current noise (CMOS)
        i_n_amp = 1e-15  # 1 fA/√Hz
        
        i_n_total = np.sqrt(i_n_Rf**2 + (i_n_amp * np.sqrt(self.bw))**2)
        
        return i_n_total * 1e12  # Convert to pA
    
    def ambient_light_cancellation(self):
        """
        Ambient light rejection techniques
        
        1. Modulated LED + synchronous detection
        2. Background subtraction
        3. Optical filtering
        """
        return {
            'modulation': 'Square wave at 1 kHz',
            'demodulation': 'Synchronous detector',
            'rejection': '> 80 dB'
        }
```

## SAR ADC Design

```python
class SARADC:
    def __init__(self, resolution=16, sampling_rate=1000):
        self.N = resolution
        self.fs = sampling_rate
    
    def capacitor_dac(self, unit_cap=10e-15):
        """
        Binary-weighted capacitor DAC
        
        C_total = 2^N * C_unit
        """
        C_total = 2**self.N * unit_cap
        
        # Area estimation (MIM capacitor)
        cap_density = 1e-15  # fF/μm²
        area = C_total / cap_density
        
        return {
            'total_capacitance': C_total * 1e15,  # fF
            'area': area * 1e-6,  # mm²
            'unit_cap': unit_cap * 1e15  # fF
        }
    
    def comparator_noise(self, bandwidth):
        """
        Comparator input-referred noise
        
        V_n = sqrt(4kT * γ / C_load)
        """
        k = 1.38e-23
        T = 300
        gamma = 1.5  # Noise factor
        C_load = 100e-15  # 100 fF
        
        V_n = np.sqrt(4 * k * T * gamma / C_load)
        return V_n * 1e6  # μV
    
    def power_estimation(self, vdd=1.8):
        """
        SAR ADC power estimation
        
        P = C_total * Vdd² * fs + P_comparator + P_logic
        """
        cap_info = self.capacitor_dac()
        C_total = cap_info['total_capacitance'] * 1e-15
        
        # DAC switching power
        P_dac = C_total * vdd**2 * self.fs
        
        # Comparator power
        P_comp = 1e-6  # 1 μW typical
        
        # SAR logic power
        P_logic = 0.5e-6  # 0.5 μW
        
        P_total = P_dac + P_comp + P_logic
        
        return P_total * 1e6  # μW
    
    def enob(self, snr_db):
        """
        Effective Number of Bits
        
        ENOB = (SNR - 1.76) / 6.02
        """
        return (snr_db - 1.76) / 6.02
```

## Bandgap Reference

```python
class BandgapReference:
    def __init__(self, vdd=1.8):
        self.vdd = vdd
    
    def output_voltage(self):
        """
        Bandgap reference voltage
        
        V_ref = V_BE + K * V_T * ln(N)
        
        Where V_T = kT/q ≈ 26 mV at 300K
        """
        V_BE = 0.7  # Base-emitter voltage
        V_T = 0.026  # Thermal voltage
        K = 10  # Current ratio
        N = 8   # Area ratio
        
        V_ref = V_BE + K * V_T * np.log(N)
        return V_ref
    
    def temperature_coefficient(self):
        """
        Temperature coefficient
        
        TC = (1/V_ref) * dV_ref/dT
        """
        # Well-designed bandgap: ~10 ppm/°C
        return 10  # ppm/°C
    
    def power_consumption(self):
        """Typical bandgap power"""
        return 10  # μW
```

## System-Level Power Budget

```python
class PowerBudget:
    def __init__(self):
        self.blocks = {}
    
    def add_block(self, name, power_uv):
        self.blocks[name] = power_uv
    
    def total_power(self):
        return sum(self.blocks.values())
    
    def generate_budget(self):
        """Generate complete power budget"""
        self.add_block('ECG InAmp', 50)
        self.add_block('ECG Filters', 20)
        self.add_block('PPG TIA', 30)
        self.add_block('PPG LED Driver', 100)
        self.add_block('ADC (8ch)', 400)
        self.add_block('Bandgap Reference', 10)
        self.add_block('Bias Circuits', 15)
        
        total = self.total_power()
        
        print("=== Power Budget ===")
        for block, power in self.blocks.items():
            print(f"{block:20s}: {power:6.1f} μW ({power/total*100:5.1f}%)")
        print(f"{'TOTAL':20s}: {total:6.1f} μW")
        
        return total
```

## Deliverables

1. **Schematic**: All transistor sizes
2. **Simulation Results**: Each block
3. **ADC Metrics**: INL, DNL, ENOB, power
4. **Power Budget**: System-level
5. **Layout Floorplan**: Area estimation

## Project Structure

```
ECE-4_ChipCraft/
├── README.md
├── ecg_frontend/
│   ├── inamp.py
│   └── filters.py
├── ppg_frontend/
│   ├── tia.py
│   └── ambient_rejection.py
├── adc/
│   └── sar_adc.py
├── reference/
│   └── bandgap.py
├── system/
│   └── power_budget.py
├── run_design.py
└── solution_template.py
```

## Tips

1. Power budget is extremely tight - optimize every block
2. Large resistors needed for low-frequency filters
3. Chopper stabilization helps with 1/f noise
4. SAR ADC is best for low-power applications
5. Bandgap reference sets overall accuracy
