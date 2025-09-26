# =========================================================================
# Kabot-1 Mission: MPU-6050 6-Axis Motion Logger
# (Flight-Ready Version - Optimized for Low RAM/CPU)
# =========================================================================
# Primary Objective: Continuously log acceleration (g) and angular velocity 
# (deg/s) data from the 6-axis IMU to analyze the flight dynamics: ascent, 
# balloon burst shock, and recovery parachute descent stability.
# =========================================================================

import time
import os
import shutil
from datetime import datetime
from smbus2 import SMBus # Standard library for I2C communication

# --- Configuration Settings ---
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "MPU6050.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "MPU6050_backup.txt")

# MPU-6050 I2C Address and Registers
BUS_NUMBER = 1          # I2C bus number on Raspberry Pi
MPU_ADDRESS = 0x68      # MPU-6050 default I2C address
POWER_MGMT_1 = 0x6B     # Power Management Register

ACCEL_XOUT_H = 0x3B     # Start register for X, Y, Z Acceleration (H & L)
GYRO_XOUT_H = 0x43      # Start register for X, Y, Z Gyroscope (H & L)

# Scale Factors (for MPU-6050 set to +/- 2g and +/- 250 deg/s, default)
ACCEL_SCALE_FACTOR = 16384.0 # 2g range
GYRO_SCALE_FACTOR = 131.0    # 250 deg/s range

# Store the start time of the script to calculate total runtime
SCRIPT_START_TIME = datetime.now()

# Initialize I2C Bus
try:
    bus = SMBus(BUS_NUMBER)
except FileNotFoundError:
    print("WARNING: I2C bus not found. Running in simulation mode.")
    bus = None

def read_word_2c(adr):
    """Reads two 8-bit registers and combines them into a signed 16-bit word."""
    if not bus: return 0 # Simulation mode
    high = bus.read_byte_data(MPU_ADDRESS, adr)
    low = bus.read_byte_data(MPU_ADDRESS, adr+1)
    value = (high << 8) + low
    
    # Convert to signed 16-bit
    if (value >= 0x8000):
        return -((65535 - value) + 1)
    else:
        return value

def get_mpu_data():
    """Reads, scales, and returns the 6-axis IMU data."""
    if not bus:
        # Generate stable mock data if bus is not available (for testing)
        t = (datetime.now() - SCRIPT_START_TIME).total_seconds()
        # Simulate slight acceleration (1g gravity) and minor noise
        return (
            0.01 + 0.05 * (t % 10) / 10,
            0.05 + 0.1 * (t % 10) / 10,
            1.0 + 0.02 * np.sin(t * 0.1), # Gravity on Z-axis
            0.1 * np.cos(t * 0.2),
            0.1 * np.sin(t * 0.3),
            0.05 * np.cos(t * 0.15)
        )
    
    # Acceleration Data
    accel_x = read_word_2c(ACCEL_XOUT_H) / ACCEL_SCALE_FACTOR
    accel_y = read_word_2c(ACCEL_XOUT_H + 2) / ACCEL_SCALE_FACTOR
    accel_z = read_word_2c(ACCEL_XOUT_H + 4) / ACCEL_SCALE_FACTOR
    
    # Gyroscope Data
    gyro_x = read_word_2c(GYRO_XOUT_H) / GYRO_SCALE_FACTOR
    gyro_y = read_word_2c(GYRO_XOUT_H + 2) / GYRO_SCALE_FACTOR
    gyro_z = read_word_2c(GYRO_XOUT_H + 4) / GYRO_SCALE_FACTOR
    
    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z


def main():
    """Main function to run the sensor logging loop."""
    print(f"Ensuring data directory '{DATA_DIR}' exists...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize the MPU-6050
    if bus:
        print("Initializing MPU-6050...")
        # Wake up the MPU-6050 (set sleep bit 0 to 0)
        bus.write_byte_data(MPU_ADDRESS, POWER_MGMT_1, 0)
        time.sleep(0.1)
    
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return
    
    print("Kabot-1 MPU-6050 Logger is active. Press Ctrl+C to stop logging.")
    main_loop()

def main_loop():
    """Continuously reads sensor data and logs it."""
    try:
        # === Core mission loop for continuous data collection ===
        while True:
            # Get 6-axis data (Acc X/Y/Z in g, Gyro X/Y/Z in deg/s)
            ax, ay, az, gx, gy, gz = get_mpu_data()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # --- Step 1: Backup the existing data file ---
            if os.path.exists(DATA_FILE):
                shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
            
            # --- Step 2: Append new data to the main file ---
            with open(DATA_FILE, "a") as f:
                f.write(f"{timestamp},{ax:.4f},{ay:.4f},{az:.4f},{gx:.4f},{gy:.4f},{gz:.4f}\n")
            
            # Updates on one line using \r for low resource terminal output
            print(f"\rLogged: {timestamp} | Accel: X={ax:.2f}, Y={ay:.2f}, Z={az:.2f} g | Gyro: X={gx:.1f}, Y={gy:.1f}, Z={gz:.1f} d/s", end="", flush=True)
            
            time.sleep(0.5) # Log at 2Hz for high-detail motion capture
            
    except KeyboardInterrupt:
        print("\nLogging terminated.")
        end_time = datetime.now()
        duration = end_time - SCRIPT_START_TIME
        print(f"Script started at: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime: {duration}")
        print("Data is saved in the 'data' directory. Run 'mpu_plotter.py' for analysis.")
    except Exception as e:
        print(f"\nAn error occurred during main loop: {e}")


if __name__ == "__main__":
    # Import numpy here only if needed for mock data, otherwise keep it out 
    # for flight use. Since it's used in get_mpu_data() for simulation, 
    # we'll include it here.
    try:
        import numpy as np
    except ImportError:
        print("WARNING: numpy not found. Mock data will be zeros.")
        def np_sin(*args): return 0
        def np_cos(*args): return 0
        def np_pi(*args): return 0
        np = type('module', (object,), {'sin': np_sin, 'cos': np_cos, 'pi': np_pi})
        
    main()

