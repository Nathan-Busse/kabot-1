#!/bin/bash
DATA_DIR="data"

echo "Available data files:"
select file in "$DATA_DIR"/*.txt; do
    if [[ -n "$file" ]]; then
        echo "Plotting $file..."
       ./src/plotter/dht_plotter.py "$file"
        break
    else
        echo "Invalid choice."
    fi
done
