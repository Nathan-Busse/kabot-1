import os
import time
import shutil
import matplotlib.pyplot as plt
from datetime import datetime
from gpiozero import LED, Button  # gpiozero abstractions

# --- Hardware Pins ---
SOUND_DETECTOR_PIN = 14   # KY-038 D0 → GPIO14
BUZZER_PIN = 21           # Piezo buzzer → GPIO21

# --- File Paths ---
DATA_FILE = "src/logger/data/sound.txt"
DATA_BACKUP_FILE = "src/logger/data/sound_backup.txt"
CHART_FILE = "src/charts/sound_chart.svg"
CHART_BACKUP_FILE = "src/charts/sound_chart_backup.svg"

# --- GPIO Devices ---
buzzer = LED(BUZZER_PIN)
sound_sensor = Button(SOUND_DETECTOR_PIN)

def log_sound_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("timestamp,sound_detected,is_buzzer_on\n")

    shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

    # --- Test 1: Buzzer ON ---
    buzzer.on()
    print("Buzzer ON. Logging sound detection...")
    for _ in range(5):
        sound_detected = int(sound_sensor.is_pressed)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},1\n")
        time.sleep(1)
    buzzer.off()
    print("Buzzer OFF.")

    # --- Test 2: Ambient Sound (Buzzer OFF) ---
    print("Logging ambient sound detection...")
    for _ in range(5):
        sound_detected = int(sound_sensor.is_pressed)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},0\n")
        time.sleep(1)

    return True

def generate_chart():
    os.makedirs(os.path.dirname(CHART_FILE), exist_ok=True)

    dates, sound_detected_values, buzzer_states = [], [], []
    with open(DATA_FILE, "r") as f:
        next(f)  # skip header
        for line in f:
            try:
                ts, sound_str, buzzer_str = line.strip().split(',')
                dates.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                sound_detected_values.append(int(sound_str))
                buzzer_states.append(int(buzzer_str))
            except Exception:
                continue

    if not dates:
        return

    if os.path.exists(CHART_FILE):
        os.replace(CHART_FILE, CHART_BACKUP_FILE)

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Sound Detection Test (D0 Pin)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Sound Detected (1=Yes, 0=No)")

    ax.step(dates, sound_detected_values, where="mid", label="Sound Detected")

    buzzer_on_dates = [dates[i] for i, state in enumerate(buzzer_states) if state == 1]
    buzzer_on_values = [1.05] * len(buzzer_on_dates)
    ax.plot(buzzer_on_dates, buzzer_on_values, "ro", label="Buzzer ON")

    ax.set_yticks([0, 1])
    fig.autofmt_xdate()
    ax.legend()
    plt.savefig(CHART_FILE)
    plt.close(fig)

if __name__ == "__main__":
    while True:
        if log_sound_data():
            generate_chart()
        time.sleep(0.1)  # 0.1  minutes
