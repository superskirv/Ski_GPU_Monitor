import json, os
import tkinter as tk
from tkinter import ttk, simpledialog
from screeninfo import get_monitors
from ski_gpu_monitor import Ski_GPU_Monitor

SKI_GPU_GUI_version = "1.0.3"

script_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_directory, "config.json")

class SKI_GPU_GUI:
    def __init__(self, root):
        self.gpu_monitor = Ski_GPU_Monitor()
        self.gpu_monitor.update_gpu_stats()

        self.config = self.load_config()
        self.root = root
        self.root.title("SKI GPU INFO")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        self.position = ""
        self.show_all_gpu = "<" # '<' = True, '>' = False
        self.updating = False
        self.refresh_time = self.config['refresh_time'] * 1000

        self.create_widgets()
        self.update_info()

    def create_widgets(self):
        self.root.configure(bg="black")

        self.buttons_frame = tk.Frame(self.root, bg='black')
        self.buttons_frame.grid(row=0, column=0, sticky='ew')
        self.buttons_frame.columnconfigure(0, weight=1)

        # Create a style for the checkbox
        style = ttk.Style()
        style.configure("Black.TCheckbutton", background="black", foreground="white")

        # Create a checkbox at position 0,0 without any text
        quit_checkbox = ttk.Checkbutton(self.buttons_frame, text="", style="Black.TCheckbutton", command=self.toggle_exit)
        quit_checkbox.grid(row=0, column=0, sticky='w')
        position_checkbox = ttk.Checkbutton(self.buttons_frame, text="", style="Black.TCheckbutton", command=self.toggle_position)
        position_checkbox.grid(row=0, column=2, sticky='e')
        self.expand_label = ttk.Label(self.buttons_frame, text=self.show_all_gpu, foreground="white", background="black")
        self.expand_label.grid(row=0, column=1, sticky='e')

        # Create a label for each GPU ID
        for gpu_id in range(self.gpu_monitor.total_gpus):
            ttk.Label(self.root, text=f"GPU {gpu_id}", foreground="white", background="black").grid(row=0, column=gpu_id+1)

        # Create labels for GPU stats
        stats_labels = ['Usage(%)', 'Temp(°C)', 'PwrUse(W)', 'MaxPwr(W)', 'vRAM Used', 'vRAM Max']
        self.gpu_stat_labels = []
        if self.show_all_gpu == "<":
            for row, stat_label in enumerate(stats_labels, start=1):
                ttk.Label(self.root, text=stat_label, foreground="white", background="black").grid(row=row, column=0)
                gpu_stat_labels_row = []
                for gpu_id in range(self.gpu_monitor.total_gpus):
                    label = ttk.Label(self.root, text="-", foreground="white", background="black")
                    label.grid(row=row, column=gpu_id+1)
                    gpu_stat_labels_row.append(label)
                    if stat_label == "MaxPwr(W)":
                        label.bind("<Button-1>", lambda event, gpu_id=gpu_id: self.change_power_limit(gpu_id))
                self.gpu_stat_labels.append(gpu_stat_labels_row)
        else:
            pass
        #self.expand_label.bind("<Button-1>", lambda event: self.toggle_expand())
    def toggle_exit(self):
        self.root.quit()
    def toggle_expand(self):
        if self.show_all_gpu == "<":
            self.show_all_gpu = ">"
        else:
            self.show_all_gpu = "<"
    def update_info(self):
        self.updating = True
        # Update GPU stats
        total_gpus = range(self.gpu_monitor.total_gpus)
        self.gpu_monitor.update_gpu_stats()
        for gpu_id in total_gpus:
            gpu_info = self.gpu_monitor.gpu[gpu_id]
            self.gpu_stat_labels[0][gpu_id].configure(text=f"{gpu_info['percent_usage']}")
            self.gpu_stat_labels[1][gpu_id].configure(text=f"{gpu_info['temperature']}")
            self.gpu_stat_labels[2][gpu_id].configure(text=f"{gpu_info['power_usage']}")
            self.gpu_stat_labels[3][gpu_id].configure(text=f"{gpu_info['max_power']}")
            self.gpu_stat_labels[4][gpu_id].configure(text=f"{gpu_info['vram_used']}")
            self.gpu_stat_labels[5][gpu_id].configure(text=f"{gpu_info['vram_max']}")
        try:
            # Schedule the update_info function to run again after 2000 milliseconds (2 seconds)
            self.root.after(self.refresh_time, self.update_info)
        except tk.TclError as e:
            self.updating = False
    def change_power_limit(self, gpu_id=0):
        def validate_input(new_text):
            if not new_text:
                return True
            try:
                int(new_text)
                return True
            except ValueError:
                return False

        new_limit = simpledialog.askstring("Change Power Limit", "Enter the new maximum power limit:")
        if new_limit is not None and validate_input(new_limit):
            if not self.config['sudo_password'] or self.config['sudo_password'] == "":
                sudo_password = simpledialog.askstring("Enter Sudo Password", "Password will not be remembered, set config to remember:")
            self.gpu_monitor.set_gpu_power(gpu_id, int(new_limit), sudo_password)
        else:
            print("Invalid input or input cancelled.")
            pass
    def toggle_position(self):
        monitor = self.get_monitor()
        if monitor:
            self.set_position(monitor)
    def get_monitor(self, monitor_id=-1):
        monitor = False
        try:
            monitors = get_monitors()
            if not self.config['preferred_monitor']:
                if len(monitors) > 1:
                    for mon in monitors:
                        if not mon.is_primary:
                            monitor = mon
                else:
                    monitor = monitors[0]
            else:
                if monitor_id > -1 and monitor_id < len(monitors):
                    monitor = monitors[monitor_id]
                else:
                    monitor = monitors[self.config['preferred_monitor']]

        except ValueError:
            return False
        return monitor
    def set_position(self, monitor):
        monitor_width, monitor_height = monitor.width, monitor.height

        # Get screen dimensions
        screen_width, screen_height, screen_x, screen_y = monitor.x, monitor.y, monitor.width, monitor.height

        # Define positions for the window
        positions = {
            "0_top_left": {"x_pos": 0, "y_pos": 0},
            "0_top_right": {"x_pos": screen_x + screen_width - self.root.winfo_width(), "y_pos": 0},
            "0_bottom_left": {"x_pos": 0, "y_pos": screen_y + screen_height - self.root.winfo_height()},
            "0_bottom_right": {"x_pos": screen_x + screen_width - self.root.winfo_width(), "y_pos": screen_y + screen_height - self.root.winfo_height()},
        }

        # Determine the next position
        positions_list = list(positions.keys())
        if not hasattr(self, 'position') or self.position not in positions_list:
            self.position = positions_list[1]
        else:
            self.position = positions_list[(positions_list.index(self.position) + 1) % len(positions_list)]

        # Get the new window position
        new_x_pos = positions[self.position]['x_pos']
        new_y_pos = positions[self.position]['y_pos']

        # Move the window to the new position
        self.root.geometry(f"+{new_x_pos}+{new_y_pos}")
        if not self.updating:
            self.update_info()
    def load_config(self):
        with open(config_file_path, "r", encoding='utf-8') as outfile:
            config = json.load(outfile)
            return config
def main():
    root = tk.Tk()
    app = SKI_GPU_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
