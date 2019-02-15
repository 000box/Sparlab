# Sparlab

https://www.youtube.com/watch?v=XKNUhKUnYeE

Sparlab is a desktop software tool that allows fighting gamers to read game memory, simulate game scenarios, and discover new combos while training.

Features:

TekkenBot Frame Reader Integration
Two Steam-compatible Virtual Joysticks for simulating input.
Key logger compatible with keyboards, xbox controllers, and arcade sticks. 
Action Editor for customizing action libraries. 
Adjustable Delay Variables for simulating delay b/w inputs. 
Auto Adjustment: increase/decrease delay variable during Simulation. 
And more. 


Developers: we welcome your contributions!

Problems we need help with:

1) Synchronized inputs with internal game counter (see Issues) 
2) Sparlab API to make use of collected data
  - Reinforcement Learning Functionality for integrating AI bots and finding most optimal future of any given game state.
  - Performance tracking based on hitboxes, health, and other factors
3) Libraries for fighting games besides Tekken
  - Could TekkenBot be scaled to work for other games?
4) Adaptation for other devices & consoles
  - PS3/PS4 controller wrapper is needed. 
  - Sparlab only works on PC, how can we get it to work on XBOX, PS4, and other consoles? 
5) User-friendly Settings & Action Editor interfaces 


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
'python .\setup.py build'  

Distributable:
'python .\setup.py bdist_msi'






