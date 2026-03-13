# FalconShield Cryptographic Protocol Specification

## 1. Overview

FalconShield is a hybrid cryptographic protocol designed for secure communication. It combines a custom Learning With Errors (LWE) based key exchange with a proprietary block cipher for symmetric encryption and HMAC-SHA256 for message authentication.

## 2. Key Exchange (LWE-based)

### 2.1 Parameters
- **n**: 256 (dimension of secret vector)
- **q**: 3329 (modulus)
- **σ**: 2.0 (Gaussian noise standard deviation)
- **m**: 512 (number of samples)

### 2.2 Key Generation
1. Generate secret key `s` ← random vector in `Z_q^n`
2. Generate matrix `A` ← random matrix in `Z_q^{m×n}`
3. Generate error vector `e` ← discrete Gaussian in `Z_q^m` with parameter σ
4. Compute `b = A·s + e mod q`
5. Public key: `(A, b)`
6. Private key: `s`

### 2.3 Encapsulation
1. Generate ephemeral secret `s'` ← random vector in `Z_q^n`
2. Generate error vectors `e', e''` ← discrete Gaussian
3. Compute `u = A^T·s' + e' mod q`
4. Compute `v = b^T·s' + e'' mod q`
5. Shared secret derived from `v` (quantized to bits)
6. Ciphertext: `(u, v)`

### 2.4 Decapsulation
1. Compute `v' = v - s^T·u mod q`
2. Shared secret derived from `v'` (same quantization)

### 2.5 Vulnerability Note
⚠️ **Warning**: The noise parameter σ=2.0 with n=256 and q=3329 may be insufficient for security against lattice reduction attacks. Standard LWE recommendations suggest larger parameters for post-quantum security.

## 3. Symmetric Encryption (FalconBlock)

### 3.1 Structure
- **Block size**: 256 bits (32 bytes)
- **Key size**: 128 bits (16 bytes)
- **Rounds**: 12
- **Mode**: CBC with random IV

### 3.2 Round Function
Each round consists of:
1. **SubBytes**: Custom S-box (8-bit, bijective)
2. **ShiftRows**: Row permutation
3. **MixColumns**: Matrix multiplication over GF(2^8)
4. **AddRoundKey**: XOR with round key

### 3.3 Key Schedule
- Expands 128-bit key to 13 round keys (12 rounds + initial whitening)
- Uses custom key schedule algorithm with rotation and S-box substitution

### 3.4 Vulnerability Note
⚠️ **Warning**: The custom S-box and key schedule have not been publicly analyzed. Custom block ciphers often contain differential or linear characteristics that reduce security.

## 4. Message Authentication (HMAC-SHA256)

### 4.1 MAC Computation
```
MAC = HMAC-SHA256(key=mac_key, message=ciphertext)
```

### 4.2 MAC Key Derivation
The MAC key is derived from the shared secret using HKDF-SHA256.

## 5. Complete Protocol Flow

### 5.1 Encryption
1. Perform LWE key exchange to obtain shared secret
2. Derive encryption key and MAC key from shared secret using HKDF
3. Generate random IV (16 bytes)
4. Encrypt plaintext using FalconBlock-CBC with encryption key and IV
5. Compute MAC over (IV || ciphertext) using MAC key
6. Output: (IV, ciphertext, MAC)

### 5.2 Decryption
1. Perform LWE key exchange to obtain shared secret
2. Derive encryption key and MAC key from shared secret using HKDF
3. Verify MAC over (IV || ciphertext)
4. If MAC valid, decrypt ciphertext using FalconBlock-CBC
5. Output: plaintext or ERROR

## 6. Security Considerations

### 6.1 Known Issues
1. **LWE Parameters**: The chosen parameters (n=256, q=3329, σ=2.0) are below current NIST recommendations for post-quantum security.
2. **Custom Block Cipher**: FalconBlock has not undergone public cryptanalysis. Custom ciphers are notoriously difficult to secure.
3. **Timing Attacks**: The reference implementation may be vulnerable to timing attacks due to non-constant-time operations.

### 6.2 Recommendations
1. Increase LWE dimension to at least n=512
2. Use standardized block cipher (AES-256) instead of custom FalconBlock
3. Implement constant-time operations throughout
4. Add authenticated encryption mode (e.g., GCM) instead of CBC + HMAC

## 7. Reference Implementation

See `falconshield.py` for the reference implementation.

## 8. Test Vectors

See `test_vectors/` directory for sample plaintext-ciphertext pairs.
