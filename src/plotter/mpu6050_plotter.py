# =========================================================================
# Kabot-1 Post-Flight MPU-6050 Data Analysis and Chart Generation (WebUI)
# =========================================================================
# Robust version:
# - Handles missing SciPy by skipping smoothing.
# - Normalizes header names (ax/ay/az/gx/gy/gz) to internal keys.
# - Aligns output filename with WebUI: src/charts/mpu_chart.svg
# =========================================================================

import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Try to import SciPy smoothing; if unavailable, continue without it
try:
    from scipy.signal import savgol_filter
    HAS_SAVGOL = True
except Exception:
    HAS_SAVGOL = False

# Paths (relative to project root)
DATA_DIR = "src/logger/data"
DATA_FILE = os.path.join(DATA_DIR, "MPU6050.txt")
CHARTS_DIR = "src/charts"
CHART_FILE = os.path.join(CHARTS_DIR, "mpu_chart.svg")  # aligns with WebUI
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "mpu_chart_backup.svg")

# Smoothing settings (used only if HAS_SAVGOL and enough points)
WINDOW_LENGTH = 51  # must be odd and <= len(series)
POLY_ORDER = 3

# Map possible header names to internal keys
HEADER_MAP = {
    "accel_x": "accel_x", "accel_y": "accel_y", "accel_z": "accel_z",
    "gyro_x": "gyro_x",   "gyro_y": "gyro_y",   "gyro_z": "gyro_z",
    "ax": "accel_x", "ay": "accel_y", "az": "accel_z",
    "gx": "gyro_x",  "gy": "gyro_y",  "gz": "gyro_z",
}

def generate_mpu_chart():
    # Basic checks
    if not os.path.exists(DATA_FILE):
        print(f"Error: Mission data file not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    # Read file
    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if not lines:
        print("Error: Log file is empty.", file=sys.stderr)
        sys.exit(2)

    # Parse header
    header = [h.strip() for h in lines[0].strip().split(",")]
    if len(header) < 7 or header[0].lower() != "timestamp":
        print("Error: Unexpected header format. First column must be 'timestamp'.", file=sys.stderr)
        print(f"Header read: {header}", file=sys.stderr)
        sys.exit(2)

    # Build key list using normalized names
    raw_keys = header[1:]
    internal_keys = []
    for k in raw_keys:
        ik = HEADER_MAP.get(k.strip())
        if ik:
            internal_keys.append((k.strip(), ik))
        else:
            # Unknown column; skip it gracefully
            internal_keys.append((k.strip(), None))

    # Prepare containers
    dates = []
    data = {
        "accel_x": [], "accel_y": [], "accel_z": [],
        "gyro_x":  [], "gyro_y":  [], "gyro_z":  []
    }

    # Parse rows
    for line in lines[1:]:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < 7:
            continue
        try:
            dates.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
        except Exception:
            continue

        for i, (raw_k, internal_k) in enumerate(internal_keys):
            if internal_k is None:
                continue
            try:
                val = float(parts[i+1])
            except Exception:
                val = np.nan
            data[internal_k].append(val)

    if not dates or all(len(v) == 0 for v in data.values()):
        print("Error: No data to plot.", file=sys.stderr)
        sys.exit(2)

    # Ensure charts dir
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # Duration
    start_time = dates[0]
    end_time = dates[-1]
    duration = end_time - start_time
    total_hours = int(duration.total_seconds() // 3600)
    total_minutes = int((duration.total_seconds() % 3600) // 60)
    total_seconds = int(duration.total_seconds() % 60)
    duration_str = f"{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s"

    # Plot style
    plt.style.use("ggplot")
    plt.rcParams.update({"font.size": 10, "axes.labelsize": 12, "axes.titlesize": 14})

    fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(
        f"Kabot I Mission MPU-6050 Motion Analysis | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        fontsize=16
    )

    date_formatter = mdates.DateFormatter("%H:%M")
    colors = {"x": "tab:red", "y": "tab:green", "z": "tab:blue"}

    # Helper for smoothing
    def maybe_smooth(series):
        if not HAS_SAVGOL:
            return None
        n = len(series)
        if n < WINDOW_LENGTH or WINDOW_LENGTH % 2 == 0:
            return None
        try:
            return savgol_filter(series, WINDOW_LENGTH, POLY_ORDER)
        except Exception:
            return None

    # Accel
    ax_accel.set_title("Acceleration Data (Linear G-Forces)", fontsize=14)
    ax_accel.set_ylabel("Acceleration (g)")
    for axis in ["x", "y", "z"]:
        raw = np.array(data[f"accel_{axis}"], dtype=float)
        ax_accel.plot(dates, raw, label=f"Accel {axis} (Raw)", color=colors[axis], linewidth=1.0, alpha=0.3)
        smooth = maybe_smooth(raw)
        if smooth is not None:
            ax_accel.plot(dates, smooth, label=f"Accel {axis} (Smoothed)", color=colors[axis], linewidth=2.0)

    ax_accel.grid(True, linestyle="--", alpha=0.6)
    ax_accel.legend(loc="upper right", ncol=3)

    # Gyro
    ax_gyro.set_title("Gyroscope Data (Rotational Velocity)", fontsize=14)
    ax_gyro.set_xlabel("Time (HH:MM)")
    ax_gyro.set_ylabel("Angular Velocity (deg/s)")
    for axis in ["x", "y", "z"]:
        raw = np.array(data[f"gyro_{axis}"], dtype=float)
        ax_gyro.plot(dates, raw, label=f"Gyro {axis} (Raw)", color=colors[axis], linewidth=1.0, alpha=0.3)
        smooth = maybe_smooth(raw)
        if smooth is not None:
            ax_gyro.plot(dates, smooth, label=f"Gyro {axis} (Smoothed)", color=colors[axis], linewidth=2.0)

    ax_gyro.xaxis.set_major_formatter(date_formatter)
    ax_gyro.grid(True, linestyle="--", alpha=0.6)
    ax_gyro.legend(loc="upper right", ncol=3)

    fig.autofmt_xdate(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Backup + save
    try:
        if os.path.exists(CHART_FILE):
            os.replace(CHART_FILE, CHART_BACKUP_FILE)
        plt.savefig(CHART_FILE)
        plt.close(fig)
        print(f"\nSuccessfully generated MPU-6050 mission chart: '{CHART_FILE}'")
        print(f"Chart covers {len(dates)} points over {duration_str}.")
    except Exception as e:
        print(f"Error saving chart: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    generate_mpu_chart()
