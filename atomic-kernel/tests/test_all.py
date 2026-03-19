# tests/test_all.py
#
# Run with: python3 tests/test_all.py
# All tests must pass before you ship anything.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crystal import tick, position_at, read, state_at, run, W, T, B, MASK
from identity import clock, sid, sid_for_object, oid_step, ObjectChain, replay_chain, GENESIS_STATE as GENESIS
from kernel import delta, replay, SUPPORTED_WIDTHS, check_parity
from observer import observe, SEEDS
from world import frame, trace
import os

PASS = 0
FAIL = 0

def check(name, condition):
    global PASS, FAIL
    if condition:
        print(f"  ✓ {name}")
        PASS += 1
    else:
        print(f"  ✗ FAIL: {name}")
        FAIL += 1

print("=" * 55)
print("ATOMIC KERNEL — FULL TEST SUITE")
print("=" * 55)

# ── Kernel law (Coq-certified) ────────────────────────────────────
print("\nKernel law (Coq: delta_deterministic, replay_deterministic, replay_len):")
check("supported widths defined",       SUPPORTED_WIDTHS == {16,32,64,128,256})
check("delta deterministic",            delta(16, 0x0001) == delta(16, 0x0001))
check("delta bounded 16-bit",           delta(16, 0x0001) <= 0xFFFF)
check("replay length = steps",          len(replay(16, 0x0001, 8)) == 8)
check("replay 32-bit length",           len(replay(32, 0x0001, 8)) == 8)
check("replay starts at masked seed",   replay(16, 0x0001, 1)[0] == 0x0001)
# Golden parity vectors — proves this matches the Coq proof exactly
golden = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'golden_parity.json')
check("parity vectors exist",           os.path.exists(golden))
if os.path.exists(golden):
    check("all parity vectors pass",    check_parity(golden))

# width=16 first 4 steps match known Coq output
seq16 = replay(16, 0x0001, 4)
check("16-bit step 0 = 0x0001",         seq16[0] == 0x0001)
check("16-bit step 1 = 0x5D17",         seq16[1] == 0x5D17)
check("16-bit step 2 = 0x98CC",         seq16[2] == 0x98CC)
check("16-bit step 3 = 0xCCD3",         seq16[3] == 0xCCD3)

# ── Crystal ───────────────────────────────────────────────────────
print("\nCrystal:")
check("period T = 8",           T == 8)
check("orbit weight W = 36",    W == 36)
check("block B sums to 36",     sum(B) == 36)
check("block B length 8",       len(B) == 8)
check("position_at(0) = 0",     position_at(0) == 0)
check("position_at(8) = 36",    position_at(8) == 36)
check("position_at(16) = 72",   position_at(16) == 72)
check("read(36) = (1,0)",        read(36) == (1, 0))
check("read(72) = (2,0)",        read(72) == (2, 0))
check("state bounded",          all(state_at(1, n) <= MASK for n in range(32)))
check("state_at period=16",     state_at(0x0001, 16) == 0x0001)
check("determinism",            state_at(0x0001, 100) == state_at(0x0001, 100))

rows = run(0x0001, 8)
check("run returns 8 rows",     len(rows) == 8)
check("run orbit 0 in first spin", all(r['orbit'] == 0 for r in rows))

# ── Identity ──────────────────────────────────────────────────────
print("\nIdentity:")
c0 = clock(0)
c8 = clock(8)
check("clock(0) frame=0",       c0['frame'] == 0)
check("clock(0) tick=1",        c0['tick'] == 1)
check("clock(8) frame=1",       c8['frame'] == 1)
check("clock string format",    c0['str'] == "0.1.00")
check("clock deterministic",    clock(42)['str'] == clock(42)['str'])

s1 = sid_for_object(0x0001)
s2 = sid_for_object(0xCAFE)
check("SID is sid: prefixed",    s1.startswith("sid:"))
check("SID stable",              sid_for_object(0x0001) == sid_for_object(0x0001))
check("Different seeds → different SIDs", s1 != s2)

chain = ObjectChain(0x0001)
r0 = chain.step(0)
r8 = chain.step(8)
check("OID is oid: prefixed",    r0['oid'].startswith("oid:"))
check("OID changes each step",   r0['oid'] != r8['oid'])
check("prev chains via state",   r8['prev_state'] == r0['state'])
check("first prev = genesis",    r0['prev_state'] == GENESIS)
check("verify r0",               chain.verify(r0))
check("verify r8",               chain.verify(r8))

# Replay produces identical chain
replayed = replay_chain(0x0001, [0, 8])
check("replay OID[0] matches",   replayed[0]['oid'] == r0['oid'])
check("replay OID[1] matches",   replayed[1]['oid'] == r8['oid'])

# ── Observer ──────────────────────────────────────────────────────
print("\nObserver:")
o = observe(0x0001, 0)
check("observe returns seed",    o['seed'] == 0x0001)
check("observe returns hex",     o['hex'] == '0x0001')
check("observe x in [0,63]",     0 <= o['x'] <= 63)
check("observe y >= 0",          o['y'] >= 0)
check("observe has color",       o['color'].startswith('rgb('))
check("observe has symbol",      len(o['symbol']) == 1)
check("observe deterministic",   observe(0x0001, 42) == observe(0x0001, 42))
check("16 seeds defined",        len(SEEDS) == 16)
check("all seeds unique",        len(set(SEEDS)) == 16)

# ── World ─────────────────────────────────────────────────────────
print("\nWorld:")
f0 = frame(0)
check("frame returns 16 objects",   len(f0) == 16)
check("all objects have orbit",     all('orbit' in o for o in f0))
check("frame deterministic",        frame(42) == frame(42))
check("frame 0 != frame 8",         frame(0) != frame(8))

t0 = trace(0, 4)
check("trace returns 4 frames",     len(t0) == 4)
check("trace frame 0 == frame(0)",  t0[0] == frame(0))
check("trace frame 3 == frame(3)",  t0[3] == frame(3))

# ── Final ─────────────────────────────────────────────────────────
print()
print("=" * 55)
total = PASS + FAIL
print(f"  {PASS}/{total} passed  {'✓ ALL GOOD' if FAIL == 0 else f'✗ {FAIL} FAILED'}")
print("=" * 55)
sys.exit(0 if FAIL == 0 else 1)
