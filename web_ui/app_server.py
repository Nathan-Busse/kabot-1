# web_ui/app_server.py
from flask import Flask, render_template, jsonify, send_from_directory
import pathlib

app = Flask(__name__)

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "src" / "logger" / "data"
CHARTS = BASE / "src" / "charts"

def tail(filepath, n=1):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            if not lines:
                return []
            return [line.strip() for line in lines[-n:]]
    except FileNotFoundError:
        return []

def parse_dht(line):
    # Adjust to your format (e.g., "timestamp,temp,humidity")
    try:
        parts = [p.strip() for p in line.split(",")]
        return {
            "timestamp": parts[0],
            "temp": float(parts[1]),
            "humidity": float(parts[2]),
        }
    except Exception:
        return {"raw": line}

def parse_mpu(line):
    # Adjust to your format; example: ts,ax,ay,az,gx,gy,gz
    try:
        parts = [p.strip() for p in line.split(",")]
        return {
            "timestamp": parts[0],
            "ax": float(parts[1]),
            "ay": float(parts[2]),
            "az": float(parts[3]),
            "gx": float(parts[4]),
            "gy": float(parts[5]),
            "gz": float(parts[6]),
        }
    except Exception:
        return {"raw": line}

@app.route("/")
def dashboard():
    dht_last = tail(DATA / "DHT11.txt", 1)
    mpu_last = tail(DATA / "MPU6050.txt", 1)
    dht = parse_dht(dht_last[0]) if dht_last else {}
    mpu = parse_mpu(mpu_last[0]) if mpu_last else {}
    return render_template("dashboard.html", dht=dht, mpu=mpu)

@app.route("/chart/<name>")
def chart(name):
    return send_from_directory(CHARTS, name)

@app.route("/api/latest")
def api_latest():
    dht_last = tail(DATA / "DHT11.txt", 1)
    mpu_last = tail(DATA / "MPU6050.txt", 1)
    return jsonify({
        "dht": parse_dht(dht_last[0]) if dht_last else None,
        "mpu": parse_mpu(mpu_last[0]) if mpu_last else None,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

