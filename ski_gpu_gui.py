import json, os
import tkinter as tk
from tkinter import ttk, simpledialog
from screeninfo import get_monitors
from ski_gpu_monitor import Ski_GPU_Monitor

script_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_directory, "config.json")

class SKI_GPU_GUI:
    def __init__(self, root):
        self.version = "1.1.1"
        self.lastupdate = "2024-06-02"
        self.gpu_monitor = Ski_GPU_Monitor()
        self.gpu_monitor.update_gpu_stats()

        self.config = self.load_config()
        self.root = root
        self.root.title("SKI GPU INFO")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        self.position = self.config['position']
        self.show_all_gpu = "<" # display carrot only. updated else where.
        self.updating = False # Keeps track of it auto refreshing statistics.
        self.refresh_time = self.config['refresh_time'] * 1000

        self.gui_displayed = False #Lets update function know if the GUI is being changed.
        self.display_modes = self.config['display_modes']
        self.gpu_gui_labels = [] #keeps track of label widgets on gui that are in root frame, I got lazy about frames...
        self.stats_labels = [] #keeps track of the displayed stat labels for updating

        self.create_widgets()
        self.set_position(self.get_monitor(), self.position)
        self.update_info()

    def create_widgets(self):
        self.root.configure(bg="black")

        self.buttons_frame = tk.Frame(self.root, bg='black')
        self.buttons_frame.grid(row=0, column=0, sticky='ew')
        self.buttons_frame.columnconfigure(0, weight=1)

        # Create a style for the checkbox
        style = ttk.Style()
        style.configure("Black.TCheckbutton", background="black", foreground="white")
        style.configure("Black.TFrame", background="black")

        # Create a checkbox at position 0,0 without any text
        quit_checkbox = ttk.Checkbutton(self.buttons_frame, text="", style="Black.TCheckbutton", command=self.toggle_exit)
        quit_checkbox.grid(row=0, column=0, sticky='w')
        position_checkbox = ttk.Checkbutton(self.buttons_frame, text="", style="Black.TCheckbutton", command=self.toggle_position)
        position_checkbox.grid(row=0, column=2, sticky='e')
        self.expand_label = ttk.Label(self.buttons_frame, text=self.show_all_gpu, foreground="white", background="black")
        self.expand_label.grid(row=0, column=1, sticky='e')

        self.create_gpu_labels()

    def create_gpu_labels(self):
        if self.config['display_mode'] == 'default':
            self.create_default_list()
            self.show_all_gpu = "<"
        elif self.config['display_mode'] == 'summary':
            self.create_summary_list()
            self.show_all_gpu = ">"
        elif self.config['display_mode'] == 'banner':
            self.create_banner_list()
            self.show_all_gpu = "^"
        self.expand_label.configure(text=f"{self.show_all_gpu}")
        self.buttons_frame.update_idletasks()
        self.expand_label.bind("<Button-1>", lambda event: self.toggle_expand())
        self.gui_displayed = True
    def create_default_list(self):
        self.stat_names = [item['name'] for item in self.display_modes["default"].values() if item['show']]
        self.stats_labels = [key for key, value in self.display_modes["default"].items() if value['show']]

        self.GPU_frame = tk.Frame(self.root, bg='black')
        self.GPU_frame.grid(row=0, column=1, rowspan=len(self.stats_labels)+1, sticky='nsew')

        self.GPU_frame.rowconfigure(0, weight=1)
        self.GPU_frame.columnconfigure(0, weight=1)
        # Create a label for each GPU ID
        self.gpu_gui_labels = []
        self.gpu_stat_labels = []
        for gpu_id in range(self.gpu_monitor.total_gpus):
            gpu_gui_label = ttk.Label(self.GPU_frame, text=f"GPU {gpu_id}", foreground="white", background="black")
            gpu_gui_label.grid(row=0, column=gpu_id, sticky='ew')
            self.gpu_gui_labels.append(gpu_gui_label)

        # Create labels for GPU stats
        for row, stat_label in enumerate(self.stat_names, start=1):
            gpu_gui_label = ttk.Label(self.root, text=stat_label, foreground="white", background="black")
            gpu_gui_label.grid(row=row, column=0, sticky='ew')
            gpu_stat_labels_row = []
            self.gpu_gui_labels.append(gpu_gui_label)
            for gpu_id in range(self.gpu_monitor.total_gpus):
                label = ttk.Label(self.GPU_frame, text="-", foreground="white", background="black")
                label.grid(row=row, column=gpu_id, sticky='ew')
                self.GPU_frame.rowconfigure(row, weight=1)
                self.GPU_frame.columnconfigure(gpu_id, weight=1)
                gpu_stat_labels_row.append(label)
                power_name = self.config['display_modes']['default']['max_power']['name']
                if stat_label == power_name:
                    label.bind("<Button-1>", lambda event, gpu_id=gpu_id: self.change_power_limit(gpu_id))
            self.gpu_stat_labels.append(gpu_stat_labels_row)
    def create_summary_list(self):
        self.stat_names = [item['name'] for item in self.display_modes["summary"].values() if item['show']]
        self.stats_labels = [key for key, value in self.display_modes["summary"].items() if value['show']]

        self.GPU_frame = tk.Frame(self.root, bg='black')
        self.GPU_frame.grid(row=0, column=1, rowspan=len(self.stats_labels)+1, sticky='nsew')
        self.gpu_stat_labels = []
        self.gpu_gui_labels = []

        gpu_gui_label = ttk.Label(self.GPU_frame, text=f"All GPUs", foreground="white", background="black")
        gpu_gui_label.grid(row=0, column=0, sticky='ew')
        self.gpu_gui_labels.append(gpu_gui_label)
        for row, stat_label in enumerate(self.stat_names, start=1):
            gpu_gui_label = ttk.Label(self.root, text=stat_label, foreground="white", background="black")
            gpu_gui_label.grid(row=row, column=0, sticky='ew')
            self.gpu_gui_labels.append(gpu_gui_label)
            gpu_stat_labels_row = []
            gpu_id = 'all'
            label = ttk.Label(self.GPU_frame, text="-", foreground="white", background="black")
            label.grid(row=row, column=0, sticky='ew')
            self.GPU_frame.rowconfigure(row, weight=1)
            self.GPU_frame.columnconfigure(0, weight=1)
            gpu_stat_labels_row.append(label)
            power_name = self.config['display_modes']['summary']['max_power']['name']
            if stat_label == power_name and self.gpu_monitor.total_gpus == 1:
                label.bind("<Button-1>", lambda event, gpu_id=gpu_id: self.change_power_limit(gpu_id))
            self.gpu_stat_labels.append(gpu_stat_labels_row)
    def create_banner_list(self):
        self.stat_names = [item['name'] for item in self.display_modes["banner"].values() if item['show']]
        self.stats_labels = [key for key, value in self.display_modes["banner"].items() if value['show']]

        self.GPU_frame = tk.Frame(self.root, bg='black')
        self.GPU_frame.grid(row=0, column=1, sticky='nsew')

        self.gpu_stat_labels = []
        self.gpu_gui_labels = []
        gpu_gui_label = ttk.Label(self.GPU_frame, text=f"All", foreground="white", background="black")
        gpu_gui_label.grid(row=0, column=0, sticky='ew')
        self.gpu_gui_labels.append(gpu_gui_label)

        for col, stat_label in enumerate(self.stat_names, start=0):
            gpu_gui_label = ttk.Label(self.GPU_frame, text=stat_label, foreground="white", background="black")
            gpu_gui_label.grid(row=0, column=col*2, sticky='ew')
            
            gpu_gui_label.grid_configure(sticky='nsew', padx=1, pady=1)
            gpu_gui_label.configure(borderwidth=2, relief="groove", background="#222222")
            
            gpu_stat_labels_col = []
            gpu_id = 'all'
            label = ttk.Label(self.GPU_frame, text="-", foreground="white", background="black")
            label.grid(row=0, column=(col*2)+1, sticky='ew')
            self.GPU_frame.rowconfigure(0, weight=1)
            self.GPU_frame.columnconfigure(col, weight=1)
            gpu_stat_labels_col.append(label)
            power_name = self.config['display_modes']['banner']['max_power']['name']
            powerusage_name = self.config['display_modes']['banner']['power_usage']['name']
            if (stat_label == power_name or stat_label == powerusage_name) and self.gpu_monitor.total_gpus == 1:
                label.bind("<Button-1>", lambda event, gpu_id="0": self.change_power_limit("0"))
            self.gpu_stat_labels.append(gpu_stat_labels_col)
    def toggle_exit(self):
        self.root.quit()
    def toggle_expand(self):
        self.gui_displayed = False
        if self.config['display_mode'] == "default":
            self.config['display_mode'] = "summary"
            self.show_all_gpu = ">"
        elif self.config['display_mode'] == "summary":
            self.config['display_mode'] = "banner"
            self.show_all_gpu = "^"
        elif self.config['display_mode'] == "banner":
            self.config['display_mode'] = "default"
            self.show_all_gpu = "<"
        else:
            self.config['display_mode'] = "default"
            self.show_all_gpu = "<"
        self.GPU_frame.destroy()
        for widget in self.gpu_gui_labels:
            widget.destroy()
        self.expand_label.configure(text=f"{self.show_all_gpu}")
        self.create_gpu_labels()
        self.update_info()
        self.set_position(self.get_monitor(), self.position)
    def update_info(self):
        self.updating = True
        # Update GPU stats
        if self.config['display_mode'] == 'default':
            self.update_default_layout()
        elif self.config['display_mode'] == 'summary':
            self.update_summary_layout()
        elif self.config['display_mode'] == 'banner':
            self.update_banner_layout()
        
        try:
            # Schedule the update_info function to run again after 2000 milliseconds (2 seconds)
            self.root.after(self.refresh_time, self.update_info)
        except tk.TclError as e:
            self.updating = False
    def update_default_layout(self):
        total_gpus = range(self.gpu_monitor.total_gpus)
        self.gpu_monitor.update_gpu_stats()
        if self.gui_displayed:
            for gpu_id in total_gpus:
                gpu_info = self.gpu_monitor.gpu[gpu_id]
                for i, stat in enumerate(self.stats_labels):
                    self.gpu_stat_labels[i][gpu_id].configure(text=f"{gpu_info[stat]}")
    def update_summary_layout(self):
        self.gpu_monitor.update_gpu_stats()
        gpu_info = self.gpu_monitor.gpu_all
        if self.gui_displayed:
            for i, key in enumerate(self.stats_labels):
                self.gpu_stat_labels[i][0].configure(text=f"{gpu_info[key]}")
    def update_banner_layout(self):
        self.gpu_monitor.update_gpu_stats()
        gpu_info = self.gpu_monitor.gpu_all
        if self.gui_displayed:
            for i, key in enumerate(self.stats_labels):
                self.gpu_stat_labels[i][0].configure(text=f"{gpu_info[key]}")
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
            else:
                sudo_password = self.config['sudo_password']
            self.gpu_monitor.set_gpu_power(gpu_id, int(new_limit), sudo_password)
    def toggle_position(self):
        monitor = self.get_monitor()
        if monitor:
            self.change_position(monitor)
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
    def change_position(self, monitor):
        # Determine the next position
        positions_list = ["top left", "top center", "top right", "bottom left", "bottom center", "bottom right", "v_center left", "v_center right", "v_center center"]
        if not hasattr(self, 'position') or self.position not in positions_list:
            self.position = positions_list[1]
        else:
            self.position = positions_list[(positions_list.index(self.position) + 1) % len(positions_list)]

        self.set_position(monitor, self.position)
    def set_position(self, monitor, position):
        monitor_width, monitor_height = monitor.width, monitor.height

        # Get screen dimensions
        screen_width, screen_height, screen_x, screen_y = monitor.x, monitor.y, monitor.width, monitor.height

        left = 0
        right = screen_x + screen_width - self.root.winfo_width()
        top = 0
        bottom = screen_y + screen_height - self.root.winfo_height()
        center = int((screen_x + screen_width - self.root.winfo_width())/2)
        v_center = int((screen_y + screen_height - self.root.winfo_height())/2)

        # Define positions for the window
        positions = {
            "top left": {"x_pos": left, "y_pos": top},
            "top center": {"x_pos": center, "y_pos": top},
            "top right": {"x_pos": right, "y_pos": top},
            "bottom left": {"x_pos": left, "y_pos": bottom},
            "bottom center": {"x_pos": center, "y_pos": bottom},
            "bottom right": {"x_pos": right, "y_pos": bottom},
            "v_center left": {"x_pos": left, "y_pos": v_center},
            "v_center right": {"x_pos": right, "y_pos": v_center},
            "v_center center": {"x_pos": center, "y_pos": v_center}
        }
        positions_list = list(positions.keys())
        if not hasattr(self, 'position') or self.position not in positions_list:
            self.position = positions_list[0]
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
