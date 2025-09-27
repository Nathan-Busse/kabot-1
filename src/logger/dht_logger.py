# =========================================================================
# The Kabot-1 Mission: High-Altitude Environmental Data Logger
# (Flight-Ready Version - Optimized for Low RAM/CPU)
# =========================================================================

import Adafruit_DHT
import time
from datetime import datetime
import os
# import shutil # Removed to prevent inefficient file copying in the main loop

# --- Configuration Settings ---
# Set to True for the actual mission flight to silence all terminal output 
# and prevent SSH session artifacts from corrupting the log file.
FLIGHT_MODE = True 

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
# The pin is set to GPIO4 (GPCLK0) for improved accuracy
DHT_PIN = 4 

# Directory for data files (Relative to src/logger/)
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "DHT11_backup.txt") # Retained for initial file integrity check

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

def main():
    """Main function to run the sensor logging loop."""
    # os.makedirs is non-blocking and memory-safe, we keep it outside the FLIGHT_MODE check
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_FILE):
        if not FLIGHT_MODE:
            print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            # Open file in 'w' (write) mode to create it and write the header once
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            # If we fail to create the file, we can't log, so exit gracefully.
            if not FLIGHT_MODE:
                print(f"CRITICAL ERROR: Failed to create log file: {e}")
            return
    
    if not FLIGHT_MODE:
        print(f"Kabot-1 Data Logger is active. Logging to {DATA_FILE}. Press Ctrl+C to stop.")
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        # === Core mission loop for continuous data collection ===
        while True:
            # Use read_retry for robust sensor reading
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            
            if humidity is not None and temperature is not None:
                # Validate the humidity reading to ensure it's within the sensor's range (20-90%)
                if 20 <= humidity <= 90:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # --- File Append Operation (Memory-Safe) ---
                    data_line = f"{timestamp},{temperature},{humidity}\n"
                    with open(DATA_FILE, "a") as f:
                        f.write(data_line)
                    
                    # --- Terminal Feedback (Only if NOT in Flight Mode) ---
                    if not FLIGHT_MODE:
                        # Use \r to overwrite line for clean status updates
                        print(f"\rLogged: {timestamp} | Temp: {temperature}°C | Hum: {humidity}%", end="", flush=True)
                    
                elif not FLIGHT_MODE:
                    print(f"\rInvalid humidity reading: {humidity}%. Data not logged.", end="", flush=True)
            elif not FLIGHT_MODE:
                print("\rFailed to retrieve data from DHT11 sensor.", end="", flush=True)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nLogging terminated.")
            end_time = datetime.now()
            duration = end_time - SCRIPT_START_TIME
            print(f"Script started at: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Script ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total runtime: {duration}")
            print("Data is saved in the 'data' directory. Run 'dht_plotter.py' for analysis.")
    except Exception as e:
        # In flight mode, we want to fail silently to prevent terminal artifacts.
        # In development, we print the error.
        if not FLIGHT_MODE:
            print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")


if __name__ == "__main__":
    main()

