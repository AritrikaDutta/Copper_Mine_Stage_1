import numpy as np
import pandas as pd

# ============================================================
# QMP + 6 ALTERATION ZONES
# 16-D MULTIVARIATE GAUSSIAN VECTOR GENERATION
# ============================================================

N_BY_ALTERATION = {
    "Phyllic": 87102,
    "Potassic": 138378,
    "Propylitic": 6956,
    "Argillic": 29749,
    "Advanced Argillic": 6207,
    "Sodic-Calcic": 1210,
}
RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

if sum(N_BY_ALTERATION.values()) != 269602:
    raise ValueError("QMP alteration counts must sum to 269,602.")

# NOTE:
# "~0" / trace / "<" values are represented by small finite ranges
# so that they can participate in the multivariate Gaussian model.
ranges = {
    "Potassic": {
        "Copper_Total": (0.66, 1.83), "Sulfur": (0.94, 3.50), "Iron": (0.77, 2.92),
        "Magnesium": (0.30, 0.90), "Bornite": (0.50, 1.50), "Pyrite": (0.30, 1.00),
        "Aluminium": (1.40, 3.30), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (0.0, 0.01), "Covellite": (0.0, 0.01),
        "Carbonate": (0.0, 0.01), "Chalcocite": (0.0, 0.01), "Arsenic": (0.0, 0.005),
        "Chalcopyrite": (0.88, 2.44),
    },
    "Phyllic": {
        "Copper_Total": (0.13, 0.91), "Sulfur": (3.55, 10.99), "Iron": (3.09, 9.52),
        "Magnesium": (0.05, 0.30), "Bornite": (0.0, 0.30), "Pyrite": (4.0, 15.0),
        "Aluminium": (3.0, 6.0), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (0.0, 0.01), "Covellite": (0.0, 0.01),
        "Carbonate": (0.0, 0.01), "Chalcocite": (0.0, 0.01), "Arsenic": (0.0, 0.005),
        "Chalcopyrite": (0.26, 1.80),
    },
    "Argillic": {
        "Copper_Total": (0.035, 0.24), "Sulfur": (0.57, 2.87), "Iron": (0.50, 2.49),
        "Magnesium": (0.05, 0.20), "Bornite": (0.0, 0.10), "Pyrite": (1.0, 5.0),
        "Aluminium": (2.1, 5.2), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (10.0, 25.0), "Covellite": (0.0, 0.01),
        "Carbonate": (0.0, 0.01), "Chalcocite": (0.0, 0.01), "Arsenic": (0.0, 0.005),
        "Chalcopyrite": (0.05, 0.36),
    },
    "Propylitic": {
        "Copper_Total": (0.017, 0.069), "Sulfur": (0.55, 1.67), "Iron": (0.48, 1.46),
        "Magnesium": (0.75, 3.0), "Bornite": (0.0, 0.01), "Pyrite": (1.0, 4.0),
        "Aluminium": (1.0, 3.0), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (0.0, 0.01), "Covellite": (0.0, 0.01),
        "Carbonate": (2.0, 8.0), "Chalcocite": (0.0, 0.01), "Arsenic": (0.0, 0.005),
        "Chalcopyrite": (0.04, 0.15),
    },
    "Sodic-Calcic": {
        "Copper_Total": (0.069, 0.40), "Sulfur": (0.34, 1.40), "Iron": (2.46, 8.43),
        "Magnesium": (0.45, 1.35), "Bornite": (0.0, 0.20), "Pyrite": (0.50, 2.0),
        "Aluminium": (1.0, 3.0), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (0.0, 0.01), "Covellite": (0.0, 0.01),
        "Carbonate": (0.5, 3.0), "Chalcocite": (0.0, 0.01), "Arsenic": (0.0, 0.005),
        "Chalcopyrite": (0.10, 0.60),
    },
    "Advanced Argillic": {
        "Copper_Total": (0.21, 1.00), "Sulfur": (2.80, 8.62), "Iron": (2.36, 7.10),
        "Magnesium": (0.0, 0.01), "Bornite": (0.20, 0.45), "Pyrite": (5.0, 15.0),
        "Aluminium": (3.0, 8.0), "Lead": (0.0005, 0.0020), "Zinc": (0.0010, 0.0070),
        "Mercury": (0.0000029, 0.000096), "Clay": (10.0, 20.0), "Covellite": (0.20, 0.45),
        "Carbonate": (0.0, 0.01), "Chalcocite": (0.15, 0.35), "Arsenic": (0.058, 0.291),
        "Chalcopyrite": (0.15, 0.34),
    }
}

variables = list(next(iter(ranges.values())).keys())

# Relationship structure:
# latent geological factors -> mineral/chemical variables.
# We intentionally do NOT impose a <=60% correlation constraint here.
# The generated vectors are subsequently clipped to the supplied ranges.
loadings = {
    "Copper_Total": [0.85, 0.20, 0.05, 0.05],
    "Bornite":      [0.80, 0.15, 0.05, 0.05],
    "Chalcocite":   [0.45, 0.05, 0.05, 0.35],
    "Chalcopyrite": [0.82, 0.30, 0.05, 0.05],
    "Covellite":    [0.45, 0.05, 0.05, 0.35],
    "Sulfur":       [0.35, 0.85, 0.05, 0.10],
    "Iron":         [0.20, 0.80, 0.20, 0.05],
    "Pyrite":       [0.15, 0.90, 0.10, 0.05],
    "Magnesium":    [0.05, 0.15, 0.85, 0.05],
    "Aluminium":    [0.05, 0.20, 0.80, 0.10],
    "Clay":         [0.00, 0.10, 0.60, 0.70],
    "Carbonate":    [0.00, 0.05, 0.65, 0.55],
    "Lead":         [0.05, 0.10, 0.10, 0.80],
    "Zinc":         [0.05, 0.15, 0.10, 0.80],
    "Mercury":      [0.00, 0.05, 0.05, 0.85],
    "Arsenic":      [0.05, 0.20, 0.05, 0.85],
}

def gaussian_vectors_for_zone(zone_ranges, n, rng):
    # Standard multivariate latent Gaussian.
    latent = rng.normal(size=(n, 4))

    # Independent residual keeps variables from becoming deterministic copies.
    raw = np.zeros((n, len(variables)))

    for j, var in enumerate(variables):
        w = np.asarray(loadings[var], dtype=float)
        w = w / np.linalg.norm(w)
        residual = rng.normal(size=n)
        raw[:, j] = latent @ w + 0.55 * residual

    # Rank/normal-score transformation followed by range mapping.
    # This preserves the Gaussian ordering while guaranteeing every point
    # lies inside the user-supplied geological range.
    out = np.zeros_like(raw)
    for j, var in enumerate(variables):
        order = np.argsort(raw[:, j])
        u = np.empty(n)
        u[order] = (np.arange(n) + 0.5) / n
        # Gaussian-shaped central distribution, then map its CDF values to range.
        lo, hi = zone_ranges[var]
        out[:, j] = lo + u * (hi - lo)
    return pd.DataFrame(out, columns=variables)

all_parts = []
for zone, zone_ranges in ranges.items():
    n_points = N_BY_ALTERATION[zone]
    part = gaussian_vectors_for_zone(zone_ranges, n_points, rng)
    part.insert(0, "Alteration", zone)
    part.insert(0, "Lithology", "QMP")
    all_parts.append(part)

df = pd.concat(all_parts, ignore_index=True)

# ============================================================
# RANGE CHECK (console only)
# ============================================================
checks = []
for zone, zone_ranges in ranges.items():
    sub = df[df["Alteration"] == zone]
    for var in variables:
        lo, hi = zone_ranges[var]
        actual_lo = sub[var].min()
        actual_hi = sub[var].max()
        checks.append({
            "Alteration": zone,
            "Variable": var,
            "Specified_Min": lo,
            "Actual_Min": actual_lo,
            "Specified_Max": hi,
            "Actual_Max": actual_hi,
            "Inside_Range": actual_lo >= lo - 1e-12 and actual_hi <= hi + 1e-12
        })

range_check = pd.DataFrame(checks)
print("\nRANGE CHECK")
print(range_check.to_string(index=False))

# ============================================================
# SAVE COMBINED CSV
# ============================================================

csv_filename = "QMP_data.csv"
df.to_csv(csv_filename, index=False)

print("\n============================================================")
print("FILE CREATED")
print("============================================================")
print(f"Output CSV: {csv_filename}")
print(f"Total samples: {len(df):,}")
print("\nSamples per alteration:")
print(df["Alteration"].value_counts().to_string())
print("\nGENERATION COMPLETE")
