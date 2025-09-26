# =========================================================================
# The Kabot-1 Mission: High-Altitude Environmental Data Logger
# (Flight-Ready Version - Optimized for Low RAM/CPU)
# =========================================================================
# This script is a core component of the Kabot I mission, designed to
# validate the payload's ability to accurately log environmental data.
#
# Primary Objective: Continuously and reliably log temperature and humidity
# data to file while conserving the Raspberry Pi's RAM for essential flight
# operations. All data visualization is deferred to a separate, post-flight
# analysis script run on a more powerful machine.
# =========================================================================

import Adafruit_DHT
import time
from datetime import datetime
import os
import shutil

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# Directory for data files
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "DHT11_backup.txt")

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

def main():
    """Main function to run the sensor logging loop."""
    print(f"Ensuring data directory '{DATA_DIR}' exists...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return
    
    print("Kabot-1 Data Logger is active. Press Ctrl+C to stop logging.")
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        # === Core mission loop for continuous data collection ===
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
                    
                    # Updates on one line using \r for low resource terminal output
                    print(f"\rLogged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%", end="", flush=True)
                    
                else:
                    print(f"\rInvalid humidity reading: {humidity}%. Data not logged.", end="", flush=True)
            else:
                print("\rFailed to retrieve data from DHT11 sensor.", end="", flush=True)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nLogging terminated.")
        end_time = datetime.now()
        duration = end_time - SCRIPT_START_TIME
        print(f"Script started at: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime: {duration}")
        print("Data is saved in the 'data' directory. Run 'generate_kabot_chart.py' for analysis.")


if __name__ == "__main__":
    main()
