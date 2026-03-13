"""
Encryption Oracle for CryptoPuzzle Challenge

This oracle allows encryption of arbitrary messages (up to 100 queries).
"""

import json
import numpy as np
from falconshield import FalconShield

class EncryptionOracle:
    """Limited encryption oracle"""
    
    def __init__(self, keypair_id: int = 0):
        self.protocol = FalconShield()
        self.queries_remaining = 100
        self.keypair_id = keypair_id
        
        # Load public key
        with open('challenge_data/public_keys.json', 'r') as f:
            public_keys = json.load(f)
        
        kp = public_keys[keypair_id]
        self.public_key = (
            np.array(kp['public_key']['A'], dtype=np.int64),
            np.array(kp['public_key']['b'], dtype=np.int64)
        )
    
    def encrypt(self, message: bytes) -> dict:
        """Encrypt a message (decrements query counter)"""
        if self.queries_remaining <= 0:
            raise ValueError("No queries remaining")
        
        if len(message) > 1024:
            raise ValueError("Message too long (max 1024 bytes)")
        
        self.queries_remaining -= 1
        
        encrypted = self.protocol.encrypt(message, self.public_key)
        
        return {
            'iv': encrypted['iv'].hex(),
            'ciphertext': encrypted['ciphertext'].hex(),
            'mac': encrypted['mac'].hex(),
            'queries_remaining': self.queries_remaining
        }
    
    def get_queries_remaining(self) -> int:
        """Get number of remaining queries"""
        return self.queries_remaining


def interactive_oracle():
    """Interactive encryption oracle"""
    oracle = EncryptionOracle()
    
    print("=== FalconShield Encryption Oracle ===")
    print(f"Queries available: {oracle.get_queries_remaining()}")
    print("\nCommands:")
    print("  encrypt <hex_message> - Encrypt a message (hex encoded)")
    print("  encrypt_ascii <text>  - Encrypt ASCII text")
    print("  remaining             - Show remaining queries")
    print("  quit                  - Exit")
    print()
    
    while True:
        try:
            cmd = input("> ").strip().split(maxsplit=1)
            
            if not cmd:
                continue
            
            if cmd[0] == 'quit':
                break
            
            elif cmd[0] == 'remaining':
                print(f"Queries remaining: {oracle.get_queries_remaining()}")
            
            elif cmd[0] == 'encrypt':
                if len(cmd) < 2:
                    print("Usage: encrypt <hex_message>")
                    continue
                message = bytes.fromhex(cmd[1])
                result = oracle.encrypt(message)
                print(json.dumps(result, indent=2))
            
            elif cmd[0] == 'encrypt_ascii':
                if len(cmd) < 2:
                    print("Usage: encrypt_ascii <text>")
                    continue
                message = cmd[1].encode()
                result = oracle.encrypt(message)
                print(json.dumps(result, indent=2))
            
            else:
                print("Unknown command")
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    interactive_oracle()
