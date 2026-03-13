"""
Generate ciphertexts for the CryptoPuzzle challenge
"""

import json
import os
import numpy as np
from falconshield import FalconShield

def generate_challenge_data():
    """Generate all challenge data"""
    protocol = FalconShield()
    
    # Generate multiple key pairs
    num_keypairs = 10
    keypairs = []
    for i in range(num_keypairs):
        public_key, private_key = protocol.lwe.keygen()
        keypairs.append({
            'id': i,
            'public_key': {
                'A': public_key[0].tolist(),
                'b': public_key[1].tolist()
            },
            'private_key': private_key.tolist()  # Will be kept secret in actual challenge
        })
    
    # Generate 100 ciphertexts
    ciphertexts = []
    plaintexts = []
    
    for i in range(100):
        # Select random key pair
        kp_idx = i % num_keypairs
        public_key = (
            np.array(keypairs[kp_idx]['public_key']['A'], dtype=np.int64),
            np.array(keypairs[kp_idx]['public_key']['b'], dtype=np.int64)
        )
        
        # Generate random plaintext (256 bytes)
        plaintext = os.urandom(256)
        plaintexts.append({
            'id': i,
            'keypair_id': kp_idx,
            'plaintext': plaintext.hex()
        })
        
        # Encrypt
        encrypted = protocol.encrypt(plaintext, public_key)
        
        ciphertexts.append({
            'id': i,
            'keypair_id': kp_idx,
            'lwe_ciphertext': {
                'u': encrypted['lwe_ciphertext'][0].tolist(),
                'v': encrypted['lwe_ciphertext'][1]
            },
            'iv': encrypted['iv'].hex(),
            'ciphertext': encrypted['ciphertext'].hex(),
            'mac': encrypted['mac'].hex()
        })
    
    # Generate known plaintext-ciphertext pairs (10 pairs)
    known_pairs = []
    for i in range(10):
        kp_idx = i % num_keypairs
        public_key = (
            np.array(keypairs[kp_idx]['public_key']['A'], dtype=np.int64),
            np.array(keypairs[kp_idx]['public_key']['b'], dtype=np.int64)
        )
        
        # Use predictable plaintext for known pairs
        plaintext = f"KNOWN_PLAINTEXT_{i:03d}".encode().ljust(256, b'X')
        
        encrypted = protocol.encrypt(plaintext, public_key)
        
        known_pairs.append({
            'id': i,
            'keypair_id': kp_idx,
            'plaintext': plaintext.hex(),
            'iv': encrypted['iv'].hex(),
            'ciphertext': encrypted['ciphertext'].hex(),
            'mac': encrypted['mac'].hex()
        })
    
    # Save public keys only (private keys are secret)
    public_keys_data = []
    for kp in keypairs:
        public_keys_data.append({
            'id': kp['id'],
            'public_key': kp['public_key']
        })
    
    # Save private keys separately (for verification)
    private_keys_data = []
    for kp in keypairs:
        private_keys_data.append({
            'id': kp['id'],
            'private_key': kp['private_key']
        })
    
    # Write files
    os.makedirs('challenge_data', exist_ok=True)
    
    with open('challenge_data/public_keys.json', 'w') as f:
        json.dump(public_keys_data, f)
    
    with open('challenge_data/private_keys.json', 'w') as f:
        json.dump(private_keys_data, f)
    
    with open('challenge_data/ciphertexts.json', 'w') as f:
        json.dump(ciphertexts, f)
    
    with open('challenge_data/known_pairs.json', 'w') as f:
        json.dump(known_pairs, f)
    
    with open('challenge_data/plaintexts.json', 'w') as f:
        json.dump(plaintexts, f)
    
    print("Challenge data generated successfully!")
    print(f"  - {num_keypairs} key pairs")
    print(f"  - {len(ciphertexts)} ciphertexts")
    print(f"  - {len(known_pairs)} known plaintext-ciphertext pairs")


if __name__ == "__main__":
    generate_challenge_data()
