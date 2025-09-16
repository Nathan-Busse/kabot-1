import Adafruit_DHT
import time

# Sensor type and GPIO pin
SENSOR = Adafruit_DHT.DHT11
PIN = 4  # BCM numbering, e.g., GPIO4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
    
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
    else:
        print("Failed to retrieve data from sensor")
    
    time.sleep(60)  # wait 60 seconds

