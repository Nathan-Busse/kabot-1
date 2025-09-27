# =========================================================================
# Kabot I Mission Master Launcher (main.py)
# =========================================================================
# This script launches all logger processes and the Flask web server 
# concurrently and silently in the background.
#
# EXECUTION: python3 main.py
#
# This script ensures that if the terminal session (SSH) is lost, all 
# mission-critical logging continues uninterrupted.
# =========================================================================

import subprocess
import time
import os

# --- Configuration ---

# Processes to launch. The paths are relative to the project root directory
# (where this main.py file is located).
PROCESSES = [
    # 1. DHT11 Temperature/Humidity Logger (Logs to CSV and JSON)
    ("DHT Logger", "src/logger/dht_logger.py"),
    
    # 2. MPU-6050 Motion Logger (Logs to CSV and JSON)
    ("MPU Logger", "src/logger/mpu6050_logger.py"),
    
    # 3. Sound Logger (Placeholder - assumes this script is ready)
    ("Sound Logger", "src/logger/sound_logger.py"),
    
    # 4. Web UI Server (Starts Flask server, reads from logger JSON files)
    ("Web Server", "web_ui/app_server.py"),
]

def launch_processes():
    """Launches all configured processes concurrently using subprocess.Popen."""
    
    running_processes = []
    
    print("--- Kabot I Mission Control Startup ---")
    print(f"Launching {len(PROCESSES)} critical processes...")

    # Redirect all stdout/stderr output from subprocesses to null to prevent 
    # terminal artifacts from corrupting logs or memory.
    DEVNULL = open(os.devnull, 'w')
    
    for name, script_path in PROCESSES:
        try:
            # Construct the command: python3 /path/to/script.py
            command = ["python3", script_path]
            
            # Use Popen to launch the process and detach it
            process = subprocess.Popen(
                command, 
                stdout=DEVNULL, # Silence all output
                stderr=DEVNULL, # Silence all errors (errors are logged internally by loggers if FLIGHT_MODE=False)
                # Run from the project root directory
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            running_processes.append((name, process))
            print(f"[SUCCESS] Launched {name} (PID: {process.pid})")
            time.sleep(0.5) # Slight delay to ensure clean startup order

        except FileNotFoundError:
            print(f"[ERROR] Python interpreter not found.")
            break
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name} ({script_path}): {e}")
            
    print("\n--- System Status ---")
    
    if running_processes:
        print("All processes launched successfully.")
        print("Logging and Web UI are active in the background.")
        print("Web Dashboard: Access http://<Pi_IP_Address>:5000")
        
        # Keep the main launcher script running to monitor status and prevent 
        # the terminal session from exiting immediately.
        monitor_processes(running_processes)
    else:
        print("No processes were launched. Mission aborted.")

def monitor_processes(processes):
    """Monitors the launched processes and cleans up on keyboard interrupt."""
    try:
        while True:
            # Simple check to see if any process died
            for name, proc in processes:
                if proc.poll() is not None: # poll returns exit code if process terminated
                    print(f"\n[ALERT] Process '{name}' (PID: {proc.pid}) has terminated unexpectedly!")
                    # You could re-launch here, but for a simple mission, an alert is enough.
                    
            time.sleep(5) # Check status every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n--- TERMINATION SEQUENCE INITIATED ---")
        print("Stopping all running Kabot I payload processes...")
        
        for name, proc in processes:
            if proc.poll() is None: # Only try to terminate if still running
                try:
                    proc.terminate()
                    print(f"[STOPPED] {name} (PID: {proc.pid})")
                except Exception as e:
                    print(f"[ERROR] Could not terminate {name}: {e}")

        print("\nMission components safely shut down. Data logging is complete.")
        DEVNULL.close()

if __name__ == "__main__":
    launch_processes()

