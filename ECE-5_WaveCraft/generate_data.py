"""
WaveCraft - Generate simulation data for SDR multi-standard receiver

Generates:
- Sample RF recordings for each wireless standard (synthesized baseband IQ)
- Standards specification summary
- Component specifications (ADCs, LNAs, PLLs)
- Test vectors for each demodulator
"""

import numpy as np
import json
import os
import csv

SEED = 42
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def generate_standards_specs():
    """Generate comprehensive wireless standards specification summary."""
    os.makedirs(os.path.join(DATA_DIR, "standards"), exist_ok=True)
    
    standards = {
        "fm_radio": {
            "name": "FM Broadcast Radio",
            "standard": "ITU-R BS.450",
            "frequency_range_mhz": [88, 108],
            "channel_bandwidth_khz": 200,
            "modulation": "Wideband FM",
            "max_deviation_khz": 75,
            "pre_emphasis_us": 75,
            "stereo_pilot_khz": 19,
            "snr_threshold_db": 30,
            "sensitivity_dbm": -90,
            "audio_bandwidth_hz": [30, 15000],
        },
        "dab_plus": {
            "name": "Digital Audio Broadcasting (DAB+)",
            "standard": "ETSI EN 300 401",
            "frequency_range_mhz": [174, 240],
            "channel_bandwidth_mhz": 1.536,
            "modulation": "OFDM with DQPSK",
            "num_subcarriers": 1536,
            "subcarrier_spacing_hz": 1000,
            "guard_interval_us": 246,
            "symbol_duration_us": 1246,
            "fec": "Convolutional (rate 1/4 to 3/4)",
            "sensitivity_dbm": -97,
        },
        "lte": {
            "name": "LTE (4G)",
            "standard": "3GPP Release 15",
            "frequency_bands": {
                "band_3": {"freq_dl_mhz": [1805, 1880], "freq_ul_mhz": [1710, 1785]},
                "band_7": {"freq_dl_mhz": [2620, 2690], "freq_ul_mhz": [2500, 2570]},
                "band_20": {"freq_dl_mhz": [791, 821], "freq_ul_mhz": [832, 862]},
            },
            "channel_bandwidths_mhz": [1.4, 3, 5, 10, 15, 20],
            "modulation": "OFDMA (DL), SC-FDMA (UL)",
            "subcarrier_spacing_khz": 15,
            "fft_sizes": [128, 256, 512, 1024, 1536, 2048],
            "cp_normal_us": 4.7,
            "cp_extended_us": 16.67,
            "modulation_schemes": ["QPSK", "16QAM", "64QAM", "256QAM"],
            "sensitivity_dbm": -100,
        },
        "wifi_6e": {
            "name": "WiFi 6E (802.11ax)",
            "standard": "IEEE 802.11ax",
            "frequency_range_mhz": [5925, 7125],
            "channel_bandwidths_mhz": [20, 40, 80, 160],
            "modulation": "OFDMA",
            "subcarrier_spacing_khz": 78.125,
            "fft_sizes": {"20mhz": 256, "40mhz": 512, "80mhz": 1024, "160mhz": 2048},
            "guard_interval_us": [0.8, 1.6, 3.2],
            "modulation_schemes": ["BPSK", "QPSK", "16QAM", "64QAM", "256QAM", "1024QAM"],
            "mcs_table": [
                {"mcs": 0, "mod": "BPSK", "rate": "1/2", "data_rate_mbps_20mhz": 8.6},
                {"mcs": 1, "mod": "QPSK", "rate": "1/2", "data_rate_mbps_20mhz": 17.2},
                {"mcs": 2, "mod": "QPSK", "rate": "3/4", "data_rate_mbps_20mhz": 25.8},
                {"mcs": 3, "mod": "16QAM", "rate": "1/2", "data_rate_mbps_20mhz": 34.4},
                {"mcs": 4, "mod": "16QAM", "rate": "3/4", "data_rate_mbps_20mhz": 51.6},
                {"mcs": 5, "mod": "64QAM", "rate": "2/3", "data_rate_mbps_20mhz": 68.8},
                {"mcs": 6, "mod": "64QAM", "rate": "3/4", "data_rate_mbps_20mhz": 77.4},
                {"mcs": 7, "mod": "64QAM", "rate": "5/6", "data_rate_mbps_20mhz": 86.0},
                {"mcs": 8, "mod": "256QAM", "rate": "3/4", "data_rate_mbps_20mhz": 103.2},
                {"mcs": 9, "mod": "256QAM", "rate": "5/6", "data_rate_mbps_20mhz": 114.7},
                {"mcs": 10, "mod": "1024QAM", "rate": "3/4", "data_rate_mbps_20mhz": 129.0},
                {"mcs": 11, "mod": "1024QAM", "rate": "5/6", "data_rate_mbps_20mhz": 143.4},
            ],
            "sensitivity_dbm": -82,
        },
        "gps_l1": {
            "name": "GPS L1 C/A",
            "standard": "IS-GPS-200",
            "center_frequency_mhz": 1575.42,
            "bandwidth_mhz": 2.046,
            "modulation": "BPSK(1) - DSSS with C/A code",
            "code_rate_mchips_s": 1.023,
            "code_length_chips": 1023,
            "code_period_ms": 1,
            "data_rate_bps": 50,
            "received_power_dbm": -130,
            "min_cn0_dbhz": 35,
            "num_satellites": 32,
            "doppler_range_hz": [-5000, 5000],
            "prn_codes_taps": {
                "1": [2, 6], "2": [3, 7], "3": [4, 8], "4": [5, 9],
                "5": [1, 9], "6": [2, 10], "7": [1, 8], "8": [2, 9],
                "9": [3, 10], "10": [2, 3], "11": [3, 4], "12": [5, 6],
            },
        },
    }
    
    with open(os.path.join(DATA_DIR, "standards", "specifications.json"), 'w') as f:
        json.dump(standards, f, indent=2)
    
    return standards


def generate_fm_test_signal():
    """Generate FM radio test signal (baseband IQ)."""
    os.makedirs(os.path.join(DATA_DIR, "test_signals"), exist_ok=True)
    
    fs = 250e3  # 250 kHz baseband sampling rate
    duration = 2  # 2 seconds
    N = int(fs * duration)
    t = np.arange(N) / fs
    
    # Audio signal: multi-tone test
    audio = np.zeros(N)
    # 1 kHz tone (standard test tone)
    audio += 0.5 * np.sin(2 * np.pi * 1000 * t)
    # Add some harmonics for richness
    audio += 0.2 * np.sin(2 * np.pi * 3000 * t)
    audio += 0.1 * np.sin(2 * np.pi * 8000 * t)
    
    # FM modulate
    max_dev = 75e3  # 75 kHz deviation
    phase = 2 * np.pi * max_dev * np.cumsum(audio) / fs
    iq = np.exp(1j * phase)
    
    # Add noise
    snr_db = 30
    noise_power = 10**(-snr_db / 10)
    noise = np.sqrt(noise_power / 2) * (np.random.randn(N) + 1j * np.random.randn(N))
    iq_noisy = iq + noise
    
    filepath = os.path.join(DATA_DIR, "test_signals", "fm_radio_iq.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "i", "q"])
        for j in range(0, N, 25):  # Subsample to keep file reasonable
            writer.writerow([j, f"{iq_noisy[j].real:.6f}", f"{iq_noisy[j].imag:.6f}"])
    
    # Also save the reference audio
    filepath2 = os.path.join(DATA_DIR, "test_signals", "fm_reference_audio.csv")
    with open(filepath2, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "amplitude"])
        for j in range(0, N, 25):
            writer.writerow([j, f"{audio[j]:.6f}"])
    
    return {"standard": "FM Radio", "fs_hz": fs, "duration_s": duration,
            "snr_db": snr_db, "deviation_hz": max_dev}


def generate_gps_test_signal():
    """Generate GPS L1 C/A test signal."""
    os.makedirs(os.path.join(DATA_DIR, "test_signals"), exist_ok=True)
    
    fs = 4.092e6  # ~4x code rate
    duration = 0.01  # 10 ms (10 code periods)
    N = int(fs * duration)
    t = np.arange(N) / fs
    
    # Generate C/A code for PRN 1 (simplified - using Gold code taps)
    def generate_gold_code(prn_taps=[2, 6], length=1023):
        """Generate a Gold code (simplified)."""
        # G1 generator: x^10 + x^3 + 1
        g1 = np.ones(10, dtype=int)
        g1_out = np.zeros(length, dtype=int)
        
        # G2 generator: x^10 + x^9 + x^8 + x^6 + x^3 + x^2 + 1
        g2 = np.ones(10, dtype=int)
        g2_out = np.zeros(length, dtype=int)
        
        for i in range(length):
            g1_out[i] = g1[-1]
            g2_out[i] = g2[prn_taps[0]-1] ^ g2[prn_taps[1]-1]
            
            # Feedback
            g1_fb = g1[2] ^ g1[9]
            g1 = np.roll(g1, 1)
            g1[0] = g1_fb
            
            g2_fb = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
            g2 = np.roll(g2, 1)
            g2[0] = g2_fb
        
        return (g1_out ^ g2_out) * 2 - 1  # Convert to +/- 1
    
    # Generate C/A codes for a few PRNs
    prn_configs = [
        {"prn": 1, "taps": [2, 6], "doppler_hz": 1500, "code_delay_chips": 300, "cn0_dbhz": 45},
        {"prn": 3, "taps": [4, 8], "doppler_hz": -2000, "code_delay_chips": 750, "cn0_dbhz": 42},
        {"prn": 7, "taps": [1, 8], "doppler_hz": 500, "code_delay_chips": 100, "cn0_dbhz": 40},
    ]
    
    signal = np.zeros(N, dtype=complex)
    
    for cfg in prn_configs:
        ca_code = generate_gold_code(cfg["taps"])
        
        # Upsample code to sampling rate
        samples_per_chip = fs / 1.023e6
        code_samples = np.zeros(N)
        for i in range(N):
            chip_idx = int((i / samples_per_chip + cfg["code_delay_chips"]) % 1023)
            code_samples[i] = ca_code[chip_idx]
        
        # Apply carrier with Doppler
        carrier = np.exp(1j * 2 * np.pi * cfg["doppler_hz"] * t)
        
        # Signal power from C/N0
        cn0_linear = 10**(cfg["cn0_dbhz"] / 10)
        signal_power = cn0_linear / fs
        amplitude = np.sqrt(signal_power)
        
        signal += amplitude * code_samples * carrier
    
    # Add noise (thermal noise floor)
    noise = np.sqrt(0.5) * (np.random.randn(N) + 1j * np.random.randn(N))
    signal_noisy = signal + noise
    
    # Save IQ data
    filepath = os.path.join(DATA_DIR, "test_signals", "gps_l1_iq.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "i", "q"])
        for j in range(0, N, 4):  # Subsample
            writer.writerow([j, f"{signal_noisy[j].real:.6f}", f"{signal_noisy[j].imag:.6f}"])
    
    # Save ground truth
    with open(os.path.join(DATA_DIR, "test_signals", "gps_ground_truth.json"), 'w') as f:
        json.dump({
            "sampling_rate_hz": fs,
            "duration_s": duration,
            "satellites": prn_configs,
        }, f, indent=2)
    
    return prn_configs


def generate_ofdm_test_signal():
    """Generate a simplified OFDM test signal (LTE-like)."""
    os.makedirs(os.path.join(DATA_DIR, "test_signals"), exist_ok=True)
    
    # LTE 5 MHz parameters
    fft_size = 512
    num_subcarriers = 300  # Active subcarriers
    cp_length = 36  # Normal CP
    num_symbols = 14  # 1 subframe (1 ms)
    subcarrier_spacing = 15e3  # 15 kHz
    fs = fft_size * subcarrier_spacing  # 7.68 MHz
    
    # Generate random QPSK data
    constellation = np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)
    
    symbols = []
    tx_data = []
    
    for sym_idx in range(num_symbols):
        # Random QPSK symbols on active subcarriers
        data_indices = np.random.randint(0, 4, num_subcarriers)
        freq_domain = np.zeros(fft_size, dtype=complex)
        
        # Map to center subcarriers (skip DC)
        start = (fft_size - num_subcarriers) // 2
        freq_domain[start:start+num_subcarriers] = constellation[data_indices]
        
        # IFFT
        time_domain = np.fft.ifft(freq_domain) * np.sqrt(fft_size)
        
        # Add cyclic prefix
        with_cp = np.concatenate([time_domain[-cp_length:], time_domain])
        symbols.append(with_cp)
        tx_data.append(data_indices.tolist())
    
    # Concatenate all symbols
    signal = np.concatenate(symbols)
    
    # Add channel (simple multipath)
    channel = np.array([1.0, 0, 0, 0, 0.3*np.exp(1j*0.5), 0, 0, 0, 0, 0.1*np.exp(1j*1.2)])
    signal_ch = np.convolve(signal, channel, mode='same')
    
    # Add noise
    snr_db = 20
    noise_power = np.mean(np.abs(signal_ch)**2) * 10**(-snr_db/10)
    noise = np.sqrt(noise_power/2) * (np.random.randn(len(signal_ch)) + 1j*np.random.randn(len(signal_ch)))
    signal_noisy = signal_ch + noise
    
    filepath = os.path.join(DATA_DIR, "test_signals", "lte_ofdm_iq.csv")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "i", "q"])
        for j in range(0, len(signal_noisy), 8):  # Subsample
            writer.writerow([j, f"{signal_noisy[j].real:.6f}", f"{signal_noisy[j].imag:.6f}"])
    
    # Save parameters
    params = {
        "standard": "LTE 5MHz",
        "fft_size": fft_size,
        "active_subcarriers": num_subcarriers,
        "cp_length": cp_length,
        "num_symbols": num_symbols,
        "subcarrier_spacing_hz": subcarrier_spacing,
        "sampling_rate_hz": fs,
        "modulation": "QPSK",
        "snr_db": snr_db,
        "channel_taps": [
            {"delay": 0, "gain": 1.0, "phase_rad": 0},
            {"delay": 4, "gain": 0.3, "phase_rad": 0.5},
            {"delay": 9, "gain": 0.1, "phase_rad": 1.2},
        ],
    }
    
    with open(os.path.join(DATA_DIR, "test_signals", "lte_parameters.json"), 'w') as f:
        json.dump(params, f, indent=2)
    
    return params


def generate_component_specs():
    """Generate SDR component specifications."""
    os.makedirs(os.path.join(DATA_DIR, "components"), exist_ok=True)
    
    components = {
        "adcs": [
            {"model": "ADC-14bit-250M", "resolution_bits": 14, "max_rate_msps": 250,
             "input_bw_mhz": 500, "snr_db": 72, "sfdr_db": 85, "enob": 11.5,
             "power_mw": 800, "interface": "JESD204B", "price_usd": 150},
            {"model": "ADC-12bit-1G", "resolution_bits": 12, "max_rate_msps": 1000,
             "input_bw_mhz": 2000, "snr_db": 64, "sfdr_db": 75, "enob": 10.3,
             "power_mw": 1500, "interface": "JESD204B", "price_usd": 300},
            {"model": "ADC-16bit-125M", "resolution_bits": 16, "max_rate_msps": 125,
             "input_bw_mhz": 200, "snr_db": 78, "sfdr_db": 92, "enob": 12.7,
             "power_mw": 500, "interface": "LVDS", "price_usd": 100},
            {"model": "ADC-12bit-3G", "resolution_bits": 12, "max_rate_msps": 3000,
             "input_bw_mhz": 5000, "snr_db": 58, "sfdr_db": 68, "enob": 9.3,
             "power_mw": 3000, "interface": "JESD204C", "price_usd": 800},
        ],
        "lnas": [
            {"model": "LNA-WB-100M-6G", "freq_min_mhz": 100, "freq_max_mhz": 6000,
             "gain_db": 15, "nf_db": 2.0, "oip3_dbm": 22, "p1db_dbm": 8,
             "power_mw": 200, "price_usd": 25},
            {"model": "LNA-NB-1G-2G", "freq_min_mhz": 1000, "freq_max_mhz": 2000,
             "gain_db": 20, "nf_db": 0.8, "oip3_dbm": 28, "p1db_dbm": 12,
             "power_mw": 80, "price_usd": 15},
            {"model": "LNA-UHF-5G-8G", "freq_min_mhz": 5000, "freq_max_mhz": 8000,
             "gain_db": 18, "nf_db": 1.5, "oip3_dbm": 20, "p1db_dbm": 6,
             "power_mw": 150, "price_usd": 35},
        ],
        "synthesizers": [
            {"model": "PLL-WB-35M-4.4G", "freq_min_mhz": 35, "freq_max_mhz": 4400,
             "phase_noise_dbc_hz_1mhz": -130, "lock_time_us": 100,
             "ref_freq_mhz": 10, "power_mw": 300, "price_usd": 40},
            {"model": "PLL-HF-4G-8G", "freq_min_mhz": 4000, "freq_max_mhz": 8000,
             "phase_noise_dbc_hz_1mhz": -125, "lock_time_us": 50,
             "ref_freq_mhz": 100, "power_mw": 450, "price_usd": 65},
        ],
        "mixers": [
            {"model": "MIX-WB-100M-6G", "rf_min_mhz": 100, "rf_max_mhz": 6000,
             "if_max_mhz": 500, "conversion_gain_db": -7, "iip3_dbm": 15,
             "nf_db": 8, "lo_power_dbm": 10, "price_usd": 20},
            {"model": "MIX-IQ-1G-6G", "rf_min_mhz": 1000, "rf_max_mhz": 6000,
             "if_max_mhz": 2000, "conversion_gain_db": 0, "iip3_dbm": 10,
             "nf_db": 10, "lo_power_dbm": 5, "image_rejection_db": 35,
             "price_usd": 30},
        ],
        "filters": [
            {"model": "SAW-88-108", "type": "SAW", "freq_center_mhz": 98,
             "bandwidth_mhz": 20, "insertion_loss_db": 2.5, "rejection_db": 40,
             "price_usd": 5},
            {"model": "BAW-1575", "type": "BAW", "freq_center_mhz": 1575.42,
             "bandwidth_mhz": 10, "insertion_loss_db": 1.5, "rejection_db": 50,
             "price_usd": 8},
            {"model": "LPF-DC-3G", "type": "LC Lowpass", "cutoff_mhz": 3000,
             "insertion_loss_db": 1.0, "rejection_30pct_db": 30, "price_usd": 3},
        ],
    }
    
    with open(os.path.join(DATA_DIR, "components", "sdr_components.json"), 'w') as f:
        json.dump(components, f, indent=2)
    
    return components


def main():
    print("Generating WaveCraft simulation data...")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("1. Generating standards specifications...")
    standards = generate_standards_specs()
    
    print("2. Generating FM radio test signal...")
    fm = generate_fm_test_signal()
    
    print("3. Generating GPS L1 test signal...")
    gps = generate_gps_test_signal()
    
    print("4. Generating OFDM (LTE) test signal...")
    ofdm = generate_ofdm_test_signal()
    
    print("5. Generating component specifications...")
    components = generate_component_specs()
    
    metadata = {
        "problem": "ECE-5 WaveCraft",
        "description": "Software-Defined Radio for Multi-Standard Reception",
        "frequency_coverage": {
            "min_mhz": 88,
            "max_mhz": 7125,
            "ratio": "81:1",
        },
        "standards_covered": list(standards.keys()),
        "data_contents": {
            "standards": f"{len(standards)} wireless standard specifications",
            "test_signals": "FM IQ, GPS L1 IQ, LTE OFDM IQ (baseband samples)",
            "components": f"ADCs, LNAs, PLLs, mixers, filters ({sum(len(v) for v in components.values())} total)",
        },
        "seed": SEED,
    }
    
    with open(os.path.join(DATA_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nData generated in: {DATA_DIR}")
    print(f"  - standards/: {len(standards)} standard specifications")
    print(f"  - test_signals/: FM, GPS, LTE IQ data")
    print(f"  - components/: SDR component catalog")
    print("\nDone!")


if __name__ == "__main__":
    main()
