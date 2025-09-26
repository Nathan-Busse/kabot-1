# =========================================================================
# The Kabot-1 Mission: High-Altitude Environmental Data Logger
# =========================================================================
# This script is the flight logger for the Kabot-1 mission.
# It continuously records temperature and humidity data from the DHT11
# sensor and writes it to a timestamped log file for later analysis.
#
# Plotting is handled separately (see plot_data.py + plot_ui.sh).
# =========================================================================

import Adafruit_DHT
import time
from datetime import datetime
import os
import shutil

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4   # GPIO4 (GPCLK0) for improved accuracy

# Directory for data files
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "DHT11_backup.txt")

# Store the start time of the script
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

    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

            if humidity is not None and temperature is not None:
                if 20 <= humidity <= 90:  # sanity check
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Backup before writing
                    if os.path.exists(DATA_FILE):
                        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

                    # Append new reading
                    with open(DATA_FILE, "a") as f:
                        f.write(f"{timestamp},{temperature},{humidity}\n")

                    print(f"\rLogged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%", 
                          end="", flush=True)
                else:
                    print(f"\rInvalid humidity reading: {humidity}%. Data not logged.", 
                          end="", flush=True)
            else:
                print("\rFailed to retrieve data from DHT11 sensor.", end="", flush=True)

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nExiting logger.")
        end_time = datetime.now()
        duration = end_time - SCRIPT_START_TIME
        print(f"Script started at: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script ended at:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime:     {duration}")

if __name__ == "__main__":
    main()
