#!/bin/bash
DATA_DIR="data"

echo "Available data files:"
select file in "$DATA_DIR"/*.txt; do
    if [[ -n "$file" ]]; then
        echo "Plotting $file..."
        ./src/dhp_plot_data.py "$file"
        break
    else
        echo "Invalid choice."
    fi
done
