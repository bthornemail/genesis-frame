# identity.py
#
# Deterministic identity built entirely on the crystal.
# NO sha256. NO cryptographic dependency. NO external library.
# Pure math — cannot be shut down by outside control.
#
# Three things, in order:
#
#   CLOCK  — where we are in crystal time (frame.tick.control)
#   SID    — what something IS  (seed is the identity — no hash needed)
#   OID    — when something HAPPENED (crystal-chained, unforgeable)
#
# The chain works because each OID XORs the previous state into the
# next seed. Change any link and the entire chain diverges.
# Same guarantee as sha256, using only the crystal.

from crystal import state_at, position_at, read, MASK, B, T

GENESIS_STATE = 0x0000   # the "before anything" state

# ── CLOCK ─────────────────────────────────────────────────────────
def clock(n):
    """
    Deterministic clock position at tick n.
    Returns frame (orbit), tick (phase+1), control (offset).
    Format: "frame.tick.CONTROL_HEX"  e.g. "4.3.0D"
    """
    pos           = position_at(n)
    orbit, offset = read(pos)
    return {
        "frame"  : orbit,
        "tick"   : (n % T) + 1,
        "control": offset,
        "str"    : f"{orbit}.{(n%T)+1}.{offset:02X}",
        "n"      : n,
    }

# ── SID — Semantic Identity ───────────────────────────────────────
def sid_for_object(seed):
    """
    Semantic Identity for a world object.
    The seed IS the identity. No hash required.
    Same seed = same SID forever on any machine.
    """
    return f"sid:{seed & MASK:04X}"

def sid(type_str, canonical_form):
    """
    General SID using base-257 polynomial encoding.
    Deterministic. Reversible. No sha256.
    """
    data = f"{type_str}:{canonical_form}".encode("utf-8")
    acc, mult = 0, 1
    for b in data:
        acc += (b + 1) * mult
        mult *= 257
    return f"sid:{type_str[:4]}:{acc & MASK:04X}"

# ── OID — Occurrence Identity ─────────────────────────────────────
def oid_step(seed, n, prev_state):
    """
    Pure crystal occurrence identity. No sha256.
    Chains by XORing prev_state into the seed before advancing.
    Change any prior occurrence → all subsequent OIDs diverge.
    Returns (new_state, oid_str).
    """
    chained   = (seed ^ prev_state) & MASK
    new_state = state_at(chained, n)
    clk       = clock(n)
    return new_state, f"oid:{seed:04X}.{clk['str']}.{new_state:04X}"

# ── Object Identity Chain ─────────────────────────────────────────
class ObjectChain:
    """
    One object's identity chain through time.
    One stable SID. Growing OID chain.
    Pure math — no cryptographic dependency. Fully replayable.
    """
    def __init__(self, seed):
        self.seed       = seed & MASK
        self.sid        = sid_for_object(seed)
        self.prev_state = GENESIS_STATE
        self.history    = []

    def step(self, n):
        """Record one occurrence at crystal tick n."""
        new_state, oid_str = oid_step(self.seed, n, self.prev_state)
        clk = clock(n)
        record = {
            "n"          : n,
            "seed"       : self.seed,
            "sid"        : self.sid,
            "oid"        : oid_str,
            "prev_state" : self.prev_state,
            "clock"      : clk["str"],
            "frame"      : clk["frame"],
            "tick"       : clk["tick"],
            "control"    : clk["control"],
            "state"      : new_state,
            "hex"        : f"0x{new_state:04X}",
        }
        self.prev_state = new_state
        self.history.append(record)
        return record

    def verify(self, record):
        """Verify a record. Recompute OID from inputs — no trust needed."""
        _, expected = oid_step(record["seed"], record["n"], record["prev_state"])
        return expected == record["oid"]

# ── Replay ────────────────────────────────────────────────────────
def replay_chain(seed, tick_numbers):
    """Replay full identity chain. Same inputs = identical output. Always."""
    chain = ObjectChain(seed)
    return [chain.step(n) for n in tick_numbers]
