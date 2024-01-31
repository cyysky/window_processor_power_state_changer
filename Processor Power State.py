import tkinter as tk
from tkinter import ttk
import subprocess
import re

# Define a list of percentages
percentages = [30, 60, 100]
current_index = [0]  # Use a list for mutability in nested function


# Function to get the GUID of the currently active power plan
def get_active_plan_guid():
    result = subprocess.run(["powercfg", "-getactivescheme"], capture_output=True, text=True)
    match = re.search(r'Power Scheme GUID: ([a-f0-9-]+)  \(.*\)', result.stdout)
    if match:
        return match.group(1)
    else:
        raise Exception("Failed to get the active power plan GUID")

# Function to get the current processor power management value
def get_current_processor_power_value(plan_guid, setting_name):
    # Query the current setting value
    result = subprocess.run(["powercfg", "-q", plan_guid, "SUB_PROCESSOR", setting_name], capture_output=True, text=True)
    
    # Adjust the regular expression to match the hexadecimal format
    match = re.search(r'Current AC Power Setting Index: 0x([\da-fA-F]+)', result.stdout)
    if match:
        # Convert the hexadecimal value to an integer, then to a percentage
        current_value = int(match.group(1), 16)
        return current_value
    else:
        raise Exception("Failed to get current power setting value")

def set_processor_power(plan_name, setting_name, value):
    # Get the GUID of the power plan
    result = subprocess.run(["powercfg", "-l"], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    plan_guid = None
    for line in lines:
        if plan_name in line:
            plan_guid = line.split()[3]
            break

    if not plan_guid:
        raise Exception("Power plan not found")

    # Set the processor power management to the desired value
    subprocess.run(["powercfg", "-setacvalueindex", plan_guid, "SUB_PROCESSOR", setting_name, str(value)])
    subprocess.run(["powercfg", "-setdcvalueindex", plan_guid, "SUB_PROCESSOR", setting_name, str(value)])
    subprocess.run(["powercfg", "-setactive", plan_guid])

    print(f"Set {setting_name} to {value}% for '{plan_name}' plan")

def update_power_setting():
    global current_index
    current_index[0] = (current_index[0] + 1) % len(percentages)
    new_percentage = percentages[current_index[0]]
    set_processor_power("Balanced", "PROCTHROTTLEMAX", new_percentage)
    label.config(text=f"Current Setting: {new_percentage}%")

def start_move(event):
    app.x = event.x
    app.y = event.y

def stop_move(event):
    app.x = None
    app.y = None

def on_motion(event):
    deltax = event.x - app.x
    deltay = event.y - app.y
    x = app.winfo_x() + deltax
    y = app.winfo_y() + deltay
    app.geometry(f"+{x}+{y}")

def close_app():
    app.destroy()
    
# Tkinter GUI setup
app = tk.Tk()
app.title("Processor Power Management")

# Remove the title bar and make the window borderless
app.overrideredirect(True)

# Bind mouse events for dragging the window
app.bind('<Button-1>', start_move)
app.bind('<ButtonRelease-1>', stop_move)
app.bind('<B1-Motion>', on_motion)

# Add a button to change the power setting
change_button = ttk.Button(app, text="Change Power Setting", command=update_power_setting)
change_button.pack()

# Get the current active plan GUID and current setting
active_plan_guid = get_active_plan_guid()
current_value = get_current_processor_power_value(active_plan_guid, "PROCTHROTTLEMAX")

# Add a label to show the current setting
label = tk.Label(app, text=f"Current Setting: {current_value}%")
label.pack()

# Add a close button
close_button = ttk.Button(app, text="Close", command=close_app)
close_button.pack()
# Run the application
app.mainloop()