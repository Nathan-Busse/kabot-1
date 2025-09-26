# =========================================================================
# Kabot-1 Post-Flight Data Analysis and Chart Generation
# =========================================================================
# This script is run *after* the payload has been retrieved and the log
# file (data/DHT11.txt) has been transferred to a powerful machine.
# It uses the full dataset to generate the final, high-fidelity mission
# chart using resource-intensive libraries like Matplotlib and SciPy.
# =========================================================================

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from scipy.signal import savgol_filter
import os

# Configuration settings (Must match dht_logger.py's directory structure)
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
CHARTS_DIR = "charts"
CHART_FILE = os.path.join(CHARTS_DIR, "chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "chart_backup.svg")

def generate_chart():
    """Reads all data from the log file and generates the final mission chart."""
    dates, temps, hums = [], [], []

    # === Step 1: Read all data from the mission log file ===
    if not os.path.exists(DATA_FILE):
        print(f"Error: Mission data file not found at {DATA_FILE}")
        print("Please ensure the data file has been transferred from the Kabot-1 payload.")
        return

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            # Skip the header line
            if lines and "timestamp" in lines[0]:
                lines = lines[1:]
            
            for line in lines:
                try:
                    timestamp_str, temp_str, hum_str = line.strip().split(',')
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    temps.append(float(temp_str))
                    hums.append(float(hum_str))
                except (ValueError, IndexError):
                    continue
    except Exception as e:
        print(f"Error reading data file for chart generation: {e}")
        return

    if not dates:
        print("No data to plot.")
        return
    
    # Ensure charts directory exists on the PC
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # === Step 2: Configure Plot Style and Title ===
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16})
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Calculate flight duration for the title
    SCRIPT_START_TIME = dates[0]
    end_time = dates[-1]
    duration = end_time - SCRIPT_START_TIME
    total_hours = duration.total_seconds() // 3600
    total_minutes = (duration.total_seconds() % 3600) // 60
    total_seconds = duration.total_seconds() % 60
    duration_str = f"{int(total_hours):02d}h {int(total_minutes):02d}m {int(total_seconds):02d}s"
    
    title_str = (
        f"Kabot I Mission Readings | Duration: {duration_str}\n"
        f"Start: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    ax1.set_title(title_str)
    
    # === Step 3: Plot Temperature Data ===
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color='tab:red')
    ax1.plot(dates, temps, color='tab:red', linewidth=1.2, alpha=0.8, label='Temperature (Raw)')
    
    # Apply Savitzky-Golay Filter for smoothing (requires at least 11 points)
    if len(temps) >= 11:
        # Window size 11, Polynomial order 3 - suitable for smoothing without losing signal features
        temp_smooth = savgol_filter(temps, 11, 3) 
        ax1.plot(dates, temp_smooth, color='darkred', linestyle='--', linewidth=2, label='Smoothed Temp (S-G Filter)')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    
    # Time axis formatting
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax1.xaxis.set_minor_locator(mdates.MinuteLocator(interval=2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=45)
    
    # === Step 4: Plot Humidity Data (Twin Axis) ===
    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue')
    ax2.plot(dates, hums, color='tab:blue', linewidth=1.2, alpha=0.8, label='Humidity (Raw)')
    
    if len(hums) >= 11:
        hum_smooth = savgol_filter(hums, 11, 3)
        ax2.plot(dates, hum_smooth, color='darkblue', linestyle='--', linewidth=2, label='Smoothed Hum (S-G Filter)')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(0, 100)
    
    # Grid and Legend
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.6)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    
    # === Step 5: Save Chart with Backup ===
    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)
        
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"\nSuccessfully generated final mission chart: '{CHART_FILE}'")
    print(f"Chart covers {len(dates)} data points over a duration of {duration_str}.")


if __name__ == "__main__":
    generate_chart()
