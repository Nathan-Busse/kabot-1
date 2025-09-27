# =========================================================================
# The Kabot-1 Mission: High-Altitude Environmental Data Logger
# (Flight-Ready Version - Optimized for Low RAM/CPU)
# =========================================================================

import Adafruit_DHT
import time
from datetime import datetime
import os
import json # New import for JSON output

# --- Configuration Settings ---
# Set to True for the actual mission flight to silence all terminal output 
FLIGHT_MODE = True 

# Sensor settings
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4 

# Directory for data files (Relative to src/logger/)
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")

# Central file for real-time monitoring dashboard
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

def write_live_data(data):
    """
    Reads the existing live data file, updates the DHT metrics, and writes 
    the complete data structure back. This ensures all logger data is 
    combined into one file for the web UI.
    """
    full_data = {}
    
    # 1. Attempt to read existing data (may not exist if other loggers haven't run yet)
    if os.path.exists(LIVE_DATA_FILE):
        try:
            # Use minimal read/write operations for memory safety
            with open(LIVE_DATA_FILE, 'r') as f:
                full_data = json.load(f)
        except Exception:
            # Ignore read errors (e.g., file being written by another logger), start fresh
            pass 

    # 2. Update the specific DHT fields
    full_data.update({
        "timestamp": data["timestamp"],
        "temp": data["temp"],
        "hum": data["hum"],
    })

    # 3. Overwrite the file with the complete, updated data structure
    try:
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=4)
    except Exception as e:
        # Fail silently in flight mode
        if not FLIGHT_MODE:
            print(f"Error writing live data JSON: {e}")


def main():
    """Main function to run the sensor logging loop."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Ensure the main data log file has a header
    if not os.path.exists(DATA_FILE):
        if not FLIGHT_MODE:
            print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,temperature,humidity\n")
        except Exception as e:
            if not FLIGHT_MODE:
                print(f"CRITICAL ERROR: Failed to create log file: {e}")
            return
    
    if not FLIGHT_MODE:
        print(f"Kabot-1 Data Logger is active. Logging to {DATA_FILE}. Press Ctrl+C to stop.")
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            
            if humidity is not None and temperature is not None:
                if 20 <= humidity <= 90:
                    # Use only HH:MM:SS for timestamp to save space in log
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Log the data line to the main CSV file (Memory-Safe Append)
                    data_line = f"{timestamp},{temperature:.1f},{humidity:.1f}\n"
                    with open(DATA_FILE, "a") as f:
                        f.write(data_line)
                    
                    # Log the data point to the centralized JSON file for the dashboard
                    data_point = {
                        "timestamp": timestamp,
                        "temp": round(temperature, 1),
                        "hum": round(humidity, 1)
                    }
                    write_live_data(data_point)

                    if not FLIGHT_MODE:
                        print(f"\rLogged: {timestamp} | Temp: {temperature:.1f}°C | Hum: {humidity:.1f}%", end="", flush=True)
                    
                elif not FLIGHT_MODE:
                    print(f"\rInvalid humidity reading: {humidity:.1f}%. Data not logged.", end="", flush=True)
            elif not FLIGHT_MODE:
                print("\rFailed to retrieve data from DHT11 sensor.", end="", flush=True)
            
            time.sleep(10) # Log every 10 seconds
            
    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nLogging terminated.")
            end_time = datetime.now()
            duration = end_time - SCRIPT_START_TIME
            print(f"Total runtime: {duration}")
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")


if __name__ == "__main__":
    main()

