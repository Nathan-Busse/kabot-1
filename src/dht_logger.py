import Adafruit_DHT
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os
import shutil

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# File paths
DATA_FILE = "DHT11.txt"
DATA_BACKUP_FILE = "DHT11_backup.txt"
CHART_FILE = "chart.svg"
CHART_BACKUP_FILE = "chart_backup.svg"

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
    
    # Create the Matplotlib figure
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color=color)
    ax1.plot(dates, temps, color=color, label='Temperature')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_title('DHT11 Temperature & Humidity Readings')
    
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Humidity (%)', color=color)
    ax2.plot(dates, hums, color=color, label='Humidity')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.gcf().autofmt_xdate()
    
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

