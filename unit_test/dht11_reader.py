# First, install the necessary libraries:
# pip3 install adafruit-blinka
# pip3 install adafruit-circuitpython-dht

import adafruit_dht
import board
from time import sleep

# Define the GPIO pin connected to the DHT sensor
# This example uses GPIO 4. Adjust as needed.
dht_pin = board.D4

# Create a DHT11 sensor object
# For DHT22, change adafruit_dht.DHT11 to adafruit_dht.DHT22
dht_device = adafruit_dht.DHT11(dht_pin, use_pulseio=False)

try:
    while True:
        try:
            # Read the temperature and humidity
            temperature_c = dht_device.temperature
            humidity_p = dht_device.humidity

            if temperature_c is not None and humidity_p is not None:
                print(f"Temperature: {temperature_c:.1f}°C")
                print(f"Humidity: {humidity_p:.1f}%")
            else:
                print("Failed to read from sensor. Retrying...")

        except RuntimeError as error:
            # Errors happen, but don't stop the script.
            print(error.args[0])

        # Wait for 60 seconds before the next reading
        sleep(60)

except KeyboardInterrupt:
    print("Script terminated by user.")
