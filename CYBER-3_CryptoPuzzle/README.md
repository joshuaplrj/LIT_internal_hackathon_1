# CYBER-3: CryptoPuzzle — Breaking FalconShield

## Overview

You are given a custom cryptographic protocol called **FalconShield**. Your task is to cryptanalyze the protocol, find vulnerabilities, and decrypt the provided ciphertexts.

## Files

- `protocol_spec.md` — Protocol specification
- `falconshield.py` — Reference implementation
- `generate_ciphertexts.py` — Script to generate challenge data
- `encryption_oracle.py` — Interactive encryption oracle (100 queries)
- `solution_template.py` — Template for your solution
- `challenge_data/` — Generated challenge data (after running generate_ciphertexts.py)

## Getting Started

1. **Generate challenge data:**
   ```bash
   python generate_ciphertexts.py
   ```

2. **Study the protocol:**
   - Read `protocol_spec.md` carefully
   - Analyze `falconshield.py` for weaknesses
   - Note the security warnings in the spec

3. **Use the encryption oracle:**
   ```bash
   python encryption_oracle.py
   ```

4. **Implement your attack:**
   - Edit `solution_template.py`
   - Implement your cryptanalysis techniques
   - Run your solution

## Challenge Data

After generation, you will have:

- **10 public keys** (LWE key pairs)
- **100 ciphertexts** (encrypted with various keys)
- **10 known plaintext-ciphertext pairs** (for analysis)

## Scoring

| Criterion | Points |
|---|---|
| Vulnerability identification | 30 |
| Number of ciphertexts decrypted | 40 |
| Quality of security assessment | 20 |
| Proposed fixes | 10 |

## Hints

1. **LWE Parameters**: The chosen parameters (n=256, q=3329, σ=2.0) are below current security recommendations. Can you exploit this?

2. **Custom Block Cipher**: FalconBlock uses a custom S-box and key schedule. Custom cryptography is notoriously hard to get right.

3. **Known Plaintext**: You have 10 plaintext-ciphertext pairs. What can you learn from them?

4. **Encryption Oracle**: You have 100 queries to the encryption oracle. Use them wisely.

## Deliverables

1. **Vulnerability Report**: Detailed description of each vulnerability found
2. **Decrypted Ciphertexts**: At least 1 ciphertext fully decrypted
3. **Security Assessment**: Rating of each protocol component
4. **Proposed Fixes**: How to make the protocol secure

## Warning

⚠️ This protocol contains **intentional vulnerabilities** for educational purposes. Do NOT use FalconShield or any similar custom cryptography in production systems. Always use well-analyzed, standardized cryptographic protocols (TLS, Signal, etc.).
