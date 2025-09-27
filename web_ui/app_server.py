from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent  # project root
DATA = BASE / "src" / "logger" / "data"
CHARTS = BASE / "src" / "charts"

app = Flask(__name__, template_folder="templates")

# --- Existing routes ---
@app.route("/")
def index():
    # pass latest log lines into dashboard.html
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

@app.route("/chart/<filename>")
def chart(filename):
    return send_from_directory(CHARTS, filename)

# --- New generator routes (replace blackbox.sh) ---
@app.route("/generate/dht")
def generate_dht():
    try:
        subprocess.run(["python3", "src/plotter/dht_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/dht_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/generate/mpu")
def generate_mpu():
    try:
        subprocess.run(["python3", "src/plotter/mpu6050_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/mpu_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/generate/sound")
def generate_sound():
    try:
        subprocess.run(["python3", "src/plotter/sound_plotter.py"], check=True)
        return jsonify({"status": "ok", "chart": "/chart/sound_chart.svg"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Entrypoint ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
