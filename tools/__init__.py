import os
from time import clock
import csv
import tkinter as tk
from tkinter import ttk, messagebox
import TekkenBot
from TekkenBot import GUI_TekkenBotPrime as TEKKENBOT
import sys


""" Future version? notebook library to replace ttk.Notebook inside Action Editor, you can resize frames with it
import Pmw as pmw"""


DEFAULT_SETTINGS = {
                    'default direction': 'R',
                    '# of Virtual Joysticks': 2,
                    '# of Physical Joysticks': 1,
                    'analog configs':
                                    {
                                    'la_dl':
                                             {
                                            'x fix':	-31129,
                                            'y fix':	-31129,
                                            'x min':	-32768,
                                            'x max':	-13959,
                                            'y min':	-32768,
                                            'y max':	-13959},

                                    'la_l':
                                             {
                                            'x fix':	-31129,
                                            'y fix':	0,
                                            'x min':	-33430,
                                            'x max':	-13959,
                                            'y min':	-13959,
                                            'y max':	13959},

                                    'la_ul':
                                             {
                                            'x fix':	-31129,
                                            'y fix':	31129,
                                            'x min':	-32768,
                                            'x max':	-13959,
                                            'y min':	13959,
                                            'y max':	32768},

                                    'la_u':
                                            {
                                            'x fix':	0,
                                            'y fix':	31129,
                                            'x min':	-13959,
                                            'x max':	13959,
                                            'y min':	13959,
                                            'y max':	33430},

                                    'la_ur':
                                            {
                                            'x fix':	31129,
                                            'y fix':	31129,
                                            'x min':	14025,
                                            'x max':	32768,
                                            'y min':	13959,
                                            'y max':	32768},

                                    'la_r':
                                            {
                                            'x fix':	31129,
                                            'y fix':	0,
                                            'x min':	14025,
                                            'x max':	33430,
                                            'y min':	-13893,
                                            'y max':	13959},

                                    'la_dr':
                                            {
                                            'x fix':	31129,
                                            'y fix':	-31129,
                                            'x min':	13959,
                                            'x max':	32768,
                                            'y min':	-32768,
                                            'y max':	-13959},

                                    'la_d':
                                            {
                                            'x fix':	0,
                                            'y fix':	-31129,
                                            'x min':	-14025,
                                            'x max':	14025,
                                            'y min':	-33423,
                                            'y max':	-13959},

                                    'la_n':
                                            {
                                            'x fix':	0,
                                            'y fix':	0,
                                            'x min':	-13107,
                                            'x max':	13107,
                                            'y min':	-13107,
                                            'y max':	13107}},

                    'Delay Variables': ['dv1','dv2'],
                    'delay variable # of decimals': 3,
                    'button configs':
                                        {'xbox':
                                                {1: ('dpu_d', 'dpu_u'), 2: ('dpd_d', 'dpd_u'), 3: ('dpl_d', 'dpl_u'), 4: ('dpr_d', 'dpr_u'), 5: ('start_d', 'start_u'),
                                                 6: ('back_d', 'back_u'), 7: ('None', 'None'), 8: ('None', 'None'), 9: ('lb_d', 'lb_u'), 10: ('rb_d', 'rb_u'), 13: ('a_d', 'a_u'),
                                                 14: ('b_d', 'b_u'), 15: ('x_d', 'x_u'), 16: ('y_d', 'y_u')},



                                        'keyboard': {'left': ('dpl_d', 'dpl_u'), 'up': ('dpu_d', 'dpu_u'), 'right': ('dpr_d', 'dpr_u'), 'down': ('dpd_d', 'dpd_u'), '1': ('a_d', 'a_u'),
                                                    '2': ('b_d', 'b_u'), '3': ('x_d', 'x_u'), '4': ('y_d', 'y_u'), '-': ('back_d', 'back_u'), '+': ('start_d', 'start_u'),
                                                    'r': ('rb_d', 'rb_u'), 'e': ('lb_d', 'lb_u'), 'q': ('lt_d', 'lt_u'), 't': ('rt_d', 'rt_u')},


                                        'arcade stick':
                                                        {'vendor id': 0x0e8f, 'buttons':
                                                                                        {'page id': 0x9, 'usage ids':
                                                                                                                {0x1: ('a_d','a_u'), 0x5: ('x_d','x_u'), 0x6: ('y_d','y_u'), 0x2: ('b_d','b_u')}},
                                                                                'hat switch':
                                                                                        {'page id': 0x1, 'usage id': 0x39, 'values':
                                                                                                                                    {0: 'la_u', 1: 'la_ur', 2: 'la_r', \
                                                                                                                                    3: 'la_dr', 4: 'la_d', \
                                                                                                                                    5: 'la_dl', 6: 'la_l', \
                                                                                                                                    7: 'la_ul', 15: 'la_n'}}}},



                    'game': 'TEKKEN 7',
                    'Action Files': ['ae_default.txt', 'ae_tekken.txt', 'ae_soulcalibur.txt'],
                    'physical joy type': 'keyboard'}
                    # 'outfeed max characters': 400,}
                    # 'default neutral allowance': 0.7}

DEFAULT_ACTIONS = {'filename': 'ae_default.txt',
                    'include': True,
                    'action config':
                                    { 'A': {'Notation': 'A', 'String': ['a_d', 'delay(0.015)', 'a_u']},
                                        'B': {'Notation': 'B', 'String': ['b_d', 'delay(0.015)', 'b_u']},
                                        'X': {'Notation': 'X', 'String': ['x_d', 'delay(0.015)', 'x_u']},
                                        'Y': {'Notation': 'Y', 'String': ['y_d', 'delay(0.015)', 'y_u']},
                                        'Start': {'Notation': 'None','String': ['start_d', 'delay(0.015)', 'start_u']},
                                        'Back': {'Notation': 'None','String': ['back_d','delay(0.015)','back_u']},
                                        'RT': {'Notation': 'RT','String': ['rt_d', 'delay(0.015)', 'rt_u']},
                                        'LT': {'Notation': 'LT','String': ['lt_d', 'delay(0.015)', 'lt_u']},
                                        'LB': {'Notation': 'LB','String': ['lb_d', 'delay(0.015)', 'lb_u']},
                                        'RB': {'Notation': 'RB','String': ['rb_d', 'delay(0.015)', 'rb_u']},
                                        'DPU': {'Notation': 'DPU', 'String': ['dpu_d', 'delay(0.015)', 'dpu_u']},
                                        'DPR': {'Notation': 'DPR', 'String': ['dpr_d', 'delay(0.015)', 'dpr_u']},
                                        'DPL': {'Notation': 'DPL', 'String': ['dpl_d', 'delay(0.015)', 'dpl_u']},
                                        'DPD': {'Notation': 'DPD', 'String': ['dpd_d', 'delay(0.015)', 'dpd_u']}}

                    }

TEKKEN_ACTIONS = {'filename': "ae_tekken.txt",
                    'include': False,
                    'action config':
                                    { 'left punch': {'Notation': '1', 'String': ['x_d', 'delay(0.015)', 'x_u']},
                                    'right kick': {'Notation': '3', 'String': ['b_d', 'delay(0.015)', 'b_u']},
                                    'left kick': {'Notation': '4', 'String': ['a_d', 'delay(0.015)', 'a_u']},
                                    'right punch': {'Notation': '2', 'String': ['y_d', 'delay(0.015)', 'y_u']},
                                    'right punch': {'Notation': '2', 'String': ['y_d', 'delay(0.015)', 'y_u']},
                                    'forward': {'Notation': 'f', 'String': ['la_r', 'delay(0.030)', 'la_n']},
                                    'backward': {'Notation': 'b', 'String': ['la_l', 'delay(0.030)', 'la_n']},
                                    'down-forward': {'Notation': 'd/f', 'String': ['la_dr', 'delay(0.015)', 'la_n']},
                                    'up-forward': {'Notation': 'u/f', 'String': ['la_ur', 'delay(0.015)', 'la_n']},
                                    'down-backward': {'Notation': 'd/b', 'String': ['la_dl', 'delay(0.015)', 'la_n']},
                                    'up-backward': {'Notation': 'u/b', 'String': ['la_ul', 'delay(0.015)', 'la_n']},
                                    'backward': {'Notation': 'b', 'String': ['la_l', 'delay(0.030)', 'la_n']},
                                    'crouch': {'Notation': 'u', 'String': ['la_d', 'delay(0.030)', 'la_n']},
                                    'jump': {'Notation': 'd', 'String': ['la_u', 'delay(0.030)', 'la_n']},
                                    'back-2 combo': {'Notation': 'b+2', 'String': ['la_l', 'y_d', 'delay(0.015)', 'neutral']},
                                    'Crouch-Dash': {'Notation': 'cd', 'String': ['la_r','delay(0.02)', 'la_n', 'delay(0.02)', 'la_d', 'delay(0.02)', 'la_dr', 'delay(0.015)']}}
                }


SOULCALIBUR_ACTIONS = {'filename': "ae_soulcalibur.txt",
                        'include': False,
                        'action config':
                                        { 'A': {'Notation': 'A',  'String': ['x_d', 'delay(0.015)', 'x_u']},
                                        'K': {'Notation': 'K',  'String': ['b_d', 'delay(0.015)', 'b_u']},
                                        'G': {'Notation': 'G',  'String': ['a_d', 'delay(0.015)', 'a_u']},
                                        'B': {'Notation': 'B',  'String': ['y_d', 'delay(0.015)', 'y_u']},
                                        'A+G': {'Notation': 'A+G',  'String': ['lt_d', 'delay(0.015)', 'lt_u']},
                                        'A+B': {'Notation': 'A+B',  'String': ['lb_d', 'delay(0.015)', 'lb_u']},
                                        'B+G': {'Notation': 'B+G',  'String': ['rb_d', 'delay(0.015)', 'rb_u']},
                                        'A+B+K': {'Notation': 'A+B+K',  'String': ['rt_d', 'delay(0.015)', 'rt_u']},
                                        'forward': {'Notation': '6',  'String': ['la_r', 'delay(0.030)', 'la_n']},
                                        'backward': {'Notation': '4',  'String': ['la_l', 'delay(0.030)', 'la_n']},
                                        'down-forward': {'Notation': '3',  'String': ['la_dr', 'delay(0.015)', 'la_n']},
                                        'up-forward': {'Notation': '9',  'String': ['la_ur', 'delay(0.015)', 'la_n']},
                                        'down-backward': {'Notation': '1',  'String': ['la_dl', 'delay(0.015)', 'la_n']},
                                        'up-backward': {'Notation': '7',  'String': ['la_ul', 'delay(0.015)', 'la_n']},
                                        'backward': {'Notation': '4',  'String': ['la_l', 'delay(0.030)', 'la_n']},
                                        'crouch': {'Notation': '2',  'String': ['la_d', 'delay(0.030)', 'la_n']},
                                        'jump': {'Notation': '8',  'String': ['la_u', 'delay(0.030)', 'la_n']}}
                        }

"""
# Next Version

# SFV Actions

# DB Fighter Z

# Guilty Gear

# Mortal Kombat
"""

# Need below for sorting configs from least to most difficult to configure, but in future version, there needs to be a much more user-friendly UI to configure settings, hence the
# descriptions and types (so everything doesnt have to show up in quotations)
CATEGORIES = {
                'General': {
                            'Action Files': {'type': 'list', 'Description': 'These APPDATA files are where your actions are imported from'},
                            # 'Fixed Delay': {'type': 'float', 'Description': 'Delay between every action inside your script'},
                            # 'Start Delay': {'type': 'float', 'Description': 'Delay before the 1st action in your script plays'},
                            'game': {'type': 'str', 'Description': "Can be 'Tekken 7' or 'None'"},
                            'default direction': {'type': 'str', 'Description': 'Can be "R" or "L".'},
                            'play hotkey': {'type': 'str', 'Description': 'Toggles b/w Play and Pause'},
                            'flip x axis hotkey': {'type': 'str', 'Description': 'When flipped, any analog value with a non-zero x value is flipped.'},
                            'virtual joy port': {'type': 'int', 'Description': 'The "port" where your virtual joystick plugs into. Can be 1,2,3 or 4.'},
                            'physical joy type': {'type': 'str', 'Description': 'Can be "arcade stick", "xbox", or "keyboard".'},
                            'Delay Variables': {'type': 'list', 'Description': 'These are for inserting into your script/action strings to simulate delay.'},
                            'delay variable # of decimals': {'type': 'int', 'Description': 'None'},
                            },

                'Advanced': {
                             'analog configs': {'type': 'dict', 'Description': '"x fix" & "y fix" are the configs used by your vjoy. "x min","x max","y min", & "y max" are used by your pjoy in order to categorize its analog states.'},
                             'button configs': {'type': 'dict', 'Description': """Mapping of buttons to ('press function', 'release function'). Arcade Stick Only: Must have valid vendor ID. All buttons have a valid page ID, each button must have a valid usage ID. \
                                                                                    Hat switch must have one valid usage id. You can find this information by viewing your Device Report (In tools)."""},
                             }
                }



class GameHook(object):
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.classpointer = {'TEKKEN 7': TEKKENBOT.GameHook}
        self.hook = None
        self.p1box = None
        self.p2box = None
        self.running = False

    def start_overlay(self, box):
        for k,v in self.classpointer.items():
            if k in self.game:
                self.hook = v(self.master)
                break

        try:
            self.hook.setup_textredirector(box)
            self.hook.start_overlay()
            self.running = True
            return 1
        except Exception as e:
            return e

    def stop_overlay(self):
        self.hook.stop_overlay()


# detailed report showing PJoy, VJoy, and detected USB devices plugged into PC
class DeviceReport(tk.Toplevel):
    def __init__(self, master, info):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("Device Report (Read-Only)")
        self.lift(master)

        hidrep = info['hid report']
        vjrep = info['vj report']
        pjrep = info['pj report']

        self.master = master

        txtFrame = tk.Frame(self, borderwidth=1, relief="sunken")
        vjoybox = tk.Text(txtFrame, wrap = tk.NONE, borderwidth=0)
        vscroll = tk.Scrollbar(txtFrame, orient=tk.VERTICAL, command=vjoybox.yview)
        hscroll = tk.Scrollbar(txtFrame, orient=tk.HORIZONTAL, command=vjoybox.xview)
        vjoybox['yscroll'] = vscroll.set
        vjoybox['xscroll'] = hscroll.set
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        vjoybox.pack(side="left", fill="both", expand=True)

        # txtFrame.place(x=0, y=0)
        txtFrame.pack(side='top', fill='both', expand=True)

        # vjoybox = tk.Text(self)
        # vjoybox.pack(fill='both', expand=1, side='top')
        vjoybox.insert('1.0', vjrep + "\n\n" + pjrep + "\n\n" + \
                        "===========================================================================" \
                        + hidrep)

        vjoybox.config(state='disabled')

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)


class Settings(tk.Toplevel):
    def __init__(self, master, save_file):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("Settings")
        self.lift(master)

        self.settings = self.master.settings
        self.save_file = save_file
        tab = tk.Frame(self, borderwidth=1, relief="sunken")
        tab.pack(side='top', fill='both', expand=1)
        self.sbox = tk.Text(tab, wrap = tk.NONE, borderwidth=0)
        vscroll1 = tk.Scrollbar(tab, orient=tk.VERTICAL, command=self.sbox.yview)
        hscroll1 = tk.Scrollbar(tab, orient=tk.HORIZONTAL, command=self.sbox.xview)
        self.sbox['yscroll'] = vscroll1.set
        self.sbox['xscroll'] = hscroll1.set
        vscroll1.pack(side="right", fill="y")
        hscroll1.pack(side="bottom", fill="x")
        self.sbox.pack(side="left", fill="both", expand=True)

        self.setup_box()

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)
        reset2defbtn = ttk.Button(btmframe, text="Reset to Default", command=self.reset_to_default)
        reset2defbtn.pack(side='right', padx=5, pady=5)
        commitbtn = ttk.Button(btmframe, text="Commit", command=self.commit)
        commitbtn.pack(side='right', padx=5, pady=5)


    def setup_box(self):
        iter1 = 1

        for k,v in self.settings.items():
            if k in list(CATEGORIES["General"]):
                if isinstance(v, str):
                    v_ins = "'{}'".format(v)
                else:
                    v_ins = str(v)
                self.sbox.insert("{}.0".format(str(iter1 + 1)), "'{}'".format(str(k)) + ":\t" + v_ins + ",\n")
                iter1 += 1


        for i0, (k,v) in enumerate(self.settings.items()):
            if k in list(CATEGORIES["Advanced"]):
                if k == 'button configs':
                    self.sbox.insert("{}.0".format(str(iter1 + 1)),"},\n")
                    iter1 += 1
                if isinstance(k, str):
                    k_ins = "'{}'".format(str(k))
                else:
                    k_ins = str(k)

                self.sbox.insert("{}.0".format(str(iter1 + 1)), k_ins + ": \n{")
                iter1 += 1
                for i1, (kk,vv) in enumerate(v.items()):
                    if isinstance(vv, dict):
                        if isinstance(kk, str):
                            k_ins = "'{}'".format(str(kk))
                        else:
                            k_ins = str(kk)

                        self.sbox.insert("{}.0".format(str(iter1 + 1)), k_ins + ": \n {")
                        iter1 += 1
                        self.sbox.insert("{}.0".format(str(iter1 + 1)), "\n")
                        iter1 += 1
                        for i2, (kkk,vvv) in enumerate(vv.items()):
                            if isinstance(vvv, dict):
                                if isinstance(kkk, str):
                                    k_ins = "'{}'".format(str(kkk))
                                else:
                                    k_ins = str(kkk)

                                self.sbox.insert("{}.0".format(str(iter1 + 1)), k_ins + ":\n   {")
                                iter1 += 1
                                for i3, (kkkk,vvvv) in enumerate(vvv.items()):
                                    if i3 == len(list(vvv)) - 1:
                                        ender = "\n"
                                    else:
                                        ender = ",\n"

                                    if isinstance(kkkk, str):
                                        k_ins = "'{}'".format(str(kkkk))
                                    else:
                                        k_ins = str(kkkk)

                                    if isinstance(vvvv, str):
                                        v_ins = "'{}'".format(vvvv)
                                    else:
                                        v_ins = str(vvvv)

                                    self.sbox.insert("{}.0".format(str(iter1 + 1)), k_ins + ":\t" + v_ins + ender)
                                    iter1 += 1

                                if i2 == len(list(vv)) - 1:
                                    ender = "  }\n"
                                else:
                                    ender = " },\n"


                                self.sbox.insert("{}.0".format(str(iter1 + 1)), ender)
                                iter1 += 1

                            else:
                                if i2 == len(list(vv)) - 1:
                                    ender = "\n"
                                else:
                                    ender = ",\n"
                                if isinstance(kkk, str):
                                    k_ins = "'{}'".format(str(kkk))
                                else:
                                    k_ins = str(kkk)

                                if isinstance(vvv, str):
                                    v_ins = "'{}'".format(vvv)
                                else:
                                    v_ins = str(vvv)

                                self.sbox.insert("{}.0".format(str(iter1 + 1)), k_ins + ":\t" + v_ins + ender)
                                iter1 += 1

                        if i1 == len(list(v)) - 1:
                            ender = "  }\n"
                        else:
                            ender = " },\n"

                        self.sbox.insert("{}.0".format(str(iter1 + 1)), ender)
                        iter1 += 1

                    else:
                        if i1 == len(list(v)) - 1:
                            ender = "\n"
                        else:
                            ender = ",\n"

                        if isinstance(kk, str):
                            k_ins = "'{}'".format(str(kk))
                        else:
                            k_ins = str(kk)

                        if isinstance(vv, str):
                            v_ins = "'{}'".format(vv)
                        else:
                            v_ins = str(vv)

                        self.sbox.insert("{}.0".format(str(iter1 + 1)), "\t" + k_ins + ":\t" + v_ins + ender)
                        iter1 += 1

                    self.sbox.insert("{}.0".format(str(iter1 + 1)), "\n")
                    iter1 += 1

        self.sbox.insert("{}.0".format(str(iter1 + 1)), "}")


    def reset_to_default(self):
        self.sbox.delete("1.0", tk.END)
        self.settings = DEFAULT_SETTINGS
        self.setup_box()


    def commit(self):
        # convert text in textbox to dictionary
        t = self.sbox.get("1.0", tk.END)

        new1 = "{%s}" % (t)

        try:
            d = eval(new1)
        except SyntaxError as e:
            messagebox.showerror(title='Error', message=e)
            return

        try:
            with open(self.save_file, "w") as f:
                f.write(str(new1))
                f.close()
            self.master.refresh()

        except SyntaxError as e:
            messagebox.showerror(title='Error', message=e)


# Allows users to create their own actions
class Action_Editor(tk.Toplevel):
    def __init__(self, master, datapath):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("Action Editor")
        self.lift(master)
        self.master = master
        self.datapath = datapath
        self.save_files = self.master.settings["Action Files"]
        # pmw.initialise(self)
        # self.note = pmw.Notebook(self,borderwidth=2,arrownavigation=True,tabpos='n')

        self.note = ttk.Notebook(self)
        self.note.pack(fill='both', expand=1)

        # container for text boxes
        self.container = {}
        for file in self.save_files:
            # filename = "action_editor_file{}".format(len(self.note.tabs()) + 1)
            fileframe = tk.Frame(self)
            self.note.add(fileframe, text = file, compound='top')

            # uncomment (and alter) if switching to pmw Notebook
            # self.note._pageAttrs[file]['tabreqwidth'] = 200
            # self.note._pageAttrs[file]['tabreqheight'] = 100
            # self.note.component(file).configure(font= ('verdana',18 ,'bold italic'), \
            #             fg= "black",bg="white",wraplength=150)
            tbox = tk.Text(fileframe, wrap = tk.NONE, borderwidth=0)
            vscroll1 = tk.Scrollbar(fileframe, orient=tk.VERTICAL, command=tbox.yview)
            hscroll1 = tk.Scrollbar(fileframe, orient=tk.HORIZONTAL, command=tbox.xview)
            tbox['yscroll'] = vscroll1.set
            tbox['xscroll'] = hscroll1.set
            vscroll1.pack(side="right", fill="y")
            hscroll1.pack(side="bottom", fill="x")
            tbox.pack(fill='both', expand=1)
            with open(self.datapath + "\\" + file, "r") as f:
                adic = eval(f.read())
                f.close()


            for i, (k,v) in enumerate(adic.items()):
                if k == 'action config':
                    tbox.insert(tk.INSERT, "'{}'".format(k) + ": {\n")

                    for iter, (kk,vv) in enumerate(v.items()):
                        if iter == len(v) - 1:
                            ender = ""
                        else:
                            ender = ","
                        tbox.insert(tk.INSERT, "\t\t'{}'".format(kk) + ":\t\t" + str(vv) + "{}\n".format(ender))
                        iter += 1
                    tbox.insert(tk.INSERT, "}")

                else:
                    if i == len(adic) - 1:
                        ender = ""
                    else:
                        ender = ","

                    insval = str(v) if ".txt" not in str(v) else "'{}'".format(v)
                    tbox.insert(tk.INSERT, "'{}'".format(k) + ":\t\t\t" + insval + "{}\n".format(ender))

            self.container[file] = tbox

        #PMW
        # self.add_plus_tab(init=True)
        # self.note.pack(fill='both', expand=1, padx=10, pady=10)

        # self.note.setnaturalsize()

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)
        commitbtn = ttk.Button(btmframe, text="Commit", command=self.commit)
        commitbtn.pack(side='right', padx=5, pady=5)


    # next version?

    # def add_plus_tab(self, init=True):
    #     if not init:
    #         filename = len(self.note.tabs()) + 1
    #         self.note.add(text="{}".format(filename)
    #         self.note._pageAttrs[file]['tabreqwidth'] = 200
    #         self.note._pageAttrs[file]['tabreqheight'] = 100
    #         self.nb.component('{}-tab'.format(filename)).configure(font= ('verdana',18 ,'bold italic'), \
    #                     fg= "black",bg="white",wraplength=150)
    #
    #     fileframe = self.note.add(text = '+')
    #     self.note._pageAttrs[file]['tabreqwidth'] = 100
    #     self.note._pageAttrs[file]['tabreqheight'] = 100
    #     self.nb.component('+-tab').configure(font= ('verdana',18 ,'bold italic'), \
    #                 fg= "black",bg="white",wraplength=150)


    def commit(self):
        for k,v in self.container.items():
            d = "{%s}" % (v.get("1.0", tk.END))
            try:
                d = eval(d)
            except SyntaxError as e:
                messagebox.showerror(title='Error', message=e)
                return
            try:
                with open(self.datapath + "\\" + k, "w") as f:
                    f.write(str(d))
                    f.close()
            except Exception as e:
                messagebox.showerror(title='Error', message=e)
                return



        self.master.refresh()


# opens USERGUIDE.txt file from main path
class User_Guide(tk.Toplevel):
    def __init__(self, master, ug):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("User Guide (Read-Only)")
        self.lift(master)

        userguide = ug

        self.master = master

        txtFrame = tk.Frame(self, borderwidth=1, relief="sunken")
        ugbox = tk.Text(txtFrame, wrap = tk.NONE, borderwidth=0)
        vscroll = tk.Scrollbar(txtFrame, orient=tk.VERTICAL, command=ugbox.yview)
        hscroll = tk.Scrollbar(txtFrame, orient=tk.HORIZONTAL, command=ugbox.xview)
        ugbox['yscroll'] = vscroll.set
        ugbox['xscroll'] = hscroll.set
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        ugbox.pack(side="left", fill="both", expand=True)
        # txtFrame.place(x=0, y=0)
        txtFrame.pack(side='top', fill='both', expand=True)

        # vjoybox = tk.Text(self)
        # vjoybox.pack(fill='both', expand=1, side='top')
        ugbox.insert('1.0', userguide)
        ugbox.config(state='disabled')

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)


# opens LICENSE file from main path
class License(tk.Toplevel):
    def __init__(self, master, l):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("License (Read-Only)")
        self.lift(master)

        license = l

        self.master = master

        txtFrame = tk.Frame(self, borderwidth=1, relief="sunken")
        lbox = tk.Text(txtFrame, wrap = tk.NONE, borderwidth=0)
        vscroll = tk.Scrollbar(txtFrame, orient=tk.VERTICAL, command=lbox.yview)
        hscroll = tk.Scrollbar(txtFrame, orient=tk.HORIZONTAL, command=lbox.xview)
        lbox['yscroll'] = vscroll.set
        lbox['xscroll'] = hscroll.set
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        lbox.pack(side="left", fill="both", expand=True)
        # txtFrame.place(x=0, y=0)
        txtFrame.pack(side='top', fill='both', expand=True)

        # vjoybox = tk.Text(self)
        # vjoybox.pack(fill='both', expand=1, side='top')
        lbox.insert('1.0', license)
        lbox.config(state='disabled')

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)

# To show that Sparlab is meant to be used for training
class AntiCheatPolicy(tk.Toplevel):
    def __init__(self, master, ac):
        super().__init__(master)

        # self.geometry("{0}x{1}+0+0".format( \
        #     master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        self.geometry("800x600")

        self.wm_title("Anti-Cheat Policy (Read-Only)")
        self.lift(master)

        anticheat = ac

        self.master = master

        txtFrame = tk.Frame(self, borderwidth=1, relief="sunken")
        acbox = tk.Text(txtFrame, wrap = tk.NONE, borderwidth=0)
        vscroll = tk.Scrollbar(txtFrame, orient=tk.VERTICAL, command=acbox.yview)
        hscroll = tk.Scrollbar(txtFrame, orient=tk.HORIZONTAL, command=acbox.xview)
        acbox['yscroll'] = vscroll.set
        acbox['xscroll'] = hscroll.set
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        acbox.pack(side="left", fill="both", expand=True)
        # txtFrame.place(x=0, y=0)
        txtFrame.pack(side='top', fill='both', expand=True)

        # vjoybox = tk.Text(self)
        # vjoybox.pack(fill='both', expand=1, side='top')
        acbox.insert('1.0', anticheat)
        acbox.config(state='disabled')

        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)


class FrameDataTable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.CreateUI()
        # self.LoadTable()
        # self.grid(sticky = (tk.N,tk.S,tk.W,tk.E))
        # parent.grid_rowconfigure(0, weight = 1)
        # parent.grid_columnconfigure(0, weight = 1)

    def CreateUI(self):
        tv = ttk.Treeview(self)
        tv['columns'] = cols = ('#', 'input command', 'internal move id number', 'internal move name', 'attack type', 'startup frames', 'frame advantage on block', 'frame advantage on hit', 'frame advantage on counter hit', \
                        'active frame connected on / total active frames', 'how well move tracks during startup', 'total number of frames in move', 'frames before attacker can act', 'frames before defender can act', 'additional move properties')
        for c in cols:
            tv.heading(c, text=c, anchor='w')
            tv.column(c, anchor="center", width=50)

        tv.grid(sticky = (tk.N,tk.S,tk.W,tk.E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

    def insert_row(self, args):
        self.treeview.insert('', 'end', text=str(args), values=tuple(args))
