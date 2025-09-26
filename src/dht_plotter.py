#!/usr/bin/env python3
import sys
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import savgol_filter

def plot_file(data_file):
    dates, temps, hums = [], [], []
    with open(data_file, "r") as f:
        lines = f.readlines()[1:]  # skip header
        for line in lines:
            try:
                t, temp, hum = line.strip().split(",")
                dates.append(datetime.strptime(t, "%Y-%m-%d %H:%M:%S"))
                temps.append(float(temp))
                hums.append(float(hum))
            except:
                continue

    if not dates:
        print("No data found.")
        return

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax1 = plt.subplots(figsize=(12,6))

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°C)", color="firebrick")
    ax1.plot(dates, temps, color="salmon", alpha=0.7, label="Temperature")
    if len(temps) >= 11:
        ax1.plot(dates, savgol_filter(temps, 11, 3), color="firebrick", linewidth=2, label="Smoothed Temp")
    ax1.tick_params(axis="y", labelcolor="firebrick")

    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate(rotation=30)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Humidity (%)", color="royalblue")
    ax2.plot(dates, hums, color="skyblue", alpha=0.7, label="Humidity")
    if len(hums) >= 11:
        ax2.plot(dates, savgol_filter(hums, 11, 3), color="royalblue", linewidth=2, label="Smoothed Hum")
    ax2.tick_params(axis="y", labelcolor="royalblue")
    ax2.set_ylim(0, 100)

    # Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)

    # Watermark
    fig.text(0.95, 0.02, "Kabot‑1 Mission", fontsize=14, color="gray", alpha=0.3, ha="right", va="bottom")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./plot_data.py <datafile>")
    else:
        plot_file(sys.argv[1])
