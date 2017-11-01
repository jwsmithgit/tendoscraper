import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"],
    #"bin_includes": ["chromedriver.exe", "geckodriver.exe"],
    #"bin_path_includes": ["bin"],
    "include_files": ["tracker_setup.txt", 
                     ("bin/chromedriver.exe", "bin/chromedriver.exe"),
                     ("bin/geckodriver.exe", "bin/geckodriver.exe") 
                     ]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "console"

setup(  name = "tracker",
    version = "0.1",
    description = "tracker",
    options = {"build_exe": build_exe_options},
    executables = [Executable("tracker.py", base=base)])