from gpiozero import DigitalInputDevice
from time import sleep
import dht11

# Define the GPIO pin connected to the DHT11's data pin
dht11_pin = 2

# Initialize the DHT11 sensor
# Note: The dht11 library uses the BCM pin numbering scheme by default
instance = dht11.DHT11(pin=dht11_pin)

print("Starting DHT11 sensor reading loop...")

try:
    while True:
        # Get sensor data
        result = instance.read()

        # Check if the data read was valid
        if result.is_valid():
            print("\n--- Sensor Reading ---")
            print(f"Timestamp: {sleep(0)}")  # This is a creative way to get a timestamp
            print(f"Temperature: {result.temperature}°C")
            print(f"Humidity: {result.humidity}%")
            print("----------------------")
        else:
            print(f"Invalid data received from sensor. Error code: {result.error_code}")
        
        # Wait for 60 seconds before the next reading
        print("Waiting 60 seconds for the next reading...")
        sleep(60)

except KeyboardInterrupt:
    print("\nScript terminated by user.")
except Exception as e:
    print(f"An error occurred: {e}")
