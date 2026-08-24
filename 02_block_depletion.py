"""
Option 1 (Locked) regeneration pipeline:
  Step 1: Fixed block pool with Hare–Niemeyer N_c counts (N_pool = 37,070)
  Step 2A: Deterministic partition of blocks into 7 shovel sub-pools
  Step 2B: Deterministic shovel queue ordering using intra-shovel Markov
            (80% same-combo, 15% Secondary-zone adjacency, 5% Tertiary-zone adjacency)
  Step 3: Assign each truck trip event to a shovel (Option A weighted dispatch by
          shovel remaining tonnage) and deplete the active block using Payload_t
  Step 4: Validate counts and depletion behavior

Inputs (read-only):
  - truck_simulation_365_days.csv

Outputs (new files):
  - block_pool_option1_fixed_365days.csv
  - shovel_subpools_option1_fixed_365days.csv
  - shovel_queues_option1_fixed_365days.csv
  - truck_block_depletion_option1_fixed_365days.csv
  - option1_validation_report_365days.txt

This script does NOT modify:
  - truck_time_365days.py
  - truck_simulation_365_days.csv
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


# ============================================================
# Global settings
# ============================================================

SEED = 42
random.seed(SEED)

TIMELINE_FILE = "truck_simulation_365_days.csv"

OUT_POOL_FILE = "block_pool_option1_fixed_365days.csv"
OUT_SUBPOOL_FILE = "shovel_subpools_option1_fixed_365days.csv"
OUT_QUEUE_FILE = "shovel_queues_option1_fixed_365days.csv"
OUT_TRUCK_BLOCK_FILE = "truck_block_depletion_option1_fixed_365days.csv"
OUT_VALIDATION_REPORT = "option1_validation_report_365days.txt"

BLOCK_VOLUME_M3 = 15 * 15 * 15  # 3,375 m^3


# ============================================================
# Step 1 inputs: combination volume% -> Hare–Niemeyer N_c
# ============================================================

# Locked N_c allocation from the user’s Hare–Niemeyer table (sum = 37,070).
N_C_BY_COMBO: Dict[str, int] = {
    # Andesite
    "Andesite|Phyllic": 6673,
    "Andesite|Propylitic": 4449,
    "Andesite|Potassic": 2966,
    "Andesite|Argillic": 1668,
    "Andesite|Advanced Argillic": 445,
    "Andesite|Sodic-Calcic": 149,
    # QMP
    "QMP|Potassic": 5561,
    "QMP|Phyllic": 3707,
    "QMP|Argillic": 1298,
    "QMP|Propylitic": 556,
    "QMP|Advanced Argillic": 297,
    "QMP|Sodic-Calcic": 74,
    # Granodiorite
    "Granodiorite|Phyllic": 2225,
    "Granodiorite|Propylitic": 1854,
    "Granodiorite|Potassic": 742,
    "Granodiorite|Argillic": 297,
    "Granodiorite|Advanced Argillic": 74,
    "Granodiorite|Sodic-Calcic": 37,
    # Diorite
    "Diorite|Propylitic": 1112,
    "Diorite|Phyllic": 927,
    "Diorite|Potassic": 371,
    "Diorite|Argillic": 186,
    "Diorite|Advanced Argillic": 37,
    "Diorite|Sodic-Calcic": 112,
    # Granite
    "Granite|Propylitic": 556,
    "Granite|Phyllic": 371,
    "Granite|Potassic": 149,
    "Granite|Argillic": 149,
    "Granite|Advanced Argillic": 19,
    "Granite|Sodic-Calcic": 19,
}

# Pool size derived from the locked N_c allocation dict (sum).
N_POOL = sum(N_C_BY_COMBO.values())


# Density ranges min/max (t/m3) for each (Lithology, Alteration) combination.
# Source: the bulk density range table provided by the user (Gemini).
DENSITY_RANGES: Dict[Tuple[str, str], Tuple[float, float]] = {
    ("Andesite", "Potassic"): (2.75, 2.90),
    ("Andesite", "Phyllic"): (2.65, 2.82),
    ("Andesite", "Propylitic"): (2.70, 2.85),
    ("Andesite", "Argillic"): (2.48, 2.65),
    ("Andesite", "Advanced Argillic"): (2.32, 2.55),
    ("Andesite", "Sodic-Calcic"): (2.80, 2.98),

    ("Diorite", "Potassic"): (2.80, 2.95),
    ("Diorite", "Phyllic"): (2.72, 2.88),
    ("Diorite", "Propylitic"): (2.78, 2.92),
    ("Diorite", "Argillic"): (2.55, 2.70),
    ("Diorite", "Advanced Argillic"): (2.40, 2.60),
    ("Diorite", "Sodic-Calcic"): (2.88, 3.02),

    ("Granodiorite", "Potassic"): (2.68, 2.82),
    ("Granodiorite", "Phyllic"): (2.62, 2.76),
    ("Granodiorite", "Propylitic"): (2.66, 2.80),
    ("Granodiorite", "Argillic"): (2.45, 2.60),
    ("Granodiorite", "Advanced Argillic"): (2.30, 2.50),
    ("Granodiorite", "Sodic-Calcic"): (2.74, 2.88),

    ("QMP", "Potassic"): (2.62, 2.75),
    ("QMP", "Phyllic"): (2.55, 2.70),
    ("QMP", "Propylitic"): (2.60, 2.72),
    ("QMP", "Argillic"): (2.38, 2.52),
    ("QMP", "Advanced Argillic"): (2.25, 2.45),
    ("QMP", "Sodic-Calcic"): (2.68, 2.82),

    ("Granite", "Potassic"): (2.60, 2.73),
    ("Granite", "Phyllic"): (2.52, 2.67),
    ("Granite", "Propylitic"): (2.58, 2.70),
    ("Granite", "Argillic"): (2.35, 2.50),
    ("Granite", "Advanced Argillic"): (2.20, 2.42),
    ("Granite", "Sodic-Calcic"): (2.65, 2.78),
}


# ============================================================
# Operational zone mapping (locked)
# ============================================================
ZONE_CORE = "CORE"
ZONE_MARGIN = "MARGIN"
ZONE_OUTER = "OUTER"
ZONE_CAP = "CAP"


def combo_zone(combo_key: str) -> str:
    lith, alt = combo_key.split("|")

    # Core Ore Zone (6): QMP {Potassic, Phyllic, Propylitic} + Granodiorite {Potassic, Phyllic, Propylitic}
    if lith == "QMP" and alt in {"Potassic", "Phyllic", "Propylitic"}:
        return ZONE_CORE
    if lith == "Granodiorite" and alt in {"Potassic", "Phyllic", "Propylitic"}:
        return ZONE_CORE

    # Volcanic Margin Zone (6): Andesite {Potassic, Phyllic, Propylitic} + Diorite {Potassic, Phyllic, Propylitic}
    if lith == "Andesite" and alt in {"Potassic", "Phyllic", "Propylitic"}:
        return ZONE_MARGIN
    if lith == "Diorite" and alt in {"Potassic", "Phyllic", "Propylitic"}:
        return ZONE_MARGIN

    # Outer Wall / Waste Zone (8): Granite {Potassic, Phyllic, Propylitic, Argillic}
    # plus argillic host variants: Andesite, Diorite, Granodiorite, QMP Argillic
    if lith == "Granite" and alt in {"Potassic", "Phyllic", "Propylitic", "Argillic"}:
        return ZONE_OUTER
    if alt == "Argillic" and lith in {"Andesite", "Diorite", "Granodiorite", "QMP"}:
        return ZONE_OUTER

    # Cap & Deep Roots Zone (10): Advanced Argillic + all Sodic-Calcic
    if alt in {"Advanced Argillic"}:
        return ZONE_CAP
    if alt in {"Sodic-Calcic"}:
        return ZONE_CAP

    raise ValueError(f"Unmapped combo zone for {combo_key}")


# ============================================================
# Shovel affinity weighting matrix (locked)
# ============================================================

# For each shovel: primary/secondary/tertiary operational zone targets.
SHOVEL_ROLE_ZONES: Dict[int, Tuple[str, str, str]] = {
    # Shovels 1–3: Primary Core, Secondary Margin, Tertiary Outer
    1: (ZONE_CORE, ZONE_MARGIN, ZONE_OUTER),
    2: (ZONE_CORE, ZONE_MARGIN, ZONE_OUTER),
    3: (ZONE_CORE, ZONE_MARGIN, ZONE_OUTER),
    # Shovels 4–5: Primary Margin, Secondary Core, Tertiary Outer
    4: (ZONE_MARGIN, ZONE_CORE, ZONE_OUTER),
    5: (ZONE_MARGIN, ZONE_CORE, ZONE_OUTER),
    # Shovel 6: Primary Outer, Secondary Margin, Tertiary Cap
    6: (ZONE_OUTER, ZONE_MARGIN, ZONE_CAP),
    # Shovel 7: Primary Cap, Secondary Outer, Tertiary Margin
    7: (ZONE_CAP, ZONE_OUTER, ZONE_MARGIN),
}


# ============================================================
# Two-tier intra-shovel adjacency definitions (locked)
# ============================================================

ALTERATION_CHAIN = ["Potassic", "Phyllic", "Propylitic", "Argillic", "Advanced Argillic"]
ALTERATION_ADJACENT = {
    alt: set()
    for alt in ALTERATION_CHAIN
}  # filled below
for i, alt in enumerate(ALTERATION_CHAIN):
    if i - 1 >= 0:
        ALTERATION_ADJACENT[alt].add(ALTERATION_CHAIN[i - 1])
    if i + 1 < len(ALTERATION_CHAIN):
        ALTERATION_ADJACENT[alt].add(ALTERATION_CHAIN[i + 1])


def combo_key_from_lith_alt(lith: str, alt: str) -> str:
    return f"{lith}|{alt}"


def lex_combo_key(combo_key: str) -> str:
    return combo_key  # already "Lith|Alt"


def pick_best_candidate_by_remaining(
    candidates: List[str],
    remaining_counts: Dict[str, int],
) -> str:
    # Deterministic: highest remaining count, then lexicographic combo_key.
    best = None
    best_cnt = -1
    for c in candidates:
        cnt = remaining_counts.get(c, 0)
        if cnt <= 0:
            continue
        if cnt > best_cnt:
            best_cnt = cnt
            best = c
        elif cnt == best_cnt and best is not None:
            if lex_combo_key(c) < lex_combo_key(best):
                best = c
    if best is None:
        raise RuntimeError("No available candidates with remaining > 0")
    return best


def adjacency_select_next_combo(
    current_combo: str,
    allowed_zone: str,
    remaining_counts: Dict[str, int],
) -> str:
    """
    Two-tier priority rule, restricted to candidates inside allowed_zone.
    - Tier 1: Same lithology, adjacent alteration chain
    - Tier 2: Same alteration, compatible lithology (implemented as: same alteration within allowed_zone)
    """
    cur_lith, cur_alt = current_combo.split("|")

    # All available candidates in allowed zone
    zone_candidates = [
        c for c, cnt in remaining_counts.items()
        if cnt > 0 and combo_zone(c) == allowed_zone
    ]
    if not zone_candidates:
        # Deterministic fallback: pick the best candidate across all remaining combos.
        any_candidates = [c for c, cnt in remaining_counts.items() if cnt > 0]
        if not any_candidates:
            raise RuntimeError("No candidates available at all (empty remaining_counts).")
        return pick_best_candidate_by_remaining(any_candidates, remaining_counts)

    # Tier 1: same lithology, adjacent alteration
    adj_alts = ALTERATION_ADJACENT.get(cur_alt, set())
    tier1 = [
        c for c in zone_candidates
        if c.split("|")[0] == cur_lith and c.split("|")[1] in adj_alts
    ]
    if tier1:
        return pick_best_candidate_by_remaining(tier1, remaining_counts)

    # Tier 2: same alteration, compatible lithology (available in allowed zone)
    tier2 = [
        c for c in zone_candidates
        if c.split("|")[1] == cur_alt and c.split("|")[0] != cur_lith
    ]
    if tier2:
        return pick_best_candidate_by_remaining(tier2, remaining_counts)

    # Fallback: any available candidate in the allowed zone
    return pick_best_candidate_by_remaining(zone_candidates, remaining_counts)


# ============================================================
# Data structures
# ============================================================

@dataclass
class Block:
    block_id: str
    combo_key: str
    lithology: str
    alteration: str
    bulk_density: float
    block_tonnage: float


def generate_block_pool() -> Tuple[Dict[str, List[Block]], pd.DataFrame]:
    pool_by_combo: Dict[str, List[Block]] = {k: [] for k in N_C_BY_COMBO.keys()}
    pool_rows = []

    next_bid = 1
    # Deterministic combo iteration for stable Block_ID assignment
    for combo_key in sorted(N_C_BY_COMBO.keys()):
        n_blocks = N_C_BY_COMBO[combo_key]
        lith, alt = combo_key.split("|")
        dmin, dmax = DENSITY_RANGES[(lith, alt)]

        for _ in range(n_blocks):
            bd = random.uniform(dmin, dmax)
            ton = bd * BLOCK_VOLUME_M3
            block_id = f"BLK-{next_bid:05d}"
            next_bid += 1

            b = Block(
                block_id=block_id,
                combo_key=combo_key,
                lithology=lith,
                alteration=alt,
                bulk_density=bd,
                block_tonnage=ton,
            )
            pool_by_combo[combo_key].append(b)

    # Shuffle within each combination for variability
    for k in pool_by_combo:
        random.shuffle(pool_by_combo[k])

    # Build a DataFrame for export
    for combo_key, blocks in pool_by_combo.items():
        for b in blocks:
            pool_rows.append({
                "Block_ID": b.block_id,
                "Lithology": b.lithology,
                "Alteration_Zone": b.alteration,
                "Combo_Key": b.combo_key,
                "Bulk_Density_t_m3": b.bulk_density,
                "Block_Tonnage_t": b.block_tonnage,
            })

    pool_df = pd.DataFrame(pool_rows)
    return pool_by_combo, pool_df


def hare_niemann_partition_counts(
    n_total: int,
    weights_by_shovel: Dict[int, float],
) -> Dict[int, int]:
    """
    Deterministic Hare–Niemeyer:
      - compute raw = n_total * weight
      - floor counts
      - distribute remaining 1s to largest remainders
      - tie by lower Shovel_ID
    """
    floors: Dict[int, int] = {}
    remainders: List[Tuple[float, int]] = []

    sum_floor = 0
    for s in sorted(weights_by_shovel.keys()):
        raw = n_total * weights_by_shovel[s]
        fl = math.floor(raw)
        floors[s] = fl
        sum_floor += fl
        remainders.append((raw - fl, s))

    remaining = n_total - sum_floor
    if remaining < 0:
        raise RuntimeError("Partition floors exceed n_total unexpectedly.")

    # Sort remainder desc, tie shovel_id asc
    remainders.sort(key=lambda x: (-x[0], x[1]))
    counts = floors.copy()

    for i in range(remaining):
        _rem, s = remainders[i]
        counts[s] += 1

    return counts


def generate_shovel_subpools(pool_by_combo: Dict[str, List[Block]]) -> Dict[int, Dict[str, List[Block]]]:
    """
    Partition each combo’s N_c blocks into 7 shovel sub-pools using the locked affinity weights
    and Hare–Niemeyer tie-break (lower Shovel_ID).
    """
    subpools: Dict[int, Dict[str, List[Block]]] = {s: {} for s in range(1, 8)}
    subpools_rows = []

    # For deterministic export we store pulled blocks explicitly later
    for combo_key, blocks in pool_by_combo.items():
        n_total = len(blocks)
        if n_total != N_C_BY_COMBO[combo_key]:
            raise RuntimeError("Block pool size mismatch for combo.")

        zone = combo_zone(combo_key)
        # Determine raw affinity weights for each shovel (based on which role the combo’s zone plays).
        # IMPORTANT: normalize so weights sum to 1.0 across shovels for this combo,
        # otherwise the Hare–Niemeyer partition would not sum to n_total cleanly.
        weights_by_shovel: Dict[int, float] = {}
        for s in range(1, 8):
            primary_zone, secondary_zone, tertiary_zone = SHOVEL_ROLE_ZONES[s]
            if zone == primary_zone:
                w = 0.80
            elif zone == secondary_zone:
                w = 0.15
            elif zone == tertiary_zone:
                w = 0.05
            else:
                w = 0.0
            weights_by_shovel[s] = w

        total_w = sum(weights_by_shovel.values())
        if total_w <= 0:
            raise RuntimeError(f"Total weight is 0 for combo={combo_key}; check zone mapping/affinities.")

        # Normalize
        for s in range(1, 8):
            weights_by_shovel[s] = weights_by_shovel[s] / total_w

        counts_by_shovel = hare_niemann_partition_counts(
            n_total=n_total,
            weights_by_shovel=weights_by_shovel,
        )

        # Pop blocks from the combo’s shuffled pool into shovel subpools
        idx = 0
        for s in range(1, 8):
            n_take = counts_by_shovel[s]
            if n_take <= 0:
                continue
            if n_take > (len(blocks) - idx):
                raise RuntimeError("Subpool take exceeds remaining blocks.")

            take = blocks[idx:idx + n_take]
            idx += n_take

            if combo_key not in subpools[s]:
                subpools[s][combo_key] = []
            subpools[s][combo_key].extend(take)

        if idx != len(blocks):
            raise RuntimeError("Not all blocks allocated in subpools.")

    # Export subpool membership
    for s in range(1, 8):
        for combo_key, blks in subpools[s].items():
            lith, alt = combo_key.split("|")
            for b in blks:
                subpools_rows.append({
                    "Shovel_ID": f"S{s}",
                    "Block_ID": b.block_id,
                    "Lithology": lith,
                    "Alteration_Zone": alt,
                    "Combo_Key": combo_key,
                    "Bulk_Density_t_m3": b.bulk_density,
                    "Block_Tonnage_t": b.block_tonnage,
                })

    pd.DataFrame(subpools_rows).to_csv(OUT_SUBPOOL_FILE, index=False)
    return subpools


def generate_shovel_queues(subpools: Dict[int, Dict[str, List[Block]]]) -> Dict[int, List[Block]]:
    """
    Build ordered block queues per shovel using locked intra-shovel Markov rule:
      - 80% attempt same-combo
      - 15% choose from secondary zone candidates using two-tier adjacency priority
      - 5% choose from tertiary zone candidates using two-tier adjacency priority

    Queue includes *all blocks* in that shovel’s subpool.
    """
    queues: Dict[int, List[Block]] = {s: [] for s in range(1, 8)}

    for s in range(1, 8):
        primary_zone, secondary_zone, tertiary_zone = SHOVEL_ROLE_ZONES[s]

        # Remaining counts per combo in this shovel
        remaining_counts: Dict[str, int] = {}
        combo_to_blocks: Dict[str, List[Block]] = {}
        total_blocks = 0

        for combo_key, blks in subpools[s].items():
            remaining_counts[combo_key] = len(blks)
            combo_to_blocks[combo_key] = blks[:]  # copy
            total_blocks += len(blks)

        if total_blocks <= 0:
            continue

        # Deterministic starting combination: max remaining count, tie lex
        current_combo = max(
            remaining_counts.keys(),
            key=lambda c: (remaining_counts[c], -ord(c[0])),
        )
        # The above key isn't ideal; enforce deterministic tie-break by lex:
        current_combo = sorted(
            remaining_counts.keys(),
            key=lambda c: (-remaining_counts[c], c)
        )[0]

        while len(queues[s]) < total_blocks:
            roll = random.random()

            if roll < 0.80:
                # Primary branch: try keep the same combination
                if remaining_counts.get(current_combo, 0) > 0:
                    next_combo = current_combo
                else:
                    # Fallback inside the Primary zone
                    next_combo = adjacency_select_next_combo(
                        current_combo=current_combo,
                        allowed_zone=primary_zone,
                        remaining_counts=remaining_counts,
                    )

            elif roll < 0.95:
                # Secondary branch
                next_combo = adjacency_select_next_combo(
                    current_combo=current_combo,
                    allowed_zone=secondary_zone,
                    remaining_counts=remaining_counts,
                )

            else:
                # Tertiary branch
                next_combo = adjacency_select_next_combo(
                    current_combo=current_combo,
                    allowed_zone=tertiary_zone,
                    remaining_counts=remaining_counts,
                )

            # Pop a block from that combo
            if remaining_counts.get(next_combo, 0) <= 0 or not combo_to_blocks[next_combo]:
                # Should not happen because adjacency_select_next_combo filters remaining>0,
                # but keep a deterministic fallback
                remaining_in_any = [c for c, cnt in remaining_counts.items() if cnt > 0]
                if not remaining_in_any:
                    break
                next_combo = sorted(remaining_in_any)[0]

            blk = combo_to_blocks[next_combo].pop()  # deterministic given seeded shuffle + pop order
            remaining_counts[next_combo] -= 1
            queues[s].append(blk)
            current_combo = next_combo

    # Export queues
    queue_rows = []
    for s in range(1, 8):
        for pos, blk in enumerate(queues[s], start=1):
            queue_rows.append({
                "Shovel_ID": f"S{s}",
                "Queue_Position": pos,
                "Block_ID": blk.block_id,
                "Lithology": blk.lithology,
                "Alteration_Zone": blk.alteration,
                "Combo_Key": blk.combo_key,
                "Bulk_Density_t_m3": blk.bulk_density,
                "Block_Tonnage_t": blk.block_tonnage,
                "Operational_Zone": combo_zone(blk.combo_key),
            })

    pd.DataFrame(queue_rows).to_csv(OUT_QUEUE_FILE, index=False)
    return queues


def assign_trips_and_deplete(
    queues: Dict[int, List[Block]],
    timeline_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Trip-by-trip depletion with Option A:
      Weighted dispatch to shovels by *remaining tonnage inventory* of each shovel.
    """
    # Prepare arrays for speed
    payload = timeline_df["Payload_t"].to_numpy(dtype=float)

    # Active pointer + remaining tonnage for each shovel
    shovel_ptr: Dict[int, int] = {s: 0 for s in range(1, 8)}
    shovel_remaining_total: Dict[int, float] = {}
    shovel_active_remaining: Dict[int, float] = {}

    for s in range(1, 8):
        q = queues.get(s, [])
        shovel_remaining_total[s] = sum(b.block_tonnage for b in q)
        if q:
            shovel_active_remaining[s] = q[0].block_tonnage
        else:
            shovel_active_remaining[s] = 0.0

    # For each shovel, keep a mutable remaining tonnage per block
    # (Store in dict: block_id -> remaining)
    remaining_by_block: Dict[str, float] = {}
    for s in range(1, 8):
        for b in queues.get(s, []):
            remaining_by_block[b.block_id] = b.block_tonnage

    n = len(timeline_df)
    # Preallocate for speed (object arrays for IDs/status, numeric arrays for masses)
    shovel_col = [None] * n
    block_id_col = [None] * n
    status_col = [None] * n
    bulk_density_col = [None] * n
    block_tonnage_col = [None] * n
    remaining_tonnage_col = [None] * n
    actual_payload_col = payload.copy()

    for i in range(n):
        # Choose shovel by remaining tonnage weights
        total_remain = sum(shovel_remaining_total.values())
        if total_remain <= 0:
            # No remaining inventory
            continue

        r = random.random() * total_remain
        chosen = None
        running = 0.0
        for s in range(1, 8):
            running += shovel_remaining_total[s]
            if r <= running:
                chosen = s
                break
        if chosen is None:
            chosen = 7

        s = chosen
        q = queues[s]
        ptr = shovel_ptr[s]
        if ptr >= len(q):
            # No more blocks in this shovel; skip deterministically
            continue

        blk = q[ptr]
        blk_id = blk.block_id
        remaining_before = remaining_by_block[blk_id]
        trip_payload = float(payload[i])

        # Last-trip cap: a truck cannot load more than the rock left in the face.
        if remaining_before <= trip_payload:
            actual_payload = round(remaining_before, 2)
            remaining_after = 0.00
            status = "FULLY_DEPLETED"
            shovel_ptr[s] += 1
            if shovel_ptr[s] < len(q):
                shovel_active_remaining[s] = remaining_by_block[q[shovel_ptr[s]].block_id]
        else:
            actual_payload = round(trip_payload, 2)
            remaining_after = round(remaining_before - trip_payload, 2)
            status = "ACTIVE"

        remaining_by_block[blk_id] = remaining_after
        shovel_remaining_total[s] = max(0.0, shovel_remaining_total[s] - remaining_before + remaining_after)

        # Write outputs for this trip event
        shovel_col[i] = f"S{s}"
        block_id_col[i] = blk_id
        status_col[i] = status
        bulk_density_col[i] = round(blk.bulk_density, 4)
        block_tonnage_col[i] = round(blk.block_tonnage, 2)
        remaining_tonnage_col[i] = remaining_after
        actual_payload_col[i] = actual_payload

    out = timeline_df.copy()
    out["Shovel_ID"] = shovel_col
    out["Block_ID"] = block_id_col
    out["Block_Status"] = status_col
    out["Bulk_Density_t_m3"] = bulk_density_col
    out["Block_Tonnage_t"] = block_tonnage_col
    out["Remaining_Tonnage_t"] = remaining_tonnage_col
    out["Payload_t"] = actual_payload_col

    return out


def validate_all(
    pool_df: pd.DataFrame,
    subpools_df: pd.DataFrame,
    queues_df: pd.DataFrame,
    truck_out_df: pd.DataFrame,
):
    """
    Lightweight validation checks.
    """
    report_lines: List[str] = []

    # Check global N_pool
    report_lines.append("Validation Report (Option 1)")
    report_lines.append("--------------------------------")

    # 1) Pool counts by combo
    pool_counts = pool_df.groupby("Combo_Key")["Block_ID"].nunique()
    expected_total = sum(N_C_BY_COMBO.values())
    report_lines.append(f"Expected total blocks (N_pool): {expected_total}")
    report_lines.append(f"Actual total blocks in pool: {pool_df['Block_ID'].nunique()}")

    mismatch = []
    for combo, n in N_C_BY_COMBO.items():
        got = int(pool_counts.get(combo, 0))
        if got != n:
            mismatch.append((combo, n, got))
    report_lines.append(f"Pool combo mismatches: {len(mismatch)}")
    if mismatch:
        report_lines.append(str(mismatch[:5]) + (" ..." if len(mismatch) > 5 else ""))

    # 2) Queue length should equal total blocks assigned to shovels
    report_lines.append(f"Queue rows (blocks in queues): {len(queues_df)}")

    # 3) Subpool sums should match pool size
    report_lines.append(f"Subpool rows (blocks in subpools): {len(subpools_df)}")

    # 4) Depletion sanity: Block_Status must exist where Block_ID exists
    non_null = truck_out_df["Block_ID"].notna()
    null_status = (non_null) & (truck_out_df["Block_Status"].isna())
    report_lines.append(f"Trips with Block_ID but missing Block_Status: {int(null_status.sum())}")

    # 5) Status correctness using Remaining_Tonnage_t
    active_wrong = (truck_out_df["Block_Status"] == "ACTIVE") & (truck_out_df["Remaining_Tonnage_t"] <= 0)
    depleted_wrong = (truck_out_df["Block_Status"] == "FULLY_DEPLETED") & (truck_out_df["Remaining_Tonnage_t"] > 0)
    report_lines.append(f"ACTIVE status with Remaining<=0: {int(active_wrong.sum())}")
    report_lines.append(f"FULLY_DEPLETED status with Remaining>0: {int(depleted_wrong.sum())}")
    negative_remaining = (truck_out_df["Remaining_Tonnage_t"] < 0).sum()
    report_lines.append(f"Negative Remaining_Tonnage_t rows: {int(negative_remaining)}")

    with open(OUT_VALIDATION_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\n".join(report_lines[:8]))


def main():
    # --- sanity checks
    if sum(N_C_BY_COMBO.values()) != N_POOL:
        raise RuntimeError("N_C_BY_COMBO does not sum to N_POOL. Fix allocation table.")

    # --- Step 1
    print("Step 1: Generating fixed block pool...")
    pool_by_combo, pool_df = generate_block_pool()
    pool_df.to_csv(OUT_POOL_FILE, index=False)

    # --- Step 2A
    print("Step 2A: Partitioning into shovel sub-pools...")
    subpools = generate_shovel_subpools(pool_by_combo)
    subpools_df = pd.read_csv(OUT_SUBPOOL_FILE)

    # --- Step 2B
    print("Step 2B: Generating ordered shovel queues...")
    queues = generate_shovel_queues(subpools)
    queues_df = pd.read_csv(OUT_QUEUE_FILE)

    # --- Step 3
    print("Step 3: Assigning trips to shovels and depleting blocks...")
    timeline_df = pd.read_csv(TIMELINE_FILE)
    truck_out = assign_trips_and_deplete(queues, timeline_df)
    truck_out.to_csv(OUT_TRUCK_BLOCK_FILE, index=False)

    # --- Step 4
    print("Step 4: Validation...")
    validate_all(pool_df, subpools_df, queues_df, truck_out)

    print(f"\nOutputs saved:")
    print(f"  Pool     : {OUT_POOL_FILE}")
    print(f"  Subpools : {OUT_SUBPOOL_FILE}")
    print(f"  Queues   : {OUT_QUEUE_FILE}")
    print(f"  Trip->Block depletion: {OUT_TRUCK_BLOCK_FILE}")
    print(f"  Report   : {OUT_VALIDATION_REPORT}")


if __name__ == "__main__":
    main()

