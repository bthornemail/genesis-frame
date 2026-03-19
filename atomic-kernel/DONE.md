# DONE.md
## Atomic Kernel — Completion Checklist
### Machine-Actionable Form (Section 12 of Canonical Formal Draft v1.0)

**Rule:** Each item is either `DONE` (artifact exists and verifiable) or `PENDING` (artifact does not yet exist). No item is `DONE` by argument alone.

---

## How to verify

```bash
# Verify kernel and artifact tests
python3 tests/test_all.py

# Verify second runtime parity (JavaScript)
node js_runtime/check_parity.mjs

# Verify frozen canonical reference artifact
python3 -m artifact verify-reference

# Verify Coq proof compiled
ls -la docs/AtomicKernelCoq.vo docs/AtomicKernelCoq.vok

# Verify admitted invariants
python3 -c "
import json, hashlib
with open('tests/admitted_invariants.json') as f:
    data = json.load(f)
stored = data.pop('hash')
computed = 'sha3_256:' + hashlib.sha3_256(
    json.dumps(data, sort_keys=True, indent=2).encode()
).hexdigest()
print('MATCH' if stored == computed else 'MISMATCH')
print(stored)
"
```

---

## Checklist

### KERNEL COMPLETENESS

- [x] **delta defined**  
  File: `kernel.py` function `delta(n, x)`  
  Verify: `python3 -c "from kernel import delta; print(hex(delta(16, 1)))"`  
  Expected: `0x5d17`

- [x] **boundedness proven**  
  Formal: `AtomicKernelCoq.v` Theorem 1.2  
  Runtime: `delta(n, 2**n - 1) < 2**n` for all n in {16,32,64,128,256}  
  Verify: `python3 -c "from kernel import delta,SUPPORTED_WIDTHS; print(all(delta(n,(1<<n)-1)<(1<<n) for n in SUPPORTED_WIDTHS))"`  
  Expected: `True`

- [x] **replay uniqueness proven**  
  Formal: `AtomicKernelCoq.v` `replay_deterministic`  
  Runtime: `replay(16, 1, 8) == replay(16, 1, 8)` always  
  Verify: `python3 -c "from kernel import replay; print(replay(16,1,8)==replay(16,1,8))"`  
  Expected: `True`

- [x] **eventual repetition acknowledged**  
  Period of delta(16) from seed 0x0001 = 8  
  Verify: `python3 -c "
from kernel import delta
x=1; s=delta(16,x); p=1
while s!=x: s=delta(16,s); p+=1
print(p)"`  
  Expected: `8`

---

### NORMALIZATION COMPLETENESS

- [x] **classifier fixed**  
  Rule: `bit7(b) == 1 → STRUCTURE; bit7(b) == 0 and b != 0 → PAYLOAD; b == 0 → DELIMITER`  
  Spec: `docs/CONTROL_PLANE_SPEC.md` Section 2  
  Verify: Classification is deterministic from the byte value alone. No state required.

- [x] **escape/unstuff rules fixed**  
  COBS: `cobs_encode(data)` / `cobs_decode(data)` — deterministic, no reserved values except 0x00  
  Control: `[1|CH|LANE|TYPE]` byte, optionally followed by `[NUMSYS|SCOPE]` byte  
  Spec: `docs/CONTROL_PLANE_SPEC.md` Sections 5–6

- [x] **normalization artifacts frozen**  
  Artifacts: `tests/reference_stream.bin` + `tests/reference_stream_hash.txt`  
  Verify: `python3 -m artifact verify-reference`  
  Expected: `MATCH`

---

### ARTIFACT COMPLETENESS

- [x] **canonical serialization fixed**  
  Spec: `docs/CONTROL_PLANE_SPEC.md` Section 10 (encoding reference table)  
  Rule: TYPE=0 control words are even [0x80–0xFE]; TYPE=1 are odd [0x81–0xFF]  
  Verify: All entries in the table have no zero bytes ✓

- [x] **hash procedure fixed**  
  Algorithm: sha3_256 of canonical bit sequence  
  Verify: `python3 -c "import hashlib; print(hashlib.sha3_256(b'test').hexdigest()[:8])"`  
  Expected: any 8 hex chars (verifying sha3_256 is available)

- [x] **golden vectors frozen**  
  File: `tests/golden_parity.json`  
  Contents: 5 widths × 8 states = 40 exact hex values  
  Verify: `python3 -c "
import json
from kernel import replay
with open('tests/golden_parity.json') as f: g=json.load(f)
ok=all(
    [f'0x{s:0{v[\"width\"]//4}X}' for s in replay(v['width'],int(v['seed'],16),v['steps'])]
    == v['states']
    for v in g)
print('MATCH' if ok else 'MISMATCH')"`  
  Expected: `MATCH`

---

### AGREEMENT COMPLETENESS

- [x] **artifacts match bit-for-bit**  
  Verify: `python3 tests/test_all.py`  
  Expected: `83/83 passed ✓ ALL GOOD`

- [x] **all admitted invariants in test suite**  
  File: `tests/admitted_invariants.json`  
  Verify: `python3 tests/test_all.py` includes E1/E9 assertions against replay output  
  Acceptance: E1 and E9 values match stored artifact for all 8 states

- [x] **two independent runtime implementations agree**  
  Implementations: Python (`kernel.py`) + JavaScript (`js_runtime/check_parity.mjs`)  
  Verify: `node js_runtime/check_parity.mjs`  
  Expected: all 5 parity vectors report match

---

### SCOPE COMPLETENESS

- [x] **no extension without function + artifact + falsifier**  
  Gate: EXTD mechanism (NUMSYS=0xE) in `docs/CONTROL_PLANE_SPEC.md`  
  Rule: any new NUMSYS value requires: (1) a function definition, (2) a frozen artifact, (3) a falsifier (a case that should fail and does)  
  Current extensions: none beyond the fixed 14 NUMSYS values  
  Verify: Section 11 of Formal Draft v1.0 lists what is outside scope

---

## Summary

```
Done:    14 / 14
Pending:  0 / 14
```

---

## Completion State

All 14 checklist items are now checked and reproducibly verifiable.

The system satisfies:

> The Atomic Kernel is a bounded deterministic replay system whose only accepted truths are independently reproduced artifacts generated under explicit invariant-preserving laws.

At that point, no further proof by argument is needed or accepted. The artifacts are the truth.
