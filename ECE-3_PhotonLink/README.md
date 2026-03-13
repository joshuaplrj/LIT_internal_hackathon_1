# ECE-3: PhotonLink — Free-Space Optical Communication System

## Overview

Design a **Free-Space Optical (FSO) communication link** between two buildings 5 km apart with 10 Gbps data rate and 99.9% availability.

## Requirements

| Parameter | Requirement |
|---|---|
| Distance | 5 km |
| Data rate | 10 Gbps |
| Wavelength | 1550 nm |
| Availability | 99.9% |
| BER | 10⁻⁹ |

## Atmospheric Challenges

| Condition | Impact |
|---|---|
| Heavy fog | >100 dB/km attenuation |
| Rain | Up to 50 mm/hr |
| Scintillation | Intensity fluctuations |
| Pointing errors | ±1 mrad building sway |

## Link Budget

### Free Space Loss

$$L_{fs} = \left(\frac{4\pi d}{\lambda}\right)^2$$

### Atmospheric Attenuation

**Kim model for fog:**
$$\alpha_{fog} = \frac{3.91}{V}\left(\frac{\lambda}{550}\right)^{-q} \text{ dB/km}$$

Where V is visibility and q depends on particle size distribution.

**ITU-R rain attenuation:**
$$\alpha_{rain} = k \cdot R^\alpha \text{ dB/km}$$

```python
import numpy as np

class FSOLinkBudget:
    def __init__(self, distance=5000, wavelength=1550e-9):
        self.d = distance
        self.lambda_ = wavelength
    
    def free_space_loss(self):
        """Free space path loss"""
        L_fs = (4 * np.pi * self.d / self.lambda_)**2
        return 10 * np.log10(L_fs)
    
    def kim_fog_model(self, visibility):
        """
        Kim model for fog attenuation
        
        V > 50 km: q = 1.6
        6 < V < 50 km: q = 1.3
        1 < V < 6 km: q = 0.16V + 0.34
        0.5 < V < 1 km: q = V - 0.5
        V < 0.5 km: q = 0
        """
        if visibility > 50:
            q = 1.6
        elif visibility > 6:
            q = 1.3
        elif visibility > 1:
            q = 0.16 * visibility + 0.34
        elif visibility > 0.5:
            q = visibility - 0.5
        else:
            q = 0
        
        alpha = (3.91 / visibility) * (self.lambda_ / 550e-9)**(-q)
        return alpha * self.d / 1000  # Total attenuation in dB
    
    def rain_attenuation(self, rain_rate):
        """
        ITU-R P.1817 rain attenuation
        
        For 1550 nm:
        k = 0.0689
        α = 1.065
        """
        k = 0.0689
        alpha = 1.065
        
        gamma = k * rain_rate**alpha  # dB/km
        return gamma * self.d / 1000
    
    def scintillation_index(self, Cn2, path_length):
        """
        Rytov variance for plane wave
        
        σ²_R = 1.23 * Cn² * k^(7/6) * L^(11/6)
        """
        k = 2 * np.pi / self.lambda_
        sigma_R = 1.23 * Cn2 * k**(7/6) * path_length**(11/6)
        return sigma_R
    
    def pointing_loss(self, beam_divergence, pointing_error):
        """
        Pointing loss due to beam wander
        
        L_point = exp(-2 * θ_e² / θ_b²)
        """
        theta_e = np.radians(pointing_error / 1000)  # mrad to rad
        theta_b = np.radians(beam_divergence / 1000)
        
        L = np.exp(-2 * theta_e**2 / theta_b**2)
        return -10 * np.log10(L)
    
    def total_link_loss(self, visibility=1, rain_rate=25, pointing_error=0.5):
        """Calculate total link loss"""
        L_fs = self.free_space_loss()
        L_fog = self.kim_fog_model(visibility)
        L_rain = self.rain_attenuation(rain_rate)
        L_point = self.pointing_loss(beam_divergence=2, pointing_error=pointing_error)
        
        return {
            'free_space': L_fs,
            'fog': L_fog,
            'rain': L_rain,
            'pointing': L_point,
            'total': L_fs + L_fog + L_rain + L_point
        }
```

## Diversity Techniques

```python
class SpatialDiversity:
    def __init__(self, num_tx, num_rx):
        self.N_tx = num_tx
        self.N_rx = num_rx
    
    def selection_combining(self, snr_array):
        """Select best receiver branch"""
        return np.max(snr_array)
    
    def maximal_ratio_combining(self, snr_array):
        """Combine all branches with optimal weights"""
        return np.sum(snr_array)
    
    def diversity_gain(self, single_branch_availability, num_branches):
        """
        Diversity gain estimation
        
        For N branches with independent fading:
        P_out_N = (P_out_1)^N
        """
        p_out_single = 1 - single_branch_availability
        p_out_diversity = p_out_single**num_branches
        availability = 1 - p_out_diversity
        
        return availability
    
    def required_branches(self, target_availability, single_branch_availability):
        """Calculate number of branches needed"""
        p_out_target = 1 - target_availability
        p_out_single = 1 - single_branch_availability
        
        N = np.ceil(np.log(p_out_target) / np.log(p_out_single))
        return int(N)
```

## Modulation Selection

```python
class FSOModulation:
    def __init__(self, data_rate=10e9):
        self.data_rate = data_rate
    
    def ook_performance(self, received_power, bandwidth):
        """
        On-Off Keying
        
        BER = 0.5 * erfc(sqrt(SNR/2))
        """
        snr = received_power / (1.38e-23 * 300 * bandwidth)
        ber = 0.5 * erfc(np.sqrt(snr / 2))
        return ber
    
    def ppm_performance(self, received_power, bandwidth, M=16):
        """
        Pulse Position Modulation
        
        Better sensitivity than OOK at cost of bandwidth
        """
        # M-PPM requires M times bandwidth
        ppm_bandwidth = M * bandwidth
        snr = received_power / (1.38e-23 * 300 * ppm_bandwidth)
        
        # PPM has log2(M)/M efficiency
        ber = self._ppm_ber(snr, M)
        return ber
    
    def dpim_performance(self, received_power, bandwidth):
        """
        Differential Pulse Interval Modulation
        """
        pass
    
    def select_modulation(self, target_ber, available_power, bandwidth):
        """Select best modulation scheme"""
        modulations = {
            'OOK': self.ook_performance(available_power, bandwidth),
            'PPM-16': self.ppm_performance(available_power, bandwidth, 16),
            'PPM-32': self.ppm_performance(available_power, bandwidth, 32),
        }
        
        for name, ber in modulations.items():
            if ber < target_ber:
                return name, ber
        
        return None, None
```

## Adaptive Optics

```python
class AdaptiveOptics:
    def __init__(self, num_actuators, wavelength=1550e-9):
        self.N = num_actuators
        self.lambda_ = wavelength
    
    def zernike_modes(self, r, theta, mode):
        """Zernike polynomials for wavefront aberration"""
        if mode == 0:  # Piston
            return 1
        elif mode == 1:  # Tip
            return 2 * r * np.cos(theta)
        elif mode == 2:  # Tilt
            return 2 * r * np.sin(theta)
        elif mode == 3:  # Defocus
            return np.sqrt(3) * (2 * r**2 - 1)
        # ... more modes
    
    def wavefront_sensor(self, image):
        """Shack-Hartmann wavefront sensor"""
        # Calculate local slopes from spot displacements
        slopes_x = []
        slopes_y = []
        
        # Process subapertures
        # ... implementation
        
        return slopes_x, slopes_y
    
    def reconstruct_wavefront(self, slopes):
        """Reconstruct wavefront from slopes"""
        # Least squares reconstruction
        # ... implementation
        pass
    
    def deformable_mirror(self, commands):
        """Apply correction to deformable mirror"""
        # Calculate mirror surface from actuator commands
        # ... implementation
        pass
    
    def strehl_ratio(self, rms_error):
        """
        Strehl ratio approximation
        
        S ≈ exp(-(2π * σ / λ)²)
        """
        return np.exp(-(2 * np.pi * rms_error / self.lambda_)**2)
```

## Hybrid RF/FSO

```python
class HybridLink:
    def __init__(self, fso_link, rf_link):
        self.fso = fso_link
        self.rf = rf_link
        self.active_link = 'FSO'
    
    def monitor_fso_quality(self, snr, threshold=10):
        """Monitor FSO link quality"""
        if snr < threshold:
            return 'POOR'
        return 'GOOD'
    
    def switch_decision(self, fso_snr, rf_snr):
        """Decide when to switch links"""
        hysteresis = 3  # dB
        
        if self.active_link == 'FSO':
            if fso_snr < rf_snr - hysteresis:
                self.active_link = 'RF'
                return 'SWITCH_TO_RF'
        else:
            if fso_snr > rf_snr + hysteresis:
                self.active_link = 'FSO'
                return 'SWITCH_TO_FSO'
        
        return 'NO_SWITCH'
    
    def seamless_handover(self):
        """Implement seamless handover protocol"""
        return {
            'make_before_break': True,
            'buffer_size': '100 ms',
            'protocol': 'MPLS fast reroute'
        }
```

## Deliverables

1. **System Design Document**: Complete architecture
2. **Link Budget Analysis**: All conditions
3. **Atmospheric Simulation**: Channel effects
4. **Diversity Gain Analysis**: Multiple branches
5. **Switching Protocol**: Hybrid link
6. **Prototype Design**: Component selection

## Project Structure

```
ECE-3_PhotonLink/
├── README.md
├── link_budget/
│   ├── fso_calculator.py
│   ├── atmospheric.py
│   └── kim_model.py
├── diversity/
│   └── spatial_diversity.py
├── modulation/
│   └── fso_modulation.py
├── adaptive_optics/
│   ├── wavefront.py
│   └── deformable_mirror.py
├── hybrid/
│   └── rf_fso_switch.py
├── simulation/
│   └── channel_sim.py
├── run_analysis.py
└── solution_template.py
```

## Tips

1. Fog is the primary impairment - design for worst case
2. Spatial diversity is essential for 99.9% availability
3. PPM gives better sensitivity than OOK
4. Adaptive optics helps with scintillation
5. RF backup ensures availability during deep fades
