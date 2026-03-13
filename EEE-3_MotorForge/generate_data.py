"""
Generate reference data for EEE-3: MotorForge — Design and Simulation of a 10 kW BLDC Motor

Creates:
  data/materials/         - Magnetic, electrical, and structural material properties
  data/magnets/           - NdFeB magnet grade specifications
  data/laminations/       - Electrical steel lamination data (BH curves, loss curves)
  data/bearings.json      - Bearing catalog for motor
  data/drive_cycles/      - Scooter drive cycle profiles
  data/thermal.json       - Thermal reference data (convection coefficients, etc.)
  data/wire_table.csv     - AWG / metric wire gauge table
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
    for sub in ["materials", "magnets", "laminations", "drive_cycles"]:
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)


def generate_magnet_data():
    """Generate NdFeB magnet grade specifications."""
    print("1. Generating magnet specifications...")

    grades = [
        {
            "grade": "N35",
            "Br_T": 1.17, "Hc_kA_m": 868, "BHmax_kJ_m3": 263,
            "Tc_C": 310, "alpha_Br_pct_C": -0.12, "beta_Hc_pct_C": -0.60,
            "density_kg_m3": 7500, "resistivity_uOhm_cm": 144,
            "max_operating_temp_C": 80, "cost_usd_per_kg": 60
        },
        {
            "grade": "N42",
            "Br_T": 1.28, "Hc_kA_m": 955, "BHmax_kJ_m3": 318,
            "Tc_C": 310, "alpha_Br_pct_C": -0.12, "beta_Hc_pct_C": -0.60,
            "density_kg_m3": 7500, "resistivity_uOhm_cm": 144,
            "max_operating_temp_C": 80, "cost_usd_per_kg": 75
        },
        {
            "grade": "N42SH",
            "Br_T": 1.28, "Hc_kA_m": 955, "BHmax_kJ_m3": 318,
            "Tc_C": 340, "alpha_Br_pct_C": -0.10, "beta_Hc_pct_C": -0.50,
            "density_kg_m3": 7500, "resistivity_uOhm_cm": 150,
            "max_operating_temp_C": 150, "cost_usd_per_kg": 95
        },
        {
            "grade": "N48",
            "Br_T": 1.38, "Hc_kA_m": 1035, "BHmax_kJ_m3": 366,
            "Tc_C": 310, "alpha_Br_pct_C": -0.12, "beta_Hc_pct_C": -0.60,
            "density_kg_m3": 7500, "resistivity_uOhm_cm": 144,
            "max_operating_temp_C": 80, "cost_usd_per_kg": 100
        },
        {
            "grade": "N52",
            "Br_T": 1.44, "Hc_kA_m": 1070, "BHmax_kJ_m3": 398,
            "Tc_C": 310, "alpha_Br_pct_C": -0.12, "beta_Hc_pct_C": -0.60,
            "density_kg_m3": 7600, "resistivity_uOhm_cm": 144,
            "max_operating_temp_C": 80, "cost_usd_per_kg": 130
        },
    ]

    with open(os.path.join(DATA_DIR, "magnets", "ndfeb_grades.json"), 'w') as f:
        json.dump({
            "magnets": grades,
            "notes": {
                "Br_T": "Remanence in Tesla",
                "Hc_kA_m": "Coercivity in kA/m",
                "BHmax_kJ_m3": "Maximum energy product in kJ/m^3",
                "Tc_C": "Curie temperature in Celsius",
                "alpha_Br_pct_C": "Temperature coefficient of Br (%/C)",
                "beta_Hc_pct_C": "Temperature coefficient of Hc (%/C)"
            }
        }, f, indent=2)

    # BH demagnetization curves for each grade
    for grade in grades:
        H = np.linspace(0, -grade["Hc_kA_m"] * 1.2, 100)  # kA/m
        # Linear demagnetization (simplified NdFeB)
        B = grade["Br_T"] + grade["Br_T"] / grade["Hc_kA_m"] * H
        B = np.clip(B, 0, grade["Br_T"])

        filepath = os.path.join(DATA_DIR, "magnets", f"{grade['grade']}_BH.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["H_kA_m", "B_T"])
            for i in range(len(H)):
                writer.writerow([f"{H[i]:.1f}", f"{B[i]:.4f}"])


def generate_lamination_data():
    """Generate electrical steel lamination BH curves and loss data."""
    print("2. Generating lamination data...")

    steels = [
        {"name": "M19_29Ga", "thickness_mm": 0.35, "density_kg_m3": 7650,
         "resistivity_uOhm_cm": 52, "Bs_T": 1.95, "mu_i": 5000,
         "kh": 0.004, "ke": 0.00002, "cost_usd_per_kg": 2.0},
        {"name": "M36_29Ga", "thickness_mm": 0.35, "density_kg_m3": 7650,
         "resistivity_uOhm_cm": 45, "Bs_T": 1.90, "mu_i": 4000,
         "kh": 0.005, "ke": 0.000025, "cost_usd_per_kg": 1.5},
        {"name": "M47_29Ga", "thickness_mm": 0.35, "density_kg_m3": 7700,
         "resistivity_uOhm_cm": 40, "Bs_T": 1.85, "mu_i": 3500,
         "kh": 0.006, "ke": 0.00003, "cost_usd_per_kg": 1.2},
        {"name": "NO20_Thin", "thickness_mm": 0.20, "density_kg_m3": 7650,
         "resistivity_uOhm_cm": 55, "Bs_T": 1.80, "mu_i": 6000,
         "kh": 0.003, "ke": 0.000008, "cost_usd_per_kg": 4.0,
         "note": "Thin non-oriented for high frequency"},
    ]

    catalog = []
    mu_0 = 4 * np.pi * 1e-7

    for steel in steels:
        # Generate BH curve
        H = np.concatenate([
            np.linspace(0, 100, 20),
            np.linspace(100, 1000, 20),
            np.linspace(1000, 10000, 20),
            np.linspace(10000, 100000, 20)
        ])

        # Jiles-Atherton simplified model
        Bs = steel["Bs_T"]
        B = Bs * np.tanh(H / 500) + mu_0 * H
        B = np.clip(B, 0, Bs + 0.1)

        filepath = os.path.join(DATA_DIR, "laminations", f"{steel['name']}_BH.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["H_A_m", "B_T", "mu_r"])
            for i in range(len(H)):
                mu_r = (B[i] / (mu_0 * (H[i] + 1e-6))) if H[i] > 0 else steel["mu_i"]
                writer.writerow([f"{H[i]:.1f}", f"{B[i]:.4f}", f"{mu_r:.0f}"])

        # Core loss data: W/kg at various frequencies and flux densities
        frequencies = [50, 100, 200, 400, 800, 1000]
        flux_densities = [0.5, 0.8, 1.0, 1.2, 1.4, 1.6]

        loss_path = os.path.join(DATA_DIR, "laminations", f"{steel['name']}_losses.csv")
        with open(loss_path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["B_T"] + [f"loss_W_kg_{freq}Hz" for freq in frequencies]
            writer.writerow(header)
            for B_val in flux_densities:
                row = [f"{B_val:.1f}"]
                for freq in frequencies:
                    # Steinmetz equation: P = kh*f*B^1.6 + ke*f^2*B^2
                    P = steel["kh"] * freq * B_val**1.6 + steel["ke"] * freq**2 * B_val**2
                    row.append(f"{P:.3f}")
                writer.writerow(row)

        catalog.append({
            "name": steel["name"],
            "thickness_mm": steel["thickness_mm"],
            "density_kg_m3": steel["density_kg_m3"],
            "saturation_B_T": steel["Bs_T"],
            "initial_permeability": steel["mu_i"],
            "cost_usd_per_kg": steel["cost_usd_per_kg"],
            "bh_file": f"laminations/{steel['name']}_BH.csv",
            "loss_file": f"laminations/{steel['name']}_losses.csv"
        })

    with open(os.path.join(DATA_DIR, "laminations", "catalog.json"), 'w') as f:
        json.dump({"laminations": catalog}, f, indent=2)


def generate_wire_table():
    """Generate magnet wire gauge table."""
    print("3. Generating wire gauge table...")

    filepath = os.path.join(DATA_DIR, "wire_table.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "AWG", "bare_diameter_mm", "insulated_diameter_mm",
            "resistance_ohm_per_m_20C", "max_current_A_5A_mm2",
            "weight_kg_per_m", "temp_coeff_per_C"
        ])

        awg_data = [
            (10, 2.588, 2.69, 0.00328, 26.3, 0.0471, 0.00393),
            (12, 2.053, 2.15, 0.00521, 16.6, 0.0297, 0.00393),
            (14, 1.628, 1.73, 0.00828, 10.4, 0.0187, 0.00393),
            (16, 1.291, 1.38, 0.01317, 6.55, 0.0118, 0.00393),
            (18, 1.024, 1.10, 0.02093, 4.12, 0.00742, 0.00393),
            (20, 0.812, 0.88, 0.03326, 2.59, 0.00467, 0.00393),
            (22, 0.644, 0.71, 0.05286, 1.63, 0.00294, 0.00393),
            (24, 0.511, 0.57, 0.08400, 1.02, 0.00185, 0.00393),
            (26, 0.405, 0.46, 0.13350, 0.645, 0.00116, 0.00393),
            (28, 0.321, 0.37, 0.21220, 0.405, 0.000732, 0.00393),
        ]
        for row in awg_data:
            writer.writerow([str(row[0])] + [f"{v:.5f}" if isinstance(v, float) else str(v) for v in row[1:]])


def generate_bearing_data():
    """Generate bearing catalog for BLDC motor."""
    print("4. Generating bearing catalog...")

    bearings = {
        "bearings": [
            {
                "designation": "6203-2RS", "type": "Deep Groove Ball",
                "bore_mm": 17, "OD_mm": 40, "width_mm": 12,
                "dynamic_load_kN": 9.56, "static_load_kN": 4.75,
                "max_speed_rpm": 17000, "mass_g": 56,
                "friction_coefficient": 0.0015, "cost_usd": 3.0
            },
            {
                "designation": "6204-2RS", "type": "Deep Groove Ball",
                "bore_mm": 20, "OD_mm": 47, "width_mm": 14,
                "dynamic_load_kN": 12.7, "static_load_kN": 6.55,
                "max_speed_rpm": 15000, "mass_g": 86,
                "friction_coefficient": 0.0015, "cost_usd": 3.5
            },
            {
                "designation": "6205-2RS", "type": "Deep Groove Ball",
                "bore_mm": 25, "OD_mm": 52, "width_mm": 15,
                "dynamic_load_kN": 14.0, "static_load_kN": 7.80,
                "max_speed_rpm": 12000, "mass_g": 110,
                "friction_coefficient": 0.0015, "cost_usd": 4.0
            },
            {
                "designation": "6206-2RS", "type": "Deep Groove Ball",
                "bore_mm": 30, "OD_mm": 62, "width_mm": 16,
                "dynamic_load_kN": 19.5, "static_load_kN": 11.2,
                "max_speed_rpm": 10000, "mass_g": 178,
                "friction_coefficient": 0.0015, "cost_usd": 5.0
            },
        ],
        "life_equation": "L10 = (C / P)^3 * 10^6 revolutions",
        "notes": "2RS = double rubber sealed, suitable for grease lubrication"
    }

    with open(os.path.join(DATA_DIR, "bearings.json"), 'w') as f:
        json.dump(bearings, f, indent=2)


def generate_drive_cycles():
    """Generate scooter drive cycle profiles."""
    print("5. Generating drive cycles...")

    # Urban commute cycle (stop-and-go, 15 minutes)
    t_urban = np.arange(0, 900, 1)  # 15 min, 1 Hz
    speed_urban = np.zeros_like(t_urban, dtype=float)

    # Segments: accelerate, cruise, decelerate, stop, repeat
    segments = [
        (0, 20, 8, 30),      # 0-30 km/h in 20s, cruise 8s
        (58, 15, 10, 40),     # accelerate to 40 km/h
        (123, 10, 0, 0),      # decelerate to stop
        (143, 20, 8, 35),
        (211, 12, 15, 45),
        (278, 10, 0, 0),
        (308, 25, 10, 30),
        (383, 15, 20, 50),
        (458, 10, 0, 0),
        (488, 20, 12, 35),
        (560, 18, 15, 40),
        (633, 10, 0, 0),
        (653, 22, 8, 30),
        (723, 15, 12, 45),
        (790, 15, 0, 0),
    ]

    for seg_start, accel_dur, cruise_dur, target_speed in segments:
        if seg_start >= len(t_urban):
            break
        # Acceleration phase
        end_accel = min(seg_start + accel_dur, len(t_urban))
        if accel_dur > 0:
            speed_urban[seg_start:end_accel] = np.linspace(
                speed_urban[max(0, seg_start - 1)] if seg_start > 0 else 0,
                target_speed,
                end_accel - seg_start
            )
        # Cruise phase
        end_cruise = min(end_accel + cruise_dur, len(t_urban))
        speed_urban[end_accel:end_cruise] = target_speed

    # Add noise
    speed_urban += np.random.randn(len(speed_urban)) * 0.5
    speed_urban = np.clip(speed_urban, 0, 60)

    filepath = os.path.join(DATA_DIR, "drive_cycles", "urban_commute.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "speed_kmh", "road_grade_pct"])
        grade = np.random.choice([-2, -1, 0, 0, 0, 1, 2], size=len(t_urban))
        for i in range(len(t_urban)):
            writer.writerow([f"{t_urban[i]}", f"{speed_urban[i]:.1f}", f"{grade[i]}"])

    # Highway / suburban cycle
    t_hwy = np.arange(0, 600, 1)  # 10 min
    speed_hwy = np.zeros_like(t_hwy, dtype=float)
    # Ramp up to 60 km/h, cruise, slight variations
    speed_hwy[:30] = np.linspace(0, 60, 30)
    speed_hwy[30:500] = 60 + np.random.randn(470) * 2
    speed_hwy[500:530] = np.linspace(60, 40, 30)
    speed_hwy[530:570] = 40 + np.random.randn(40) * 1
    speed_hwy[570:] = np.linspace(40, 0, 30)
    speed_hwy = np.clip(speed_hwy, 0, 70)

    filepath = os.path.join(DATA_DIR, "drive_cycles", "suburban.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "speed_kmh", "road_grade_pct"])
        for i in range(len(t_hwy)):
            writer.writerow([f"{t_hwy[i]}", f"{speed_hwy[i]:.1f}", "0"])

    # Hill climb test
    t_hill = np.arange(0, 300, 1)
    speed_hill = np.zeros_like(t_hill, dtype=float)
    speed_hill[:20] = np.linspace(0, 25, 20)
    speed_hill[20:250] = 25 + np.random.randn(230) * 1
    speed_hill[250:] = np.linspace(25, 0, 50)
    speed_hill = np.clip(speed_hill, 0, 35)
    grade_hill = np.full(len(t_hill), 8.0)  # 8% grade

    filepath = os.path.join(DATA_DIR, "drive_cycles", "hill_climb.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "speed_kmh", "road_grade_pct"])
        for i in range(len(t_hill)):
            writer.writerow([f"{t_hill[i]}", f"{speed_hill[i]:.1f}", f"{grade_hill[i]:.1f}"])


def generate_thermal_data():
    """Generate thermal reference data."""
    print("6. Generating thermal reference data...")

    thermal = {
        "convection_coefficients": {
            "natural_air_horizontal": {"h_W_m2K": 10, "range": [5, 15]},
            "forced_air_low_speed": {"h_W_m2K": 25, "range": [15, 40]},
            "forced_air_high_speed": {"h_W_m2K": 80, "range": [50, 120]},
            "natural_air_vertical": {"h_W_m2K": 12, "range": [8, 18]}
        },
        "thermal_conductivities_W_mK": {
            "copper": 401, "aluminum": 237, "steel_1010": 51.9,
            "silicon_steel_M19": 25, "NdFeB_magnet": 9,
            "epoxy_potting": 0.8, "slot_liner_nomex": 0.14,
            "air": 0.026, "thermal_grease": 3.0,
            "winding_impregnation": 1.2
        },
        "specific_heat_J_kgK": {
            "copper": 385, "aluminum": 897, "steel": 502,
            "silicon_steel": 480, "NdFeB": 450, "epoxy": 1100
        },
        "emissivity": {
            "black_anodized_aluminum": 0.85,
            "polished_aluminum": 0.05,
            "painted_steel": 0.90,
            "bare_copper": 0.07,
            "winding_varnish": 0.93
        },
        "insulation_classes": {
            "Class_A": {"max_temp_C": 105, "hot_spot_margin_C": 10},
            "Class_B": {"max_temp_C": 130, "hot_spot_margin_C": 10},
            "Class_F": {"max_temp_C": 155, "hot_spot_margin_C": 10},
            "Class_H": {"max_temp_C": 180, "hot_spot_margin_C": 15}
        },
        "scooter_vehicle_params": {
            "total_mass_kg": 150,
            "rider_mass_kg": 75,
            "wheel_radius_m": 0.20,
            "frontal_area_m2": 0.6,
            "Cd": 0.9,
            "Crr": 0.015,
            "gear_ratio": 8.5,
            "transmission_efficiency": 0.95
        }
    }

    with open(os.path.join(DATA_DIR, "thermal.json"), 'w') as f:
        json.dump(thermal, f, indent=2)


def generate_pole_slot_configs():
    """Generate common BLDC pole/slot configurations with winding factors."""
    print("7. Generating pole/slot configurations...")

    configs = [
        {"poles": 4, "slots": 6, "q": 0.5, "kw1": 0.866, "cogging_lcm": 12,
         "winding": "concentrated", "layers": 2},
        {"poles": 6, "slots": 9, "q": 0.5, "kw1": 0.866, "cogging_lcm": 18,
         "winding": "concentrated", "layers": 2},
        {"poles": 8, "slots": 9, "q": 0.375, "kw1": 0.945, "cogging_lcm": 72,
         "winding": "concentrated", "layers": 2},
        {"poles": 8, "slots": 12, "q": 0.5, "kw1": 0.866, "cogging_lcm": 24,
         "winding": "concentrated", "layers": 2},
        {"poles": 10, "slots": 12, "q": 0.4, "kw1": 0.933, "cogging_lcm": 60,
         "winding": "concentrated", "layers": 2},
        {"poles": 12, "slots": 18, "q": 0.5, "kw1": 0.866, "cogging_lcm": 36,
         "winding": "concentrated", "layers": 2},
        {"poles": 14, "slots": 12, "q": 0.286, "kw1": 0.933, "cogging_lcm": 84,
         "winding": "concentrated", "layers": 2},
        {"poles": 16, "slots": 18, "q": 0.375, "kw1": 0.945, "cogging_lcm": 144,
         "winding": "concentrated", "layers": 2},
        {"poles": 20, "slots": 24, "q": 0.4, "kw1": 0.933, "cogging_lcm": 120,
         "winding": "concentrated", "layers": 2},
    ]

    for cfg in configs:
        # Electrical frequency at rated speed (4000 RPM)
        cfg["f_e_Hz_at_4000rpm"] = cfg["poles"] / 2 * 4000 / 60
        # Torque ripple index (lower LCM → more cogging)
        cfg["cogging_index"] = cfg["cogging_lcm"] / (cfg["poles"] * cfg["slots"])

    with open(os.path.join(DATA_DIR, "pole_slot_configs.json"), 'w') as f:
        json.dump({
            "configurations": configs,
            "notes": {
                "q": "Slots per pole per phase",
                "kw1": "Fundamental winding factor",
                "cogging_lcm": "LCM of poles and slots (higher = less cogging)"
            }
        }, f, indent=2)


def main():
    print("Generating MotorForge reference data...")
    print("=" * 50)

    ensure_dirs()
    generate_magnet_data()
    generate_lamination_data()
    generate_wire_table()
    generate_bearing_data()
    generate_drive_cycles()
    generate_thermal_data()
    generate_pole_slot_configs()

    print(f"\nData generated in: {DATA_DIR}")
    print("  - magnets/: 5 NdFeB grades + BH curves")
    print("  - laminations/: 4 electrical steels (BH curves + losses)")
    print("  - wire_table.csv: Magnet wire gauge reference")
    print("  - bearings.json: Motor bearing catalog")
    print("  - drive_cycles/: 3 scooter drive profiles")
    print("  - thermal.json: Thermal properties reference")
    print("  - pole_slot_configs.json: BLDC configurations")
    print("\nDone!")


if __name__ == "__main__":
    main()
