import os, time, shutil
import matplotlib
matplotlib.use("Agg")  # headless, lightweight
import matplotlib.pyplot as plt
from datetime import datetime
from gpiozero import LED, Button

# --- Hardware Pins ---
SOUND_DETECTOR_PIN = 14
BUZZER_PIN = 21

# --- File Paths ---
DATA_DIR = "src/logger/data"
CHARTS_DIR = "src/charts"
DATA_FILE = os.path.join(DATA_DIR, "sound.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "sound_backup.txt")
CHART_FILE = os.path.join(CHARTS_DIR, "sound_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "sound_chart_backup.svg")

# --- GPIO Devices ---
buzzer = LED(BUZZER_PIN)
sound_sensor = Button(SOUND_DETECTOR_PIN)

def safe_write(path, line):
    tmp = path + ".tmp"
    with open(tmp, "a") as f:
        f.write(line)
    os.replace(tmp, path)

def log_sound_data():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,sound_detected,is_buzzer_on\n")

        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

        # Test 1: Buzzer ON
        buzzer.on()
        print("Buzzer ON...", end="", flush=True)
        for _ in range(5):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            val = int(sound_sensor.is_pressed)
            safe_write(DATA_FILE, f"{ts},{val},1\n")
            time.sleep(1)
        buzzer.off()
        print("OFF...", end="", flush=True)

        # Test 2: Ambient
        print("Ambient...", end="", flush=True)
        for _ in range(5):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            val = int(sound_sensor.is_pressed)
            safe_write(DATA_FILE, f"{ts},{val},0\n")
            time.sleep(1)
        print("done.", flush=True)
        return True
    except Exception as e:
        print(f"[Error in log_sound_data: {e}]", flush=True)
        return False

def generate_chart():
    try:
        os.makedirs(CHARTS_DIR, exist_ok=True)
        dates, vals, buzz = [], [], []
        with open(DATA_FILE, "r") as f:
            next(f)
            for line in f:
                try:
                    ts, s, b = line.strip().split(',')
                    dates.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                    vals.append(int(s))
                    buzz.append(int(b))
                except Exception:
                    continue
        if not dates:
            return
        if os.path.exists(CHART_FILE):
            os.replace(CHART_FILE, CHART_BACKUP_FILE)

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.step(dates, vals, where="mid", label="Sound Detected")
        buzzer_on_dates = [dates[i] for i, state in enumerate(buzz) if state == 1]
        ax.plot(buzzer_on_dates, [1.05]*len(buzzer_on_dates), "ro", label="Buzzer ON")
        ax.set_yticks([0, 1])
        ax.set_title("Sound Detection (D0)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Detected")
        fig.autofmt_xdate()
        ax.legend()
        plt.savefig(CHART_FILE)
        plt.close(fig)
    except Exception as e:
        print(f"[Error in generate_chart: {e}]", flush=True)

if __name__ == "__main__":
    try:
        while True:
            if log_sound_data():
                generate_chart()
            time.sleep(6)  # 0.1 minutes
    except KeyboardInterrupt:
        buzzer.off()
        print("\nLogger stopped cleanly.", flush=True)
