# =========================================================================
# Kabot-1 Mission: MPU-6050 Motion Logger (Live Data Stream Enabled)
# =========================================================================
# Primary Objective: Continuously sample and log motion data.
# Secondary Objective: Update a central JSON file for the real-time web UI.
# =========================================================================

import time
import os
from datetime import datetime
import json 
import random

# --- Configuration Settings ---
FLIGHT_MODE = True 
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "MPU6050.txt")

# Central file for real-time monitoring dashboard
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

LOG_INTERVAL = 1 # Log motion data more frequently than temp/humidity

# --- MPU/MOCK SENSOR SETUP ---
try:
    import numpy as np
    
    class MockMPU6050:
        def get_accel_data(self):
            t = time.time() * 0.1
            # Mock Z-Accel centered around 1.0g
            return {
                'x': 0.15 + random.uniform(-0.02, 0.02),
                'y': -0.20 + random.uniform(-0.02, 0.02),
                'z': 1.0 + 0.1 * np.sin(t*0.5) + random.uniform(-0.02, 0.02)
            }
        def get_gyro_data(self):
            # Mock X-Gyro (Roll Rate) fluctuation
            return {
                'x': 5.0 * np.cos(time.time() * 0.2) + random.uniform(-0.5, 0.5),
                'y': 6.3 + random.uniform(-0.1, 0.1),
                'z': 0.1 + random.uniform(-0.1, 0.1)
            }
    sensor = MockMPU6050()
    if not FLIGHT_MODE:
        print("MPU-6050 Logger running in Mock Simulation Mode (with NumPy).")

except ImportError:
    if not FLIGHT_MODE:
        print("WARNING: NumPy not found. Running in simple simulation mode.")
    class SimpleMockMPU6050:
        def get_accel_data(self):
            return {'x': 0.17, 'y': -0.20, 'z': 1.0}
        def get_gyro_data(self):
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
    sensor = SimpleMockMPU6050()


def write_live_data(data):
    """
    Reads the existing live data file, updates the MPU metrics, and writes 
    the complete data structure back.
    """
    full_data = {}
    
    # 1. Attempt to read existing data
    if os.path.exists(LIVE_DATA_FILE):
        try:
            with open(LIVE_DATA_FILE, 'r') as f:
                full_data = json.load(f)
        except Exception:
            pass # Ignore read errors

    # 2. Update the specific MPU fields
    full_data.update({
        "timestamp": data["timestamp"],
        "accel_z": data["accel_z"],
        "gyro_x": data["gyro_x"],
    })

    # 3. Overwrite the file with the complete, updated data structure
    try:
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=4)
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"Error writing live data JSON: {e}")


def initialize_log_file():
    """Ensures the data directory exists and the log file is created with a header."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        if not FLIGHT_MODE:
            print(f"Creating MPU-6050 Log file: {LOG_FILE}")
        try:
            with open(LOG_FILE, "w") as f:
                header = "timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n"
                f.write(header)
        except Exception as e:
            if not FLIGHT_MODE:
                print(f"Error creating log file: {e}")
            return False
    return True

def log_data_point():
    """Reads MPU-6050 data, formats it, and APPENDS it to the log file and updates the JSON stream."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        accel_data = sensor.get_accel_data()
        gyro_data = sensor.get_gyro_data()
        
        # --- 1. CSV Log (Memory-Safe Append) ---
        data_line = (
            f"{timestamp},"
            f"{accel_data['x']:.2f},{accel_data['y']:.2f},{accel_data['z']:.2f},"
            f"{gyro_data['x']:.2f},{gyro_data['y']:.2f},{gyro_data['z']:.2f}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(data_line)
        
        # --- 2. JSON Live Data Update ---
        data_point = {
            "timestamp": timestamp,
            # We focus on Z (vertical acceleration) and X (roll rate) for the dashboard
            "accel_z": round(accel_data['z'], 2), 
            "gyro_x": round(gyro_data['x'], 2),
        }
        write_live_data(data_point)
        
        if not FLIGHT_MODE:
            print(f"\rLogged: {timestamp} | Accel Z:{accel_data['z']:.2f} g | Gyro X:{gyro_data['x']:.2f} d/s", end="", flush=True)

    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\rError logging MPU-6050 data: {e}        ", end="", flush=True)


def main_loop():
    """Runs the memory-safe logging loop."""
    try:
        if not initialize_log_file():
            return
            
        if not FLIGHT_MODE:
            print("\nMPU-6050 Logger is active. Press Ctrl+C to stop.")
        
        while True:
            log_data_point()
            time.sleep(LOG_INTERVAL)
            
    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\n\nMPU-6050 logging terminated.")
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\nAn unexpected error occurred during main loop: {e}")

if __name__ == "__main__":
    main_loop()

