import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time

try:
    import updater
except:
    pass

import _input
import _output
from multiprocessing import Queue, freeze_support
import webbrowser
from collections import ChainMap
import tools
import sys
# from datetime import datetime
import hook.hid as hid


__version__ = '1.0.7'

DATAPATH = '%s\\Sparlab\\%s' %  (os.environ['APPDATA'], __version__)
LOGPATH = DATAPATH + "\\logs"
# default text files if file pointer not functional
HID_REPORT = r"{}\hidreport.txt".format(DATAPATH)
DEFAULT_ACTLIB = {'ae_default.txt': tools.DEFAULT_ACTIONS, 'ae_tekken.txt': tools.TEKKEN_ACTIONS, 'ae_soulcalibur.txt': tools.SOULCALIBUR_ACTIONS}


with open("USERGUIDE.txt", "r") as f:
    USERGUIDE = f.read()
    f.close()

with open("LICENSE", "r") as f:
    LICENSE = f.read()
    f.close()

with open("ANTICHEATPOLICY.txt", "r") as f:
    ANTICHEATPOLICY = f.read()
    f.close()

#ff4242 (favorite color)
TITLE_FONT = ("Verdana", 24)
LARGE_FONT = ("Verdana", 12)
SMALL_FONT = ("Verdana", 8)
HELP_FONT = ("Verdana", 7)
ICON = "sparlab_logo.ico"


class App(tk.Tk):

    def refresh(self):
        """ After user presses play, makes changes in Settings or Action Editor, or presses Refresh button, this function will be called"""
        # settings
        with open(DATAPATH + "\\" + "settings.txt", "r") as f:
            # string to python dict
            self.settings = eval(f.read())
            f.close()

        imports = []
        for i in range(len(self.settings["Action Files"])):
            filename = self.settings["Action Files"][i]
            path = DATAPATH + "\\" + filename
            try:
                with open(path, "r") as f:
                    d = eval(f.read())
                    if d["include"] == True:
                        imports.append(d["action config"])
                    f.close()
            except SyntaxError as e:
                # print("syntax")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))
            except FileNotFoundError:
                # print("adding new action path: ", path)
                try:
                    if path in list(DEFAULT_ACTLIB):
                        d = DEFAULT_ACTLIB[filename]
                    else:
                        d = {'filename': i, 'include': False, 'action config': {'action 1': {'Notation': 'None', 'Hotkey': 'None', 'String': []}}}
                    with open(path, "w") as f:
                        f.write(str(d))
                        f.close()

                    if d["include"] == True:
                        imports.append(d["action config"])

                except Exception as e:
                    # print("error ({}) when adding new action path ({})".format(e, path))
                    messagebox.showerror(title="Warning", message='action file with path {} was not able to be appended ({})'.format(path, e))

            except Exception as e:
                # print("other")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))

        self.act_cfg = dict(ChainMap(*imports))




        # self.hotkeys_enabled = False

        # set stringvars
        try:
            self.pjoy_type = self.settings['physical joy type']
            self.default_dir = self.settings['default direction']
            self.digits = self.settings['delay variable # of decimals']

            # self.log_type = self.settings['log type']
        except TypeError as e:
            messagebox.showerror(title="Error", message=e)

        dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
        info = {'settings': self.settings, 'actcfg': self.act_cfg, 'delay vars': dt} #, 'hks enabled': self.hotkeys_enabled}

        for i in range(1, 3):
            self.ui_j["VJ"][i].put(info)

        self.ui_j["INP"].put(info)


        return True


    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Sparlab")
        tk.Tk.iconbitmap(self, default=ICON)
        self.geometry('{}x{}'.format(750, 500))
        # self.configure(background="#ffffff")

        self.settingsfile = DATAPATH + "\\" + "settings.txt"

        # if this folder doesn't exist, create it along with storing copies of default settings & functions
        if not os.path.exists(DATAPATH):
            os.makedirs(DATAPATH)
            with open(self.settingsfile, "w") as f:
                f.write(str(tools.DEFAULT_SETTINGS))
                f.close()

        if not os.path.exists(LOGPATH):
            os.makedirs(LOGPATH)

        # settings
        with open(self.settingsfile, "r") as f:
            # string to python dict
            self.settings = eval(f.read())
            f.close()


        imports = []
        for i in range(len(self.settings["Action Files"])):
            filename = self.settings["Action Files"][i]
            path = DATAPATH + "\\" + filename
            try:
                with open(path, "r") as f:
                    d = eval(f.read())
                    if d["include"] == True:
                        imports.append(d["action config"])
                    f.close()
            except SyntaxError as e:
                # print("syntax")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))
            except FileNotFoundError:
                # print("adding new action path: ", path)
                try:
                    if filename in list(DEFAULT_ACTLIB):
                        d = DEFAULT_ACTLIB[filename]
                    else:
                        d = {'filename': filename, 'include': False, 'action config': {'action 1': {'Notation': 'None', 'Hotkey': 'None', 'String': []}}}
                    with open(path, "w") as f:
                        f.write(str(d))
                        f.close()

                    if d["include"] == True:
                        imports.append(d["action config"])

                except Exception as e:
                    # print("error ({}) when adding new action path ({})".format(e, path))
                    messagebox.showerror(title="Warning", message='action file with path {} was not able to be appended ({})'.format(path, e))

            except Exception as e:
                # print("other")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))



        self.act_cfg = dict(ChainMap(*imports))

        # self.hks_on = False
        self.on = {1: False, 2: False}

        # self.hotkeys_enabled = False
        self.out_disabled = False
        self.aa_enabled = False
        self.rep = 0
        self.digits = self.settings['delay variable # of decimals']
        self.vjtext = {1: None, 2: None}
        self.mirrorvar = {1: None, 2: None}
        self.mirror = {1: None, 2: None}
        self.mirror_box = {1: None, 2: None}
        self.game_hook = tools.GameHook(self, self.settings['game'])
        self.outtype = 'String'

        try:
            self.pjoy_type = self.settings['physical joy type']
            self.default_dir = self.settings['default direction']
            self.dir = self.settings['default direction']

        except TypeError as e:
            messagebox.showerror(title="Error", message=e)



    def post_init(self):
        self.simulating = {1: False, 2: False}
        self.simulating_once = {1: False, 2: False}
        try:
            with open(DATAPATH + "\\" + "lastsession.txt", "r") as f:
                ls = eval(f.read())
                self.delay_tuners = {i: tk.StringVar(value=ls['delay_vars'][i]) for i in self.settings['Delay Variables']}
                # print("lastsession: ", ls)
                self.aavar = tk.StringVar(value=str(ls['auto adjustment']['variable']))
                self.aaval = tk.StringVar(value=str(ls['auto adjustment']['value']))
                self.aafreq = tk.StringVar(value=str(ls['auto adjustment']['frequency']))
                self.vjtext = ls['vjtext']

                self.open_file(lastsess=ls)
                f.close()
        except FileNotFoundError:
            try:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in eval(self.settings['Delay Variables'])}
            except:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in self.settings['Delay Variables']}

            self.aaval = tk.StringVar()
            self.aafreq = tk.StringVar(value=1)
            self.aavar = tk.StringVar(value=list(self.delay_tuners.items())[0][0])

            self.add_tab()

        except Exception as e:
            # print("error ({}) when attempting to load lastsession.txt".format(e))
            try:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in eval(self.settings['Delay Variables'])}
            except:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in self.settings['Delay Variables']}

            self.aaval = tk.StringVar()
            self.aafreq = tk.StringVar(value=1)
            self.aavar = tk.StringVar(value=list(self.delay_tuners.items())[0][1])

            self.add_tab()

        self.create_top_menu()
        # info getters
        for i in range(1, 3):
            self.after(200, lambda joy=i, tp='VJ': self.info_from_joy(j=joy, _type=tp))
            self.ui_j['VJ'][i].put({'settings': self.settings})

        self.after(200, lambda joy=1, tp='INP': self.info_from_joy(j=joy, _type=tp))
        self.ui_j['INP'].put({'settings': self.settings})

        self.check_for_update(booting=True)


    def info_from_joy(self, j=1, _type='VJ'):

        strtb = self.last_update['str_inputtextbox']
        rawtb = self.last_update['raw_inputtextbox']
        fdtb = self.last_update['fd_inputtextbox']

        # intb = self.last_update[_type][j]['inputtextbox']
        if _type == 'VJ':
            q = self.j_ui[_type][j]
        else:
            q = self.j_ui['INP']

        while q.qsize():
            try:
                info = q.get(0)
                # print("info: ", info)

                if info != None and strtb != None:
                    # print("info: ", info)
                    strtb.config(state='normal')
                    # next version
                    try:
                        self.pj_report = info['pjoy report']
                    except KeyError:
                        pass
                    try:
                        joy = info['joy']

                        joy = info["joy"]
                        # action string
                        a = info['action']
                        # action function
                        # n_chars = outtb.count("1.0", tk.INSERT)
                        startover = info['start over']
                        # print("351 startover: ", startover)
                        # print("joy: {}, a: {}, startover: {}".format(joy, a, startover))

                    except KeyError as e:
                        pass
                        # print("355 keyerror: ", e)
                        # print("355 e: ", e)
                    except Exception as e:
                        pass
                        # print("358 e: ", e)
                        # print("258: ", e)
                    try:
                        if startover:
                            if self.simulating[j] and _type == 'VJ':
                                self.rep += 1
                            char0 = "{}.0".format(int(float(strtb.index(tk.INSERT))))
                            strtb.see(char0)
                            if self.rep % int(self.aafreq.get()) == 0 and self.simulating[j] and _type == 'VJ':
                                self.make_auto_adjustment()

                        if not self.out_disabled:
                            # ins = str(self.rep) + ": " if startover else ""
                            # print("insert: ", a)
                            strtb.insert(tk.INSERT, a)

                        strtb.see(tk.END)

                    except KeyError as e:
                        pass
                        # print("377 KEY ERROR: ", e)
                    except UnboundLocalError as e:
                        pass
                        # print("380 ULE ERROR: ", e)
                        # print("ULE ERROR: ", e)
                    except TypeError as e:
                        # print("383 Type ERROR: ", e)
                        # pass
                        pass
                    except Exception as e:
                        # pass
                        messagebox.showerror(title='Error', message=e)

                    try:
                        w = info['warning']
                        messagebox.showerror(title='Warning', message=w)
                    except KeyError as e:
                        pass
                        # print("382 e: ", e)
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    try:
                        e = info['error']
                        # print("ERROR: ", e)
                        messagebox.showerror(title='Error', message=e)
                    except KeyError as e:
                        pass
                        # print("382 e: ", e)
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    try:
                        r = info['raw']
                        # rep = info['rep']
                        # if rep == 0:
                        #     self.rep += 1
                        joy = info['joy']
                        # if not self.out_disabled:
                        rawtb.config(state='normal')
                        rawtb.insert(tk.INSERT, r)

                        char0 = "{}.0".format(int(float(rawtb.index(tk.END))))
                        rawtb.see(char0)
                        rawtb.config(state='disabled')

                    except KeyError as e:
                        pass
                        # print("raw key error: ", e)
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)



                    try:
                        facing = info['facing']
                        if self.dir != facing:
                            self.toggle_mirror()
                    except:
                        pass
                    try:
                        self.vj_report = info['vjoy report']
                    except KeyError:
                        pass

                    try:
                        vbusnotexist = info['vbusnotexist']
                        messagebox.showerror(title="Error", message="No virtual bus driver was found on your system.")
                    except:
                        pass
                    try:
                        playing = info['playing']
                        if playing == False:
                            # print("stop!!!")
                            self.stop()
                        elif playing == True:
                            self.play()
                    except Exception as e:
                        # msg = "{}: {}".format(type(e).__name__, e.args)
                        # print("PLAYING EXCEPTION: ", e)
                        pass
            except Exception as e:
                msg = "{} ERROR: {}: {}".format(j, type(e).__name__, e.args)
                # print(msg)

        self.after(200, lambda joy=j, t=_type: self.info_from_joy(j=joy, _type=t))


    #enable scrolling with mouse (to make it more app-like on other devices) in future version?
    def scroll_start(self, event):
        event.widget.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        event.widget.scan_dragto(event.x, event.y)


    def add_tab(self, name = None):

        # self.note = ttk.Notebook(self)

        # app always opens on this sheet
        self.new_file(name=name)
        # self.note.pack(fill='both', expand=1)
        # self.note.grid(column=0, row=0, sticky='nsew')


    def create_top_menu(self):
        """ Menu at top of app """

        self.menu = tk.Menu(self, tearoff=False)
        self.config(menu=self.menu)
        filemenu = tk.Menu(self, tearoff=False)
        editmenu = tk.Menu(self, tearoff=False)
        modemenu = tk.Menu(self, tearoff=False)
        helpmenu = tk.Menu(self, tearoff=False)
        toolmenu = tk.Menu(self, tearoff=False)

        self.toggle_labels = {}

        # self.submenus =                                                             {'File': (filemenu, [('New', self.new_file,None ), ('Open', self.open_file, None),
                        #                                                           ('Save Script', self.save_as, None),('Save Log', self.save_as, True), ('Refresh', self.refresh, None),
                                                                                    # ('Exit', self.destroy, None)]),


        self.submenus = {'Edit': (editmenu, [('Settings', self.settings_editor, None), ("Action Editor", self.action_editor, None)]),
                        #('Toggle Hotkeys', self.toggle_hotkeys, None),

                        'Help': (helpmenu, [('Device Report', self.view_device_report, None), ('User Guide', self.view_user_guide, None), ('License', self.view_license, None), ('Anti-Cheat Policy', self.view_anticheatpolicy, None),
                         ('Community', self.view_community, None), ('Check for Update', self.check_for_update, None)])}


        for k, v in self.submenus.items():
            self.menu.add_cascade(label=k, menu=v[0])
            if k in ['Edit', 'Tools', 'Help']:
                for i in v[1]:
                    # acc = i[2]
                    arg = i[2]

                    # if i[0] in ['Play']:
                    #     stat = 'disabled'
                    # else:
                    stat = 'normal'

                    command = lambda func=i[1], a=arg: self.menu_command(func, a)
                    v[0].add_command(label=i[0], command=command, state=stat)


    def menu_command(self, func, arg):
        if arg == None:
            func()
        else:
            func(arg)



    def pack_joy_textboxes(self, tab):
        frame = tk.Frame(tab)
        frame.pack(side='top', fill='both')

        labelframe = tk.Frame(frame)
        labelframe.pack(side='top', fill='x')
        script1labelframe = tk.Frame(labelframe)
        script1labelframe.pack(side='left', fill='x')
        script2labelframe = tk.Frame(labelframe)
        script2labelframe.pack(side='right', fill='x')

        loglabelframe = tk.Frame(labelframe)
        loglabelframe.pack(side='right', fill='x')
        l = tk.Label(script1labelframe, text='P1 VJoy', font='Verdana 8 bold')
        l.pack(side='left', padx=20)
        l = tk.Label(script2labelframe, text='P2 VJoy', font='Verdana 8 bold')
        l.pack(side='right', padx=20)
        # l = tk.Label(loglabelframe, text='VJ{} Log'.format(j), font='Verdana 10 bold')
        # l.pack(side='right', padx=10)

        # l = tk.Label(loglabelframe, text='Log', font='Verdana 10 bold')
        # l.pack(side='top', padx=10)

        script1frame = tk.Frame(frame)
        script1frame.pack(side='left', expand=1, fill='both')
        script2frame = tk.Frame(frame)
        script2frame.pack(side='right', expand=1, fill='both')

        script1tbframe = tk.Frame(script1frame)
        script1tbframe.pack(side='top', fill='x')

        script1 = tk.Text(script1tbframe, width=10, height=3)
        self.vscroll['VJ'][1] = ttk.Scrollbar(script1tbframe, orient=tk.VERTICAL, command=script1.yview)
        self.hscroll['VJ'][1] = ttk.Scrollbar(script1tbframe, orient=tk.HORIZONTAL, command=script1.xview)
        script1['yscroll'] = self.vscroll['VJ'][1].set
        script1['xscroll'] = self.hscroll['VJ'][1].set
        self.vscroll['VJ'][1].pack(side="right", fill="y")
        self.hscroll['VJ'][1].pack(side="bottom", fill="x")
        script1.pack(fill='both', side='top', anchor='n')

        script2tbframe = tk.Frame(script2frame)
        script2tbframe.pack(side='top', fill='x')

        script2 = tk.Text(script2tbframe, width=10, height=3)
        self.vscroll['VJ'][2] = ttk.Scrollbar(script2tbframe, orient=tk.VERTICAL, command=script2.yview)
        self.hscroll['VJ'][2] = ttk.Scrollbar(script2tbframe, orient=tk.HORIZONTAL, command=script2.xview)
        script2['yscroll'] = self.vscroll['VJ'][2].set
        script2['xscroll'] = self.hscroll['VJ'][2].set
        self.vscroll['VJ'][2].pack(side="right", fill="y")
        self.hscroll['VJ'][2].pack(side="bottom", fill="x")
        script2.pack(fill='both', side='top', anchor='n')




        if self.vjtext[1] != None:
            script1.insert("1.0", self.vjtext[1])

        if self.vjtext[2] != None:
            script2.insert("1.0", self.vjtext[2])

        self.last_update['scripttextbox'][1] = script1
        self.last_update['scripttextbox'][2] = script2


        btm_ribbon = tk.Frame(tab)
        btm_ribbon.pack(side='top', fill='x')

        # right to left


        self.mirror[2] = False
        self.mirrorvar[2] = tk.StringVar(value='0')
        mirrorframe = tk.Frame(btm_ribbon)
        mirrorframe.pack(side='right', padx=10)
        tk.Label(mirrorframe, text="Mirror Input", font="Verdana 8").pack(side='top', fill='x')
        self.mirror_box[2] = ttk.Checkbutton(mirrorframe)
        self.mirror_box[2].bind("<Button-1>", lambda e: self.toggle_mirror(event=e, vj=2))
        self.mirror_box[2].pack(side='top')
        self.mirror_box[2].invoke()
        self.mirror_box[2].invoke()


        s = "Unplug" if self.on[1] else "Plug In"

        self.switch[1] = ttk.Button(btm_ribbon, text=s, width=12)
        self.switch[1].pack(side='left', anchor='sw', padx=5)
        self.switch[1].bind("<Button 1>", lambda e: self.toggle_controller(event=e, vj=1))

        self.mirror[1] = False
        self.mirrorvar[1] = tk.StringVar(value='0')
        mirrorframe = tk.Frame(btm_ribbon)
        mirrorframe.pack(side='left', padx=10)
        tk.Label(mirrorframe, text="Mirror Input", font="Verdana 8").pack(side='top', fill='x')
        self.mirror_box[1] = ttk.Checkbutton(mirrorframe)
        self.mirror_box[1].bind("<Button-1>", lambda e: self.toggle_mirror(event=e, vj=1))
        self.mirror_box[1].pack(side='top')
        self.mirror_box[1].invoke()
        self.mirror_box[1].invoke()



        s = "Unplug" if self.on[2] else "Plug In"

        self.switch[2] = ttk.Button(btm_ribbon, text=s, width=12)
        self.switch[2].pack(side='right', anchor='sw', padx=5)
        self.switch[2].bind("<Button 1>", lambda e: self.toggle_controller(event=e, vj=2))



    def pack_joy_cbs(self, tab):
        cbframe = tk.Frame(tab)
        cbframe.pack(side='top', fill='x')

        self.simulate_btn = ttk.Button(cbframe, text="Simulate")
        self.simulate_btn.bind("<Button 1>", self.play)
        self.simulate_btn.pack(side='right')

        self.repeat = False
        self.repeatvar = tk.StringVar(value='0')
        repeatframe = tk.Frame(cbframe)
        repeatframe.pack(side='right', padx=10)
        tk.Label(repeatframe, text="Repeat", font="Verdana 8").pack(side='top', fill='x')
        self.repeat_box = ttk.Checkbutton(repeatframe)
        self.repeat_box.bind("<Button-1>", self.toggle_repeat)
        self.repeat_box.pack(side='top')
        self.repeat_box.invoke()
        self.repeat_box.invoke()
        self.p2 = False
        self.p2var = tk.StringVar(value='0')
        p2frame = tk.Frame(cbframe)
        p2frame.pack(side='right', padx=10)
        tk.Label(p2frame, text="P2", font="Verdana 8").pack(side='top', fill='x')
        self.p2_box = ttk.Checkbutton(p2frame)
        self.p2_box.bind("<Button-1>", self.toggle_p2)
        self.p2_box.pack(side='top')
        self.p2_box.invoke()
        self.p2_box.invoke()
        self.p1 = False
        self.p1var = tk.StringVar(value='0')
        p1frame = tk.Frame(cbframe)
        p1frame.pack(side='right', padx=10)
        tk.Label(p1frame, text="P1", font="Verdana 8").pack(side='top', fill='x')
        self.p1_box = ttk.Checkbutton(p1frame)
        self.p1_box.bind("<Button-1>", self.toggle_p1)
        self.p1_box.pack(side='top')
        self.p1_box.invoke()
        self.p1_box.invoke()




    def pack_inputbox(self, tab, j=1):
        pjtitle = tk.Frame(tab)
        pjtitle.pack(side='top', fill='x')

        # l = tk.Label(pjtitle, text='PJoy', font='Verdana 10 bold')
        # l.pack(side='top', anchor='nw', padx=10)
        self.inputnote = ttk.Notebook(tab)
        self.inputnote.pack(side='top', expand=1, fill='both')
        self.inputnote.bind("<<NotebookTabChanged>>", self.switch_inputtype)
        pj_outframe = tk.Frame(self.inputnote)
        # pj_outframe.pack(side='top', expand=1, fill='both')
        self.inputnote.add(pj_outframe, text="String", compound='top')

        l = tk.Label(pj_outframe, text='String Input', font='Verdana 8 bold')
        l.pack(side='top', anchor='nw', padx=10)

        strtb = tk.Text(pj_outframe, background="#ffffff", state='disabled', height=3, width=20, wrap=tk.NONE)
        self.vscroll['INPstring'] = ttk.Scrollbar(pj_outframe, orient=tk.VERTICAL, command=strtb.yview)
        self.hscroll['INPstring'] = ttk.Scrollbar(pj_outframe, orient=tk.HORIZONTAL, command=strtb.xview)
        strtb['yscroll'] = self.vscroll['INPstring'].set
        strtb['xscroll'] = self.hscroll['INPstring'].set
        self.vscroll['INPstring'].pack(side="right", fill="y")
        self.hscroll['INPstring'].pack(side="bottom", fill="x")

        # strtb.bind("<ButtonPress-1>", self.scroll_start)
        # strtb.bind("<B1-Motion>", self.scroll_move)
        strtb.pack(fill='both',expand=1, side='top')
        self.last_update['str_inputtextbox'] = strtb

        rawframe = tk.Frame(self.inputnote)
        # pj_outframe.pack(side='top', expand=1, fill='both')
        self.inputnote.add(rawframe, text="Raw", compound='top')
        l = tk.Label(rawframe, text='Raw Input', font='Verdana 8 bold')
        l.pack(side='top', anchor='nw', padx=10)

        rinptb = tk.Text(rawframe, background="#ffffff", state='disabled', height=3, width=20, wrap=tk.NONE)
        self.vscroll['INPraw'] = ttk.Scrollbar(rawframe, orient=tk.VERTICAL, command=rinptb.yview)
        self.hscroll['INPraw'] = ttk.Scrollbar(rawframe, orient=tk.HORIZONTAL, command=rinptb.xview)
        rinptb['yscroll'] = self.vscroll['INPraw'].set
        rinptb['xscroll'] = self.hscroll['INPraw'].set
        self.vscroll['INPraw'].pack(side="right", fill="y")
        self.hscroll['INPraw'].pack(side="bottom", fill="x")

        # outtb.bind("<ButtonPress-1>", self.scroll_start)
        # outtb.bind("<B1-Motion>", self.scroll_move)
        rinptb.pack(fill='both',expand=1, side='top')
        self.last_update['raw_inputtextbox'] = rinptb

        fdframe = tk.Frame(self.inputnote)

        self.inputnote.add(fdframe, text='Frame', compound='top')
        l = tk.Label(fdframe, text='Frame Data', font='Verdana 8 bold')
        l.pack(side='top', anchor='nw', padx=10)
        # l = tk.Label(rawframe, text='Frame Input', font='Verdana 8 bold')
        # l.pack(side='top', anchor='nw', padx=10)
        self.last_update['fd_inputtable'] = fdframe
        fdtb = tk.Text(fdframe, background="#ffffff", state='disabled', height=3, width=20, wrap=tk.NONE)
        self.vscroll['INPfd'] = ttk.Scrollbar(fdframe, orient=tk.VERTICAL, command=fdtb.yview)
        self.hscroll['INPfd'] = ttk.Scrollbar(fdframe, orient=tk.HORIZONTAL, command=fdtb.xview)
        fdtb['yscroll'] = self.vscroll['INPfd'].set
        fdtb['xscroll'] = self.hscroll['INPfd'].set
        self.vscroll['INPfd'].pack(side="right", fill="y")
        self.hscroll['INPfd'].pack(side="bottom", fill="x")

        # outtb.bind("<ButtonPress-1>", self.scroll_start)
        # outtb.bind("<B1-Motion>", self.scroll_move)
        fdtb.pack(fill='both',expand=1, side='top')
        self.last_update['fd_inputtextbox'] = fdtb




        self.inpvarframe = tk.Frame(tab)
        self.inpvarframe.pack(side='top', fill='both', anchor='n')

        clearbtn = ttk.Button(self.inpvarframe, text='Clear', width=12)
        clearbtn.pack(side='top', anchor='ne', padx=5, pady=10)
        clearbtn.bind("<Button 1>", lambda e: self.delete_outtxt(event=e, type='INP', j=1))

        # s = 'View String' if self.raw_out['INP'][j] else 'View Raw'
        # self.rawbtn['INP'][j] = ttk.Button(self.inpvarframe, text=s, width=12)
        # self.rawbtn['INP'][j].pack(side='right', anchor='ne', padx=5)
        # self.rawbtn['INP'][j].bind("<Button 1>", lambda e: self.toggle_output_view(event=e, type='INP', j=1))

        # inptypevarframe = tk.Frame(self.inpvarframe)
        # inptypevarframe.pack(side='right', anchor='ne', padx=5)
        # tk.Label(inptypevarframe, text="View", font="Verdana 8").pack(side='top', fill='x')


    def pack_widgets(self):
        """Buttons to be displayed above sparsheets"""
        # tab widget
        tab = self.last_update['tab']
        # name of the loaded source
        name = self.last_update['name']
        # path of content, if loaded from a user's directory (important when save/load functionality re-added)
        source = self.last_update['source']

        self.last_update['scripttextbox'] = {1: None, 2: None}
        self.outdbtn = {'INP': None}


        self.vscroll = {'VJ': {1: None, 2: None}, 'INPstring': None, 'INPraw': None, 'INPfd': None}
        self.hscroll = {'VJ': {1: None, 2: None}, 'INPstring': None, 'INPraw': None, 'INPfd': None}
        self.switch = {}



        def delay_tuners_aa_allvjoys():
            # delay tuner frame
            vjtitle = tk.Frame(tab)
            vjtitle.pack(side='top', fill='x')
            # l = tk.Label(vjtitle, text='VJoy', font='Verdana 10 bold')
            # l.pack(side='top', anchor='n', padx=5, pady=5)

            delayvarlabframe = tk.Frame(tab)
            delayvarlabframe.pack(side='top', fill='x')
            l = tk.Label(delayvarlabframe, text="Delay Variables", width=20, font='Verdana 8')
            l.pack(side='left', padx=(30 * len(self.delay_tuners))/2, anchor='n', pady=5)


            self.delaytunerframe = tk.Frame(tab)
            self.delaytunerframe.pack(side='top', fill='x')
            self.binds = []

            dvd = int(self.digits)

            for iter, (notation, var) in enumerate(self.delay_tuners.items()):
                sb = tk.Spinbox(self.delaytunerframe, to=100.00, from_=0.00, textvariable=var, increment=float("0."+"".join(["0" for i in range(dvd-1)]) + "1"), width=dvd + 3, command=lambda: self.tune_var())
                bind = sb.bind('<Key>', self.tune_var)
                self.binds.append((sb, bind))
                l = tk.Label(self.delaytunerframe, text=notation, width=2, font='Verdana 8')
                l.pack(side='left', padx=5, anchor='n')
                sb.pack(side='left', padx=5, anchor='n')
                if iter == 0:
                    default_aavarname = notation


            # auto adjustment
            # aalabframe = tk.Frame(tab)
            # aalabframe.pack(side='top', fill='x', padx=30)

            tk.Label(delayvarlabframe, text="Freq.", font="Verdana 8").pack(side='right', padx=15)
            tk.Label(delayvarlabframe, text="Val.", font="Verdana 8").pack(side='right', padx=25)
            tk.Label(delayvarlabframe, text="Var.", font="Verdana 8").pack(side='right', padx=35)
            tk.Label(delayvarlabframe, text="Auto Adjustment", font="Verdana 8").pack(side='right', padx=0)
            # self.aaframe = tk.Frame(tab)
            # self.aaframe.pack(side='top', fill='x')

            state = 'normal' if self.aa_enabled == True else 'disabled'
            enabbtn_name = 'Enable' if not self.aa_enabled else 'Disable'

            self.aafreqsb = tk.Spinbox(self.delaytunerframe, to=1000, from_=0, textvariable=self.aafreq, increment=1, width=int(self.digits) + 3, state=state)
            self.aafreqsb.pack(side='right', padx=5)

            self.aavalsb = tk.Spinbox(self.delaytunerframe, to=0.1, from_=-0.1, textvariable=self.aaval, increment=float("0."+"".join(["0" for i in range(dvd-1)]) + "1"), width=int(self.digits) + 3, state=state)
            self.aavalsb.pack(side='right', padx=5)

            self.auto_adjbox = ttk.Combobox(self.delaytunerframe, width=8, values=[var for var in list(self.delay_tuners)], textvariable=self.aavar, state=state)
            self.auto_adjbox.pack(side='right', padx=5)
            self.auto_adjbox.set(default_aavarname)

            self.enable_aa_btn = ttk.Button(self.delaytunerframe, text=enabbtn_name, width=8, state='normal')
            self.enable_aa_btn.pack(side='right', padx=55)
            self.enable_aa_btn.bind("<Button 1>", lambda e: self.toggle_aa(event=e))

        def separator():
            sepframe = tk.Frame(tab, height=10)
            sepframe.pack(side='top', fill='x', anchor='n', pady=5)
            sep = ttk.Separator(sepframe, orient='horizontal').pack(side='top', fill='x', expand=1, anchor='nw')


        delay_tuners_aa_allvjoys()

        separator()

        self.pack_joy_textboxes(tab)
        separator()
        self.pack_joy_cbs(tab)
        separator()
        self.pack_inputbox(tab)


    # run this function every rep
    def make_auto_adjustment(self):
        var = self.aavar.get()
        aval = self.aaval.get()

        current_val = self.delay_tuners[var].get()

        if self.aa_enabled:
            self.delay_tuners[var].set(str(round(float(current_val) + float(aval), self.digits)))

            self.tune_var()

    def delete_outtxt(self, j=1, type='VJ'):
        for tb in [self.last_update['str_inputtextbox'], self.last_update['raw_inputtextbox'], self.last_update['fd_inputtextbox']]:
            tb.config(state='normal')
            tb.delete("1.0", tk.END)
            tb.config(state='disabled')



    def tune_var(self, event=None):
        try:
            dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
        except Exception as e:
            pass
            # print("tune_var error: ", e)
        # print("tune var! dt: ", dt)
        for i in [1,2]:
            self.ui_j["VJ"][i].put({'delay vars': dt})


    def track_change_to_text(event):
        text.tag_add("here", "1.0", "1.4")
        text.tag_config("here", background="black", foreground="green")


    def new_file(self, source=None, name=None):
        # try:
        #     self.note.forget(self.note.select())
        # except:
        #     pass

        tab = tk.Frame(self)
        self.last_update = {'name': name, 'source': source, 'tab': tab, 'VJ': {i:{} for i in [1,2]}, 'INP': {}}

        # name = "file" if name == None else name
        # self.note.add(tab, text = name, compound='top')
        tab.pack(expand=1, fill='both')
        self.pack_widgets()



    def open_file(self, lastsess=None):
        def readFile(filename):
            f = open(filename, "r")
            text = f.read()
            return text

        if lastsess:
            # self.note = ttk.Notebook(self)
            # self.note.pack(fill='both', expand=1)
            self.new_file()
            return

        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes = ftypes)
        #path = filedialog.askdirectory()
        fl = dlg.show()

        if fl != '':
            docname = fl.split("/")[-1].split(".")[0]
            self.new_file(name=docname, source=fl) #, text=readFile(fl)


    def toggle_controller(self, vj=1, event=None):
        if self.on[vj]:
            # self.hks_on = False

            self.on[vj] = False
            print("self.on[1] = {}, self.on[2] = {}".format(self.on[1], self.on[2]))
            s = "On"
            info = {'playing': False, 'vjoy on': False, 'once': False}
            self.ui_j["VJ"][vj].put(info)
            self.j_ui["VJ"][vj].put(info)
            if all([not self.on[1], not self.on[2]]):
                print("disable simulate_btn")
                self.simulate_btn.config(state='disabled')

        elif not self.on[vj]:
            # print("vjoy on")

            self.simulate_btn.config(state='normal')
            info = {'playing': False, 'vjoy on': True, 'settings': self.settings, 'actcfg': self.act_cfg, 'facing': self.dir, 'once': False}
            s = "Off"
            self.ui_j["VJ"][vj].put(info)
            self.on[vj] = True
            print("self.on[1] = {}, self.on[2] = {}".format(self.on[1], self.on[2]))

        else:
            messagebox.showerror(title='Error', message='An error occurred when changing the state of your virtual controller.')
            return

        self.switch[vj].config(text="Turn VJoy {}".format(s))


    def toggle_mirror(self, event, vj=1):
        if self.mirrorvar[vj].get() == '1':
            self.mirrorvar[vj].set("0")
            self.mirror[vj] = False
            dir = 'R' if self.default_dir == 'R' else 'L'
            # print("mirror = False")
        else:
            self.mirrorvar[vj].set("1")
            self.mirror[vj] = True
            # print("mirror = True")
            dir = 'L' if self.default_dir == 'R' else 'R'

        info = {'facing': dir}
        self.dir = dir
        self.ui_j["VJ"][vj].put(info)


    def toggle_aa(self, event=None):
        if self.aa_enabled == True:
            self.aa_enabled = False
            self.enable_aa_btn.config(text="Enable")
            self.aavalsb.config(state='disabled')
            self.auto_adjbox.config(state='disabled')
            self.aafreqsb.config(state='disabled')
        else:
            self.aa_enabled = True
            self.enable_aa_btn.config(text="Disable")
            self.aavalsb.config(state='normal')
            self.auto_adjbox.config(state='normal')
            self.aafreqsb.config(state='normal')

    def toggle_p1(self, event):
        if self.p1var.get() == '1':
            self.p1var.set("0")
            self.p1 = False
            # print("p1 = False")
        else:
            self.p1var.set("1")
            self.p1 = True
            # print("p1 = True")

    def toggle_p2(self, event):
        if self.p2var.get() == '1':
            self.p2var.set("0")
            self.p2 = False
            # print("p2 = False")
        else:
            self.p2var.set("1")
            self.p2 = True
            # print("p2 = True")


    # DEPRECATED

    # # toggles ability to see output actions from PJoy & VJoy
    # def toggle_output(self, j=1, event=None):
    #     if self.out_disabled == True:
    #         self.out_disabled = False
    #         self.outdbtn.config(text="Disable Out")
    #         # self.play1btn[j].config(state='disabled')
    #     else:
    #         self.out_disabled = True
    #         self.outdbtn.config(text="Enable Log")
    #         # self.play1btn[j].config(state='normal')

    def toggle_repeat(self, event):
        if self.repeatvar.get() == '1':
            self.repeatvar.set("0")
            self.repeat = False
            # print("repeat = False")
        else:
            self.repeatvar.set("1")
            self.repeat = True
            # print("repeat = True")

    # plays notation script on repeat (separated by start delay) until stopped (stop command)
    def play(self, event=None):
        repeat = True if self.repeatvar.get() == '1' else False

        for vj in [1,2]:
            if vj == 1:
                p = self.p1
            else:
                p = self.p2

            intb = self.last_update['scripttextbox'][vj]


            if event == None:
                self.simulate_btn.unbind("<Button 1>")
            self.simulate_btn.config(text = "Stop")
            self.simulate_btn.bind("<Button 1>", self.stop)


            lasttxt = intb.get("1.0", "end").splitlines()[0]

            if not self.simulating[vj] and p:
                self.simulating[vj] = True

                self.simulating_once[vj] = False if repeat else True
                # print("playing once: ", once)
                res = self.refresh()
                if not res:
                    if event == None:
                        self.simulate_btn.unbind("<Button 1>")
                    self.simulate_btn.config(text = "Simulate")
                    self.simulate_btn.bind("<Button 1>", self.play)
                    return

                # split by space
                moveslist = lasttxt.split(" ")
                actlist = []

                for i in moveslist:
                    # pre configs: predelays
                    for ind, _d in enumerate(list(self.delay_tuners)):
                        #print"ind: {}; _d: {}".format(ind, _d))
                        if i == _d:
                            actlist.append((_d, ["delay({})".format(_d)]))

                    # print("i: ", i)

                    for k,v in self.act_cfg.items():
                        if i == v["Notation"]:
                            if v["String"] != None:
                                actlist.append((i, v["String"]))
                            break

                dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
                # print("DT: ", dt)
                info1 = {'playing': self.simulating[vj], 'settings': self.settings, 'actlist': actlist,'actcfg': self.act_cfg, 'facing': self.dir, 'delay vars': dt, 'once': self.simulating_once[vj]} #, 'hks enabled': self.hotkeys_enabled}

                if len(actlist) == 0:
                    self.stop(vj=vj)
                    self.j_ui["VJ"][vj].put({'error': 'No actions were found in your Notation Script.'})
                    return

                # self.highlight_script()

                self.rep = 0

                self.ui_j['VJ'][vj].put(info1)




    def view_device_report(self):
        with open(HID_REPORT, "w") as f:
            try:
                hid.core.show_hids(output = f)
            except Exception as e:
                print("HID Error: ", e)
            f.close()

        with open(HID_REPORT, "r") as hidr:
            self.hid_report = str(hidr.read())
            hidr.close()

        info = {'hid report': self.hid_report, 'vj report': self.vj_report, 'pj report': self.pj_report}

        report = tools.DeviceReport(self, info)

    # next version?
    # def view_graph(self):
    #     if self.logging == True:
    #         self.logger.update_displays()
    #         self.logger.view_log()
    #     else:
    #         messagebox.showerror(title='Error', message='The log box is not checked.')
    #         return

    def view_user_guide(self):
        ug = tools.User_Guide(self, USERGUIDE)


    def view_community(self):
        webbrowser.open('https://www.reddit.com/r/Sparlab/', new=2)

    def settings_editor(self):
        popup = tools.Settings(self, self.settingsfile)

    def action_editor(self):
        popup = tools.Action_Editor(self, DATAPATH)

    def view_license(self):
        popup = tools.License(self, LICENSE)

    def view_anticheatpolicy(self):
        popup = tools.AntiCheatPolicy(self, ANTICHEATPOLICY)


    def switch_inputtype(self, event):
        newtype = event.widget.tab(event.widget.select(), "text")
        try:
            oldtype = self.outtype

            if newtype == 'String':
                tb = self.last_update["str_inputtextbox"]
            elif newtype == 'Raw':
                tb = self.last_update["raw_inputtextbox"]
            elif newtype == 'Frame':
                tb = self.last_update["fd_inputtextbox"]

            if newtype in ['String', 'Raw']:
                # if oldtype == 'Frame Data':
                #     self.game_hook.stop_overlay()
                self.outtype = newtype

            else:
                if not self.game_hook.running:
                    res = self.game_hook.start_overlay(tb)
                    if res != 1:
                        messagebox.showerror(title='Error', message=res)
                        self.inptypebox.set(oldtype)

                self.outtype = newtype

            info = {'inputtype': self.outtype}

            for i in range(1, 3):
                self.j_ui['VJ'][i].put(info)
            self.j_ui['INP'].put(info)
        except Exception as e:
            print("switch input type error: ", e)

    def stop(self, event=None):
        self.simulate_btn.bind("<Button 1>", self.play)
        self.simulating = {1: False, 2: False}
        self.simulating_once = {1: False, 2: False}
        self.ui_j["VJ"][1].put({'playing': False})
        self.ui_j["VJ"][2].put({'playing': False})
        self.simulate_btn.config(text='Simulate')

    def enable_btn(self, btn):
        btn.config(state='normal')


    # deprecated, may add later
    # def save_as(self, log=False):
    #     #print"save test")
    #     if not log:
    #         tb = self.last_update['notestextbox']
    #         name = self.last_update["name"]
    #     else:
    #         tb = self.last_update['vj1inputtextbox']
    #         name = "log-{}".format(str(datetime.today().strftime('%Y-%m-%d')))
    #
    #
    #     txt = tb.get("1.0", tk.END).splitlines()
    #     txt = "\n".join(txt)
    #     #print"split line text: ", txt)
    #     #src = self.frames[tab][-1]
    #
    #     # check if there is source for the text box, if yes, write to source else pull up Save As window
    #     ftypes = [('Text files', '*.txt'), ('All files', '*')]
    #
    #     f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=ftypes, title=name)
    #
    #     if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
    #         return
    #     try:
    #         with open(f, "w") as file:
    #             file.write(txt)
    #             file.close()
    #     except FileNotFoundError as e:
    #         print("save as file not found: ", e)
    #     except Exception as e:
    #         self.vj1_ui.put({'error': "There was an error while saving your file in the path '{}'.".format(f)})
    #
    #     tab = self.last_update["tab"]
    #     newtabname = str(f).split("/")[-1]
    #     self.note.tab(tab, text=newtabname)

    # This function will only work with an updater.py file.
    def check_for_update(self, booting=False):
        try:
            res, link, v = updater.check_for_update(str(__version__))
            if res == True:

                yn = messagebox.askyesno(title="New Update Available", message="Would you like to visit our downloads page to download Sparlab version {}?".format(v))
                if yn == True:
                    webbrowser.open('https://www.umensch.com/downloads/', new=2)
                else:
                    return

            else:
                if booting == False:
                    messagebox.showinfo(title="", message="No update is currently available.")
        except:
            pass



def save_session():
    try:
        dts = {k:float(v.get()) for k,v in root.delay_tuners.items()}
        d = ChainMap(*[{'delay_vars': dts, 'auto adjustment': {'variable': root.aavar.get(), 'value': root.aaval.get(), 'frequency': root.aafreq.get()}}, \
        dict([('vjtext', dict([(j, root.last_update[j]['scripttextbox'].get("1.0", tk.END)) for j in range(1, 3)]))])])
        with open(DATAPATH + "\\" + "lastsession.txt", "w") as f:
            f.write(str(d))
            f.close()
    except Exception as e:
        print("EXCEPTION WHEN SAVING SESSION: ", e)
    sys.exit()


if __name__ == '__main__':
    freeze_support()
    # # communication from UI to VJ1

    try:
        root = App()
    except Exception as e:
        print("ROOT = APP() ERROR: ", e)
    root.protocol("WM_DELETE_WINDOW", save_session)
    processes = {}

    # setup parallel processes

    root.ui_j = ui_j = {'VJ': {1: Queue(), 2: Queue()},
                        'INP': Queue()}
    root.j_ui = j_ui = {'VJ': {1: Queue(), 2: Queue()},
                        'INP': Queue()}

    root.post_init()


    for i in range(1, 3):
        args = (ui_j['VJ'][i], j_ui['VJ'][i], i)

        processes[i] = _input.Inputter(args=args)
        processes[i].daemon = True
        processes[i].start()

    # # setup parallel processes
    # args = (ui_vj2, vj2_ui, vj2_vj1, vj1_vj2, 2, True)
    # # setup_inputter(args)
    # inp2 = _input.Inputter(args=args)
    # inp2.daemon = True
    # inp2.start()

    ui_pj = root.ui_j['INP']
    pj_ui = root.j_ui['INP']


    args = (pj_ui, ui_pj, root.pjoy_type, HID_REPORT)
    out = _output.Outputter(args=args)
    out.daemon = True
    out.start()

    try:
        root.mainloop()
        # print("running mainloop")
    except Exception as e:
        print("ROOT MAINLOOP EXCEPTION: ", e)
