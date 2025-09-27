# =========================================================================
# Kabot-1 Blackbox Analyzer (Post-Flight Data Analysis Launcher)
# =========================================================================
# This script provides a simple menu interface for managing post-flight
# tasks, specifically running the resource-intensive data plotting scripts
# and viewing the results.
#
# NOTE: This script is intended to be run on the ground station (PC)
# after the mission data has been transferred from the Kabot-1 payload.
# =========================================================================

PYTHON_EXECUTABLE="python3"

# Define script and chart paths
DHT_PLOTTER_SCRIPT="src/plotter/dht_plotter.py"
MPU_PLOTTER_SCRIPT="src/plotter/mpu6050_plotter.py"
SOUND_PLOTTER_SCRIPT="src/plotter/sound_plotter.py" # NEW: Sound Plotter Script
DHT_CHART_PATH="src/charts/chart.svg"
MPU_CHART_PATH="src/charts/mpu6050_chart.svg"
SOUND_CHART_PATH="src/charts/sound_chart.svg" # NEW: Sound Chart Path

# Function to check for required dependencies
check_dependencies() {
    # Check if python3 is available
    if ! command -v $PYTHON_EXECUTABLE &> /dev/null; then
        echo "Error: 'python3' command not found."
        echo "Please ensure Python 3 is installed and in your PATH."
        exit 1
    fi
    # Check for Matplotlib/SciPy by attempting to import them
    if ! $PYTHON_EXECUTABLE -c "import matplotlib; import scipy" &> /dev/null; then
        echo "Error: Matplotlib or SciPy are not installed."
        echo "Please install required libraries: pip install matplotlib scipy numpy"
        exit 1
    fi
}

# Function to run the DHT Plotter script
generate_dht_chart() {
    echo ""
    echo "================================================="
    echo " Starting DHT Chart Generation (Temp/Hum)"
    echo "================================================="
    $PYTHON_EXECUTABLE $DHT_PLOTTER_SCRIPT
    if [ $? -eq 0 ]; then
        echo ""
        echo "Chart generation successful! File saved to $DHT_CHART_PATH"
    else
        echo ""
        echo "Chart generation failed. Check the error messages above."
    fi
}

# Function to run the MPU Plotter script
generate_mpu_chart() {
    echo ""
    echo "================================================="
    echo " Starting MPU-6050 Chart Generation (Motion)"
    echo "================================================="
    $PYTHON_EXECUTABLE $MPU_PLOTTER_SCRIPT
    if [ $? -eq 0 ]; then
        echo ""
        echo "Chart generation successful! File saved to $MPU_CHART_PATH"
    else
        echo ""
        echo "Chart generation failed. Check the error messages above."
    fi
}

# NEW: Function to run the Sound Plotter script
generate_sound_chart() {
    echo ""
    echo "================================================="
    echo " Starting Sound Chart Generation (Waveform/FFT)"
    echo "================================================="
    # Note: The sound plotter will likely require 'scipy.io.wavfile' and a custom 
    # Python script if raw PCM data is logged. We'll assume the script is ready 
    # to run when this menu option is selected.
    $PYTHON_EXECUTABLE $SOUND_PLOTTER_SCRIPT
    if [ $? -eq 0 ]; then
        echo ""
        echo "Chart generation successful! File saved to $SOUND_CHART_PATH"
    else
        echo ""
        echo "Chart generation failed. Check the error messages above."
    fi
}


# Function to view the generated chart
view_chart() {
    CHART_TO_VIEW=""
    echo "Which chart would you like to view?"
    echo "  [D] DHT (Temperature/Humidity)"
    echo "  [M] MPU-6050 (Motion/G-Force)"
    echo "  [S] Sound (Waveform/FFT) - Coming Soon!"
    read -p "Enter choice [D/M/S]: " view_choice
    
    view_choice=$(echo "$view_choice" | tr '[:lower:]' '[:upper:]') # Convert to uppercase
    
    case "$view_choice" in
        "D")
            CHART_TO_VIEW=$DHT_CHART_PATH
            ;;
        "M")
            CHART_TO_VIEW=$MPU_CHART_PATH
            ;;
        "S")
            CHART_TO_VIEW=$SOUND_CHART_PATH
            ;;
        *)
            echo "Invalid choice."
            return
            ;;
    esac
    
    if [ ! -f "$CHART_TO_VIEW" ]; then
        echo "Error: Chart file not found at $CHART_TO_VIEW."
        echo "Please run the appropriate generation option first (Menu options 1 or 2)."
        return
    fi
    
    echo "Opening $CHART_TO_VIEW..."
    
    # Use 'open' on macOS/WSL, 'xdg-open' on most Linux distributions
    if command -v xdg-open &> /dev/null; then
        xdg-open "$CHART_TO_VIEW"
    elif command -v open &> /dev/null; then
        open "$CHART_TO_VIEW"
    else
        echo "Warning: Could not find 'xdg-open' or 'open' command."
        echo "Please open the file manually: $CHART_TO_VIEW"
    fi
}

# Main menu loop
show_menu() {
    clear
    echo "================================================="
    echo " KABOT-1 BLACKBOX ANALYZER (Post-Flight Analysis)"
    echo "================================================="
    echo " 1) Generate Final DHT Chart (Temp/Hum)"
    echo " 2) Generate Final MPU-6050 Chart (Motion)"
    echo " 3) Generate Sound Chart (Waveform/FFT) - Needs Setup"
    echo "-------------------------------------------------"
    echo " 4) View Last Generated Chart"
    echo " 5) Exit Blackbox Analyzer"
    echo "================================================="
}

# --- Main Execution ---
check_dependencies

while true; do
    show_menu
    read -p "Enter choice [1-5]: " choice
    case $choice in
        1) generate_dht_chart ;;
        2) generate_mpu_chart ;;
        3) generate_sound_chart ;; # NEW: Added call for sound chart
        4) view_chart ;;
        5) echo "Exiting. Good luck with your analysis!" ; exit 0 ;;
        *) echo "Invalid option. Please try again." ;;
    esac
    echo ""
    read -p "Press Enter to continue..."
done

