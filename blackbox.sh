#!/bin/bash
# =========================================================================
# Kabot-1 Blackbox Analyzer (Post-Flight Data Analysis Launcher)
# =========================================================================

PYTHON_EXECUTABLE="python3"

# Define script and chart paths
DHT_PLOTTER_SCRIPT="src/plotter/dht_plotter.py"
MPU_PLOTTER_SCRIPT="src/plotter/mpu6050_plotter.py"
SOUND_PLOTTER_SCRIPT="src/plotter/sound_plotter.py"
DHT_CHART_PATH="src/charts/dht_chart.svg"
MPU_CHART_PATH="src/charts/mpu_chart.svg"
SOUND_CHART_PATH="src/charts/sound_chart.svg"

check_dependencies() {
    if ! command -v $PYTHON_EXECUTABLE &> /dev/null; then
        echo "Error: 'python3' not found."
        exit 1
    fi
    if ! $PYTHON_EXECUTABLE -c "import matplotlib; import scipy" &> /dev/null; then
        echo "Error: Missing matplotlib/scipy. Install with: pip install matplotlib scipy numpy"
        exit 1
    fi
}

generate_dht_chart() {
    echo "=== Generating DHT Chart ==="
    $PYTHON_EXECUTABLE $DHT_PLOTTER_SCRIPT
}

generate_mpu_chart() {
    echo "=== Generating MPU Chart ==="
    $PYTHON_EXECUTABLE $MPU_PLOTTER_SCRIPT
}

generate_sound_chart() {
    echo "=== Generating Sound Chart ==="
    $PYTHON_EXECUTABLE $SOUND_PLOTTER_SCRIPT
}

view_chart() {
    echo "Which chart to view? [D/M/S]"
    read -r choice
    case "$choice" in
        D|d) echo "Last DHT chart: $DHT_CHART_PATH" ;;
        M|m) echo "Last MPU chart: $MPU_CHART_PATH" ;;
        S|s) echo "Last Sound chart: $SOUND_CHART_PATH" ;;
        *) echo "Invalid choice." ;;
    esac
}

# --- Main Execution ---
check_dependencies

# Non-interactive mode (argument passed)
if [ -n "$1" ]; then
    case $1 in
        1) generate_dht_chart ;;
        2) generate_mpu_chart ;;
        3) generate_sound_chart ;;
        4) view_chart ;;
        5) echo "Exiting." ; exit 0 ;;
        *) echo "Invalid option: $1" ; exit 1 ;;
    esac
    exit 0
fi

# Interactive menu loop
while true; do
    clear
    echo "================================================="
    echo " KABOT-1 BLACKBOX ANALYZER (Post-Flight Analysis)"
    echo "================================================="
    echo " 1) Generate Final DHT Chart"
    echo " 2) Generate Final MPU-6050 Chart"
    echo " 3) Generate Sound Chart"
    echo " 4) View Last Generated Chart"
    echo " 5) Exit"
    echo "================================================="
    read -p "Enter choice [1-5]: " choice
    case $choice in
        1) generate_dht_chart ;;
        2) generate_mpu_chart ;;
        3) generate_sound_chart ;;
        4) view_chart ;;
        5) echo "Exiting." ; exit 0 ;;
        *) echo "Invalid option." ;;
    esac
    read -p "Press Enter to continue..."
done
