# =========================================================================
# Kabot-1 Post-Flight MPU-6050 Data Analysis and Chart Generation
# =========================================================================
# This script is run post-flight to analyze the payload's movement (vibration,
# spin, and G-forces) across the mission. It plots all 6 axes of data.
# =========================================================================

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from scipy.signal import savgol_filter
import os

# Configuration settings (Paths are relative to src/plotter)
# Data is located at ../logger/data
DATA_DIR = "../logger/data"
DATA_FILE = os.path.join(DATA_DIR, "MPU6050.txt")
# Charts are located at ../charts
CHARTS_DIR = "../charts"
CHART_FILE = os.path.join(CHARTS_DIR, "mpu6050_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "mpu6050_chart_backup.svg")

# Savitzky-Golay Filter settings
WINDOW_LENGTH = 51 # Use a larger window for smoothing high-frequency motion data
POLY_ORDER = 3

def generate_mpu_chart():
    """Reads all MPU-6050 data and generates a composite 6-axis chart."""
    
    # Initialize lists to store all 7 columns of data
    dates = []
    data_columns = {
        'accel_x': [], 'accel_y': [], 'accel_z': [],
        'gyro_x': [], 'gyro_y': [], 'gyro_z': []
    }
    
    # === Step 1: Read all data from the mission log file ===
    if not os.path.exists(DATA_FILE):
        print(f"Error: Mission data file not found at {DATA_FILE}")
        print("Please ensure the MPU-6050 data file has been transferred from the Kabot-1 payload.")
        return

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            
            if not lines:
                print("No data found in log file.")
                return

            # Determine column names and their order from the header
            header = lines[0].strip().split(',')
            data_keys = header[1:] # Skip 'timestamp'
            
            for line in lines[1:]:
                try:
                    parts = line.strip().split(',')
                    timestamp_str = parts[0]
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    
                    # Populate data columns
                    for i, key in enumerate(data_keys):
                        data_columns[key].append(float(parts[i+1]))
                        
                except (ValueError, IndexError):
                    continue
    except Exception as e:
        print(f"Error reading data file for chart generation: {e}")
        return

    if not dates:
        print("No data to plot.")
        return
    
    # Ensure charts directory exists
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # Calculate flight duration for the title
    SCRIPT_START_TIME = dates[0]
    end_time = dates[-1]
    duration = end_time - SCRIPT_START_TIME
    total_hours = duration.total_seconds() // 3600
    total_minutes = (duration.total_seconds() % 3600) // 60
    total_seconds = duration.total_seconds() % 60
    duration_str = f"{int(total_hours):02d}h {int(total_minutes):02d}m {int(total_seconds):02d}s"
    
    # === Step 2: Configure Plot Style and Structure ===
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 10, 'axes.labelsize': 12, 'axes.titlesize': 14})
    
    # Create a figure with two subplots (1 for Accel, 1 for Gyro)
    fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Overall Title
    fig.suptitle(
        f"Kabot I Mission MPU-6050 Motion Analysis | Duration: {duration_str}\n"
        f"Start: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        fontsize=16
    )
    
    # Common Time axis formatting
    date_formatter = mdates.DateFormatter('%H:%M')
    
    # --- Acceleration Plot (Top Subplot) ---
    ax_accel.set_title('Acceleration Data (Linear G-Forces)', fontsize=14)
    ax_accel.set_ylabel('Acceleration (g)')
    
    colors = {'x': 'tab:red', 'y': 'tab:green', 'z': 'tab:blue'}
    
    if len(dates) >= WINDOW_LENGTH:
        print(f"Applying Savitzky-Golay filter (Window: {WINDOW_LENGTH}, Poly: {POLY_ORDER}) to smooth data...")

    for axis in ['x', 'y', 'z']:
        key = f'accel_{axis}'
        raw_data = data_columns[key]
        
        # Plot Raw Data
        ax_accel.plot(dates, raw_data, label=f'Accel {axis} (Raw)', 
                      color=colors[axis], linewidth=1.0, alpha=0.3)
        
        # Plot Smoothed Data
        if len(raw_data) >= WINDOW_LENGTH:
            smooth_data = savgol_filter(raw_data, WINDOW_LENGTH, POLY_ORDER)
            ax_accel.plot(dates, smooth_data, label=f'Accel {axis} (Smoothed)', 
                          color=colors[axis], linewidth=2.0)
    
    ax_accel.grid(True, linestyle='--', alpha=0.6)
    ax_accel.legend(loc='upper right', ncol=3)
    
    # --- Gyroscope Plot (Bottom Subplot) ---
    ax_gyro.set_title('Gyroscope Data (Rotational Velocity)', fontsize=14)
    ax_gyro.set_xlabel('Time (HH:MM)')
    ax_gyro.set_ylabel('Angular Velocity (deg/s)')
    
    for axis in ['x', 'y', 'z']:
        key = f'gyro_{axis}'
        raw_data = data_columns[key]
        
        # Plot Raw Data
        ax_gyro.plot(dates, raw_data, label=f'Gyro {axis} (Raw)', 
                     color=colors[axis], linewidth=1.0, alpha=0.3)
        
        # Plot Smoothed Data
        if len(raw_data) >= WINDOW_LENGTH:
            smooth_data = savgol_filter(raw_data, WINDOW_LENGTH, POLY_ORDER)
            ax_gyro.plot(dates, smooth_data, label=f'Gyro {axis} (Smoothed)', 
                         color=colors[axis], linewidth=2.0)
                         
    ax_gyro.xaxis.set_major_formatter(date_formatter)
    ax_gyro.grid(True, linestyle='--', alpha=0.6)
    ax_gyro.legend(loc='upper right', ncol=3)
    
    # Rotate x-axis labels for readability
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make space for suptitle
    
    # === Step 3: Save Chart with Backup ===
    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)
        
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"\nSuccessfully generated MPU-6050 mission chart: '{CHART_FILE}'")
    print(f"Chart covers {len(dates)} data points over a duration of {duration_str}.")


if __name__ == "__main__":
    generate_mpu_chart()

