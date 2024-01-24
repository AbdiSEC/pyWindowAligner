import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
from screeninfo import get_monitors
import json
import os
import subprocess

excluded_titles = ["Program Manager", "NVIDIA GeForce Overlay", "Windows Shell Experience Host", "Microsoft Text Input Application"]

def update_window_list():
    window_list.delete(0, tk.END)
    for window in gw.getAllWindows():
        if window.title and window.title not in excluded_titles:
            truncated_title = window.title[:34]
            window_list.insert(tk.END, truncated_title)

def move_selected_window():
    selection = window_list.curselection()
    if selection:
        full_title = [window.title for window in gw.getAllWindows() if window.title.startswith(window_list.get(selection[0]))][0]
        selected_window = gw.getWindowsWithTitle(full_title)[0]

        if not selected_window.isMinimized and selected_window.isMaximized:
            print("Error: Cannot move a minimized or maximized window.")
            return

        try:
            x = int(new_x_entry.get())
            y = int(new_y_entry.get())
            print(f"Moving window to X: {x}, Y: {y}")
        except ValueError:
            print("Error: Please enter valid numeric values for X and Y.")
            return

        selected_window.moveTo(x, y)
        print(f"Window moved to X: {x}, Y: {y}")


def move_up():
    move_window(0, -1)

def move_down():
    move_window(0, 1)

def move_left():
    move_window(-1, 0)

def move_right():
    move_window(1, 0)

def move_window(dx, dy):
    selection = window_list.curselection()
    if selection:
        title = window_list.get(selection[0])
        selected_window = [window for window in gw.getAllWindows() if window.title.startswith(title)][0]
        if selected_window:
            x, y = selected_window.left, selected_window.top
            selected_window.moveTo(x + dx, y + dy)

def update_coordinates():
    selection = window_list.curselection()
    if selection:
        try:
            full_title = [window.title for window in gw.getAllWindows() if window.title.startswith(window_list.get(selection[0]))][0]
            selected_window = gw.getWindowsWithTitle(full_title)[0]
            current_x_entry.delete(0, tk.END)
            current_y_entry.delete(0, tk.END)
            current_x_entry.insert(0, selected_window.left)
            current_y_entry.insert(0, selected_window.top)
            current_width_entry.delete(0, tk.END)
            current_height_entry.delete(0, tk.END)
            current_width_entry.insert(0, selected_window.width)
            current_height_entry.insert(0, selected_window.height)
        except AttributeError:
            print("Error: Unable to retrieve window dimensions.")


def update_window_size():
    selection = window_list.curselection()
    if selection:
        full_title = [window.title for window in gw.getAllWindows() if window.title.startswith(window_list.get(selection[0]))][0]
        selected_window = gw.getWindowsWithTitle(full_title)[0]

        try:
            width = int(new_width_entry.get())
            height = int(new_height_entry.get())
        except ValueError:
            print("Error: Please enter valid numeric values for Width and Height.")
            return

        selected_window.resizeTo(width, height)

def hide_selected_application():
    selection = window_list.curselection()
    if selection:
        full_title = [window.title for window in gw.getAllWindows() if window.title.startswith(window_list.get(selection[0]))][0]
        if full_title not in excluded_titles:
            excluded_titles.append(full_title)
        update_window_list()

def draw_monitors_and_windows(canvas, scale_factor=7):
    canvas.delete("all")
    monitors = get_monitors()
    min_x = min(monitor.x for monitor in monitors)
    min_y = min(monitor.y for monitor in monitors)

    for monitor in monitors:
        adjusted_x = (monitor.x - min_x) / scale_factor
        adjusted_y = (monitor.y - min_y) / scale_factor
        monitor_width = monitor.width / scale_factor
        monitor_height = monitor.height / scale_factor
        canvas.create_rectangle(adjusted_x, adjusted_y, adjusted_x + monitor_width, adjusted_y + monitor_height, fill="grey")
        canvas.create_text(adjusted_x + monitor_width / 2, adjusted_y + monitor_height / 2, text=f"{monitor.name}")

    colors = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "brown", "black", "white"]
    color_index = 0
    for window in gw.getAllWindows():
        if window.title and window.title not in excluded_titles:
            for monitor in monitors:
                if monitor.x <= window.left <= monitor.x + monitor.width and monitor.y <= window.top <= monitor.y + monitor.height:
                    window_x = (window.left - min_x) / scale_factor
                    window_y = (window.top - min_y) / scale_factor
                    window_width = window.width / scale_factor
                    window_height = window.height / scale_factor
                    color = colors[color_index % len(colors)]
                    color_index += 1
                    canvas.create_rectangle(window_x, window_y, window_x + window_width, window_y + window_height, outline=color)
                    canvas.create_text(window_x + window_width / 2, window_y + window_height / 2, text=window.title[:34], fill=color)
                    break

def show_monitors_and_windows():
    monitor_window = tk.Toplevel(root)
    monitor_window.title("Monitor and Windows Layout")
    monitors = get_monitors()
    total_width = max(monitor.x + monitor.width for monitor in monitors) - min(monitors, key=lambda m: m.x).x
    total_height = max(monitor.y + monitor.height for monitor in monitors) - min(monitors, key=lambda m: m.y).y
    scale_factor = 7
    canvas = tk.Canvas(monitor_window, width=total_width / scale_factor, height=total_height / scale_factor)
    canvas.pack()

    def update_layout():
        draw_monitors_and_windows(canvas, scale_factor)
        monitor_window.after(1000, update_layout)

    update_layout()

def save_config():
    config = {
        "applications": [],
        "excluded_titles": excluded_titles
    }
    for window in gw.getAllWindows():
        if window.title and window.title not in excluded_titles:
            config["applications"].append(
                {"name": window.title, "x": window.left, "y": window.top, "width": window.width,
                 "height": window.height})
    with open("config.json", "w") as file:
        json.dump(config, file)
    print("Configuration saved.")

def load_config():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
        global excluded_titles
        excluded_titles = config.get("excluded_titles", [])
        for app in config["applications"]:
            for window in gw.getAllWindows():
                if window.title == app["name"]:
                    window.moveTo(app["x"], app["y"])
                    window.resizeTo(app["width"], app["height"])
                    break
        print("Configuration loaded.")
        update_window_list()
    except FileNotFoundError:
        print("Config file not found.")

def open_file_location():
    file_path = os.path.realpath("config.json")
    folder_path = os.path.dirname(file_path)
    if os.name == 'nt':
        subprocess.Popen(['explorer', folder_path])
    elif os.name == 'posix':
        subprocess.Popen(['open', folder_path])
    else:
        subprocess.Popen(['xdg-open', folder_path])

button_width = 20

root = tk.Tk()
root.title("Window Aligner")
root.geometry("480x520")


style = ttk.Style()
style.theme_use('clam')


main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)


left_frame = ttk.Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="ns")


right_frame = ttk.Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="nsew")


refresh_button = ttk.Button(left_frame, text="Refresh Window List", command=update_window_list, width=button_width)
refresh_button.pack(pady=10, padx=5)

hide_button = ttk.Button(left_frame, text="Hide Application from List", command=hide_selected_application, width=button_width)
hide_button.pack(pady=10, padx=10)

monitor_button = ttk.Button(left_frame, text="Show Monitors", command=show_monitors_and_windows, width=button_width)
monitor_button.pack(pady=10, padx=10)

save_button = ttk.Button(left_frame, text="Save Config", command=save_config, width=button_width)
save_button.pack(pady=10, padx=10)

load_button = ttk.Button(left_frame, text="Load Config", command=load_config, width=button_width)
load_button.pack(pady=10, padx=10)

open_location_button = ttk.Button(left_frame, text="Open File Location", command=open_file_location, width=button_width)
open_location_button.pack(pady=10, padx=10)


window_list = tk.Listbox(right_frame, height=10, width=50)
window_list.grid(row=0, column=0, columnspan=2, pady=10, padx=10)
window_list.bind('<<ListboxSelect>>', lambda e: update_coordinates())


current_coord_frame = ttk.Frame(right_frame)
current_coord_frame.grid(row=1, column=0, columnspan=2, pady=10)

current_x_label = ttk.Label(current_coord_frame, text="Current X:")
current_x_label.grid(row=0, column=0, padx=10)
current_x_entry = ttk.Entry(current_coord_frame)
current_x_entry.grid(row=0, column=1, padx=10)

current_y_label = ttk.Label(current_coord_frame, text="Current Y:")
current_y_label.grid(row=1, column=0, padx=10)
current_y_entry = ttk.Entry(current_coord_frame)
current_y_entry.grid(row=1, column=1, padx=10)


new_coord_frame = ttk.Frame(right_frame)
new_coord_frame.grid(row=2, column=0, columnspan=2, pady=10)

new_x_label = ttk.Label(new_coord_frame, text="New X:")
new_x_label.grid(row=0, column=0, padx=10)
new_x_entry = ttk.Entry(new_coord_frame)
new_x_entry.grid(row=0, column=1, padx=10)

new_y_label = ttk.Label(new_coord_frame, text="New Y:")
new_y_label.grid(row=1, column=0, padx=10)
new_y_entry = ttk.Entry(new_coord_frame)
new_y_entry.grid(row=1, column=1, padx=10)

move_button = ttk.Button(new_coord_frame, text="Move Window", command=move_selected_window, width=button_width)
move_button.grid(row=2, column=0, columnspan=2, pady=10)

current_size_frame = ttk.Frame(right_frame)
current_size_frame.grid(row=3, column=0, columnspan=2, pady=10)

current_width_label = ttk.Label(current_size_frame, text="Current Width:")
current_width_label.grid(row=0, column=0, padx=10)
current_width_entry = ttk.Entry(current_size_frame)
current_width_entry.grid(row=0, column=1, padx=10)

current_height_label = ttk.Label(current_size_frame, text="Current Height:")
current_height_label.grid(row=1, column=0, padx=10)
current_height_entry = ttk.Entry(current_size_frame)
current_height_entry.grid(row=1, column=1, padx=10)

new_size_frame = ttk.Frame(right_frame)
new_size_frame.grid(row=4, column=0, columnspan=2, pady=10)

new_width_label = ttk.Label(new_size_frame, text="New Width:")
new_width_label.grid(row=0, column=0, padx=10)
new_width_entry = ttk.Entry(new_size_frame)
new_width_entry.grid(row=0, column=1, padx=10)

new_height_label = ttk.Label(new_size_frame, text="New Height:")
new_height_label.grid(row=1, column=0, padx=10)
new_height_entry = ttk.Entry(new_size_frame)
new_height_entry.grid(row=1, column=1, padx=10)

style.configure("square.buttons", width=5, height=5)

update_size_button = ttk.Button(new_size_frame, text="Update Window Size", command=update_window_size, width=button_width)
update_size_button.grid(row=2, column=0, columnspan=2, pady=10)

up_button = ttk.Button(new_coord_frame, text="Up", command=move_up)
up_button.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

down_button = ttk.Button(new_coord_frame, text="Down", command=move_down)
down_button.grid(row=5, column=1, sticky="nsew", padx=5, pady=5)

left_button = ttk.Button(new_coord_frame, text="Left", command=move_left)
left_button.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

right_button = ttk.Button(new_coord_frame, text="Right", command=move_right)
right_button.grid(row=4, column=2, sticky="nsew", padx=5, pady=5)



update_window_list()


root.mainloop()