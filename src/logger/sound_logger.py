import os
import time
import gpiozero
import matplotlib.pyplot as plt
from datetime import datetime
import shutil

# --- Hardware Pins ---
# Keyes KY-038 D0 pin connected to GPIO14
SOUND_DETECTOR_PIN = 14
# Piezo Buzzer connected to GPIO4
BUZZER_PIN = 21

# --- File Paths ---
DATA_FILE = "sound_data_D0.txt"
DATA_BACKUP_FILE = "sound_data_D0_backup.txt"
CHART_FILE = "sound_chart_D0.svg"
CHART_BACKUP_FILE = "sound_chart_D0_backup.svg"

# --- ADC/A0 Code (Commented Out) ---
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn

# I2C_SDA_PIN = board.D14
# I2C_SCL_PIN = board.D15
# i2c = busio.I2C(I2C_SCL_PIN, I2C_SDA_PIN)
# ads = ADS.ADS1115(i2c)
# chan = AnalogIn(ads, ADS.P0)
# A0_DATA_FILE = "sound_data_A0.txt"


def log_sound_data():
    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False

    # Backup data file
    if os.path.exists(DATA_FILE):
        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

    # --- GPIO Setup ---
    zerogpio.setup(BUZZER_PIN, zerogpio.OUT)
    zerogpio.setup(SOUND_DETECTOR_PIN, zerogpio.IN)

    # --- Test 1: Buzzer ON ---
    zerogpio.output(BUZZER_PIN, zerogpio.HIGH)
    print("Buzzer ON. Logging sound detection...")

    for _ in range(5):
        sound_detected = zerogpio.input(SOUND_DETECTOR_PIN)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},1\n")
        time.sleep(1)

    zerogpio.output(BUZZER_PIN, zerogpio.LOW)
    print("Buzzer OFF.")

    # --- Test 2: Ambient Sound (Buzzer OFF) ---
    print("Logging ambient sound detection...")

    for _ in range(5):
        sound_detected = zerogpio.input(SOUND_DETECTOR_PIN)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},0\n")
        time.sleep(1)

    return True


def generate_chart():
    dates, sound_detected_values, buzzer_states = [], [], []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            next(f)
            for line in f:
                try:
                    timestamp_str, sound_str, buzzer_str = line.strip().split(',')
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    sound_detected_values.append(int(sound_str))
                    buzzer_states.append(int(buzzer_str))
                except (ValueError, IndexError):
                    continue

    if not dates:
        return

    if os.path.exists(CHART_FILE):
        os.rename(CHART_FILE, CHART_BACKUP_FILE)

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.set_xlabel('Time')
    ax.set_ylabel('Sound Detected (1=Yes, 0=No)')
    ax.set_title('Sound Detection Test (D0 Pin)')
    ax.step(dates, sound_detected_values, where='mid', label='Sound Detected')

    buzzer_on_dates = [dates[i] for i, state in enumerate(buzzer_states) if state == 1]
    buzzer_on_values = [1.05] * len(buzzer_on_dates)
    ax.plot(buzzer_on_dates, buzzer_on_values, 'ro', label='Buzzer ON')

    ax.set_yticks([0, 1])
    plt.gcf().autofmt_xdate()
    ax.legend()
    plt.savefig(CHART_FILE)
    plt.close(fig)


if __name__ == "__main__":
    while True:
        if log_sound_data():
            generate_chart()
        time.sleep(1200)
