# =========================================================================
# Kabot-1 Main Project Entry Point
# =========================================================================
# This file serves as the primary entry point for the Kabot-1 flight software.
# During the mission, it would typically launch the logger scripts.
# For post-flight analysis, use 'mission_control.sh'.

import sys
import os

# Set the path to the logger script (for mission use)
LOGGER_SCRIPT = os.path.join("src", "logger", "dht_logger.py")

def main():
    """Launches the core flight logger when run on the RPi."""
    
    print("=================================================")
    print(" KABOT I - FLIGHT SOFTWARE (DHT Logger Mode) ")
    print("=================================================")
    
    # This block would execute the flight logger on the Raspberry Pi
    if os.path.exists(LOGGER_SCRIPT):
        print(f"To start the mission logger, run: python3 {LOGGER_SCRIPT}")
        
    # This message helps the user during post-flight analysis on a PC
    else:
        print(f"Logger script not found at expected path: {LOGGER_SCRIPT}")

    print("\nFor post-flight analysis, use the 'mission_control.sh' script in the root directory.")

if __name__ == "__main__":
    main()

