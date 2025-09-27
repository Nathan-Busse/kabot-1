import os, sys
import matplotlib.pyplot as plt
import numpy as np

DATA_FILE = "src/logger/data/sound.txt"
CHARTS_DIR = "src/charts"
CHART_FILE = os.path.join(CHARTS_DIR, "sound_chart.svg")

def generate_sound_chart():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Sound log not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    with open(DATA_FILE) as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        print("No sound data to plot.", file=sys.stderr)
        sys.exit(2)

    values = [float(x.split(",")[1]) for x in lines if "," in x]

    os.makedirs(CHARTS_DIR, exist_ok=True)
    plt.style.use("ggplot")
    plt.figure(figsize=(12,6))
    plt.plot(values, color="purple", linewidth=1)
    plt.title("Sound Logger Data")
    plt.xlabel("Sample")
    plt.ylabel("Level")
    plt.savefig(CHART_FILE)
    plt.close()
    print(f"Chart generated: {CHART_FILE}")

if __name__ == "__main__":
    generate_sound_chart()
