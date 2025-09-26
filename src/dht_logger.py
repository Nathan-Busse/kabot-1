# =========================================================================
# The Kabot-1 Mission: High-Altitude Environmental Data Logger
# =========================================================================
# This script is a core component of the Kabot I mission, designed to
# validate the payload's ability to accurately log environmental data and
# manage thermal regulation. The primary objectives are to collect
# temperature and humidity data in near-space conditions and to prove the
# data collection system's reliability.
#
# Data is logged continuously to a file to be recovered and analyzed after
# the flight. The final mission chart, which visualizes the entire flight
# duration, is only generated upon mission completion (Ctrl+C) to conserve
# the Raspberry Pi's RAM during the flight.
# =========================================================================

import Adafruit_DHT
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os
import shutil
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import savgol_filter

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# Directory for data files
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "DHT11_backup.txt")

# Directory for charts
CHARTS_DIR = "charts"
CHART_FILE = os.path.join(CHARTS_DIR, "chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "chart_backup.svg")

# Number of points for the moving average calculation
MOVING_AVG_POINTS = 5

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

def main():
    """Main function to run the sensor logging loop."""
    print(f"Ensuring directory '{DATA_DIR}' exists...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return
    
    print(f"Ensuring directory '{CHARTS_DIR}' exists...")
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            
            if humidity is not None and temperature is not None:
                if 20 <= humidity <= 90:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if os.path.exists(DATA_FILE):
                        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
                    
                    with open(DATA_FILE, "a") as f:
                        f.write(f"{timestamp},{temperature},{humidity}\n")
                    
                    print(f"\rLogged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%", end="", flush=True)
                else:
                    print(f"\rInvalid humidity reading: {humidity}%. Data not logged.", end="", flush=True)
            else:
                print("\rFailed to retrieve data from DHT11 sensor.", end="", flush=True)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nExiting program.")
        end_time = datetime.now()
        duration = end_time - SCRIPT_START_TIME
        print(f"Script started at: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime: {duration}")
        print("Generating final chart from all logged data...")
        generate_chart()

def generate_chart():
    """Generates an updated chart from all logged data."""
    dates, temps, hums = [], [], []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                lines = f.readlines()
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
    
    # Style and figure setup
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16})
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    end_time = dates[-1] if dates else datetime.now()
    duration = end_time - SCRIPT_START_TIME
    total_hours = duration.seconds // 3600
    total_minutes = (duration.seconds % 3600) // 60
    total_seconds = duration.seconds % 60
    duration_str = f"{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s"
    
    title_str = (
        f"DHT11 Readings: "
        f"Start: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Duration: {duration_str}"
    )
    ax1.set_title(title_str)
    
    # Temperature
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color='tab:red')
    ax1.plot(dates, temps, color='tab:red', linewidth=1.2, alpha=0.8, label='Temperature')
    if len(temps) >= 11:
        temp_smooth = savgol_filter(temps, 11, 3)
        ax1.plot(dates, temp_smooth, color='darkred', linestyle='--', linewidth=2, label='Smoothed Temp')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    
    # Time axis formatting
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax1.xaxis.set_minor_locator(mdates.MinuteLocator(interval=2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=45)
    
    # Humidity
    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue')
    ax2.plot(dates, hums, color='tab:blue', linewidth=1.2, alpha=0.8, label='Humidity')
    if len(hums) >= 11:
        hum_smooth = savgol_filter(hums, 11, 3)
        ax2.plot(dates, hum_smooth, color='darkblue', linestyle='--', linewidth=2, label='Smoothed Hum')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(0, 100)
    
    # Grid
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.6)
    
    # Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    
    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)
        
    plt.savefig(CHART_FILE)
    plt.close(fig)

if __name__ == "__main__":
    main()
