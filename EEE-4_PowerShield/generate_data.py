"""
Generate reference data for EEE-4: PowerShield — Solid-State Circuit Breaker for DC Microgrids

Creates:
  data/semiconductors/    - SiC MOSFET and IGBT device datasheets (SOA, switching, thermal)
  data/snubber/           - MOV characteristics, TVS diode data
  data/gate_drivers.json  - Isolated gate driver IC catalog
  data/fault_scenarios/   - DC microgrid fault current waveforms
  data/thermal/           - Heatsink catalog, thermal interface materials
  data/standards.json     - Relevant standards and test requirements
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
    for sub in ["semiconductors", "snubber", "fault_scenarios", "thermal"]:
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)


def generate_semiconductor_data():
    """Generate SiC MOSFET and IGBT device data."""
    print("1. Generating semiconductor device data...")

    devices = [
        {
            "part_number": "C3M0075120K",
            "type": "SiC MOSFET",
            "manufacturer": "Wolfspeed",
            "Vds_max_V": 1200, "Id_cont_A": 30, "Id_pulse_A": 300,
            "Rds_on_mOhm_25C": 75, "Rds_on_mOhm_150C": 120,
            "Qg_nC": 120, "Ciss_pF": 3500, "Coss_pF": 200, "Crss_pF": 15,
            "td_on_ns": 15, "tr_ns": 22, "td_off_ns": 20, "tf_ns": 15,
            "Eon_uJ": 280, "Eoff_uJ": 90,
            "Vgs_max_V": 25, "Vgs_th_V": 2.5,
            "Tj_max_C": 175, "Rth_jc_C_W": 0.5,
            "package": "TO-247-3", "cost_usd": 15
        },
        {
            "part_number": "C3M0021120K",
            "type": "SiC MOSFET",
            "manufacturer": "Wolfspeed",
            "Vds_max_V": 1200, "Id_cont_A": 60, "Id_pulse_A": 500,
            "Rds_on_mOhm_25C": 21, "Rds_on_mOhm_150C": 36,
            "Qg_nC": 65, "Ciss_pF": 1900, "Coss_pF": 115, "Crss_pF": 9,
            "td_on_ns": 12, "tr_ns": 18, "td_off_ns": 18, "tf_ns": 12,
            "Eon_uJ": 190, "Eoff_uJ": 60,
            "Vgs_max_V": 25, "Vgs_th_V": 2.5,
            "Tj_max_C": 175, "Rth_jc_C_W": 0.3,
            "package": "TO-247-3", "cost_usd": 25
        },
        {
            "part_number": "IMW120R045M1H",
            "type": "SiC MOSFET",
            "manufacturer": "Infineon",
            "Vds_max_V": 1200, "Id_cont_A": 45, "Id_pulse_A": 400,
            "Rds_on_mOhm_25C": 45, "Rds_on_mOhm_150C": 72,
            "Qg_nC": 85, "Ciss_pF": 2400, "Coss_pF": 150, "Crss_pF": 12,
            "td_on_ns": 14, "tr_ns": 20, "td_off_ns": 19, "tf_ns": 14,
            "Eon_uJ": 230, "Eoff_uJ": 75,
            "Vgs_max_V": 25, "Vgs_th_V": 4.0,
            "Tj_max_C": 175, "Rth_jc_C_W": 0.4,
            "package": "TO-247-3", "cost_usd": 20
        },
        {
            "part_number": "CAB450M12XM3",
            "type": "SiC MOSFET Module",
            "manufacturer": "Wolfspeed",
            "Vds_max_V": 1200, "Id_cont_A": 450, "Id_pulse_A": 900,
            "Rds_on_mOhm_25C": 3.2, "Rds_on_mOhm_150C": 5.5,
            "Qg_nC": 1400, "Ciss_pF": 45000, "Coss_pF": 3000, "Crss_pF": 100,
            "td_on_ns": 60, "tr_ns": 40, "td_off_ns": 80, "tf_ns": 30,
            "Eon_uJ": 4500, "Eoff_uJ": 2000,
            "Vgs_max_V": 25, "Vgs_th_V": 2.5,
            "Tj_max_C": 175, "Rth_jc_C_W": 0.06,
            "package": "XM3", "cost_usd": 350
        },
        {
            "part_number": "FGH40N120AN",
            "type": "IGBT",
            "manufacturer": "ON Semi",
            "Vds_max_V": 1200, "Id_cont_A": 40, "Id_pulse_A": 200,
            "Rds_on_mOhm_25C": None, "Rds_on_mOhm_150C": None,
            "Vce_sat_V_25C": 2.1, "Vce_sat_V_150C": 2.5,
            "Qg_nC": 180, "Ciss_pF": 5500, "Coss_pF": 90, "Crss_pF": 35,
            "td_on_ns": 30, "tr_ns": 25, "td_off_ns": 200, "tf_ns": 150,
            "Eon_uJ": 1200, "Eoff_uJ": 800,
            "Vgs_max_V": 20, "Vgs_th_V": 5.5,
            "Tj_max_C": 175, "Rth_jc_C_W": 0.42,
            "package": "TO-247-3", "cost_usd": 8,
            "note": "IGBT for comparison — too slow for SSCB"
        },
    ]

    with open(os.path.join(DATA_DIR, "semiconductors", "catalog.json"), 'w') as f:
        json.dump({"devices": devices}, f, indent=2)

    # Generate SOA (Safe Operating Area) curves for each SiC device
    for dev in devices:
        if dev["type"] == "IGBT":
            continue
        Vds = np.array([1, 10, 50, 100, 200, 400, 600, 800, 1000, 1200])
        # DC SOA limit
        Id_dc = np.minimum(dev["Id_cont_A"], dev["Tj_max_C"] / (dev["Rth_jc_C_W"] * dev["Rds_on_mOhm_25C"] / 1000) / Vds)
        Id_dc = np.clip(Id_dc, 0, dev["Id_pulse_A"])
        # Pulse SOA (10us, 100us, 1ms)
        Id_10us = np.minimum(dev["Id_pulse_A"], Id_dc * 10)
        Id_100us = np.minimum(dev["Id_pulse_A"], Id_dc * 5)
        Id_1ms = np.minimum(dev["Id_pulse_A"], Id_dc * 2)

        filepath = os.path.join(DATA_DIR, "semiconductors", f"{dev['part_number']}_SOA.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Vds_V", "Id_DC_A", "Id_10us_A", "Id_100us_A", "Id_1ms_A"])
            for i in range(len(Vds)):
                writer.writerow([f"{Vds[i]}", f"{Id_dc[i]:.1f}", f"{Id_10us[i]:.0f}",
                               f"{Id_100us[i]:.0f}", f"{Id_1ms[i]:.0f}"])

    # Rds(on) vs temperature curves
    for dev in devices:
        if dev["Rds_on_mOhm_25C"] is None:
            continue
        temps = np.arange(-40, 200, 10)
        # SiC has positive temp coefficient
        Rds = dev["Rds_on_mOhm_25C"] * (1 + 0.004 * (temps - 25))
        Rds = np.clip(Rds, dev["Rds_on_mOhm_25C"] * 0.8, dev["Rds_on_mOhm_25C"] * 2.0)

        filepath = os.path.join(DATA_DIR, "semiconductors", f"{dev['part_number']}_RdsVsTemp.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["temperature_C", "Rds_on_mOhm"])
            for i in range(len(temps)):
                writer.writerow([f"{temps[i]}", f"{Rds[i]:.1f}"])


def generate_snubber_data():
    """Generate MOV and TVS diode reference data."""
    print("2. Generating snubber/clamping component data...")

    # MOV characteristics
    movs = [
        {"part": "V510LA40A", "Vclamp_V": 510, "Vpk_V": 650, "energy_J": 210,
         "capacitance_pF": 3500, "peak_current_A": 6500, "response_ns": 25},
        {"part": "V575LA80A", "Vclamp_V": 575, "Vpk_V": 745, "energy_J": 400,
         "capacitance_pF": 4000, "peak_current_A": 10000, "response_ns": 25},
        {"part": "V625LA80A", "Vclamp_V": 625, "Vpk_V": 810, "energy_J": 500,
         "capacitance_pF": 4200, "peak_current_A": 10000, "response_ns": 25},
    ]

    # TVS diodes
    tvs = [
        {"part": "SMDJ440A", "Vbr_V": 440, "Vclamp_V": 550, "peak_power_kW": 3,
         "peak_current_A": 5.5, "capacitance_pF": 800},
        {"part": "1.5KE440A", "Vbr_V": 440, "Vclamp_V": 600, "peak_power_kW": 1.5,
         "peak_current_A": 2.5, "capacitance_pF": 400},
        {"part": "5KP440A", "Vbr_V": 440, "Vclamp_V": 560, "peak_power_kW": 5,
         "peak_current_A": 8.9, "capacitance_pF": 1500},
    ]

    # MOV V-I characteristic curves
    for mov in movs:
        I = np.logspace(-3, 4, 50)  # 1mA to 10kA
        # Simplified V-I: V = V_clamp * (I / I_ref)^alpha
        alpha = 0.04  # MOV nonlinearity exponent
        V = mov["Vclamp_V"] * (I / 1.0) ** alpha
        V = np.clip(V, mov["Vclamp_V"] * 0.7, mov["Vpk_V"])

        filepath = os.path.join(DATA_DIR, "snubber", f"{mov['part']}_VI.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["current_A", "voltage_V"])
            for i in range(len(I)):
                writer.writerow([f"{I[i]:.4f}", f"{V[i]:.1f}"])

    with open(os.path.join(DATA_DIR, "snubber", "catalog.json"), 'w') as f:
        json.dump({"MOVs": movs, "TVS_diodes": tvs}, f, indent=2)


def generate_gate_driver_data():
    """Generate isolated gate driver catalog."""
    print("3. Generating gate driver catalog...")

    drivers = {
        "gate_drivers": [
            {
                "part": "UCC21710", "manufacturer": "TI",
                "isolation_kV": 5.7, "peak_source_A": 10, "peak_sink_A": 10,
                "propagation_delay_ns": 50, "delay_matching_ns": 5,
                "CMTI_kV_us": 200, "Vcc_range_V": [15, 30],
                "features": ["DESAT protection", "Active Miller clamp", "Fault reporting",
                             "Soft turn-off"],
                "cost_usd": 6.5, "package": "SOIC-16"
            },
            {
                "part": "ACPL-W346", "manufacturer": "Broadcom",
                "isolation_kV": 5.0, "peak_source_A": 4, "peak_sink_A": 4,
                "propagation_delay_ns": 120, "delay_matching_ns": 25,
                "CMTI_kV_us": 50, "Vcc_range_V": [15, 30],
                "features": ["Optocoupler isolation", "DESAT input"],
                "cost_usd": 3.5, "package": "SO-8"
            },
            {
                "part": "SI8271GB", "manufacturer": "Skyworks",
                "isolation_kV": 5.0, "peak_source_A": 4, "peak_sink_A": 4,
                "propagation_delay_ns": 35, "delay_matching_ns": 3,
                "CMTI_kV_us": 300, "Vcc_range_V": [6.5, 30],
                "features": ["Capacitive isolation", "Integrated bootstrap"],
                "cost_usd": 2.5, "package": "SOIC-8"
            },
            {
                "part": "CGD15HB62LP", "manufacturer": "Wolfspeed",
                "isolation_kV": 5.7, "peak_source_A": 10, "peak_sink_A": 10,
                "propagation_delay_ns": 55, "delay_matching_ns": 8,
                "CMTI_kV_us": 200, "Vcc_range_V": [15, 25],
                "features": ["Designed for SiC", "DESAT with soft turn-off",
                             "Active Miller clamp", "UVLO"],
                "cost_usd": 12.0, "package": "PCB module"
            },
        ],
        "design_notes": {
            "Vgs_recommended_SiC": "+20V / -5V",
            "gate_resistor_guideline": "Rg_on = Vgs / I_peak_source, Rg_off = Vgs / I_peak_sink",
            "bootstrap_capacitor": "C_boot > 10 * Qg for reliable turn-on"
        }
    }

    with open(os.path.join(DATA_DIR, "gate_drivers.json"), 'w') as f:
        json.dump(drivers, f, indent=2)


def generate_fault_scenarios():
    """Generate DC microgrid fault current waveforms."""
    print("4. Generating fault scenario waveforms...")

    dt = 1e-7  # 100ns time step
    t_total = 1e-3  # 1ms simulation
    t = np.arange(0, t_total, dt)

    scenarios = [
        {"name": "bolted_short_circuit", "R_fault_Ohm": 0.001, "L_line_uH": 50,
         "description": "Bolted short circuit at bus terminals"},
        {"name": "cable_fault_5m", "R_fault_Ohm": 0.01, "L_line_uH": 200,
         "description": "Short circuit through 5m cable"},
        {"name": "cable_fault_20m", "R_fault_Ohm": 0.05, "L_line_uH": 800,
         "description": "Short circuit through 20m cable"},
        {"name": "high_impedance_fault", "R_fault_Ohm": 1.0, "L_line_uH": 200,
         "description": "High impedance ground fault"},
        {"name": "arc_fault", "R_fault_Ohm": 0.1, "L_line_uH": 300,
         "description": "Arc fault with variable resistance"},
    ]

    V_bus = 400  # V
    R_source = 0.005  # Source resistance
    C_bus = 2000e-6  # Bus capacitance 2000uF

    for scenario in scenarios:
        R_f = scenario["R_fault_Ohm"]
        L = scenario["L_line_uH"] * 1e-6

        # Fault current: i(t) = V_bus / (R_total) * (1 - exp(-R_total * t / L))
        R_total = R_source + R_f
        I_fault = np.zeros_like(t)

        # Pre-fault: normal operation at 200A
        fault_start_idx = int(100e-6 / dt)  # Fault at 100us

        I_fault[:fault_start_idx] = 200  # Normal load current

        for i in range(fault_start_idx, len(t)):
            t_fault = (i - fault_start_idx) * dt

            if scenario["name"] == "arc_fault":
                # Arc fault: oscillating resistance
                R_arc = R_f * (1 + 0.5 * np.sin(2 * np.pi * 50000 * t_fault))
                R_total_arc = R_source + R_arc
                I_fault[i] = V_bus / R_total_arc * (1 - np.exp(-R_total_arc * t_fault / L))
            else:
                I_fault[i] = V_bus / R_total * (1 - np.exp(-R_total * t_fault / L))

            # Add capacitor discharge contribution
            I_cap = (V_bus / (R_total + 0.001)) * np.exp(-t_fault / (R_total * C_bus))
            I_fault[i] += I_cap * 0.3  # Partial contribution

        # Add noise
        I_fault += np.random.randn(len(t)) * 2

        # Bus voltage during fault
        V_bus_t = np.full_like(t, V_bus)
        V_bus_t[fault_start_idx:] = V_bus * np.exp(
            -(t[fault_start_idx:] - t[fault_start_idx]) / (R_total * C_bus)
        )

        filepath = os.path.join(DATA_DIR, "fault_scenarios", f"{scenario['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_us", "current_A", "voltage_V", "di_dt_A_us"])
            for i in range(0, len(t), 10):  # Downsample 10x
                di_dt = (I_fault[min(i + 1, len(t) - 1)] - I_fault[i]) / dt / 1e6
                writer.writerow([
                    f"{t[i] * 1e6:.2f}",
                    f"{I_fault[i]:.1f}",
                    f"{V_bus_t[i]:.1f}",
                    f"{di_dt:.1f}"
                ])

        scenario["peak_current_A"] = float(np.max(I_fault))
        scenario["di_dt_max_A_us"] = float(np.max(np.diff(I_fault) / dt / 1e6))
        scenario["file"] = f"fault_scenarios/{scenario['name']}.csv"

    with open(os.path.join(DATA_DIR, "fault_scenarios", "scenarios.json"), 'w') as f:
        json.dump({
            "bus_voltage_V": V_bus,
            "rated_current_A": 200,
            "bus_capacitance_uF": C_bus * 1e6,
            "scenarios": scenarios
        }, f, indent=2)


def generate_thermal_data():
    """Generate heatsink catalog and thermal interface materials."""
    print("5. Generating thermal data...")

    heatsinks = [
        {
            "model": "HS-AL-200x100-NatConv",
            "type": "natural_convection",
            "material": "Aluminum 6063-T5",
            "dimensions_mm": {"L": 200, "W": 100, "H": 50},
            "fin_count": 15, "fin_height_mm": 40,
            "Rth_sa_C_W": 0.8,
            "mass_g": 450, "cost_usd": 12
        },
        {
            "model": "HS-AL-200x100-ForcedAir",
            "type": "forced_air",
            "material": "Aluminum 6063-T5",
            "dimensions_mm": {"L": 200, "W": 100, "H": 50},
            "fin_count": 25, "fin_height_mm": 40,
            "Rth_sa_C_W": 0.25,
            "fan_required": "80mm, 3000 RPM",
            "mass_g": 550, "cost_usd": 25
        },
        {
            "model": "HS-CU-120x60-Liquid",
            "type": "liquid_cooled",
            "material": "Copper",
            "dimensions_mm": {"L": 120, "W": 60, "H": 20},
            "Rth_sa_C_W": 0.05,
            "flow_rate_lpm": 2.0,
            "mass_g": 800, "cost_usd": 85
        },
    ]

    tims = [
        {"name": "Thermal Pad (soft)", "Rth_C_W_cm2": 0.50, "thickness_mm": 1.0,
         "k_W_mK": 2.0, "cost_per_pad_usd": 0.5},
        {"name": "Thermal Grease (standard)", "Rth_C_W_cm2": 0.20, "thickness_mm": 0.05,
         "k_W_mK": 3.0, "cost_per_tube_usd": 5.0},
        {"name": "Thermal Grease (high performance)", "Rth_C_W_cm2": 0.08, "thickness_mm": 0.03,
         "k_W_mK": 8.0, "cost_per_tube_usd": 15.0},
        {"name": "Solder (direct die attach)", "Rth_C_W_cm2": 0.02, "thickness_mm": 0.10,
         "k_W_mK": 50.0, "cost_usd": "assembly dependent"},
    ]

    with open(os.path.join(DATA_DIR, "thermal", "catalog.json"), 'w') as f:
        json.dump({
            "heatsinks": heatsinks,
            "thermal_interface_materials": tims
        }, f, indent=2)

    # Transient thermal impedance curves (Zth_jc) for reference device
    t_pulse = np.logspace(-6, 1, 50)  # 1us to 10s
    # Foster network approximation: 4 RC pairs
    R_vals = [0.05, 0.10, 0.15, 0.20]
    tau_vals = [1e-4, 1e-3, 1e-2, 1e-1]

    Zth = np.zeros_like(t_pulse)
    for R, tau in zip(R_vals, tau_vals):
        Zth += R * (1 - np.exp(-t_pulse / tau))

    filepath = os.path.join(DATA_DIR, "thermal", "transient_Zth.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["pulse_duration_s", "Zth_jc_C_W"])
        for i in range(len(t_pulse)):
            writer.writerow([f"{t_pulse[i]:.6e}", f"{Zth[i]:.4f}"])


def generate_standards():
    """Generate relevant standards reference."""
    print("6. Generating standards reference...")

    standards = {
        "applicable_standards": [
            {
                "standard": "IEC 60947-2",
                "title": "Low-voltage switchgear and controlgear - Circuit-breakers",
                "key_requirements": [
                    "Making and breaking capacity tests",
                    "Short-time withstand current",
                    "Overload trip characteristics"
                ]
            },
            {
                "standard": "IEC 62271-100",
                "title": "High-voltage switchgear - AC circuit-breakers",
                "relevance": "Reference for breaking capacity test methodology"
            },
            {
                "standard": "UL 489B",
                "title": "Molded-Case Circuit Breakers, Molded-Case Switches and Circuit-Breaker Enclosures",
                "relevance": "North American safety standard"
            },
            {
                "standard": "IEC 61000-4-5",
                "title": "Surge immunity test",
                "relevance": "Voltage transient limits"
            }
        ],
        "dc_microgrid_standards": [
            {
                "standard": "IEEE 2030.10",
                "title": "Standard for DC Microgrids for Rural and Remote Electricity Access",
                "voltage_levels_V": [48, 380, 750, 1500]
            }
        ],
        "test_requirements": {
            "breaking_capacity_test": {
                "voltage_V": 400,
                "prospective_fault_A": 10000,
                "power_factor": "N/A (DC)",
                "num_operations": 3,
                "time_constant_ms": 15
            },
            "endurance_test": {
                "rated_current_A": 200,
                "num_cycles": 10000,
                "duty_cycle": "1s on / 9s off"
            },
            "temperature_rise_test": {
                "rated_current_A": 200,
                "max_terminal_rise_C": 65,
                "ambient_C": 40
            }
        }
    }

    with open(os.path.join(DATA_DIR, "standards.json"), 'w') as f:
        json.dump(standards, f, indent=2)


def main():
    print("Generating PowerShield reference data...")
    print("=" * 50)

    ensure_dirs()
    generate_semiconductor_data()
    generate_snubber_data()
    generate_gate_driver_data()
    generate_fault_scenarios()
    generate_thermal_data()
    generate_standards()

    print(f"\nData generated in: {DATA_DIR}")
    print("  - semiconductors/: 5 devices (SiC + IGBT) with SOA + Rds vs temp")
    print("  - snubber/: MOV catalog with V-I curves + TVS diodes")
    print("  - gate_drivers.json: 4 isolated gate driver ICs")
    print("  - fault_scenarios/: 5 DC fault waveforms (current + voltage)")
    print("  - thermal/: Heatsink catalog + TIMs + Zth curve")
    print("  - standards.json: Test requirements reference")
    print("\nDone!")


if __name__ == "__main__":
    main()
