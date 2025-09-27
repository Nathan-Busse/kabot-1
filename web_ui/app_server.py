from flask import Flask, render_template, send_from_directory, jsonify
import pathlib

app = Flask(__name__)

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "src" / "logger" / "data"
CHARTS = BASE / "src" / "charts"

def tail(filepath, n=1):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-n:]]
    except FileNotFoundError:
        return []

@app.route("/")
def dashboard():
    dht_last = tail(DATA / "DHT11.txt", 1)
    mpu_last = tail(DATA / "MPU6050.txt", 1)
    sound_last = tail(DATA / "sound.txt", 1)  # optional if you have this log

    return render_template(
        "dashboard.html",
        dht_last=dht_last[0] if dht_last else "No data",
        mpu_last=mpu_last[0] if mpu_last else "No data",
        sound_last=sound_last[0] if sound_last else "No data",
    )

@app.route("/chart/<filename>")
def chart(filename):
    return send_from_directory(CHARTS, filename)

@app.route("/api/latest")
def api_latest():
    return jsonify({
        "dht": tail(DATA / "DHT11.txt", 1),
        "mpu": tail(DATA / "MPU6050.txt", 1),
        "sound": tail(DATA / "sound.txt", 1),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
