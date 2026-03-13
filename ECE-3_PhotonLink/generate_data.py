"""
PhotonLink - Generate simulation data for FSO communication system

Generates:
- Atmospheric condition statistics (visibility, turbulence Cn2)
- Weather/climate profiles for availability analysis
- Component catalog (lasers, detectors, optics)
- Turbulence time series data
"""

import numpy as np
import json
import os
import csv

SEED = 42
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def generate_atmospheric_statistics():
    """Generate atmospheric condition statistics for different climates."""
    os.makedirs(os.path.join(DATA_DIR, "atmosphere"), exist_ok=True)
    
    # Visibility CDF data for different cities (hours per year)
    cities = {
        "london": {"name": "London, UK", "climate": "maritime_temperate",
                    "visibility_percentiles": {
                        "0.1": 0.05, "1": 0.2, "5": 0.8, "10": 1.5,
                        "25": 5.0, "50": 10.0, "75": 18.0, "90": 25.0,
                        "99": 35.0, "99.9": 50.0}},
        "mumbai": {"name": "Mumbai, India", "climate": "tropical_monsoon",
                   "visibility_percentiles": {
                       "0.1": 0.1, "1": 0.5, "5": 1.5, "10": 3.0,
                       "25": 8.0, "50": 15.0, "75": 22.0, "90": 28.0,
                       "99": 35.0, "99.9": 45.0}},
        "dubai": {"name": "Dubai, UAE", "climate": "hot_desert",
                  "visibility_percentiles": {
                      "0.1": 0.2, "1": 1.0, "5": 3.0, "10": 5.0,
                      "25": 10.0, "50": 20.0, "75": 30.0, "90": 40.0,
                      "99": 50.0, "99.9": 55.0}},
        "singapore": {"name": "Singapore", "climate": "tropical_rainforest",
                      "visibility_percentiles": {
                          "0.1": 0.3, "1": 1.0, "5": 2.5, "10": 5.0,
                          "25": 8.0, "50": 12.0, "75": 18.0, "90": 22.0,
                          "99": 30.0, "99.9": 40.0}},
        "phoenix": {"name": "Phoenix, USA", "climate": "hot_desert_low_humidity",
                    "visibility_percentiles": {
                        "0.1": 2.0, "1": 5.0, "5": 10.0, "10": 15.0,
                        "25": 25.0, "50": 40.0, "75": 60.0, "90": 80.0,
                        "99": 100.0, "99.9": 120.0}},
    }
    
    with open(os.path.join(DATA_DIR, "atmosphere", "visibility_statistics.json"), 'w') as f:
        json.dump(cities, f, indent=2)
    
    # Cn2 (refractive index structure constant) profiles
    # Time of day variation (24 hours)
    hours = np.arange(0, 24, 0.5)
    
    cn2_profiles = {}
    for condition in ["weak", "moderate", "strong"]:
        if condition == "weak":
            base = 5e-17
            amplitude = 3e-17
        elif condition == "moderate":
            base = 5e-16
            amplitude = 4e-16
        else:
            base = 5e-15
            amplitude = 4e-15
        
        # Cn2 peaks during afternoon (solar heating)
        cn2 = base + amplitude * np.exp(-((hours - 14) / 3)**2)
        cn2 += np.random.randn(len(hours)) * base * 0.1
        cn2 = np.maximum(cn2, 1e-18)
        
        cn2_profiles[condition] = {
            "description": f"{condition.title()} turbulence conditions",
            "cn2_values": [f"{v:.2e}" for v in cn2],
        }
    
    cn2_data = {
        "hours": [f"{h:.1f}" for h in hours],
        "profiles": cn2_profiles,
        "notes": "Cn2 in m^(-2/3). Values represent path-averaged Cn2 at ground level.",
    }
    
    with open(os.path.join(DATA_DIR, "atmosphere", "cn2_profiles.json"), 'w') as f:
        json.dump(cn2_data, f, indent=2)
    
    return cities, cn2_profiles


def generate_weather_timeseries():
    """Generate 1 year of hourly weather data for availability analysis."""
    os.makedirs(os.path.join(DATA_DIR, "weather"), exist_ok=True)
    
    hours = 8760  # 1 year
    
    for city in ["london", "mumbai", "phoenix"]:
        t = np.arange(hours)
        
        if city == "london":
            # Maritime: frequent fog, moderate rain
            visibility = np.random.lognormal(2.5, 0.8, hours)
            visibility = np.clip(visibility, 0.05, 50)
            # Add fog events (winter mornings)
            for day in range(365):
                hour_start = day * 24 + 4  # 4 AM
                if np.random.random() < 0.15:  # 15% chance of fog
                    duration = np.random.randint(2, 8)
                    fog_vis = np.random.uniform(0.05, 0.5)
                    end = min(hour_start + duration, hours)
                    visibility[hour_start:end] = fog_vis
            
            rain_rate = np.zeros(hours)
            for day in range(365):
                if np.random.random() < 0.35:  # 35% of days have rain
                    start = day * 24 + np.random.randint(0, 20)
                    duration = np.random.randint(1, 6)
                    rate = np.random.exponential(5)
                    end = min(start + duration, hours)
                    rain_rate[start:end] = rate
        
        elif city == "mumbai":
            # Tropical monsoon: heavy rain June-Sept
            visibility = np.random.lognormal(2.5, 0.6, hours)
            visibility = np.clip(visibility, 0.1, 45)
            
            rain_rate = np.zeros(hours)
            for day in range(365):
                month = day // 30
                if 5 <= month <= 8:  # Monsoon
                    if np.random.random() < 0.6:
                        start = day * 24 + np.random.randint(0, 18)
                        duration = np.random.randint(2, 10)
                        rate = np.random.exponential(20)
                        end = min(start + duration, hours)
                        rain_rate[start:end] = rate
                        visibility[start:end] = np.clip(visibility[start:end] * 0.3, 0.1, 5)
                else:
                    if np.random.random() < 0.05:
                        start = day * 24 + np.random.randint(0, 20)
                        duration = np.random.randint(1, 3)
                        rate = np.random.exponential(5)
                        end = min(start + duration, hours)
                        rain_rate[start:end] = rate
        
        else:  # phoenix
            # Desert: very clear most of the time
            visibility = np.random.lognormal(3.5, 0.4, hours)
            visibility = np.clip(visibility, 1, 120)
            
            rain_rate = np.zeros(hours)
            for day in range(365):
                if np.random.random() < 0.05:
                    start = day * 24 + np.random.randint(12, 20)
                    duration = np.random.randint(1, 3)
                    rate = np.random.exponential(10)
                    end = min(start + duration, hours)
                    rain_rate[start:end] = rate
                    visibility[start:end] *= 0.5
        
        # Temperature (affects Cn2)
        day_of_year = np.arange(hours) / 24
        hour_of_day = np.arange(hours) % 24
        
        if city == "london":
            temp_base = 10 + 8 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        elif city == "mumbai":
            temp_base = 28 + 5 * np.sin(2 * np.pi * (day_of_year - 120) / 365)
        else:
            temp_base = 25 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        temp = temp_base + 5 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        temp += np.random.randn(hours) * 1.5
        
        filepath = os.path.join(DATA_DIR, "weather", f"{city}_hourly.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["hour", "visibility_km", "rain_rate_mmhr",
                           "temperature_c", "wind_speed_mps"])
            for j in range(hours):
                wind = max(0, np.random.lognormal(1.5, 0.6))
                writer.writerow([j, f"{visibility[j]:.2f}", f"{rain_rate[j]:.1f}",
                               f"{temp[j]:.1f}", f"{wind:.1f}"])
    
    return ["london", "mumbai", "phoenix"]


def generate_component_catalog():
    """Generate optical component catalog."""
    os.makedirs(os.path.join(DATA_DIR, "components"), exist_ok=True)
    
    catalog = {
        "laser_sources": [
            {"model": "LS-1550-100", "wavelength_nm": 1550, "power_mw": 100,
             "type": "DFB laser", "linewidth_mhz": 1, "power_consumption_w": 0.5,
             "price_usd": 500, "eye_safe": True},
            {"model": "LS-1550-500", "wavelength_nm": 1550, "power_mw": 500,
             "type": "EDFA amplified", "linewidth_mhz": 0.1, "power_consumption_w": 3,
             "price_usd": 2500, "eye_safe": True},
            {"model": "LS-1550-2W", "wavelength_nm": 1550, "power_mw": 2000,
             "type": "High power EDFA", "linewidth_mhz": 0.1, "power_consumption_w": 10,
             "price_usd": 8000, "eye_safe": False},
            {"model": "LS-850-200", "wavelength_nm": 850, "power_mw": 200,
             "type": "VCSEL array", "linewidth_mhz": 100, "power_consumption_w": 1,
             "price_usd": 300, "eye_safe": False},
        ],
        "detectors": [
            {"model": "DET-InGaAs-APD", "type": "InGaAs APD",
             "wavelength_range_nm": [900, 1700], "responsivity_a_w": 0.9,
             "gain": 10, "bandwidth_ghz": 2.5, "nep_pw_sqrt_hz": 0.5,
             "dark_current_na": 10, "price_usd": 1500},
            {"model": "DET-InGaAs-PIN", "type": "InGaAs PIN",
             "wavelength_range_nm": [900, 1700], "responsivity_a_w": 1.0,
             "gain": 1, "bandwidth_ghz": 10, "nep_pw_sqrt_hz": 5,
             "dark_current_na": 1, "price_usd": 800},
            {"model": "DET-Si-APD", "type": "Silicon APD",
             "wavelength_range_nm": [400, 1000], "responsivity_a_w": 0.5,
             "gain": 100, "bandwidth_ghz": 1, "nep_pw_sqrt_hz": 0.1,
             "dark_current_na": 5, "price_usd": 500},
        ],
        "telescopes": [
            {"model": "TEL-100", "aperture_mm": 100, "focal_length_mm": 500,
             "fov_mrad": 2, "weight_kg": 2, "price_usd": 3000},
            {"model": "TEL-200", "aperture_mm": 200, "focal_length_mm": 1000,
             "fov_mrad": 1, "weight_kg": 8, "price_usd": 8000},
            {"model": "TEL-300", "aperture_mm": 300, "focal_length_mm": 1500,
             "fov_mrad": 0.5, "weight_kg": 20, "price_usd": 15000},
        ],
        "tracking_systems": [
            {"model": "TRK-COARSE", "type": "CCD camera + gimbal",
             "accuracy_mrad": 0.5, "bandwidth_hz": 10, "range_deg": 5,
             "price_usd": 5000},
            {"model": "TRK-FINE", "type": "QPD + FSM",
             "accuracy_mrad": 0.01, "bandwidth_hz": 1000, "range_deg": 0.5,
             "price_usd": 15000},
            {"model": "TRK-AO", "type": "Adaptive optics (DM + WFS)",
             "accuracy_mrad": 0.001, "bandwidth_hz": 500, "range_deg": 0.1,
             "num_actuators": 97, "price_usd": 50000},
        ],
        "modulators": [
            {"model": "MOD-MZM-10G", "type": "Mach-Zehnder",
             "bandwidth_ghz": 10, "insertion_loss_db": 4, "extinction_ratio_db": 25,
             "vpi_v": 3.5, "price_usd": 2000},
            {"model": "MOD-MZM-25G", "type": "Mach-Zehnder",
             "bandwidth_ghz": 25, "insertion_loss_db": 5, "extinction_ratio_db": 20,
             "vpi_v": 4.0, "price_usd": 4000},
            {"model": "MOD-EAM-40G", "type": "Electro-absorption",
             "bandwidth_ghz": 40, "insertion_loss_db": 6, "extinction_ratio_db": 12,
             "vpi_v": 2.0, "price_usd": 3500},
        ],
    }
    
    with open(os.path.join(DATA_DIR, "components", "catalog.json"), 'w') as f:
        json.dump(catalog, f, indent=2)
    
    return catalog


def generate_turbulence_timeseries():
    """Generate turbulence-induced intensity fluctuation time series."""
    os.makedirs(os.path.join(DATA_DIR, "turbulence"), exist_ok=True)
    
    # Generate scintillation time series for different Cn2 values
    fs = 1000  # 1 kHz sampling
    duration = 10  # 10 seconds
    N = fs * duration
    t = np.arange(N) / fs
    
    scenarios = [
        {"cn2": 1e-16, "label": "weak", "rytov_var": 0.1},
        {"cn2": 1e-15, "label": "moderate", "rytov_var": 1.0},
        {"cn2": 1e-14, "label": "strong", "rytov_var": 10.0},
    ]
    
    wavelength = 1550e-9
    distance = 5000
    k = 2 * np.pi / wavelength
    
    for sc in scenarios:
        # Log-normal intensity fluctuations (weak turbulence)
        # Rytov variance: sigma_R^2 = 1.23 * Cn2 * k^(7/6) * L^(11/6)
        sigma_R2 = 1.23 * sc["cn2"] * k**(7/6) * distance**(11/6)
        
        # Generate correlated Gaussian process
        # Greenwood frequency determines temporal bandwidth
        v_wind = 5  # m/s crosswind
        f_G = 0.102 * (v_wind / (wavelength * distance))**0.5  # Greenwood freq
        
        # Low-pass filtered white noise
        noise = np.random.randn(N)
        # Simple 1st order low-pass at Greenwood frequency
        alpha = 2 * np.pi * f_G / fs
        filtered = np.zeros(N)
        filtered[0] = noise[0]
        for i in range(1, N):
            filtered[i] = (1 - alpha) * filtered[i-1] + alpha * noise[i]
        
        # Scale to desired log-amplitude variance
        sigma_chi = np.sqrt(sigma_R2 / 4)  # Log-amplitude variance
        log_amplitude = filtered * sigma_chi / np.std(filtered)
        
        # Intensity = exp(2 * chi) for log-normal
        intensity = np.exp(2 * log_amplitude)
        intensity = intensity / np.mean(intensity)  # Normalize mean to 1
        
        # Also add beam wander
        wander_x = np.cumsum(np.random.randn(N) * 0.001) * np.sqrt(sc["cn2"]) * 1e6
        wander_y = np.cumsum(np.random.randn(N) * 0.001) * np.sqrt(sc["cn2"]) * 1e6
        
        filepath = os.path.join(DATA_DIR, "turbulence", f"scintillation_{sc['label']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "normalized_intensity", "log_intensity_db",
                           "beam_wander_x_urad", "beam_wander_y_urad"])
            for j in range(0, N, 10):  # 100 Hz output
                writer.writerow([f"{t[j]:.4f}", f"{intensity[j]:.6f}",
                               f"{10*np.log10(intensity[j]):.3f}",
                               f"{wander_x[j]:.3f}", f"{wander_y[j]:.3f}"])
        
        sc["sigma_R2"] = float(sigma_R2)
        sc["greenwood_freq_hz"] = float(f_G)
        sc["scintillation_index"] = float(np.var(intensity) / np.mean(intensity)**2)
    
    with open(os.path.join(DATA_DIR, "turbulence", "scenarios.json"), 'w') as f:
        json.dump(scenarios, f, indent=2, default=str)
    
    return scenarios


def main():
    print("Generating PhotonLink simulation data...")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("1. Generating atmospheric statistics...")
    cities, cn2 = generate_atmospheric_statistics()
    
    print("2. Generating 1-year weather time series (3 cities)...")
    weather_cities = generate_weather_timeseries()
    
    print("3. Generating component catalog...")
    catalog = generate_component_catalog()
    
    print("4. Generating turbulence time series (3 conditions)...")
    turb = generate_turbulence_timeseries()
    
    metadata = {
        "problem": "ECE-3 PhotonLink",
        "description": "Free-Space Optical Communication System",
        "system_params": {
            "distance_m": 5000,
            "wavelength_nm": 1550,
            "data_rate_gbps": 10,
            "target_availability": 0.999,
            "target_ber": 1e-9,
        },
        "data_contents": {
            "atmosphere": f"Visibility statistics for {len(cities)} cities + Cn2 profiles",
            "weather": f"1-year hourly data for {len(weather_cities)} cities",
            "components": f"Optical component catalog ({sum(len(v) for v in catalog.values())} items)",
            "turbulence": f"{len(turb)} scintillation time series",
        },
        "seed": SEED,
    }
    
    with open(os.path.join(DATA_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nData generated in: {DATA_DIR}")
    print(f"  - atmosphere/: visibility stats + Cn2 profiles")
    print(f"  - weather/: 1-year hourly data for 3 cities")
    print(f"  - components/: optical component catalog")
    print(f"  - turbulence/: scintillation time series")
    print("\nDone!")


if __name__ == "__main__":
    main()
