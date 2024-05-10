# SKI GPU Monitor
## About
This python app uses nvidia-smi commands to get and display single or multiple GPU information onto a compact borderless window.

The purpose is to allow me to monitor my GPU's while running various ai related tasks and to allow me to set GPU watt limits on the fly. But it works well with other high demand GPU loads.

## Planned Features
I kind of got this where I want it, but maybe these?
1) Log statistics to file periodically?
2) Minimize to Tray?
3) Write GUI in something other than tkinter?

## Install
### Only tested on Linux.

Download both py scripts and place in a folder of your choice.

### Dependancies
You will need to pip install these if you dont already have them.
* screeninfo, tkinter, json, os, subprocess, time

## Run
run the ski_gpu_gui.py script
* python3 ./ski_gpu_gui.py

The config file will be generated on the first run. Exit the app(check box on top left), and edit the config file to fit your purposes.

A note will also be inserted into the config file that helps explain some things, I expect that note to be more upto date that this read me(because I am forgetful).

## Config File
* "Config_Note": Can be deleted, meant for lazy people as a quick reference.
* "sudo_password": Can set sudo password here if you hate security, otherwise you will have to type it in each time you change power limit settings in app.
* "gpu": Each GPU will need an entry, if you add a gpu, DELETE your config file, or carefully add the data in the correct format. If all else fails, delete your config to regenerate your config file.
  * "power_initial": The app will automatically try to set GPU Power Limit to this number. It will fail without a sudo password set. But you can manually change it in the app while running.
  * "power_max": This will restrict the maximum power limit to this number, by default the program will create the config and pull this number from nvidia-smi
  * "power_min": This will restrict the minimum power limit to this number, by default the program will create the config and pull this number from nvidia-smi
* "refresh_time": The number of seconds untill the auto refresh of the GPU stats.
* "min_wait": The minimum time in second the app will allow it to call on nvidia-smi, typically it doesnt update more than once per second.
  * This is used internally and should not be less than 1, I repeatedly hammer the nvidia-smi call, and its only stopped by this time out.
* "preferred_monitor": The prefered monitor id the app will start on. By default this will be set to False, which means it will goto the last non primary monitor. Will cause issues if set incorrectly.
  * false/0/1/etc: Use the id of the monitor or just leave it as false
* "position": Default Position of the window inside of the selected monitor. Must be an integer.
  * top/bottom/v_center left/right/center
  * EX: "top right" or "v_center left"
  * Only nine options are valid, defaults to "top left".
* "display_mode": This is the mode the display starts in. (default, summary, banner)
* "display_modes": This is the settings for the options being displayed.

## Usage
Once the app is started you basically have 2 static buttons, and one button for every GPU. I used check boxes as buttons, cause they are small.
* Close App - Top Left Check Box
* Move Window Snap - Top Right Check Box
* Carrot - Cycles Display Mode, Default, Summary, or Banner
* Change Power Limit - Click on the Number for the GPU you want to change.
  * You will be prompted for the amount
  * You will be prompted for the sudo password if not set.
