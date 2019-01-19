from hook.xinput import *
from multiprocessing import Process
import time
from hook import keyboard
from msvcrt import kbhit
import sys
import hook.hid as hid


class Outputter(Process):

    def __init__(self, args=None):

        self.joytype_map = {
                            'xbox': 'xbox_process',
                            'keyboard': 'kb_process',
                            'arcade stick': 'arcadestick_process',
                            'None': 'none_process'
                            }

        self.q1, self.q2, self.q3, self.q4, self.port, self.joy_type, hid_out_fullpath = args
        # queue for getting info from 1st process
        self.last_action_info = {'start over': True, 'action': 'None', 'type': 0, 'time': 0, 'joy': 'pjoy', 'value': (0, 0), 'tmark': time.clock()}
        self.raw_out = False
        with open(hid_out_fullpath, "w") as f:
            self.send_hid_report(f)
            f.close()
        if self.joy_type == 'xbox':
            self.xbox_test()

        super().__init__(target=getattr(self, self.joytype_map[self.joy_type]))


    def send_hid_report(self, outfile):
        try:
            hid.core.show_hids(output = outfile)
        except:
            pass


    def xbox_test(self, fromq=False):
        self.joys = XInputJoystick.enumerate_devices()

        if not self.joys:
            self.q3.put({'warning': 'No xbox device was found. Change your pjoy type in settings'})
            self.joy_type == 'None'
            self.settings['physical joy type'] = self.joy_type
            self.none_process()
        else:
            # physical joystick
            self.pjoy = self.joys[0]
            # print('using %d' % self.pjoy.device_number)
            battery = self.pjoy.get_battery_information()
            # virtual joystick (temp)
            # self.vjoy = self.joys[0]
            self.last_action_info = {'start over': True, 'action': 'None', 'type': 0, 'time': 0, 'joy': 'pjoy', 'value': (0, 0), 'tmark': time.clock()}


    def processIncoming(self, init=False):
        # unpack data from queue

        # may need to find a more robust way of doing this. Test for speed
        #begin = time.clock()
        while self.q4.qsize():
            try:
                info = self.q4.get(0)
                if info is not None:

                    try:
                        self.actcfg = info['actcfg']

                    except Exception as e:
                        pass

                    try:
                        self.raw_out = info['raw output']
                    except KeyError as e:
                        pass

                    try:
                        if init == True:
                            self.settings = info['settings']
                            self.b2f_map = self.settings["Button-Function Map"]
                            self.analog_vals = self.settings['analog configs']
                            self.as_cfg = self.b2f_map['arcade stick']
                            # print("self.as_cfg = ", self.as_cfg)
                            self.joy_type = self.settings['physical joy type']
                            self.na = self.settings['default neutral allowance']
                        else:
                            settings = info['settings']
                            if settings != self.settings:
                                self.settings = settings
                                joy_type = self.settings['physical joy type']
                                b2f_map = self.settings["Button-Function Map"]
                                analog_vals = self.settings['analog configs']
                                as_cfg = b2f_map['arcade stick']

                                # if any([joy_type != self.joy_type, analog_vals != self.analog_vals, as_cfg != self.as_cfg, b2f_map != self.b2f_map]):

                                if self.joy_type == 'arcade stick':
                                    self.device.close()
                                elif self.joy_type == 'keyboard':
                                    self.remove_hooks()


                                self.b2f_map = b2f_map
                                self.analog_vals = analog_vals
                                self.as_cfg = as_cfg
                                self.joy_type = joy_type

                                if self.joy_type == 'xbox':
                                    self.xbox_test()
                                    self.xbox_process()
                                elif self.joy_type == 'keyboard':
                                    # print("keyboard switch")
                                    self.kb_process()
                                elif self.joy_type == 'arcade stick':
                                    self.arcadestick_process()
                                elif self.joy_type == 'None':
                                    self.none_process()
                                else:
                                    self.q3.put({'error': "{} is not a valid device type. Change your pjoy type in Settings".format(self.joy_type)})
                                    self.joy_type = 'None'
                                    self.settings['physical joy type'] = self.joy_type
                                    self.none_process()

                    except Exception as e:
                        print("SETTINGS (out): ", e)
                        # pass

                        #print("HKS ON (out): ", e)
                    try:
                        self.facing = info['facing']
                    except Exception as e:
                        #print("FACING: ", e)
                        pass

                    # try:
                    #     self.na = info['neutral allowance']
                    # except Exception as e:
                    #     pass

            except Exception as e:
                msg = "{} (out): {}".format(type(e).__name__, e.args)


# self.b2f_map = self.cfg['button to notation map']

# 'button to notation map': {(13, 1): {'Notation': None, 'Hotkey': None, 'Function': 'a_d'},


    def none_process(self):
        while True:
            self.processIncoming()
            time.sleep(0.5)

    def xbox_process(self):
        while True:
            self.processIncoming(init=True)
            try:
                _ = self.settings
                break
            except AttributeError:
                time.sleep(0.1)
                # print("waiting on settings...")

        xbhooks = self.settings["Button-Function Map"]["xbox"]
        pj_report = """
                    Physical Joystick Type: {}
                    Available Joysticks: {}
                    Hooks: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, self.joys, xbhooks, self.pjoy)
        self.q3.put({'pjoy report': pj_report})

        @self.pjoy.event
        def on_button(button, pressed):
            now = time.clock()

            lait = self.last_action_info["time"]
            laia = self.last_action_info["action"]
            laip = self.last_action_info["type"]
            laij = self.last_action_info["joy"]
            laiso = self.last_action_info["start over"]
            laisv = self.last_action_info['value']
            laitm = self.last_action_info['tmark']

            time_bw_events = now - laitm
            #print('button', button, pressed)
            if self.raw_out == True:
                self.q3.put({'raw': "[event: {}, value: {}],".format(button, pressed)})
                return
            if pressed != laip or button != laia:
                action = self.b2f_map['xbox'][button][::-1][pressed]

                if time_bw_events > self.na and pressed == 1:
                    startover = True
                    time_bw_events = 0
                else:
                    startover = False

                info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy'}
                self.q3.put(info)

                self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': laisv, 'tmark': now}


        @self.pjoy.event
        def on_axis(axis, value):
            now = time.clock()

            lait = self.last_action_info["time"]
            laia = self.last_action_info["action"]
            laip = self.last_action_info["type"]
            laij = self.last_action_info["joy"]
            laiso = self.last_action_info["start over"]
            laisv = self.last_action_info['value']
            laitm = self.last_action_info['tmark']

            time_bw_events = now - laitm

            if self.raw_out == True:
                self.q3.put({'raw': "[event: {}, value: {}],".format(axis, value)})
                return

            if axis not in ['lt', 'rt']:
                action = self.get_stick_dir(axis, value)

                # show correct analog on UI
                try:
                    if axis == 'ra':
                        action = action.replace(action[0], "r")
                    elif axis == 'la':
                        action = action.replace(action[0], "l")
                except AttributeError:
                    # action = None
                    pass

            else:

                n = int(value)
                if n == 1:
                    action = "{}_d".format(axis)
                else:
                    action = "{}_u".format(axis)
            if action not in [None, 'None']:
                pressed = 1 # by default
                dontq = False # 'dont queue info, but define it in self.lai, do this to filter out actions'
                if action in ['la_n','ra_n','rt_u','lt_u']:
                    # only count neutral when RESETTING to neutral position (cv must have smaller eucl dist. to hv than lv has to cv)
                    pressed = 0
                    if laia == action:
                        dontq = True

                else:
                    if laia == action:
                        dontq = True


                if time_bw_events > self.na and laip == 0:
                    startover = True
                    time_bw_events = 0
                else:
                    startover = False

                # if time_bw_events <= 0.009:
                #     time_bw_events = 0

                if dontq == True:
                    self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': value, 'tmark': laitm}
                    return

                info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy'}

                self.q3.put(info)
                self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': value, 'tmark': now}


        while True:
            try:
                self.pjoy.dispatch_events()
            except RuntimeError:
                self.last_action_info = {'start over': True, 'action': 'None', 'type': 0, 'time': 0, 'joy': 'pjoy', 'value': (0, 0), 'tmark': time.clock()}
                self.kb_process()
            # self.vjoy.dispatch_events()
            self.processIncoming()

    def get_stick_dir(self, axis, value):
        x, y = value

        for k,v in self.analog_vals.items():

            if x > v['x min'] and x < v['x max'] and y > v['y min'] and y < v['y max']:
                return k







    def keyevent(self, event):
        now = event.time

        lait = self.last_action_info["time"]
        laia = self.last_action_info["action"]
        laip = self.last_action_info["type"]
        laij = self.last_action_info["joy"]
        laiso = self.last_action_info["start over"]
        laisv = self.last_action_info['value']
        laitm = self.last_action_info['tmark']

        time_bw_events = now - laitm

        type = event.event_type

        if self.raw_out == True:
            self.q3.put({'raw': "[event: {}, value: {}],".format(event, event.scan_code)})
            return

        key = self.translate_scancode(event.scan_code).lower()
        if key != None:
            try:
                action = self.b2f_map['keyboard'][key][0] if type == 'down' else self.b2f_map['keyboard'][key][1]

                if action == laia:
                    self.last_action_info = {'start over': False, 'action': laia, 'type': laisv, 'time': time_bw_events, 'joy': 'pjoy', 'value': laisv, 'tmark': laitm}
                    return

                pressed = 1 if type == 'down' else 0

                if time_bw_events > self.na and pressed == 1:
                    startover = True
                    time_bw_events = 0
                else:
                    startover = False

                info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy'}

                self.q3.put(info)
                self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': pressed, 'tmark': now}

            except Exception as e:
                pass


    def add_kb_hooks(self):
        self.handles = []

        for k,v in self.b2f_map['keyboard'].items():
            try:
                handle1 = keyboard.hook_key(k, lambda e: e.event_type == keyboard.KEY_DOWN or self.keyevent(e), suppress=False)
                self.handles.append(handle1)
                handle2 = keyboard.hook_key(k, lambda e: e.event_type == keyboard.KEY_UP or self.keyevent(e), suppress=False)
                self.handles.append(handle2)
                # hk = keyboard.add_hotkey(k, self.keydown, args=(v[0],))
            except Exception as e:
                self.q3.put({'error': e})

        kbhooks = self.settings["Button-Function Map"]["keyboard"]
        pj_report = """
                    Physical Joystick Type: {}
                    Hooks: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, kbhooks, keyboard._listener)
        self.q3.put({'pjoy report': pj_report})

    def remove_hooks(self):
        keyboard.unhook_all()


    def kb_process(self):
        while True:
            self.processIncoming(init=True)
            try:
                _ = self.settings
                break
            except AttributeError:
                time.sleep(0.1)
                # print("waiting on settings...")

        self.add_kb_hooks()

        while True:
            self.processIncoming()
            time.sleep(0.5)


    def translate_scancode(self, scancode, to_dk=True):
        dk = {
            "1":            0x02,
            "2":            0x03,
            "3":            0x04,
            "4":            0x05,
            "5":            0x06,
            "6":            0x07,
            "7":            0x08,
            "8":            0x09,
            "9":            0x0A,
            "0":            0x0B,

            "NUMPAD1":      0x4F,       "NP1":      0x4F,
            "NUMPAD2":      0x50,       "NP2":      0x50,
            "NUMPAD3":      0x51,       "NP3":      0x51,
            "NUMPAD4":      0x4B,       "NP4":      0x4B,
            "NUMPAD5":      0x4C,       "NP5":      0x4C,
            "NUMPAD6":      0x4D,       "NP6":      0x4D,
            "NUMPAD7":      0x47,       "NP7":      0x47,
            "NUMPAD8":      0x48,       "NP8":      0x48,
            "NUMPAD9":      0x49,       "NP9":      0x49,
            "NUMPAD0":      0x52,       "NP0":      0x52,
            "DIVIDE":       0xB5,       "NPDV":     0xB5,
            "MULTIPLY":     0x37,       "NPM":      0x37,
            "SUBSTRACT":    0x4A,       "NPS":      0x4A,
            "ADD":          0x4E,       "NPA":      0x4E,
            "DECIMAL":      0x53,       "NPDC":     0x53,
            "NUMPADENTER":  0x9C,       "NPE":      0x9C,

            "A":            0x1E,
            "B":            0x30,
            "C":            0x2E,
            "D":            0x20,
            "E":            0x12,
            "F":            0x21,
            "G":            0x22,
            "H":            0x23,
            "I":            0x17,
            "J":            0x24,
            "K":            0x25,
            "L":            0x26,
            "M":            0x32,
            "N":            0x31,
            "O":            0x18,
            "P":            0x19,
            "Q":            0x10,
            "R":            0x13,
            "S":            0x1F,
            "T":            0x14,
            "U":            0x16,
            "V":            0x2F,
            "W":            0x11,
            "X":            0x2D,
            "Y":            0x15,
            "Z":            0x2C,

            "F1":           0x3B,
            "F2":           0x3C,
            "F3":           0x3D,
            "F4":           0x3E,
            "F5":           0x3F,
            "F6":           0x40,
            "F7":           0x41,
            "F8":           0x42,
            "F9":           0x43,
            "F10":          0x44,
            "F11":          0x57,
            "F12":          0x58,

            "UP":           0xC8,
            "LEFT":         0xCB,
            "RIGHT":        0xCD,
            "DOWN":         0xD0,

            "ESC":          0x01,
            "SPACE":        0x39,       "SPC":      0x39,
            "RETURN":       0x1C,       "ENT":      0x1C,
            "INSERT":       0xD2,       "INS":      0xD2,
            "DELETE":       0xD3,       "DEL":      0xD3,
            "HOME":         0xC7,
            "END":          0xCF,
            "PRIOR":        0xC9,       "PGUP":     0xC9,
            "NEXT":         0xD1,       "PGDN":     0xD1,
            "BACK":         0x0E,
            "TAB":          0x0F,
            "LCONTROL":     0x1D,       "LCTRL":    0x1D,
            "RCONTROL":     0x9D,       "RCTRL":    0x9D,
            "LSHIFT":       0x2A,       "LSH":      0x2A,
            "RSHIFT":       0x36,       "RSH":      0x36,
            "LMENU":        0x38,       "LALT":     0x38,
            "RMENU":        0xB8,       "RALT":     0xB8,
            "LWIN":         0xDB,
            "RWIN":         0xDC,
            "APPS":         0xDD,
            "CAPITAL":      0x3A,       "CAPS":     0x3A,
            "NUMLOCK":      0x45,       "NUM":      0x45,
            "SCROLL":       0x46,       "SCR":      0x46,

            "MINUS":        0x0C,       "MIN":      0x0C,
            "LBRACKET":     0x1A,       "LBR":      0x1A,
            "RBRACKET":     0x1B,       "RBR":      0x1B,
            "SEMICOLON":    0x27,       "SEM":      0x27,
            "APOSTROPHE":   0x28,       "APO":      0x28,
            "GRAVE":        0x29,       "GRA":      0x29,
            "BACKSLASH":    0x2B,       "BSL":      0x2B,
            "COMMA":        0x33,       "COM":      0x33,
            "PERIOD":       0x34,       "PER":      0x34,
            "SLASH":        0x35,       "SLA":      0x35,
        }

        # virtual keys
        vk = {
            "1":            0x31,
            "2":            0x32,
            "3":            0x33,
            "4":            0x34,
            "5":            0x35,
            "6":            0x36,
            "7":            0x37,
            "8":            0x38,
            "9":            0x39,
            "0":            0x30,

            "NUMPAD1":      0x61,       "NP1":      0x61,
            "NUMPAD2":      0x62,       "NP2":      0x62,
            "NUMPAD3":      0x63,       "NP3":      0x63,
            "NUMPAD4":      0x64,       "NP4":      0x64,
            "NUMPAD5":      0x65,       "NP5":      0x65,
            "NUMPAD6":      0x66,       "NP6":      0x66,
            "NUMPAD7":      0x67,       "NP7":      0x67,
            "NUMPAD8":      0x68,       "NP8":      0x68,
            "NUMPAD9":      0x69,       "NP9":      0x69,
            "NUMPAD0":      0x60,       "NP0":      0x60,
            "DIVIDE":       0x6F,       "NPDV":     0x6F,
            "MULTIPLY":     0x6A,       "NPM":      0x6A,
            "SUBSTRACT":    0x6D,       "NPS":      0x6D,
            "ADD":          0x6B,       "NPA":      0x6B,
            "DECIMAL":      0x6E,       "NPDC":     0x6E,
            "NUMPADENTER":  0x0D,       "NPE":      0x0D,

            "A":            0x41,
            "B":            0x42,
            "C":            0x43,
            "D":            0x44,
            "E":            0x45,
            "F":            0x46,
            "G":            0x47,
            "H":            0x48,
            "I":            0x49,
            "J":            0x4A,
            "K":            0x4B,
            "L":            0x4C,
            "M":            0x4D,
            "N":            0x4E,
            "O":            0x4F,
            "P":            0x50,
            "Q":            0x51,
            "R":            0x52,
            "S":            0x53,
            "T":            0x54,
            "U":            0x55,
            "V":            0x56,
            "W":            0x57,
            "X":            0x58,
            "Y":            0x59,
            "Z":            0x5A,

            "F1":           0x70,
            "F2":           0x71,
            "F3":           0x72,
            "F4":           0x73,
            "F5":           0x74,
            "F6":           0x75,
            "F7":           0x76,
            "F8":           0x77,
            "F9":           0x78,
            "F10":          0x79,
            "F11":          0x7A,
            "F12":          0x7B,

            "UP":           0x26,
            "LEFT":         0x25,
            "RIGHT":        0x27,
            "DOWN":         0x28,

            "ESC":          0x1B,
            "SPACE":        0x20,       "SPC":      0x20,
            "RETURN":       0x0D,       "ENT":      0x0D,
            "INSERT":       0x2D,       "INS":      0x2D,
            "DELETE":       0x2E,       "DEL":      0x2E,
            "HOME":         0x24,
            "END":          0x23,
            "PRIOR":        0x21,       "PGUP":     0x21,
            "NEXT":         0x22,       "PGDN":     0x22,
            "BACK":         0x08,
            "TAB":          0x09,
            "LCONTROL":     0xA2,       "LCTRL":    0xA2,
            "RCONTROL":     0xA3,       "RCTRL":    0xA3,
            "LSHIFT":       0xA0,       "LSH":      0xA0,
            "RSHIFT":       0xA1,       "RSH":      0xA1,
            "LMENU":        0xA4,       "LALT":     0xA4,
            "RMENU":        0xA5,       "RALT":     0xA5,
            "LWIN":         0x5B,
            "RWIN":         0x5C,
            "APPS":         0x5D,
            "CAPITAL":      0x14,       "CAPS":     0x14,
            "NUMLOCK":      0x90,       "NUM":      0x90,
            "SCROLL":       0x91,       "SCR":      0x91,

            "MINUS":        0xBD,       "MIN":      0xBD,
            "LBRACKET":     0xDB,       "LBR":      0xDB,
            "RBRACKET":     0xDD,       "RBR":      0xDD,
            "SEMICOLON":    0xBA,       "SEM":      0xBA,
            "APOSTROPHE":   0xDE,       "APO":      0xDE,
            "GRAVE":        0xC0,       "GRA":      0xC0,
            "BACKSLASH":    0xDC,       "BSL":      0xDC,
            "COMMA":        0xBC,       "COM":      0xBC,
            "PERIOD":       0xBE,       "PER":      0xBE,
            "SLASH":        0xBF,       "SLA":      0xBF,
        }

        # convert numpad keys to user's intended keys
        numpad = {"NUMPAD8": 'w',
                    "NUMPAD2": 's',
                    "NUMPAD6": 'd',
                    "NUMPAD4": 'a'}

        if to_dk == True:
            for k,v in dk.items():
                if scancode == v:
                    if k in list(numpad):
                        return numpad[k]
                    return k
            return None


    def arcadestick_process(self):

        # get_hid_info()
        # print("\n\n\n")
        workers = []

        while True:
            self.processIncoming(init=True)
            try:
                infos = self.as_cfg
                break
            except AttributeError:
                time.sleep(0.1)
                # print("waiting on arcade stick cfgs...")


        # adding buttons
        for k,v in self.as_cfg['buttons']['usage ids'].items():
            info = {'page id': self.as_cfg['buttons']['page id'], 'usage id': k, 'values': v, 'type': 'button'}
            # child queue
            workers.append(info)

        # add hat switch
        info = {'page id': self.as_cfg['hat switch']['page id'], 'usage id': self.as_cfg['hat switch']['usage id'], 'values': self.as_cfg['hat switch']['values'], 'type': 'hat switch'}


        workers.append(info)

        self.last_action_info = {'start over': True, 'action': 'None', 'type': 0, 'time': 0, 'joy': 'pjoy', 'value': (0, 0), 'tmark': time.clock()}

        vID = self.as_cfg['vendor id']
        try:
            self.device = hid.HidDeviceFilter(vendor_id = vID).get_devices()[0]
            self.device.open()
        except IndexError as e:
            self.q3.put({'error': 'A device with vendor id "{}" could not be found'.format(vID)})
            # print("618: ", e)
            self.joy_type = "None"
            self.settings['physical joy type'] = self.joy_type
            self.none_process()

        if not self.device:
            self.q3.put({'error': 'A device with vendor id "{}" could not be found'.format(vID)})
            self.joy_type = "None"
            self.settings['physical joy type'] = self.joy_type
            self.none_process()

        hooks = []
        for info in workers:
            worker_added = False

            # communication b/w parent thread

            pID = info['page id']
            uID = info['usage id']
            vals = info['values']
            type = info['type']

            # play with this value (or set it if you know your device capabilities)
            # this allows to poll the telephony device for the current usage value
            input_interrupt_transfers = False
            # get all currently connected HID devices we could filter by doing
            # something like hid.HidDeviceFilter(vendor_id = 0x1234), product Id
            # filters (with masks) and other capabilities also available

            try:
                usage_hook = hid.get_full_usage_id(pID, uID)
                cont = True
            except Exception as e:
                self.q3.put({'error': e})
                # print("647: ", e)
                cont = False

            if cont == True:
                # browse input reports
                all_input_reports = self.device.find_input_reports()
                # print("ALL INPUT REPORTS: ", all_input_reports)

                for input_report in all_input_reports:
                    if usage_hook in input_report:

                        # print("\nMonitoring {0.vendor_name} {0.product_name} "\
                        #         "device.\n".format(self.device))

                        # add event handler (example of other available
                        # events: EVT_PRESSED, EVT_RELEASED, EVT_ALL, ...)

                        try:
                            self.device.add_event_handler(usage_hook, lambda event, value, v=vals, t=type: self.arcadestick_event(event, value, vals_=v, type_=t), hid.HID_EVT_CHANGED) #level usage
                            cont = True
                        except KeyError as e:
                            self.q3.put({'error': "An error occured while attempting to add an event handler for usage id {}: {},".format(uID, e)})
                            cont = False                                                                                                             #   HID_EVT_CHANGED

                        if cont == True:
                            if input_interrupt_transfers:
                                # poll the current value (GET_REPORT directive),
                                # allow handler to process result
                                input_report.get()

                            hooks.append("Usage Hook: {} --> {}; ".format(usage_hook, vals))
                            worker_added = True


        pj_report = """
                    Physical Joystick Type: {}
                    Hooks: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, hooks, str(self.device))
        self.q3.put({'pjoy report': pj_report})

        try:
            while not kbhit() and self.device.is_plugged():
                #just keep the device opened to receive events
                self.processIncoming()
                time.sleep(0.5)
            return
        except Exception as e:
            self.q3.put({'error': e})
            # print("692: ", e)

        self.device.close()


    def arcadestick_event(self, value, event, vals_=None, type_=None):
        now = time.clock()
        # self.happening += 1
        # if self.happening > 1:
        #     while self.happening > 1:
        #         nothing = None

        # print("value: {}, event: {}".format(value, event))
        if self.raw_out == True:
            self.q3.put({'raw': "[Event: {}, Value: {}],".format(event, value)})
            return

        lait = self.last_action_info["time"]
        laia = self.last_action_info["action"]
        laip = self.last_action_info["type"]
        laij = self.last_action_info["joy"]
        laiso = self.last_action_info["start over"]
        laisv = self.last_action_info['value']
        laitm = self.last_action_info['tmark']

        time_bw_events = now - laitm


        if type_ == 'hat switch':
            try:
                action = vals_[value]
            except Exception as e:
                self.q3.put({'error': "No hat switch value was found for {}.".format(e)})
                return

            pressed = 1 if action != 'la_n' else 0


        else:
            try:
                action = vals_[::-1][value]
            except Exception as e:
                self.q3.put({'error': "No button value was found for {}.".format(e)})
                return
            pressed = value


        # if pressed != laip or action != laia:
        if time_bw_events > self.na and pressed == 1:
            startover = True
            time_bw_events = 0
        else:
            startover = False


        info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy'}

        self.q3.put(info)

        self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': value, 'tmark': now}
