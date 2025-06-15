import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DEVICE_FILE = "devices.json"

@app.route('/delete_device', methods=['POST'])
def delete_device():
    device_name = request.json.get("name")

    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Device list not found"}), 400

    # Remove the device with the matching name
    devices = [device for device in devices if device["name"] != device_name]

    with open(DEVICE_FILE, "w") as file:
        json.dump(devices, file, indent=4)

    return jsonify({"status": "success"}), 200

@app.route('/get_started')
def get_started():
    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        devices = []  # Handle missing or corrupted JSON file

    return render_template('get_started.html', devices=devices)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/save_device', methods=['POST'])
def save_device():
    device_data = request.get_json()
    
    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        devices = []

    devices.append(device_data)

    with open(DEVICE_FILE, "w") as file:
        json.dump(devices, file, indent=4)

    return jsonify({"status": "success"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)