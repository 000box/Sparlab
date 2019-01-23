# Sparlab

Sparlab is an open source training platform for all fighting gamers. 

Features:

Steam-compatible Virtual Joystick for simulating input w/ over 50 input functions.
Key loggers for USB Input devices such as keyboards, xbox controllers, and arcade sticks. 
Action Editor for customizing action libraries. 
Hotkey Listener to allow users to stay focused inside their game windows. 
Adjustable Delay Variables for simulating delay b/w inputs. 
And more.


Developers

Our vision:
We want Sparlab to be a tool that every fighting gamer uses. They will use this tool instead of built-in game features and other third party injection tools because:
1) it will scale equally across all fighting games and devices. This will allow gamers to cross-train more easily than in the past.
build a stable, scalable and useful training platform for fighting gamers. 
2) it will be provide detailed performance reports with machine learning algorithms, allowing gamers to understand themselves and their opponents at much deeper levels. 
3) it will be customizable and accessible by the end user upon the creation of an API

4) l completely remove the need to reverse-engineer games for frame data and other assets.  
5 it will be continuously supported and improved by the community. 

To achieve more robust method of timing user input, UI design, more built-in virtual gamepads, object tracker that can accurately predict X,Y coordinates and proximity to  for each player, health bar readers, and hit box detectors. What ideas would you like to see Sparlab have? Your contributions 

Feel free to think of your own ideas for improving Sparlab! 

License: The attached general public license gives you the freedom to make your own changes and distribute your own copies of Sparlab. 

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







