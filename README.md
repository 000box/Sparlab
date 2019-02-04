# Sparlab

Sparlab is an open source training tool that allows fighting gamers to simulate game scenarios and discover new combos.

Features:

Two Steam-compatible Virtual Joysticks for simulating input.
Key logger compatible with keyboards, xbox controllers, and arcade sticks. 
Action Editor for customizing action libraries. 
Adjustable Delay Variables for simulating delay b/w inputs. 
Auto Adjustment: increase/decrease delay variable during Simulation. 
And more. 


How to run from Command Line: 

Requirements:
Python version: 3.6

To setup: 
1) Clone this repository or download the zip file to a convenient location.
2) Type "python .\sparlab.py" at command line. Install any required packages ('pip install [INSERT PACKAGE HERE]') 
3) In the Help menu at the top of the app, open the User Guide and follow the setup instructions.


How to build executable/distributable: 

Requirements:
cx_Freeze

Executable:
In powershell inside the __main__ directory, enter 'python .\setup.py build' to the command line.

Distributable:
In powershell inside the __main__ directory, enter 'python .\setup.py bdist_msi' to the command line. 






