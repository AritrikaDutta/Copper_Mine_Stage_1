# =============================================================================
# GRANODIORITE + ALL ALTERATION ZONES
# 17-D GEOLOGICAL + MINERALOGICAL SYNTHETIC DATA GENERATION
#
# Variables:
#   Copper (Total)
#   Sulfur
#   Iron
#   Magnesium
#   Bornite
#   Pyrite
#   Aluminium
#   Lead
#   Zinc
#   Mercury
#   Clay
#   Covellite
#   Carbonate
#   Chalcocite
#   Arsenic
#   Chalcopyrite
#
# Distribution:
#   Gaussian / truncated Gaussian
#
# Geological relationships preserved:
#   Copper       <-> Chalcopyrite
#   Copper       <-> Bornite
#   Copper       <-> Chalcocite
#   Chalcopyrite -> Sulfur
#   Chalcopyrite -> Iron
#   Pyrite       -> Sulfur
#   Pyrite       -> Iron
#   Clay         <-> Aluminium
#
# Output:
#   Granodiorite_data.csv
# =============================================================================

import numpy as np
import pandas as pd


# =============================================================================
# SETTINGS
# =============================================================================

SEED = 42
N_BY_ALTERATION = {
    "Phyllic": 51195,
    "Potassic": 11607,
    "Propylitic": 41316,
    "Argillic": 5776,
    "Advanced Argillic": 1104,
    "Sodic-Calcic": 468,
}

rng = np.random.default_rng(SEED)

ZONES = [
    "Potassic",
    "Phyllic",
    "Argillic",
    "Propylitic",
    "Sodic-Calcic",
    "Advanced Argillic"
]

if sum(N_BY_ALTERATION.values()) != 111466:
    raise ValueError("Granodiorite alteration counts must sum to 111,466.")


# =============================================================================
# GAUSSIAN HELPER FUNCTIONS
# =============================================================================

def gaussian_clip(mean, std, low, high, size):
    """
    Generate Gaussian-distributed values and clip them
    within the specified range.
    """

    x = rng.normal(mean, std, size)

    return np.clip(
        x,
        low,
        high
    )


def gaussian_from_range(low, high, size, concentration=0.95):
    """
    Generate approximately Gaussian-distributed values
    centered within the supplied range.
    """

    # Handle fixed / zero-width ranges
    if high <= low:
        return np.full(size, low)

    mean = (low + high) / 2

    std = (
        (high - low)
        / (2 * concentration * 2.0)
    )

    return gaussian_clip(
        mean,
        std,
        low,
        high,
        size
    )


# =============================================================================
# GRANODIORITE GEOLOGICAL RANGES
# =============================================================================

RANGES = {

    # -------------------------------------------------------------------------
    # POTASSIC
    # -------------------------------------------------------------------------

    "Potassic": {

        "Copper_Total": (0.60, 1.66),
        "Sulfur": (0.85, 3.18),
        "Iron": (0.70, 2.65),
        "Magnesium": (0.27, 0.82),
        "Bornite": (0.45, 1.36),
        "Pyrite": (0.27, 0.91),
        "Aluminium": (1.30, 3.00),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (0.00, 0.005),
        "Covellite": (0.00, 0.005),
        "Carbonate": (0.00, 0.005),
        "Chalcocite": (0.00, 0.005),
        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.80, 2.22)
    },


    # -------------------------------------------------------------------------
    # PHYLLIC
    # -------------------------------------------------------------------------

    "Phyllic": {

        "Copper_Total": (0.12, 0.83),
        "Sulfur": (3.23, 9.99),
        "Iron": (2.81, 8.66),
        "Magnesium": (0.05, 0.30),
        "Bornite": (0.00, 0.27),
        "Pyrite": (3.64, 13.60),
        "Aluminium": (2.70, 5.50),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (0.00, 0.005),
        "Covellite": (0.00, 0.005),
        "Carbonate": (0.00, 0.005),
        "Chalcocite": (0.00, 0.005),
        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.24, 1.65)
    },


    # -------------------------------------------------------------------------
    # ARGILLIC
    # -------------------------------------------------------------------------

    "Argillic": {

        "Copper_Total": (0.032, 0.22),
        "Sulfur": (0.52, 2.61),
        "Iron": (0.45, 2.26),
        "Magnesium": (0.05, 0.20),
        "Bornite": (0.00, 0.09),
        "Pyrite": (0.90, 4.50),
        "Aluminium": (2.10, 5.20),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (10.0, 25.0),
        "Covellite": (0.00, 0.005),
        "Carbonate": (0.00, 0.005),
        "Chalcocite": (0.00, 0.005),
        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.05, 0.33)
    },


    # -------------------------------------------------------------------------
    # PROPYLITIC
    # -------------------------------------------------------------------------

    "Propylitic": {

        "Copper_Total": (0.015, 0.063),
        "Sulfur": (0.50, 1.52),
        "Iron": (0.44, 1.33),
        "Magnesium": (0.75, 3.00),
        "Bornite": (0.00, 0.18),
        "Pyrite": (0.91, 3.64),
        "Aluminium": (1.00, 3.00),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (0.00, 0.005),
        "Covellite": (0.00, 0.005),
        "Carbonate": (2.00, 8.00),
        "Chalcocite": (0.00, 0.005),
        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.03, 0.13)
    },


    # -------------------------------------------------------------------------
    # SODIC-CALCIC
    # -------------------------------------------------------------------------

    "Sodic-Calcic": {

        "Copper_Total": (0.063, 0.36),
        "Sulfur": (0.31, 1.27),
        "Iron": (2.24, 7.66),
        "Magnesium": (0.41, 1.23),
        "Bornite": (0.00, 0.18),
        "Pyrite": (0.45, 1.80),
        "Aluminium": (1.00, 3.00),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (0.00, 0.005),
        "Covellite": (0.00, 0.005),
        "Carbonate": (0.50, 3.00),
        "Chalcocite": (0.00, 0.005),
        "Arsenic": (0.00, 0.005),
        "Chalcopyrite": (0.10, 0.54)
    },


    # -------------------------------------------------------------------------
    # ADVANCED ARGILLIC
    # -------------------------------------------------------------------------

    "Advanced Argillic": {

        "Copper_Total": (0.16, 0.80),
        "Sulfur": (2.55, 7.84),
        "Iron": (2.15, 6.45),
        "Magnesium": (0.00, 0.005),
        "Bornite": (0.18, 0.41),
        "Pyrite": (4.50, 13.60),
        "Aluminium": (3.00, 8.00),
        "Lead": (0.00, 0.002),
        "Zinc": (0.00, 0.007),
        "Mercury": (0.00, 0.0001),
        "Clay": (10.0, 20.0),
        "Covellite": (0.18, 0.41),
        "Carbonate": (0.00, 0.005),
        "Chalcocite": (0.14, 0.32),
        "Arsenic": (0.053, 0.264),
        "Chalcopyrite": (0.14, 0.31)
    }
}


# =============================================================================
# GENERATE ONE ALTERATION ZONE
# =============================================================================

def generate_zone(zone, n):

    r = RANGES[zone]

    data = {}

    # =========================================================================
    # MINERALS
    # =========================================================================

    data["Bornite"] = gaussian_from_range(
        *r["Bornite"],
        n
    )

    data["Pyrite"] = gaussian_from_range(
        *r["Pyrite"],
        n
    )

    data["Chalcocite"] = gaussian_from_range(
        *r["Chalcocite"],
        n
    )

    data["Covellite"] = gaussian_from_range(
        *r["Covellite"],
        n
    )


    # =========================================================================
    # CHALCOPYRITE
    #
    # Directly generated within the geological range.
    #
    # Copper will later be correlated with Chalcopyrite.
    # =========================================================================

    data["Chalcopyrite"] = gaussian_from_range(
        *r["Chalcopyrite"],
        n
    )


    # =========================================================================
    # COPPER
    #
    # Copper is positively related to:
    #
    #   Chalcopyrite
    #   Bornite
    #   Chalcocite
    #
    # We first create a normalized mineralogical copper signal,
    # then map it into the specified Copper range.
    # =========================================================================

    copper_min, copper_max = r["Copper_Total"]

    mineral_signal = (

        0.65 * data["Chalcopyrite"] +

        0.20 * data["Bornite"] +

        0.10 * data["Chalcocite"] +

        0.05 * data["Covellite"]

    )

    signal_min = mineral_signal.min()
    signal_max = mineral_signal.max()

    if signal_max > signal_min:

        normalized_signal = (
            mineral_signal - signal_min
        ) / (
            signal_max - signal_min
        )

    else:

        normalized_signal = np.full(
            n,
            0.5
        )


    # Add moderate random geological variation
    normalized_signal += rng.normal(
        0,
        0.08,
        n
    )

    normalized_signal = np.clip(
        normalized_signal,
        0,
        1
    )

    data["Copper_Total"] = (
        copper_min
        +
        normalized_signal *
        (copper_max - copper_min)
    )


    # =========================================================================
    # SULFUR
    #
    # Sulfur is related to:
    #
    #   Pyrite
    #   Chalcopyrite
    #   Bornite
    # =========================================================================

    sulfur_base = gaussian_from_range(
        *r["Sulfur"],
        n
    )

    sulfur_signal = (

        0.50 * sulfur_base +

        0.25 * data["Pyrite"] +

        0.20 * data["Chalcopyrite"] +

        0.05 * data["Bornite"]

    )

    sulfur_min = sulfur_signal.min()
    sulfur_max = sulfur_signal.max()

    if sulfur_max > sulfur_min:

        sulfur_norm = (
            sulfur_signal - sulfur_min
        ) / (
            sulfur_max - sulfur_min
        )

    else:

        sulfur_norm = np.full(
            n,
            0.5
        )

    sulfur_norm += rng.normal(
        0,
        0.05,
        n
    )

    sulfur_norm = np.clip(
        sulfur_norm,
        0,
        1
    )

    data["Sulfur"] = (
        r["Sulfur"][0]
        +
        sulfur_norm *
        (
            r["Sulfur"][1]
            -
            r["Sulfur"][0]
        )
    )


    # =========================================================================
    # IRON
    #
    # Iron is related primarily to:
    #
    #   Pyrite
    #   Chalcopyrite
    #
    # The Sodic-Calcic zone has intrinsically high iron.
    # =========================================================================

    iron_base = gaussian_from_range(
        *r["Iron"],
        n
    )

    iron_signal = (

        0.60 * iron_base +

        0.25 * data["Pyrite"] +

        0.15 * data["Chalcopyrite"]

    )

    iron_min = iron_signal.min()
    iron_max = iron_signal.max()

    if iron_max > iron_min:

        iron_norm = (
            iron_signal - iron_min
        ) / (
            iron_max - iron_min
        )

    else:

        iron_norm = np.full(
            n,
            0.5
        )

    iron_norm += rng.normal(
        0,
        0.05,
        n
    )

    iron_norm = np.clip(
        iron_norm,
        0,
        1
    )

    data["Iron"] = (
        r["Iron"][0]
        +
        iron_norm *
        (
            r["Iron"][1]
            -
            r["Iron"][0]
        )
    )


    # =========================================================================
    # MAGNESIUM
    # =========================================================================

    data["Magnesium"] = gaussian_from_range(
        *r["Magnesium"],
        n
    )


    # =========================================================================
    # ALUMINIUM
    #
    # Aluminium and Clay are positively related where clay is significant.
    # =========================================================================

    data["Clay"] = gaussian_from_range(
        *r["Clay"],
        n
    )

    aluminium_base = gaussian_from_range(
        *r["Aluminium"],
        n
    )

    if r["Clay"][1] > 1:

        clay_norm = (

            data["Clay"] - r["Clay"][0]

        ) / (

            r["Clay"][1] - r["Clay"][0]

        )

        clay_norm = np.clip(
            clay_norm,
            0,
            1
        )

        aluminium_signal = (

            0.65 * aluminium_base +

            0.35 * (
                r["Aluminium"][0]
                +
                clay_norm *
                (
                    r["Aluminium"][1]
                    -
                    r["Aluminium"][0]
                )
            )

        )

        # Normalize back into the specified range
        aluminium_signal = np.clip(
            aluminium_signal,
            r["Aluminium"][0],
            r["Aluminium"][1]
        )

        data["Aluminium"] = aluminium_signal

    else:

        data["Aluminium"] = aluminium_base


    # =========================================================================
    # TRACE ELEMENTS
    # =========================================================================

    data["Lead"] = gaussian_from_range(
        *r["Lead"],
        n
    )

    data["Zinc"] = gaussian_from_range(
        *r["Zinc"],
        n
    )

    data["Mercury"] = gaussian_from_range(
        *r["Mercury"],
        n
    )

    data["Arsenic"] = gaussian_from_range(
        *r["Arsenic"],
        n
    )


    # =========================================================================
    # CARBONATE
    # =========================================================================

    data["Carbonate"] = gaussian_from_range(
        *r["Carbonate"],
        n
    )



    return pd.DataFrame(data)


# =============================================================================
# GENERATE ALL ALTERATION ZONES
# =============================================================================

zone_frames = []


for zone in ZONES:

    n_points = N_BY_ALTERATION[zone]
    print(f"Generating {zone} (n={n_points:,})...")

    df_zone = generate_zone(
        zone,
        n_points
    )

    # Add merge keys
    df_zone["Lithology"] = "Granodiorite"
    df_zone["Alteration"] = zone

    zone_frames.append(
        df_zone
    )


# =============================================================================
# COMBINE ALL ZONES
# =============================================================================

df = pd.concat(
    zone_frames,
    ignore_index=True
)


# =============================================================================
# COLUMN ORDER
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
# RANGE VALIDATION
# =============================================================================

print("\n")
print("=" * 90)
print("RANGE VALIDATION")
print("=" * 90)


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

            actual_min >= low - 1e-9

            and

            actual_max <= high + 1e-9

        )

        if not valid:
            all_valid = False

        symbol = "✓" if valid else "✗"

        print(
            f"{variable:<18}"
            f"{actual_min:.6f} - "
            f"{actual_max:.6f} "
            f"{symbol}"
        )


print("\n")


if all_valid:

    print("✓ ALL VARIABLES ARE WITHIN THEIR SPECIFIED GEOLOGICAL RANGES")

else:

    print("✗ SOME VARIABLES ARE OUTSIDE THEIR SPECIFIED RANGES")


# =============================================================================
# CORRELATION CHECK
# =============================================================================

print("\n")
print("=" * 90)
print("IMPORTANT GEOLOGICAL CORRELATIONS")
print("=" * 90)


correlation_pairs = [

    ("Copper_Total", "Chalcopyrite"),

    ("Copper_Total", "Bornite"),

    ("Copper_Total", "Chalcocite"),

    ("Chalcopyrite", "Sulfur"),

    ("Chalcopyrite", "Iron"),

    ("Pyrite", "Sulfur"),

    ("Pyrite", "Iron"),

    ("Clay", "Aluminium")

]


for a, b in correlation_pairs:

    corr = df[a].corr(
        df[b]
    )

    print(
        f"{a:<20}"
        f" vs "
        f"{b:<20}"
        f": {corr:+.3f}"
    )


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

print("\n")
print("=" * 90)
print("SUMMARY STATISTICS")
print("=" * 90)


numeric_columns = [

    c for c in df.columns

    if c not in [
        "Lithology",
        "Alteration"
    ]

]


summary = df[
    numeric_columns
].agg(
    ["min", "mean", "max", "std"]
).T


print(summary)


# =============================================================================
# ALTERATION COUNTS
# =============================================================================

print("\n")
print("=" * 90)
print("ALTERATION COUNTS")
print("=" * 90)

print(
    df["Alteration"].value_counts()
)


# =============================================================================
# DATASET INFORMATION
# =============================================================================

print("\n")
print("=" * 90)
print("DATASET GENERATED SUCCESSFULLY")
print("=" * 90)

print(
    f"Total samples : {len(df):,}"
)

print(
    f"Variables     : {len(df.columns)}"
)

print(
    f"Dataset shape : {df.shape}"
)


# =============================================================================
# SAVE CSV
# =============================================================================

output_file = (
    "Granodiorite_data.csv"
)


df.to_csv(
    output_file,
    index=False
)


print(
    f"Output file   : {output_file}"
)


# =============================================================================
# FIRST FIVE ROWS
# =============================================================================

print("\nFirst five rows:")

print(
    df.head()
)