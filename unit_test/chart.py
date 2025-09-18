import time
import datetime
import matplotlib.pyplot as plt
import zerogpio as gpio

# Pin assignments (BCM numbering)
DOUT_PIN = 23     # Sound sensor DOUT
BUZZER_PIN = 18   # Buzzer control pin

# Sampling parameters
BURST_DURATION = 2.0      # seconds
SAMPLE_RATE = 4000        # Hz
SAMPLE_INTERVAL = 1.0 / SAMPLE_RATE

# Setup GPIO
gpio.pinMode(DOUT_PIN, gpio.INPUT)
gpio.pinMode(BUZZER_PIN, gpio.OUTPUT)

def buzzer_on():
    gpio.digitalWrite(BUZZER_PIN, gpio.HIGH)  # Active buzzer
    # For passive piezo, use gpio.pwmStart(BUZZER_PIN, freq, duty)

def buzzer_off():
    gpio.digitalWrite(BUZZER_PIN, gpio.LOW)
    # For passive piezo, gpio.pwmStop(BUZZER_PIN)

def measure_and_plot():
    """Measure DOUT state during a burst and save a chart as SVG."""
    timestamps = []
    states = []
    start_time = time.perf_counter()

    for i in range(int(BURST_DURATION * SAMPLE_RATE)):
        now = time.perf_counter() - start_time
        state = gpio.digitalRead(DOUT_PIN)
        timestamps.append(now)
        states.append(state)
        # Busy-wait until next sample
        while (time.perf_counter() - start_time) < ((i + 1) * SAMPLE_INTERVAL):
            pass

    # Calculate high fraction
    high_fraction = sum(states) / len(states)

    # Plot
    plt.figure(figsize=(8, 3))
    plt.step(timestamps, states, where='post')
    plt.ylim(-0.2, 1.2)
    plt.xlabel("Time (s)")
    plt.ylabel("DOUT State")
    plt.title(f"Burst at {datetime.datetime.utcnow().isoformat()}Z\nHigh fraction: {high_fraction:.3f}")
    plt.grid(True)

    # Save as SVG
    filename = f"burst_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.svg"
    plt.savefig(filename, format='svg', bbox_inches='tight')
    plt.close()

    return high_fraction, filename

# Main loop
while True:
    buzzer_on()
    frac, fname = measure_and_plot()
    buzzer_off()
    print(f"Burst complete. High fraction: {frac:.3f}. Chart saved as {fname}")
    # TODO: log frac + altitude/pressure/temp to CSV here
    time.sleep(28)  # Wait until next burst
