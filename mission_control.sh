# =========================================================================
# Kabot-1 Mission Control and Post-Flight Data Analysis Launcher
# =========================================================================
# This script provides a simple menu interface for managing post-flight
# tasks, specifically running the resource-intensive data plotting script
# and viewing the results.
#
# NOTE: This script is intended to be run on the ground station (PC)
# after the mission data has been transferred from the Kabot-1 payload.
# =========================================================================

PYTHON_EXECUTABLE="python3"
PLOTTER_SCRIPT="src/plotter/dht_plotter.py"
CHART_PATH="src/charts/chart.svg"

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
    echo " Starting DHT Chart Generation (Post-Flight Analysis)"
    echo "================================================="
    
    # Run the Python plotting script
    $PYTHON_EXECUTABLE $PLOTTER_SCRIPT
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "Chart generation successful! File saved to $CHART_PATH"
    else
        echo ""
        echo "Chart generation failed. Check the error messages above."
    fi
}

# Function to view the generated chart
view_chart() {
    if [ ! -f $CHART_PATH ]; then
        echo "Error: Chart file not found at $CHART_PATH."
        echo "Please run option 1 first to generate the chart."
        return
    fi
    
    echo "Opening $CHART_PATH..."
    
    # Use 'open' on macOS/Windows Subsystem for Linux (WSL), 'xdg-open' on most Linux distributions
    # This command attempts to open the file with the default viewer.
    if command -v xdg-open &> /dev/null; then
        xdg-open $CHART_PATH
    elif command -v open &> /dev/null; then
        open $CHART_PATH
    else
        echo "Warning: Could not find 'xdg-open' or 'open' command."
        echo "Please open the file manually: $CHART_PATH"
    fi
}

# Main menu loop
show_menu() {
    clear
    echo "================================================="
    echo " KABOT-1 MISSION CONTROL (Post-Flight Analysis)"
    echo "================================================="
    echo " 1) Generate Final DHT Chart (Runs $PLOTTER_SCRIPT)"
    echo " 2) View Last Generated Chart ($CHART_PATH)"
    echo " 3) Exit Mission Control"
    echo "================================================="
}

# --- Main Execution ---
check_dependencies

while true; do
    show_menu
    read -p "Enter choice [1-3]: " choice
    case $choice in
        1) generate_dht_chart ;;
        2) view_chart ;;
        3) echo "Exiting. Good luck with your analysis!" ; exit 0 ;;
        *) echo "Invalid option. Please try again." ;;
    esac
    echo ""
    read -p "Press Enter to continue..."
done

