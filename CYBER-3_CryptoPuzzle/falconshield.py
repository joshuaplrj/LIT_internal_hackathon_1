"""
FalconShield Cryptographic Protocol - Reference Implementation

WARNING: This implementation contains intentional vulnerabilities for educational purposes.
Do NOT use in production systems.
"""

import numpy as np
import hashlib
import hmac
import os
from typing import Tuple, Optional

# LWE Parameters
LWE_N = 256      # Dimension
LWE_Q = 3329     # Modulus
LWE_SIGMA = 2.0  # Noise standard deviation
LWE_M = 512      # Number of samples

# FalconBlock Parameters
BLOCK_SIZE = 32   # 256 bits
KEY_SIZE = 16     # 128 bits
NUM_ROUNDS = 12

# Custom S-box (intentionally weak - linear structure in high bits)
SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]

INV_SBOX = [0] * 256
for i, v in enumerate(SBOX):
    INV_SBOX[v] = i

# MixColumns matrix (over GF(2^8))
MIX_MATRIX = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02],
]


class LWEKeyExchange:
    """LWE-based Key Exchange"""
    
    def __init__(self, n: int = LWE_N, q: int = LWE_Q, sigma: float = LWE_SIGMA, m: int = LWE_M):
        self.n = n
        self.q = q
        self.sigma = sigma
        self.m = m
    
    def _sample_gaussian(self, size: int) -> np.ndarray:
        """Sample from discrete Gaussian distribution"""
        samples = np.random.normal(0, self.sigma, size)
        return np.round(samples).astype(np.int64) % self.q
    
    def _sample_uniform(self, shape: tuple) -> np.ndarray:
        """Sample uniform random values mod q"""
        return np.random.randint(0, self.q, shape, dtype=np.int64)
    
    def keygen(self) -> Tuple[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        """Generate LWE key pair"""
        # Secret key
        s = self._sample_uniform(self.n)
        
        # Public matrix
        A = self._sample_uniform((self.m, self.n))
        
        # Error vector
        e = self._sample_gaussian(self.m)
        
        # b = A·s + e mod q
        b = (A @ s + e) % self.q
        
        return (A, b), s
    
    def encapsulate(self, public_key: Tuple[np.ndarray, np.ndarray]) -> Tuple[Tuple[np.ndarray, int], bytes]:
        """Generate shared secret and ciphertext"""
        A, b = public_key
        
        # Ephemeral secret
        s_prime = self._sample_uniform(self.n)
        
        # Error vectors
        e_prime = self._sample_gaussian(self.n)
        e_double_prime = self._sample_gaussian(1)[0]
        
        # u = A^T·s' + e' mod q
        u = (A.T @ s_prime + e_prime) % self.q
        
        # v = b^T·s' + e'' mod q
        v = int((b @ s_prime + e_double_prime) % self.q)
        
        # Derive shared secret from v (VULNERABILITY: simple quantization)
        # This is a weak derivation that leaks information
        shared_secret = self._derive_secret(v)
        
        return (u, v), shared_secret
    
    def decapsulate(self, ciphertext: Tuple[np.ndarray, int], private_key: np.ndarray) -> bytes:
        """Recover shared secret from ciphertext"""
        u, v = ciphertext
        
        # v' = v - s^T·u mod q
        v_prime = int((v - private_key @ u) % self.q)
        
        # Derive shared secret
        shared_secret = self._derive_secret(v_prime)
        
        return shared_secret
    
    def _derive_secret(self, v: int) -> bytes:
        """Derive shared secret from v value (VULNERABLE)"""
        # Simple quantization - leaks information about v
        # Better: use reconciliation mechanism
        bit = (v % self.q) > (self.q // 2)
        return bytes([0xFF if bit else 0x00] * 32)


class FalconBlock:
    """Custom block cipher (intentionally weakened)"""
    
    def __init__(self, key: bytes):
        if len(key) != KEY_SIZE:
            raise ValueError(f"Key must be {KEY_SIZE} bytes")
        self.key = key
        self.round_keys = self._key_schedule(key)
    
    def _gf_multiply(self, a: int, b: int) -> int:
        """Multiply in GF(2^8) with irreducible polynomial x^8 + x^4 + x^3 + x + 1"""
        p = 0
        for _ in range(8):
            if b & 1:
                p ^= a
            a <<= 1
            if a & 0x100:
                a ^= 0x11b
            b >>= 1
        return p
    
    def _key_schedule(self, key: bytes) -> list:
        """Generate round keys (VULNERABLE: weak key schedule)"""
        round_keys = []
        key_words = [int.from_bytes(key[i:i+4], 'big') for i in range(0, 16, 4)]
        
        # Rcon values
        rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8]
        
        for i in range(NUM_ROUNDS + 1):
            if i < 4:
                round_keys.append(key_words[i])
            else:
                # Weak key schedule - linear relationship
                temp = key_words[(i-1) % 4]
                # Rotate
                temp = ((temp << 8) | (temp >> 24)) & 0xFFFFFFFF
                # S-box (only on first byte - weakness)
                b0 = SBOX[(temp >> 24) & 0xFF]
                temp = (b0 << 24) | (temp & 0x00FFFFFF)
                # XOR with rcon
                temp ^= rcon[(i-4) % len(rcon)] << 24
                # Generate new word
                new_word = key_words[(i-4) % 4] ^ temp
                round_keys.append(new_word)
        
        return round_keys
    
    def _sub_bytes(self, state: np.ndarray) -> np.ndarray:
        """Apply S-box substitution"""
        return np.array([SBOX[b] for b in state.flatten()], dtype=np.uint8).reshape(state.shape)
    
    def _inv_sub_bytes(self, state: np.ndarray) -> np.ndarray:
        """Apply inverse S-box substitution"""
        return np.array([INV_SBOX[b] for b in state.flatten()], dtype=np.uint8).reshape(state.shape)
    
    def _shift_rows(self, state: np.ndarray) -> np.ndarray:
        """Shift rows"""
        result = state.copy()
        for i in range(1, 4):
            result[i] = np.roll(state[i], -i)
        return result
    
    def _inv_shift_rows(self, state: np.ndarray) -> np.ndarray:
        """Inverse shift rows"""
        result = state.copy()
        for i in range(1, 4):
            result[i] = np.roll(state[i], i)
        return result
    
    def _mix_columns(self, state: np.ndarray) -> np.ndarray:
        """Mix columns"""
        result = np.zeros_like(state)
        for col in range(4):
            for row in range(4):
                val = 0
                for k in range(4):
                    val ^= self._gf_multiply(MIX_MATRIX[row][k], state[k, col])
                result[row, col] = val
        return result
    
    def _add_round_key(self, state: np.ndarray, round_key: int) -> np.ndarray:
        """Add round key"""
        key_bytes = round_key.to_bytes(4, 'big')
        for col in range(4):
            for row in range(4):
                state[row, col] ^= key_bytes[row]
        return state
    
    def encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single block"""
        if len(block) != BLOCK_SIZE:
            raise ValueError(f"Block must be {BLOCK_SIZE} bytes")
        
        # Reshape to 4x8 matrix (non-standard - weakness)
        state = np.frombuffer(block, dtype=np.uint8).reshape(4, 8)
        
        # Initial round key
        state = self._add_round_key(state[:4, :4], self.round_keys[0])
        
        # Rounds
        for round_num in range(1, NUM_ROUNDS):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            if round_num < NUM_ROUNDS - 1:  # Skip MixColumns in last round
                state = self._mix_columns(state)
            state = self._add_round_key(state, self.round_keys[round_num])
        
        return state.tobytes()
    
    def decrypt_block(self, block: bytes) -> bytes:
        """Decrypt a single block"""
        if len(block) != BLOCK_SIZE:
            raise ValueError(f"Block must be {BLOCK_SIZE} bytes")
        
        state = np.frombuffer(block, dtype=np.uint8).reshape(4, 8)
        
        # Reverse rounds
        for round_num in range(NUM_ROUNDS - 1, 0, -1):
            state = self._add_round_key(state[:4, :4], self.round_keys[round_num])
            if round_num < NUM_ROUNDS - 1:
                state = self._inv_mix_columns(state)
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
        
        # Final round key
        state = self._add_round_key(state, self.round_keys[0])
        
        return state.tobytes()


class FalconShield:
    """Complete FalconShield protocol implementation"""
    
    def __init__(self):
        self.lwe = LWEKeyExchange()
    
    def _derive_keys(self, shared_secret: bytes) -> Tuple[bytes, bytes]:
        """Derive encryption and MAC keys from shared secret"""
        # HKDF-like derivation
        enc_key = hashlib.sha256(shared_secret + b"encryption").digest()[:KEY_SIZE]
        mac_key = hashlib.sha256(shared_secret + b"mac").digest()
        return enc_key, mac_key
    
    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding"""
        pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
        return data + bytes([pad_len] * pad_len)
    
    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        pad_len = data[-1]
        if pad_len > BLOCK_SIZE or pad_len == 0:
            raise ValueError("Invalid padding")
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding")
        return data[:-pad_len]
    
    def encrypt(self, plaintext: bytes, public_key: Tuple[np.ndarray, np.ndarray]) -> dict:
        """Encrypt a message"""
        # Key exchange
        ciphertext_lwe, shared_secret = self.lwe.encapsulate(public_key)
        
        # Derive keys
        enc_key, mac_key = self._derive_keys(shared_secret)
        
        # Generate IV
        iv = os.urandom(16)
        
        # Pad plaintext
        padded = self._pad(plaintext)
        
        # Encrypt using CBC mode
        cipher = FalconBlock(enc_key)
        encrypted = b''
        prev_block = iv
        
        for i in range(0, len(padded), BLOCK_SIZE):
            block = padded[i:i+BLOCK_SIZE]
            # XOR with previous ciphertext block (or IV)
            xored = bytes(a ^ b for a, b in zip(block, prev_block[:BLOCK_SIZE]))
            encrypted_block = cipher.encrypt_block(xored)
            encrypted += encrypted_block
            prev_block = encrypted_block
        
        # Compute MAC
        mac_data = iv + encrypted
        mac = hmac.new(mac_key, mac_data, hashlib.sha256).digest()
        
        return {
            'lwe_ciphertext': ciphertext_lwe,
            'iv': iv,
            'ciphertext': encrypted,
            'mac': mac
        }
    
    def decrypt(self, encrypted_data: dict, private_key: np.ndarray) -> bytes:
        """Decrypt a message"""
        # Key exchange
        shared_secret = self.lwe.decapsulate(encrypted_data['lwe_ciphertext'], private_key)
        
        # Derive keys
        enc_key, mac_key = self._derive_keys(shared_secret)
        
        # Verify MAC
        mac_data = encrypted_data['iv'] + encrypted_data['ciphertext']
        expected_mac = hmac.new(mac_key, mac_data, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_mac, encrypted_data['mac']):
            raise ValueError("MAC verification failed")
        
        # Decrypt using CBC mode
        cipher = FalconBlock(enc_key)
        decrypted = b''
        prev_block = encrypted_data['iv']
        
        for i in range(0, len(encrypted_data['ciphertext']), BLOCK_SIZE):
            block = encrypted_data['ciphertext'][i:i+BLOCK_SIZE]
            decrypted_block = cipher.decrypt_block(block)
            # XOR with previous ciphertext block (or IV)
            xored = bytes(a ^ b for a, b in zip(decrypted_block, prev_block[:BLOCK_SIZE]))
            decrypted += xored
            prev_block = block
        
        # Remove padding
        return self._unpad(decrypted)


def generate_test_vectors():
    """Generate test vectors for the protocol"""
    protocol = FalconShield()
    
    # Generate key pair
    public_key, private_key = protocol.lwe.keygen()
    
    # Test messages
    messages = [
        b"Hello, World!",
        b"The quick brown fox jumps over the lazy dog",
        b"A" * 100,
        os.urandom(256)
    ]
    
    print("=== FalconShield Test Vectors ===\n")
    
    for i, msg in enumerate(messages):
        print(f"Test {i+1}:")
        print(f"  Plaintext ({len(msg)} bytes): {msg[:50]}{'...' if len(msg) > 50 else ''}")
        
        encrypted = protocol.encrypt(msg, public_key)
        print(f"  IV: {encrypted['iv'].hex()}")
        print(f"  Ciphertext: {encrypted['ciphertext'][:32].hex()}...")
        print(f"  MAC: {encrypted['mac'].hex()}")
        
        decrypted = protocol.decrypt(encrypted, private_key)
        print(f"  Decrypted: {decrypted[:50]}{'...' if len(decrypted) > 50 else ''}")
        print(f"  Match: {msg == decrypted}\n")


if __name__ == "__main__":
    generate_test_vectors()
