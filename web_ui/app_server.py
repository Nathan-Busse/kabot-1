from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent  # project root
DATA = BASE / "src" / "logger" / "data"
CHARTS = BASE / "src" / "charts"

app = Flask(__name__, template_folder="templates")

# --- Dashboard ---
@app.route("/")
def index():
    def tail(path, n=1):
        try:
            with open(path, "r") as f:
                return f.readlines()[-n:][0].strip()
        except Exception:
            return "No data"

    return render_template(
        "dashboard.html",
        dht_last=tail(DATA / "DHT11.txt"),
        mpu_last=tail(DATA / "MPU6050.txt"),
        sound_last=tail(DATA / "sound.txt"),
    )

# --- Serve charts ---
@app.route("/chart/<filename>")
def chart(filename):
    return send_from_directory(CHARTS, filename)

# --- Blackbox Analyzer routes ---
@app.route("/blackbox/dht")
def blackbox_dht():
    try:
        subprocess.run(["python3", "src/plotter/dht_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/dht_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/blackbox/mpu")
def blackbox_mpu():
    try:
        subprocess.run(["python3", "src/plotter/mpu6050_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/mpu_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/blackbox/sound")
def blackbox_sound():
    try:
        subprocess.run(["python3", "src/plotter/sound_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/sound_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
