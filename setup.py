import sys
import setuptools
from cx_Freeze import setup, Executable
import os



import updater
import _input
import _output
from multiprocessing import Queue, freeze_support
import webbrowser
from collections import ChainMap
import tools

os.environ['TCL_LIBRARY'] = r'C:\Users\John Ward\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\John Ward\AppData\Local\Programs\Python\Python36\tcl\tk8.6'


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","tkinter","PIL","time","decimal","math","custom","_input", "updater", "_output", "hook", "tools",
                                "vjoy","multiprocessing"],
                        "include_files": ["LICENSE.txt", ("driver", "driver"), "userguide.txt",
                                        os.path.join(r'C:\Users\John Ward\AppData\Local\Programs\Python\Python36\DLLs', 'tcl86t.dll'),
                                        os.path.join(r'C:\Users\John Ward\AppData\Local\Programs\Python\Python36\DLLs', 'tk86t.dll')],
                        'include_msvcr': True}




# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Sparlab",
        version = "1.0.5",
        description = "Sparlab",
        author = "John Ward",
        options = {"build_exe": build_exe_options},
        executables = [Executable("sparlab.py", base=base, icon = os.path.join(r'C:\Users\John Ward\Desktop\sparlab\plugins\images', 'sparlab_logo.ico'))])
