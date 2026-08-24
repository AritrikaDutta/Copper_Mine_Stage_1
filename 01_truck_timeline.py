import random
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# 1. SIMULATION SETTINGS
# ============================================================

START_DATE = "2025-01-01"
SIMULATION_DAYS = 365

NUM_TRUCKS = 80

# Trips per truck per roster day (variable)
MIN_DAILY_TRIPS = 28
MAX_DAILY_TRIPS = 32

# Trips per truck per shift
MIN_SHIFT_TRIPS = 12
MAX_SHIFT_TRIPS = 16

# Payload range in tonnes (Cat 797F rated capacity)
MIN_PAYLOAD = 340.0
MAX_PAYLOAD = 363.0

# Arrival -> Departure (spotting, loading, departure)
MIN_DWELL_MINUTES = 4
MAX_DWELL_MINUTES = 8

# Previous Departure -> Next Arrival (haul cycle)
MIN_INTER_TRIP_GAP = 25
MAX_INTER_TRIP_GAP = 40

# Fleet stagger at every shift start
MIN_STAGGER_MINUTES = 0
MAX_STAGGER_MINUTES = 30

# Shift change delay (handover, inspection) before first trip
MIN_SHIFT_CHANGE_MINUTES = 30
MAX_SHIFT_CHANGE_MINUTES = 45

# Meal break duration
MIN_MEAL_BREAK_MINUTES = 30
MAX_MEAL_BREAK_MINUTES = 45

# Meal break stagger around shift midpoint
MAX_MEAL_STAGGER_MINUTES = 30

# Shift times (24-hour clock)
DAY_SHIFT_START_HOUR = 6
DAY_SHIFT_END_HOUR = 18
NIGHT_SHIFT_START_HOUR = 18
NIGHT_SHIFT_END_HOUR = 6

OUTPUT_FILE = "truck_simulation_365_days.csv"

# Columns written to the output CSV (internal-only fields excluded)
OUTPUT_COLUMNS = [
    "Roster_Date",
    "Calendar_Date",
    "Shift_ID",
    "Truck_ID",
    "Trip_ID",
    "Arrival_Time",
    "Departure_Time",
    "Payload_t",
    "Dwell_Minutes",
]

# Meal break windows keyed by (roster_date, truck_id, shift_id) for validation
meal_break_lookup = {}


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def random_seconds_in_minute_range(min_minutes, max_minutes):
    """Random duration in seconds between min and max minutes (inclusive)."""
    return random.randint(
        min_minutes * 60,
        max_minutes * 60
    )


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_shift_bounds(roster_date_str, shift_id):
    """
    Return (shift_start, shift_end) for a roster day and shift.

    DAY:   roster_date 06:00 -> roster_date 18:00
    NIGHT: roster_date 18:00 -> next calendar day 06:00
    """
    roster_dt = parse_date(roster_date_str)

    if shift_id == "DAY":
        shift_start = roster_dt.replace(
            hour=DAY_SHIFT_START_HOUR,
            minute=0,
            second=0
        )
        shift_end = roster_dt.replace(
            hour=DAY_SHIFT_END_HOUR,
            minute=0,
            second=0
        )
    else:
        shift_start = roster_dt.replace(
            hour=NIGHT_SHIFT_START_HOUR,
            minute=0,
            second=0
        )
        next_day = roster_dt + timedelta(days=1)
        shift_end = next_day.replace(
            hour=NIGHT_SHIFT_END_HOUR,
            minute=0,
            second=0
        )

    return shift_start, shift_end


def get_meal_break_window(shift_start, shift_end, shift_id):
    """
    Schedule a staggered meal break mid-shift.
    Day shift centers around 12:00; night shift around 00:00.
    """
    if shift_id == "DAY":
        break_center = shift_start.replace(hour=12, minute=0, second=0)
    else:
        midnight = (shift_start + timedelta(days=1)).replace(
            hour=0, minute=0, second=0
        )
        break_center = midnight

    stagger_seconds = random.randint(0, MAX_MEAL_STAGGER_MINUTES * 60)
    break_start = break_center + timedelta(seconds=stagger_seconds)
    break_duration = random_seconds_in_minute_range(
        MIN_MEAL_BREAK_MINUTES,
        MAX_MEAL_BREAK_MINUTES
    )
    break_end = break_start + timedelta(seconds=break_duration)

    # Keep break inside shift window
    if break_start < shift_start:
        break_start = shift_start
    if break_end > shift_end:
        break_end = shift_end

    return break_start, break_end


def assign_shift_trip_targets():
    """
    Pick daily trip total (28-32) and split into day/night shift
    targets (each 12-16).
    """
    daily_target = random.randint(MIN_DAILY_TRIPS, MAX_DAILY_TRIPS)

    day_low = max(MIN_SHIFT_TRIPS, daily_target - MAX_SHIFT_TRIPS)
    day_high = min(MAX_SHIFT_TRIPS, daily_target - MIN_SHIFT_TRIPS)

    day_target = random.randint(day_low, day_high)
    night_target = daily_target - day_target

    return daily_target, day_target, night_target


def compute_first_arrival(shift_start):
    """
    First trip arrival = shift start + fleet stagger + shift change.
    All components include random seconds.
    """
    stagger = random_seconds_in_minute_range(
        MIN_STAGGER_MINUTES,
        MAX_STAGGER_MINUTES
    )
    shift_change = random_seconds_in_minute_range(
        MIN_SHIFT_CHANGE_MINUTES,
        MAX_SHIFT_CHANGE_MINUTES
    )
    return shift_start + timedelta(seconds=stagger + shift_change)


def skip_past_break(current_time, break_start, break_end):
    """If current_time falls inside meal break, jump to break end."""
    if break_start <= current_time < break_end:
        return break_end
    return current_time


# ============================================================
# 3. GENERATE TRUCK IDs
# ============================================================

truck_ids = [f"T{i}" for i in range(1, NUM_TRUCKS + 1)]
random.shuffle(truck_ids)


# ============================================================
# 4. GENERATE TRIPS FOR ONE SHIFT
# ============================================================

def generate_shift_trips(
    truck_id,
    roster_date,
    shift_id,
    shift_target,
    trip_number_start
):
    records = []
    shift_start, shift_end = get_shift_bounds(roster_date, shift_id)
    meal_start, meal_end = get_meal_break_window(
        shift_start, shift_end, shift_id
    )
    meal_break_lookup[(roster_date, truck_id, shift_id)] = (
        meal_start,
        meal_end,
    )

    current_arrival = compute_first_arrival(shift_start)
    current_arrival = skip_past_break(
        current_arrival, meal_start, meal_end
    )

    trip_number = trip_number_start
    trips_completed = 0

    while trips_completed < shift_target:

        if current_arrival >= shift_end:
            break

        current_arrival = skip_past_break(
            current_arrival, meal_start, meal_end
        )

        if current_arrival >= shift_end:
            break

        dwell_seconds = random_seconds_in_minute_range(
            MIN_DWELL_MINUTES,
            MAX_DWELL_MINUTES
        )
        departure = current_arrival + timedelta(seconds=dwell_seconds)

        if departure > shift_end:
            break

        payload = round(
            random.uniform(MIN_PAYLOAD, MAX_PAYLOAD),
            2
        )

        calendar_date = current_arrival.strftime("%Y-%m-%d")

        records.append({
            "Roster_Date": roster_date,
            "Calendar_Date": calendar_date,
            "Shift_ID": shift_id,
            "Truck_ID": truck_id,
            "Trip_ID": (
                f"{truck_id}_{shift_id}_TRIP_{trip_number:03d}"
            ),
            "Arrival_Time": current_arrival,
            "Departure_Time": departure,
            "Payload_t": payload,
        })

        trips_completed += 1
        trip_number += 1

        inter_trip_seconds = random_seconds_in_minute_range(
            MIN_INTER_TRIP_GAP,
            MAX_INTER_TRIP_GAP
        )
        current_arrival = departure + timedelta(
            seconds=inter_trip_seconds
        )

    return records, trip_number


# ============================================================
# 5. GENERATE TRIPS FOR ONE TRUCK FOR ONE ROSTER DAY
# ============================================================

def generate_trips_for_truck_day(truck_id, roster_date):
    """
    One roster day = DAY shift (06:00-18:00) + NIGHT shift (18:00-06:00).
    Trip numbers run continuously day -> night and reset next roster day.
    """
    daily_target, day_target, night_target = assign_shift_trip_targets()

    day_records, next_trip_number = generate_shift_trips(
        truck_id=truck_id,
        roster_date=roster_date,
        shift_id="DAY",
        shift_target=day_target,
        trip_number_start=1,
    )

    night_records, _ = generate_shift_trips(
        truck_id=truck_id,
        roster_date=roster_date,
        shift_id="NIGHT",
        shift_target=night_target,
        trip_number_start=next_trip_number,
    )

    return day_records + night_records


# ============================================================
# 6. GENERATE DATA FOR 365 ROSTER DAYS
#
# Simulation begins on 2025-01-01 at 06:00 (DAY shift),
# not at midnight (which would fall mid-night-shift).
# ============================================================

all_records = []
start_date = parse_date(START_DATE)

for day_number in range(SIMULATION_DAYS):
    roster_date = (
        start_date + timedelta(days=day_number)
    ).strftime("%Y-%m-%d")

    print(
        f"Generating roster day {day_number + 1}/{SIMULATION_DAYS}: "
        f"{roster_date}"
    )

    for truck_id in truck_ids:
        truck_records = generate_trips_for_truck_day(
            truck_id=truck_id,
            roster_date=roster_date,
        )
        all_records.extend(truck_records)


# ============================================================
# 7. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(all_records)

df = df.sort_values(
    by=["Roster_Date", "Arrival_Time", "Truck_ID"]
).reset_index(drop=True)

df["Dwell_Minutes"] = (
    df["Departure_Time"] - df["Arrival_Time"]
).dt.total_seconds() / 60


# ============================================================
# 8. INTER-TRIP GAP (per truck, per roster day, per shift)
# ============================================================

validation_df = df.sort_values(
    by=["Roster_Date", "Truck_ID", "Shift_ID", "Arrival_Time"]
).copy()

validation_df["Previous_Departure"] = (
    validation_df
    .groupby(["Roster_Date", "Truck_ID", "Shift_ID"])["Departure_Time"]
    .shift(1)
)

validation_df["Meal_Break_Start"] = validation_df.apply(
    lambda row: meal_break_lookup[
        (row["Roster_Date"], row["Truck_ID"], row["Shift_ID"])
    ][0],
    axis=1,
)
validation_df["Meal_Break_End"] = validation_df.apply(
    lambda row: meal_break_lookup[
        (row["Roster_Date"], row["Truck_ID"], row["Shift_ID"])
    ][1],
    axis=1,
)

validation_df["Inter_Trip_Gap_Minutes"] = (
    validation_df["Arrival_Time"] - validation_df["Previous_Departure"]
).dt.total_seconds() / 60

# Gaps that span a meal break are not haul-cycle gaps
validation_df["Gap_Crosses_Meal_Break"] = (
    validation_df["Previous_Departure"].notna()
    & validation_df["Meal_Break_Start"].notna()
    & (validation_df["Previous_Departure"] < validation_df["Meal_Break_End"])
    & (validation_df["Arrival_Time"] > validation_df["Meal_Break_Start"])
)

haul_cycle_gaps = validation_df[
    validation_df["Previous_Departure"].notna()
    & ~validation_df["Gap_Crosses_Meal_Break"]
]["Inter_Trip_Gap_Minutes"]


# ============================================================
# 9. SUMMARY METRICS
# ============================================================

number_of_trucks = df["Truck_ID"].nunique()
total_trips = len(df)

trips_per_truck_day = df.groupby(["Roster_Date", "Truck_ID"]).size()
trips_per_truck_shift = df.groupby(
    ["Roster_Date", "Truck_ID", "Shift_ID"]
).size()
daily_trips = df.groupby("Roster_Date").size()

min_payload = df["Payload_t"].min()
max_payload = df["Payload_t"].max()
average_payload = df["Payload_t"].mean()
payload_valid = df["Payload_t"].between(MIN_PAYLOAD, MAX_PAYLOAD).all()

min_dwell = df["Dwell_Minutes"].min()
max_dwell = df["Dwell_Minutes"].max()
average_dwell = df["Dwell_Minutes"].mean()
dwell_valid = df["Dwell_Minutes"].between(
    MIN_DWELL_MINUTES, MAX_DWELL_MINUTES
).all()

gap_values = haul_cycle_gaps
min_gap = gap_values.min()
max_gap = gap_values.max()
average_gap = gap_values.mean()
gap_valid = gap_values.between(
    MIN_INTER_TRIP_GAP, MAX_INTER_TRIP_GAP
).all()

daily_trip_rule_valid = trips_per_truck_day.between(
    MIN_DAILY_TRIPS, MAX_DAILY_TRIPS
).all()

shift_trip_rule_valid = trips_per_truck_shift.between(
    MIN_SHIFT_TRIPS, MAX_SHIFT_TRIPS
).all()


# ============================================================
# 10. TIME BOUNDARY VALIDATION (within shift windows)
# ============================================================

time_valid = True

for _, row in df.iterrows():
    shift_start, shift_end = get_shift_bounds(
        row["Roster_Date"], row["Shift_ID"]
    )
    if not (
        row["Arrival_Time"] >= shift_start
        and row["Departure_Time"] <= shift_end
    ):
        time_valid = False
        break


# ============================================================
# 11. TRIP NUMBERING VALIDATION
#
# Continuous DAY -> NIGHT within roster day; reset each roster day.
# ============================================================

trip_numbering_valid = True

for (roster_date, truck_id), group in df.groupby(
    ["Roster_Date", "Truck_ID"]
):
    trip_numbers = (
        group["Trip_ID"]
        .str.extract(r"_TRIP_(\d+)$")[0]
        .astype(int)
        .tolist()
    )
    trip_numbers = sorted(trip_numbers)
    expected = list(range(1, len(trip_numbers) + 1))
    if trip_numbers != expected:
        trip_numbering_valid = False
        break

    day_trips = (
        group[group["Shift_ID"] == "DAY"]["Trip_ID"]
        .str.extract(r"_TRIP_(\d+)$")[0]
        .astype(int)
    )
    night_trips = (
        group[group["Shift_ID"] == "NIGHT"]["Trip_ID"]
        .str.extract(r"_TRIP_(\d+)$")[0]
        .astype(int)
    )

    if len(day_trips) > 0 and len(night_trips) > 0:
        if night_trips.min() != day_trips.max() + 1:
            trip_numbering_valid = False
            break


# ============================================================
# 12. ROSTER DATE FOR NIGHT-SHIFT AFTER-MIDNIGHT TRIPS
# ============================================================

night_after_midnight = df[
    (df["Shift_ID"] == "NIGHT")
    & (df["Calendar_Date"] > df["Roster_Date"])
]

roster_date_valid = (
    night_after_midnight["Roster_Date"] < night_after_midnight["Calendar_Date"]
).all() if len(night_after_midnight) > 0 else True


# ============================================================
# 13. TONNAGE
# ============================================================

total_tonnage = df["Payload_t"].sum()
average_tonnage_per_truck_day = (
    df.groupby(["Roster_Date", "Truck_ID"])["Payload_t"].sum().mean()
)
daily_tonnage = df.groupby("Roster_Date")["Payload_t"].sum()


# ============================================================
# 14. FINAL VALIDATION
# ============================================================

all_valid = (
    number_of_trucks == NUM_TRUCKS
    and payload_valid
    and dwell_valid
    and gap_valid
    and daily_trip_rule_valid
    and shift_trip_rule_valid
    and time_valid
    and trip_numbering_valid
    and roster_date_valid
)


# ============================================================
# 15. TERMINAL SUMMARY
# ============================================================

end_roster_date = (
    start_date + timedelta(days=SIMULATION_DAYS - 1)
).strftime("%Y-%m-%d")

print("\n")
print("=" * 75)
print("365-DAY SHIFT-BASED TRUCK SIMULATION VALIDATION")
print("=" * 75)

print(f"\nSimulation period      : {START_DATE} to {end_roster_date}")
print(f"  (Night shift on last roster day extends to 06:00 next morning)")
print(f"Simulation starts at   : {START_DATE} 06:00 (DAY shift)")
print(f"Total trucks           : {number_of_trucks}")
print(f"Expected trucks        : {NUM_TRUCKS}")
print(f"\nTotal trips generated  : {total_trips:,}")

print("\nTrips per roster day:")
print("-" * 45)
for date, trips in daily_trips.items():
    print(f"  {date} : {trips:,} trips")

print("\nTrips per truck per roster day:")
print("-" * 45)
print(f"  Minimum              : {trips_per_truck_day.min()}")
print(f"  Maximum              : {trips_per_truck_day.max()}")
print(f"  Average              : {trips_per_truck_day.mean():.2f}")
print(f"  Target range valid   : {daily_trip_rule_valid}")

print("\nTrips per truck per shift:")
print("-" * 45)
print(f"  Minimum              : {trips_per_truck_shift.min()}")
print(f"  Maximum              : {trips_per_truck_shift.max()}")
print(f"  Average              : {trips_per_truck_shift.mean():.2f}")
print(f"  Target range valid   : {shift_trip_rule_valid}")

print("\nPayload:")
print("-" * 45)
print(f"  Minimum              : {min_payload:.2f} tonnes")
print(f"  Maximum              : {max_payload:.2f} tonnes")
print(f"  Average              : {average_payload:.2f} tonnes")
print(f"  Range valid          : {payload_valid}")

print("\nArrival -> Departure:")
print("-" * 45)
print(f"  Minimum              : {min_dwell:.2f} minutes")
print(f"  Maximum              : {max_dwell:.2f} minutes")
print(f"  Average              : {average_dwell:.2f} minutes")
print(f"  Range valid          : {dwell_valid}")

print("\nDeparture -> Next Arrival (haul cycle, excl. meal breaks):")
print("-" * 45)
print(f"  Minimum gap          : {min_gap:.2f} minutes")
print(f"  Maximum gap          : {max_gap:.2f} minutes")
print(f"  Average gap          : {average_gap:.2f} minutes")
print(f"  Range valid          : {gap_valid}")

print("\nTrip numbering (DAY -> NIGHT continuous, daily reset):")
print("-" * 45)
print(f"  Numbering valid      : {trip_numbering_valid}")

print("\nRoster date for night-shift after-midnight trips:")
print("-" * 45)
print(f"  After-midnight trips : {len(night_after_midnight):,}")
print(f"  Roster date valid    : {roster_date_valid}")

print("\nShift time boundaries:")
print("-" * 45)
print(f"  Boundaries valid     : {time_valid}")

earliest = df["Arrival_Time"].min()
latest = df["Departure_Time"].max()
print(f"  Earliest arrival     : {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Latest departure     : {latest.strftime('%Y-%m-%d %H:%M:%S')}")

print("\nTonnage:")
print("-" * 45)
print(f"  Total 7-day tonnage  : {total_tonnage:,.2f} tonnes")
print(f"  Avg tonnes/truck/day : {average_tonnage_per_truck_day:,.2f} tonnes")

print("\nDaily tonnage:")
print("-" * 45)
for date, tonnes in daily_tonnage.items():
    print(f"  {date} : {tonnes:,.2f} tonnes")

print("\n")
print("=" * 75)
if all_valid:
    print("FINAL RESULT: SIMULATION PASSED ALL VALIDATIONS")
else:
    print("FINAL RESULT: SIMULATION FAILED VALIDATION")
print("=" * 75)


# ============================================================
# 16. SAVE CSV
# ============================================================

df[OUTPUT_COLUMNS].to_csv(OUTPUT_FILE, index=False)

print(f"\nDataset saved successfully as: {OUTPUT_FILE}")
print(f"Total rows saved     : {len(df):,}")
print("=" * 75)
