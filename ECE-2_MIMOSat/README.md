# ECE-2: MIMO-Sat — LEO Satellite Communication Link Design

## Overview

Design a **communication link** for a Low Earth Orbit (LEO) satellite constellation providing broadband internet to rural areas.

## System Parameters

| Parameter | Value |
|---|---|
| Orbit altitude | 550 km |
| Downlink frequency | 12 GHz (Ku-band) |
| Uplink frequency | 14 GHz (Ku-band) |
| Ground antenna | 1.2 m parabolic dish |
| Satellite antenna | 256-element phased array |
| Downlink data rate | 100 Mbps |
| Uplink data rate | 10 Mbps |
| BER requirement | 10⁻⁶ |

## Link Budget Analysis

### Free Space Path Loss

$$FSPL = 20\log_{10}(d) + 20\log_{10}(f) + 32.44 \text{ dB}$$

Where:
- $d$ = distance in km
- $f$ = frequency in MHz

### Received Power

$$P_r = P_t + G_t + G_r - FSPL - L_{atm} - L_{rain} - L_{pointing}$$

### Link Budget Calculator

```python
import numpy as np

class LinkBudget:
    def __init__(self, frequency, altitude):
        self.f = frequency
        self.h = altitude
        self.c = 3e8
        self.k = 1.38e-23  # Boltzmann constant
    
    def free_space_loss(self, distance):
        """FSPL in dB"""
        wavelength = self.c / self.f
        return 20 * np.log10(4 * np.pi * distance / wavelength)
    
    def slant_range(self, elevation_angle):
        """Calculate slant range from elevation angle"""
        Re = 6371  # Earth radius in km
        theta = np.radians(elevation_angle)
        
        d = Re * np.sin(theta) + np.sqrt(
            (Re * np.sin(theta))**2 + 2 * Re * self.h + self.h**2
        )
        return d
    
    def atmospheric_loss(self, elevation_angle):
        """Atmospheric absorption"""
        # Zenith attenuation at Ku-band ~0.1 dB
        zenith_atten = 0.1
        return zenith_atten / np.sin(np.radians(elevation_angle))
    
    def rain_attenuation(self, rain_rate, elevation_angle):
        """
        ITU-R P.618 rain attenuation model
        
        A_rain = γ_R * L_s / sin(θ)
        """
        # Specific attenuation coefficients for Ku-band
        k = 0.0367  # Horizontal polarization
        alpha = 1.1544
        
        gamma_r = k * rain_rate**alpha  # dB/km
        
        # Effective path length
        L_s = min(35, self.h / np.sin(np.radians(elevation_angle)))
        
        return gamma_r * L_s / np.sin(np.radians(elevation_angle))
    
    def antenna_gain(self, diameter, efficiency=0.6):
        """Parabolic antenna gain"""
        wavelength = self.c / self.f
        return 10 * np.log10(
            efficiency * (np.pi * diameter / wavelength)**2
        )
    
    def g_t(self, antenna_temp=150):
        """Figure of merit G/T"""
        gain_linear = 10**(self.antenna_gain(1.2) / 10)
        T_sys = antenna_temp + 290  # System noise temperature
        return 10 * np.log10(gain_linear / T_sys)
    
    def eb_n0(self, p_received, data_rate, noise_figure=3):
        """Calculate Eb/N0"""
        noise_power = self.k * 290 * data_rate * 10**(noise_figure/10)
        eb_n0_linear = p_received / noise_power
        return 10 * np.log10(eb_n0_linear)
    
    def required_eb_n0(self, ber=1e-6, coding_gain=0):
        """
        Required Eb/N0 for given BER
        
        For QPSK: Eb/N0 ≈ 10.5 dB @ BER=1e-6
        """
        eb_n0_uncoded = 10.5  # QPSK
        return eb_n0_uncoded - coding_gain
    
    def link_margin(self, p_received, data_rate, ber=1e-6):
        """Calculate link margin"""
        eb_n0_actual = self.eb_n0(p_received, data_rate)
        eb_n0_required = self.required_eb_n0(ber)
        return eb_n0_actual - eb_n0_required
```

## Modulation and Coding

### Modulation Selection

| Modulation | Spectral Efficiency | Required Eb/N0 | Margin |
|---|---|---|---|
| QPSK | 2 bps/Hz | 10.5 dB | High |
| 8PSK | 3 bps/Hz | 14.0 dB | Medium |
| 16APSK | 4 bps/Hz | 16.5 dB | Low |

### FEC Code Selection

| Code | Rate | Coding Gain | Complexity |
|---|---|---|---|
| LDPC | 0.75 | 9 dB | Medium |
| Turbo | 0.67 | 8 dB | High |
| Polar | 0.75 | 9.5 dB | Medium |

```python
class ModulationCoding:
    def __init__(self):
        self.modulations = {
            'QPSK': {'efficiency': 2, 'ebn0_req': 10.5},
            '8PSK': {'efficiency': 3, 'ebn0_req': 14.0},
            '16APSK': {'efficiency': 4, 'ebn0_req': 16.5}
        }
        
        self.codes = {
            'LDPC_3/4': {'rate': 0.75, 'gain': 9.0},
            'Turbo_2/3': {'rate': 0.67, 'gain': 8.0},
            'Polar_3/4': {'rate': 0.75, 'gain': 9.5}
        }
    
    def select_modcod(self, required_rate, bandwidth, available_ebn0):
        """Select modulation and coding scheme"""
        for mod_name, mod in self.modulations.items():
            for code_name, code in self.codes.items():
                spectral_eff = mod['efficiency'] * code['rate']
                achievable_rate = bandwidth * spectral_eff
                
                required_ebn0 = mod['ebn0_req'] - code['gain']
                
                if achievable_rate >= required_rate and required_ebn0 <= available_ebn0:
                    return {
                        'modulation': mod_name,
                        'coding': code_name,
                        'rate': achievable_rate,
                        'required_ebn0': required_ebn0
                    }
        
        return None
```

## Doppler Analysis

```python
class DopplerAnalysis:
    def __init__(self, frequency, altitude=550e3):
        self.f = frequency
        self.h = altitude
        self.c = 3e8
    
    def satellite_velocity(self):
        """Orbital velocity"""
        G = 6.674e-11  # Gravitational constant
        M = 5.972e24   # Earth mass
        Re = 6371e3    # Earth radius
        
        r = Re + self.h
        return np.sqrt(G * M / r)
    
    def max_doppler_shift(self):
        """Maximum Doppler shift"""
        v = self.satellite_velocity()
        return v * self.f / self.c
    
    def doppler_rate(self, elevation_angle):
        """Rate of Doppler change"""
        v = self.satellite_velocity()
        Re = 6371e3
        
        # Simplified model
        theta = np.radians(elevation_angle)
        dopp_rate = v**2 * self.f / (self.c * (Re + self.h))
        
        return dopp_rate
    
    def compensation_strategy(self):
        """Doppler compensation approach"""
        return {
            'pre_correction': 'Predict Doppler from ephemeris',
            'tracking': 'AFC loop in receiver',
            'range': f'±{self.max_doppler_shift()/1e3:.1f} kHz'
        }
```

## Beamforming

```python
class PhasedArray:
    def __init__(self, num_elements, spacing, frequency):
        self.N = num_elements
        self.d = spacing
        self.f = frequency
        self.c = 3e8
        self.wavelength = self.c / frequency
    
    def array_factor(self, theta, phi, weights):
        """Calculate array factor"""
        k = 2 * np.pi / self.wavelength
        
        # Element positions (linear array)
        n = np.arange(self.N)
        positions = n * self.d
        
        # Phase shifts
        phase = k * positions * np.sin(np.radians(theta))
        
        # Array factor
        af = np.sum(weights * np.exp(1j * phase))
        
        return np.abs(af)
    
    def beam_pattern(self, scan_angle):
        """Calculate beam pattern for given scan angle"""
        # Steering vector
        k = 2 * np.pi / self.wavelength
        n = np.arange(self.N)
        steering = np.exp(-1j * k * n * self.d * np.sin(np.radians(scan_angle)))
        
        # Uniform weights
        weights = steering / self.N
        
        # Calculate pattern
        theta_range = np.arange(-90, 91, 1)
        pattern = [self.array_factor(t, 0, weights) for t in theta_range]
        
        return theta_range, pattern
    
    def scan_loss(self, scan_angle):
        """Gain loss due to scanning"""
        # Element pattern (cosine approximation)
        element_gain = np.cos(np.radians(scan_angle))
        
        # Projected aperture
        aperture_loss = np.cos(np.radians(scan_angle))
        
        return 10 * np.log10(element_gain * aperture_loss)
```

## Deliverables

1. **Link Budget Spreadsheets**: Both directions
2. **Modulation/Coding Selection**: With waterfall curves
3. **Beam Pattern Plots**: And hopping schedule
4. **Doppler Analysis**: And compensation strategy
5. **ACM Table**: And availability analysis
6. **Link Simulation**: MATLAB/Python

## Project Structure

```
ECE-2_MIMOSat/
├── README.md
├── link_budget/
│   ├── calculator.py
│   └── rain_model.py
├── modulation/
│   ├── modcod.py
│   └── ber_curves.py
├── beamforming/
│   ├── phased_array.py
│   └── beam_hopping.py
├── doppler/
│   └── analysis.py
├── simulation/
│   └── link_sim.py
├── run_analysis.py
└── solution_template.py
```

## Tips

1. Rain attenuation is the dominant impairment at Ku-band
2. Doppler shift is massive at LEO - must compensate
3. Beam hopping maximizes satellite capacity
4. ACM adapts to channel conditions
5. Link margin of 3 dB is typical for rain fade
