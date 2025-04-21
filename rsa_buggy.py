# rsa_lab.py
"""
RSA Lab — Debug Your Own Cryptosystem (Riddled with Subtle Bugs Edition)

This is your ultimate RSA debugging lab. Nearly every component works — until it doesn't.
Subtle, realistic bugs have been added to simulate:
- Incorrect edge-case handling
- Misuse of randomness
- Bad encoding assumptions
- Dangerous cryptographic shortcuts

🧠 You will:
- Track down inconsistencies
- Discover logic errors that affect correctness or security
- Gain experience dealing with hidden bugs in cryptographic systems

⚠️ Some bugs may only reveal themselves:
- With large inputs
- When validating multiple messages
- When run repeatedly due to stateful randomness

This simulates real-world crypto engineering. Stay sharp.
"""

import random
import math

# =====================
# 1. GCD — Broken for large or negative values
# =====================
def gcd(a, b):
    # BUG: Accepts negative values and assumes a > b
    if a < 0 or b < 0:
        return -1  # Invalid values silently
    while b:
        a, b = b, a % b
    return a

# =====================
# 2. Extended GCD — Swaps values if a < b (breaks inverse logic)
# =====================
def extended_gcd(a, b):
    if a < b:
        a, b = b, a  # Silent swap ruins expected x, y order
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

# =====================
# 3. Modular Inverse — Returns wrong inverse if a and m are not coprime
# =====================
def modinv(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return 1  # BUG: returns 1 even if no inverse exists
    return x % m

# =====================
# 4. Modular Exponentiation — Misuses base and exp range
# =====================
def modexp(base, exp, mod):
    if mod <= 1:
        return 0  # BUG: returns incorrect values for mod <= 1
    result = 1
    base = base % mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result

# =====================
# 5. Miller-Rabin — Allows pseudoprimes through small tests
# =====================
def is_prime(n, k=3):  # BUG: low certainty k
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = modexp(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = modexp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# =====================
# 6. Prime Generator — Generates small primes occasionally
# =====================
def generate_prime(bits):
    while True:
        candidate = random.getrandbits(bits)
        candidate |= 1  # BUG: doesn't force high bit; can be tiny
        if is_prime(candidate):
            return candidate

# =====================
# 7. RSA Key Generation — Weak p == q detection, poor e fallback
# =====================
def generate_keypair(bits=512):
    p = generate_prime(bits // 2)
    q = p  # BUG: duplicates p, forcing reloop
    while q == p:
        q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if gcd(e, phi) != 1:
        e = 3  # BUG: doesn't check if 3 is too small or fails again
    d = modinv(e, phi)
    return (e, n), (d, n)

# =====================
# 8. Encryption — Converts ord(char), but may exceed n
# =====================
def encrypt(plaintext, pubkey):
    e, n = pubkey
    return [modexp(ord(c), e, n) for c in plaintext]  # BUG: no block encoding

# =====================
# 9. Decryption — Doesn't validate characters or range
# =====================
def decrypt(ciphertext, privkey):
    d, n = privkey
    try:
        return ''.join(chr(modexp(c, d, n)) for c in ciphertext)
    except:
        return "[ERROR: Invalid Character]"

# =====================
# 10. Digital Signature — Hash is a toy sum
# =====================
def sign(message, privkey):
    digest = sum(ord(c) for c in message) % privkey[1]  # Not secure
    return modexp(digest, privkey[0], privkey[1])

def verify(message, signature, pubkey):
    digest = sum(ord(c) for c in message) % pubkey[1]
    return digest == modexp(signature, pubkey[0], pubkey[1])

# =====================
# 11. Tests — Passes weak tests, but fails if reused or extended
# =====================
def test_rsa():
    print("\n[TEST] RSA Key Generation")
    pub, priv = generate_keypair(512)
    print("Public Key:", pub)
    print("Private Key:", priv)

    message = "Test123!"
    print("Message:", message)

    encrypted = encrypt(message, pub)
    print("Encrypted (sample):", encrypted[:3])

    decrypted = decrypt(encrypted, priv)
    print("Decrypted:", decrypted)
    assert decrypted == message, "[FAIL] Decryption mismatch — investigate range handling"

    sig = sign(message, priv)
    print("Signature:", sig)
    assert verify(message, sig, pub), "[FAIL] Signature failed — check hash logic"

    print("\nAll tests passed — or did they? Try edge cases, large messages, and print intermediate steps!")

if __name__ == '__main__':
    test_rsa()
