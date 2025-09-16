import time
import sys

# A simple loop to keep the script from exiting.
if __name__ == "__main__":
    print("Kabot is running!")
    try:
        while True:
            # Your main program logic goes here
            # For example: read sensor data, log to file, etc.
            print("Kabot is still alive...")
            time.sleep(10)  # Sleep for 10 seconds to avoid high CPU usage
    except KeyboardInterrupt:
        # Gracefully exit on Ctrl+C (not relevant for a payload, but good practice)
        print("Kabot is stopping...")
        sys.exit(0)
