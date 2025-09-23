import Adafruit_DHT
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os
import shutil
import matplotlib.dates as mdates
import numpy as np

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# File paths
DATA_FILE = "DHT11.txt"
DATA_BACKUP_FILE = "DHT11_backup.txt"
CHART_FILE = "chart.svg"
CHART_BACKUP_FILE = "chart_backup.svg"

# Chart settings
# Only plot the last 120 data points (20 minutes at 10 second intervals)
MAX_CHART_POINTS = 120
# Number of points for the moving average calculation
MOVING_AVG_POINTS = 5

def main():
    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return # Exit if file cannot be created
    
    main_loop()

def main_loop():
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
                    
                    print(f"Logged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%")
                    
                    generate_chart()
                else:
                    print(f"Invalid humidity reading: {humidity}%. Data not logged.")
            else:
                print("Failed to retrieve data from DHT11 sensor.")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nExiting program.")

def generate_chart():
    # Read all data from the file
    dates, temps, hums = [], [], []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            next(f)
            for line in f:
                try:
                    timestamp_str, temp_str, hum_str = line.strip().split(',')
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    temps.append(float(temp_str))
                    hums.append(float(hum_str))
                except (ValueError, IndexError):
                    continue

    if not dates:
        return
    
    # Trim the data to only include the last N points for the chart
    if len(dates) > MAX_CHART_POINTS:
        dates = dates[-MAX_CHART_POINTS:]
        temps = temps[-MAX_CHART_POINTS:]
        hums = hums[-MAX_CHART_POINTS:]
    
    # Create the Matplotlib figure
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Set a more descriptive title
    start_time = dates[0].strftime("%H:%M")
    end_time = dates[-1].strftime("%H:%M")
    ax1.set_title(f"DHT11 Readings: {start_time} to {end_time}")
    
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

    # === BEGIN ENHANCEMENTS FOR DATA ANALYTICS ===
    
    # Add a moving average line for temperature
    temp_ma = np.convolve(temps, np.ones(MOVING_AVG_POINTS)/MOVING_AVG_POINTS, mode='valid')
    ax1.plot(dates[len(dates)-len(temp_ma):], temp_ma, color='darkred', linestyle='--', label=f'{MOVING_AVG_POINTS}-Point Avg Temp')
    
    # Add a moving average line for humidity
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

    # === END ENHANCEMENTS ===

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

