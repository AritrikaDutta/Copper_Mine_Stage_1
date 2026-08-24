# Copper Mine Final Dataset — Design & Geometallurgical Reference

---

## 1. Overview

| Item | Value |
|---|---|
| Simulation horizon | 365 days (2025-01-01 DAY shift start) |
| Trip records | **875,846** |
| Fleet | 80 trucks, 160 operators, 7 shovels |
| Geological domains | 30 (5 lithologies × 6 alterations) |
| Block pool | 37,080 blocks |
| Intermediate master | `copper_mine_master_dataset_365days.csv` (20 columns) |
| Merged ops + chemistry | `copper_mine_final_combined_365days.csv` (36 columns) |
| **Final deliverable** | **`copper_mine_final_with_geomet_365days.csv` (47 columns)** |

End-state pipeline: truck timeline + block depletion → 20-column master → mineralogy merge (16 chemistry columns) → derived geometallurgical properties → final 47-column ordered CSV.

---

## 2. Ops Simulation

### 2.1 General Parameters

| Parameter | Value |
|---|---|
| Simulation start | 2025-01-01 06:00 (DAY shift start) |
| Simulation duration | 365 days |
| Fleet size | 80 trucks |
| Operators | 160 (OP-001 to OP-160) |
| Random seed | 42 |

### 2.2 Shift Structure

| Parameter | Value |
|---|---|
| Shifts per day | 2 |
| DAY shift | 06:00–18:00 |
| NIGHT shift | 18:00–06:00 (next calendar day) |
| Roster_Date rule | Night-shift trips after midnight keep Roster_Date = shift-start day |
| Calendar_Date rule | Actual calendar date derived from Arrival_Time |

### 2.3 Operational Timing Ranges

| Parameter | Min | Max | Unit | Notes |
|---|---|---|---|---|
| Payload per trip | 340.0 | 363.0 | tonnes | Cat 797F rated capacity |
| Dwell / ground time | 4 | 8 | minutes | Spotting + 4 shovel passes + departure |
| Inter-trip gap (haul cycle) | 25 | 40 | minutes | Simulates shallow vs deep pit |
| Fleet stagger at shift start | 0 | 30 | minutes | Prevents simultaneous shovel clogging |
| Shift change delay | 30 | 45 | minutes | Hot-seat swap, safety tailgate, pre-op |
| Meal break duration | 30 | 45 | minutes | Operator meal rotation |
| Meal break stagger | 0 | 30 | minutes | Around ~12:00 (DAY) or ~00:00 (NIGHT) |

All timing values include **random seconds** (not rounded to whole minutes).

### 2.4 Trip Targets

| Parameter | Min | Max |
|---|---|---|
| Trips per truck per roster day | 28 | 32 |
| Trips per truck per shift | 12 | 16 |

Trip numbering runs **continuously DAY → NIGHT** within a roster day and **resets at the next DAY shift**.

### 2.5 Trip_ID Format

```
T{Truck_ID}_{Shift_ID}_TRIP_{Trip_Number:03d}
```

Example: `T15_DAY_TRIP_007`

### 2.6 Operator Assignment (Fixed per truck per shift)

| Shift | Formula | Example |
|---|---|---|
| DAY | `OP-{Truck_Number:03d}` | Truck 15 → OP-015 |
| NIGHT | `OP-{Truck_Number + 80:03d}` | Truck 15 → OP-095 |

### 2.7 Operational Zones & Shovel Assignment

| Zone | Combinations |
|---|---|
| **CORE** (6) | QMP: Potassic, Phyllic, Propylitic; Granodiorite: Potassic, Phyllic, Propylitic |
| **MARGIN** (6) | Andesite: Potassic, Phyllic, Propylitic; Diorite: Potassic, Phyllic, Propylitic |
| **OUTER** (8) | Granite: Potassic, Phyllic, Propylitic, Argillic; Andesite/Diorite/Granodiorite/QMP Argillic |
| **CAP** (10) | All Advanced Argillic + all Sodic-Calcic |

7 active shovels (S1–S7). Affinity: Primary 80% / Secondary 15% / Tertiary 5%. Trip dispatch weights by remaining sub-pool tonnage.

### 2.8 Intra-Shovel Queue Ordering (Markov Continuity)

| Probability | Action |
|---|---|
| 80% | Same lithology–alteration combination |
| 15% | Secondary operational zone |
| 5% | Tertiary operational zone |

Alteration adjacency chain: `Potassic ↔ Phyllic ↔ Propylitic ↔ Argillic ↔ Advanced Argillic`.

---

## 3. Block Model & Depletion

### 3.1 Block Geometry

| Parameter | Value |
|---|---|
| Block dimensions | 15 m × 15 m × 15 m |
| Block volume | 3,375 m³ |
| Block_Tonnage formula | `3375 × Bulk_Density_t_m3` |

### 3.2 Total Block Pool Size

| Parameter | Value |
|---|---|
| Expected blocks consumed in 1 year | ~33,700 |
| Buffer | 10% |
| N_pool (total blocks generated) | 37,080 |

### 3.3 Depletion Rule

- Each trip decrements the block's `Remaining_Tonnage_t` by the trip's `Payload_t`.
- Last trip on a block is capped to remaining tonnage (no negative remaining).
- When `Remaining_Tonnage_t ≤ 0`, status → `FULLY_DEPLETED`.
- The shovel advances to the next block in its queue.
- Typical trips to deplete one block: **~21–30** (emergent, not hardcoded).

### 3.4 Combination Distribution (30 Lithology × Alteration)

Allocation uses the **Hare–Niemeyer (Largest Remainder) method** — deterministic, exact sum to N_pool.

| Lithology | Alteration | Volume % | Locked Block Count (N_c) |
|---|---|---|---|
| Andesite | Phyllic | 18.00% | 6,673 |
| QMP | Potassic | 15.00% | 5,561 |
| Andesite | Propylitic | 12.00% | 4,449 |
| QMP | Phyllic | 10.00% | 3,707 |
| Andesite | Potassic | 8.00% | 2,966 |
| Granodiorite | Phyllic | 6.00% | 2,225 |
| Granodiorite | Propylitic | 5.00% | 1,854 |
| Andesite | Argillic | 4.50% | 1,668 |
| QMP | Argillic | 3.50% | 1,298 |
| Diorite | Propylitic | 3.00% | 1,112 |
| Diorite | Phyllic | 2.50% | 927 |
| Granodiorite | Potassic | 2.00% | 742 |
| QMP | Propylitic | 1.50% | 556 |
| Granite | Propylitic | 1.50% | 556 |
| Andesite | Advanced Argillic | 1.20% | 445 |
| Granite | Phyllic | 1.00% | 371 |
| Diorite | Potassic | 1.00% | 371 |
| QMP | Advanced Argillic | 0.80% | 297 |
| Granodiorite | Argillic | 0.80% | 297 |
| Diorite | Argillic | 0.50% | 186 |
| Granite | Argillic | 0.40% | 149 |
| Granite | Potassic | 0.40% | 149 |
| Andesite | Sodic-Calcic | 0.40% | 149 |
| Diorite | Sodic-Calcic | 0.30% | 112 |
| QMP | Sodic-Calcic | 0.20% | 74 |
| Granodiorite | Advanced Argillic | 0.20% | 74 |
| Granodiorite | Sodic-Calcic | 0.10% | 37 |
| Diorite | Advanced Argillic | 0.10% | 37 |
| Granite | Advanced Argillic | 0.05% | 19 |
| Granite | Sodic-Calcic | 0.05% | 19 |
| **TOTAL** | | **100.00%** | **37,080** |

Geological calibration: giant Andean porphyry (Atacama Belt) — Andesite ~52%, QMP ~33%, Granodiorite ~15%; Phyllic + Potassic ≈ 70% of mineralized volume.

### 3.5 Bulk Density Ranges (t/m³)

Each block samples once from `U[min, max]` for its combination; density is fixed for the block lifetime.

| Lithology | Alteration | Min | Max |
|---|---|---|---|
| Andesite | Potassic | 2.75 | 2.90 |
| Andesite | Phyllic | 2.65 | 2.82 |
| Andesite | Propylitic | 2.70 | 2.85 |
| Andesite | Argillic | 2.48 | 2.65 |
| Andesite | Advanced Argillic | 2.32 | 2.55 |
| Andesite | Sodic-Calcic | 2.80 | 2.98 |
| Diorite | Potassic | 2.80 | 2.95 |
| Diorite | Phyllic | 2.72 | 2.88 |
| Diorite | Propylitic | 2.78 | 2.92 |
| Diorite | Argillic | 2.55 | 2.70 |
| Diorite | Advanced Argillic | 2.40 | 2.60 |
| Diorite | Sodic-Calcic | 2.88 | 3.02 |
| Granodiorite | Potassic | 2.68 | 2.82 |
| Granodiorite | Phyllic | 2.62 | 2.76 |
| Granodiorite | Propylitic | 2.66 | 2.80 |
| Granodiorite | Argillic | 2.45 | 2.60 |
| Granodiorite | Advanced Argillic | 2.30 | 2.50 |
| Granodiorite | Sodic-Calcic | 2.74 | 2.88 |
| QMP | Potassic | 2.62 | 2.75 |
| QMP | Phyllic | 2.55 | 2.70 |
| QMP | Propylitic | 2.60 | 2.72 |
| QMP | Argillic | 2.38 | 2.52 |
| QMP | Advanced Argillic | 2.25 | 2.45 |
| QMP | Sodic-Calcic | 2.68 | 2.82 |
| Granite | Potassic | 2.60 | 2.73 |
| Granite | Phyllic | 2.52 | 2.67 |
| Granite | Propylitic | 2.58 | 2.70 |
| Granite | Argillic | 2.35 | 2.50 |
| Granite | Advanced Argillic | 2.20 | 2.42 |
| Granite | Sodic-Calcic | 2.65 | 2.78 |

### 3.6 Lithology Codes

| Lithology Name | Code |
|---|---|
| Andesite | AND |
| QMP | QMP |
| Granodiorite | GRD |
| Diorite | DIO |
| Granite | GRN |

---

## 4. Master 20-Column Schema

Output file: `copper_mine_master_dataset_365days.csv`

| # | Column | Data Type | How Determined |
|---|---|---|---|
| 1 | Roster_Date | Date (YYYY-MM-DD) | From truck timeline; night-shift after-midnight trips keep shift-start day |
| 2 | Calendar_Date | Date (YYYY-MM-DD) | Actual calendar date from Arrival_Time |
| 3 | Shift_ID | DAY / NIGHT | From truck timeline |
| 4 | Shovel_ID | S1–S7 | Weighted dispatch by remaining sub-pool tonnage |
| 5 | Truck_ID | T1–T80 | From truck timeline |
| 6 | Operator_ID | OP-001–OP-160 | DAY: OP-{truck:03d}; NIGHT: OP-{truck+80:03d} |
| 7 | Trip_ID | String | T{truck}_{shift}_TRIP_{num:03d} |
| 8 | Block_ID | BLK-00001–BLK-37080 | Active block in shovel queue at time of trip |
| 9 | Lithology_Code | AND/QMP/GRD/DIO/GRN | Mapped from Lithology_Name |
| 10 | Lithology_Name | String | Fixed per block from pool generation |
| 11 | Alteration_Name | String | Fixed per block from pool generation |
| 12 | Operational_Zone | CORE/MARGIN/OUTER/CAP | Derived from (Lithology, Alteration) |
| 13 | Bulk_Density_t_m3 | Float | U[min, max] per block; fixed for block lifetime |
| 14 | Block_Tonnage_t | Float | 3375 × Bulk_Density; fixed per block |
| 15 | Remaining_Tonnage_t | Float | Block_Tonnage minus cumulative payload extracted |
| 16 | Block_Status | ACTIVE / FULLY_DEPLETED | ACTIVE while Remaining > 0; FULLY_DEPLETED when ≤ 0 |
| 17 | Payload_t | Float | U[340, 363] per trip (last trip capped to remaining) |
| 18 | Arrival_Time | Datetime | Generated with all timing rules + random seconds |
| 19 | Departure_Time | Datetime | Arrival_Time + dwell (4–8 min + random seconds) |
| 20 | Dwell_Minutes | Float | (Departure − Arrival) in minutes |

---

## 5. Mineralogy Layer

### 5.1 Source Files

Chemistry rows are generated per lithology and saved as:

| File | Lithology | Rows (match master trips) |
|---|---|---|
| `Andesite_data.csv` | Andesite | 415,606 |
| `QMP_data.csv` | QMP | 269,602 |
| `Granodiorite_data.csv` | Granodiorite | 111,466 |
| `Diorite_data.csv` | Diorite | 53,522 |
| `Granite_data.csv` | Granite | 25,650 |
| **Total** | | **875,846** |

Each file starts with `Lithology`, `Alteration`, then chemistry columns. Alteration counts match master trip counts by domain.

### 5.2 Chemistry Columns (16)

Merged onto every trip for all lithology × alteration combinations:

- Chalcopyrite
- Bornite
- Pyrite
- Chalcocite
- Covellite
- Copper_Total
- Sulfur
- Iron
- Aluminium
- Magnesium
- Clay
- Carbonate
- Arsenic
- Lead
- Zinc
- Mercury

### 5.3 Merge Rule

1. Match mineralogy `(Lithology, Alteration)` to master `(Lithology_Name, Alteration_Name)`.
2. Shuffle mineralogy rows **within** each combination only (seed 42).
3. Attach **one chemistry row per trip** (1:1 counts required).
4. Output: `copper_mine_final_combined_365days.csv` — **36 columns** (20 master + 16 chemistry).

---

## 6. Derived Geometallurgical Properties

Implemented in `calculate_geomet_properties.py` on the 36-column merged file. Input: `copper_mine_final_combined_365days.csv`. Output: `copper_mine_final_with_geomet_365days.csv`.

### 6.1 Alteration_Intensity_pct

Conditional routing on `Alteration_Name`. Results capped at 100% and clipped ≥ 0 (2 decimals).

```
If Alteration_Name == "Phyllic"           --> Phyllic Formula
If Alteration_Name == "Potassic"          --> Potassic Formula
If Alteration_Name == "Argillic"          --> Argillic Formula
If Alteration_Name == "Advanced Argillic" --> Argillic Formula
If Alteration_Name == "Propylitic"        --> Propylitic Formula
If Alteration_Name == "Sodic-Calcic"      --> Sodic-Calcic Formula
```

| Alteration_Name | Formula |
|---|---|
| **Phyllic** | `min(100, (Pyrite + Clay) / (Aluminium × 2.5) × 100)` |
| **Potassic** | `min(100, (Chalcopyrite + Bornite) / (Copper_Total + 0.001) × 100)` |
| **Argillic** | `min(100, Clay / (Clay + Magnesium + 0.001) × 100)` |
| **Advanced Argillic** | Same as Argillic |
| **Propylitic** | `min(100, (Carbonate + Magnesium) / (Iron + Aluminium + 0.001) × 100)` |
| **Sodic-Calcic** | `min(100, (Iron − Pyrite × 0.466) / (Sulfur + 0.001) × 10)` |

### 6.2 Weathering_State

```text
Secondary_Cu_Ratio = (Chalcocite + Covellite) / (Copper_Total + 0.0001)
Primary_Cu_Ratio   = (Chalcopyrite + Bornite) / (Copper_Total + 0.0001)
```

| Weathering_State | Rule | Processing Route |
|---|---|---|
| **Oxide** | `Sulfur < 0.5` AND `Clay > 10` | Acid Heap Leach |
| **Transition** | `Secondary_Cu_Ratio >= 0.35` AND `Sulfur >= 0.5` | Mixed Leach / Flotation |
| **Fresh (Hypogene)** | `Primary_Cu_Ratio >= 0.50` AND `Sulfur >= 1.5` | Concentrator Flotation |

Unmatched rows → `Unclassified`.

### 6.3 Mo_pct

```text
Mo_pct = (Copper_Total / R_Cu:Mo) × (Alteration_Intensity_pct / 100) × K_lith
```

| Alteration | R_Cu:Mo | Lithology | K_lith |
|---|---|---|---|
| Potassic | 20 | QMP | 1.25 |
| Phyllic | 45 | Granodiorite | 1.10 |
| Argillic | 120 | Andesite | 0.90 |
| Advanced Argillic | 180 | Diorite | 0.80 |
| Propylitic | 250 | Granite | 0.70 |
| Sodic-Calcic | 500 | | |

Stoichiometric sulfur cap:

```text
S_consumed = 0.3494×Chalcopyrite + 0.2554×Bornite + 0.5345×Pyrite
           + 0.2014×Chalcocite + 0.3353×Covellite
S_excess = max(0, Sulfur − S_consumed)
Mo_max = S_excess × 1.496
Mo_pct_final = min(Mo_pct_calculated, Mo_max)
```

### 6.4 Quartz_pct

| Lithology | Q_base (wt%) | Alteration | M_alt |
|---|---|---|---|
| Granite | 30.0 | Advanced Argillic | 1.60 |
| QMP | 25.0 | Phyllic | 1.40 |
| Granodiorite | 18.0 | Potassic | 1.20 |
| Diorite | 5.0 | Argillic | 1.00 |
| Andesite | 3.0 | Propylitic | 0.85 |
| | | Sodic-Calcic | 0.85 |

```text
M_non_quartz = Chalcopyrite + Bornite + Pyrite + Chalcocite
             + Covellite + Clay + Carbonate
Space_Factor = max(0.05, 1 − M_non_quartz / 100)
Quartz_pct = min(85.0, (Q_base × M_alt + 0.15 × Aluminium) × Space_Factor)
```

### 6.5 Bond_Work_Index (BWi, kWh/t)

```text
BWi = Clamp(
  BWi_base(Lithology, Alteration)
  + 0.12×(Quartz_pct − mean Quartz_pct in domain)
  − 0.08×(Clay − mean Clay in domain)
  + 0.05×Pyrite,
  6.0, 24.0
)
```

Domain means are per `(Lithology_Name, Alteration_Name)`.

| Lithology | Potassic | Phyllic | Argillic | Adv. Argillic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Granite | 16.5 | 18.5 | 12.5 | 17.0 | 15.5 | 17.5 |
| QMP | 15.0 | 17.0 | 11.0 | 15.5 | 14.0 | 16.0 |
| Granodiorite | 14.0 | 16.0 | 10.5 | 14.5 | 13.0 | 15.0 |
| Diorite | 13.5 | 15.0 | 10.0 | 13.5 | 14.5 | 16.5 |
| Andesite | 12.0 | 14.0 | 9.0 | 12.5 | 13.0 | 14.5 |

### 6.6 Axb (SAG Mill Impact Hardness)

Lower Axb = harder rock. Clamp `[15, 180]`.

```text
Axb = Clamp(
  Axb_base
  − 0.40×(Quartz_pct − domain mean)
  + 0.85×(Clay − domain mean)
  + Axb_base × (Alteration_Intensity_pct/100) × I_factor,
  15.0, 180.0
)
```

| Lithology | Potassic | Phyllic | Argillic | Adv. Argillic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Granite | 32 | 28 | 65 | 30 | 38 | 26 |
| QMP | 38 | 32 | 75 | 35 | 45 | 30 |
| Granodiorite | 42 | 36 | 82 | 40 | 50 | 34 |
| Diorite | 45 | 40 | 90 | 45 | 48 | 32 |
| Andesite | 52 | 44 | 110 | 50 | 55 | 38 |

| Alteration | I_factor |
|---|---|
| Argillic | +0.35 |
| Propylitic | +0.10 |
| Potassic | −0.10 |
| Advanced Argillic | −0.10 |
| Phyllic | −0.15 |
| Sodic-Calcic | −0.20 |

### 6.7 DWi (Drop Weight Index, kWh/m³)

```text
DWi = (100 × Bulk_Density_t_m3) / Axb
```

Higher DWi = harder rock (`<2` soft; `2.5–7` medium porphyry; `>10` very hard).

### 6.8 Bond_Abrasion_Index (Ai, grams)

```text
Ai = Clamp(
  Ai_base
  + 0.006×(Quartz_pct − domain mean)
  + 0.003×Pyrite
  − 0.002×(Clay − domain mean),
  0.01, 0.80
)
```

| Lithology | Potassic | Phyllic | Argillic | Adv. Argillic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Granite | 0.38 | 0.52 | 0.18 | 0.48 | 0.32 | 0.42 |
| QMP | 0.35 | 0.48 | 0.15 | 0.44 | 0.28 | 0.38 |
| Granodiorite | 0.30 | 0.42 | 0.12 | 0.38 | 0.24 | 0.34 |
| Diorite | 0.24 | 0.36 | 0.10 | 0.32 | 0.20 | 0.28 |
| Andesite | 0.20 | 0.30 | 0.08 | 0.26 | 0.16 | 0.22 |

### 6.9 UCS_mpa

```text
UCS = Clamp(
  UCS_base × [1 + (Alteration_Intensity_pct/100)×U_factor]
  + 1.2×(Quartz_pct − domain mean)
  − 1.5×(Clay − domain mean),
  15.0, 320.0
)
```

| Lithology | Potassic | Phyllic | Argillic | Adv. Argillic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Granite | 180 | 150 | 55 | 130 | 160 | 220 |
| QMP | 160 | 135 | 45 | 120 | 145 | 200 |
| Granodiorite | 150 | 125 | 40 | 110 | 135 | 190 |
| Diorite | 140 | 115 | 35 | 100 | 125 | 175 |
| Andesite | 125 | 100 | 30 | 85 | 110 | 160 |

| Alteration | U_factor |
|---|---|
| Sodic-Calcic | +0.25 |
| Potassic | +0.10 |
| Propylitic | −0.10 |
| Phyllic | −0.20 |
| Advanced Argillic | −0.30 |
| Argillic | −0.60 |

### 6.10 RQD (%)

```text
RQD = Clamp(
  RQD_base
  − 0.35×Alteration_Intensity_pct
  − Weathering_Penalty
  − 0.40×(Clay − domain mean),
  5.0, 100.0
)
```

Weathering penalty: Oxide 45 / Transition 20 / Fresh (Hypogene) 0.

| Lithology | Potassic | Phyllic | Argillic | Adv. Argillic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Granite | 85 | 65 | 35 | 55 | 80 | 90 |
| QMP | 80 | 60 | 30 | 50 | 75 | 85 |
| Granodiorite | 82 | 62 | 32 | 52 | 78 | 88 |
| Diorite | 78 | 58 | 28 | 48 | 72 | 82 |
| Andesite | 75 | 55 | 25 | 45 | 70 | 80 |

### 6.11 Moisture_pct

```text
Moisture_pct = Clamp(
  Moisture_base(Weathering, Alteration)
  + 0.12×Clay
  + Lithology_delta,
  0.2, 12.0
)
```

Lithology delta: Andesite +0.30; Diorite/Granodiorite +0.10; Granite/QMP 0.00.  
`Fresh (Hypogene)` / `Unclassified` map to Fresh baseline.

| Weathering | Argillic | Adv. Argillic | Phyllic | Potassic | Propylitic | Sodic-Calcic |
|---|---|---|---|---|---|---|
| Oxide | 5.5 | 4.8 | 3.8 | 3.2 | 3.5 | 3.0 |
| Transition | 3.2 | 2.5 | 1.8 | 1.4 | 1.6 | 1.2 |
| Fresh | 1.8 | 1.2 | 0.6 | 0.4 | 0.5 | 0.3 |

---

## 7. Final 47-Column Order

Deliverable: `copper_mine_final_with_geomet_365days.csv`

Practical chronology (trip → cycle → block → geology → mass → chemistry → gangue → deleterious → geomet):

| # | Column | Group |
|---|---|---|
| 1 | Roster_Date | Trip / ops identity |
| 2 | Calendar_Date | Trip / ops identity |
| 3 | Shift_ID | Trip / ops identity |
| 4 | Trip_ID | Trip / ops identity |
| 5 | Shovel_ID | Trip / ops identity |
| 6 | Truck_ID | Trip / ops identity |
| 7 | Operator_ID | Trip / ops identity |
| 8 | Arrival_Time | Cycle times |
| 9 | Departure_Time | Cycle times |
| 10 | Dwell_Minutes | Cycle times |
| 11 | Block_ID | Block identity & status |
| 12 | Block_Status | Block identity & status |
| 13 | Operational_Zone | Block identity & status |
| 14 | Lithology_Code | Geology classification |
| 15 | Lithology_Name | Geology classification |
| 16 | Alteration_Name | Geology classification |
| 17 | Alteration_Intensity_pct | Geology classification |
| 18 | Weathering_State | Geology classification |
| 19 | Bulk_Density_t_m3 | Block mass / density |
| 20 | Block_Tonnage_t | Block mass / density |
| 21 | Remaining_Tonnage_t | Block mass / density |
| 22 | Payload_t | Block mass / density |
| 23 | Moisture_pct | Block mass / density |
| 24 | Copper_Total | Ore / sulfide chemistry |
| 25 | Mo_pct | Ore / sulfide chemistry |
| 26 | Chalcopyrite | Ore / sulfide chemistry |
| 27 | Bornite | Ore / sulfide chemistry |
| 28 | Chalcocite | Ore / sulfide chemistry |
| 29 | Covellite | Ore / sulfide chemistry |
| 30 | Pyrite | Ore / sulfide chemistry |
| 31 | Sulfur | Ore / sulfide chemistry |
| 32 | Iron | Ore / sulfide chemistry |
| 33 | Quartz_pct | Gangue / alteration minerals |
| 34 | Clay | Gangue / alteration minerals |
| 35 | Carbonate | Gangue / alteration minerals |
| 36 | Aluminium | Gangue / alteration minerals |
| 37 | Magnesium | Gangue / alteration minerals |
| 38 | Arsenic | Deleterious / penalty elements |
| 39 | Lead | Deleterious / penalty elements |
| 40 | Zinc | Deleterious / penalty elements |
| 41 | Mercury | Deleterious / penalty elements |
| 42 | Bond_Work_Index | Comminution / rock-mass geomet |
| 43 | Axb | Comminution / rock-mass geomet |
| 44 | DWi | Comminution / rock-mass geomet |
| 45 | Bond_Abrasion_Index | Comminution / rock-mass geomet |
| 46 | UCS_mpa | Comminution / rock-mass geomet |
| 47 | RQD | Comminution / rock-mass geomet |
