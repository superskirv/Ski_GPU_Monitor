import subprocess, json, os, time

Ski_GPU_Monitor_version = "1.0.3"

script_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_directory, "config.json")

class Ski_GPU_Monitor:
    #import subprocess, json, os, time
    def __init__(self):
        self.config = self.load_config()
        self.last_run = [0,0,0]
        self.min_wait = self.config['min_wait'] #second

        self.total_vram_used = 0
        self.total_vram_max = 0
        self.gpu_usage = []
        self.gpu_temp = []
        self.gpu_power_usage = []
        self.gpu_max_power = []
        self.gpu_vram_used = []
        self.gpu_vram_max = []

        self.gpu = {}
        self.total_gpus = 0
        self.total_list = self.get_number_gpu()
        for gpu_id in self.total_list:
            print('gpu_id',gpu_id)
            if len(list(self.config['gpu'].keys())) > 0:
                self.set_gpu_power(gpu_id, self.config['gpu'][str(gpu_id)]['power_initial'])
            self.run_nvidiasmi(gpu_id)
    def get_total_vram_max(self):
        self.update_gpu_stats()
        self.total_vram_max = 0
        for gpu_id, stats in self.gpu.items():
            self.total_vram_max += self.gpu[gpu_id]['vram_max']
        return self.total_vram_max
    def get_total_vram_used(self):
        self.update_gpu_stats()
        self.total_vram_used = 0
        self.update_gpu_stats()
        for gpu_id, stats in self.gpu.items():
            self.total_vram_used += self.gpu[gpu_id]['vram_used']
        return self.total_vram_used

    def get_GPU_usage(self):
        self.update_gpu_stats()
        self.gpu_usage = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_usage.append(self.gpu[gpu_id]['percent_usage'])
        return self.gpu_usage
    def get_GPU_temp(self):
        self.update_gpu_stats()
        self.gpu_temp = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_temp.append(self.gpu[gpu_id]['temperature'])
        return self.gpu_temp
    def get_GPU_power_usage(self):
        self.update_gpu_stats()
        self.gpu_power_usage = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_power_usage.append(self.gpu[gpu_id]['power_usage'])
        return self.gpu_power_usage
    def get_GPU_max_power(self):
        self.update_gpu_stats()
        self.gpu_max_power = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_max_power.append(self.gpu[gpu_id]['max_power'])
        return self.gpu_max_power
    def get_vram_used(self):
        self.update_gpu_stats()
        self.gpu_vram_used = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_vram_used.append(self.gpu[gpu_id]['vram_used'])
        return self.gpu_vram_used
    def get_vram_max(self):
        self.update_gpu_stats()
        self.gpu_vram_max = []
        for gpu_id, stats in self.gpu.items():
            self.gpu_vram_max.append(self.gpu[gpu_id]['vram_max'])
        return self.gpu_vram_max

    def get_number_gpu(self):
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"], capture_output=True, text=True)
            gpu_ids = [int(id.strip()) for id in result.stdout.strip().split('\n')]
            self.total_gpus = len(gpu_ids)
            return gpu_ids
        except subprocess.CalledProcessError:
            print("Error(0100): nvidia-smi command failed.")
            return []
    def get_gpu_max_power(self, gpu_id):
        try:
            result = subprocess.run(["nvidia-smi", f"--id={gpu_id}", "--query-gpu=power.max_limit", "--format=csv,noheader,nounits"], capture_output=True, text=True)
            max_power_gpu = int(float(result.stdout.strip()))
            return max_power_gpu
        except subprocess.CalledProcessError as e:
            print(f"Error(0101): running nvidia-smi: {e}")
            return None
    def get_gpu_min_power(self, gpu_id):
        try:
            result = subprocess.run(["nvidia-smi", f"--id={gpu_id}", "--query-gpu=power.min_limit", "--format=csv,noheader,nounits"], capture_output=True, text=True)
            max_power_gpu = int(float(result.stdout.strip()))
            return max_power_gpu
        except subprocess.CalledProcessError as e:
            print(f"Error(0102): running nvidia-smi: {e}")
            return None

    def set_gpu_power(self, gpu_id, limit, sudo_password=False):
        if not sudo_password:
            sudo_password = self.config["sudo_password"]

        if limit > self.config['gpu'][str(gpu_id)]['power_max']:
            limit = self.config['gpu'][str(gpu_id)]['power_max']
        if limit < self.config['gpu'][str(gpu_id)]['power_min']:
            limit = self.config['gpu'][str(gpu_id)]['power_min'] 

        try:
            command = f"echo {sudo_password} | sudo -S nvidia-smi -i {gpu_id} -pl {limit}"
            subprocess.run(command, shell=True, check=True)
            print(f"GPU{gpu_id} power limit set to {limit} Watts.")
        except subprocess.CalledProcessError as e:
            print(f"Error(0200) setting GPU power limit: {e}")
    def update_gpu_stats(self):
        for gpu_id in self.total_list:
            if time.time() - self.last_run[gpu_id] > self.min_wait:
                self.run_nvidiasmi(gpu_id)
    def run_nvidiasmi(self, gpu_id):
        if time.time() - self.last_run[gpu_id] > self.min_wait:
            try:
                result = subprocess.run(['nvidia-smi', f'--id={gpu_id}', '--query-gpu=index,utilization.gpu,temperature.gpu,power.draw,power.limit,memory.used,memory.total', '--format=csv,noheader,nounits'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                self.last_run[gpu_id] = time.time()

                gpu_info = result.stdout.strip().split(',')
                keyname = int(gpu_info[0])
                gpu_data = {
                    'percent_usage': int(gpu_info[1]),
                    'temperature': int(gpu_info[2]),
                    'power_usage': float(gpu_info[3]),
                    'max_power': float(gpu_info[4]),
                    'vram_used': int(gpu_info[5]),
                    'vram_max': int(gpu_info[6])
                }
                self.gpu[keyname] = gpu_data
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error(0000): running nvidia-smi: {e}")
                return False
        else:
            #print(f"Error(0101): running nvidia-smi: Running too often.")
            return False
    def load_config(self):
        if not os.path.isfile(config_file_path):
            config = self.build_config()
        else:
            with open(config_file_path, "r", encoding='utf-8') as outfile:
                config = json.load(outfile)
        return config
    def build_config(self):
        config = {
            "Config_Note": [
                "This note is for information purposes only and can be deleted."
                'sudo_password be False / "" / "actual password"',
                "gpu data will only be automatically added if config is missing",
                "preferred_monitor can be set to [False,0,1,etc], if False it will default to the non primary monitor",
                "position is not working yet, but will change which corner the window starts in."
            ],
            "sudo_password": False,
            "gpu": {},
            "refresh_time": 3,
            "min_wait": 1,
            "preferred_monitor": False,
            "position": 1
        }
        #Saves a partial config file to allow the GPU Monitor to start without errors.
        with open(config_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(config, outfile, indent=2)

        gpu_monitor = Ski_GPU_Monitor()
        gpus = gpu_monitor.get_number_gpu()
        gpu_data = {}
        for gpu_id in gpus:
            max_power = gpu_monitor.get_gpu_max_power(gpu_id)
            min_power = gpu_monitor.get_gpu_min_power(gpu_id)
            gpu_data[str(gpu_id)] = {
                "power_initial": int((max_power-min_power)/2)+min_power,
                "power_max": max_power,
                "power_min": min_power
            }
        config['gpu'] = gpu_data
        #Saves a complete config file, with some default GPU Data, USERS will need to edit to fine tune.
        with open(config_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(config, outfile, indent=2)
        return config