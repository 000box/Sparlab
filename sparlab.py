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
from datetime import datetime
import hook.hid as hid

__version__ = '1.0.62'

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
                print("syntax")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))
            except FileNotFoundError:
                print("adding new action path: ", path)
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
                    print("error ({}) when adding new action path ({})".format(e, path))
                    messagebox.showerror(title="Warning", message='action file with path {} was not able to be appended ({})'.format(path, e))

            except Exception as e:
                print("other")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))

        self.act_cfg = dict(ChainMap(*imports))
        vjoys = self.settings['# of Virtual Joysticks']
        if vjoys > self.vjoys and vjoys < 2:
            diff = vjoys - self.vjoys
            for i in range(diff):
                self.ui_j['VJ'][self.vjoys + i] = qout = Queue()
                self.j_ui['VJ'][self.vjoys + i] = qin = Queue()

                # distribute new queue to each inputter process, these queues are for sending info to not yet built process
                # send queue to all processes except the not yet built process (hence the len(vjoys) MINUS 1)
                me_opps = {i: Queue() for i in range(1, vjoys - 1)}
                for k,v in me_opps.items():
                    self.ui_j['VJ'][k].put({'new contact': v})
                # distribute new queue to each inputter process, these queues are for receiving info from not yet built process
                opps_me = {i: Queue() for i in range(1, vjoys - 1)}
                for k,v in opps_me.items():
                    self.ui_j['VJ'][k].put({'new mailman': v})

                vj_info = {'ui_j': qout, 'j_ui': qin, 'me_opps': me_opps, 'opps_me': opps_me}
                self.pack_vjoy(self.last_update["tab"], j=self.vjoys + i, newvj_info=vj_info)
            self.vjoys = vjoys
        elif vjoys < self.vjoys and vjoys > 1:
            diff = self.vjoys - vjoys
            for i in range(diff):
                self.ui_j['VJ'][self.vjoys - i].put({'quit': True})
                del self.ui_j['VJ'][self.vjoys - i]
                del self.j_ui['VJ'][self.vjoys - i]



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

        for i in range(1, self.vjoys + 1):
            self.ui_j["VJ"][i].put(info)

        for i in range(1, self.pjoys + 1):
            self.ui_j["PJ"][i].put(info)


        return True


    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Sparlab")
        tk.Tk.iconbitmap(self, default=ICON)
        self.geometry('{}x{}'.format(750, 550))
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
                print("syntax")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))
            except FileNotFoundError:
                print("adding new action path: ", path)
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
                    print("error ({}) when adding new action path ({})".format(e, path))
                    messagebox.showerror(title="Warning", message='action file with path {} was not able to be appended ({})'.format(path, e))

            except Exception as e:
                print("other")
                messagebox.showerror(title="Warning", message='action file with path {} was not able to be imported ({})'.format(path, e))


        self.act_cfg = dict(ChainMap(*imports))

        # self.hks_on = False
        self.on = dict([(j, False) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])])
        self.vjoys = self.settings['# of Virtual Joysticks']
        self.pjoys = self.settings['# of Physical Joysticks']
        if self.vjoys > 2:
            self.vjoys = 2

        # self.hotkeys_enabled = False
        self.out_disabled = {'VJ': dict([(j, False) for j in range(1, 1 + self.vjoys)]), 'PJ': dict([(j, False) for j in range(1, 1 + self.pjoys)])}
        self.aa_enabled = False
        self.rep = 0
        self.digits = self.settings['delay variable # of decimals']
        self.vjtext = {i: None for i in range(1, self.vjoys + 1)}

        try:
            self.pjoy_type = self.settings['physical joy type']
            self.default_dir = self.settings['default direction']
            self.dir = self.settings['default direction']

        except TypeError as e:
            messagebox.showerror(title="Error", message=e)



    def post_init(self):
        self.playing = {i: False for i in range(1, self.vjoys + 1)}
        self.playing_once = {i: False for i in range(1, self.vjoys + 1)}
        self.all_playing = False

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
            print("error ({}) when attempting to load lastsession.txt".format(e))
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
        for i in range(1, 1 + self.vjoys):
            self.after(200, lambda joy=i, tp='VJ': self.info_from_joy(j=joy, _type=tp))
            self.ui_j['VJ'][i].put({'settings': self.settings})
        for i in range(1, 1 + self.pjoys):
            self.after(200, lambda joy=i, tp='PJ': self.info_from_joy(j=joy, _type=tp))
            self.ui_j['PJ'][i].put({'settings': self.settings})

        self.check_for_update(booting=True)


    def info_from_joy(self, j=1, _type='VJ'):

        outtb = self.last_update[_type][j]['outputtextbox']
        # intb = self.last_update[_type][j]['inputtextbox']
        q = self.j_ui[_type][j]

        while q.qsize():
            try:
                info = q.get(0)
                # print("info: ", info)

                if info != None and outtb != None:
                    print("info: ", info)
                    outtb.config(state='normal')
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
                        print("351 startover: ", startover)
                        print("joy: {}, a: {}, startover: {}".format(joy, a, startover))

                    except KeyError as e:
                        print("355 keyerror: ", e)
                        # print("355 e: ", e)
                    except Exception as e:
                        print("358 e: ", e)
                        # print("258: ", e)
                    try:
                        if startover:
                            if self.playing[j] and _type == 'VJ':
                                self.rep += 1
                            char0 = "{}.0".format(int(float(outtb.index(tk.INSERT))))
                            outtb.see(char0)
                            if self.rep % int(self.aafreq.get()) == 0 and self.playing[j] and _type == 'VJ':
                                self.make_auto_adjustment()

                        if not self.out_disabled[_type][j]:
                            # ins = str(self.rep) + ": " if startover else ""
                            print("insert: ", a)
                            outtb.insert(tk.INSERT, a)

                        outtb.see(tk.END)

                    except KeyError as e:
                        # pass
                        print("377 KEY ERROR: ", e)
                    except UnboundLocalError as e:
                        pass
                        # print("380 ULE ERROR: ", e)
                        # print("ULE ERROR: ", e)
                    except TypeError as e:
                        print("383 Type ERROR: ", e)
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
                        rep = info['rep']
                        if rep == 0:
                            self.rep += 1
                        joy = info['joy']
                        if not self.out_disabled[_type][j]:
                            outtb.insert(tk.INSERT, str(self.rep) + ": " + r)
                            char0 = "{}.0".format(int(float(outtb.index(tk.END))))
                            outtb.see(char0)
                    except KeyError:
                        pass
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    outtb.config(state='disabled')

                    try:
                        facing = info['facing']
                        if self.dir != facing:
                            self.toggle_xaxis()
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
                            self.stop(once=self.playing_once[j], vj=j, from_vj=True, all=self.all_playing)
                        elif playing == True:
                            self.play(once=self.playing_once[j], vj=j, all=self.all_playing)
                    except Exception as e:
                        # msg = "{}: {}".format(type(e).__name__, e.args)
                        # print("PLAYING EXCEPTION: ", e)
                        pass
            except Exception as e:
                msg = "{} ERROR: {}: {}".format(j, type(e).__name__, e.args)
                print(msg)

        self.after(200, lambda joy=j, t=_type: self.info_from_joy(j=joy, _type=t))


    #enable scrolling with mouse (to make it more app-like on other devices) in future version?
    def scroll_start(self, event):
        event.widget.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        event.widget.scan_dragto(event.x, event.y)


    # def highlight_script(self):
    #     """
    #     run this function in loop
    #     """
    #     box = self.last_update["vj1textbox"]
    #     tag_name = "color-yellow"
    #     try:
    #         box.tag_config(tag_name, background='yellow')
    #         lb = box.search("[", "1.0", tk.END)
    #         if not lb:
    #             return
    #         rb = box.search("] ", "1.0", "2.0")
    #         if not rb:
    #             return
    #         box.tag_add(tag_name, lb, rb)
    #     except KeyError as e:
    #         print("keyerror highlight script: ", e)
    #     except TypeError as e:
    #         print("typeerror highlight script: ", e)

    # next version
    # def highlight_notation(self, notation, ind):
    #     box = self.last_update["vj1textbox"]
    #     tag_name = "color-green"
    #     try:
    #         box.tag_delete(tag_name)
    #     except:
    #         pass
    #
    #     box.tag_config(tag_name, background='#42f448')
    #
    #     if ind == 0:
    #         self.c_index = box.index("1.1")
    #
    #     start = self.c_index
    #     self.rb_index = box.search(']', start, tk.END)
    #     end = box.tag_nextrange(tag_name, "1.0", "end-1c")[1]
    #     char1 = box.search(notation, start, end)
    #     char2 = str(float(char1) + 0.1)
    #     if self.playing == True:
    #         box.tag_add(tag_name, char1, box.index(char2))




    # def highlight_if_scripted(self, event):
    #     box = event.widget
    #     tag_name = "color-yellow"
    #     try:
    #         box.tag_delete(tag_name)
    #     except:
    #         pass
    #
    #     box.tag_config(tag_name, background='yellow')
    #     lb = box.search("[", "1.0", tk.INSERT)
    #     if not lb:
    #         return
    #     self.rb_index = rb = box.search("]", tk.INSERT, tk.END)
    #     if not rb:
    #         return
    #
    #     box.tag_add(tag_name, lb, str(float(rb) + 0.1))

        # next version

        # highlight recognized notations

        # tag_name = 'color-green'
        # box.tag_config(tag_name, background='#42f448')
        #
        # try:
        #     box.tag_remove(tag_name, "1.0", tk.END)
        # except:
        #     pass
        #
        # allnotations = [self.act_cfg[i]['Notation'] for i in list(self.act_cfg)]
        #
        # for notation in allnotations:
        #     found_n = box.search(notation, tk.INSERT, rb, exact=True, forwards=True)
        #     if found_n:
        #         box.tag_add(tag_name, found_n)
        #     found_n = box.search(notation, lb, tk.INSERT, exact=True, backwards=True)
        #     if found_n:
        #         box.tag_add(tag_name, found_n)
        #
        # # remove any tags if necessary
        # for range in box.tag_ranges(tag_name):
        #     if range not in allnotations:
        #         print("range: ", range)



    def add_tab(self, name = None):
        """ Each Sparsheet is a tab with a built-in text editor and assigned hotkey"""

        self.note = ttk.Notebook(self)

        # app always opens on this sheet
        self.new_file(name=name)
        self.note.pack(fill='both', expand=1)
        # self.note.grid(column=0, row=0, sticky='nsew')


    def create_top_menu(self):
        """ Menu at top of app """

        self.menu = tk.Menu(self, tearoff=False)
        self.config(menu=self.menu)
        filemenu = tk.Menu(self, tearoff=False)
        editmenu = tk.Menu(self, tearoff=False)
        togmenu = tk.Menu(self, tearoff=False)
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
            if k in ['File', 'Edit', 'Tools', 'Help']:
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



    def pack_vjoy(self, tab, j=1, newvj_info=None):
        if newvj_info:
            new_inputter(newvj_info)

        frame = tk.Frame(tab)
        frame.pack(side='top', fill='both')

        labelframe = tk.Frame(frame)
        labelframe.pack(side='top', fill='x')
        scriptlabelframe = tk.Frame(labelframe)
        scriptlabelframe.pack(side='left', fill='x')
        loglabelframe = tk.Frame(labelframe)
        loglabelframe.pack(side='right', fill='x')
        l = tk.Label(scriptlabelframe, text='VJ{} Script'.format(j), font='Verdana 10 bold')
        l.pack(side='left', padx=10)

        l = tk.Label(loglabelframe, text='VJ{} Log'.format(j), font='Verdana 10 bold')
        l.pack(side='right', padx=10)

        # l = tk.Label(loglabelframe, text='Log', font='Verdana 10 bold')
        # l.pack(side='top', padx=10)

        scriptframe = tk.Frame(frame)
        scriptframe.pack(side='left', expand=1, fill='both')
        scripttbframe = tk.Frame(scriptframe)
        scripttbframe.pack(side='top', fill='x')

        script = tk.Text(scripttbframe, width=10, height=3)
        self.vscroll['VJ'][j] = ttk.Scrollbar(scripttbframe, orient=tk.VERTICAL, command=script.yview)
        self.hscroll['VJ'][j] = ttk.Scrollbar(scripttbframe, orient=tk.HORIZONTAL, command=script.xview)
        script['yscroll'] = self.vscroll['VJ'][j].set
        script['xscroll'] = self.hscroll['VJ'][j].set
        self.vscroll['VJ'][j].pack(side="right", fill="y")
        self.hscroll['VJ'][j].pack(side="bottom", fill="x")
        script.pack(fill='both', side='top', anchor='n')

        if self.vjtext[j] != None:
            script.insert("1.0", self.vjtext[j])

        self.last_update["VJ"][j]['inputtextbox'] = script

        logframe = tk.Frame(frame)
        logframe.pack(side='right', fill='both', expand=1)
        logtbframe = tk.Frame(logframe)
        logtbframe.pack(side='top', fill='x')

        # vj1_outframe = tk.Frame(tab)
        # vj1_outframe.pack(side='right', expand=1, fill='both', anchor='nw')
        outtb = tk.Text(logtbframe, background="#ffffff", state='disabled', height=3, width=10, wrap=tk.NONE)
        self.vscroll['VJ'][j] = ttk.Scrollbar(logtbframe, orient=tk.VERTICAL, command=outtb.yview)
        self.hscroll['VJ'][j] = ttk.Scrollbar(logtbframe, orient=tk.HORIZONTAL, command=outtb.xview)
        outtb['yscroll'] = self.vscroll['VJ'][j].set
        outtb['xscroll'] = self.hscroll['VJ'][j].set
        self.vscroll['VJ'][j].pack(side="right", fill="y")
        self.hscroll['VJ'][j].pack(side="bottom", fill="x")
        # outtb.bind("<ButtonPress-1>", self.scroll_start)
        # outtb.bind("<B1-Motion>", self.scroll_move)
        outtb.pack(fill='both', anchor='n', side='top')
        self.last_update['VJ'][j]['outputtextbox'] = outtb

        scriptbtnframe = tk.Frame(scriptframe)
        scriptbtnframe.pack(side='top', anchor='n', fill='x')

        self.playloopbtn[j] = ttk.Button(scriptbtnframe, text = "Simulate Loop", width=15, state='normal' if self.on[j] else 'disabled')
        self.playloopbtn[j].pack(side='left', anchor='sw', padx=5)
        self.playloopbtn[j].bind("<Button 1>", lambda e: self.play(event=e, vj=j))

        state = 'normal' if all([self.on[j], not self.out_disabled['VJ'][j]]) else 'disabled'

        self.play1btn[j] = ttk.Button(scriptbtnframe, text="Simulate Once", state=state, width=15)
        self.play1btn[j].pack(side='left', anchor='sw', padx=5)
        self.play1btn[j].bind("<Button 1>", lambda e: self.play(event=e, vj=j, once=True))
        s = "Off" if self.on[j] == True else "On"

        self.switch[j] = ttk.Button(scriptbtnframe, text="Turn VJoy {}".format(s), width=12)
        self.switch[j].pack(side='left', anchor='sw', padx=5)
        self.switch[j].bind("<Button 1>", lambda e: self.toggle_controller(event=e, vj=j))

        logbtnframe = tk.Frame(logframe)
        logbtnframe.pack(side='bottom', fill='x')
        clearbtn = ttk.Button(logbtnframe, text='Clear', width=12)
        clearbtn.pack(side='right', anchor='ne', padx=5)
        clearbtn.bind("<Button 1>", lambda e: self.delete_outtxt(event=e, type='VJ', j=j))

        s = 'View String' if self.raw_out['VJ'][j] else 'View Raw'
        self.rawbtn['VJ'][j] = ttk.Button(logbtnframe, text=s, width=12)
        self.rawbtn['VJ'][j].pack(side='right', anchor='ne', padx=5)
        self.rawbtn['VJ'][j].bind("<Button 1>", lambda e: self.toggle_output_view(event=e, type='VJ', j=j))
        s = 'Enable Log' if self.out_disabled['VJ'][j] else 'Disable Log'
        self.outdbtn['VJ'][j] = ttk.Button(logbtnframe, text=s, width=12)
        self.outdbtn['VJ'][j].pack(side='right', anchor='ne', padx=5)
        self.rawbtn['VJ'][j].bind("<Button 1>", lambda e: self.toggle_output(event=e, type='VJ', j=j))

    def pack_pj(self, tab, j=1):
        pjtitle = tk.Frame(tab)
        pjtitle.pack(side='top', fill='x')

        # l = tk.Label(pjtitle, text='PJoy', font='Verdana 10 bold')
        # l.pack(side='top', anchor='nw', padx=10)

        pj_outframe = tk.Frame(tab)
        pj_outframe.pack(side='top', expand=1, fill='both', anchor='n')

        l = tk.Label(pj_outframe, text='PJ{} Log'.format(j), font='Verdana 10 bold')
        l.pack(side='top', anchor='nw', padx=10)

        outtb = tk.Text(pj_outframe, background="#ffffff", state='disabled', height=3, width=20, wrap=tk.NONE)
        self.vscroll['PJ'][j] = ttk.Scrollbar(pj_outframe, orient=tk.VERTICAL, command=outtb.yview)
        self.hscroll['PJ'][j] = ttk.Scrollbar(pj_outframe, orient=tk.HORIZONTAL, command=outtb.xview)
        outtb['yscroll'] = self.vscroll['PJ'][j].set
        outtb['xscroll'] = self.hscroll['PJ'][j].set
        self.vscroll['PJ'][j].pack(side="right", fill="y")
        self.hscroll['PJ'][j].pack(side="bottom", fill="x")
        # outtb.bind("<ButtonPress-1>", self.scroll_start)
        # outtb.bind("<B1-Motion>", self.scroll_move)
        outtb.pack(fill='both',expand=1, side='top')
        self.last_update['PJ'][j]['outputtextbox'] = outtb

        self.outvarframe = tk.Frame(tab)
        self.outvarframe.pack(side='top', fill='x', anchor='n')

        clearbtn = ttk.Button(self.outvarframe, text='Clear', width=12)
        clearbtn.pack(side='right', anchor='ne', padx=5)
        clearbtn.bind("<Button 1>", lambda e: self.delete_outtxt(event=e, type='PJ', j=1))

        s = 'View String' if self.raw_out['PJ'][j] else 'View Raw'
        self.rawbtn['PJ'][j] = ttk.Button(self.outvarframe, text=s, width=12)
        self.rawbtn['PJ'][j].pack(side='right', anchor='ne', padx=5)
        self.rawbtn['PJ'][j].bind("<Button 1>", lambda e: self.toggle_output_view(event=e, type='PJ', j=1))

        s = 'Enable Log' if self.out_disabled['PJ'][j] else 'Disable Log'
        self.outdbtn['PJ'][j] = ttk.Button(self.outvarframe, text=s, width=12)
        self.outdbtn['PJ'][j].pack(side='right', anchor='ne', padx=5)
        self.outdbtn['PJ'][j].bind("<Button 1>", lambda e: self.toggle_output(event=e, type='PJ', j=1))


    def pack_widgets(self):
        """Buttons to be displayed above sparsheets"""
        # tab widget
        tab = self.last_update['tab']
        # name of the loaded source
        name = self.last_update['name']
        # path of content, if loaded from a user's directory (important when save/load functionality re-added)
        source = self.last_update['source']


        self.outdbtn = {'VJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Physical Joysticks'])])}
        self.rawbtn =  {'VJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Physical Joysticks'])])}
        self.raw_out =  {'VJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Physical Joysticks'])])}
        self.play1btn = dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])])
        self.playloopbtn = dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])])
        self.vscroll = {'VJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Physical Joysticks'])])}
        self.hscroll = {'VJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, None) for j in range(1, 1 + self.settings['# of Physical Joysticks'])])}
        self.switch = {}



        def delay_tuners_aa_allvjoys():
            # delay tuner frame
            vjtitle = tk.Frame(tab)
            vjtitle.pack(side='top', fill='x')
            # l = tk.Label(vjtitle, text='VJoy', font='Verdana 10 bold')
            # l.pack(side='top', anchor='n', padx=5, pady=5)

            delayvarlabframe = tk.Frame(tab)
            delayvarlabframe.pack(side='top', fill='x')
            l = tk.Label(delayvarlabframe, text="Delay Variables:", width=20, font='Verdana 10')
            l.pack(side='left', padx=(30 * len(self.delay_tuners))/2, anchor='n', pady=5)


            self.delaytunerframe = tk.Frame(tab)
            self.delaytunerframe.pack(side='top', fill='x')
            self.binds = []
            # l = tk.Label(self.delaytunerframe, text='Delay Variables:', font='Verdana 10')
            # l.pack(side='left', anchor='n', padx=5, pady=5)
            dvd = int(self.digits)

            for iter, (notation, var) in enumerate(self.delay_tuners.items()):
                sb = tk.Spinbox(self.delaytunerframe, to=100.00, from_=0.00, textvariable=var, increment=float("0."+"".join(["0" for i in range(dvd-1)]) + "1"), width=dvd + 3, command=lambda: self.tune_var())
                bind = sb.bind('<Key>', self.tune_var)
                self.binds.append((sb, bind))
                l = tk.Label(self.delaytunerframe, text=notation, width=2, font='Verdana 10')
                l.pack(side='left', padx=5, anchor='n')
                sb.pack(side='left', padx=5, anchor='n')
                if iter == 0:
                    default_aavarname = notation


            # auto adjustment
            # aalabframe = tk.Frame(tab)
            # aalabframe.pack(side='top', fill='x', padx=30)

            tk.Label(delayvarlabframe, text="Freq.").pack(side='right', padx=15)
            tk.Label(delayvarlabframe, text="Val.").pack(side='right', padx=25)
            tk.Label(delayvarlabframe, text="Var.").pack(side='right', padx=35)
            tk.Label(delayvarlabframe, text="Auto Adjustment").pack(side='right', padx=0)
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

        def master_btns():
            mastervjframe = tk.Frame(tab)
            mastervjframe.pack(side='top', fill='x', pady=5)
            self.master_playloopbtn = ttk.Button(mastervjframe, text = "Simulate Both Loops", width=18, state='normal' if all([self.on[i] for i in range(1, self.vjoys + 1)]) else 'disabled')
            self.master_playloopbtn.pack(side='left', anchor='nw', padx=5)
            self.master_playloopbtn.bind("<Button 1>", lambda e: self.play(event=e, all=True))


            state = 'normal' if all([self.on[i] for i in range(1, 1 + self.vjoys)]) else 'disabled'

            self.master_play1btn = ttk.Button(mastervjframe, text="Simulate Both Once", state=state, width=18)
            self.master_play1btn.pack(side='left', anchor='nw', padx=5)
            self.master_play1btn.bind("<Button 1>", lambda e: self.play(event=e, once=True, all=True))

            s = "Flip X Axis" if self.dir == self.default_dir else "Unflip X Axis"
            # self.dirstatuslab = tk.Label(vj1_btnframe, text='XFlip')

            # self.xa_sb = tk.Checkbutton(vj1_btnframe, onvalue=1, offvalue=0, textvariable=self.xavar, command=lambda: self.toggle_xaxis())
            self.xa_sb = ttk.Button(mastervjframe, text=s, width=12)
            # self.dirstatuslab.pack(side='left', anchor="ne", padx=15)
            self.xa_sb.pack(side='left', anchor='nw', padx=5)
            self.xa_sb.bind("<Button 1>", lambda e: self.toggle_xaxis(event=e))



        delay_tuners_aa_allvjoys()

        separator()

        for i in range(1, 1 + self.vjoys):
            self.pack_vjoy(tab, j=i)
            separator()

        master_btns()
        separator()

        for i in range(1, 1 + self.pjoys):
            self.pack_pj(tab, j=i)

    # run this function every rep
    def make_auto_adjustment(self):
        var = self.aavar.get()
        aval = self.aaval.get()

        current_val = self.delay_tuners[var].get()

        if self.aa_enabled:
            self.delay_tuners[var].set(str(round(float(current_val) + float(aval), self.digits)))

            self.tune_var()

    def delete_outtxt(self, j=1, type='VJ'):
        self.last_update[type][j]['outputtextbox'].config(state='normal')
        self.last_update[type][j]['outputtextbox'].delete("1.0", tk.END)
        self.last_update[type][j]['outputtextbox'].config(state='disabled')


    def tune_var(self, event=None):
        try:
            dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
        except Exception as e:
            print("tune_var error: ", e)
        # print("tune var! dt: ", dt)
        for i in range(1, 1+self.vjoys):
            self.ui_j["VJ"][i].put({'delay vars': dt})


    def track_change_to_text(event):
        text.tag_add("here", "1.0", "1.4")
        text.tag_config("here", background="black", foreground="green")


    def new_file(self, source=None, name=None):
        try:
            self.note.forget(self.note.select())
        except:
            pass

        tab = tk.Frame(self.note)
        self.last_update = {'name': name, 'source': source, 'tab': tab, 'VJ': {i:{} for i in range(1, 1+self.vjoys)}, 'PJ': {i:{} for i in range(1, 1+self.pjoys)}}

        name = "file" if name == None else name
        self.note.add(tab, text = name, compound='top')

        self.pack_widgets()



    def open_file(self, lastsess=None):
        def readFile(filename):
            f = open(filename, "r")
            text = f.read()
            return text

        if lastsess:
            self.note = ttk.Notebook(self)
            self.note.pack(fill='both', expand=1)

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
            self.playloopbtn[vj].config(state='disabled')
            self.play1btn[vj].config(state='disabled')
            self.on[vj] = False
            s = "On"
            info = {'playing': False, 'both': False, 'vjoy on': False, 'once': False}
            self.ui_j["VJ"][vj].put(info)
            self.j_ui["VJ"][vj].put(info)
            self.play1btn[vj].config(state='disabled')
            self.playloopbtn[vj].config(state='disabled')
            self.master_play1btn.config(state='disabled')
            self.master_playloopbtn.config(state='disabled')
        elif not self.on[vj]:
            # print("vjoy on")
            self.playloopbtn[vj].config(state='normal')
            self.play1btn[vj].config(state='normal')
            info = {'playing': False, 'both': False, 'vjoy on': True, 'settings': self.settings, 'actcfg': self.act_cfg, 'facing': self.dir, 'once': False}
            s = "Off"
            self.ui_j["VJ"][vj].put(info)
            self.on[vj] = True

            if all([self.on[j] for j in range(1, 1+self.vjoys)]):
                self.master_play1btn.config(state='normal')
                self.master_playloopbtn.config(state='normal')

        else:
            messagebox.showerror(title='Error', message='An error occurred when changing the state of your virtual controller.')
            return

        self.switch[vj].config(text="Turn VJoy {}".format(s))



    def toggle_xaxis(self, event=None):
        if self.dir == self.default_dir:
            dir = 'L' if self.default_dir == 'R' else 'R'
            self.xa_sb.config(text="Unflip X Axis")
        else:
            dir = 'R' if self.default_dir == 'R' else 'L'
            self.xa_sb.config(text="Flip X Axis")
        self.dir = dir
        info = {'facing': dir}
        for vj in range(1, 1 + self.vjoys):
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

    # for user to configure joystick
    def toggle_output_view(self, type='VJ', j=1, event=None):
        if self.raw_out[type][j]:
            self.raw_out[type][j] = raw_out = False
            self.rawbtn[type][j].config(text='View Raw')
        else:
            self.raw_out[type][j] = raw_out = True
            self.rawbtn[type][j].config(text='View String')

        info = {'raw output': raw_out}
        self.ui_j[type][j].put(info)


    # toggles ability to see output actions from PJoy & VJoy
    def toggle_output(self, j=1, event=None):
        if self.out_disabled[j] == True:
            self.out_disabled[j] = False
            self.outdbtn[j].config(text="Disable Out")
            # self.play1btn[j].config(state='disabled')
        else:
            self.out_disabled[j] = True
            self.outdbtn[j].config(text="Enable Log")
            # self.play1btn[j].config(state='normal')


    # plays notation script on repeat (separated by start delay) until stopped (stop command)
    def play(self, event=None, once=False, vj=1, all=False):
        if event != None:
            event.widget.unbind("<Button-1>")
        if not all:
            intb = self.last_update["VJ"][vj]['inputtextbox']

            if not once:
                if event == None:
                    self.playloopbtn[vj].unbind("<Button 1>")
                self.playloopbtn[vj].config(text = "Stop Loop")
                self.playloopbtn[vj].bind("<Button 1>", lambda e: self.stop(event=e, vj=vj))
                # self.after(200, lambda btn=self.playloopbtn[vj]: self.enable_btn(btn))
                self.play1btn[vj].config(state='disabled')
            else:
                if event == None:
                    self.play1btn[vj].unbind("<Button 1>")
                self.play1btn[vj].config(text = "Stop")
                self.play1btn[vj].bind("<Button 1>", lambda e: self.stop(event=e, vj=vj, once=True))
                # self.after(200, lambda btn=self.play1btn[vj]: self.enable_btn(btn))
                self.playloopbtn[vj].config(state='disabled')

            lasttxt = intb.get("1.0", "end").splitlines()[0]

            if not self.playing[vj]:
                self.playing[vj] = True
                self.playing_once[vj] = once
                print("playing once: ", once)
                res = self.refresh()
                if not res:
                    if not once:
                        if event == None:
                            self.playloopbtn[vj].unbind("<Button 1>")
                        self.playloopbtn[vj].config(text = "Simulate Loop")
                        self.playloopbtn[vj].bind("<Button 1>", lambda e: self.play(event=e, vj=vj))
                    else:
                        if event == None:
                            self.play1btn[vj].unbind("<Button 1>")
                        self.play1btn[vj].config(text="Simulate Once")
                        self.play1btn[vj].bind("<Button 1>", lambda e: self.stop(event=e, vj=vj, once=True))
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

                    print("i: ", i)

                    for k,v in self.act_cfg.items():
                        if i == v["Notation"]:
                            if v["String"] != None:
                                actlist.append((i, v["String"]))
                            break

                dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
                # print("DT: ", dt)
                info1 = {'playing': self.playing[vj], 'both': False, 'settings': self.settings, 'actlist': actlist,'actcfg': self.act_cfg, 'facing': self.dir, 'delay vars': dt, 'once': self.playing_once[vj]} #, 'hks enabled': self.hotkeys_enabled}
                # print("preplay INFO: ", info)
                # print("PLAYING: ", actlist)
                if len(actlist) == 0:
                    self.stop(once=self.playing_once[vj], vj=vj)
                    self.j_ui["VJ"][vj].put({'error': 'No actions were found in your Notation Script.'})
                    return

                # self.highlight_script()

                self.rep = 0

                self.ui_j['VJ'][vj].put(info1)

        if all:
            if once:
                if event == None:
                    self.master_play1btn.unbind("<Button 1>")
                self.master_play1btn.config(text="Stop")
                self.master_play1btn.bind("<Button 1>", lambda e: self.stop(event=e, all=True, once=True))
                # self.after(200, lambda btn=self.master_play1btn: self.enable_btn(btn))
                self.master_playloopbtn.config(state='disabled')
            else:
                if event == None:
                    self.master_playloopbtn.unbind("<Button 1>")
                self.master_playloopbtn.unbind("<Button 1>")
                self.master_playloopbtn.config(text = "Stop")
                self.master_playloopbtn.bind("<Button 1>", lambda e: self.stop(event=e, all=True))
                # self.after(200, lambda btn=self.master_playloopbtn: self.enable_btn(btn))
                self.master_play1btn.config(state="disabled")

            for j in range(1, 1 + self.vjoys):
                self.playing[j] = True
                if once:
                    self.playing_once[j] = True
                self.play1btn[j].config(state='disabled')
                self.play1btn[j].config(state='disabled')
                self.playloopbtn[j].config(state='disabled')
                self.playloopbtn[j].config(state='disabled')


            vjtext = [(j, self.last_update["VJ"][j]['inputtextbox'].get("1.0", tk.END).splitlines()[0]) for j in range(1, 1 + self.vjoys)]

            if not self.all_playing:
                self.all_playing = True
                res = self.refresh()
                if res == False:
                    if not once:
                        self.master_playloopbtn.config(text = "Simulate Both Loops", command=lambda: self.play(all=True))
                    else:
                        self.master_play1btn.config(text="Simulate Both Once", command=lambda: self.play(once=True, all=True))
                    for j in range(1, 1 + self.vjoys):
                        self.play1btn[vj].config(state='normal')
                        self.play1btn[vj].config(state='normal')
                        self.playloopbtn[vj].config(state='normal')
                        self.playloopbtn[vj].config(state='normal')
                    return

                # split by space
                for j, text in vjtext:
                    moveslist = text.split(" ")
                    actlist = []

                    for i in moveslist:
                        # pre configs: predelays
                        for ind, _d in enumerate(list(self.delay_tuners)):
                            #print"ind: {}; _d: {}".format(ind, _d))
                            if i == _d:
                                actlist.append((_d, ["delay({})".format(_d)]))

                        print("i: ", i)

                        for k,v in self.act_cfg.items():
                            if i == v["Notation"]:
                                if v["String"] != None:
                                    actlist.append((i, v["String"]))
                                break

                    dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
                    # print("DT: ", dt)
                    info = {'playing': self.playing[j], 'both': True, 'settings': self.settings, 'actlist': actlist,'actcfg': self.act_cfg, 'facing': self.dir, 'delay vars': dt, 'once': self.playing_once[j]}

                    self.ui_j["VJ"][j].put(info)



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


    def stop(self, event=None, once=False, vj=1, all=False, from_vj=False):
        if event != None:
            event.widget.unbind("<Button 1>")

        if self.playing[vj] or self.all_playing:
            if not all:
                self.ui_j["VJ"][vj].put({'playing': False, 'both': False, 'once': False})
                if not once:
                    if event == None:
                        self.playloopbtn[vj].unbind("<Button 1>")
                    print("vj{} stop1".format(vj))
                    self.playloopbtn[vj].config(text='Simulate Loop', state='normal')
                    self.playloopbtn[vj].bind("<Button 1>", lambda e: self.play(event=e, vj=vj))
                    self.play1btn[vj].config(state='normal')
                    self.playloopbtn[vj].config(state='normal')
                    # self.play1btn[vj].config(state='disabled')
                    # self.after(200, lambda btn=self.playloopbtn[vj]: self.enable_btn(btn))
                    # self.after(200, lambda btn=self.play1btn[vj]: self.enable_btn(btn))

                else:
                    if event == None:
                        self.play1btn[vj].unbind("<Button 1>")
                    print("vj{} stop2".format(vj))
                    self.play1btn[vj].config(text='Simulate Once', state='normal')
                    self.play1btn[vj].bind("<Button-1>", lambda e: self.play(event=e, once=True, vj=vj))
                    self.playloopbtn[vj].config(state='normal')
                    self.play1btn[vj].config(state='normal')
                    # self.playloopbtn[vj].config(state='disabled')
                    # self.after(200, lambda btn=self.play1btn[vj]: self.enable_btn(btn))
                    # self.after(200, lambda btn=self.playloopbtn[vj]: self.enable_btn(btn))

                self.playing[vj] = False
                self.playing_once[vj] = False

            if all:
                self.all_playing = False

                if once:
                    if event == None:
                        self.master_play1btn.unbind("<Button 1>")
                    self.master_play1btn.config(text="Simulate Both Once", state='normal')
                    self.master_play1btn.bind("<Button 1>", lambda e: self.play(event=e, all=True, once=True))
                    self.master_playloopbtn.config(state='normal')
                    # self.after(200, lambda btn=self.master_play1btn: self.enable_btn(btn))
                    # self.after(200, lambda btn=self.master_playloopbtn: self.enable_btn(btn))
                else:
                    if event == None:
                        self.master_playloopbtn.unbind("<Button 1>")
                    self.master_playloopbtn.config(text="Simulate Both Loops", state='normal')
                    self.master_playloopbtn.bind("<Button-1>", lambda e: self.play(event=e, all=True))
                    self.master_play1btn.config(state='normal')
                    # self.after(200, lambda btn=self.master_playloopbtn: self.enable_btn(btn))
                    # self.after(200, lambda btn=self.master_play1btn: self.enable_btn(btn))

                for j in range(1, 1 + self.vjoys):
                    self.play1btn[j].config(state='normal')
                    self.playloopbtn[j].config(state='normal')
                    self.playing[j] = False
                    self.playing_once[j] = False
                    self.ui_j["VJ"][j].put({'playing': False, 'both': False})


    def enable_btn(self, btn):
        btn.config(state='normal')


    # deprecated, may add later
    # def save_as(self, log=False):
    #     #print"save test")
    #     if not log:
    #         tb = self.last_update['notestextbox']
    #         name = self.last_update["name"]
    #     else:
    #         tb = self.last_update['vj1outputtextbox']
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


def new_inputter(info):
    # pass list of communications (queues):
    # ui_j, j_ui,
    # {'ui_j': Queue(), 'j_ui': Queue(), 'me_opps': [Queue(), Queue(), ...], 'opps_me': [Queue(), Queue(), ...]}
    args = (ui_vj1, vj1_ui, vj1_vj2, vj2_vj1, 1, False)
    # setup_inputter(args)
    inp1 = _input.Inputter(args=args)
    inp1.daemon = True
    inp1.start()



def save_session():
    try:
        dts = {k:float(v.get()) for k,v in root.delay_tuners.items()}
        d = ChainMap(*[{'delay_vars': dts, 'auto adjustment': {'variable': root.aavar.get(), 'value': root.aaval.get(), 'frequency': root.aafreq.get()}}, \
        dict([('vjtext', dict([(j, root.last_update["VJ"][j]['inputtextbox'].get("1.0", tk.END)) for j in range(1, 1 + root.vjoys)]))])])
        with open(DATAPATH + "\\" + "lastsession.txt", "w") as f:
            f.write(str(d))
            f.close()
    except Exception as e:
        print("EXCEPTION WHEN SAVING SESSION: ", e)
    sys.exit()


if __name__ == '__main__':
    freeze_support()
    # # communication from UI to VJ1
    # ui_vj1 = Queue()
    # # communication from UI to VJ2
    # ui_vj2 = Queue()
    # # communication from VJ1 to UI
    # vj1_ui = Queue()
    # # communication from VJ2 to UI
    # vj2_ui = Queue()
    # # communication from UI to PJoy
    # ui_pj = Queue()
    # # communication from PJoy to UI
    # pj_ui = Queue()
    # # communication from vj1 to vj2
    # vj1_vj2 = Queue()
    # # communication from vj2 to vj1
    # vj2_vj1 = Queue()

    root = App()
    root.protocol("WM_DELETE_WINDOW", save_session)
    processes = {}
    # setup parallel processes
    vjoys = root.vjoys

    root.ui_j = ui_j = {'VJ': dict([(j, Queue()) for j in range(1, 1 + root.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, Queue()) for j in range(1, 1 + root.settings['# of Physical Joysticks'])])}
    root.j_ui = j_ui = {'VJ': dict([(j, Queue()) for j in range(1, 1 + root.settings['# of Virtual Joysticks'])]), \
                        'PJ': dict([(j, Queue()) for j in range(1, 1 + root.settings['# of Physical Joysticks'])])}

    me_opp = Queue()
    opp_me = Queue()

    root.post_init()

    for i in range(1, vjoys + 1):
        if i == 1:
            is_opp = False
            args = (ui_j['VJ'][i], j_ui['VJ'][i], me_opp, opp_me, i, is_opp)
        else:
            is_opp = True
            args = (ui_j['VJ'][i], j_ui['VJ'][i], opp_me, me_opp, i, is_opp)


        processes[i] = _input.Inputter(args=args)
        processes[i].daemon = True
        processes[i].start()

    # # setup parallel processes
    # args = (ui_vj2, vj2_ui, vj2_vj1, vj1_vj2, 2, True)
    # # setup_inputter(args)
    # inp2 = _input.Inputter(args=args)
    # inp2.daemon = True
    # inp2.start()

    ui_pj = root.ui_j['PJ']
    pj_ui = root.j_ui['PJ']
    pjoys = root.pjoys
    for i in range(1, 1 + pjoys):
        args = (pj_ui[i], ui_pj[i], root.pjoy_type, HID_REPORT)
        out = _output.Outputter(args=args)
        out.daemon = True
        out.start()
        root.mainloop()
