import os
import time
import board
import busio
import adafruit_mpu6050
import matplotlib.pyplot as plt
from datetime import datetime
import shutil

# --- I2C Setup for MPU6050 ---
# The MPU6050 typically connects to the primary I2C bus on GPIO2/GPIO3
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# --- File Paths ---
DATA_FILE = "mpu6050_data.txt"
DATA_BACKUP_FILE = "mpu6050_data_backup.txt"
CHART_FILE = "mpu6050_chart.svg"
CHART_BACKUP_FILE = "mpu6050_chart_backup.svg"

# --- Main Logging Function ---
def log_mpu_data():
    """Reads MPU6050 data, logs it, and backs up the file."""

    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,acceleration_x,acceleration_y,acceleration_z,gyro_x,gyro_y,gyro_z\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False # Exit if file can't be created

    # Backup data file
    if os.path.exists(DATA_FILE):
        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

    # Read data from the sensor
    try:
        accel_data = mpu.acceleration
        gyro_data = mpu.gyro
    except OSError as e:
        print(f"Failed to read MPU6050 data: {e}")
        return False

    # Log the new data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DATA_FILE, "a") as f:
        f.write(f"{timestamp},{accel_data[0]},{accel_data[1]},{accel_data[2]},{gyro_data[0]},{gyro_data[1]},{gyro_data[2]}\n")
    
    print(f"Logged MPU6050 data: Accel ({accel_data}), Gyro ({gyro_data})")
    return True

# --- Chart Generation ---
def generate_chart():
    """Reads logged data and creates an updated SVG chart."""
    dates, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = [], [], [], [], [], [], []
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            next(f)  # Skip header
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) == 7:
                        dates.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
                        accel_x.append(float(parts[1]))
                        accel_y.append(float(parts[2]))
                        accel_z.append(float(parts[3]))
                        gyro_x.append(float(parts[4]))
                        gyro_y.append(float(parts[5]))
                        gyro_z.append(float(parts[6]))
                except (ValueError, IndexError):
                    continue

    if not dates:
        return
    
    # Backup the existing chart before plotting a new one
    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Plotting Accelerometer Data
    fig_accel, ax_accel = plt.subplots(figsize=(10, 6))
    ax_accel.set_title('MPU6050 Accelerometer Data')
    ax_accel.set_xlabel('Time')
    ax_accel.set_ylabel('Acceleration (m/s²)')
    ax_accel.plot(dates, accel_x, label='X-axis')
    ax_accel.plot(dates, accel_y, label='Y-axis')
    ax_accel.plot(dates, accel_z, label='Z-axis')
    plt.gcf().autofmt_xdate()
    ax_accel.legend()
    plt.savefig('accel_chart.svg') # Save as a separate file
    plt.close(fig_accel)

    # Plotting Gyroscope Data
    fig_gyro, ax_gyro = plt.subplots(figsize=(10, 6))
    ax_gyro.set_title('MPU6050 Gyroscope Data')
    ax_gyro.set_xlabel('Time')
    ax_gyro.set_ylabel('Angular Velocity (rad/s)')
    ax_gyro.plot(dates, gyro_x, label='X-axis')
    ax_gyro.plot(dates, gyro_y, label='Y-axis')
    ax_gyro.plot(dates, gyro_z, label='Z-axis')
    plt.gcf().autofmt_xdate()
    ax_gyro.legend()
    plt.savefig('gyro_chart.svg') # Save as a separate file
    plt.close(fig_gyro)

    print("Charts generated and saved.")

if __name__ == "__main__":
    while True:
        if log_mpu_data():
            generate_chart()
        time.sleep(300) # Wait 5 minutes before the next logging interval
