"""
ChipCraft - Generate simulation data for biomedical AFE ASIC design

Generates:
- Process technology (PDK) parameters for 180nm CMOS
- Sample ECG waveform data
- Sample PPG waveform data
- Noise measurement references
- Component/transistor model parameters
"""

import numpy as np
import json
import os
import csv

SEED = 42
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def generate_process_parameters():
    """Generate 180nm CMOS process technology parameters."""
    os.makedirs(os.path.join(DATA_DIR, "process"), exist_ok=True)
    
    pdk = {
        "technology": "180nm Generic CMOS",
        "node": "0.18um",
        "supply_voltage_v": 1.8,
        "nmos": {
            "vth_nom_v": 0.45,
            "vth_sigma_mv": 15,
            "kp_ua_v2": 270,
            "lambda_v_inv": 0.04,
            "cox_ff_um2": 8.6,
            "mu_cm2_vs": 450,
            "tox_nm": 4.0,
            "min_length_um": 0.18,
            "min_width_um": 0.22,
            "gm_id_table": {
                "weak_inversion": {"gm_id_range": [20, 28], "id_w_ua_um": [0.01, 0.1]},
                "moderate_inversion": {"gm_id_range": [12, 20], "id_w_ua_um": [0.1, 1.0]},
                "strong_inversion": {"gm_id_range": [5, 12], "id_w_ua_um": [1.0, 50.0]},
            },
            "noise": {
                "thermal_gamma": 0.67,
                "flicker_kf": 4e-25,
                "flicker_af": 1.0,
                "flicker_ef": 1.0,
            },
        },
        "pmos": {
            "vth_nom_v": -0.45,
            "vth_sigma_mv": 18,
            "kp_ua_v2": 70,
            "lambda_v_inv": 0.05,
            "cox_ff_um2": 8.6,
            "mu_cm2_vs": 120,
            "tox_nm": 4.0,
            "min_length_um": 0.18,
            "min_width_um": 0.22,
            "gm_id_table": {
                "weak_inversion": {"gm_id_range": [20, 28], "id_w_ua_um": [0.005, 0.05]},
                "moderate_inversion": {"gm_id_range": [12, 20], "id_w_ua_um": [0.05, 0.5]},
                "strong_inversion": {"gm_id_range": [5, 12], "id_w_ua_um": [0.5, 20.0]},
            },
            "noise": {
                "thermal_gamma": 0.67,
                "flicker_kf": 1.5e-24,
                "flicker_af": 1.0,
                "flicker_ef": 1.0,
            },
        },
        "resistors": {
            "poly_high_r": {"sheet_r_ohm_sq": 1000, "tc_ppm_c": 1500, "matching_percent_um": 0.5},
            "poly_r": {"sheet_r_ohm_sq": 200, "tc_ppm_c": 800, "matching_percent_um": 0.3},
            "nwell_r": {"sheet_r_ohm_sq": 600, "tc_ppm_c": 3000, "matching_percent_um": 1.0},
            "diffusion_r": {"sheet_r_ohm_sq": 100, "tc_ppm_c": 1500, "matching_percent_um": 0.5},
        },
        "capacitors": {
            "mim_cap": {"density_ff_um2": 1.0, "tc_ppm_c": 30, "matching_percent_um": 0.1,
                        "voltage_coeff_ppm_v": 50},
            "poly_cap": {"density_ff_um2": 0.7, "tc_ppm_c": 20, "matching_percent_um": 0.15,
                         "voltage_coeff_ppm_v": 100},
            "mos_cap": {"density_ff_um2": 8.6, "tc_ppm_c": 100, "matching_percent_um": 0.3,
                        "voltage_coeff_ppm_v": 500},
        },
        "bjt": {
            "npn_vertical": {"beta": 100, "va_v": 50, "is_a": 5e-18,
                            "area_um2": 4, "re_ohm": 5},
            "pnp_lateral": {"beta": 10, "va_v": 20, "is_a": 2e-18,
                           "area_um2": 16, "re_ohm": 50},
        },
    }
    
    with open(os.path.join(DATA_DIR, "process", "pdk_parameters.json"), 'w') as f:
        json.dump(pdk, f, indent=2)
    
    # gm/Id lookup table (NMOS)
    gm_id_values = np.arange(5, 29, 0.5)
    id_w = np.zeros_like(gm_id_values)
    ft = np.zeros_like(gm_id_values)
    
    for i, gm_id in enumerate(gm_id_values):
        if gm_id > 20:  # Weak inversion
            id_w[i] = 0.01 * np.exp((gm_id - 20) * 0.15)
        elif gm_id > 12:  # Moderate inversion
            denom = max((20 - gm_id) / 8, 1e-6)
            id_w[i] = 0.1 * denom ** (-1.5) * 0.1
        else:  # Strong inversion
            denom = max((12 - gm_id) / 7, 1e-6)
            id_w[i] = 1.0 * denom ** (-2) * 1.0
        
        gm = gm_id * id_w[i] * 1e-6  # A/V
        cgs = 2/3 * 8.6e-15 * 0.18 * 1  # F (W=1um, L=0.18um)
        ft[i] = gm / (2 * np.pi * cgs) / 1e9  # GHz
    
    filepath = os.path.join(DATA_DIR, "process", "gm_id_lookup_nmos.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["gm_id_v_inv", "id_w_ua_um", "ft_ghz", "vdsat_mv"])
        for i in range(len(gm_id_values)):
            vdsat = 2 / gm_id_values[i] * 1000  # mV
            writer.writerow([f"{gm_id_values[i]:.1f}", f"{id_w[i]:.4f}",
                           f"{ft[i]:.2f}", f"{vdsat:.0f}"])
    
    return pdk


def generate_ecg_signals():
    """Generate realistic ECG waveform data."""
    os.makedirs(os.path.join(DATA_DIR, "signals"), exist_ok=True)
    
    fs = 1000  # 1 kHz sampling rate
    duration = 30  # 30 seconds
    N = fs * duration
    t = np.arange(N) / fs
    
    scenarios = []
    
    ecg_types = [
        {"name": "normal_sinus", "heart_rate_bpm": 72, "amplitude_mv": 1.0,
         "noise_uv": 10, "dc_offset_mv": 300, "description": "Normal sinus rhythm"},
        {"name": "tachycardia", "heart_rate_bpm": 120, "amplitude_mv": 0.8,
         "noise_uv": 15, "dc_offset_mv": 250, "description": "Sinus tachycardia"},
        {"name": "bradycardia", "heart_rate_bpm": 48, "amplitude_mv": 1.2,
         "noise_uv": 8, "dc_offset_mv": 350, "description": "Sinus bradycardia"},
        {"name": "noisy_motion", "heart_rate_bpm": 80, "amplitude_mv": 1.0,
         "noise_uv": 50, "dc_offset_mv": 300, "description": "Motion artifact contaminated"},
        {"name": "low_amplitude", "heart_rate_bpm": 70, "amplitude_mv": 0.3,
         "noise_uv": 5, "dc_offset_mv": 280, "description": "Low amplitude ECG"},
        {"name": "electrode_pop", "heart_rate_bpm": 75, "amplitude_mv": 1.0,
         "noise_uv": 10, "dc_offset_mv": 300, "description": "Intermittent electrode contact"},
    ]
    
    for ecg_type in ecg_types:
        hr = ecg_type["heart_rate_bpm"]
        amp = ecg_type["amplitude_mv"]
        rr_interval = 60.0 / hr
        
        ecg = np.zeros(N)
        
        # Generate PQRST complexes
        beat_times = np.arange(0, duration, rr_interval)
        # Add heart rate variability
        beat_times += np.cumsum(np.random.randn(len(beat_times)) * 0.02)
        
        for bt in beat_times:
            idx = int(bt * fs)
            if idx + int(0.6 * fs) >= N:
                break
            
            # P wave
            p_center = idx + int(0.06 * fs)
            p_width = int(0.04 * fs)
            if 0 <= p_center < N:
                p_range = np.arange(max(0, p_center - p_width), min(N, p_center + p_width))
                ecg[p_range] += 0.1 * amp * np.exp(-((p_range - p_center) / (p_width/2))**2)
            
            # QRS complex
            q_center = idx + int(0.12 * fs)
            if 0 <= q_center < N and q_center + int(0.03 * fs) < N:
                q_range = np.arange(q_center, min(N, q_center + int(0.015 * fs)))
                ecg[q_range] -= 0.1 * amp * np.sin(np.pi * np.arange(len(q_range)) / len(q_range))
            
            r_center = idx + int(0.14 * fs)
            r_width = int(0.012 * fs)
            if 0 <= r_center < N:
                r_range = np.arange(max(0, r_center - r_width), min(N, r_center + r_width))
                ecg[r_range] += amp * np.exp(-((r_range - r_center) / (r_width/2))**2)
            
            s_center = idx + int(0.16 * fs)
            if 0 <= s_center < N and s_center + int(0.02 * fs) < N:
                s_range = np.arange(s_center, min(N, s_center + int(0.02 * fs)))
                ecg[s_range] -= 0.15 * amp * np.exp(-np.arange(len(s_range)) / (len(s_range)/3))
            
            # T wave
            t_center = idx + int(0.3 * fs)
            t_width = int(0.08 * fs)
            if 0 <= t_center < N:
                t_range = np.arange(max(0, t_center - t_width), min(N, t_center + t_width))
                ecg[t_range] += 0.3 * amp * np.exp(-((t_range - t_center) / (t_width/2))**2)
        
        # Add DC offset
        ecg += ecg_type["dc_offset_mv"]
        
        # Add noise
        noise = np.random.randn(N) * ecg_type["noise_uv"] / 1000  # Convert uV to mV
        
        # Add 50/60 Hz powerline interference
        powerline = 0.02 * amp * np.sin(2 * np.pi * 50 * t)
        
        # Add baseline wander
        baseline = 0.1 * amp * np.sin(2 * np.pi * 0.15 * t) + 0.05 * amp * np.sin(2 * np.pi * 0.3 * t)
        
        ecg_noisy = ecg + noise + powerline + baseline
        
        # Special artifacts
        if ecg_type["name"] == "noisy_motion":
            # Add motion artifacts (large, low-frequency)
            motion_times = np.random.uniform(5, 25, 5)
            for mt in motion_times:
                idx = int(mt * fs)
                width = int(np.random.uniform(0.2, 1.0) * fs)
                end = min(idx + width, N)
                ecg_noisy[idx:end] += np.random.uniform(-2, 2) * amp * \
                    np.sin(np.pi * np.arange(end - idx) / (end - idx))
        
        if ecg_type["name"] == "electrode_pop":
            # Add electrode pop artifacts
            pop_times = np.random.uniform(3, 27, 8)
            for pt in pop_times:
                idx = int(pt * fs)
                if idx < N - 100:
                    ecg_noisy[idx:idx+50] += np.random.choice([-1, 1]) * 5 * amp
                    ecg_noisy[idx+50:idx+100] -= np.random.choice([-1, 1]) * 2 * amp
        
        filepath = os.path.join(DATA_DIR, "signals", f"ecg_{ecg_type['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "ecg_clean_mv", "ecg_noisy_mv"])
            for j in range(N):
                writer.writerow([f"{t[j]:.4f}", f"{ecg[j]:.6f}", f"{ecg_noisy[j]:.6f}"])
        
        scenarios.append({
            "name": ecg_type["name"],
            "description": ecg_type["description"],
            "heart_rate_bpm": hr,
            "amplitude_mv": amp,
            "noise_uv_rms": ecg_type["noise_uv"],
            "dc_offset_mv": ecg_type["dc_offset_mv"],
            "sampling_rate_hz": fs,
            "duration_s": duration,
        })
    
    return scenarios


def generate_ppg_signals():
    """Generate realistic PPG waveform data."""
    os.makedirs(os.path.join(DATA_DIR, "signals"), exist_ok=True)
    
    fs = 1000  # 1 kHz
    duration = 30  # 30 seconds
    N = fs * duration
    t = np.arange(N) / fs
    
    scenarios = []
    
    ppg_types = [
        {"name": "clean_finger", "dc_ua": 5.0, "ac_percent": 2.0,
         "heart_rate_bpm": 72, "ambient_ua": 0.5, "spo2": 98,
         "description": "Clean fingertip PPG, high perfusion"},
        {"name": "low_perfusion", "dc_ua": 1.0, "ac_percent": 0.5,
         "heart_rate_bpm": 80, "ambient_ua": 0.5, "spo2": 95,
         "description": "Low perfusion (cold extremities)"},
        {"name": "wrist_ppg", "dc_ua": 2.0, "ac_percent": 0.3,
         "heart_rate_bpm": 75, "ambient_ua": 2.0, "spo2": 97,
         "description": "Wrist-worn PPG (lower signal)"},
        {"name": "high_ambient", "dc_ua": 3.0, "ac_percent": 1.5,
         "heart_rate_bpm": 70, "ambient_ua": 8.0, "spo2": 98,
         "description": "High ambient light environment"},
        {"name": "motion_artifact", "dc_ua": 5.0, "ac_percent": 2.0,
         "heart_rate_bpm": 90, "ambient_ua": 1.0, "spo2": 96,
         "description": "Walking/exercise motion artifacts"},
    ]
    
    for ppg_type in ppg_types:
        hr = ppg_type["heart_rate_bpm"]
        dc = ppg_type["dc_ua"]
        ac_pct = ppg_type["ac_percent"]
        rr_interval = 60.0 / hr
        
        # Generate PPG waveform (sawtooth-like with dicrotic notch)
        ppg_ac = np.zeros(N)
        beat_times = np.arange(0, duration, rr_interval)
        beat_times += np.cumsum(np.random.randn(len(beat_times)) * 0.015)
        
        for i, bt in enumerate(beat_times):
            idx = int(bt * fs)
            if idx < 0:
                continue  # Skip beats with negative timing from jitter
            beat_len = int(rr_interval * fs)
            if idx + beat_len >= N:
                break
            
            beat_t = np.arange(beat_len) / fs
            # Systolic peak
            systolic = np.exp(-((beat_t - 0.1) / 0.06)**2)
            # Dicrotic notch and wave
            dicrotic = 0.3 * np.exp(-((beat_t - 0.35) / 0.08)**2)
            
            pulse = systolic + dicrotic
            pulse = pulse / np.max(pulse)  # Normalize
            
            end_idx = min(idx + beat_len, N)
            ppg_ac[idx:end_idx] += pulse[:end_idx - idx]
        
        # Scale AC component
        ac_amplitude = dc * ac_pct / 100
        ppg_signal = dc + ac_amplitude * ppg_ac
        
        # Add ambient light (DC + 100/120 Hz flicker)
        ambient = ppg_type["ambient_ua"] + 0.1 * ppg_type["ambient_ua"] * np.sin(2 * np.pi * 100 * t)
        
        # Add shot noise
        shot_noise = np.random.randn(N) * np.sqrt(2 * 1.6e-19 * (dc + ppg_type["ambient_ua"]) * 1e-6 * fs) / 1e-6
        
        ppg_total = ppg_signal + ambient + shot_noise
        
        # Add motion artifacts if applicable
        if ppg_type["name"] == "motion_artifact":
            motion = 0.5 * dc * np.sin(2 * np.pi * 1.8 * t)  # Walking frequency
            motion += 0.2 * dc * np.sin(2 * np.pi * 3.6 * t)  # Harmonic
            ppg_total += motion
        
        filepath = os.path.join(DATA_DIR, "signals", f"ppg_{ppg_type['name']}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "ppg_clean_ua", "ppg_with_ambient_ua",
                           "ambient_ua", "photodiode_total_ua"])
            for j in range(0, N, 1):  # Full 1kHz
                writer.writerow([f"{t[j]:.4f}", f"{ppg_signal[j]:.6f}",
                               f"{ppg_total[j]:.6f}", f"{ambient[j]:.6f}",
                               f"{ppg_total[j]:.6f}"])
        
        scenarios.append({
            "name": ppg_type["name"],
            "description": ppg_type["description"],
            "heart_rate_bpm": hr,
            "dc_current_ua": dc,
            "ac_percent": ac_pct,
            "ambient_light_ua": ppg_type["ambient_ua"],
            "spo2_percent": ppg_type["spo2"],
            "sampling_rate_hz": fs,
            "duration_s": duration,
        })
    
    return scenarios


def generate_noise_references():
    """Generate noise measurement reference data."""
    os.makedirs(os.path.join(DATA_DIR, "reference"), exist_ok=True)
    
    # Published AFE performance comparison
    published_designs = [
        {"paper": "Texas Instruments ADS1298", "year": 2012, "technology_nm": 180,
         "ecg_noise_uvrms": 4.0, "cmrr_db": 115, "power_uw": 750,
         "adc_bits": 24, "channels": 8, "sampling_rate_sps": 32000},
        {"paper": "Analog Devices AD8232", "year": 2013, "technology_nm": 500,
         "ecg_noise_uvrms": 14, "cmrr_db": 80, "power_uw": 340,
         "adc_bits": 0, "channels": 1, "sampling_rate_sps": 0},
        {"paper": "ISSCC 2018 - Samsung AFE", "year": 2018, "technology_nm": 65,
         "ecg_noise_uvrms": 1.3, "cmrr_db": 120, "power_uw": 120,
         "adc_bits": 16, "channels": 1, "sampling_rate_sps": 1000},
        {"paper": "JSSC 2020 - Low Power ECG", "year": 2020, "technology_nm": 180,
         "ecg_noise_uvrms": 2.8, "cmrr_db": 105, "power_uw": 200,
         "adc_bits": 16, "channels": 2, "sampling_rate_sps": 500},
        {"paper": "ISSCC 2021 - Wearable PPG/ECG", "year": 2021, "technology_nm": 55,
         "ecg_noise_uvrms": 0.9, "cmrr_db": 130, "power_uw": 85,
         "adc_bits": 18, "channels": 4, "sampling_rate_sps": 2000},
    ]
    
    with open(os.path.join(DATA_DIR, "reference", "published_designs.json"), 'w') as f:
        json.dump(published_designs, f, indent=2)
    
    # Noise floor targets
    noise_budget = {
        "ecg_channel": {
            "total_budget_uvrms": 5.0,
            "breakdown": {
                "instrumentation_amp": 2.5,
                "high_pass_filter": 1.0,
                "low_pass_filter": 0.5,
                "pga": 1.5,
                "adc_quantization": 1.0,
                "adc_thermal": 0.8,
                "power_supply_rejection": 0.5,
                "rss_total": 3.4,
            },
            "note": "RSS total should be < 5 uVrms budget"
        },
        "ppg_channel": {
            "total_budget_narms": 100,
            "breakdown": {
                "tia_thermal": 50,
                "tia_shot_noise": 30,
                "ambient_light_shot": 40,
                "adc_quantization": 20,
                "led_driver_noise": 15,
                "rss_total": 75,
            },
        },
    }
    
    with open(os.path.join(DATA_DIR, "reference", "noise_budget.json"), 'w') as f:
        json.dump(noise_budget, f, indent=2)
    
    return published_designs


def main():
    print("Generating ChipCraft simulation data...")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("1. Generating process technology parameters...")
    pdk = generate_process_parameters()
    
    print("2. Generating sample ECG signals (6 scenarios)...")
    ecg = generate_ecg_signals()
    
    print("3. Generating sample PPG signals (5 scenarios)...")
    ppg = generate_ppg_signals()
    
    print("4. Generating noise reference data...")
    refs = generate_noise_references()
    
    metadata = {
        "problem": "ECE-4 ChipCraft",
        "description": "Mixed-Signal ASIC Design for Biomedical Sensing",
        "design_targets": {
            "ecg_noise_uvrms": 5.0,
            "ecg_cmrr_db": 100,
            "ecg_input_impedance_gohm": 10,
            "ppg_snr_db": 60,
            "ppg_ambient_rejection_db": 80,
            "adc_resolution_bits": 16,
            "adc_enob_bits": 14,
            "total_power_uw": 500,
        },
        "data_contents": {
            "process": "180nm CMOS PDK parameters + gm/Id lookup",
            "signals": f"{len(ecg)} ECG scenarios + {len(ppg)} PPG scenarios",
            "reference": f"{len(refs)} published design comparisons + noise budget",
        },
        "seed": SEED,
    }
    
    with open(os.path.join(DATA_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nData generated in: {DATA_DIR}")
    print(f"  - process/: PDK parameters + gm/Id lookup table")
    print(f"  - signals/: {len(ecg)} ECG + {len(ppg)} PPG waveforms")
    print(f"  - reference/: published designs + noise budget")
    print("\nDone!")


if __name__ == "__main__":
    main()
