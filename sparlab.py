import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
import updater
import _input
import _output
from multiprocessing import Queue, freeze_support
import webbrowser
from collections import ChainMap
import tools
import sys
from datetime import datetime

__version__ = '1.0.5'

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
        """ After user presses play or Refresh, this function will be called"""
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
                self.q3.put({"warning": 'action file with path {} was not able to be imported ({})'.format(path, e)})
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
                    self.q3.put({"warning": 'action file with path {} was not able to be appended ({})'.format(path, e)})

            except Exception as e:
                print("other")
                self.q3.put({"warning": 'action file with path {} was not able to be imported ({})'.format(path, e)})

        self.act_cfg = dict(ChainMap(*imports))

        # set stringvars
        try:
            self.vjoy_type = self.settings['virtual joy type']
            self.pjoy_type = self.settings['physical joy type']
            self.fps = int(self.settings['fps'])
            self.port = int(self.settings["virtual joy port"])
            self.default_dir = self.settings['default direction']
            # self.log_type = self.settings['log type']
        except TypeError as e:
            messagebox.showerror(title="Error", message=e)

        dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
        info = {'settings': self.settings, 'actcfg': self.act_cfg, 'delay vars': dt, 'hks enabled': self.hotkeys_enabled}
        self.q1.put(info)
        self.q4.put(info)

        tb = root.last_update['intextbox']
        txt = tb.get("1.0", tk.END).splitlines()
        txt = "\n".join(txt)
        name = root.last_update["name"]
        src = root.last_update['source']
        dts = {k:float(v.get()) for k,v in root.delay_tuners.items()}
        d = {'text': txt, 'source': src, 'name': name, 'delay_vars': dts}
        with open(DATAPATH + "\\" + "lastsession.txt", "w") as f:
            f.write(str(d))
            f.close()

        return True


    def __init__(self, q1, q2, q3, q4):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Sparlab")
        tk.Tk.iconbitmap(self, default=ICON)
        self.geometry('{}x{}'.format(750, 400))
        self.configure(background="#ffffff")

        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4

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
                self.q3.put({"warning": 'action file with path {} was not able to be imported ({})'.format(path, e)})
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
                    self.q3.put({"warning": 'action file with path {} was not able to be appended ({})'.format(path, e)})

            except Exception as e:
                print("other")
                self.q3.put({"warning": 'action file with path {} was not able to be imported ({})'.format(path, e)})

        self.act_cfg = dict(ChainMap(*imports))


        self.playing = False
        self.hks_on = False
        self.raw_out = False
        self.joy_is_on = False
        self.hotkeys_enabled = False
        self.out_disabled = False

        try:
            self.vjoy_type = self.settings['virtual joy type']
            self.pjoy_type = self.settings['physical joy type']
            self.fps = int(self.settings['fps'])
            # self.action_interval_t = float(self.settings['Fixed Delay'])
            # self.start_delay_t = float(self.settings['Start Delay'])
            self.port = int(self.settings["virtual joy port"])
            self.default_dir = self.settings['default direction']
            self.dir = self.settings['default direction']
            # self.outfeedmaxchars = int(self.settings['outfeed max characters'])
            self.vjoy_txtcolor = self.settings['virtual joy text color']
            self.pjoy_txtcolor = self.settings['physical joy text color']
            # self.dna = self.settings['default neutral allowance']
            # self.log_type = self.settings['log type']

        except TypeError as e:
            messagebox.showerror(title="Error", message=e)

        try:

            with open(DATAPATH + "\\" + "lastsession.txt", "r") as f:
                ls = eval(f.read())
                self.delay_tuners = {i: tk.StringVar(value=ls['delay_vars'][i]) for i in self.settings['Delay Variables']}
                self.open_file(lastsess=ls)
                f.close()
        except FileNotFoundError:

            try:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in eval(self.settings['Delay Variables'])}
            except:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in self.settings['Delay Variables']}

            self.add_tab()
        except Exception as e:
            print("error ({}) when attempting to load lastsession.txt".format(e))
            try:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in eval(self.settings['Delay Variables'])}
            except:
                self.delay_tuners = {i:tk.StringVar(value=0.0) for i in self.settings['Delay Variables']}

            self.add_tab()


        self.create_top_menu()
        # queue getters
        self.processIncoming()
        self.after(100, self.processIncoming3)
        self.q4.put({'settings': self.settings})

        self.check_for_update(booting=True)


    def processIncoming(self):
        while self.q2.qsize():
            try:
                info = self.q2.get(0)
                #print("info from session: ", info)
                if info != None:
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
                        messagebox.showerror(title="Warning", message=info['error'])
                    except KeyError:
                        pass
                    try:
                        playing = info['playing']
                        if playing == False:
                            #print("q2 pause")
                            self.pause()
                        elif playing == True:
                            #print("q2 play")
                            self.play()
                    except Exception as e:
                        msg = "{}: {}".format(type(e).__name__, e.args)
                        #print(msg)

                    try:
                        hk_act = info['hk action']
                        #print("hotkey: ", hk_act)
                    except Exception as e:
                        pass

                    try:
                        e = info['error']
                        messagebox.showerror(title='Error', message=e)
                    except KeyError as e:
                        pass


            except Exception as e:
                msg = "{}: {}".format(type(e).__name__, e.args)
                #print("Q2 EXCEPTION: ", msg)

        self.after(200, self.processIncoming)

    def processIncoming3(self):
        while self.q3.qsize():
            try:
                info = self.q3.get(0)
                # print("info: ", info)
                outtb = self.last_update['outtextbox']
                intb = self.last_update['intextbox']
                if info != None and outtb != None:
                    # print("info: ", info)
                    outtb.config(state='normal')
                    # next version
                    try:
                        self.pj_report = info['pjoy report']
                    except KeyError:
                        pass
                    try:
                        joy = info['joy']
                        if joy == 'pjoy':
                            color = self.pjoy_txtcolor
                        elif joy == 'vjoy':
                            color = self.vjoy_txtcolor
                        tag_name = "color-" + color
                        outtb.tag_configure(tag_name, foreground=color)

                        joy = info["joy"]
                        a = info['action']
                        # n_chars = outtb.count("1.0", tk.INSERT)
                        startover = info['start over']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("258: ", e)
                    try:
                        if not self.out_disabled:

                            if startover:
                                char0 = "{}.0".format(int(float(outtb.index(tk.INSERT))))
                                outtb.see(char0)

                            outtb.insert(tk.INSERT, a, tag_name)
                            outtb.see(tk.END)

                    except KeyError as e:
                        pass
                    except UnboundLocalError as e:
                        pass
                        # print("ULE ERROR: ", e)
                    except TypeError as e:
                        pass
                    except Exception as e:
                        print("OTHER ERROR: ", e)
                        messagebox.showerror(title='Error', message=e)

                    try:
                        w = info['warning']
                        messagebox.showerror(title='Warning', message=w)
                    except KeyError:
                        pass
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    try:
                        e = info['error']
                        print("ERROR: ", e)
                        messagebox.showerror(title='Error', message=e)
                    except KeyError:
                        pass
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    try:
                        r = info['raw']
                        joy = info['joy']
                        if joy == 'pjoy':
                            color = self.pjoy_txtcolor
                        elif joy == 'vjoy':
                            color = self.vjoy_txtcolor
                        tag_name = "color-" + color
                        outtb.tag_configure(tag_name, foreground=color)

                        if self.out_disabled == False:
                            outtb.insert(tk.INSERT, r, tag_name)
                            char0 = "{}.0".format(int(float(outtb.index(tk.END))))
                            outtb.see(char0)
                    except KeyError:
                        pass
                    except Exception as e:
                        messagebox.showerror(title='Error', message=e)

                    outtb.config(state='disabled')

            except Exception as e:
                msg = "Q3 ERROR: {}: {}".format(type(e).__name__, e.args)
                print(msg)

        self.after(200, self.processIncoming3)


    #enable scrolling with mouse (to make it more app-like on other devices) in future version?
    def scroll_start(self, event):
        event.widget.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        event.widget.scan_dragto(event.x, event.y)


    def highlight_script(self):
        """
        run this function in loop
        """
        box = self.last_update["intextbox"]
        tag_name = "color-yellow"
        try:
            box.tag_config(tag_name, background='yellow')
            lb = box.search("[", "1.0", tk.END)
            if not lb:
                return
            rb = box.search("] ", "1.0", tk.END)
            if not rb:
                return
            box.tag_add(tag_name, lb, rb)
        except KeyError as e:
            print("keyerror highlight script: ", e)
        except TypeError as e:
            print("typeerror highlight script: ", e)

    # next version
    # def highlight_notation(self, notation, ind):
    #     box = self.last_update["intextbox"]
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




    def highlight_if_scripted(self, event):
        box = event.widget
        tag_name = "color-yellow"
        try:
            box.tag_delete(tag_name)
        except:
            pass

        box.tag_config(tag_name, background='yellow')
        lb = box.search("[", "1.0", tk.INSERT)
        if not lb:
            return
        self.rb_index = rb = box.search("]", tk.INSERT, tk.END)
        if not rb:
            return

        box.tag_add(tag_name, lb, str(float(rb) + 0.1))

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

        self.submenus = {'File': (filemenu, [('New', self.new_file,None ), ('Open', self.open_file, None),
                        ('Save Script', self.save_as, None),('Save Log', self.save_as, True),('Refresh', self.refresh, None),
                        ('Exit', self.destroy, None)]),
                        'Edit': (editmenu, [('Settings', self.settings_editor, None), ("Action Editor", self.action_editor, None)]),
                        'Tools': (toolmenu, [('Device Report', self.view_device_report, None),('Toggle VJoy', self.toggle_controller, None),
                        ('Toggle X Axis ', self.toggle_xaxis, None), ('Enable/Disable Log', self.toggle_output, None),   #('Play', self.play, None),
                        ('Toggle Hotkeys', self.toggle_hotkeys, None), ('Log String/Raw', self.toggle_output_view, None)]),
                        'Help': (helpmenu, [('User Guide', self.view_user_guide, None), ('License', self.view_license, None), ('Anti-Cheat Policy', self.view_anticheatpolicy, None),
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


    def pack_widgets(self):
        """Buttons to be displayed above sparsheets"""

        tab = self.last_update['tab']
        name = self.last_update['name']
        text = self.last_update['text']
        source = self.last_update['source']


        # if vars != None:
        #     # self.aivar.set(vars['aivar'])
        #     # self.sdvar.set(vars['sdvar'])
        #     # self.navar = tk.StringVar(vars['navar'])
        # else:
        #     self.aivar = tk.StringVar(value=str(self.action_interval_t))
            # self.sdvar = tk.StringVar(value=str(self.start_delay_t))

        btnframe = tk.Frame(tab)

        btnframe.pack(side='top', anchor='n', fill='x')


        self.initButton = btn = ttk.Button(btnframe, text = "Play", width=12, command=lambda: self.play(), state='normal' if self.joy_is_on else 'disabled')
        self.initButton.pack(side='right', anchor='ne', padx=5)
        l = tk.Label(btnframe, text='Script', font='Verdana 10 bold')
        l.pack(side='left', anchor='nw', padx=10)


        s = "Off" if self.joy_is_on == True else "On"
        # self.joystatuslab = tk.Label(btnframe, text="VJoy Status: {}".format(s))
        #
        # self.vj_sb = tk.Checkbutton(btnframe, onvalue=1, offvalue=0, textvariable=self.vjvar, command=lambda: self.toggle_controller())
        self.vj_sb = ttk.Button(btnframe, text="Turn VJoy {}".format(s), command=lambda: self.toggle_controller(), width=12)
        # self.joystatuslab.pack(side='left', anchor="ne")
        self.vj_sb.pack(side='right', anchor='ne', padx=5)

        s = "Flip X Axis" if self.dir == self.default_dir else "Unflip X Axis"
        # self.dirstatuslab = tk.Label(btnframe, text='XFlip')

        # self.xa_sb = tk.Checkbutton(btnframe, onvalue=1, offvalue=0, textvariable=self.xavar, command=lambda: self.toggle_xaxis())
        self.xa_sb = ttk.Button(btnframe, text=s, command=lambda: self.toggle_xaxis(), width=12)
        # self.dirstatuslab.pack(side='left', anchor="ne", padx=15)
        self.xa_sb.pack(side='right', anchor='ne', padx=5)

        s = "Enable HKs" if self.hotkeys_enabled == False else "Disable HKs"
        # self.hkstatuslab = tk.Label(btnframe, text='HKs')
        # self.hk_sb = tk.Checkbutton(btnframe, onvalue=1, offvalue=0, textvariable=self.hkvar, command=lambda: self.toggle_hotkeys())
        self.hk_sb = ttk.Button(btnframe, text=s, command=lambda: self.toggle_hotkeys(), width=12)
        # self.hkstatuslab.pack(side='left', anchor="ne", padx=15)
        self.hk_sb.pack(side='right', anchor='ne', padx=5)

        savelogbtn = ttk.Button(btnframe, text='Save Script', width=12, command=lambda: self.save_as())
        savelogbtn.pack(side='right', anchor='ne', padx=5)


        inframe = tk.Frame(tab)
        inframe.pack(side='top', expand=1, fill='both', anchor='nw')

        txt = tk.Text(inframe, background="#ffffff", height=5, width=20, wrap=tk.NONE)
        vscroll = tk.Scrollbar(inframe, orient=tk.VERTICAL, command=txt.yview)
        hscroll = tk.Scrollbar(inframe, orient=tk.HORIZONTAL, command=txt.xview)
        txt['yscroll'] = vscroll.set
        txt['xscroll'] = hscroll.set
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")

        txt.pack(fill='both', expand=1, side='top', anchor='n')
        txt.bind('<Key>',self.highlight_if_scripted)

        self.last_update['intextbox'] = txt
        if text == None:
            txt.insert("1.0", "[]")
        else:
            txt.insert("1.0", text)

        # delay tuner frame
        self.delaytunerframe = tk.Frame(tab)
        self.delaytunerframe.pack(side='top', fill='x', anchor='n')

        l = tk.Label(self.delaytunerframe, text='Delay Variables:', font='Verdana 10')
        l.pack(side='left', anchor='n', padx=5, pady=5)

        for iter, (notation, var) in enumerate(self.delay_tuners.items()):
            if notation not in ['fps', 'Fixed Delay', 'Start Delay']:
                l = tk.Label(self.delaytunerframe, text=notation, width=2, font='Verdana 10')
                l.pack(side='left', padx=5, anchor='n', pady=5)

                sb = tk.Spinbox(self.delaytunerframe, to=100.00, from_=0.00, textvariable=var, increment=0.001, width=6, command=lambda: self.tune_var())
                sb.bind('<Key>',self.tune_var)
                sb.pack(side='left', padx=5, anchor='n', pady=5)

        delframe = tk.Frame(tab)
        delframe.pack(side='top', fill='x', anchor='n')

        # self.sdtuner = tk.Spinbox(delframe, to=100.00, from_=0.00, textvariable=self.sdvar, increment=0.001, width=6, command=lambda: self.tune_var())
        # self.sdtuner.bind('<Key>',self.tune_var)

        # deprecated for now (might add in future version)
        # l = tk.Label(delframe, text='Start Delay (s):', font='Verdana 10')
        # l.pack(side='left', anchor='n', padx=5, pady=5)
        # self.sdtuner.pack(side='left', anchor='n', pady=5)
        # self.delay_tuners['Start Delay'] = self.sdvar


        # self.aituner = tk.Spinbox(delframe, to=100.00, from_=0.00, textvariable=self.aivar, increment=0.001, width=6, command=lambda: self.tune_var())
        # self.aituner.bind('<Key>',self.tune_var)
        # l = tk.Label(delframe, text='Fixed Delay (s)', font='Verdana 10')
        # l.pack(side='left', anchor='n', padx=5, pady=5)
        # self.aituner.pack(side='left', anchor='n', pady=5)
        # self.delay_tuners['Fixed Delay'] = self.aivar

        sepframe = tk.Frame(tab)
        sepframe.pack(side='top', fill='x', anchor='n')
        sep = ttk.Separator(sepframe, orient='horizontal').pack(side='top', fill='x', expand=1, anchor='nw')

        # for next version?
        # outhelpframe = tk.Frame(tab)
        # outhelpframe.pack(side='top', fill='x', expand=1, anchor='n')
        # self.ohelpbox = tk.Text(outhelpframe, state='disabled')
        # self.ohelpbox.pack(fill='both', expand=1)


        self.outvarframe = tk.Frame(tab)
        self.outvarframe.pack(side='top', fill='x', anchor='n')

        l = tk.Label(self.outvarframe, text='Log', font='Verdana 10 bold')
        l.pack(side='left', anchor='nw', padx=10)


        """       Logging for next version?

        s = 'Start Log' if self.logging == False else 'Stop Log'
        self.log_sb = ttk.Button(self.outvarframe, width=12, text='Start Log', command=lambda: self.toggle_logging())
        self.log_sb.pack(side='right', anchor='ne', padx=5)"""

        clearbtn = ttk.Button(self.outvarframe, text='Clear', width=12, command=lambda: self.delete_outtxt())
        clearbtn.pack(side='right', anchor='ne', padx=5)


        s = 'View String' if self.raw_out == True else 'View Raw'
        self.rawbtn = ttk.Button(self.outvarframe, text=s, width=12, command=lambda: self.toggle_output_view())
        self.rawbtn.pack(side='right', anchor='ne', padx=5)

        s = 'Enable Log' if self.out_disabled == True else 'Disable Log'
        self.outdbtn = ttk.Button(self.outvarframe, text=s, width=12, command=lambda: self.toggle_output())
        self.outdbtn.pack(side='right', anchor='ne', padx=5)

        savelogbtn = ttk.Button(self.outvarframe, text='Save Log', width=12, command=lambda: self.save_as(log=True))
        savelogbtn.pack(side='right', anchor='ne', padx=5)

        outframe = tk.Frame(tab)

        outframe.pack(side='top', expand=1, fill='both', anchor='nw')

        outtb = tk.Text(outframe, background="#ffffff", state='disabled', height=5, width=20, wrap=tk.NONE)
        self.vscroll = tk.Scrollbar(outframe, orient=tk.VERTICAL, command=outtb.yview)
        self.hscroll = tk.Scrollbar(outframe, orient=tk.HORIZONTAL, command=outtb.xview)
        outtb['yscroll'] = self.vscroll.set
        outtb['xscroll'] = self.hscroll.set
        self.vscroll.pack(side="right", fill="y")
        self.hscroll.pack(side="bottom", fill="x")
        # outtb.bind("<ButtonPress-1>", self.scroll_start)
        # outtb.bind("<B1-Motion>", self.scroll_move)
        outtb.pack(fill='both',expand=1, anchor='nw', side='top')
        self.last_update['outtextbox'] = outtb


    def delete_outtxt(self):
        outbox = self.last_update['outtextbox']
        outbox.config(state='normal')
        outbox.delete("1.0", tk.END)
        outbox.config(state='disabled')


# dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
#self.delay_tuners = {k:float(v.get()) for k,v in self.delay_tuners.items()}
    def tune_var(self, event=None):
        time.sleep(0.02)
        dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
        print("tune var! dt: ", dt)
        self.q1.put({'delay vars': dt})

    def track_change_to_text(event):
        text.tag_add("here", "1.0", "1.4")
        text.tag_config("here", background="black", foreground="green")


    def new_file(self, name=None, source=None, text=None):
        # very likely don't need this
        # try:
        #     tkvars = {
        #     'aivar': self.aivar.get()}
        #                 # 'sdvar': self.sdvar.get()} #, 'navar': self.navar.get()
        #     self.note.forget(self.note.select())
        # except:
        #     tkvars = None

        tab = tk.Frame(self.note)
        self.last_update = {'text': text, 'name': name, 'source': source, 'tab': tab}

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

            self.new_file(text=lastsess['text'], source=lastsess['source'], name=lastsess['name'])
            return

        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes = ftypes)
        #path = filedialog.askdirectory()
        fl = dlg.show()

        if fl != '':
            docname = fl.split("/")[-1].split(".")[0]
            self.new_file(name=docname, source=fl, text=readFile(fl))


    # deprecated until improved
    # def toggle_logging(self):
    #     if self.logging == False:
    #         self.log_sb.config(text='Stop Log')
    #         self.logging = True
    #         actlist = self.get_vjoy_actlist()
    #         self.logger = tools.Action_Logger(self, LOGPATH, type=self.log_type, vja=actlist)
    #     else:
    #         self.log_sb.config(text='Start Log')
    #         self.logging = False
    #         try:
    #             self.logger.close_log()
    #         except TypeError as e:
    #             print(e)


    def toggle_controller(self):
        if self.joy_is_on == True:
            self.hks_on = False
            self.initButton.config(state='disabled')
            self.joy_is_on = False
            s = "On"
            info = {'playing': False, 'vjoy on': False}
            self.q1.put(info)
            self.q4.put(info)
        elif self.joy_is_on == False:
            # print("vjoy on")
            self.initButton.config(state='normal')
            info = {'playing': False, 'vjoy on': True, 'joy': self.port, 'settings': self.settings, 'actcfg': self.act_cfg, 'facing': self.dir}
            s = "Off"
            self.q1.put(info)
            self.q4.put(info)
            self.joy_is_on = True
        else:
            messagebox.showerror(title='Error', message='An error occurred when changing the state of your virtual controller.')
            return

        self.vj_sb.config(text="Turn VJoy {}".format(s))


    def toggle_xaxis(self):
        if self.dir == self.default_dir:
            dir = 'L' if self.default_dir == 'R' else 'R'
            self.xa_sb.config(text="Unflip X Axis")
        else:
            dir = 'R' if self.default_dir == 'R' else 'L'
            self.xa_sb.config(text="Flip X Axis")
        self.dir = dir
        info = {'facing': dir}
        self.q1.put(info)
        self.q4.put(info)


    def toggle_hotkeys(self):
        if self.hotkeys_enabled == True:
            self.hotkeys_enabled = False
            self.hk_sb.config(text='Enable HKs')
        else:
            self.hotkeys_enabled = True
            self.hk_sb.config(text='Disable HKs')

        info = {'hks enabled': self.hotkeys_enabled}
        self.q1.put(info)
        self.q4.put(info)

    # for user to configure joystick
    def toggle_output_view(self):
        if self.raw_out == True:
            self.raw_out = False
            self.rawbtn.config(text='View Raw')
        else:
            self.raw_out = True
            self.rawbtn.config(text='View String')

        info = {'raw output': self.raw_out}
        self.q1.put(info)
        self.q4.put(info)

    # toggles ability to see output actions from PJoy & VJoy
    def toggle_output(self):
        if self.out_disabled == True:
            self.out_disabled = False
            self.outdbtn.config(text="Disable Out")
        else:
            self.out_disabled = True
            self.outdbtn.config(text="Enable Log")

    # plays notation script on repeat (separated by start delay) until stopped (pause command)
    def play(self):
        intb = self.last_update['intextbox']

        self.initButton.config(text = "Pause", command=lambda: self.pause())

        lasttxt = intb.get("1.0", "end").splitlines()[0]

        if self.playing == False:
            self.playing = True

            res = self.refresh()
            if res == False:
                self.initButton.config(text = "Play", command=lambda: self.play())
                return

            # split by space
            moveslist = lasttxt.split(" ")
            actlist = []

            leftbracketpassed = False
            rightbracketpassed = False


            for i in moveslist:
                # pre configs: predelays

                for ind, _d in enumerate(list(self.delay_tuners)):
                    #print"ind: {}; _d: {}".format(ind, _d))
                    if i == _d:
                        actlist.append((_d, ["delay({})".format(self.delay_tuners[_d].get())]))


                for k,v in self.act_cfg.items():
                    if i == '[': leftbracketpassed = True
                    if '[' in list(i) and leftbracketpassed == False:
                        i = "".join(list(i)[1:])
                        #print"i when leftbracketpassed: ", i)
                        leftbracketpassed = True

                    if i == ']': rightbracketpassed = True
                    if ']' in list(i) and rightbracketpassed == False:
                        i = "".join(list(i)[0:-2])
                        #print"i when rightbracketpassed: ", i)
                        rightbracketpassed = True

                    if v["String"] != None and v["Notation"] == i and leftbracketpassed == True and rightbracketpassed == False:
                        actlist.append((self.act_cfg[k]["Notation"], self.act_cfg[k]["String"]))

                    if rightbracketpassed == True:
                        break

            dt = {k:float(v.get()) for k,v in self.delay_tuners.items()}
            # print("DT: ", dt)

            info = {'playing': True, 'settings': self.settings, 'actlist': actlist,'actcfg': self.act_cfg, 'facing': self.dir, 'delay vars': dt, 'hks enabled': self.hotkeys_enabled}
            # print("preplay INFO: ", info)
            # print("PLAYING: ", actlist)
            if len(actlist) == 0:
                self.pause()
                self.q3.put({'error': 'No actions were found in your Notation Script.'})
                return

            self.highlight_script()

            self.q1.put(info)


    # deprecated along with logging , this func gets a concatenated list of all notations' strings without playing script
    def get_vjoy_actlist(self):
        intb = self.last_update['intextbox']

        lasttxt = intb.get("1.0", "end").splitlines()[0]

        _ = self.refresh()

        # split by space
        moveslist = lasttxt.split(" ")
        actlist = []

        leftbracketpassed = False
        rightbracketpassed = False


        for i in moveslist:
            # pre configs: predelays

            for ind, _d in enumerate(list(self.delay_tuners)):
                #print"ind: {}; _d: {}".format(ind, _d))
                if i == _d:
                    actlist.append("delay({})".format(self.delay_tuners[_d].get()))


            for k,v in self.act_cfg.items():
                if i == '[': leftbracketpassed = True
                if '[' in list(i) and leftbracketpassed == False:
                    i = "".join(list(i)[1:])
                    #print"i when leftbracketpassed: ", i)
                    leftbracketpassed = True

                if i == ']': rightbracketpassed = True
                if ']' in list(i) and rightbracketpassed == False:
                    i = "".join(list(i)[0:-2])
                    #print"i when rightbracketpassed: ", i)
                    rightbracketpassed = True


                if v["String"] != None and v["Notation"] == i and leftbracketpassed == True and rightbracketpassed == False:
                    newaction = []
                    action = self.act_cfg[k]["String"]
                    for a in action:
                        added = False
                        for dt in list(self.delay_tuners):
                            if dt in a:
                                n = self.delay_tuners[dt].get()
                                a = 'delay({})'.format(n)
                                newaction.append(a)
                                added = True
                                break
                        if added == False:
                            newaction.append(a)

                    actlist.append(newaction)

                if rightbracketpassed == True:
                    break

            if rightbracketpassed == True:
                break

        newactlist = []
        for act in actlist:
            if isinstance(act, list):
                for i in act:
                    newactlist.append(i)
            else:
                newactlist.append(act)

        print("vjoy's actlist for logging: ", newactlist)
        return newactlist


    def view_reference(self):
        dicts = {'Settings': self.settings, 'Actions': self.act_cfg}
        ref = tools.PopupDoc(self, dicts)

    def view_device_report(self):
        with open(HID_REPORT, "r") as hidr:
            self.hid_report = str(hidr.read())
            hidr.close()

        info = {'hid report': self.hid_report, 'vj report': self.vj_report, 'pj report': self.pj_report}

        report = tools.DeviceReport(self, info)

    # next version
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


    def pause(self):
        if self.playing == True:
            self.initButton.config(text='Play', command=lambda: self.play())

            box = self.last_update["intextbox"]
            tag_name = "color-green"

            #print("testing pause script")
            self.playing = False

            info = {'playing': False}

            self.q1.put(info)
            self.q4.put(info)

            box.tag_delete(tag_name)

    def save_as(self, log=False):
        #print"save test")
        if not log:
            tb = self.last_update['intextbox']
            name = self.last_update["name"]
        else:
            tb = self.last_update['outtextbox']
            name = "log-{}".format(str(datetime.today().strftime('%Y-%m-%d')))


        txt = tb.get("1.0", tk.END).splitlines()
        txt = "\n".join(txt)
        #print"split line text: ", txt)
        #src = self.frames[tab][-1]

        # check if there is source for the text box, if yes, write to source else pull up Save As window
        ftypes = [('Text files', '*.txt'), ('All files', '*')]

        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=ftypes, title=name)

        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        try:
            with open(f, "w") as file:
                file.write(txt)
                file.close()
        except FileNotFoundError as e:
            print("save as file not found: ", e)
        except Exception as e:
            self.q3.put({'error': "There was an error while saving your file in the path '{}'.".format(f)})



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
    tb = root.last_update['intextbox']
    txt = tb.get("1.0", tk.END).splitlines()
    txt = "\n".join(txt)
    name = root.last_update["name"]
    src = root.last_update['source']
    dts = {k:float(v.get()) for k,v in root.delay_tuners.items()}
    d = {'text': txt, 'source': src, 'name': name, 'delay_vars': dts}
    with open(DATAPATH + "\\" + "lastsession.txt", "w") as f:
        f.write(str(d))
        f.close()
    quit()


if __name__ == '__main__':
    freeze_support()
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    q4 = Queue()

    root = App(q1, q2, q3, q4)
    root.protocol("WM_DELETE_WINDOW", save_session)
    # setup parallel processes
    args = (q1, q2, q3, int(root.port), root.vjoy_type)
    # setup_inputter(args)

    inp = _input.Inputter(args=args)
    inp.daemon = True
    inp.start()


    args = (q1, q2, q3, q4, root.port, root.pjoy_type, HID_REPORT)
    out = _output.Outputter(args=args)
    out.daemon = True
    out.start()

    root.mainloop()
