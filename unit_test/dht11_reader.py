from gpiozero import Button
from dht11 import DHT11
from time import sleep

# Define the GPIO pin connected to the DHT11 data pin.
# This example uses GPIO 4. Adjust as needed for your setup.
dht_pin = 4

# Create a DHT11 sensor object
sensor = DHT11(dht_pin)

try:
    while True:
        # Read the sensor data
        result = sensor.read()

        # Check if the read was successful
        if result.is_valid():
            # Get the temperature in Celsius
            temperature_c = result.temperature
            # Get the humidity percentage
            humidity_p = result.humidity

            print(f"Temperature: {temperature_c}°C")
            print(f"Humidity: {humidity_p}%")
        else:
            print("Failed to read from sensor. Retrying...")

        # Wait for 60 seconds before the next reading
        sleep(60)

except KeyboardInterrupt:
    print("Script terminated by user.")
except Exception as e:
    print(f"An error occurred: {e}")
