"""
Generate reference data for EEE-5: E-Harvest — High-Efficiency RF Energy Harvesting System

Creates:
  data/rf_environment/    - Ambient RF power survey data
  data/antennas/          - Antenna specifications and radiation patterns
  data/diodes/            - Schottky diode models (SPICE parameters + V-I curves)
  data/regulators/        - Low-power voltage regulator catalog
  data/capacitors/        - Energy storage capacitor catalog
  data/substrates.json    - PCB substrate properties
  data/matching.json      - Smith chart reference points for common impedances
"""

import os
import json
import csv
import numpy as np

SEED = 42
np.random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def ensure_dirs():
    for sub in ["rf_environment", "antennas", "diodes", "regulators", "capacitors"]:
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)


def generate_rf_environment():
    """Generate ambient RF power survey data for urban environment."""
    print("1. Generating RF environment data...")

    # RF power survey at various frequencies
    bands = [
        {"name": "FM_Radio", "center_MHz": 100, "BW_MHz": 20, "avg_dBm": -25, "std_dB": 5},
        {"name": "TV_VHF", "center_MHz": 200, "BW_MHz": 50, "avg_dBm": -30, "std_dB": 8},
        {"name": "TV_UHF", "center_MHz": 600, "BW_MHz": 100, "avg_dBm": -28, "std_dB": 7},
        {"name": "GSM_900", "center_MHz": 940, "BW_MHz": 35, "avg_dBm": -18, "std_dB": 6},
        {"name": "GSM_1800", "center_MHz": 1840, "BW_MHz": 75, "avg_dBm": -22, "std_dB": 7},
        {"name": "UMTS_2100", "center_MHz": 2140, "BW_MHz": 60, "avg_dBm": -24, "std_dB": 6},
        {"name": "WiFi_2400", "center_MHz": 2440, "BW_MHz": 100, "avg_dBm": -30, "std_dB": 10},
        {"name": "LTE_700", "center_MHz": 740, "BW_MHz": 30, "avg_dBm": -20, "std_dB": 5},
        {"name": "LTE_1900", "center_MHz": 1950, "BW_MHz": 60, "avg_dBm": -23, "std_dB": 6},
    ]

    # Spectral survey: power vs frequency
    freq_sweep = np.arange(500, 2600, 5)  # 500 MHz to 2.5 GHz, 5 MHz steps
    power_sweep = np.full_like(freq_sweep, -50.0, dtype=float)  # Noise floor

    for band in bands:
        f_start = band["center_MHz"] - band["BW_MHz"] / 2
        f_end = band["center_MHz"] + band["BW_MHz"] / 2
        mask = (freq_sweep >= f_start) & (freq_sweep <= f_end)
        if np.any(mask):
            # Band-shaped power distribution
            f_band = freq_sweep[mask]
            p_band = band["avg_dBm"] - 3 * ((f_band - band["center_MHz"]) / (band["BW_MHz"] / 2))**2
            p_band += np.random.randn(len(p_band)) * 2
            power_sweep[mask] = np.maximum(power_sweep[mask], p_band)

    filepath = os.path.join(DATA_DIR, "rf_environment", "spectral_survey.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_MHz", "power_dBm"])
        for i in range(len(freq_sweep)):
            writer.writerow([f"{freq_sweep[i]}", f"{power_sweep[i]:.1f}"])

    # Location-based survey (distance from cell tower)
    distances = np.arange(10, 510, 10)  # 10m to 500m
    locations = []
    for d in distances:
        # Free-space path loss at 900 MHz
        FSPL_900 = 20 * np.log10(d) + 20 * np.log10(900e6) - 147.55
        P_900 = 43 - FSPL_900 + np.random.randn() * 4  # 43 dBm EIRP typical

        FSPL_2400 = 20 * np.log10(d) + 20 * np.log10(2400e6) - 147.55
        P_2400 = 20 - FSPL_2400 + np.random.randn() * 6  # 20 dBm WiFi

        locations.append({
            "distance_m": int(d),
            "P_900MHz_dBm": round(float(P_900), 1),
            "P_2400MHz_dBm": round(float(P_2400), 1)
        })

    with open(os.path.join(DATA_DIR, "rf_environment", "survey.json"), 'w') as f:
        json.dump({
            "bands": bands,
            "location_survey": locations,
            "notes": "Urban environment, measurements at 1.5m height"
        }, f, indent=2)


def generate_antenna_data():
    """Generate antenna specifications and radiation patterns."""
    print("2. Generating antenna data...")

    antennas = [
        {
            "name": "Patch_900MHz",
            "type": "Microstrip Patch",
            "frequency_MHz": 900,
            "bandwidth_pct": 4.0,
            "gain_dBi": 6.0,
            "dimensions_mm": {"W": 87, "L": 78, "h": 3.2},
            "impedance_ohm": {"real": 50, "imag": 0},
            "substrate": "FR4",
            "polarization": "Linear",
            "beamwidth_deg": {"E_plane": 90, "H_plane": 100}
        },
        {
            "name": "Patch_2400MHz",
            "type": "Microstrip Patch",
            "frequency_MHz": 2400,
            "bandwidth_pct": 5.0,
            "gain_dBi": 7.0,
            "dimensions_mm": {"W": 32, "L": 28, "h": 1.6},
            "impedance_ohm": {"real": 50, "imag": 0},
            "substrate": "FR4",
            "polarization": "Linear",
            "beamwidth_deg": {"E_plane": 85, "H_plane": 95}
        },
        {
            "name": "Dual_Band_Fractal",
            "type": "Koch Fractal Dipole",
            "frequency_MHz": [900, 2400],
            "bandwidth_pct": [3.5, 4.5],
            "gain_dBi": [2.5, 3.0],
            "dimensions_mm": {"W": 50, "L": 50},
            "impedance_ohm": {"real": 73, "imag": -15},
            "substrate": "FR4",
            "polarization": "Linear",
            "beamwidth_deg": {"E_plane": 120, "H_plane": 120},
            "note": "Fits 50x50mm constraint"
        },
        {
            "name": "Wideband_Spiral",
            "type": "Archimedean Spiral",
            "frequency_MHz": [800, 2500],
            "bandwidth_pct": 100,
            "gain_dBi": [3.0, 4.0],
            "dimensions_mm": {"diameter": 50},
            "impedance_ohm": {"real": 188, "imag": 0},
            "substrate": "FR4",
            "polarization": "Circular",
            "beamwidth_deg": {"E_plane": 100, "H_plane": 100},
            "note": "Very wideband but needs impedance transformer"
        },
    ]

    # Generate S11 (return loss) vs frequency for each antenna
    for ant in antennas:
        if isinstance(ant["frequency_MHz"], list):
            f_range = np.arange(ant["frequency_MHz"][0] * 0.7,
                               ant["frequency_MHz"][-1] * 1.3, 5)
            S11 = np.full_like(f_range, -2.0)  # Poor match baseline
            for fc in ant["frequency_MHz"]:
                bw = fc * ant["bandwidth_pct"][0] / 100 if isinstance(ant["bandwidth_pct"], list) else fc * ant["bandwidth_pct"] / 100
                S11 += -15 * np.exp(-((f_range - fc) / (bw / 2))**2)
        else:
            fc = ant["frequency_MHz"]
            bw_pct = ant["bandwidth_pct"]
            bw = fc * bw_pct / 100
            f_range = np.arange(fc * 0.8, fc * 1.2, 2)
            S11 = -2 - 18 * np.exp(-((f_range - fc) / (bw / 2))**2)

        S11 = np.clip(S11, -35, -0.5)

        filepath = os.path.join(DATA_DIR, "antennas", f"{ant['name']}_S11.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["frequency_MHz", "S11_dB"])
            for i in range(len(f_range)):
                writer.writerow([f"{f_range[i]:.0f}", f"{S11[i]:.2f}"])

    # Radiation pattern (generic, E-plane) for patch at 900 MHz
    theta = np.arange(-180, 181, 2)
    gain_pattern = 6 * np.cos(np.radians(theta))**2
    gain_pattern = np.where(np.abs(theta) > 90, -15, gain_pattern)
    gain_pattern += np.random.randn(len(theta)) * 0.3

    filepath = os.path.join(DATA_DIR, "antennas", "Patch_900MHz_pattern.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["theta_deg", "gain_dBi"])
        for i in range(len(theta)):
            writer.writerow([f"{theta[i]}", f"{gain_pattern[i]:.2f}"])

    with open(os.path.join(DATA_DIR, "antennas", "catalog.json"), 'w') as f:
        json.dump({"antennas": antennas}, f, indent=2)


def generate_diode_data():
    """Generate Schottky diode models for rectifier design."""
    print("3. Generating Schottky diode data...")

    diodes = [
        {
            "part": "HSMS-2850",
            "manufacturer": "Broadcom",
            "type": "Zero-bias Schottky",
            "Vf_mV": 150,
            "Is_nA": 3000,
            "n": 1.06,
            "Rs_Ohm": 25,
            "Cj0_pF": 0.18,
            "BV_V": 3.8,
            "package": "SOT-23",
            "frequency_range": "Up to 6 GHz",
            "best_for": "High power (> -20 dBm)",
            "cost_usd": 0.40
        },
        {
            "part": "HSMS-2860",
            "manufacturer": "Broadcom",
            "type": "DC-biased Schottky",
            "Vf_mV": 350,
            "Is_nA": 50,
            "n": 1.08,
            "Rs_Ohm": 6,
            "Cj0_pF": 0.18,
            "BV_V": 7.0,
            "package": "SOT-23",
            "frequency_range": "Up to 4 GHz",
            "best_for": "Higher voltage applications",
            "cost_usd": 0.35
        },
        {
            "part": "SMS7630",
            "manufacturer": "Skyworks",
            "type": "Zero-bias Schottky",
            "Vf_mV": 90,
            "Is_nA": 5000,
            "n": 1.05,
            "Rs_Ohm": 20,
            "Cj0_pF": 0.14,
            "BV_V": 2.0,
            "package": "SC-79",
            "frequency_range": "Up to 24 GHz",
            "best_for": "Very low power (< -20 dBm)",
            "cost_usd": 0.60
        },
        {
            "part": "HSMS-2820",
            "manufacturer": "Broadcom",
            "type": "Zero-bias Schottky",
            "Vf_mV": 340,
            "Is_nA": 22,
            "n": 1.08,
            "Rs_Ohm": 6,
            "Cj0_pF": 0.70,
            "BV_V": 15.0,
            "package": "SOT-23",
            "frequency_range": "Up to 4 GHz",
            "best_for": "Detector/mixer applications",
            "cost_usd": 0.30
        },
    ]

    # Generate V-I curves
    for diode in diodes:
        V = np.linspace(-1, 0.6, 200)
        Is = diode["Is_nA"] * 1e-9
        n = diode["n"]
        Vt = 0.02585  # Thermal voltage at 25°C
        Rs = diode["Rs_Ohm"]

        # Shockley equation (simplified, ignoring Rs effect on V)
        I = Is * (np.exp(V / (n * Vt)) - 1)
        I = np.clip(I, -Is * 10, 0.1)  # Limit current range

        filepath = os.path.join(DATA_DIR, "diodes", f"{diode['part']}_VI.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["voltage_V", "current_A"])
            for i in range(len(V)):
                writer.writerow([f"{V[i]:.4f}", f"{I[i]:.6e}"])

    # Generate RF-to-DC efficiency curves (input power vs efficiency)
    input_power_dBm = np.arange(-30, 5, 1)
    for diode in diodes:
        # Efficiency model: peaks at moderate power, drops at low power
        P_opt_dBm = -5  # Optimal input power
        eta_peak = 0.55 if "2850" in diode["part"] else 0.45
        if "7630" in diode["part"]:
            eta_peak = 0.50
            P_opt_dBm = -10

        eta = eta_peak * np.exp(-0.5 * ((input_power_dBm - P_opt_dBm) / 8)**2)
        # Very low efficiency at very low power
        eta[input_power_dBm < -25] *= np.exp(0.2 * (input_power_dBm[input_power_dBm < -25] + 25))
        eta = np.clip(eta, 0, 0.7)

        filepath = os.path.join(DATA_DIR, "diodes", f"{diode['part']}_efficiency.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["input_power_dBm", "efficiency"])
            for i in range(len(input_power_dBm)):
                writer.writerow([f"{input_power_dBm[i]}", f"{eta[i]:.4f}"])

    with open(os.path.join(DATA_DIR, "diodes", "catalog.json"), 'w') as f:
        json.dump({
            "diodes": diodes,
            "rectifier_topologies": [
                {"name": "Single Series", "stages": 1, "Vout_approx": "Vpeak - Vf",
                 "best_for": "Highest efficiency at moderate power"},
                {"name": "Voltage Doubler", "stages": 2, "Vout_approx": "2*(Vpeak - Vf)",
                 "best_for": "Higher output voltage, moderate efficiency"},
                {"name": "Dickson 3-stage", "stages": 3, "Vout_approx": "3*(Vpeak - Vf)",
                 "best_for": "Very low input power, high output voltage"},
                {"name": "Dickson 5-stage", "stages": 5, "Vout_approx": "5*(Vpeak - Vf)",
                 "best_for": "Extremely low input power"}
            ]
        }, f, indent=2)


def generate_regulator_data():
    """Generate low-power voltage regulator catalog."""
    print("4. Generating regulator catalog...")

    regulators = {
        "regulators": [
            {
                "part": "TPS7A02",
                "type": "Ultra-low Iq LDO",
                "manufacturer": "TI",
                "Vin_min_V": 1.1, "Vin_max_V": 6.5,
                "Vout_V": 1.8,
                "Iq_nA": 25,
                "Iout_max_mA": 200,
                "dropout_mV": 100,
                "noise_uV_rms": 6.6,
                "PSRR_dB_1kHz": 62,
                "package": "SOT-23-5",
                "cost_usd": 0.80,
                "note": "Best for ultra-low power, 25nA quiescent"
            },
            {
                "part": "ADP151",
                "type": "Ultra-low noise LDO",
                "manufacturer": "Analog Devices",
                "Vin_min_V": 2.2, "Vin_max_V": 5.5,
                "Vout_V": 1.8,
                "Iq_nA": 9000,
                "Iout_max_mA": 200,
                "dropout_mV": 150,
                "noise_uV_rms": 9,
                "PSRR_dB_1kHz": 70,
                "package": "TSOT-5",
                "cost_usd": 1.20,
                "note": "Very low noise, good for sensor applications"
            },
            {
                "part": "BQ25570",
                "type": "MPPT Energy Harvester",
                "manufacturer": "TI",
                "Vin_min_V": 0.1, "Vin_max_V": 5.1,
                "Vout_V": "Programmable 1.8-5.0",
                "Iq_nA": 488,
                "Iout_max_mA": 110,
                "features": ["Cold start from 330mV/15uW", "MPPT",
                             "Programmable Vout", "Battery management"],
                "efficiency_pct": 90,
                "package": "QFN-20",
                "cost_usd": 3.50,
                "note": "Complete energy harvesting solution with MPPT"
            },
            {
                "part": "SPV1040",
                "type": "Boost converter for energy harvesting",
                "manufacturer": "STMicroelectronics",
                "Vin_min_V": 0.3, "Vin_max_V": 5.5,
                "Vout_V": "Up to 5.2",
                "Iq_uA": 4,
                "Iout_max_mA": 70,
                "features": ["Built-in MPPT", "93% peak efficiency"],
                "efficiency_pct": 93,
                "package": "TSSOP-8",
                "cost_usd": 2.80,
                "note": "Good for boosting low RF rectifier output"
            },
        ]
    }

    with open(os.path.join(DATA_DIR, "regulators", "catalog.json"), 'w') as f:
        json.dump(regulators, f, indent=2)


def generate_capacitor_data():
    """Generate energy storage capacitor catalog."""
    print("5. Generating capacitor catalog...")

    capacitors = {
        "storage_capacitors": [
            {
                "type": "MLCC (Ceramic)",
                "part": "GRM219R71E105KA12",
                "capacitance_uF": 1,
                "voltage_V": 25,
                "ESR_mOhm": 50,
                "leakage_nA": 10,
                "size_mm": "0805",
                "energy_uJ": 313,
                "cost_usd": 0.05
            },
            {
                "type": "MLCC (Ceramic)",
                "part": "GRM32ER71A106KA12",
                "capacitance_uF": 10,
                "voltage_V": 10,
                "ESR_mOhm": 20,
                "leakage_nA": 50,
                "size_mm": "1206",
                "energy_uJ": 500,
                "cost_usd": 0.10
            },
            {
                "type": "Tantalum",
                "part": "TAJA106K010RNJ",
                "capacitance_uF": 10,
                "voltage_V": 10,
                "ESR_mOhm": 2000,
                "leakage_uA": 1,
                "size_mm": "1206",
                "energy_uJ": 500,
                "cost_usd": 0.20
            },
            {
                "type": "Supercapacitor",
                "part": "CPH3225A",
                "capacitance_mF": 11,
                "voltage_V": 3.3,
                "ESR_Ohm": 70,
                "leakage_uA": 1.5,
                "size_mm": "3.2x2.5x0.9",
                "energy_mJ": 59.9,
                "cost_usd": 2.50,
                "note": "Thin-film supercap, good for energy buffering"
            },
            {
                "type": "Supercapacitor",
                "part": "DMF3Z5R5H474M3DTA0",
                "capacitance_mF": 470,
                "voltage_V": 5.5,
                "ESR_Ohm": 25,
                "leakage_uA": 5,
                "size_mm": "Coin 13.5x5.5",
                "energy_mJ": 7108,
                "cost_usd": 4.00,
                "note": "Higher capacity for intermittent operation"
            },
        ],
        "sizing_formula": {
            "energy_storage": "E = 0.5 * C * (V_max^2 - V_min^2)",
            "discharge_time": "t = C * (V_max - V_min) / I_load",
            "example": {
                "C_uF": 470000,
                "V_max": 3.3,
                "V_min": 1.8,
                "I_load_uA": 100,
                "discharge_time_s": 7050
            }
        }
    }

    with open(os.path.join(DATA_DIR, "capacitors", "catalog.json"), 'w') as f:
        json.dump(capacitors, f, indent=2)


def generate_substrate_data():
    """Generate PCB substrate properties."""
    print("6. Generating substrate data...")

    substrates = {
        "pcb_substrates": [
            {
                "name": "FR4",
                "er": 4.4, "tan_delta": 0.02,
                "thickness_mm": [0.8, 1.0, 1.6],
                "copper_thickness_um": [18, 35],
                "cost_relative": 1.0,
                "max_frequency_GHz": 3.0,
                "note": "Standard, adequate for 900 MHz - 2.4 GHz"
            },
            {
                "name": "Rogers RO4003C",
                "er": 3.38, "tan_delta": 0.0027,
                "thickness_mm": [0.508, 0.813, 1.524],
                "copper_thickness_um": [18, 35],
                "cost_relative": 5.0,
                "max_frequency_GHz": 18.0,
                "note": "Low loss, excellent for RF circuits"
            },
            {
                "name": "Rogers RT/duroid 5880",
                "er": 2.2, "tan_delta": 0.0009,
                "thickness_mm": [0.787, 1.575],
                "copper_thickness_um": [18, 35],
                "cost_relative": 8.0,
                "max_frequency_GHz": 40.0,
                "note": "Very low loss, best RF performance"
            },
        ],
        "microstrip_equations": {
            "effective_er": "er_eff = (er+1)/2 + (er-1)/2 * (1+12*h/W)^(-0.5)",
            "characteristic_impedance": "Z0 = (120*pi) / (sqrt(er_eff) * (W/h + 1.393 + 0.667*ln(W/h + 1.444)))",
            "wavelength": "lambda = c / (f * sqrt(er_eff))"
        },
        "design_constraint": {
            "pcb_size_mm": {"W": 50, "L": 50},
            "layers": 2,
            "note": "Must fit entire rectenna on 50x50mm 2-layer PCB"
        }
    }

    with open(os.path.join(DATA_DIR, "substrates.json"), 'w') as f:
        json.dump(substrates, f, indent=2)


def generate_matching_data():
    """Generate impedance matching reference data."""
    print("7. Generating matching network reference data...")

    # Rectifier input impedance vs frequency and power (measured)
    freqs = [900, 1200, 1800, 2400]
    powers = [-20, -15, -10, -5, 0]

    impedance_data = []
    for freq in freqs:
        for pwr in powers:
            # Rectifier impedance is nonlinear — varies with power
            R = 200 - 10 * (pwr + 20) + np.random.randn() * 5  # Real part
            X = -80 + 5 * (pwr + 20) + (freq - 900) * 0.02 + np.random.randn() * 3  # Imaginary
            impedance_data.append({
                "frequency_MHz": freq,
                "input_power_dBm": pwr,
                "Z_real_Ohm": round(float(R), 1),
                "Z_imag_Ohm": round(float(X), 1)
            })

    matching = {
        "rectifier_impedances": impedance_data,
        "source_impedance_Ohm": 50,
        "matching_topologies": [
            {
                "name": "L-network (series L, shunt C)",
                "suitable_when": "Z_load > Z_source",
                "Q_factor": "sqrt(R_load/R_source - 1)",
                "bandwidth": "Narrow (5-10%)"
            },
            {
                "name": "Pi-network",
                "suitable_when": "Need wider bandwidth",
                "Q_factor": "Adjustable",
                "bandwidth": "Medium (10-20%)"
            },
            {
                "name": "T-network",
                "suitable_when": "Need impedance step-up",
                "Q_factor": "Adjustable",
                "bandwidth": "Medium (10-20%)"
            },
            {
                "name": "Multi-section matching",
                "suitable_when": "Wideband 900-2400 MHz",
                "Q_factor": "Low",
                "bandwidth": "Wide (>50%)"
            },
        ],
        "notes": [
            "Rectifier impedance is power-dependent — match at expected operating power",
            "Conjugate match: Z_match = Z_rect* for maximum power transfer",
            "Component parasitics matter above 1 GHz — use distributed elements"
        ]
    }

    with open(os.path.join(DATA_DIR, "matching.json"), 'w') as f:
        json.dump(matching, f, indent=2)


def main():
    print("Generating E-Harvest reference data...")
    print("=" * 50)

    ensure_dirs()
    generate_rf_environment()
    generate_antenna_data()
    generate_diode_data()
    generate_regulator_data()
    generate_capacitor_data()
    generate_substrate_data()
    generate_matching_data()

    print(f"\nData generated in: {DATA_DIR}")
    print("  - rf_environment/: Spectral survey + location power survey")
    print("  - antennas/: 4 antenna designs + S11 curves + radiation pattern")
    print("  - diodes/: 4 Schottky diodes (V-I + RF-DC efficiency curves)")
    print("  - regulators/: 4 low-power regulator/harvester ICs")
    print("  - capacitors/: Energy storage catalog")
    print("  - substrates.json: PCB material properties")
    print("  - matching.json: Impedance matching reference")
    print("\nDone!")


if __name__ == "__main__":
    main()
