# ECE-5: WaveCraft — Software-Defined Radio for Multi-Standard Reception

## Overview

Design a **Software-Defined Radio (SDR) receiver** capable of simultaneously receiving multiple wireless standards from 88 MHz to 7.125 GHz.

## Standards

| Standard | Frequency | Bandwidth | Modulation |
|---|---|---|---|
| FM Radio | 88–108 MHz | 200 kHz | Wideband FM |
| DAB+ | 174–240 MHz | 1.5 MHz | OFDM |
| LTE | 700 MHz – 2.6 GHz | Up to 20 MHz | OFDMA |
| WiFi 6E | 5.925–7.125 GHz | Up to 160 MHz | OFDM |
| GPS L1 | 1.57542 GHz | 2.046 MHz | BPSK CDMA |

## Architecture Options

### 1. Superheterodyne

```
Antenna → LNA → Mixer → IF Filter → ADC → DSP
                    ↑
                   LO
```

### 2. Direct Conversion (Zero-IF)

```
Antenna → LNA → I/Q Mixer → LPF → ADC → DSP
                    ↑
                   LO
```

### 3. Direct Sampling

```
Antenna → LNA → ADC → DSP
```

```python
class SDRArchitecture:
    def __init__(self, freq_min, freq_max, bandwidth_max):
        self.f_min = freq_min
        self.f_max = freq_max
        self.bw_max = bandwidth_max
    
    def direct_conversion(self):
        """Direct conversion (zero-IF) architecture"""
        return {
            'pros': [
                'Simple architecture',
                'No image rejection needed',
                'Wideband capable'
            ],
            'cons': [
                'I/Q imbalance',
                'DC offset',
                'LO leakage',
                '1/f noise'
            ],
            'suitability': 'Good for wideband, moderate dynamic range'
        }
    
    def superheterodyne(self, if_freq=100e6):
        """Superheterodyne architecture"""
        return {
            'pros': [
                'Excellent selectivity',
                'High dynamic range',
                'Well-proven'
            ],
            'cons': [
                'Image frequency problem',
                'Multiple conversion stages',
                'Complex filtering'
            ],
            'suitability': 'Best for high-performance single-band'
        }
    
    def direct_sampling(self, adc_bits=16, adc_rate=3e9):
        """Direct sampling architecture"""
        nyquist_bandwidth = adc_rate / 2
        
        return {
            'pros': [
                'Maximum flexibility',
                'No analog mixing',
                'All-digital processing'
            ],
            'cons': [
                'Requires very fast ADC',
                'High power consumption',
                'ADC dynamic range limits'
            ],
            'suitability': f'Can cover up to {nyquist_bandwidth/1e9:.1f} GHz'
        }
    
    def recommended_architecture(self):
        """Recommend architecture for multi-standard"""
        # Hybrid approach
        return {
            'low_band': 'Direct conversion (88 MHz - 2.6 GHz)',
            'high_band': 'Superheterodyne with IF sampling (2.6 - 7.125 GHz)',
            'adc': 'Direct sampling at IF'
        }
```

## Analog Front-End

### Wideband LNA

```python
class WidebandLNA:
    def __init__(self, freq_min, freq_max):
        self.f_min = freq_min
        self.f_max = freq_max
    
    def noise_figure(self, frequency):
        """
        Noise figure vs frequency
        
        Typically increases at band edges
        """
        f_center = (self.f_min + self.f_max) / 2
        f_bw = self.f_max - self.f_min
        
        # Minimum NF at center, increases at edges
        nf_min = 1.5  # dB
        nf_variation = 1.5  # dB
        
        normalized_freq = 2 * (frequency - f_center) / f_bw
        nf = nf_min + nf_variation * normalized_freq**2
        
        return nf
    
    def gain(self, frequency):
        """Gain vs frequency"""
        # Flat gain across band
        return 15  # dB typical
    
    def ip3(self):
        """Third-order intercept point"""
        return 0  # dBm typical for wideband LNA
```

### Frequency Synthesizer

```python
class PLLSynthesizer:
    def __init__(self, ref_freq=10e6, vco_range=(1e9, 6e9)):
        self.f_ref = ref_freq
        self.vco_min, self.vco_max = vco_range
    
    def calculate_dividers(self, f_out):
        """
        Calculate PLL divider values
        
        f_out = f_ref * N / R
        """
        # Integer-N PLL
        for R in range(1, 1000):
            for N in range(1, 10000):
                f_vco = self.f_ref * N / R
                if abs(f_vco - f_out) < 1e3:  # Within 1 kHz
                    if self.vco_min <= f_vco <= self.vco_max:
                        return {'R': R, 'N': N, 'f_vco': f_vco}
        
        return None
    
    def phase_noise(self, offset_freq):
        """
        Phase noise model
        
        L(f) = L_floor + 20*log10(N) + 10*log10(f_ref)
        """
        L_floor = -220  # dBc/Hz floor
        N = 100  # Typical divider
        
        L = L_floor + 20 * np.log10(N) + 10 * np.log10(self.f_ref)
        return L
    
    def settling_time(self, bandwidth=100e3):
        """
        PLL settling time
        
        t_settle ≈ 4 / (2π * BW)
        """
        return 4 / (2 * np.pi * bandwidth)
```

## Digital Front-End

### Digital Down-Conversion

```python
class DigitalDownConverter:
    def __init__(self, fs, fc, bw):
        self.fs = fs
        self.fc = fc
        self.bw = bw
    
    def nco(self, frequency, phase=0):
        """
        Numerically Controlled Oscillator
        
        Generates complex exponential at desired frequency
        """
        t = np.arange(0, 1/self.fs, 1/self.fs)
        return np.exp(1j * (2 * np.pi * frequency * t + phase))
    
    def mix(self, signal, lo_freq):
        """Mix signal to baseband"""
        lo = self.nco(lo_freq)
        return signal * np.conj(lo)
    
    def decimate(self, signal, factor, filter_coeffs=None):
        """
        Decimate signal by factor M
        
        1. Apply anti-aliasing filter
        2. Downsample by M
        """
        if filter_coeffs is None:
            # Default anti-aliasing filter
            filter_coeffs = signal.firwin(64, 1/factor)
        
        # Filter
        filtered = np.convolve(signal, filter_coeffs, mode='same')
        
        # Downsample
        return filtered[::factor]
```

### Polyphase Channelizer

```python
class PolyphaseChannelizer:
    def __init__(self, num_channels, filter_length):
        self.M = num_channels
        self.N = filter_length
    
    def design_prototype_filter(self, transition_width):
        """
        Design prototype lowpass filter
        
        Cutoff at 1/M of sampling rate
        """
        from scipy import signal
        
        cutoff = 1 / self.M - transition_width
        taps = signal.firwin(self.N, cutoff)
        
        return taps
    
    def polyphase_decomposition(self, prototype_filter):
        """
        Decompose prototype filter into polyphase components
        
        h_k[n] = h[nM + k] for k = 0, 1, ..., M-1
        """
        polyphase_filters = []
        
        for k in range(self.M):
            polyphase_filters.append(prototype_filter[k::self.M])
        
        return polyphase_filters
    
    def channelize(self, wideband_signal):
        """
        Channelize wideband signal into M channels
        """
        # FFT-based channelization
        M = self.M
        
        # Reshape into blocks
        num_blocks = len(wideband_signal) // M
        blocks = wideband_signal[:num_blocks * M].reshape(num_blocks, M)
        
        # Apply polyphase filtering
        # ... implementation
        
        # FFT to separate channels
        channels = np.fft.fft(blocks, axis=1)
        
        return channels.T  # M channels
```

## Baseband Processing

### FM Demodulator

```python
class FMDemodulator:
    def __init__(self, fs=200e3, max_deviation=75e3):
        self.fs = fs
        self.max_dev = max_deviation
    
    def discriminator(self, iq_signal):
        """
        FM discriminator demodulation
        
        dφ/dt = Im(s[n] * conj(s[n-1]))
        """
        # Phase difference
        phase_diff = np.angle(iq_signal[1:] * np.conj(iq_signal[:-1]))
        
        # Scale to audio
        audio = phase_diff * self.fs / (2 * np.pi * self.max_dev)
        
        return audio
    
    def deemphasis(self, audio, tau=75e-6):
        """
        De-emphasis filter (75 μs for US, 50 μs for EU)
        
        H(s) = 1 / (1 + sτ)
        """
        # First-order IIR
        alpha = 1 / (1 + self.fs * tau)
        
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        
        for n in range(1, len(audio)):
            filtered[n] = alpha * audio[n] + (1 - alpha) * filtered[n-1]
        
        return filtered
    
    def stereo_decode(self, left_plus_right, left_minus_right):
        """
        Stereo decoding
        
        L = (L+R) + (L-R)
        R = (L+R) - (L-R)
        """
        left = (left_plus_right + left_minus_right) / 2
        right = (left_plus_right - left_minus_right) / 2
        
        return left, right
```

### GPS Receiver

```python
class GPSReceiver:
    def __init__(self, fs=4.092e6):
        self.fs = fs
        self.code_rate = 1.023e6  # C/A code chipping rate
        self.code_length = 1023
    
    def generate_ca_code(self, prn):
        """
        Generate C/A code for given PRN
        
        G1 ⊕ G2 (delayed)
        """
        # Simplified - actual implementation uses two LFSRs
        code = np.random.randint(0, 2, self.code_length) * 2 - 1
        return code
    
    def acquisition(self, signal, prn, doppler_range=(-5000, 5000)):
        """
        Code phase and Doppler acquisition
        
        2D search: code delay × Doppler frequency
        """
        ca_code = self.generate_ca_code(prn)
        
        best_corr = 0
        best_delay = 0
        best_doppler = 0
        
        for doppler in range(doppler_range[0], doppler_range[1], 500):
            # Mix to remove Doppler
            t = np.arange(len(signal)) / self.fs
            mixed = signal * np.exp(-1j * 2 * np.pi * doppler * t)
            
            # Correlate with C/A code
            for delay in range(self.code_length):
                code_shifted = np.roll(ca_code, delay)
                corr = np.abs(np.sum(mixed * code_shifted))
                
                if corr > best_corr:
                    best_corr = corr
                    best_delay = delay
                    best_doppler = doppler
        
        return {'delay': best_delay, 'doppler': best_doppler, 'peak': best_corr}
    
    def tracking(self, signal, initial_delay, initial_doppler):
        """
        Code and carrier tracking
        
        DLL for code, PLL for carrier
        """
        return {
            'dll': 'Delay Lock Loop for code tracking',
            'pll': 'Phase Lock Loop for carrier tracking',
            'bw_code': 1,  # Hz
            'bw_carrier': 10  # Hz
        }
```

## Deliverables

1. **Architecture Document**: Design choices
2. **Analog Front-End**: Schematics and calculations
3. **Digital Processing**: Source code
4. **Simulation Results**: 2 standards
5. **Performance Analysis**: Sensitivity, selectivity, dynamic range

## Project Structure

```
ECE-5_WaveCraft/
├── README.md
├── architecture/
│   └── sdr_architecture.py
├── analog_frontend/
│   ├── lna.py
│   └── synthesizer.py
├── digital_frontend/
│   ├── ddc.py
│   └── channelizer.py
├── baseband/
│   ├── fm_demod.py
│   ├── gps_receiver.py
│   └── lte_receiver.py
├── simulation/
│   └── sdr_sim.py
├── run_simulation.py
└── solution_template.py
```

## Tips

1. Direct conversion is simplest but has I/Q issues
2. Wideband LNA design is challenging
3. Polyphase channelizer is efficient for multi-standard
4. FM demodulation is straightforward
5. GPS acquisition requires 2D search
