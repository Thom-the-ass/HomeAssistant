import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DEVICE_FILE = "devices.json"

# Toggles lights on and off
@app.route('/toggle_light', methods=['POST'])
def toggle_light():
    data = request.json
    #Gets the IP address of the device that it needs to control
    ip_address = data.get("ip_address")
    # Gets the state that it needs to be in ("Off or on")
    state = data.get("state")

    # Sending an http request (ie going to the route which will turn the light on or off)
    try:
        import requests
        requests.get(f"http://{ip_address}/light/{state}")
        return jsonify({"status": "success", "message": f"Light at {ip_address} set to {state}"})
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to send command"}), 500

#The lights page - reads in the JSON file to show all the lights
@app.route('/lights')
def lights():
    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        devices = []

    # Filter devices by category "Lights"
    light_devices = [device for device in devices if device["category"] == "Lights"]

    # Group devices by location
    grouped_devices = {}
    for device in light_devices:
        grouped_devices.setdefault(device["location"], []).append(device)

    return render_template('lights.html', grouped_devices=grouped_devices)

# This is for the configuring new device

# Deleting an item
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

# Adding an item
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

# Render the getting started page - might change this name to devices
@app.route('/get_started')
def get_started():
    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        devices = []  # Handle missing or corrupted JSON file

    return render_template('get_started.html', devices=devices)

# The index page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)