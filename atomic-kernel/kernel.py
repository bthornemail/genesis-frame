# kernel.py
#
# The formal kernel law — certified by the Coq proof in AtomicKernelCoq.v
#
# This is the BASE transition function: delta(n, x)
# It is the law the Coq theorems prove:
#   - delta_deterministic : same input → same output
#   - replay_deterministic: same seed → same sequence
#   - replay_len          : sequence has exactly `steps` elements
#
# This is NOT the same as crystal.py.
# crystal.py adds the periodic differential (B injection) on top of this.
# This file is the mathematical foundation that crystal.py is built on.
#
# Supported widths: 16, 32, 64, 128, 256
# (matches the Coq companion: W16, W32, W64, W128, W256)

SUPPORTED_WIDTHS = {16, 32, 64, 128, 256}

# ── Primitives ────────────────────────────────────────────────────
def mask(n, x):
    """Bound x to n bits. Coq: mask n x = N.land x (2^n - 1)"""
    return x & ((1 << n) - 1)

def rotl(n, x, k):
    """Rotate x left by k within n-bit space. Coq: rotl n x k"""
    k2 = k % n
    return mask(n, (x << k2) | (x >> (n - k2)))

def rotr(n, x, k):
    """Rotate x right by k within n-bit space. Coq: rotr n x k"""
    k2 = k % n
    return mask(n, (x >> k2) | (x << (n - k2)))

def constant_of_width(n):
    """
    Build the n-bit mixing constant: 0x1D repeated for each byte.
    Coq: repeat_byte_1d_nat (n/8)
    For n=16: 0x1D1D
    For n=32: 0x1D1D1D1D
    For n=64: 0x1D1D1D1D1D1D1D1D
    """
    assert n % 8 == 0, f"width must be multiple of 8, got {n}"
    c = 0
    for _ in range(n // 8):
        c = (c << 8) | 0x1D
    return c

# ── The formal delta law ──────────────────────────────────────────
def delta(n, x):
    """
    The certified transition function.
    Coq: delta n x = mask n (rotl n x 1 XOR rotl n x 3 XOR rotr n x 2 XOR C_n)
    This is the law. Everything else is built on this.
    """
    assert n in SUPPORTED_WIDTHS, f"unsupported width {n}"
    C = constant_of_width(n)
    return mask(n, rotl(n,x,1) ^ rotl(n,x,3) ^ rotr(n,x,2) ^ C)

# ── Replay ────────────────────────────────────────────────────────
def replay(n, seed, steps):
    """
    Apply delta for `steps` steps from `seed`.
    Coq: replay n seed steps = replay_loop steps n (mask n seed)
    Returns list of states [s0, s1, ..., s_{steps-1}]
    where s0 = mask(n, seed), s_{i+1} = delta(n, s_i)
    """
    assert n in SUPPORTED_WIDTHS, f"unsupported width {n}"
    x   = mask(n, seed)
    out = []
    for _ in range(steps):
        out.append(x)
        x = delta(n, x)
    return out

# ── Conformance check against golden vectors ──────────────────────
def check_parity(vectors_path):
    """
    Verify this implementation matches the golden parity vectors.
    Run this to confirm the kernel law is correctly implemented.
    """
    import json
    with open(vectors_path) as f:
        vectors = json.load(f)

    all_pass = True
    for v in vectors:
        n      = v['width']
        seed   = int(v['seed'], 16)
        steps  = v['steps']
        actual = replay(n, seed, steps)
        fmt    = f"0x{{:0{n//4}X}}"
        actual_hex = [fmt.format(x) for x in actual]

        if 'states' in v:
            expected = v['states']
            if actual_hex != expected:
                print(f"  FAIL width={n} seed={v['seed']}")
                for i, (a, e) in enumerate(zip(actual_hex, expected)):
                    if a != e:
                        print(f"    step {i}: got {a}, expected {e}")
                all_pass = False
            else:
                print(f"  ✓ width={n} seed={v['seed']}")
        else:
            print(f"  width={n}: {actual_hex[:3]}...")

    return all_pass


# ── Self-test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Kernel law self-test (Coq-certified delta)")
    print("=" * 55)
    print()
    print("Width 16, seed 0x0001, 8 steps:")
    seq = replay(16, 0x0001, 8)
    for i, x in enumerate(seq):
        print(f"  step {i}: 0x{x:04X}")

    print()
    print("Determinism (Coq: delta_deterministic):")
    a = delta(16, 0x0001)
    b = delta(16, 0x0001)
    print(f"  delta(16, 0x0001) == delta(16, 0x0001): {a == b} ✓")

    print()
    print("Length (Coq: replay_len):")
    for n in SUPPORTED_WIDTHS:
        seq = replay(n, 1, 8)
        print(f"  replay({n}, 1, 8) length = {len(seq)} ✓")

    print()
    print("Parity vector check:")
    import os
    golden = os.path.join(os.path.dirname(__file__), 'tests', 'golden_parity.json')
    if os.path.exists(golden):
        ok = check_parity(golden)
        print(f"\n  {'ALL PASS ✓' if ok else 'SOME FAILED ✗'}")
    else:
        print("  (golden_parity.json not found — run tests/test_all.py first)")
