# ECE-1: RadarForge — FMCW Radar System for Drone Detection

## Overview

Design a **Frequency Modulated Continuous Wave (FMCW) radar** system capable of detecting small drones (RCS ≈ 0.01 m²) at ranges up to **500 meters**.

## System Requirements

| Parameter | Requirement |
|---|---|
| Operating frequency | 24 GHz (ISM band) |
| Range resolution | ≤ 1 m |
| Velocity resolution | ≤ 0.5 m/s |
| Angular resolution | ≤ 5° in azimuth |
| Detection probability | ≥ 90% at 500 m (Pfa = 10⁻⁶) |
| Update rate | ≥ 10 Hz |

## Task

### 1. System-Level Design

- Calculate required bandwidth and chirp duration
- Determine transmit power (link budget)
- Select antenna configuration (MIMO virtual array)
- Calculate array geometry for angular resolution

### 2. Signal Processing Chain

- Range-Doppler processing (2D FFT)
- CFAR detection (CA-CFAR or OS-CFAR)
- Angle estimation (MUSIC, ESPRIT, or beamforming)
- Tracking (Kalman filter or particle filter)

### 3. Clutter and Interference Mitigation

- Design clutter rejection filter
- Handle interference from other radars

### 4. Simulation

- Generate simulated radar returns
- Process through signal processing chain
- Display range-Doppler maps and tracks

## Key Equations

### FMCW Basics

**Range resolution:**
$$\Delta R = \frac{c}{2B}$$

where B is the bandwidth.

**Velocity resolution:**
$$\Delta v = \frac{\lambda}{2 T_{chirp} \cdot N_{chirps}}$$

**Maximum unambiguous range:**
$$R_{max} = \frac{f_s \cdot c}{2 \cdot S}$$

where S is the chirp slope (B/T_chirp).

### Radar Equation

**Received power:**
$$P_r = \frac{P_t G_t G_r \lambda^2 \sigma}{(4\pi)^3 R^4}$$

where σ is the RCS.

### Link Budget

**SNR:**
$$SNR = \frac{P_t G_t G_r \lambda^2 \sigma}{(4\pi)^3 R^4 k T_0 B F L}$$

## Deliverables

1. **System Design Document**: All calculations and design choices
2. **Signal Processing Implementation**: Python/MATLAB code
3. **Simulation Results**: Range-Doppler maps, detection performance
4. **Tracking Results**: Drone trajectory tracking

## Getting Started

1. **Run system design calculator:**
   ```bash
   python system_design.py
   ```

2. **Generate simulated data:**
   ```bash
   python generate_radar_data.py
   ```

3. **Run signal processing:**
   ```bash
   python signal_processing.py
   ```

4. **Visualize results:**
   ```bash
   python visualize.py
   ```

## Project Structure

```
ECE-1_RadarForge/
├── README.md
├── system_design.py
├── radar/
│   ├── fmcw.py
│   ├── antenna.py
│   └── propagation.py
├── signal_processing/
│   ├── range_doppler.py
│   ├── cfar.py
│   ├── angle_estimation.py
│   └── tracking.py
├── simulation/
│   ├── target.py
│   ├── clutter.py
│   └── noise.py
├── generate_radar_data.py
├── solution_template.py
└── visualize.py
```

## Tips

1. Start with the radar equation to verify feasibility
2. Use 2D FFT for efficient range-Doppler processing
3. CFAR threshold must adapt to local noise/clutter
4. MIMO virtual array greatly improves angular resolution
5. Track-before-detect can improve sensitivity for weak targets
