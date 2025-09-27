from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import pathlib

# Project root
BASE = pathlib.Path(__file__).resolve().parent.parent
CHARTS = BASE / "src" / "charts"
BLACKBOX = BASE / "blackbox.sh"

app = Flask(__name__, template_folder="templates")

# --- Dashboard ---
@app.route("/")
def index():
    return render_template("dashboard.html")

# --- Serve charts ---
@app.route("/chart/<filename>")
def chart(filename):
    return send_from_directory(CHARTS, filename)

# --- Blackbox wrapper routes ---
@app.route("/blackbox/<choice>")
def run_blackbox(choice):
    # Map web choices to blackbox.sh menu numbers
    mapping = {
        "dht": "1",
        "mpu": "2",
        "sound": "3",
        "view": "4"
    }
    opt = mapping.get(choice)
    if not opt:
        return jsonify({"status": "error", "message": "Invalid choice"}), 400

    try:
        # Run blackbox.sh with simulated input
        result = subprocess.run(
            [str(BLACKBOX)],
            input=f"{opt}\n".encode(),
            cwd=str(BASE),
            capture_output=True,
            check=True
        )
        return jsonify({
            "status": "ok",
            "output": result.stdout.decode()
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": e.stderr.decode() or str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
