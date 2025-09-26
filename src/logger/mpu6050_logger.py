# =========================================================================
# Kabot-1 Mission: MPU-6050 Motion Logger
# (Flight-Ready Version - Optimized for Minimal RAM Usage)
# =========================================================================
# Primary Objective: Continuously sample and log accelerometer and gyroscope 
# data to analyze flight dynamics, spin rates, and external forces.
# This version uses memory-safe file handling (append mode) to prevent 
# excessive RAM consumption during long missions.
# =========================================================================

import time
import os
from datetime import datetime

# --- Configuration Settings ---
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "MPU6050.txt")
LOG_BACKUP_FILE = os.path.join(DATA_DIR, "MPU6050_backup.txt")

# Logging interval in seconds
LOG_INTERVAL = 1

# Attempt to import MPU6050 library
try:
    # Assuming the use of a simple library for I2C access
    # from mpu6050 import MPU6050 
    # sensor = MPU6050(0x68) # Assuming default address
    
    # Placeholder for the actual sensor initialization
    class MockMPU6050:
        """Mocks MPU6050 sensor data for simulation purposes."""
        def get_accel_data(self):
            # Simulate slight turbulence and gravity offset
            t = time.time() * 0.1
            return {
                'x': 0.15 + 0.05 * (np.sin(t) + np.random.randn() * 0.01),
                'y': -0.20 + 0.05 * (np.cos(t) + np.random.randn() * 0.01),
                'z': 1.18 + 0.05 * (np.sin(t*0.5) + np.random.randn() * 0.01)
            }

        def get_gyro_data(self):
            # Simulate slow rotation/drift
            return {
                'x': -6.5 + np.random.randn() * 0.1,
                'y': 6.3 + np.random.randn() * 0.1,
                'z': 0.1 + np.random.randn() * 0.1
            }

    sensor = MockMPU6050()
    import numpy as np # Used by MockMPU6050
    HAS_MPU_SENSOR = True
    print("MPU-6050 Logger running in Mock Simulation Mode.")

except ImportError:
    # This block runs if the MPU6050 library is not installed
    print("WARNING: MPU6050 library not found. Running in simulation mode without dynamic data.")
    
    # Simple fallback Mock class without dependencies
    class SimpleMockMPU6050:
        def get_accel_data(self):
            return {'x': 0.17, 'y': -0.20, 'z': 1.18}
        def get_gyro_data(self):
            return {'x': -6.5, 'y': 6.3, 'z': 0.1}

    sensor = SimpleMockMPU6050()
    HAS_MPU_SENSOR = False


def initialize_log_file():
    """
    Ensures the data directory exists and the log file is created with a header.
    It performs a one-time check, making this a memory-safe operation.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        print(f"Creating MPU-6050 Log file: {LOG_FILE}")
        try:
            with open(LOG_FILE, "w") as f:
                header = "timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n"
                f.write(header)
        except Exception as e:
            print(f"Error creating log file: {e}")
            return False
    return True

def log_data_point():
    """
    Reads MPU-6050 data, formats it, and APPENDS it to the log file.
    
    CRITICAL: This function opens the file in append mode ('a'), writes one line,
    and immediately closes the file. This prevents RAM usage from ballooning.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        accel_data = sensor.get_accel_data()
        gyro_data = sensor.get_gyro_data()
        
        # Format the data into a single CSV line
        data_line = (
            f"{timestamp},"
            f"{accel_data['x']:.2f},{accel_data['y']:.2f},{accel_data['z']:.2f},"
            f"{gyro_data['x']:.2f},{gyro_data['y']:.2f},{gyro_data['z']:.2f}\n"
        )
        
        # === Memory-Safe File Append Operation ===
        with open(LOG_FILE, "a") as f:
            f.write(data_line)
        
        # Display feedback (use '\r' to overwrite the line in the terminal)
        print(f"\rLogged: {timestamp} | Accel X:{accel_data['x']:.2f} g | Gyro Z:{gyro_data['z']:.2f} d/s", end="", flush=True)

    except Exception as e:
        print(f"\rError logging MPU-6050 data: {e}        ", end="", flush=True)


def main_loop():
    """Runs the memory-safe logging loop."""
    try:
        if not initialize_log_file():
            return
            
        print("\nMPU-6050 Logger is active. Press Ctrl+C to stop.")
        
        # === Core mission loop for continuous data collection ===
        while True:
            log_data_point()
            time.sleep(LOG_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nMPU-6050 logging terminated.")
        print(f"Data saved to {LOG_FILE}.")
    except Exception as e:
        print(f"\nAn error occurred during main loop: {e}")

if __name__ == "__main__":
    main_loop()

