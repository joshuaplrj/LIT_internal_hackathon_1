"""
MIMO-Sat - Generate simulation data for LEO satellite link design

Generates:
- ITU-R rain model data for multiple climate zones
- Orbit and pass geometry data
- Ground station configurations
- Atmospheric absorption profiles
- Beam hopping schedule parameters
"""

import numpy as np
import json
import os
import csv

SEED = 42
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def generate_rain_model_data():
    """Generate ITU-R P.837/P.838 rain attenuation data."""
    os.makedirs(os.path.join(DATA_DIR, "rain_model"), exist_ok=True)
    
    # Rain rate exceedance data for different climate zones (ITU-R P.837)
    climate_zones = {
        "A": {"name": "Polar tundra", "R001": 8, "R01": 2, "R1": 0.5},
        "B": {"name": "Polar taiga", "R001": 12, "R01": 4, "R1": 1},
        "C": {"name": "Temperate maritime", "R001": 15, "R01": 5, "R1": 1.5},
        "D": {"name": "Temperate continental", "R001": 19, "R01": 8, "R1": 2.1},
        "E": {"name": "Subtropical dry", "R001": 22, "R01": 6, "R1": 1.7},
        "H": {"name": "Subtropical humid", "R001": 32, "R01": 10, "R1": 3.2},
        "K": {"name": "Tropical moderate", "R001": 42, "R01": 12, "R1": 4.5},
        "N": {"name": "Tropical wet", "R001": 65, "R01": 22, "R1": 7},
        "P": {"name": "Tropical heavy", "R001": 145, "R01": 35, "R1": 12},
        "Q": {"name": "Tropical extreme", "R001": 115, "R01": 30, "R1": 10.5},
    }
    
    # Exceedance percentages
    percentages = [0.001, 0.002, 0.003, 0.005, 0.01, 0.02, 0.03, 0.05,
                   0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0]
    
    rain_data = {}
    for zone_id, zone in climate_zones.items():
        # Interpolate/extrapolate rain rates for all percentages
        # Using log-normal model
        R001 = zone["R001"]
        R01 = zone["R01"]
        R1 = zone["R1"]
        
        rates = []
        for p in percentages:
            if p <= 0.001:
                rate = R001
            elif p <= 0.01:
                rate = R001 * (0.01 / p) ** (np.log(R001/R01) / np.log(10))
            elif p <= 0.1:
                rate = R01 * (0.1 / p) ** (np.log(R01/R1) / np.log(10))
            else:
                rate = R1 * (1.0 / p) ** 0.5
            rates.append(max(0, rate))
        
        rain_data[zone_id] = {
            "zone_name": zone["name"],
            "rain_rates": {f"p{p}": round(r, 2) for p, r in zip(percentages, rates)},
        }
    
    with open(os.path.join(DATA_DIR, "rain_model", "itu_r_rain_zones.json"), 'w') as f:
        json.dump(rain_data, f, indent=2)
    
    # Specific attenuation coefficients (ITU-R P.838)
    # γ_R = k * R^α dB/km
    freq_ghz = [1, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]
    
    coeffs_h = {  # Horizontal polarization
        "k": [0.0000387, 0.000154, 0.000650, 0.00175, 0.00454, 0.0101,
              0.0188, 0.0367, 0.0751, 0.124, 0.187, 0.350, 0.536, 0.707, 1.06, 1.32],
        "alpha": [0.912, 0.963, 1.121, 1.308, 1.327, 1.276,
                  1.217, 1.154, 1.099, 1.061, 1.021, 0.939, 0.873, 0.826, 0.753, 0.723],
    }
    
    coeffs_v = {  # Vertical polarization
        "k": [0.0000352, 0.000138, 0.000591, 0.00155, 0.00395, 0.00887,
              0.0168, 0.0335, 0.0691, 0.113, 0.167, 0.310, 0.479, 0.642, 0.975, 1.24],
        "alpha": [0.880, 0.923, 1.075, 1.265, 1.310, 1.264,
                  1.200, 1.128, 1.065, 1.030, 0.997, 0.929, 0.868, 0.824, 0.752, 0.720],
    }
    
    attenuation_data = {
        "frequencies_ghz": freq_ghz,
        "horizontal": coeffs_h,
        "vertical": coeffs_v,
        "formula": "gamma_R = k * R^alpha [dB/km], R in mm/hr",
    }
    
    with open(os.path.join(DATA_DIR, "rain_model", "specific_attenuation_coeffs.json"), 'w') as f:
        json.dump(attenuation_data, f, indent=2)
    
    return rain_data


def generate_orbit_data():
    """Generate orbital parameters and pass geometry."""
    os.makedirs(os.path.join(DATA_DIR, "orbit"), exist_ok=True)
    
    # Constellation parameters (Starlink-like)
    constellation = {
        "name": "LEO Broadband Constellation",
        "altitude_km": 550,
        "inclination_deg": 53.0,
        "num_orbital_planes": 72,
        "sats_per_plane": 22,
        "total_satellites": 1584,
        "orbital_period_min": 95.7,
        "orbital_velocity_kms": 7.59,
        "min_elevation_deg": 25,
    }
    
    # Generate satellite pass data for a ground station
    passes = []
    for i in range(50):
        max_elev = np.random.uniform(25, 90)
        duration = 120 + (max_elev - 25) * 6  # seconds, longer for higher passes
        
        t = np.linspace(0, duration, int(duration))
        
        # Elevation profile (sinusoidal approximation)
        elevation = max_elev * np.sin(np.pi * t / duration)
        elevation = np.maximum(elevation, 0)
        
        # Slant range from elevation
        Re = 6371  # km
        h = 550  # km
        slant_range = np.zeros_like(elevation)
        for j, el in enumerate(elevation):
            if el > 0:
                theta = np.radians(el)
                slant_range[j] = -Re * np.sin(theta) + np.sqrt(
                    (Re * np.sin(theta))**2 + 2 * Re * h + h**2)
            else:
                slant_range[j] = np.sqrt(Re**2 + (Re + h)**2)
        
        # Azimuth (linear sweep)
        az_start = np.random.uniform(0, 360)
        az_end = az_start + np.random.uniform(60, 180)
        azimuth = np.linspace(az_start, az_end, len(t)) % 360
        
        # Doppler shift at 12 GHz
        v_sat = 7590  # m/s
        c = 3e8
        f = 12e9
        doppler = v_sat * f / c * np.cos(np.radians(elevation)) * np.sign(t - duration/2)
        
        pass_info = {
            "pass_id": i + 1,
            "max_elevation_deg": round(float(max_elev), 1),
            "duration_s": round(float(duration), 1),
            "start_azimuth_deg": round(float(az_start), 1),
        }
        passes.append(pass_info)
        
        filepath = os.path.join(DATA_DIR, "orbit", f"pass_{i+1:03d}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "elevation_deg", "azimuth_deg",
                           "slant_range_km", "doppler_hz"])
            for j in range(0, len(t), 5):  # 0.2 Hz sampling
                writer.writerow([f"{t[j]:.1f}", f"{elevation[j]:.2f}",
                               f"{azimuth[j]:.2f}", f"{slant_range[j]:.1f}",
                               f"{doppler[j]:.0f}"])
    
    constellation["passes"] = passes
    
    with open(os.path.join(DATA_DIR, "orbit", "constellation_params.json"), 'w') as f:
        json.dump(constellation, f, indent=2)
    
    return constellation


def generate_ground_stations():
    """Generate ground station configurations."""
    os.makedirs(os.path.join(DATA_DIR, "ground_stations"), exist_ok=True)
    
    stations = [
        {"id": "GS-01", "name": "Rural India", "lat": 20.0, "lon": 78.0,
         "climate_zone": "N", "antenna_dia_m": 1.2, "elevation_limit_deg": 25},
        {"id": "GS-02", "name": "Rural Brazil", "lat": -15.0, "lon": -47.0,
         "climate_zone": "P", "antenna_dia_m": 1.2, "elevation_limit_deg": 25},
        {"id": "GS-03", "name": "Rural Africa", "lat": -2.0, "lon": 30.0,
         "climate_zone": "N", "antenna_dia_m": 0.75, "elevation_limit_deg": 30},
        {"id": "GS-04", "name": "Northern Europe", "lat": 60.0, "lon": 25.0,
         "climate_zone": "C", "antenna_dia_m": 1.2, "elevation_limit_deg": 25},
        {"id": "GS-05", "name": "Arctic Canada", "lat": 65.0, "lon": -100.0,
         "climate_zone": "A", "antenna_dia_m": 1.5, "elevation_limit_deg": 20},
        {"id": "GS-06", "name": "Southeast Asia", "lat": 5.0, "lon": 103.0,
         "climate_zone": "P", "antenna_dia_m": 0.75, "elevation_limit_deg": 30},
        {"id": "GS-07", "name": "Outback Australia", "lat": -25.0, "lon": 135.0,
         "climate_zone": "E", "antenna_dia_m": 1.2, "elevation_limit_deg": 25},
        {"id": "GS-08", "name": "Sahel Region", "lat": 14.0, "lon": 0.0,
         "climate_zone": "K", "antenna_dia_m": 0.75, "elevation_limit_deg": 30},
    ]
    
    # Add computed parameters
    c = 3e8
    for gs in stations:
        for freq_ghz, label in [(12, "downlink"), (14, "uplink")]:
            freq = freq_ghz * 1e9
            wavelength = c / freq
            D = gs["antenna_dia_m"]
            efficiency = 0.6
            gain = 10 * np.log10(efficiency * (np.pi * D / wavelength)**2)
            beamwidth = np.degrees(1.22 * wavelength / D)
            
            gs[f"{label}_gain_dbi"] = round(float(gain), 1)
            gs[f"{label}_beamwidth_deg"] = round(float(beamwidth), 2)
    
    with open(os.path.join(DATA_DIR, "ground_stations", "stations.json"), 'w') as f:
        json.dump(stations, f, indent=2)
    
    return stations


def generate_atmospheric_profiles():
    """Generate atmospheric absorption profiles."""
    os.makedirs(os.path.join(DATA_DIR, "atmosphere"), exist_ok=True)
    
    # ITU-R P.676 atmospheric gaseous attenuation
    frequencies = np.arange(1, 50, 0.5)  # GHz
    
    # Simplified oxygen and water vapor absorption
    # Zenith attenuation (dB)
    oxygen = 0.001 * frequencies**1.5 * np.exp(-((frequencies - 60) / 15)**2) + 0.005
    water_vapor = 0.002 * frequencies**1.2 * np.exp(-((frequencies - 22.2) / 5)**2) + 0.001
    total = oxygen + water_vapor
    
    filepath = os.path.join(DATA_DIR, "atmosphere", "gaseous_attenuation.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_ghz", "oxygen_db", "water_vapor_db", "total_zenith_db"])
        for i, freq in enumerate(frequencies):
            writer.writerow([f"{freq:.1f}", f"{oxygen[i]:.4f}",
                           f"{water_vapor[i]:.4f}", f"{total[i]:.4f}"])
    
    # Elevation angle scaling
    elevations = np.arange(5, 91, 1)
    scaling = 1.0 / np.sin(np.radians(elevations))
    
    # Atmospheric loss at 12 GHz and 14 GHz vs elevation
    filepath2 = os.path.join(DATA_DIR, "atmosphere", "elevation_scaling.csv")
    with open(filepath2, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["elevation_deg", "path_scaling", "loss_12ghz_db", "loss_14ghz_db"])
        idx_12 = int((12 - 1) / 0.5)
        idx_14 = int((14 - 1) / 0.5)
        for i, el in enumerate(elevations):
            writer.writerow([f"{el:.0f}", f"{scaling[i]:.3f}",
                           f"{total[idx_12] * scaling[i]:.4f}",
                           f"{total[idx_14] * scaling[i]:.4f}"])
    
    return {"frequencies": len(frequencies), "elevations": len(elevations)}


def generate_link_budget_template():
    """Generate a link budget calculation template."""
    
    template = {
        "downlink": {
            "frequency_ghz": 12.0,
            "satellite_eirp_dbw": 40.0,
            "satellite_antenna_gain_dbi": 35.0,
            "satellite_tx_power_dbw": 5.0,
            "ground_antenna_diameter_m": 1.2,
            "ground_antenna_efficiency": 0.6,
            "ground_antenna_gain_dbi": 39.8,
            "system_noise_temp_k": 400,
            "ground_g_over_t_dbk": 13.8,
            "data_rate_mbps": 100,
            "modulation": "QPSK",
            "code_rate": 0.75,
            "coding_type": "LDPC",
            "implementation_loss_db": 2.0,
            "pointing_loss_db": 0.5,
        },
        "uplink": {
            "frequency_ghz": 14.0,
            "ground_eirp_dbw": 45.0,
            "ground_tx_power_dbw": 2.0,
            "ground_antenna_gain_dbi": 43.0,
            "satellite_antenna_gain_dbi": 35.0,
            "satellite_noise_temp_k": 800,
            "satellite_g_over_t_dbk": 6.0,
            "data_rate_mbps": 10,
            "modulation": "QPSK",
            "code_rate": 0.5,
            "coding_type": "LDPC",
            "implementation_loss_db": 2.5,
            "pointing_loss_db": 1.0,
        },
        "modcod_table": [
            {"name": "QPSK_1/4", "efficiency_bps_hz": 0.49, "ebn0_req_db": -2.35},
            {"name": "QPSK_1/3", "efficiency_bps_hz": 0.66, "ebn0_req_db": -1.24},
            {"name": "QPSK_2/5", "efficiency_bps_hz": 0.79, "ebn0_req_db": -0.30},
            {"name": "QPSK_1/2", "efficiency_bps_hz": 0.99, "ebn0_req_db": 1.00},
            {"name": "QPSK_3/5", "efficiency_bps_hz": 1.19, "ebn0_req_db": 2.23},
            {"name": "QPSK_2/3", "efficiency_bps_hz": 1.32, "ebn0_req_db": 3.10},
            {"name": "QPSK_3/4", "efficiency_bps_hz": 1.49, "ebn0_req_db": 4.03},
            {"name": "8PSK_3/5", "efficiency_bps_hz": 1.77, "ebn0_req_db": 5.18},
            {"name": "8PSK_2/3", "efficiency_bps_hz": 1.98, "ebn0_req_db": 6.20},
            {"name": "8PSK_3/4", "efficiency_bps_hz": 2.23, "ebn0_req_db": 7.02},
            {"name": "16APSK_2/3", "efficiency_bps_hz": 2.64, "ebn0_req_db": 8.97},
            {"name": "16APSK_3/4", "efficiency_bps_hz": 2.97, "ebn0_req_db": 10.21},
            {"name": "16APSK_4/5", "efficiency_bps_hz": 3.17, "ebn0_req_db": 11.03},
            {"name": "32APSK_3/4", "efficiency_bps_hz": 3.70, "ebn0_req_db": 12.73},
            {"name": "32APSK_4/5", "efficiency_bps_hz": 3.95, "ebn0_req_db": 13.64},
        ],
    }
    
    with open(os.path.join(DATA_DIR, "link_budget_template.json"), 'w') as f:
        json.dump(template, f, indent=2)
    
    return template


def main():
    print("Generating MIMO-Sat simulation data...")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("1. Generating ITU-R rain model data...")
    rain = generate_rain_model_data()
    
    print("2. Generating orbit and pass geometry data...")
    orbit = generate_orbit_data()
    
    print("3. Generating ground station configurations...")
    stations = generate_ground_stations()
    
    print("4. Generating atmospheric absorption profiles...")
    atm = generate_atmospheric_profiles()
    
    print("5. Generating link budget template...")
    template = generate_link_budget_template()
    
    metadata = {
        "problem": "ECE-2 MIMO-Sat",
        "description": "LEO Satellite Communication Link Design",
        "system_params": {
            "orbit_altitude_km": 550,
            "downlink_freq_ghz": 12,
            "uplink_freq_ghz": 14,
            "ground_antenna_m": 1.2,
            "satellite_elements": 256,
            "downlink_rate_mbps": 100,
            "uplink_rate_mbps": 10,
            "ber_requirement": 1e-6,
        },
        "data_contents": {
            "rain_model": f"{len(rain)} climate zones with exceedance data + attenuation coefficients",
            "orbit": f"constellation params + {len(orbit.get('passes', []))} pass geometries",
            "ground_stations": f"{len(stations)} stations in different climate zones",
            "atmosphere": "gaseous attenuation + elevation scaling profiles",
            "link_budget_template": "DVB-S2X ModCod table + link parameters",
        },
        "seed": SEED,
    }
    
    with open(os.path.join(DATA_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nData generated in: {DATA_DIR}")
    print(f"  - rain_model/: {len(rain)} climate zones + attenuation coefficients")
    print(f"  - orbit/: constellation params + 50 satellite passes")
    print(f"  - ground_stations/: {len(stations)} ground stations")
    print(f"  - atmosphere/: absorption profiles")
    print(f"  - link_budget_template.json: ModCod table + link params")
    print("\nDone!")


if __name__ == "__main__":
    main()
