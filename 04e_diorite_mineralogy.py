# =============================================================================
# DIORITE PORPHYRY COPPER SYNTHETIC DATASET
# =============================================================================
# 6 alteration zones with master trip counts (total 53,522 samples)
#
# ONLY THE REQUESTED GEOLOGICAL / MINERALOGICAL VARIABLES ARE GENERATED:
#
# Copper (Total), Sulfur, Iron, Magnesium, Bornite, Pyrite, Aluminium,
# Clay, Carbonate, Chalcocite, Covellite, Lead, Zinc, Arsenic, Mercury,
# Chalcopyrite
# =============================================================================

import numpy as np
import pandas as pd

# =============================================================================
# SETTINGS
# =============================================================================

SEED = 42
N_BY_ALTERATION = {
    "Phyllic": 18840,
    "Potassic": 3893,
    "Propylitic": 24421,
    "Argillic": 3302,
    "Advanced Argillic": 392,
    "Sodic-Calcic": 2674,
}
OUTPUT_FILE = "Diorite_data.csv"

rng = np.random.default_rng(SEED)

if sum(N_BY_ALTERATION.values()) != 53522:
    raise ValueError("Diorite alteration counts must sum to 53,522.")


# =============================================================================
# GAUSSIAN GENERATOR
# =============================================================================

def gaussian(n, low, high, mean_ratio=0.50, std_ratio=0.16):

    if low == high:
        return np.full(n, low)

    mean = low + mean_ratio * (high - low)
    std = std_ratio * (high - low)

    values = rng.normal(mean, std, n)

    return np.clip(values, low, high)


# =============================================================================
# LATENT VARIABLE GENERATOR
# =============================================================================

def latent_to_range(latent, low, high):

    if low == high:
        return np.full(len(latent), low)

    latent_min = latent.min()
    latent_max = latent.max()

    if latent_max == latent_min:
        return np.full(len(latent), (low + high) / 2)

    values = (
        low
        + (latent - latent_min)
        / (latent_max - latent_min)
        * (high - low)
    )

    return np.clip(values, low, high)


# =============================================================================
# ZONE RANGES
# =============================================================================

RANGES = {

    # -------------------------------------------------------------------------
    # POTASSIC
    # -------------------------------------------------------------------------

    "Potassic": {

        "Copper_Total": (0.42, 1.16),
        "Sulfur": (0.60, 2.23),
        "Iron": (0.49, 1.86),
        "Magnesium": (0.15, 0.50),
        "Bornite": (0.32, 0.95),
        "Pyrite": (0.19, 0.64),
        "Aluminium": (0.90, 2.10),

        "Clay": (0.0, 0.0),
        "Carbonate": (0.0, 0.0),
        "Chalcocite": (0.0, 0.0),
        "Covellite": (0.0, 0.0),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.0, 0.005),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.56, 1.55),
    },


    # -------------------------------------------------------------------------
    # PHYLLIC
    # -------------------------------------------------------------------------

    "Phyllic": {

        "Copper_Total": (0.08, 0.58),
        "Sulfur": (2.26, 6.99),
        "Iron": (1.97, 6.05),
        "Magnesium": (0.05, 0.30),
        "Bornite": (0.0, 0.19),
        "Pyrite": (2.54, 9.54),
        "Aluminium": (1.90, 3.80),

        "Clay": (0.0, 0.0),
        "Carbonate": (0.0, 0.0),
        "Chalcocite": (0.0, 0.0),
        "Covellite": (0.0, 0.0),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.0, 0.005),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.16, 1.15),
    },


    # -------------------------------------------------------------------------
    # ARGILLIC
    # -------------------------------------------------------------------------

    "Argillic": {

        "Copper_Total": (0.02, 0.15),
        "Sulfur": (0.36, 1.83),
        "Iron": (0.32, 1.58),
        "Magnesium": (0.05, 0.20),
        "Bornite": (0.0, 0.06),
        "Pyrite": (0.64, 3.18),
        "Aluminium": (2.10, 5.20),

        "Clay": (10, 25),
        "Carbonate": (0.0, 0.0),
        "Chalcocite": (0.0, 0.0),
        "Covellite": (0.0, 0.0),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.0, 0.005),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.03, 0.23),
    },


    # -------------------------------------------------------------------------
    # PROPYLITIC
    # -------------------------------------------------------------------------

    "Propylitic": {

        "Copper_Total": (0.01, 0.04),
        "Sulfur": (0.35, 1.06),
        "Iron": (0.31, 0.93),
        "Magnesium": (0.75, 3.00),
        "Bornite": (0.0, 0.06),
        "Pyrite": (0.64, 2.54),
        "Aluminium": (1.00, 3.00),

        "Clay": (0.0, 0.0),
        "Carbonate": (2.00, 8.00),
        "Chalcocite": (0.0, 0.0),
        "Covellite": (0.0, 0.0),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.0, 0.005),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.02, 0.08),
    },


    # -------------------------------------------------------------------------
    # SODIC-CALCIC
    # -------------------------------------------------------------------------

    "Sodic-Calcic": {

        "Copper_Total": (0.04, 0.25),
        "Sulfur": (0.22, 0.89),
        "Iron": (1.56, 5.36),
        "Magnesium": (0.45, 1.35),
        "Bornite": (0.0, 0.13),
        "Pyrite": (0.32, 1.27),
        "Aluminium": (1.00, 3.00),

        "Clay": (0.0, 0.0),
        "Carbonate": (0.50, 3.00),
        "Chalcocite": (0.0, 0.0),
        "Covellite": (0.0, 0.0),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.0, 0.005),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.06, 0.38),
    },


    # -------------------------------------------------------------------------
    # ADVANCED ARGILLIC
    # -------------------------------------------------------------------------

    "Advanced Argillic": {

        "Copper_Total": (0.11, 0.55),
        "Sulfur": (1.78, 5.48),
        "Iron": (1.50, 4.52),
        "Magnesium": (0.0, 0.0),
        "Bornite": (0.13, 0.29),
        "Pyrite": (3.20, 9.50),
        "Aluminium": (3.00, 8.00),

        "Clay": (10, 20),
        "Carbonate": (0.0, 0.0),
        "Chalcocite": (0.10, 0.22),
        "Covellite": (0.13, 0.29),

        "Lead": (0.0, 0.002),
        "Zinc": (0.0, 0.007),
        "Arsenic": (0.037, 0.185),
        "Mercury": (0.0, 0.0001),

        # UPDATED
        "Chalcopyrite": (0.10, 0.22),
    }
}


# =============================================================================
# GENERATE ONE ZONE
# =============================================================================

def generate_zone(zone, n):

    r = RANGES[zone]

    # -------------------------------------------------------------------------
    # SHARED GEOLOGICAL FACTORS
    # -------------------------------------------------------------------------

    copper_factor = rng.normal(0, 1, n)
    sulphide_factor = rng.normal(0, 1, n)
    alteration_factor = rng.normal(0, 1, n)
    mechanical_factor = rng.normal(0, 1, n)

    # =========================================================================
    # CHALCOPYRITE
    # =========================================================================
    #
    # Primarily controlled by copper + sulphide geological factors.
    #

    chalcopyrite_latent = (
        0.65 * copper_factor
        + 0.45 * sulphide_factor
        + rng.normal(0, 0.35, n)
    )

    chalcopyrite = latent_to_range(
        chalcopyrite_latent,
        r["Chalcopyrite"][0],
        r["Chalcopyrite"][1]
    )

    # =========================================================================
    # BORNITE
    # =========================================================================

    bornite_latent = (
        0.75 * copper_factor
        + 0.25 * sulphide_factor
        + rng.normal(0, 0.30, n)
    )

    bornite = latent_to_range(
        bornite_latent,
        r["Bornite"][0],
        r["Bornite"][1]
    )

    # =========================================================================
    # PYRITE
    # =========================================================================

    pyrite_latent = (
        0.90 * sulphide_factor
        + rng.normal(0, 0.35, n)
    )

    pyrite = latent_to_range(
        pyrite_latent,
        r["Pyrite"][0],
        r["Pyrite"][1]
    )

    # =========================================================================
    # CHALCOCITE
    # =========================================================================

    chalcocite = gaussian(
        n,
        r["Chalcocite"][0],
        r["Chalcocite"][1],
        mean_ratio=0.40,
        std_ratio=0.18
    )

    # =========================================================================
    # COVELLITE
    # =========================================================================

    covellite = gaussian(
        n,
        r["Covellite"][0],
        r["Covellite"][1],
        mean_ratio=0.40,
        std_ratio=0.18
    )

    # =========================================================================
    # TOTAL COPPER
    # =========================================================================
    #
    # Copper is related to copper-bearing minerals:
    #
    # Chalcopyrite + Bornite + Chalcocite + Covellite
    #

    copper_signal = (
        0.60 * chalcopyrite
        + 0.35 * bornite
        + 0.65 * chalcocite
        + 0.60 * covellite
        + rng.normal(
            0,
            0.05 * (r["Copper_Total"][1] - r["Copper_Total"][0]),
            n
        )
    )

    copper = latent_to_range(
        copper_signal,
        r["Copper_Total"][0],
        r["Copper_Total"][1]
    )

    # =========================================================================
    # SULFUR
    # =========================================================================
    #
    # Sulfur increases with sulphide minerals.
    #

    sulfur_signal = (
        0.50 * chalcopyrite
        + 0.85 * pyrite
        + 0.35 * bornite
        + 0.25 * chalcocite
        + 0.25 * covellite
        + rng.normal(
            0,
            0.08 * (r["Sulfur"][1] - r["Sulfur"][0]),
            n
        )
    )

    sulfur = latent_to_range(
        sulfur_signal,
        r["Sulfur"][0],
        r["Sulfur"][1]
    )

    # =========================================================================
    # IRON
    # =========================================================================
    #
    # Mainly related to pyrite and chalcopyrite.
    # Sodic-Calcic additionally has a magnetite contribution.
    #

    iron_signal = (
        0.35 * chalcopyrite
        + 0.80 * pyrite
        + 0.20 * sulphide_factor
    )

    if zone == "Sodic-Calcic":

        magnetite_factor = rng.normal(0, 1, n)

        iron_signal += (
            1.0
            + 0.60 * magnetite_factor
        )

    iron_signal += rng.normal(
        0,
        0.08 * (r["Iron"][1] - r["Iron"][0]),
        n
    )

    iron = latent_to_range(
        iron_signal,
        r["Iron"][0],
        r["Iron"][1]
    )

    # =========================================================================
    # MAGNESIUM
    # =========================================================================

    magnesium = gaussian(
        n,
        r["Magnesium"][0],
        r["Magnesium"][1],
        mean_ratio=0.45,
        std_ratio=0.16
    )

    # =========================================================================
    # CLAY
    # =========================================================================
    #
    # Clay is strongly controlled by alteration intensity.
    #

    clay_latent = (
        0.80 * alteration_factor
        + rng.normal(0, 0.40, n)
    )

    clay = latent_to_range(
        clay_latent,
        r["Clay"][0],
        r["Clay"][1]
    )

    # =========================================================================
    # ALUMINIUM
    # =========================================================================
    #
    # Aluminium increases with clay / alteration intensity.
    #

    clay_normalized = (
        (clay - clay.mean())
        / (clay.std() + 1e-9)
    )

    aluminium_latent = (
        0.70 * alteration_factor
        + 0.55 * clay_normalized
        + rng.normal(0, 0.35, n)
    )

    aluminium = latent_to_range(
        aluminium_latent,
        r["Aluminium"][0],
        r["Aluminium"][1]
    )

    # =========================================================================
    # CARBONATE
    # =========================================================================

    carbonate = gaussian(
        n,
        r["Carbonate"][0],
        r["Carbonate"][1],
        mean_ratio=0.45,
        std_ratio=0.18
    )

    # =========================================================================
    # TRACE ELEMENTS
    # =========================================================================

    lead = gaussian(
        n,
        r["Lead"][0],
        r["Lead"][1],
        mean_ratio=0.35,
        std_ratio=0.20
    )

    zinc = gaussian(
        n,
        r["Zinc"][0],
        r["Zinc"][1],
        mean_ratio=0.35,
        std_ratio=0.20
    )

    mercury = gaussian(
        n,
        r["Mercury"][0],
        r["Mercury"][1],
        mean_ratio=0.35,
        std_ratio=0.18
    )

    arsenic = gaussian(
        n,
        r["Arsenic"][0],
        r["Arsenic"][1],
        mean_ratio=0.45,
        std_ratio=0.18
    )


    # =========================================================================
    # BUILD DATAFRAME
    # =========================================================================

    df = pd.DataFrame({

        "Copper_Total": copper,
        "Sulfur": sulfur,
        "Iron": iron,
        "Magnesium": magnesium,
        "Bornite": bornite,
        "Pyrite": pyrite,
        "Aluminium": aluminium,
        "Clay": clay,
        "Carbonate": carbonate,
        "Chalcocite": chalcocite,
        "Covellite": covellite,
        "Lead": lead,
        "Zinc": zinc,
        "Arsenic": arsenic,
        "Mercury": mercury,
        "Chalcopyrite": chalcopyrite

    })

    df.insert(0, "Alteration", zone)
    df.insert(0, "Lithology", "Diorite")

    return df


# =============================================================================
# GENERATE ALL ZONES
# =============================================================================

zone_data = []

for zone in RANGES.keys():

    n_points = N_BY_ALTERATION[zone]
    print(f"Generating {zone} (n={n_points:,})...")

    zone_df = generate_zone(
        zone,
        n_points
    )

    zone_data.append(zone_df)


# =============================================================================
# COMBINE ALL ZONES
# =============================================================================

df = pd.concat(
    zone_data,
    ignore_index=True
)


# =============================================================================
# COLUMN ORDER
# =============================================================================

df = df[
    ["Lithology", "Alteration"]
    + [
        "Copper_Total",
        "Sulfur",
        "Iron",
        "Magnesium",
        "Bornite",
        "Pyrite",
        "Aluminium",
        "Clay",
        "Carbonate",
        "Chalcocite",
        "Covellite",
        "Lead",
        "Zinc",
        "Arsenic",
        "Mercury",
        "Chalcopyrite"
    ]
]


# =============================================================================
# SHUFFLE
# =============================================================================

df = df.sample(
    frac=1,
    random_state=SEED
).reset_index(drop=True)


# =============================================================================
# SAVE
# =============================================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# BASIC OUTPUT
# =============================================================================

print("\n" + "=" * 80)
print("DATASET GENERATED SUCCESSFULLY")
print("=" * 80)

print(f"Total samples : {len(df):,}")
print(f"Total columns : {len(df.columns)}")
print(f"Output file   : {OUTPUT_FILE}")

print("\nColumns:")
for column in df.columns:
    print(column)

print("\nDataset shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())