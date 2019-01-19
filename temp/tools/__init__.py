import os
from datetime import date
from time import clock
import csv
import tkinter as tk
from tkinter import ttk

# mapping of bottom buttons to commands,
#function that performs when user presses


DEFAULT_SETTINGS = {'fps': 60, 'Fixed Delay': 0.00, 'Start Delay': 3.0, 'default direction': 'R', 'play hotkey': '0', 'flip x axis hotkey': '/', 'virtual joy port': 1, 'virtual joy type': 'xbox', 'analog configs': {'la_dl': {'x fix': -0x7999, 'y fix': -0x7999, 'x min': -0.5, 'x max': -0.213, 'y min': -0.5, 'y max': -0.213}, 'la_l': {'x fix': -0x7999, 'y fix': 0, 'x min': -0.51, 'x max': -0.213, 'y min': -0.213, 'y max': 0.213}, 'la_ul': {'x fix': -0x7999, 'y fix': 0x7999, 'x min': -0.5, 'x max': -0.214, 'y min': 0.213, 'y max': 0.5}, 'la_u': {'x fix': 0, 'y fix': 0x7999, 'x min': -0.213, 'x max': 0.213, 'y min': 0.212, 'y max': 0.51}, 'la_ur': {'x fix': 0x7999, 'y fix': 0x7999, 'x min': 0.214, 'x max': 0.5, 'y min': 0.213, 'y max': 0.5}, 'la_r': {'x fix': 0x7999, 'y fix': 0, 'x min': 0.214, 'x max': 0.51, 'y min': -0.212, 'y max': 0.213}, 'la_dr': {'x fix': 0x7999, 'y fix': -0x7999, 'x min': 0.213, 'x max': 0.5, 'y min': -0.5, 'y max': -0.213}, 'la_d': {'x fix': 0, 'y fix': -0x7999, 'x min': -0.214, 'x max': 0.214, 'y min': -0.51, 'y max': -0.213}, 'la_n': {'x fix': 0, 'y fix': 0, 'x min': -0.2, 'x max': 0.2, 'y min': -0.2, 'y max': 0.2}}, 'Delay Variables': ['dv1','dv2','dv3','dv4','dv5'], 'Button-Function Map': {'xbox': {1: ('dpu_d', 'dpu_u'), 2: ('dpd_d', 'dpd_u'), 3: ('dpl_d', 'dpl_u'), 4: ('dpr_d', 'dpr_u'), 5: ('start_d', 'start_u'), 6: ('back_d', 'back_u'), 7: ('None', 'None'), 8: ('None', 'None'), 9: ('lb_d', 'lb_u'), 10: ('rb_d', 'rb_u'), 13: ('a_d', 'a_u'), 14: ('b_d', 'b_u'), 15: ('x_d', 'x_u'), 16: ('y_d', 'y_u')},
'keyboard': {'w': ('dpu_d', 'dpu_u'), 's': ('dpd_d', 'dpd_u'), 'a': ('dpl_d', 'dpl_u'), 'd': ('dpr_d', 'dpr_u'), 'b': ('start_d', 'start_u'), 'v': ('back_d', 'back_u'), 'e': ('lb_d', 'lb_u'), 'r': ('rb_d', 'rb_u'), '1': ('a_d', 'a_u'), '2': ('b_d', 'b_u'), '3': ('x_d', 'x_u'), '4': ('y_d', 'y_u')}, 'arcade stick': {'vendor id': 0x0e8f, 'buttons': {'page id': 0x9, 'usage ids': {0x1: ('a_d','a_u'), 0x5: ('x_d','x_u'), 0x6: ('y_d','y_u'), 0x2: ('b_d','b_u')}}, 'hat switch': {'page id': 0x1, 'usage id': 0x39, 'values': {0: 'la_u', 1: 'la_ur', 2: 'la_r', 3: 'la_dr', 4: 'la_d', 5: 'la_dl', 6: 'la_l', 7: 'la_ul', 15: 'la_n'}}}}, 'Action Files': ['action_editor_example.txt'], 'physical joy type': 'keyboard', 'outfeed max characters': 400, 'virtual joy text color': 'purple', 'physical joy text color': 'red', 'log type': 'comparison', 'default neutral allowance': 0.7}

DEFAULT_ACTIONS = { 'left punch': {'Notation': '1', 'Hotkey': 'None', 'String': ['x_d', 'delay(0.015)', 'x_u']},
                    'right kick': {'Notation': '3', 'Hotkey': 'None', 'String': ['b_d', 'delay(0.015)', 'b_u']},
                    'left kick': {'Notation': '4', 'Hotkey': 'l+p', 'String': ['a_d', 'delay(0.015)', 'a_u']},
                    'right punch': {'Notation': '2', 'Hotkey': 'None', 'String': ['y_d', 'delay(0.015)', 'y_u']},
                    'start': {'Notation': 'None', 'Hotkey': '`', 'String': ['start_d', 'delay(0.015)', 'start_u']},
                    'double-dash': {'Notation': 'dd', 'Hotkey': 'None', 'String': ['la_r', 'delay(0.015)', 'la_n', 'delay(0.015)', 'la_r', 'delay(0.015)', 'la_n']},
                    'right punch': {'Notation': '2', 'Hotkey': 'None', 'String': ['y_d', 'delay(0.015)', 'y_u']},
                    'forward': {'Notation': 'f', 'Hotkey': 'None', 'String': ['la_r', 'delay(0.030)', 'la_n']},
                    'backward': {'Notation': 'b', 'Hotkey': 'None', 'String': ['la_l', 'delay(0.030)', 'la_n']},
                    'crouch': {'Notation': 'u', 'Hotkey': 'None', 'String': ['la_d', 'delay(0.030)', 'la_n']},
                    'jump': {'Notation': 'd', 'Hotkey': 'None', 'String': ['la_u', 'delay(0.030)', 'la_n']}}


CATEGORIES = {
                'General': {
                            'Action Files': {'type': 'list', 'Description': 'These APPDATA files are where your actions are imported from'},
                            'fps':  {'type': 'int', 'Description': 'Manipulates the time length used by the "j_f" function'},
                            'Fixed Delay': {'type': 'float', 'Description': 'Delay between every action inside your script'},
                            'Start Delay': {'type': 'float', 'Description': 'Delay before the 1st action in your script plays'},
                            'default direction': {'type': 'str', 'Description': 'Can be "R" or "L".'},
                            'play hotkey': {'type': 'str', 'Description': 'Toggles b/w Play and Pause'},
                            'flip x axis hotkey': {'type': 'str', 'Description': 'When flipped, any analog value with a non-zero x value is flipped.'},
                            'virtual joy port': {'type': 'int', 'Description': 'The "port" where your virtual joystick plugs into. Can be 1,2,3 or 4.'},
                            'physical joy type': {'type': 'str', 'Description': 'Can be "arcade stick", "xbox", or "keyboard".'},
                            'outfeed max characters':  {'type': 'int', 'Description': 'Your outfeed box clears after surpassing this number.'},
                            'Delay Variables': {'type': 'list', 'Description': 'These are for inserting into your script/action strings to simulate delay.'},
                            'virtual joy text color': {'type': 'str', 'Description': 'The color of this joy\'s outfeed text.'},
                            'physical joy text color': {'type': 'str', 'Description': 'The color of this joy\'s outfeed text.'},
                            'log type': {'type': 'str', 'Description': 'Can be "normal" (logs pj activity) or "comparison" (logs pj activity alongside your script\'s string value).'},
                            'default neutral allowance': {'type': 'int', 'Description': 'When your pjoy is inactive for this amt. of time while you are in the middle of a string, the outfeed will end the string and start a new one.'},
                            'virtual joy type': {'type': 'str', 'Description': 'This setting must be equal to "xbox" for now.'}
                            },

                'Advanced': {
                             'analog configs': {'type': 'dict', 'Description': '"x fix" & "y fix" are the configs used by your vjoy. "x min","x max","y min", & "y max" are used by your pjoy in order to categorize its analog states.'},
                             'Button-Function Map': {'type': 'dict', 'Description': """Mapping of buttons to ('press function', 'release function'). Arcade Stick Only: Must have valid vendor ID. All buttons have a valid page ID, each button must have a valid usage ID. \
                                                                                    Hat switch must have one valid usage id. You can find this information by viewing your Device Report (In tools)."""},
                             }
                }


class Action_Logger:
    def __init__(self, master, path, type='normal',title=date.today(), vja=None):
        self.master = master
        self.type = type

        title = str(title) + "-{}".format(clock()) + ".csv"

        if type == 'comparison':
            headers = ["#","Result (pj)", "Target (vj)"]
        elif type == 'normal':
            headers = ["#", "Result (pj)"]
        else:
            self.master.q2.put({'Warning': '"{}" is not a valid log type'.format(self.type)})
            type = 'normal'
            headers = ["#", "Result (pj)"]


        self.csvfile = open('{}\\{}'.format(path, title), 'w', newline='')

        self.dictwriter = csv.DictWriter(self.csvfile, fieldnames=headers)


        self.dictwriter.writeheader()
        self.row = 0
        self.ca = []
        self.current = 0
        self.vjdata = vja
        self.pjdata = []


    def beg_string(self):
        print("BEGIN STRING")
        self.ca = []

    def end_string(self):
        print("END STRING. APPEND {} TO HISTORY".format(self.ca))
        self.row += 1
        if self.type == 'comparison':
            self.dictwriter.writerow({'#': self.row, "Result (pj)": self.ca, "Target (vj)": self.vjdata})
        elif self.type == 'normal':
            self.dictwriter.writerow({'#': self.row, "Result": self.ca})
        else:
            self.master.q2.put({'Warning': '"{}" is not a valid log type'.format(self.type)})
            self.type = 'normal'
            self.dictwriter.writerow({'#': self.row, "Result": self.ca})


    def add_to_string(self, item):
        print("ADD {} TO STRING".format(item))
        self.ca.append(item)

    def close_log(self):
        self.csvfile.close()

    def __del__(self):
        try:
            self.close_log()
        except Exception as e:
            pass




class PopupDoc(tk.Toplevel):
    def __init__(self, master, info):
        super().__init__(master)
        self.geometry("400x800")
        self.wm_title("Action Reference (Read-Only)")
        self.lift(master)

        self.master = master
        self.action_reference(info)

    def action_reference(self, info):
        forbidden = ["None", None, ""]
        settings = {}
        tolookfor = ["play hotkey", "flip x axis hotkey"]
        for k,v in info["Settings"].items():
            if k in tolookfor:
                settings[k] = v

        hks = {}
        for k,v in info["Actions"].items():
            if v["Hotkey"] not in forbidden:
                hks[k] = v["Hotkey"]

        notations = {}
        for k,v in info["Actions"].items():
            if v["Notation"] not in forbidden:
                notations[k] = v["Notation"]

        strings = {}
        for k,v in info["Actions"].items():
            if v["String"] not in forbidden:
                strings[k] = v["String"]


        # textbox for main keys
        tk.Label(self, text="Hotkeys", font="Verdana 12").pack(side="top")
        hkbox = tk.Text(self, width=8, height=5, state='normal')
        hkbox.pack(anchor='nw', side='top', padx=5, pady=10, fill='both', expand=1)
        for iter, (k,v) in enumerate(settings.items()):
            hkbox.insert("{}.0".format(str(iter+1)), k + ":\t" + v + "\n")
        for iter1, (k,v) in enumerate(hks.items()):
            hkbox.insert("{}.0".format(str(iter + iter1 + 1)), k + ":\t" + v + "\n")
        hkbox.config(state='disabled')

        tk.Label(self, text="Notations", font="Verdana 12").pack(side="top")
        notationbox = tk.Text(self, width=16, height=5, state='normal')
        notationbox.pack(anchor='s', side='top', padx=5, pady=10, fill='both', expand=1)
        for iter, (k,v) in enumerate(notations.items()):
            notationbox.insert("{}.0".format(str(iter + 1)), k + ":\t" + v + "\n")
        notationbox.config(state='disabled')

        tk.Label(self, text="Strings", font="Verdana 12").pack(side="top")
        self.sbox = tk.Text(self, width=16, height=5, state='normal')
        self.sbox.pack(anchor='s', side='top', padx=5, pady=10, fill='both', expand=1)
        for iter, (k,v) in enumerate(strings.items()):
            self.sbox.insert("{}.0".format(str(iter + 1)), k + ":\t" + str(v) + "\n")
        self.sbox.config(state='disabled')

        ttk.Button(self, text="Cancel", command=lambda: self.destroy()).pack(side='bottom', anchor='s', pady=5)

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
                if k == 'Button-Function Map':
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
            self.master.q2.put({'error': e})
            return

        try:
            with open(self.save_file, "w") as f:
                f.write(str(new1))
                f.close()
            self.master.refresh()

        except SyntaxError as e:
            self.master.q2.put({'error': e})

        # FOR TESTING

        # shared_items = {}
        # nonshared_items = {}
        # for k,v in settings.items():
        #     if k in self.settings and settings[k] == self.settings[k]:
        #         shared_items[k] = v
        #     else:
        #         nonshared_items[k] = v
        #
        #
        # print("shared items: ", shared_items)
        # print("non-shared items: ", nonshared_items)

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
        self.note = ttk.Notebook(self)
        self.note.pack(fill='both', expand=1)

        # container for text boxes
        self.container = {}
        for file in self.save_files:
            fileframe = tk.Frame(self)
            self.note.add(fileframe, text = file, compound='top')

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

            iter = 1
            for i, (k,v) in enumerate(adic.items()):
                if i == len(adic) - 1:
                    ender = ""
                else:
                    ender = ","

                tbox.insert("{}.0".format(iter), "'{}'".format(k) + ":\t\t\t" + str(v) + "{}\n\n".format(ender))
                iter += 1

            self.container[file] = tbox


        btmframe = tk.Frame(self)
        btmframe.pack(side='top', fill='x')

        cancelbtn = ttk.Button(btmframe, text="Cancel", command=self.destroy)
        cancelbtn.pack(side='right', padx=5, pady=5)
        commitbtn = ttk.Button(btmframe, text="Commit", command=self.commit)
        commitbtn.pack(side='right', padx=5, pady=5)



    def commit(self):
        for k,v in self.container.items():
            d = "{%s}" % (v.get("1.0", tk.END))
            try:
                d = eval(d)
            except SyntaxError as e:
                self.master.q2.put({'error': e})
                return
            try:
                with open(self.datapath + "\\" + k, "w") as f:
                    f.write(str(d))
                    f.close()
            except Exception as e:
                self.master.q2.put({'error': e})

        self.master.refresh()


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
