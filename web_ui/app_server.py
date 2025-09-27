import subprocess
import pathlib
from flask import Flask, render_template, jsonify, send_from_directory

BASE = pathlib.Path(__file__).resolve().parent.parent  # project root
CHARTS = BASE / "src" / "charts"
BLACKBOX = BASE / "blackbox.sh"

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/chart/<filename>")
def chart(filename):
    return send_from_directory(CHARTS, filename)

# --- Blackbox wrapper routes ---
@app.route("/blackbox/<sensor>")
def run_blackbox(sensor):
    # Map sensor to menu option number in blackbox.sh
    options = {"dht": "1", "mpu": "2", "sound": "3"}
    choice = options.get(sensor)
    if not choice:
        return jsonify({"status": "error", "message": "Invalid sensor"}), 400

    try:
        # Run blackbox.sh with the choice as input
        result = subprocess.run(
            [str(BLACKBOX)],
            input=f"{choice}\n".encode(),
            cwd=str(BASE),
            check=True,
            capture_output=True
        )
        return jsonify({
            "status": "ok",
            "chart": f"/chart/{sensor}_chart.svg",
            "output": result.stdout.decode()
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": e.stderr.decode() or str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
