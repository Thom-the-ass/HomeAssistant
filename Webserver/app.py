import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# This Json file is resposible for the storeage of devices
DEVICE_FILE = "devices.json"

# Toggles lights on and off
# Note to self, this essentially just accesses this url and, update the state of the light
@app.route('/toggle_light', methods=['POST'])
def toggle_light():
    data = request.json
    #Gets the IP address of the device that it needs to control
    ip_address = data.get("ip_address")
    # Gets the state that it needs to be in ("Off or on")
    state = data.get("state")

    # Sending an http request (ie going to the route which will turn the light on or off)
    try:
        # Can clean this up a bit
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
# This currently has a bug where it will delete all items of the same name - slightly problematic, might need to add a primary key
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

# Raw view to see all the devices, this is not nicely set up and kinda feels redundant, so might need to make this a hidden page
@app.route('/devices')
def devices():
    try:
        with open(DEVICE_FILE, "r") as file:
            devices = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        devices = []

    # Group devices first by location, then by category
    grouped_devices = {}
    for device in devices:
        location = device["location"]
        category = device["category"]

        if location not in grouped_devices:
            grouped_devices[location] = {}

        if category not in grouped_devices[location]:
            grouped_devices[location][category] = []

        grouped_devices[location][category].append(device)

    return render_template('devices.html', grouped_devices=grouped_devices)

# Toggles device state - only used in the device menu - might get rid of this
@app.route('/toggle_device', methods=['POST'])
def toggle_device():
    data = request.json
    ip_address = data.get("ip_address")
    category = data.get("category")

    # Define different endpoints for various device categories
    action_endpoint = {
        "Lights": "/light/toggle",
        "Security": "/security/toggle",
        "Climate": "/climate/toggle",
        "Other": "/device/toggle"
    }

    try:
        import requests
        requests.get(f"http://{ip_address}{action_endpoint.get(category, '/device/toggle')}")
        return jsonify({"status": "success", "message": f"{category} device at {ip_address} toggled."})
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to send command"}), 500


# The index page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)