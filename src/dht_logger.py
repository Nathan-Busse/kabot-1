import Adafruit_DHT
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os
import shutil
import matplotlib.dates as mdates
import numpy as np
from collections import deque

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# File paths
DATA_FILE = "DHT11.txt"
DATA_BACKUP_FILE = "DHT11_backup.txt"

# Directory for charts
CHARTS_DIR = "charts"
CHART_FILE = os.path.join(CHARTS_DIR, "chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "chart_backup.svg")

# Chart settings
# Only plot the last 120 data points (20 minutes at 10 second intervals)
MAX_CHART_POINTS = 120
# Number of points for the moving average calculation
MOVING_AVG_POINTS = 5

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

def main():
    """Main function to run the sensor logging loop."""
    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return # Exit if file cannot be created
    
    # === Create the charts directory if it doesn't exist ===
    print(f"Ensuring directory '{CHARTS_DIR}' exists...")
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            
            if humidity is not None and temperature is not None:
                # Validate the humidity reading to ensure it's within the sensor's range (20-90%)
                if 20 <= humidity <= 90:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # --- Step 1: Backup the existing data file ---
                    if os.path.exists(DATA_FILE):
                        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
                    
                    # --- Step 2: Append new data to the main file ---
                    with open(DATA_FILE, "a") as f:
                        f.write(f"{timestamp},{temperature},{humidity}\n")
                    
                    # === UPDATED PRINT STATEMENT ===
                    # Use \r to return to the start of the line and overwrite the previous output
                    print(f"\rLogged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%", end="", flush=True)
                    
                    generate_chart()
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


def generate_chart():
    """
    Generates an updated chart from the most recent data.
    This function is optimized to read only the last N lines,
    preventing high memory usage on the Raspberry Pi.
    """
    # Read only the last N lines from the file using deque for memory efficiency
    dates, temps, hums = [], [], []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                # Use deque to get the last N lines without loading the entire file
                last_lines = deque(f, MAX_CHART_POINTS + 1)
                # Skip the header line if it's present in the last lines
                if last_lines and "timestamp" in last_lines[0]:
                    last_lines.popleft()
                
                for line in last_lines:
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
        return
    
    # Create the Matplotlib figure
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # === UPDATED TITLE TO INCLUDE FLIGHT DURATION ===
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
    
    # Add a grid for better readability and precision
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color=color)
    # Add markers to the plot points
    ax1.plot(dates, temps, color=color, label='Temperature', marker='o', markersize=4)
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Format the x-axis to show time and rotate labels
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate(rotation=45)
    
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Humidity (%)', color=color)
    # Add markers to the plot points
    ax2.plot(dates, hums, color=color, label='Humidity', marker='o', markersize=4)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Explicitly set the y-axis limits for humidity to a sensible range
    ax2.set_ylim(0, 100)
    
    # Add a moving average line for temperature
    if len(temps) >= MOVING_AVG_POINTS:
        temp_ma = np.convolve(temps, np.ones(MOVING_AVG_POINTS)/MOVING_AVG_POINTS, mode='valid')
        ax1.plot(dates[len(dates)-len(temp_ma):], temp_ma, color='darkred', linestyle='--', label=f'{MOVING_AVG_POINTS}-Point Avg Temp')
    
    # Add a moving average line for humidity
    if len(hums) >= MOVING_AVG_POINTS:
        hum_ma = np.convolve(hums, np.ones(MOVING_AVG_POINTS)/MOVING_AVG_POINTS, mode='valid')
        ax2.plot(dates[len(dates)-len(hum_ma):], hum_ma, color='darkblue', linestyle='--', label=f'{MOVING_AVG_POINTS}-Point Avg Hum')
    
    # Find and highlight the max and min points
    if temps:
        max_temp_idx = np.argmax(temps)
        min_temp_idx = np.argmin(temps)
        ax1.plot(dates[max_temp_idx], temps[max_temp_idx], marker='o', color='darkred', markersize=8, label='Max Temp')
        ax1.plot(dates[min_temp_idx], temps[min_temp_idx], marker='o', color='darkred', markersize=8, label='Min Temp')
        ax1.annotate(f'{temps[max_temp_idx]:.1f}°C', xy=(dates[max_temp_idx], temps[max_temp_idx]), xytext=(5,-10), textcoords='offset points', ha='center')
        ax1.annotate(f'{temps[min_temp_idx]:.1f}°C', xy=(dates[min_temp_idx], temps[min_temp_idx]), xytext=(5,10), textcoords='offset points', ha='center')
    
    if hums:
        max_hum_idx = np.argmax(hums)
        min_hum_idx = np.argmin(hums)
        ax2.plot(dates[max_hum_idx], hums[max_hum_idx], marker='o', color='darkblue', markersize=8, label='Max Hum')
        ax2.plot(dates[min_hum_idx], hums[min_hum_idx], marker='o', color='darkblue', markersize=8, label='Min Hum')
        ax2.annotate(f'{hums[max_hum_idx]:.1f}%', xy=(dates[max_hum_idx], hums[max_hum_idx]), xytext=(5,-10), textcoords='offset points', ha='center')
        ax2.annotate(f'{hums[min_hum_idx]:.1f}%', xy=(dates[min_hum_idx], hums[min_hum_idx]), xytext=(5,10), textcoords='offset points', ha='center')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    # --- Step 3: Backup the existing chart before creating the new one ---
    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)
        
    plt.savefig(CHART_FILE)
    plt.close(fig)

if __name__ == "__main__":
    main()
