# ============================================================
# GRANITE + ALL ALTERATION ZONES
# MULTIVARIATE GAUSSIAN SYNTHETIC DATA GENERATOR
#
# Zones / Alteration types (counts from master Granite trips):
#   Phyllic           7,909
#   Potassic          2,482
#   Propylitic       12,714
#   Argillic          2,293
#   Advanced Argillic   225
#   Sodic-Calcic         27
#   TOTAL            25,650
#
# Output columns start with Lithology, Alteration (no Sample_ID)
# so they match the mineralogy merge schema.
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# 1. SETTINGS
# ============================================================

# Trip counts from master dataset for Granite × Alteration
N_BY_ALTERATION = {
    "Phyllic": 7909,
    "Potassic": 2482,
    "Propylitic": 12714,
    "Argillic": 2293,
    "Advanced Argillic": 225,
    "Sodic-Calcic": 27,
}

RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)

if sum(N_BY_ALTERATION.values()) != 25650:
    raise ValueError(
        "Granite alteration counts must sum to 25,650."
    )


# ============================================================
# 2. VARIABLES
# ============================================================

variables = [
    "Copper_Total",
    "Chalcopyrite",
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
]

N_VARIABLES = len(variables)

if N_VARIABLES != 16:
    raise ValueError(
        "The dataset must contain exactly 16 variables."
    )


# ============================================================
# 3. ALTERATION-ZONE RANGES
# ============================================================

ZONE_RANGES = {

    # --------------------------------------------------------
    # POTASSIC
    # --------------------------------------------------------

    "Potassic": {

        "Copper_Total": (0.30, 0.85),
        "Chalcopyrite": (0.40, 1.13),
        "Sulfur": (0.61, 2.52),
        "Iron": (0.51, 2.13),
        "Magnesium": (0.15, 0.50),
        "Bornite": (0.18, 0.55),
        "Pyrite": (0.40, 1.00),
        "Aluminium": (0.90, 2.40),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (0.0, 0.001),
        "Covellite": (0.0, 0.001),
        "Carbonate": (0.0, 0.001),
        "Chalcocite": (0.0, 0.001),
        "Arsenic": (0.0005, 0.005),
    },


    # --------------------------------------------------------
    # PHYLLIC
    # --------------------------------------------------------

    "Phyllic": {

        "Copper_Total": (0.04, 0.26),
        "Chalcopyrite": (0.08, 0.52),
        "Sulfur": (1.91, 6.11),
        "Iron": (1.66, 5.31),
        "Magnesium": (0.05, 0.20),
        "Bornite": (0.18, 0.55),
        "Pyrite": (3.50, 11.0),
        "Aluminium": (2.00, 4.50),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (0.0, 0.001),
        "Covellite": (0.0, 0.001),
        "Carbonate": (0.0, 0.001),
        "Chalcocite": (0.0, 0.001),
        "Arsenic": (0.0005, 0.005),
    },

    # --------------------------------------------------------
    # ARGILLIC
    # --------------------------------------------------------

    "Argillic": {

        "Copper_Total": (0.01, 0.09),
        "Chalcopyrite": (0.02, 0.14),
        "Sulfur": (0.39, 1.94),
        "Iron": (0.34, 1.69),
        "Magnesium": (0.05, 0.20),
        "Bornite": (0.0, 0.02),
        "Pyrite": (0.70, 3.50),
        "Aluminium": (2.10, 5.20),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (10.0, 25.0),
        "Covellite": (0.0, 0.001),
        "Carbonate": (0.0, 0.001),
        "Chalcocite": (0.0, 0.001),
        "Arsenic": (0.0005, 0.005),
    },


    # --------------------------------------------------------
    # PROPYLITIC
    # --------------------------------------------------------

    "Propylitic": {

        "Copper_Total": (0.006, 0.025),
        "Chalcopyrite": (0.01, 0.05),
        "Sulfur": (0.38, 1.15),
        "Iron": (0.33, 1.00),
        "Magnesium": (0.60, 1.80),
        "Bornite": (0.0, 0.02),
        "Pyrite": (0.70, 2.10),
        "Aluminium": (0.80, 2.20),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (0.0, 0.001),
        "Covellite": (0.0, 0.001),
        "Carbonate": (2.0, 8.0),
        "Chalcocite": (0.0, 0.001),
        "Arsenic": (0.0005, 0.005),
    },


    # --------------------------------------------------------
    # SODIC-CALCIC
    # --------------------------------------------------------

    "Sodic-Calcic": {
        "Copper_Total": (0.025, 0.15),
        "Chalcopyrite": (0.01, 0.05),
        "Sulfur": (0.19, 0.76),
        "Iron": (1.11, 4.43),
        "Magnesium": (0.30, 1.00),
        "Bornite": (0.0, 0.03),
        "Pyrite": (0.30, 1.20),
        "Aluminium": (0.50, 1.50),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (0.0, 0.001),
        "Covellite": (0.0, 0.001),
        "Carbonate": (0.30, 1.20),
        "Chalcocite": (0.0, 0.001),
        "Arsenic": (0.0005, 0.005),
    },


    # --------------------------------------------------------
    # ADVANCED ARGILLIC
    # --------------------------------------------------------

    "Advanced Argillic": {

        "Copper_Total": (0.065, 0.32),
        "Chalcopyrite": (0.05, 0.12),
        "Sulfur": (1.92, 6.11),
        "Iron": (1.64, 5.17),
        "Magnesium": (0.0, 0.001),
        "Bornite": (0.07, 0.16),
        "Pyrite": (3.50, 11.0),
        "Aluminium": (2.50, 6.50),
        "Lead": (0.0010, 0.0020),
        "Zinc": (0.0030, 0.0070),
        "Mercury": (0.0000029, 0.000096),
        "Clay": (8.0, 16.0),
        "Covellite": (0.05, 0.13),
        "Carbonate": (0.0, 0.001),
        "Chalcocite": (0.05, 0.13),
        "Arsenic": (0.021, 0.106),
    }
}


# ============================================================
# 4. CHECK ALL ZONES HAVE ALL 16 VARIABLES
# ============================================================

for zone, zone_ranges in ZONE_RANGES.items():
    missing = set(variables) - set(zone_ranges.keys())
    if missing:
        raise ValueError(f"{zone} is missing variables: {missing}")


# ============================================================
# 5. PRINT SETTINGS
# ============================================================

print("=" * 75)
print("GRANITE + ALL ALTERATION ZONES")
print("MULTIVARIATE GAUSSIAN SYNTHETIC DATA GENERATION")
print("=" * 75)

print(f"\nNumber of variables per sample : {N_VARIABLES}")
print(f"Number of alteration zones     : {len(ZONE_RANGES)}")
print("Points per alteration zone:")
for zone_name, n_points in N_BY_ALTERATION.items():
    print(f"  {zone_name:<20}: {n_points:,}")
print(f"Total number of samples        : {sum(N_BY_ALTERATION.values()):,}")


# ============================================================
# 6. GAUSSIAN SCALING FUNCTION
# ============================================================

def scale_to_range(values, minimum, maximum):
    """
    Convert a Gaussian dimension into the specified geological range.
    The 0.5 and 99.5 percentiles are used as practical Gaussian bounds 
    so that extreme tails do not dominate the synthetic dataset.
    """

    if maximum <= minimum:
        return np.full_like(values, minimum)
    lower = np.percentile(values, 0.5)
    upper = np.percentile(values, 99.5)

    clipped = np.clip(values, lower, upper)
    normalized = ((clipped - lower) / (upper - lower))

    return (minimum + normalized * (maximum - minimum))

# ============================================================
# 7. GAUSSIAN NOISE
# ============================================================

def gaussian_noise(rng, n, scale=1.0):

    return rng.normal(loc=0.0, scale=scale, size=n)

# ============================================================
# 8. GENERATE ONE ALTERATION ZONE
# ============================================================

def generate_zone(zone_name, zone_ranges, n_points,rng):

    """
    Generate one alteration zone in a structured
    multidimensional Gaussian space.
    """

    # --------------------------------------------------------
    # LATENT GEOLOGICAL FACTORS
    # --------------------------------------------------------

    latent = rng.normal(loc=0.0, scale=1.0, size=(n_points, 6))

    F_CU = latent[:, 0]
    F_SULFIDE = latent[:, 1]
    F_ROCK = latent[:, 2]
    F_TRACE = latent[:, 3]
    F_ALT = latent[:, 4]
    F_GANGUE = latent[:, 5]


    # --------------------------------------------------------
    # RAW VECTOR
    # --------------------------------------------------------

    raw = {}


    # Copper
    raw["Copper_Total"] = (
        0.70 * F_CU
        + 0.20 * F_SULFIDE
        + 0.10 * F_ROCK
        + 0.20 * gaussian_noise(rng, n_points)
    )


    # Sulfur
    raw["Sulfur"] = (
        0.50 * F_SULFIDE
        + 0.30 * F_CU
        + 0.10 * F_ROCK
        + 0.20 * gaussian_noise(rng, n_points)
    )


    # Iron
    raw["Iron"] = (
        0.50 * F_SULFIDE
        + 0.25 * F_CU
        + 0.20 * F_ROCK
        + 0.20 * gaussian_noise(rng, n_points)
    )


    # Magnesium
    raw["Magnesium"] = (
        0.70 * F_ROCK
        + 0.20 * F_ALT
        + 0.25 * gaussian_noise(rng, n_points)
    )


    # Bornite
    raw["Bornite"] = (
        0.75 * F_CU
        + 0.15 * F_SULFIDE
        + 0.25 * gaussian_noise(rng, n_points)
    )


    # Pyrite
    raw["Pyrite"] = (
        0.80 * F_SULFIDE
        + 0.15 * F_CU
        + 0.20 * F_ROCK
        + 0.25 * gaussian_noise(rng, n_points)
    )


    # Aluminium
    raw["Aluminium"] = (
        0.65 * F_ROCK
        + 0.20 * F_ALT
        + 0.15 * F_SULFIDE
        + 0.25 * gaussian_noise(rng, n_points)
    )


    # Lead
    raw["Lead"] = (
        0.60 * F_TRACE
        + 0.20 * F_SULFIDE
        + 0.30 * gaussian_noise(rng, n_points)
    )


    # Zinc
    raw["Zinc"] = (
        0.55 * F_TRACE
        + 0.25 * F_SULFIDE
        + 0.30 * gaussian_noise(rng, n_points)
    )


    # Mercury
    raw["Mercury"] = (
        0.60 * F_TRACE
        + 0.15 * F_ALT
        + 0.35 * gaussian_noise(rng, n_points)
    )


    # Clay
    raw["Clay"] = (
        0.65 * F_ALT
        + 0.20 * F_ROCK
        + 0.35 * gaussian_noise(rng, n_points)
    )


    # Covellite
    raw["Covellite"] = (
        0.55 * F_CU
        + 0.25 * F_ALT
        + 0.35 * gaussian_noise(rng, n_points)
    )


    # Carbonate
    raw["Carbonate"] = (
        0.60 * F_ROCK
        + 0.25 * F_ALT
        + 0.35 * gaussian_noise(rng, n_points)
    )


    # Chalcocite
    raw["Chalcocite"] = (
        0.60 * F_CU
        + 0.25 * F_ALT
        + 0.30 * gaussian_noise(rng, n_points)
    )


    # Arsenic
    raw["Arsenic"] = (
        0.60 * F_TRACE
        + 0.25 * F_SULFIDE
        + 0.25 * F_ALT
        + 0.30 * gaussian_noise(rng, n_points)
    )


    # CHALCOPYRITE
    #
    # IMPORTANT:
    #
    # Chalcopyrite is strongly related to copper
    # mineralization.
    #
    # Therefore it is driven mainly by F_CU,
    # with secondary influence from F_SULFIDE.
    #
    # This should produce a strong positive
    # Copper_Total ↔ Chalcopyrite relationship.
    raw["Chalcopyrite"] = (0.80 * F_CU + 0.25 * F_SULFIDE + 0.10 * F_ROCK + 0.15 * gaussian_noise(rng, n_points))


    # --------------------------------------------------------
    # CONVERT TO PHYSICAL RANGES
    # --------------------------------------------------------

    data = {}

    for variable in variables:

        minimum, maximum = zone_ranges[variable]

        data[variable] = scale_to_range(
            raw[variable],
            minimum,
            maximum
        )


    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    zone_df = pd.DataFrame(data)

    zone_df.insert(
        0,
        "Lithology",
        "Granite"
    )

    zone_df.insert(
        1,
        "Alteration",
        zone_name
    )

    return zone_df


# ============================================================
# 9. GENERATE ALL SIX ALTERATION ZONES
# ============================================================

all_zone_data = {}

for zone_name, zone_ranges in ZONE_RANGES.items():

    if zone_name not in N_BY_ALTERATION:
        raise ValueError(
            f"Missing sample count for alteration: {zone_name}"
        )

    n_points = N_BY_ALTERATION[zone_name]

    print("\n" + "-" * 75)
    print(f"GENERATING: GRANITE + {zone_name} (n={n_points:,})")
    print("-" * 75)

    zone_df = generate_zone(
        zone_name,
        zone_ranges,
        n_points,
        rng
    )

    all_zone_data[zone_name] = zone_df

    print(
        f"Generated {len(zone_df):,} samples."
    )


# ============================================================
# 10. COMBINE ALL ZONES
# ============================================================

combined_df = pd.concat(
    all_zone_data.values(),
    ignore_index=True
)


print("\n" + "=" * 75)
print("COMBINED DATASET")
print("=" * 75)

print(
    f"\nShape: {combined_df.shape}"
)

print("\nSamples per alteration zone:")

print(
    combined_df["Alteration"]
    .value_counts()
    .to_string()
)


# ============================================================
# 11. RANGE VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("RANGE VALIDATION")
print("=" * 75)

range_check_all = []

for zone_name, zone_df in all_zone_data.items():

    zone_ranges = ZONE_RANGES[zone_name]

    for variable in variables:

        minimum, maximum = zone_ranges[variable]

        actual_min = zone_df[variable].min()
        actual_max = zone_df[variable].max()

        inside_range = (
            actual_min >= minimum - 1e-12
            and
            actual_max <= maximum + 1e-12
        )

        range_check_all.append({

            "Lithology": "Granite",

            "Alteration": zone_name,

            "Variable": variable,

            "Specified_Min": minimum,

            "Actual_Min": actual_min,

            "Specified_Max": maximum,

            "Actual_Max": actual_max,

            "Inside_Range": inside_range
        })


range_check_df = pd.DataFrame(
    range_check_all
)


print(
    range_check_df
    .to_string(index=False)
)


# ============================================================
# 12. SAVE COMBINED CSV
# ============================================================

csv_filename = "Granite_data.csv"

combined_df.to_csv(
    csv_filename,
    index=False
)


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("FILE CREATED")
print("=" * 75)

print(f"\nOutput CSV:\n  {csv_filename}")

print(
    "\nTotal samples:"
)

print(
    f"  {len(combined_df):,}"
)

print(
    "\nSamples per alteration:"
)

print(
    combined_df[
        "Alteration"
    ]
    .value_counts()
    .to_string()
)

print("\n" + "=" * 75)
print("GENERATION COMPLETE")
print("=" * 75)
