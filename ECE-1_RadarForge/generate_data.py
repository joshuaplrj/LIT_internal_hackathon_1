"""
RadarForge - Generate simulation data for FMCW radar drone detection

Generates:
- Drone trajectory scenarios (multiple flight profiles)
- Clutter environment profiles
- Target RCS models
- Atmospheric/propagation conditions
"""

import numpy as np
import json
import os
import csv

SEED = 42
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def generate_drone_trajectories(num_scenarios=20):
    """Generate drone flight trajectory scenarios."""
    os.makedirs(os.path.join(DATA_DIR, "trajectories"), exist_ok=True)
    
    trajectories = []
    
    flight_profiles = [
        {"name": "straight_approach", "desc": "Drone flying straight toward radar"},
        {"name": "crossing", "desc": "Drone crossing at constant range"},
        {"name": "loitering", "desc": "Drone circling at fixed position"},
        {"name": "ascending", "desc": "Drone ascending vertically"},
        {"name": "evasive", "desc": "Drone performing evasive maneuvers"},
    ]
    
    for i in range(num_scenarios):
        profile = flight_profiles[i % len(flight_profiles)]
        dt = 0.01  # 10 ms time step (100 Hz update)
        duration = 30.0  # 30 seconds
        t = np.arange(0, duration, dt)
        N = len(t)
        
        if profile["name"] == "straight_approach":
            r0 = np.random.uniform(400, 500)
            v_radial = -np.random.uniform(5, 15)
            x = r0 + v_radial * t + np.random.randn(N) * 0.05
            y = np.random.uniform(-50, 50) + np.random.randn(N) * 0.1
            z = np.random.uniform(20, 100) + np.random.randn(N) * 0.05
            
        elif profile["name"] == "crossing":
            r0 = np.random.uniform(100, 400)
            v_tangential = np.random.uniform(5, 20)
            angle0 = np.random.uniform(-30, 30)
            x = r0 * np.ones(N) + np.random.randn(N) * 0.1
            y = v_tangential * t + np.random.randn(N) * 0.1
            z = np.random.uniform(30, 80) + np.random.randn(N) * 0.05
            
        elif profile["name"] == "loitering":
            center_range = np.random.uniform(100, 300)
            radius = np.random.uniform(20, 50)
            omega = np.random.uniform(0.1, 0.5)
            x = center_range + radius * np.cos(omega * t) + np.random.randn(N) * 0.05
            y = radius * np.sin(omega * t) + np.random.randn(N) * 0.05
            z = np.random.uniform(40, 80) + np.random.randn(N) * 0.02
            
        elif profile["name"] == "ascending":
            r0 = np.random.uniform(100, 300)
            climb_rate = np.random.uniform(2, 8)
            x = r0 + np.random.randn(N) * 0.1
            y = np.random.randn(N) * 0.1
            z = 10 + climb_rate * t + np.random.randn(N) * 0.05
            
        elif profile["name"] == "evasive":
            r0 = np.random.uniform(150, 350)
            x = r0 + 30 * np.sin(0.3 * t) + np.random.randn(N) * 0.2
            y = 20 * np.cos(0.5 * t) + 5 * np.sin(1.2 * t) + np.random.randn(N) * 0.2
            z = 50 + 15 * np.sin(0.2 * t) + np.random.randn(N) * 0.1
        
        # Compute derived quantities
        r = np.sqrt(x**2 + y**2 + z**2)
        vx = np.gradient(x, dt)
        vy = np.gradient(y, dt)
        vz = np.gradient(z, dt)
        v_radial_actual = (x * vx + y * vy + z * vz) / r
        azimuth = np.degrees(np.arctan2(y, x))
        elevation = np.degrees(np.arcsin(z / r))
        
        # RCS fluctuation (Swerling I model)
        rcs_mean = 0.01  # m^2
        rcs = np.random.exponential(rcs_mean, N)
        
        scenario = {
            "id": f"scenario_{i+1:03d}",
            "profile": profile["name"],
            "description": profile["desc"],
            "duration_s": duration,
            "dt_s": dt,
            "num_samples": N,
            "rcs_mean_m2": rcs_mean,
        }
        trajectories.append(scenario)
        
        # Save trajectory CSV
        filepath = os.path.join(DATA_DIR, "trajectories", f"trajectory_{i+1:03d}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "x_m", "y_m", "z_m", "range_m",
                           "v_radial_mps", "azimuth_deg", "elevation_deg", "rcs_m2"])
            for j in range(0, N, 10):  # Subsample to 10 Hz
                writer.writerow([
                    f"{t[j]:.3f}", f"{x[j]:.3f}", f"{y[j]:.3f}", f"{z[j]:.3f}",
                    f"{r[j]:.3f}", f"{v_radial_actual[j]:.3f}",
                    f"{azimuth[j]:.3f}", f"{elevation[j]:.3f}", f"{rcs[j]:.6f}"
                ])
    
    return trajectories


def generate_clutter_scenarios(num_scenarios=5):
    """Generate ground clutter and interference scenarios."""
    os.makedirs(os.path.join(DATA_DIR, "clutter"), exist_ok=True)
    
    scenarios = []
    clutter_types = [
        {"name": "urban", "sigma0_db": -15, "doppler_spread_hz": 50,
         "desc": "Urban environment with buildings, vehicles"},
        {"name": "rural", "sigma0_db": -25, "doppler_spread_hz": 10,
         "desc": "Open farmland with vegetation clutter"},
        {"name": "suburban", "sigma0_db": -20, "doppler_spread_hz": 30,
         "desc": "Suburban area with trees and houses"},
        {"name": "industrial", "sigma0_db": -10, "doppler_spread_hz": 80,
         "desc": "Industrial area with rotating machinery, cranes"},
        {"name": "coastal", "sigma0_db": -18, "doppler_spread_hz": 40,
         "desc": "Coastal area with sea clutter"},
    ]
    
    for i, ctype in enumerate(clutter_types):
        # Generate clutter map: range bins x angle bins
        range_bins = np.arange(0, 500, 1)  # 1 m resolution
        angle_bins = np.arange(-60, 61, 1)  # 1 deg resolution
        
        # Clutter reflectivity map (dB)
        base_sigma0 = ctype["sigma0_db"]
        clutter_map = base_sigma0 + np.random.randn(len(range_bins), len(angle_bins)) * 5
        
        # Add discrete clutter sources (buildings, towers, etc.)
        num_discretes = np.random.randint(5, 20)
        discrete_clutter = []
        for _ in range(num_discretes):
            r_idx = np.random.randint(10, len(range_bins))
            a_idx = np.random.randint(0, len(angle_bins))
            rcs_db = np.random.uniform(10, 40)
            clutter_map[r_idx, a_idx] += rcs_db
            discrete_clutter.append({
                "range_m": float(range_bins[r_idx]),
                "azimuth_deg": float(angle_bins[a_idx]),
                "rcs_db": float(rcs_db)
            })
        
        scenario = {
            "id": f"clutter_{i+1:03d}",
            "type": ctype["name"],
            "description": ctype["desc"],
            "sigma0_db": ctype["sigma0_db"],
            "doppler_spread_hz": ctype["doppler_spread_hz"],
            "num_discrete_sources": num_discretes,
            "discrete_sources": discrete_clutter,
            "range_bins": len(range_bins),
            "angle_bins": len(angle_bins),
        }
        scenarios.append(scenario)
        
        # Save clutter map as CSV
        filepath = os.path.join(DATA_DIR, "clutter", f"clutter_{ctype['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["range_m"] + [f"az_{a}deg" for a in angle_bins])
            for ri, r in enumerate(range_bins):
                writer.writerow([f"{r:.0f}"] + [f"{clutter_map[ri, ai]:.1f}"
                               for ai in range(len(angle_bins))])
    
    return scenarios


def generate_rcs_models():
    """Generate target RCS models for different drone types."""
    os.makedirs(os.path.join(DATA_DIR, "targets"), exist_ok=True)
    
    drones = [
        {"name": "small_quadcopter", "mass_kg": 0.5, "wingspan_m": 0.3,
         "rcs_mean_m2": 0.005, "rcs_std_m2": 0.003,
         "swerling_type": 1, "micro_doppler_hz": [80, 160, 240]},
        {"name": "medium_quadcopter", "mass_kg": 2.0, "wingspan_m": 0.5,
         "rcs_mean_m2": 0.01, "rcs_std_m2": 0.008,
         "swerling_type": 1, "micro_doppler_hz": [60, 120, 180]},
        {"name": "large_hexacopter", "mass_kg": 10.0, "wingspan_m": 1.0,
         "rcs_mean_m2": 0.05, "rcs_std_m2": 0.03,
         "swerling_type": 1, "micro_doppler_hz": [40, 80, 120]},
        {"name": "fixed_wing_small", "mass_kg": 3.0, "wingspan_m": 1.5,
         "rcs_mean_m2": 0.02, "rcs_std_m2": 0.01,
         "swerling_type": 3, "micro_doppler_hz": [20]},
        {"name": "racing_drone", "mass_kg": 0.8, "wingspan_m": 0.25,
         "rcs_mean_m2": 0.003, "rcs_std_m2": 0.002,
         "swerling_type": 1, "micro_doppler_hz": [150, 300, 450]},
    ]
    
    # Generate RCS vs aspect angle for each drone
    aspects = np.arange(0, 360, 1)  # 1 deg resolution
    
    for drone in drones:
        rcs_pattern = drone["rcs_mean_m2"] * (
            1 + 0.5 * np.cos(np.radians(2 * aspects)) +
            0.3 * np.cos(np.radians(4 * aspects)) +
            np.random.randn(len(aspects)) * drone["rcs_std_m2"]
        )
        rcs_pattern = np.maximum(rcs_pattern, 1e-4)  # Floor at -40 dBsm
        
        filepath = os.path.join(DATA_DIR, "targets", f"rcs_{drone['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["aspect_deg", "rcs_m2", "rcs_dbsm"])
            for j, asp in enumerate(aspects):
                writer.writerow([f"{asp:.0f}", f"{rcs_pattern[j]:.6f}",
                               f"{10*np.log10(rcs_pattern[j]):.2f}"])
    
    return drones


def generate_propagation_conditions():
    """Generate atmospheric/propagation condition data."""
    os.makedirs(os.path.join(DATA_DIR, "propagation"), exist_ok=True)
    
    conditions = []
    weather_types = [
        {"name": "clear", "rain_rate_mmhr": 0, "atm_loss_db_km": 0.02,
         "visibility_km": 20, "turbulence_cn2": 1e-15},
        {"name": "light_rain", "rain_rate_mmhr": 5, "atm_loss_db_km": 0.05,
         "visibility_km": 5, "turbulence_cn2": 5e-15},
        {"name": "heavy_rain", "rain_rate_mmhr": 25, "atm_loss_db_km": 0.15,
         "visibility_km": 2, "turbulence_cn2": 1e-14},
        {"name": "fog", "rain_rate_mmhr": 0, "atm_loss_db_km": 0.5,
         "visibility_km": 0.2, "turbulence_cn2": 1e-16},
        {"name": "snow", "rain_rate_mmhr": 0, "atm_loss_db_km": 0.3,
         "visibility_km": 1, "turbulence_cn2": 5e-16},
    ]
    
    # Time-varying atmospheric data (1 hour at 1-second intervals)
    t = np.arange(0, 3600, 1)
    
    for wtype in weather_types:
        # Generate slow-varying atmospheric loss
        atm_base = wtype["atm_loss_db_km"]
        atm_variation = atm_base * 0.1 * np.sin(2 * np.pi * t / 600)  # 10 min period
        atm_loss = atm_base + atm_variation + np.random.randn(len(t)) * atm_base * 0.02
        
        filepath = os.path.join(DATA_DIR, "propagation", f"atm_{wtype['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "atm_loss_db_km", "visibility_km",
                           "rain_rate_mmhr", "cn2"])
            for j in range(0, len(t), 10):  # 0.1 Hz sampling
                vis = wtype["visibility_km"] + np.random.randn() * 0.1 * wtype["visibility_km"]
                rain = max(0, wtype["rain_rate_mmhr"] + np.random.randn() * 0.5)
                cn2 = wtype["turbulence_cn2"] * (1 + 0.3 * np.random.randn())
                writer.writerow([f"{t[j]:.0f}", f"{atm_loss[j]:.4f}",
                               f"{vis:.2f}", f"{rain:.1f}", f"{cn2:.2e}"])
        
        conditions.append(wtype)
    
    return conditions


def generate_interference_scenarios():
    """Generate radar interference scenarios."""
    os.makedirs(os.path.join(DATA_DIR, "interference"), exist_ok=True)
    
    scenarios = [
        {"name": "no_interference", "num_interferers": 0, "interferers": []},
        {"name": "single_radar", "num_interferers": 1, "interferers": [
            {"freq_ghz": 24.05, "bandwidth_mhz": 100, "power_dbm": 10,
             "azimuth_deg": 45, "range_m": 200, "type": "automotive_radar"}
        ]},
        {"name": "dense_automotive", "num_interferers": 5, "interferers": [
            {"freq_ghz": 24.0 + i*0.05, "bandwidth_mhz": 150,
             "power_dbm": 10 + np.random.randint(-5, 5),
             "azimuth_deg": float(np.random.randint(-90, 90)),
             "range_m": float(np.random.randint(50, 500)),
             "type": "automotive_radar"}
            for i in range(5)
        ]},
        {"name": "wifi_interference", "num_interferers": 2, "interferers": [
            {"freq_ghz": 24.0, "bandwidth_mhz": 20, "power_dbm": 20,
             "azimuth_deg": -30, "range_m": 100, "type": "wifi_24ghz"},
            {"freq_ghz": 24.125, "bandwidth_mhz": 20, "power_dbm": 15,
             "azimuth_deg": 60, "range_m": 300, "type": "wifi_24ghz"}
        ]},
    ]
    
    with open(os.path.join(DATA_DIR, "interference", "scenarios.json"), 'w') as f:
        json.dump(scenarios, f, indent=2)
    
    return scenarios


def main():
    print("Generating RadarForge simulation data...")
    print("=" * 50)
    
    # Generate all data
    print("1. Generating drone trajectories (20 scenarios)...")
    trajectories = generate_drone_trajectories(20)
    
    print("2. Generating clutter scenarios (5 environments)...")
    clutter = generate_clutter_scenarios(5)
    
    print("3. Generating target RCS models (5 drone types)...")
    targets = generate_rcs_models()
    
    print("4. Generating propagation conditions (5 weather types)...")
    propagation = generate_propagation_conditions()
    
    print("5. Generating interference scenarios...")
    interference = generate_interference_scenarios()
    
    # Save metadata
    metadata = {
        "problem": "ECE-1 RadarForge",
        "description": "FMCW Radar System for Drone Detection",
        "radar_params": {
            "center_freq_ghz": 24.0,
            "bandwidth_mhz": 150,
            "chirp_duration_ms": 1.0,
            "chirps_per_frame": 128,
            "sampling_rate_mhz": 2.0,
            "tx_antennas": 2,
            "rx_antennas": 8,
            "transmit_power_mw": 10,
        },
        "target_params": {
            "rcs_m2": 0.01,
            "max_range_m": 500,
            "max_velocity_mps": 30,
        },
        "data_contents": {
            "trajectories": {
                "count": len(trajectories),
                "format": "CSV (time, x, y, z, range, v_radial, azimuth, elevation, rcs)",
                "scenarios": trajectories,
            },
            "clutter": {
                "count": len(clutter),
                "format": "CSV (range x angle clutter map)",
                "scenarios": clutter,
            },
            "targets": {
                "count": len(targets),
                "format": "CSV (aspect angle vs RCS)",
                "models": [{k: v for k, v in t.items()} for t in targets],
            },
            "propagation": {
                "count": len(propagation),
                "format": "CSV (time-varying atmospheric conditions)",
                "conditions": propagation,
            },
            "interference": {
                "count": len(interference),
                "format": "JSON (interferer parameters)",
            },
        },
        "seed": SEED,
    }
    
    with open(os.path.join(DATA_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nData generated in: {DATA_DIR}")
    print(f"  - trajectories/: {len(trajectories)} drone flight scenarios")
    print(f"  - clutter/: {len(clutter)} environment types")
    print(f"  - targets/: {len(targets)} drone RCS models")
    print(f"  - propagation/: {len(propagation)} weather conditions")
    print(f"  - interference/: {len(interference)} interference scenarios")
    print("\nDone!")


if __name__ == "__main__":
    main()
