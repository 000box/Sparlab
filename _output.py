from hook.xinput import *
from multiprocessing import Process
import time
from hook import kb
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

        self.pj_ui, self.ui_pj, self.joy_type, hid_out_fullpath = args
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
        except Exception as e:
            print("HID Error: ", e)
            self.pj_ui.put({'warning': 'HID information was not able to be sent to your Device Report.'})


    def xbox_test(self, fromq=False):
        self.joys = XInputJoystick.enumerate_devices()

        if not self.joys:
            self.pj_ui.put({'warning': 'No xbox device was found. Change your pjoy type in settings'})
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
        while self.ui_pj.qsize():
            try:
                info = self.ui_pj.get(0)
                if info is not None:

                    try:
                        self.actcfg = info['actcfg']

                    except Exception as e:
                        pass


                    # try:
                    #     hks_on = info['hks enabled']
                    #     if hks_on and self.joy_type == 'keyboard' and self.listener != None:
                    #         print("79")
                    #         self.last_joy_type = 'keyboard'
                    #         self.joy_type = 'None'
                    #         self.listener.stop()
                    #         del self.listener
                    #         self.listener = None
                    #         self.none_process()
                    #     elif not hks_on and self.joy_type == 'None' and self.last_joy_type == 'keyboard' and self.listener == None:
                    #         print("85")
                    #         self.joy_type = 'keyboard'
                    #         time.sleep(0.5)
                    #         self.kb_process()
                    # except KeyError as e:
                    #     pass
                    # except Exception as e:
                    #     print("HKS ENABLED OUT ERROR: ", e)
                    #     self.pj_ui.put({'error': e})
                    try:
                        self.raw_out = info['raw output']
                    except KeyError as e:
                        pass

                    try:
                        if init == True:
                            self.settings = info['settings']
                            self.button_vals = self.settings["button configs"]
                            self.analog_vals = self.settings['analog configs']
                            self.as_cfg = self.button_vals['arcade stick']
                            self.kb_cfg = self.button_vals['keyboard']
                            self.dv_digits = self.settings['delay variable # of decimals']
                            # print("self.as_cfg = ", self.as_cfg)
                            self.joy_type = self.settings['physical joy type']
                        else:
                            settings = info['settings']
                            if settings != self.settings:
                                self.settings = settings
                                joy_type = self.settings['physical joy type']
                                btn_vals = self.settings["button configs"]
                                analog_vals = self.settings['analog configs']
                                btn_cfg = self.settings["button configs"]
                                kb_cfg = self.button_vals['keyboard']
                                as_cfg = self.button_vals['arcade stick']
                                dv_digits = self.settings['delay variable # of decimals']

                                if any([joy_type != self.joy_type, analog_vals != self.analog_vals, as_cfg != self.as_cfg, btn_vals != self.button_vals]):

                                    if self.joy_type == 'arcade stick':
                                        self.device.close()
                                    elif self.joy_type == 'keyboard':
                                        self.listener.stop()
                                        del self.listener

                                    self.button_vals = btn_vals
                                    self.analog_vals = analog_vals
                                    self.as_cfg = as_cfg
                                    self.joy_type = joy_type
                                    self.kb_cfg = kb_cfg
                                    self.dv_digits = dv_digits
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
                                        self.pj_ui.put({'error': "{} is not a valid device type. Change your pjoy type in Settings".format(self.joy_type)})
                                        self.joy_type = 'None'
                                        self.settings['physical joy type'] = self.joy_type
                                        self.none_process()

                    except KeyError as e:
                        print("keyerror: ", e)
                    except Exception as e:
                        print("SETTINGS (out): ", e)
                        self.pj_ui.put({'error': e})
                        # pass

                        #print("HKS ON (out): ", e)
                    try:
                        self.facing = info['facing']
                    except Exception as e:
                        #print("FACING: ", e)
                        pass

            except Exception as e:
                msg = "{} (out): {}".format(type(e).__name__, e.args)


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

        self.last_tmark = time.clock()
        self.pressed = []
        self.current_axis = 'la_n'
        xbhooks = self.settings["button configs"]["xbox"]
        pj_report = """
                    Physical Joystick Type: {}
                    Available Joysticks: {}
                    Hooks: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, self.joys, xbhooks, self.pjoy)
        self.pj_ui.put({'pjoy report': pj_report})

        @self.pjoy.event
        def on_button(button, pressed):
            now = time.clock()
            dontq = False
            oppo = 1 if pressed == 0 else 0
            time_bw_events = now - self.last_tmark
            #print('button', button, pressed)
            if self.raw_out == True:
                self.pj_ui.put({'raw': "[event: {}, value: {}]\n".format(button, pressed), 'joy': 'pjoy'})
                return

            act = self.button_vals['xbox'][button][::-1][pressed]

            if button not in [None, 'None']:
                if button not in self.pressed and pressed == 1:

                    if len(self.pressed) == 0:
                        startover = True
                        time_bw_events = 0
                        self.pressed = []
                        self.pressed.append(button)
                        action = "]\n['{}'".format(act)
                    elif time_bw_events > 0:
                        startover = False
                        if time_bw_events >= 0.005:
                            action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)
                        else:
                            action = ",'{}'".format(act)
                        self.pressed.append(button)
                    else:
                        dontq = True
                        print("top else: self.pressed = ", self.pressed)
                else:
                    startover = False
                    if pressed == 0:
                        try:
                            self.pressed.remove(button)
                            if time_bw_events >= 0.005:
                                action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)
                            else:
                                action = ",'{}'".format(act)

                        except ValueError:
                            print("value error under except: self.pressed = ", self.pressed)
                            dontq = True
                    else:
                        print("dontq under else: self.pressed = ", self.pressed)
                        dontq = True


                if not dontq:
                    info = {'start over': startover, 'action': action, 'joy': 'pjoy', 'func': act}
                    self.pj_ui.put(info)

                    self.last_tmark = now




        @self.pjoy.event
        def on_axis(axis, value):
            now = time.clock()


            time_bw_events = now - self.last_tmark

            if self.raw_out == True:
                value = str((value[0] * 65536, value[1] * 65536))
                self.pj_ui.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'pjoy'})
                return

            if axis not in ['lt', 'rt']:
                act = self.get_stick_dir(axis, value)

                # show correct analog on UI
                try:
                    if axis == 'ra':
                        act = act.replace(act[0], "r")
                    elif axis == 'la':
                        act = act.replace(act[0], "l")
                except AttributeError:
                    # action = None
                    pass

            else:

                n = int(value)
                if n == 1:
                    act = "{}_d".format(axis)
                else:
                    act = "{}_u".format(axis)

            if act not in ['None', None]:

                dontq = False # 'dont queue info, but define it in self.lai, do this to filter out actions'
                possible_axis_presses = ['la_dr', 'la_r', 'la_d', 'la_dl', 'la_l', 'la_ul', 'la_u', 'la_ur',
                                        'ra_dr', 'ra_r', 'ra_d', 'ra_dl', 'ra_l', 'ra_ul', 'ra_u', 'ra_ur', 'rt_d', 'lt_d']
                possible_neutrals = ['la_n','ra_n','rt_u','lt_u']

                if act in possible_neutrals:
                    # only count neutral when RESETTING to neutral position (cv must have smaller eucl dist. to hv than lv has to cv)
                    pressed = 0
                    startover = False
                    if act == self.current_axis or time_bw_events < 0.01:
                        dontq = True
                    else:
                        for a in possible_axis_presses:
                            if a in self.pressed:
                                self.pressed.remove(a)

                        if time_bw_events >= 0.005:
                            action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)
                        else:
                            action = ",'{}'".format(act)

                else:
                    pressed = 1
                    if act in self.pressed or time_bw_events < 0.01:
                        dontq = True
                    else:
                        for a in possible_axis_presses + possible_neutrals:
                            if a in self.pressed:
                                self.pressed.remove(a)

                    if dontq == True or time_bw_events < 0:
                        return
                    # if time_bw_events < 0:
                    #     self.last_tmark = time.time()


                    if time_bw_events > 0.2 and len(self.pressed) == 0:
                        startover = True
                        time_bw_events = 0
                        self.pressed = []
                        self.pressed.append(act)
                        action = "]\n['{}'".format(act)
                    else:
                        startover = False
                        self.pressed.append(act)
                        if time_bw_events >= 0.005:
                            action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)
                        else:
                            action = ",'{}'".format(act)

            # if time_bw_events <= 0.009:
            #     time_bw_events = 0

                if dontq:
                    return

                info = {'start over': startover, 'action': action, 'joy': 'pjoy', 'func': act}

                self.pj_ui.put(info)
                self.last_tmark = now
                self.current_axis = act


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
        x, y = (x * 65536, y * 65536)
        for k,v in self.analog_vals.items():
            if x > v['x min'] and x < v['x max'] and y > v['y min'] and y < v['y max']:
                return k


    def kb_process(self):

        def on_press(key):
            now = time.time()

            try: k = key.char # single-char keys
            except: k = key.name # other keys

            if k in list(self.button_vals['keyboard']): # keys interested
                # print("press: {}".format(k))
                # self.keys.append(k) # store it in global-like variable
                try:
                    act = self.button_vals['keyboard'][k][0]
                    value = 1
                    time_bw_events = now - self.last_tmark

                    if time_bw_events > 0.2 and len(self.pressed) == 0:
                        startover = True
                        time_bw_events = 0
                        action = "]\n['{}'".format(act)

                    else:
                        startover = False
                        action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)


                    if self.raw_out:
                        self.pj_ui.put({'raw': "[event: {}, value: {}]\n".format(k, value)})
                        return

                    if act not in self.pressed:
                        info = {'joy': 'pjoy', 'action': action, 'start over': startover, 'func': act}
                        print("put press to q3")
                        self.pj_ui.put(info)
                        self.last_tmark = now
                        self.pressed.append(act)
                except Exception as e:
                    print("error ({}) ; key ({})".format(e, k))



        def on_release(key):
            now = time.time()

            try: k = key.char # single-char keys
            except: k = key.name # other keys

            # print("k release before: ", k)

            if k in list(self.button_vals['keyboard']): # keys interested
                # self.keys.append(k) # store it in global-like variable
                # print("k release after: ", k)
                act = self.button_vals['keyboard'][k][1]
                actspress = self.button_vals['keyboard'][k][0]
                value = 0
                time_bw_events = now - self.last_tmark
                startover = False

                action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)

                if self.raw_out:
                    self.pj_ui.put({'raw': "[event: {}, value: {}]\n".format(k, value)})
                    return

                info = {'joy': 'pjoy', 'action': action, 'start over': startover, 'func': act}
                self.pj_ui.put(info)
                self.last_value = value
                self.last_tmark = now
                self.last_act = act
                try:
                    self.pressed.remove(actspress)
                except ValueError:
                    pass

        while True:
            self.processIncoming(init=True)
            try:
                _ = self.settings
                break
            except AttributeError:
                time.sleep(0.1)
                print("waiting on settings...")

        self.pressed = []
        self.last_value = 0
        self.last_tmark = time.time()
        self.last_act = None
        self.listener = kb.keyboard.Listener(on_press=on_press, on_release=on_release)

        pj_report = """
                    Physical Joystick Type: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, self.listener)

        self.pj_ui.put({'pjoy report': pj_report})

        self.listener.start() # start to listen on a separate thread


        while True:
            self.processIncoming()
            time.sleep(0.5)


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

        # default pj report, changes when variables are defined
        pj_report = """
                    Physical Joystick Type: {}
                    Hooks: {}
                    Joystick Instance: {}
                    """.format(self.joy_type, [], 'None')



        try:
            self.device = hid.HidDeviceFilter(vendor_id = vID).get_devices()[0]
            self.device.open()
        except IndexError as e:
            self.pj_ui.put({'error': 'A device with vendor id "{}" could not be found'.format(vID)})
            # print("618: ", e)
            self.joy_type = "None"
            self.settings['physical joy type'] = self.joy_type
            self.pj_ui.put({'pjoy report': pj_report})
            self.none_process()
        except Exception as e:
            print("error: ", e)
            self.pj_ui.put({'error': 'An error occurred when attempting to point to a device with vendor id "{}". This might be happening because your device is not plugged in.'.format(vID)})
            self.joy_type = "None"
            self.settings['physical joy type'] = self.joy_type
            self.pj_ui.put({'pjoy report': pj_report})
            self.none_process()

        if not self.device:
            self.pj_ui.put({'error': 'A device with vendor id "{}" could not be found'.format(vID)})
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
                self.pj_ui.put({'error': e})
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
                            self.pj_ui.put({'error': "An error occured while attempting to add an event handler for usage id {}: {},".format(uID, e)})
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
        self.pj_ui.put({'pjoy report': pj_report})

        try:
            while not kbhit() and self.device.is_plugged():
                #just keep the device opened to receive events
                self.processIncoming()
                time.sleep(0.5)
            return
        except Exception as e:
            self.pj_ui.put({'error': e})
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
            self.pj_ui.put({'raw': "[Event: {}, Value: {}]\n".format(event, value), 'joy': 'pjoy'})
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
                act = vals_[value]
            except Exception as e:
                self.pj_ui.put({'error': "No hat switch value was found for {}.".format(e)})
                return

            pressed = 1 if act != 'la_n' else 0


        else:
            try:
                act = vals_[::-1][value]
            except Exception as e:
                self.pj_ui.put({'error': "No button value was found for {}.".format(e)})
                return
            pressed = value


        # if pressed != laip or action != laia:
        if time_bw_events > 0.7 and pressed == 1:
            startover = True
            time_bw_events = 0
            action = "]\n['{}'".format(act)
        else:
            startover = False
            action = ",'delay({})','{}'".format(round(time_bw_events, self.dv_digits), act)


        info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'func': act}

        self.pj_ui.put(info)

        self.last_action_info = {'start over': startover, 'action': action, 'type': pressed, 'time': time_bw_events, 'joy': 'pjoy', 'value': value, 'tmark': now}
