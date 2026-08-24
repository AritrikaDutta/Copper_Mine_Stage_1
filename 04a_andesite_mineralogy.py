# =============================================================================
# SYNTHETIC PORPHYRY COPPER DATASET
# ANDESITE + ALL ALTERATION ZONES
#
# 17 GEOLOGICAL / CHEMICAL / MINERALOGICAL VARIABLES
#
# Variables:
# Copper (Total)
# Sulfur
# Iron
# Magnesium
# Bornite
# Pyrite
# Aluminium
# Lead
# Zinc
# Mercury
# Clay
# Covellite
# Carbonate
# Chalcocite
# Arsenic
# Chalcopyrite
# =============================================================================

import numpy as np
import pandas as pd
from scipy.stats import truncnorm


# =============================================================================
# 1. SETTINGS
# =============================================================================

SEED = 42
N_BY_ALTERATION = {
    "Phyllic": 171916,
    "Potassic": 75208,
    "Propylitic": 114635,
    "Argillic": 40450,
    "Advanced Argillic": 9963,
    "Sodic-Calcic": 3434,
}

rng = np.random.default_rng(SEED)

OUTPUT_FILE = "Andesite_data.csv"

if sum(N_BY_ALTERATION.values()) != 415606:
    raise ValueError("Andesite alteration counts must sum to 415,606.")


# =============================================================================
# 2. ALTERATION ZONES
# =============================================================================

ZONES = [
    "Potassic",
    "Phyllic",
    "Argillic",
    "Propylitic",
    "Sodic-Calcic",
    "Advanced Argillic"
]


# =============================================================================
# 3. TRUNCATED GAUSSIAN SAMPLING
# =============================================================================

def gaussian(low, high, size):

    # Exact zero / fixed value
    if low == high:
        return np.full(size, low)

    mean = (low + high) / 2
    sd = (high - low) / 6

    a = (low - mean) / sd
    b = (high - mean) / sd

    return truncnorm.rvs(
        a,
        b,
        loc=mean,
        scale=sd,
        size=size,
        random_state=rng
    )


# =============================================================================
# 4. GEOLOGICAL RANGES
#
# ~0%  -> exactly 0
# <X   -> 0 to X
# =============================================================================

RANGES = {

    # =========================================================================
    # POTASSIC
    # =========================================================================

    "Potassic": {

        "Copper_Total": (0.27, 0.75),
        "Sulfur": (0.38, 1.35),
        "Iron": (0.32, 1.13),
        "Magnesium": (0.12, 0.40),
        "Bornite": (0.10, 0.35),
        "Pyrite": (0.19, 0.64),
        "Aluminium": (0.70, 1.80),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (0.00, 0.00),
        "Covellite": (0.00, 0.00),
        "Carbonate": (0.00, 0.00),
        "Chalcocite": (0.00, 0.00),

        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.36, 1.00)
    },


    # =========================================================================
    # PHYLLIC
    # =========================================================================

    "Phyllic": {

        "Copper_Total": (0.10, 0.66),
        "Sulfur": (2.76, 8.55),
        "Iron": (2.40, 7.42),

        "Magnesium": (0.05, 0.30),
        "Bornite": (0.10, 0.35),
        "Pyrite": (3.00, 11.00),
        "Aluminium": (2.00, 4.20),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (0.00, 0.00),
        "Covellite": (0.00, 0.00),
        "Carbonate": (0.00, 0.00),
        "Chalcocite": (0.00, 0.00),

        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.20, 1.31)
    },


    # =========================================================================
    # ARGILLIC
    # =========================================================================

    "Argillic": {

        "Copper_Total": (0.03, 0.19),
        "Sulfur": (0.41, 2.06),
        "Iron": (0.36, 1.78),

        "Magnesium": (0.05, 0.20),
        "Bornite": (0.00, 0.06),
        "Pyrite": (0.60, 3.50),
        "Aluminium": (2.30, 5.60),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (12.00, 28.00),
        "Covellite": (0.00, 0.00),
        "Carbonate": (0.00, 0.00),
        "Chalcocite": (0.00, 0.00),

        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.05, 0.29)
    },


    # =========================================================================
    # PROPYLITIC
    # =========================================================================

    "Propylitic": {

        "Copper_Total": (0.01, 0.04),
        "Sulfur": (0.35, 1.06),
        "Iron": (0.31, 0.93),

        "Magnesium": (0.75, 3.00),
        "Bornite": (0.00, 0.06),
        "Pyrite": (0.60, 1.90),

        "Aluminium": (1.00, 3.00),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (0.00, 0.00),
        "Covellite": (0.00, 0.00),
        "Carbonate": (2.00, 8.00),
        "Chalcocite": (0.00, 0.00),

        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.02, 0.08)
    },


    # =========================================================================
    # SODIC-CALCIC
    # =========================================================================

    "Sodic-Calcic": {

        "Copper_Total": (0.02, 0.14),
        "Sulfur": (0.12, 0.50),
        "Iron": (0.90, 3.05),

        "Magnesium": (0.15, 0.45),
        "Bornite": (0.00, 0.00),
        "Pyrite": (0.15, 0.70),
        "Aluminium": (0.50, 1.50),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (0.00, 0.00),
        "Covellite": (0.00, 0.00),
        "Carbonate": (0.30, 1.50),
        "Chalcocite": (0.00, 0.00),

        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.03, 0.21)
    },


    # =========================================================================
    # ADVANCED ARGILLIC
    # =========================================================================

    "Advanced Argillic": {

        "Copper_Total": (0.11, 0.55),
        "Sulfur": (1.78, 5.48),
        "Iron": (1.50, 4.52),

        "Magnesium": (0.00, 0.00),
        "Bornite": (0.13, 0.29),
        "Pyrite": (3.50, 10.50),

        "Aluminium": (3.00, 8.00),

        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),

        "Clay": (12.00, 22.00),
        "Covellite": (0.13, 0.29),
        "Carbonate": (0.00, 0.00),
        "Chalcocite": (0.10, 0.22),

        "Arsenic": (0.037, 0.185),
        "Chalcopyrite": (0.10, 0.22)
    }
}


# =============================================================================
# 5. SAMPLE FROM RANGE
# =============================================================================

def sample_range(zone, variable, n):

    low, high = RANGES[zone][variable]

    return gaussian(
        low,
        high,
        n
    )


# =============================================================================
# 6. GENERATE ONE ZONE
# =============================================================================

def generate_zone(zone, n):

    r = RANGES[zone]

    data = {}


    # =========================================================================
    # COPPER
    # =========================================================================

    copper = sample_range(
        zone,
        "Copper_Total",
        n
    )

    data["Copper_Total"] = copper


    # Normalize Copper only for creating relationships
    cu_low, cu_high = r["Copper_Total"]

    cu_norm = (
        (copper - cu_low)
        /
        max(cu_high - cu_low, 1e-12)
    )


    # =========================================================================
    # CHALCOPYRITE
    #
    # Positive relationship with Copper
    # =========================================================================

    cp_low, cp_high = r["Chalcopyrite"]

    chalcopyrite = (
        cp_low
        +
        cu_norm * (cp_high - cp_low)
    )

    chalcopyrite += rng.normal(
        0,
        (cp_high - cp_low) * 0.04,
        n
    )

    chalcopyrite = np.clip(
        chalcopyrite,
        cp_low,
        cp_high
    )

    data["Chalcopyrite"] = chalcopyrite


    # =========================================================================
    # BORNITE
    #
    # Positive relationship with Copper where Bornite exists
    # =========================================================================

    bn_low, bn_high = r["Bornite"]

    if bn_high > bn_low:

        bornite = (
            bn_low
            +
            cu_norm * (bn_high - bn_low)
        )

        bornite += rng.normal(
            0,
            (bn_high - bn_low) * 0.06,
            n
        )

        bornite = np.clip(
            bornite,
            bn_low,
            bn_high
        )

    else:

        bornite = np.full(
            n,
            bn_low
        )

    data["Bornite"] = bornite


    # =========================================================================
    # CHALCOCITE
    #
    # Positive relationship with Copper where present
    # =========================================================================

    ch_low, ch_high = r["Chalcocite"]

    if ch_high > ch_low:

        chalcocite = (
            ch_low
            +
            cu_norm * (ch_high - ch_low)
        )

        chalcocite += rng.normal(
            0,
            (ch_high - ch_low) * 0.05,
            n
        )

        chalcocite = np.clip(
            chalcocite,
            ch_low,
            ch_high
        )

    else:

        chalcocite = np.full(
            n,
            ch_low
        )

    data["Chalcocite"] = chalcocite


    # =========================================================================
    # COVELLITE
    #
    # Positive relationship with Copper where present
    # =========================================================================

    cv_low, cv_high = r["Covellite"]

    if cv_high > cv_low:

        covellite = (
            cv_low
            +
            cu_norm * (cv_high - cv_low)
        )

        covellite += rng.normal(
            0,
            (cv_high - cv_low) * 0.05,
            n
        )

        covellite = np.clip(
            covellite,
            cv_low,
            cv_high
        )

    else:

        covellite = np.full(
            n,
            cv_low
        )

    data["Covellite"] = covellite


    # =========================================================================
    # PYRITE
    # =========================================================================

    pyrite = sample_range(
        zone,
        "Pyrite",
        n
    )

    data["Pyrite"] = pyrite


    # =========================================================================
    # SULFUR
    #
    # Related to:
    # Pyrite + Chalcopyrite + Bornite
    # =========================================================================

    sulfur_low, sulfur_high = r["Sulfur"]

    pyrite_norm = (
        (pyrite - r["Pyrite"][0])
        /
        max(
            r["Pyrite"][1] - r["Pyrite"][0],
            1e-12
        )
    )

    cp_norm = (
        (chalcopyrite - cp_low)
        /
        max(
            cp_high - cp_low,
            1e-12
        )
    )

    if bn_high > bn_low:

        bn_norm = (
            (bornite - bn_low)
            /
            max(
                bn_high - bn_low,
                1e-12
            )
        )

    else:

        bn_norm = np.zeros(n)


    sulfur_index = (
        0.50 * pyrite_norm
        +
        0.35 * cp_norm
        +
        0.15 * bn_norm
    )

    sulfur = (
        sulfur_low
        +
        sulfur_index
        *
        (sulfur_high - sulfur_low)
    )

    sulfur += rng.normal(
        0,
        (sulfur_high - sulfur_low) * 0.03,
        n
    )

    sulfur = np.clip(
        sulfur,
        sulfur_low,
        sulfur_high
    )

    data["Sulfur"] = sulfur


    # =========================================================================
    # IRON
    #
    # Related mainly to Pyrite, with a smaller Chalcopyrite contribution
    # =========================================================================

    iron_low, iron_high = r["Iron"]

    iron_index = (
        0.70 * pyrite_norm
        +
        0.30 * cp_norm
    )

    iron = (
        iron_low
        +
        iron_index
        *
        (iron_high - iron_low)
    )

    iron += rng.normal(
        0,
        (iron_high - iron_low) * 0.03,
        n
    )

    iron = np.clip(
        iron,
        iron_low,
        iron_high
    )

    data["Iron"] = iron


    # =========================================================================
    # MAGNESIUM
    # =========================================================================

    data["Magnesium"] = sample_range(
        zone,
        "Magnesium",
        n
    )


    # =========================================================================
    # CLAY
    # =========================================================================

    data["Clay"] = sample_range(
        zone,
        "Clay",
        n
    )


    # =========================================================================
    # ALUMINIUM
    #
    # Related to Clay where Clay is present.
    # =========================================================================

    al_low, al_high = r["Aluminium"]

    if r["Clay"][1] > r["Clay"][0]:

        clay_norm = (
            (data["Clay"] - r["Clay"][0])
            /
            max(
                r["Clay"][1] - r["Clay"][0],
                1e-12
            )
        )

        aluminium = (
            al_low
            +
            clay_norm * (al_high - al_low)
        )

        aluminium += rng.normal(
            0,
            (al_high - al_low) * 0.05,
            n
        )

        aluminium = np.clip(
            aluminium,
            al_low,
            al_high
        )

    else:

        aluminium = sample_range(
            zone,
            "Aluminium",
            n
        )

    data["Aluminium"] = aluminium


    # =========================================================================
    # CARBONATE
    # =========================================================================

    data["Carbonate"] = sample_range(
        zone,
        "Carbonate",
        n
    )


    # =========================================================================
    # LEAD
    # =========================================================================

    data["Lead"] = sample_range(
        zone,
        "Lead",
        n
    )


    # =========================================================================
    # ZINC
    # =========================================================================

    data["Zinc"] = sample_range(
        zone,
        "Zinc",
        n
    )


    # =========================================================================
    # MERCURY
    # =========================================================================

    data["Mercury"] = sample_range(
        zone,
        "Mercury",
        n
    )


    # =========================================================================
    # ARSENIC
    # =========================================================================

    data["Arsenic"] = sample_range(
        zone,
        "Arsenic",
        n
    )



    # =========================================================================
    # RETURN DATAFRAME
    # =========================================================================

    return pd.DataFrame(data)


# =============================================================================
# 7. GENERATE ALL ZONES
# =============================================================================

all_data = []

for zone in ZONES:

    n_points = N_BY_ALTERATION[zone]
    print(f"Generating {zone} (n={n_points:,})...")

    zone_data = generate_zone(
        zone,
        n_points
    )

    zone_data["Lithology"] = "Andesite"
    zone_data["Alteration"] = zone

    all_data.append(
        zone_data
    )


# =============================================================================
# 8. COMBINE DATA
# =============================================================================

df = pd.concat(
    all_data,
    ignore_index=True
)


# =============================================================================
# 9. FINAL COLUMN ORDER
# =============================================================================

columns = [

    "Lithology",
    "Alteration",

    "Copper_Total",
    "Sulfur",
    "Iron",
    "Magnesium",
    "Bornite",
    "Pyrite",
    "Aluminium",

    "Lead",
    "Zinc",
    "Mercury",

    "Clay",
    "Covellite",
    "Carbonate",
    "Chalcocite",
    "Arsenic",

    "Chalcopyrite"
]

df = df[columns]


# =============================================================================
# 10. SHUFFLE
# =============================================================================

df = df.sample(
    frac=1,
    random_state=SEED
).reset_index(drop=True)


# =============================================================================
# 11. RANGE VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("RANGE VALIDATION")
print("=" * 80)

all_valid = True

for zone in ZONES:

    print(f"\n--- {zone} ---")

    zone_df = df[
        df["Alteration"] == zone
    ]

    for variable, (low, high) in RANGES[zone].items():

        actual_min = zone_df[variable].min()
        actual_max = zone_df[variable].max()

        valid = (
            actual_min >= low - 1e-10
            and
            actual_max <= high + 1e-10
        )

        if not valid:
            all_valid = False

        symbol = "✓" if valid else "✗"

        print(
            f"{variable:<18} "
            f"{actual_min:.6f} - "
            f"{actual_max:.6f} "
            f"{symbol}"
        )


print("\nOverall validation:")

if all_valid:
    print("✓ ALL VALUES ARE WITHIN THE SPECIFIED RANGES")
else:
    print("✗ SOME VALUES ARE OUTSIDE THE SPECIFIED RANGES")


# =============================================================================
# 12. CORRELATION CHECK
# =============================================================================

print("\n" + "=" * 80)
print("GEOLOGICAL CORRELATION CHECK")
print("=" * 80)

correlation_pairs = [

    ("Copper_Total", "Chalcopyrite"),
    ("Copper_Total", "Bornite"),
    ("Copper_Total", "Chalcocite"),
    ("Copper_Total", "Covellite"),

    ("Pyrite", "Sulfur"),
    ("Chalcopyrite", "Sulfur"),
    ("Bornite", "Sulfur"),

    ("Pyrite", "Iron"),
    ("Chalcopyrite", "Iron"),

    ("Clay", "Aluminium")
]


for x, y in correlation_pairs:

    correlation = df[x].corr(
        df[y]
    )

    print(
        f"{x:<18} vs "
        f"{y:<18}: "
        f"{correlation:+.3f}"
    )


# =============================================================================
# 13. DATASET SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("DATASET SUMMARY")
print("=" * 80)

print(
    f"Total samples : {len(df):,}"
)

print(
    f"Total columns : {len(df.columns)}"
)

print(
    f"Dataset shape : {df.shape}"
)


# =============================================================================
# 14. ALTERATION COUNTS
# =============================================================================

print("\n" + "=" * 80)
print("ALTERATION COUNTS")
print("=" * 80)

print(
    df["Alteration"].value_counts()
)


# =============================================================================
# 15. SAVE DATASET
# =============================================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 80)
print("DATASET GENERATED SUCCESSFULLY")
print("=" * 80)

print(
    f"Output file : {OUTPUT_FILE}"
)

print("\nFirst five rows:")

print(
    df.head()
)