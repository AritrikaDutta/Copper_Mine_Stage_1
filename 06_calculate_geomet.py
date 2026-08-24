"""
Calculate derived geometallurgical properties from the 36-column
combined copper mine dataset.

This file is intentionally structured as a growing calculation library:
new derived columns can be added one by one as formulas are finalized.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


INPUT_FILE = "copper_mine_final_combined_365days.csv"
OUTPUT_FILE = "copper_mine_final_with_geomet_365days.csv"

# Practical column order for the final deliverable CSV.
FINAL_COLUMN_ORDER = [
    # 1. Trip / ops identity
    "Roster_Date",
    "Calendar_Date",
    "Shift_ID",
    "Trip_ID",
    "Shovel_ID",
    "Truck_ID",
    "Operator_ID",
    # 2. Cycle times
    "Arrival_Time",
    "Departure_Time",
    "Dwell_Minutes",
    # 3. Block identity & status
    "Block_ID",
    "Block_Status",
    "Operational_Zone",
    # 4. Geology classification
    "Lithology_Code",
    "Lithology_Name",
    "Alteration_Name",
    "Alteration_Intensity_pct",
    "Weathering_State",
    # 5. Block mass / density
    "Bulk_Density_t_m3",
    "Block_Tonnage_t",
    "Remaining_Tonnage_t",
    "Payload_t",
    "Moisture_pct",
    # 6. Ore / sulfide chemistry
    "Copper_Total",
    "Mo_pct",
    "Chalcopyrite",
    "Bornite",
    "Chalcocite",
    "Covellite",
    "Pyrite",
    "Sulfur",
    "Iron",
    # 7. Gangue / alteration minerals
    "Quartz_pct",
    "Clay",
    "Carbonate",
    "Aluminium",
    "Magnesium",
    # 8. Deleterious / penalty elements
    "Arsenic",
    "Lead",
    "Zinc",
    "Mercury",
    # 9. Comminution / rock-mass geomet
    "Bond_Work_Index",
    "Axb",
    "DWi",
    "Bond_Abrasion_Index",
    "UCS_mpa",
    "RQD",
]

# Base Cu:Mo ratio by alteration zone (R_Cu:Mo)
R_CU_MO_BY_ALTERATION = {
    "Potassic": 20,
    "Phyllic": 45,
    "Argillic": 120,
    "Advanced Argillic": 180,
    "Propylitic": 250,
    "Sodic-Calcic": 500,
}

# Lithology multiplier (K_lith)
K_LITH_BY_LITHOLOGY = {
    "QMP": 1.25,
    "Granodiorite": 1.10,
    "Andesite": 0.90,
    "Diorite": 0.80,
    "Granite": 0.70,
}

# MoS2 stoichiometry: Mo / S mass ratio for excess-sulfur cap
MO_S_RATIO = 59.94 / 40.06  # 1.496

# Bond Work Index baseline (kWh/t) by (Lithology_Name, Alteration_Name)
BWI_BASE_MATRIX = {
    ("Granite", "Potassic"): 16.5,
    ("Granite", "Phyllic"): 18.5,
    ("Granite", "Argillic"): 12.5,
    ("Granite", "Advanced Argillic"): 17.0,
    ("Granite", "Propylitic"): 15.5,
    ("Granite", "Sodic-Calcic"): 17.5,
    ("QMP", "Potassic"): 15.0,
    ("QMP", "Phyllic"): 17.0,
    ("QMP", "Argillic"): 11.0,
    ("QMP", "Advanced Argillic"): 15.5,
    ("QMP", "Propylitic"): 14.0,
    ("QMP", "Sodic-Calcic"): 16.0,
    ("Granodiorite", "Potassic"): 14.0,
    ("Granodiorite", "Phyllic"): 16.0,
    ("Granodiorite", "Argillic"): 10.5,
    ("Granodiorite", "Advanced Argillic"): 14.5,
    ("Granodiorite", "Propylitic"): 13.0,
    ("Granodiorite", "Sodic-Calcic"): 15.0,
    ("Diorite", "Potassic"): 13.5,
    ("Diorite", "Phyllic"): 15.0,
    ("Diorite", "Argillic"): 10.0,
    ("Diorite", "Advanced Argillic"): 13.5,
    ("Diorite", "Propylitic"): 14.5,
    ("Diorite", "Sodic-Calcic"): 16.5,
    ("Andesite", "Potassic"): 12.0,
    ("Andesite", "Phyllic"): 14.0,
    ("Andesite", "Argillic"): 9.0,
    ("Andesite", "Advanced Argillic"): 12.5,
    ("Andesite", "Propylitic"): 13.0,
    ("Andesite", "Sodic-Calcic"): 14.5,
}

BWI_MIN = 6.0
BWI_MAX = 24.0

# Axb (SAG mill impact hardness) baseline matrix (kWh/t impact-hardness units)
# keyed by (Lithology_Name, Alteration_Name)
AXB_BASE_MATRIX = {
    ("Granite", "Potassic"): 32.0,
    ("Granite", "Phyllic"): 28.0,
    ("Granite", "Argillic"): 65.0,
    ("Granite", "Advanced Argillic"): 30.0,
    ("Granite", "Propylitic"): 38.0,
    ("Granite", "Sodic-Calcic"): 26.0,
    ("QMP", "Potassic"): 38.0,
    ("QMP", "Phyllic"): 32.0,
    ("QMP", "Argillic"): 75.0,
    ("QMP", "Advanced Argillic"): 35.0,
    ("QMP", "Propylitic"): 45.0,
    ("QMP", "Sodic-Calcic"): 30.0,
    ("Granodiorite", "Potassic"): 42.0,
    ("Granodiorite", "Phyllic"): 36.0,
    ("Granodiorite", "Argillic"): 82.0,
    ("Granodiorite", "Advanced Argillic"): 40.0,
    ("Granodiorite", "Propylitic"): 50.0,
    ("Granodiorite", "Sodic-Calcic"): 34.0,
    ("Diorite", "Potassic"): 45.0,
    ("Diorite", "Phyllic"): 40.0,
    ("Diorite", "Argillic"): 90.0,
    ("Diorite", "Advanced Argillic"): 45.0,
    ("Diorite", "Propylitic"): 48.0,
    ("Diorite", "Sodic-Calcic"): 32.0,
    ("Andesite", "Potassic"): 52.0,
    ("Andesite", "Phyllic"): 44.0,
    ("Andesite", "Argillic"): 110.0,
    ("Andesite", "Advanced Argillic"): 50.0,
    ("Andesite", "Propylitic"): 55.0,
    ("Andesite", "Sodic-Calcic"): 38.0,
}

AXB_CLAMP_MIN = 15.0
AXB_CLAMP_MAX = 180.0

# Alteration intensity factor I_factor (sign indicates hardening vs softening)
AXB_I_FACTOR_BY_ALTERATION = {
    "Argillic": 0.35,
    "Propylitic": 0.10,
    "Potassic": -0.10,
    "Advanced Argillic": -0.10,
    "Phyllic": -0.15,
    "Sodic-Calcic": -0.20,
}

# Bond Abrasion Index baseline (Ai, grams) by (Lithology_Name, Alteration_Name)
AI_BASE_MATRIX = {
    ("Granite", "Potassic"): 0.38,
    ("Granite", "Phyllic"): 0.52,
    ("Granite", "Argillic"): 0.18,
    ("Granite", "Advanced Argillic"): 0.48,
    ("Granite", "Propylitic"): 0.32,
    ("Granite", "Sodic-Calcic"): 0.42,
    ("QMP", "Potassic"): 0.35,
    ("QMP", "Phyllic"): 0.48,
    ("QMP", "Argillic"): 0.15,
    ("QMP", "Advanced Argillic"): 0.44,
    ("QMP", "Propylitic"): 0.28,
    ("QMP", "Sodic-Calcic"): 0.38,
    ("Granodiorite", "Potassic"): 0.30,
    ("Granodiorite", "Phyllic"): 0.42,
    ("Granodiorite", "Argillic"): 0.12,
    ("Granodiorite", "Advanced Argillic"): 0.38,
    ("Granodiorite", "Propylitic"): 0.24,
    ("Granodiorite", "Sodic-Calcic"): 0.34,
    ("Diorite", "Potassic"): 0.24,
    ("Diorite", "Phyllic"): 0.36,
    ("Diorite", "Argillic"): 0.10,
    ("Diorite", "Advanced Argillic"): 0.32,
    ("Diorite", "Propylitic"): 0.20,
    ("Diorite", "Sodic-Calcic"): 0.28,
    ("Andesite", "Potassic"): 0.20,
    ("Andesite", "Phyllic"): 0.30,
    ("Andesite", "Argillic"): 0.08,
    ("Andesite", "Advanced Argillic"): 0.26,
    ("Andesite", "Propylitic"): 0.16,
    ("Andesite", "Sodic-Calcic"): 0.22,
}

AI_CLAMP_MIN = 0.01
AI_CLAMP_MAX = 0.80

# Unconfined Compressive Strength baseline (UCS, MPa) by (Lithology_Name, Alteration_Name)
UCS_BASE_MATRIX = {
    ("Granite", "Potassic"): 180.0,
    ("Granite", "Phyllic"): 150.0,
    ("Granite", "Argillic"): 55.0,
    ("Granite", "Advanced Argillic"): 130.0,
    ("Granite", "Propylitic"): 160.0,
    ("Granite", "Sodic-Calcic"): 220.0,
    ("QMP", "Potassic"): 160.0,
    ("QMP", "Phyllic"): 135.0,
    ("QMP", "Argillic"): 45.0,
    ("QMP", "Advanced Argillic"): 120.0,
    ("QMP", "Propylitic"): 145.0,
    ("QMP", "Sodic-Calcic"): 200.0,
    ("Granodiorite", "Potassic"): 150.0,
    ("Granodiorite", "Phyllic"): 125.0,
    ("Granodiorite", "Argillic"): 40.0,
    ("Granodiorite", "Advanced Argillic"): 110.0,
    ("Granodiorite", "Propylitic"): 135.0,
    ("Granodiorite", "Sodic-Calcic"): 190.0,
    ("Diorite", "Potassic"): 140.0,
    ("Diorite", "Phyllic"): 115.0,
    ("Diorite", "Argillic"): 35.0,
    ("Diorite", "Advanced Argillic"): 100.0,
    ("Diorite", "Propylitic"): 125.0,
    ("Diorite", "Sodic-Calcic"): 175.0,
    ("Andesite", "Potassic"): 125.0,
    ("Andesite", "Phyllic"): 100.0,
    ("Andesite", "Argillic"): 30.0,
    ("Andesite", "Advanced Argillic"): 85.0,
    ("Andesite", "Propylitic"): 110.0,
    ("Andesite", "Sodic-Calcic"): 160.0,
}

UCS_CLAMP_MIN = 15.0
UCS_CLAMP_MAX = 320.0

# Intensity structural factor U_factor (strengthen vs degrade)
UCS_U_FACTOR_BY_ALTERATION = {
    "Sodic-Calcic": 0.25,
    "Potassic": 0.10,
    "Propylitic": -0.10,
    "Phyllic": -0.20,
    "Advanced Argillic": -0.30,
    "Argillic": -0.60,
}

# Rock Quality Designation baseline (RQD, %) by (Lithology_Name, Alteration_Name)
RQD_BASE_MATRIX = {
    ("Granite", "Potassic"): 85.0,
    ("Granite", "Phyllic"): 65.0,
    ("Granite", "Argillic"): 35.0,
    ("Granite", "Advanced Argillic"): 55.0,
    ("Granite", "Propylitic"): 80.0,
    ("Granite", "Sodic-Calcic"): 90.0,
    ("QMP", "Potassic"): 80.0,
    ("QMP", "Phyllic"): 60.0,
    ("QMP", "Argillic"): 30.0,
    ("QMP", "Advanced Argillic"): 50.0,
    ("QMP", "Propylitic"): 75.0,
    ("QMP", "Sodic-Calcic"): 85.0,
    ("Granodiorite", "Potassic"): 82.0,
    ("Granodiorite", "Phyllic"): 62.0,
    ("Granodiorite", "Argillic"): 32.0,
    ("Granodiorite", "Advanced Argillic"): 52.0,
    ("Granodiorite", "Propylitic"): 78.0,
    ("Granodiorite", "Sodic-Calcic"): 88.0,
    ("Diorite", "Potassic"): 78.0,
    ("Diorite", "Phyllic"): 58.0,
    ("Diorite", "Argillic"): 28.0,
    ("Diorite", "Advanced Argillic"): 48.0,
    ("Diorite", "Propylitic"): 72.0,
    ("Diorite", "Sodic-Calcic"): 82.0,
    ("Andesite", "Potassic"): 75.0,
    ("Andesite", "Phyllic"): 55.0,
    ("Andesite", "Argillic"): 25.0,
    ("Andesite", "Advanced Argillic"): 45.0,
    ("Andesite", "Propylitic"): 70.0,
    ("Andesite", "Sodic-Calcic"): 80.0,
}

RQD_CLAMP_MIN = 5.0
RQD_CLAMP_MAX = 100.0

# Weathering_State penalty (% points subtracted from RQD)
# Maps "Fresh (Hypogene)" to the Fresh case in the specification.
RQD_WEATHERING_PENALTY = {
    "Oxide": 45.0,
    "Transition": 20.0,
    "Fresh (Hypogene)": 0.0,
    "Fresh": 0.0,
    "Unclassified": 0.0,
}

# Moisture_pct baseline (%) by (Weathering_State, Alteration_Name)
# Fresh (Hypogene) / Unclassified map onto the Fresh row.
MOISTURE_BASE_MATRIX = {
    ("Oxide", "Argillic"): 5.5,
    ("Oxide", "Advanced Argillic"): 4.8,
    ("Oxide", "Phyllic"): 3.8,
    ("Oxide", "Potassic"): 3.2,
    ("Oxide", "Propylitic"): 3.5,
    ("Oxide", "Sodic-Calcic"): 3.0,
    ("Transition", "Argillic"): 3.2,
    ("Transition", "Advanced Argillic"): 2.5,
    ("Transition", "Phyllic"): 1.8,
    ("Transition", "Potassic"): 1.4,
    ("Transition", "Propylitic"): 1.6,
    ("Transition", "Sodic-Calcic"): 1.2,
    ("Fresh", "Argillic"): 1.8,
    ("Fresh", "Advanced Argillic"): 1.2,
    ("Fresh", "Phyllic"): 0.6,
    ("Fresh", "Potassic"): 0.4,
    ("Fresh", "Propylitic"): 0.5,
    ("Fresh", "Sodic-Calcic"): 0.3,
}

MOISTURE_WEATHERING_KEY = {
    "Oxide": "Oxide",
    "Transition": "Transition",
    "Fresh (Hypogene)": "Fresh",
    "Fresh": "Fresh",
    "Unclassified": "Fresh",
}

MOISTURE_LITH_DELTA = {
    "Andesite": 0.30,
    "Diorite": 0.10,
    "Granodiorite": 0.10,
    "Granite": 0.00,
    "QMP": 0.00,
}

MOISTURE_CLAMP_MIN = 0.2
MOISTURE_CLAMP_MAX = 12.0

# Quartz_pct: primary base quartz (wt%) by Lithology_Name
QUARTZ_Q_BASE_BY_LITHOLOGY = {
    "Granite": 30.0,
    "QMP": 25.0,
    "Granodiorite": 18.0,
    "Diorite": 5.0,
    "Andesite": 3.0,
}

# Quartz_pct: hydrothermal multiplier by Alteration_Name
QUARTZ_M_ALT_BY_ALTERATION = {
    "Advanced Argillic": 1.60,
    "Phyllic": 1.40,
    "Potassic": 1.20,
    "Argillic": 1.00,
    "Propylitic": 0.85,
    "Sodic-Calcic": 0.85,
}

QUARTZ_PCT_MAX = 85.0
QUARTZ_SPACE_FACTOR_MIN = 0.05


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clip_pct(series: pd.Series) -> pd.Series:
    return np.minimum(100.0, series).round(2)


def calculate_alteration_intensity_pct(df: pd.DataFrame) -> pd.Series:
    """
    Conditional alteration-intensity routing by Alteration_Name.

    Formulas:
      - Phyllic:
          min(100, ((Pyrite + Clay) / (Aluminium * 2.5)) * 100)
      - Potassic:
          min(100, ((Chalcopyrite + Bornite) / (Copper_Total + 0.001)) * 100)
      - Argillic / Advanced Argillic:
          min(100, (Clay / (Clay + Magnesium + 0.001)) * 100)
      - Propylitic:
          min(100, ((Carbonate + Magnesium) / (Iron + Aluminium + 0.001)) * 100)
      - Sodic-Calcic:
          min(100, ((Iron - (Pyrite * 0.466)) / (Sulfur + 0.001)) * 10)
    """

    require_columns(
        df,
        [
            "Alteration_Name",
            "Pyrite",
            "Clay",
            "Aluminium",
            "Chalcopyrite",
            "Bornite",
            "Copper_Total",
            "Magnesium",
            "Carbonate",
            "Iron",
            "Sulfur",
        ],
    )

    alt = df["Alteration_Name"].astype(str)

    out = pd.Series(np.nan, index=df.index, dtype=float)

    phyllic_mask = alt == "Phyllic"
    potassic_mask = alt == "Potassic"
    argillic_mask = alt.isin(["Argillic", "Advanced Argillic"])
    propylitic_mask = alt == "Propylitic"
    sodic_calcic_mask = alt == "Sodic-Calcic"

    out.loc[phyllic_mask] = (
        (df.loc[phyllic_mask, "Pyrite"] + df.loc[phyllic_mask, "Clay"])
        / (df.loc[phyllic_mask, "Aluminium"] * 2.5)
        * 100.0
    )

    out.loc[potassic_mask] = (
        (df.loc[potassic_mask, "Chalcopyrite"] + df.loc[potassic_mask, "Bornite"])
        / (df.loc[potassic_mask, "Copper_Total"] + 0.001)
        * 100.0
    )

    out.loc[argillic_mask] = (
        df.loc[argillic_mask, "Clay"]
        / (
            df.loc[argillic_mask, "Clay"]
            + df.loc[argillic_mask, "Magnesium"]
            + 0.001
        )
        * 100.0
    )

    out.loc[propylitic_mask] = (
        (df.loc[propylitic_mask, "Carbonate"] + df.loc[propylitic_mask, "Magnesium"])
        / (
            df.loc[propylitic_mask, "Iron"]
            + df.loc[propylitic_mask, "Aluminium"]
            + 0.001
        )
        * 100.0
    )

    out.loc[sodic_calcic_mask] = (
        (
            df.loc[sodic_calcic_mask, "Iron"]
            - (df.loc[sodic_calcic_mask, "Pyrite"] * 0.466)
        )
        / (df.loc[sodic_calcic_mask, "Sulfur"] + 0.001)
        * 10.0
    )

    # Prevent negative percentages and cap at 100.
    out = out.clip(lower=0.0)
    return clip_pct(out)


def calculate_weathering_state(df: pd.DataFrame) -> pd.Series:
    """
    Deterministic weathering-state routing.

    Helper ratios:
      - Secondary_Cu_Ratio = (Chalcocite + Covellite) / (Copper_Total + 0.0001)
      - Primary_Cu_Ratio   = (Chalcopyrite + Bornite) / (Copper_Total + 0.0001)

    Routing rules:
      - Oxide:
          Sulfur < 0.5 AND Clay > 10
      - Transition:
          Secondary_Cu_Ratio >= 0.35 AND Sulfur >= 0.5
      - Fresh (Hypogene):
          Primary_Cu_Ratio >= 0.50 AND Sulfur >= 1.5

    Rows that do not satisfy any rule are labeled "Unclassified".
    """

    require_columns(
        df,
        [
            "Chalcocite",
            "Covellite",
            "Copper_Total",
            "Chalcopyrite",
            "Bornite",
            "Sulfur",
            "Clay",
        ],
    )

    secondary_cu_ratio = (
        (df["Chalcocite"] + df["Covellite"])
        / (df["Copper_Total"] + 0.0001)
    )
    primary_cu_ratio = (
        (df["Chalcopyrite"] + df["Bornite"])
        / (df["Copper_Total"] + 0.0001)
    )

    out = pd.Series("Unclassified", index=df.index, dtype="object")

    oxide_mask = (df["Sulfur"] < 0.5) & (df["Clay"] > 10)
    transition_mask = (secondary_cu_ratio >= 0.35) & (df["Sulfur"] >= 0.5)
    fresh_mask = (primary_cu_ratio >= 0.50) & (df["Sulfur"] >= 1.5)

    # Priority order follows the business rules as given.
    out.loc[oxide_mask] = "Oxide"
    out.loc[transition_mask] = "Transition"
    out.loc[fresh_mask] = "Fresh (Hypogene)"

    return out


def calculate_mo_pct(
    df: pd.DataFrame,
    alteration_intensity_pct: pd.Series,
) -> pd.Series:
    """
    Domain-specific molybdenum grade (Mo_pct) with stoichiometric sulfur cap.

    Step 1 — Base formula:
      Mo_pct = (Cu_pct / R_Cu:Mo) * (Alteration_Intensity_pct / 100) * K_lith

    Step 2 — Domain parameters from Alteration_Name and Lithology_Name.

    Step 3 — Sulfur mass-balance cap:
      S_consumed = 0.3494*Chalcopyrite + 0.2554*Bornite + 0.5345*Pyrite
                 + 0.2014*Chalcocite + 0.3353*Covellite
      S_excess = max(0, S_pct - S_consumed)
      Mo_max = S_excess * 1.496
      Mo_pct_final = min(Mo_pct_calculated, Mo_max)
    """

    require_columns(
        df,
        [
            "Alteration_Name",
            "Lithology_Name",
            "Copper_Total",
            "Sulfur",
            "Chalcopyrite",
            "Bornite",
            "Pyrite",
            "Chalcocite",
            "Covellite",
        ],
    )

    cu_pct = df["Copper_Total"]
    s_pct = df["Sulfur"]

    r_cu_mo = df["Alteration_Name"].map(R_CU_MO_BY_ALTERATION)
    k_lith = df["Lithology_Name"].map(K_LITH_BY_LITHOLOGY)

    mo_calculated = (
        (cu_pct / r_cu_mo)
        * (alteration_intensity_pct / 100.0)
        * k_lith
    )

    s_consumed = (
        0.3494 * df["Chalcopyrite"]
        + 0.2554 * df["Bornite"]
        + 0.5345 * df["Pyrite"]
        + 0.2014 * df["Chalcocite"]
        + 0.3353 * df["Covellite"]
    )
    s_excess = np.maximum(0.0, s_pct - s_consumed)
    mo_max = s_excess * MO_S_RATIO

    mo_final = np.minimum(mo_calculated, mo_max)
    mo_final = mo_final.clip(lower=0.0)

    return mo_final.round(4)


def calculate_quartz_pct(df: pd.DataFrame) -> pd.Series:
    """
    Quartz_pct (wt%) from lithology base silica, alteration multiplier,
    aluminium contribution, and non-quartz mass-balance space factor.

    M_non_quartz = Chalcopyrite + Bornite + Pyrite + Chalcocite
                 + Covellite + Clay + Carbonate

    Space_Factor = max(0.05, 1 − M_non_quartz / 100)

    Quartz_pct = min(
        85.0,
        (Q_base × M_alt + 0.15 × Aluminium) × Space_Factor
    )
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Chalcopyrite",
            "Bornite",
            "Pyrite",
            "Chalcocite",
            "Covellite",
            "Clay",
            "Carbonate",
            "Aluminium",
        ],
    )

    q_base = df["Lithology_Name"].map(QUARTZ_Q_BASE_BY_LITHOLOGY)
    if q_base.isna().any():
        bad = sorted(df.loc[q_base.isna(), "Lithology_Name"].astype(str).unique())
        raise ValueError(f"Missing Q_base for Lithology_Name: {bad}")

    m_alt = df["Alteration_Name"].map(QUARTZ_M_ALT_BY_ALTERATION)
    if m_alt.isna().any():
        bad = sorted(df.loc[m_alt.isna(), "Alteration_Name"].astype(str).unique())
        raise ValueError(f"Missing M_alt for Alteration_Name: {bad}")

    m_non_quartz = (
        df["Chalcopyrite"]
        + df["Bornite"]
        + df["Pyrite"]
        + df["Chalcocite"]
        + df["Covellite"]
        + df["Clay"]
        + df["Carbonate"]
    )
    space_factor = np.maximum(QUARTZ_SPACE_FACTOR_MIN, 1.0 - m_non_quartz / 100.0)

    quartz = (q_base * m_alt + 0.15 * df["Aluminium"]) * space_factor
    return np.minimum(QUARTZ_PCT_MAX, quartz).round(2)


def calculate_bond_work_index(df: pd.DataFrame) -> pd.Series:
    """
    Bond Work Index (BWi, kWh/t) from domain baseline + mineral deviations.

    BWi = Clamp(
        BWi_base(Lithology, Alteration)
        + ΔBWi_Quartz
        - ΔBWi_Clay
        + ΔBWi_Pyrite,
        6.0,
        24.0,
    )

    Where domain means are per (Lithology_Name, Alteration_Name):
      ΔBWi_Quartz = 0.12 × (Quartz_pct − mean Quartz_pct in domain)
      ΔBWi_Clay   = 0.08 × (Clay − mean Clay in domain)
      ΔBWi_Pyrite = 0.05 × Pyrite

    Requires derived Quartz_pct and Clay.
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Quartz_pct",
            "Clay",
            "Pyrite",
        ],
    )

    domain_keys = list(zip(df["Lithology_Name"], df["Alteration_Name"]))
    bwi_base = pd.Series(
        [BWI_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = bwi_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(l), str(a))
                for l, a in zip(
                    df.loc[unknown, "Lithology_Name"],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(f"Unknown Lithology-Alteration domains for BWi_base: {bad}")

    domain = ["Lithology_Name", "Alteration_Name"]
    quartz_domain_mean = df.groupby(domain)["Quartz_pct"].transform("mean")
    clay_domain_mean = df.groupby(domain)["Clay"].transform("mean")

    delta_quartz = 0.12 * (df["Quartz_pct"] - quartz_domain_mean)
    delta_clay = 0.08 * (df["Clay"] - clay_domain_mean)
    delta_pyrite = 0.05 * df["Pyrite"]

    bwi = bwi_base + delta_quartz - delta_clay + delta_pyrite
    return bwi.clip(lower=BWI_MIN, upper=BWI_MAX).round(2)


def calculate_axb(df: pd.DataFrame) -> pd.Series:
    """
    Axb (SAG Mill Impact Hardness) from baseline + domain deviations.

    Inverse scale: lower Axb means harder, more impact-resistant rock.

    Clamp: [15.0, 180.0]

    Formula:
      Axb = Clamp(
        Axb_base(Lithology, Alteration)
        + ΔAxb_Quartz
        + ΔAxb_Clay
        + ΔAxb_Intensity,
        15.0,
        180.0
      )

    Mineral deviations use domain means (Lithology_Name, Alteration_Name):
      ΔAxb_Quartz = -0.40 * (Quartz_pct - mean Quartz_pct in domain)
      ΔAxb_Clay   = +0.85 * (Clay - mean Clay in domain)

    Alteration intensity:
      ΔAxb_Intensity = Axb_base * (Alteration_Intensity_pct / 100) * I_factor
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Quartz_pct",
            "Clay",
            "Alteration_Intensity_pct",
        ],
    )

    domain_keys = list(zip(df["Lithology_Name"], df["Alteration_Name"]))
    axb_base = pd.Series(
        [AXB_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = axb_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(l), str(a))
                for l, a in zip(
                    df.loc[unknown, "Lithology_Name"],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(f"Unknown Lithology-Alteration domains for Axb_base: {bad}")

    # Domain means for quartz/clay deviations (computed per (Lithology, Alteration)).
    domain = ["Lithology_Name", "Alteration_Name"]
    quartz_domain_mean = df.groupby(domain)["Quartz_pct"].transform("mean")
    clay_domain_mean = df.groupby(domain)["Clay"].transform("mean")

    delta_quartz = -0.40 * (df["Quartz_pct"] - quartz_domain_mean)
    delta_clay = 0.85 * (df["Clay"] - clay_domain_mean)

    i_factor = df["Alteration_Name"].map(AXB_I_FACTOR_BY_ALTERATION)
    if i_factor.isna().any():
        bad = sorted(df.loc[i_factor.isna(), "Alteration_Name"].astype(str).unique())
        raise ValueError(f"Missing I_factor for Alteration_Name: {bad}")

    delta_intensity = (
        axb_base * (df["Alteration_Intensity_pct"] / 100.0) * i_factor
    )

    axb = axb_base + delta_quartz + delta_clay + delta_intensity
    return axb.clip(lower=AXB_CLAMP_MIN, upper=AXB_CLAMP_MAX).round(2)


def calculate_bond_abrasion_index(df: pd.DataFrame) -> pd.Series:
    """
    Bond Abrasion Index (Ai, grams) from domain baseline + mineral deviations.

    Ai = Clamp(
        Ai_base(Lithology, Alteration)
        + ΔAi_Quartz
        + ΔAi_Pyrite
        - ΔAi_Clay,
        0.01,
        0.80,
    )

    Where domain means are per (Lithology_Name, Alteration_Name):
      ΔAi_Quartz = 0.006 × (Quartz_pct − mean Quartz_pct in domain)
      ΔAi_Pyrite = 0.003 × Pyrite
      ΔAi_Clay   = 0.002 × (Clay − mean Clay in domain)
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Quartz_pct",
            "Clay",
            "Pyrite",
        ],
    )

    domain_keys = list(zip(df["Lithology_Name"], df["Alteration_Name"]))
    ai_base = pd.Series(
        [AI_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = ai_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(l), str(a))
                for l, a in zip(
                    df.loc[unknown, "Lithology_Name"],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(f"Unknown Lithology-Alteration domains for Ai_base: {bad}")

    domain = ["Lithology_Name", "Alteration_Name"]
    quartz_domain_mean = df.groupby(domain)["Quartz_pct"].transform("mean")
    clay_domain_mean = df.groupby(domain)["Clay"].transform("mean")

    delta_quartz = 0.006 * (df["Quartz_pct"] - quartz_domain_mean)
    delta_pyrite = 0.003 * df["Pyrite"]
    delta_clay = 0.002 * (df["Clay"] - clay_domain_mean)

    ai = ai_base + delta_quartz + delta_pyrite - delta_clay
    return ai.clip(lower=AI_CLAMP_MIN, upper=AI_CLAMP_MAX).round(3)


def calculate_ucs_mpa(df: pd.DataFrame) -> pd.Series:
    """
    Unconfined Compressive Strength (UCS, MPa).

    UCS = Clamp(
        UCS_base(Lithology, Alteration) × [1.0 + ΔUCS_Intensity]
        + ΔUCS_Quartz
        − ΔUCS_Clay,
        15.0,
        320.0,
    )

    Where:
      ΔUCS_Intensity = (Alteration_Intensity_pct / 100) × U_factor
      ΔUCS_Quartz    = 1.2 × (Quartz_pct − mean Quartz_pct in domain)
      ΔUCS_Clay      = 1.5 × (Clay − mean Clay in domain)
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Quartz_pct",
            "Clay",
            "Alteration_Intensity_pct",
        ],
    )

    domain_keys = list(zip(df["Lithology_Name"], df["Alteration_Name"]))
    ucs_base = pd.Series(
        [UCS_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = ucs_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(l), str(a))
                for l, a in zip(
                    df.loc[unknown, "Lithology_Name"],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(f"Unknown Lithology-Alteration domains for UCS_base: {bad}")

    u_factor = df["Alteration_Name"].map(UCS_U_FACTOR_BY_ALTERATION)
    if u_factor.isna().any():
        bad = sorted(df.loc[u_factor.isna(), "Alteration_Name"].astype(str).unique())
        raise ValueError(f"Missing U_factor for Alteration_Name: {bad}")

    delta_intensity = (df["Alteration_Intensity_pct"] / 100.0) * u_factor

    domain = ["Lithology_Name", "Alteration_Name"]
    quartz_domain_mean = df.groupby(domain)["Quartz_pct"].transform("mean")
    clay_domain_mean = df.groupby(domain)["Clay"].transform("mean")

    delta_quartz = 1.2 * (df["Quartz_pct"] - quartz_domain_mean)
    delta_clay = 1.5 * (df["Clay"] - clay_domain_mean)

    ucs = ucs_base * (1.0 + delta_intensity) + delta_quartz - delta_clay
    return ucs.clip(lower=UCS_CLAMP_MIN, upper=UCS_CLAMP_MAX).round(1)


def calculate_rqd(df: pd.DataFrame) -> pd.Series:
    """
    Rock Quality Designation (RQD, %).

    RQD = Clamp(
        RQD_base(Lithology, Alteration)
        − ΔRQD_Intensity
        − Penalty_Weathering
        − ΔRQD_Clay,
        5.0,
        100.0,
    )

    Where:
      ΔRQD_Intensity = 0.35 × Alteration_Intensity_pct
      Penalty_Weathering = 45 (Oxide) / 20 (Transition) / 0 (Fresh)
      ΔRQD_Clay = 0.40 × (Clay − mean Clay in domain)
    """

    require_columns(
        df,
        [
            "Lithology_Name",
            "Alteration_Name",
            "Alteration_Intensity_pct",
            "Weathering_State",
            "Clay",
        ],
    )

    domain_keys = list(zip(df["Lithology_Name"], df["Alteration_Name"]))
    rqd_base = pd.Series(
        [RQD_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = rqd_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(l), str(a))
                for l, a in zip(
                    df.loc[unknown, "Lithology_Name"],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(f"Unknown Lithology-Alteration domains for RQD_base: {bad}")

    delta_intensity = 0.35 * df["Alteration_Intensity_pct"]

    weathering_penalty = df["Weathering_State"].map(RQD_WEATHERING_PENALTY)
    if weathering_penalty.isna().any():
        bad = sorted(
            df.loc[weathering_penalty.isna(), "Weathering_State"].astype(str).unique()
        )
        raise ValueError(f"Missing weathering penalty for Weathering_State: {bad}")

    clay_domain_mean = df.groupby(
        ["Lithology_Name", "Alteration_Name"]
    )["Clay"].transform("mean")
    delta_clay = 0.40 * (df["Clay"] - clay_domain_mean)

    rqd = rqd_base - delta_intensity - weathering_penalty - delta_clay
    return rqd.clip(lower=RQD_CLAMP_MIN, upper=RQD_CLAMP_MAX).round(1)


def calculate_moisture_pct(df: pd.DataFrame) -> pd.Series:
    """
    Moisture Content (Moisture_pct, weight %).

    Moisture_pct = Clamp(
        Moisture_base(Weathering_State, Alteration)
        + ΔMoisture_Clay
        + ΔMoisture_Lithology,
        0.2,
        12.0,
    )

    Where:
      ΔMoisture_Clay = 0.12 × Clay
      ΔMoisture_Lithology =
        +0.30 Andesite
        +0.10 Diorite / Granodiorite
         0.00 Granite / QMP
    """

    require_columns(
        df,
        [
            "Weathering_State",
            "Alteration_Name",
            "Lithology_Name",
            "Clay",
        ],
    )

    weathering_key = df["Weathering_State"].map(MOISTURE_WEATHERING_KEY)
    if weathering_key.isna().any():
        bad = sorted(
            df.loc[weathering_key.isna(), "Weathering_State"].astype(str).unique()
        )
        raise ValueError(f"Unknown Weathering_State for Moisture_base: {bad}")

    domain_keys = list(zip(weathering_key, df["Alteration_Name"]))
    moisture_base = pd.Series(
        [MOISTURE_BASE_MATRIX.get(key, np.nan) for key in domain_keys],
        index=df.index,
        dtype=float,
    )

    unknown = moisture_base.isna()
    if unknown.any():
        bad = sorted(
            {
                (str(w), str(a))
                for w, a in zip(
                    weathering_key.loc[unknown],
                    df.loc[unknown, "Alteration_Name"],
                )
            }
        )
        raise ValueError(
            f"Unknown Weathering-Alteration domains for Moisture_base: {bad}"
        )

    delta_clay = 0.12 * df["Clay"]
    delta_lith = df["Lithology_Name"].map(MOISTURE_LITH_DELTA)
    if delta_lith.isna().any():
        bad = sorted(
            df.loc[delta_lith.isna(), "Lithology_Name"].astype(str).unique()
        )
        raise ValueError(f"Missing lithology moisture delta for: {bad}")

    moisture = moisture_base + delta_clay + delta_lith
    return moisture.clip(lower=MOISTURE_CLAMP_MIN, upper=MOISTURE_CLAMP_MAX).round(2)


def calculate_dwi(df: pd.DataFrame) -> pd.Series:
    """
    Drop Weight Index (DWi, kWh/m³) from bulk density and Axb.

    DWi = (100 × ρ) / (A × b)

    Where:
      ρ   = Bulk_Density_t_m3 (t/m³)
      A×b = Axb (SAG mill impact hardness)

    Scale (inverse of Axb): higher DWi = harder rock.
    """

    require_columns(df, ["Bulk_Density_t_m3", "Axb"])

    rho = df["Bulk_Density_t_m3"]
    axb = df["Axb"]

    if (axb <= 0).any():
        raise ValueError("Axb must be > 0 to calculate DWi.")

    dwi = (100.0 * rho) / axb
    return dwi.round(2)


def reorder_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply practical column chronology for the final geomet CSV."""
    missing = [c for c in FINAL_COLUMN_ORDER if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for final order: {missing}")

    extras = [c for c in df.columns if c not in FINAL_COLUMN_ORDER]
    return df[FINAL_COLUMN_ORDER + extras]


def main() -> None:
    print(f"Reading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    print("Calculating Alteration_Intensity_pct...")
    df["Alteration_Intensity_pct"] = calculate_alteration_intensity_pct(df)

    print("Calculating Weathering_State...")
    df["Weathering_State"] = calculate_weathering_state(df)

    print("Calculating Mo_pct...")
    df["Mo_pct"] = calculate_mo_pct(df, df["Alteration_Intensity_pct"])

    print("Calculating Quartz_pct...")
    df["Quartz_pct"] = calculate_quartz_pct(df)

    print("Calculating Bond_Work_Index...")
    df["Bond_Work_Index"] = calculate_bond_work_index(df)

    print("Calculating Axb...")
    df["Axb"] = calculate_axb(df)

    print("Calculating DWi...")
    df["DWi"] = calculate_dwi(df)

    print("Calculating Bond_Abrasion_Index...")
    df["Bond_Abrasion_Index"] = calculate_bond_abrasion_index(df)

    print("Calculating UCS_mpa...")
    df["UCS_mpa"] = calculate_ucs_mpa(df)

    print("Calculating RQD...")
    df["RQD"] = calculate_rqd(df)

    print("Calculating Moisture_pct...")
    df["Moisture_pct"] = calculate_moisture_pct(df)

    print("Reordering columns for final CSV...")
    df = reorder_final_columns(df)

    print(f"Writing {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)

    print("Done.")
    print(
        df[
            [
                "Alteration_Name",
                "Alteration_Intensity_pct",
                "Weathering_State",
                "Mo_pct",
                "Quartz_pct",
                "Bond_Work_Index",
                "Axb",
                "DWi",
                "Bond_Abrasion_Index",
                "UCS_mpa",
                "RQD",
                "Moisture_pct",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
