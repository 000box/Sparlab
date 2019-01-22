import multiprocessing
from hook import keyboard
import time
import vjoy
import threading


class Inputter(multiprocessing.Process):
    """
    This is for inputting hotkeys and 'bot' commands to virtual xbox controller api
    """

    def __init__(self, args=None):
        super().__init__(target=self.vjoy_process)
        # queue for getting info from 1st process
        self.q1, self.q2, self.q3, self.joy_n, self.joy_type = args

        self.running = True
        self.playing = False
        self.vjoy_on = False
        self.hks_enabled = False
        self.rest = True
        self.raw_out = False
        # ignore action interval (set to False at end of loops)
        # self.iai = False
        #holds all hotkeys
        self.hotkeys = []
        self.hk_names = []
        #holds all action strings
        self.strings = []
        # variable for making sure client process has been informed
        self.client_informed = False
        # self.start_delay_t = None
        if self.joy_type == 'xbox':
            self.joy = vjoy.VXBOX_Device(self.joy_n)

            vjr =   """
                    Virtual XBOX 360 Joystick: {}
                    Virtual Bus Driver Exists: {}
                    """.format(self.joy, self.joy.isVBusExists())

        else: #just default to 'xbox' for now.
            # self.q2.put({'error': "{} cannot be used as a virtual controller.\nIn your appdata's settings.txt file, change your joy type to 'xbox'\n and restart the app.".format(self.joy_type)})
            # return
            self.joy = vjoy.VXBOX_Device(self.joy_n)

            vjr =   """
                    Virtual XBOX 360 Joystick: {}
                    Virtual Bus Driver Exists: {}
                    """.format(self.joy, self.joy.isVBusExists())

        self.q2.put({'vjoy report': vjr})

    def check_for_vbus(self):
        if self.joy.isVBusExists() == False:
            self.q2.put({'vbusnotexist': False})
        else:
            return

    def processIncoming(self):
        # unpack data from queue

        # may need to find a more robust way of doing this. Test for speed
        #begin = time.time()
        while self.q1.qsize():
            try:
                info = self.q1.get(0)
                if info is not None:
                    # True or False
                    try:
                        self.actlist = info['actlist']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                    try:
                        self.raw_out = info['raw output']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                    try:
                        self.act_cfg = info['actcfg']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("ACTCFG EXCEPTION: ", e)
                    try:
                        self.hks_enabled = info['hks enabled']
                        self.refresh()
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("HKS ENABLED: ", e)
                        self.q3.put({'error': e})
                    try:
                        self.playing = info['playing']
                        self.refresh(playing=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("PLAYING EXCEPTION: ", e)
                    try:
                        n = int(info['joy'])
                        self.refresh(joy=True, joy_n=n)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("JOY EXCEPTION: ", e)
                    try:
                        self.settings = info['settings']
                        self.refresh(settings=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("SETTINGS (IN) exception: ", e)
                    try:
                        self.custom_delays = info['delay vars']
                        # print("SELF.CUSTOM_DELAYS = ", self.custom_delays)
                        # self.refresh(delays=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("CUSTOM DELAYS EXCEPTION: ", e)
                    try:
                        self.vjoy_on = info['vjoy on']
                        self.refresh(vjoy_on=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("VJOY EXCEPTION: ", e)
                    try:
                        self.facing = info['facing']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("FACING EXCEPTION: ", e)
                    try:
                        _ = info['refresh']
                        self.refresh()
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("REFRESH EXCEPTION: ", e)
                        self.q3.put({'error', e})
                    try:
                        if info['vjoy on'] == True:
                            self.vjoy_on = True
                            self.refresh(vjoy_on=True)
                        else:
                            self.vjoy_on = False
                            self.refresh(vjoy_on=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        self.q3.put({'error': e})
                        print("VJOY ON EXCEPTION: ", e)


            except Exception as e:
                print("PI ERROR: ", e)
                self.q3.put({'error': e})
                # msg = "{}: {}".format(type(e).__name__, e.args)


    # mainly for resetting hotkeys
    def refresh(self, vjoy_on=False, hks_enabled=False, settings=False, playing=False, joy=False, joy_n=0, actlist=None):

        # if delays:
        #     # self.fps = int(self.custom_delays['fps'])
        #     # print("sElF.fPs = ", self.fps)
        #     try:
        #         self.act_int_t = float(self.custom_delays['Fixed Delay'])
        #         self.start_delay_t = float(self.custom_delays['Start Delay'])
        #     except Exception as e:
        #         print("REFRESH DELAYS ERROR: ", e)

        if vjoy_on:
            if self.vjoy_on:

                # notifies client if vbus needs to be installed
                self.check_for_vbus()
                # turn on controller
                if not self.joy.is_on:
                    self.joy.TurnOn()
            else:
                self.joy.TurnOff()
                # unbind hotkeys (if any exist)
                for k in self.hotkeys:
                    try:
                        keyboard.remove_hotkey(k)
                    except:
                        pass
                # empty containers
                self.strings = []
                self.hotkeys = []
                self.hk_names = []

        elif joy:
            if joy_n != self.joy_n:
                del self.joy
                self.joy = vjoy.VXBOX_Device(joy_n)


        elif playing:
            if self.playing == True:
                self.rest = False
                self.strings = self.actlist
            else:
                self.rest = True
                self.strings = []
            self.client_informed = True


        elif settings:
            self.fps = int(self.settings['fps'])
            self.defaultdir = self.settings['default direction']
            self.joy_type = self.settings['virtual joy type']

        # only perform this operation if vjoy is on and hotkeys are enabled
        if self.vjoy_on == True and self.hks_enabled == True:
            if len(self.hotkeys) > 0:
                for k in self.hotkeys:
                    try:
                        keyboard.remove_hotkey(k)
                    except:
                        pass
            # empty containers
            self.strings = []
            self.hotkeys = []
            self.hk_names = []
            # unbind hotkeys if any exist, bc we are rebinding all of them.
            for k,v in self.act_cfg.items():

                hk = v['Hotkey']

                try:
                    string = eval(v['String'])
                except:
                    string = v['String']
                notation = v['Notation']

                if hk not in ["None", "'None'"] and string not in ["None", "'None'"] and hk != None and string != None:
                    try:
                        key = keyboard.add_hotkey(str(hk), self.perform_hk, args=(notation,string))
                        print("appending {} to list".format(hk))
                        self.hk_names.append(hk)
                        self.hotkeys.append(key)
                    except Exception as e:
                        print(e)

            v = self.settings['play hotkey']
            key = keyboard.add_hotkey(str(v), self.toggle_play)
            self.hk_names.append('play hotkey')
            self.hotkeys.append(key)

            v = self.settings['flip x axis hotkey']
            key = keyboard.add_hotkey(str(v), self.switch_sides)
            self.hk_names.append('flip x axis hotkey')
            self.hotkeys.append(key)




    def update_queue(self, info):
        if self.running == False:
            quit()

        # place info on client process' queue
        self.q2.put(info)
        self.q3.put(info)

    def vjoy_process(self):
        """This loop runs while client process is alive."""

        while self.running:
            if self.playing == True:
                # self.start_delay()
                info = {'start over': True, 'action': '[', 'joy': 'vjoy'}
                self.update_queue(info)
                for iter, string in enumerate(self.strings):
                    self.parse_action(string, ind=iter)
                # self.iai = False
                info = {'start over': False, 'action': ']\n', 'joy': 'vjoy'}
                self.update_queue(info)
            # check for msg from client every 0.2 seconds
            if self.playing == False:
                time.sleep(0.1)
                self.processIncoming()


    def perform_hk(self, notation, string):
        if self.hks_enabled == True:
            info = {'start over': True, 'action': '[', 'joy': 'vjoy'}
            self.update_queue(info)
            # give main process time to pause the sequence
            if self.playing == True:
                time.sleep(0.3)
            self.parse_action(string, hk=True)

    def parse_action(self, string, ind=0, hk=False):

        if (self.facing == 'R' and self.defaultdir == 'L') or (self.facing == 'L' and self.defaultdir == 'R'):
            flipx = True
        else:
            flipx = False
        # only execute action if the hks are on (they are on whenever controller is on)
        if self.vjoy_on == True:
            if hk == False:
                #((notation, string))
                try:
                    iterstring = string[1]
                    notation = string[0]
                except TypeError as e:
                    try:
                        iterstring = eval(string[1])
                    except Exception as e:
                        self.q3.put({'error': e})
                        return
                try:
                    for iter, a in enumerate(iterstring):
                        print("a: ", a)
                        if self.raw_out:
                            if a in ['la_r', 'la_dr', 'la_d', 'la_dl', 'la_l', 'la_ul', 'la_u', 'la_ur', 'la_n']:
                                axis = 'la'
                                value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                                self.q3.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy'})
                                continue
                            elif a in ['ra_r', 'ra_dr', 'ra_d', 'ra_dl', 'ra_l', 'ra_ul', 'ra_u', 'ra_ur', 'ra_n']:
                                axis = 'ra'
                                value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                                self.q3.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy'})
                                continue
                            elif a in ['a_d','b_d','x_d','y_d','rt_d','lt_d','rb_d','lb_d',
                                        'dpu_d','dpr_d','dpd_d','dpl_d','start_d','back_d',
                                        'a_u','b_u','x_u','y_u','rt_u','lt_u','rb_u','lb_u',
                                        'dpu_u','dpr_u','dpd_u','dpl_u','start_u','back_u']:

                                for btn, down_up_pair in self.settings['analog configs']['xbox'].items():
                                    d, u = down_up_pair
                                    if d == a:
                                        value = 1
                                        button = btn
                                        break
                                    elif u == a:
                                        value = 0
                                        button = btn
                                        break

                                try:
                                    self.q3.put({'raw': "[event: {}, value: {}]\n".format(button, value), 'joy': 'vjoy'})
                                    continue
                                except Exception as e:
                                    self.q3.put({'error': "an error ({}) occurred while converting string item ({}) to its raw form.".format(e, a)})
                                    continue

                        if ind > 0:
                            info = {'start over': False, 'action': ',', 'type': 0, 'time': 0, 'joy': 'vjoy', 'user input': (notation, string)}
                            self.update_queue(info)

                        combine = False
                        string2 = False

                        self.processIncoming()

                        if a in list(self.custom_delays):
                            f = self.custom_delays[iterstring]
                            print("self.custom_delays[iterstring]: ", f)
                            t = float(f)
                            ts = self.joy.delay_for(t)
                            a = 'delay({})'.format(t)
                            info = {'startover': False, 'action': a, 'type': 0, 'time': t, 'joy': 'vjoy'}
                            self.update_queue(info)
                            return

                        elif a in list(self.settings["analog configs"]):
                            cfg = self.settings["analog configs"][a]
                        elif a == 'j_f':
                            cfg = self.fps
                        elif 'delay' in a:
                            a, t = a.split("(")
                            cfg = "".join(list(t)[0:-1])
                            if cfg in list(self.custom_delays):
                                cfg = self.custom_delays[cfg]
                            else:
                                cfg = float(cfg)

                        elif 'combine' in a:
                            a, cfg = a.split("(")
                            cfg = "".join(list(cfg)[0:-1])
                            acts = cfg.split(",")
                            bin = []
                            for i in acts:
                                i = i.replace(" ", "")
                                c = (i, flipx)
                                bin.append(c)
                            combine = True
                        elif 'string' in a:
                            a, cfg = a.split("(")
                            act = "".join(list(cfg)[0:-1])
                            s = (self.act_cfg[act]["Notation"], self.act_cfg[act]["String"])
                            self.parse_action(s, hk=hk)
                            string2 = True

                        else:
                            cfg = None

                        if self.rest == False and combine == False and string2 == False:
                            print("exec: ", str(a))
                            ts = getattr(self.joy, str(a))(cfg, flipx=flipx)
                            print("ts: ", ts)

                        elif self.rest == False and combine == True:
                            ts = self.joy.combine(bin)

                        else:
                            print('Action {} (string: {}) did not get filtered. Rest = {}, combine = {}, string2 = {}'.format(a, string, self.rest, combine, string2))


                        if list(a)[-1] == 'u' or a in ['la_n', 'ra_n']:
                            type = 0
                        else:
                            type = 1

                        if a in ['delay', 'j_f']:
                            if a == 'j_f':
                                cfg = cfg / 1000

                            if cfg >= 0.005:
                                a = 'delay({})'.format(cfg)

                        flips = {'la_r': 'la_l', 'la_dr': 'la_dl', 'la_ur': 'la_ul', 'la_l': 'la_r', 'la_dl': 'la_dr', 'la_ul': 'la_ur',
                                'ra_r': 'ra_l', 'ra_dr': 'ra_dl', 'ra_ur': 'ra_ul', 'ra_l': 'ra_r', 'ra_dl': 'ra_dr', 'ra_ul': 'ra_ur',
                                'dpl_u': 'dpr_u', 'dpl_d': 'dpr_d', 'dpr_u': 'dpl_u', 'dpr_d': 'dpl_d'}

                        if a in list(flips) and flipx == True:
                            a = flips[a]
                        # time_bw_events = ts - self.last_update
                        info = {'start over': False, 'action': "'{}'".format(a), 'type': type, 'time': 0.1, 'joy': 'vjoy'}
                        self.update_queue(info)
                        # self.last_update = ts
                    # if a == 'i_a_i':
                    #     self.iai = True
                except Exception as e:
                    self.q3.put({'error': e})
                    #pass
            else:
                iterstring = string
                notation = 'None'
                for k,v in self.act_cfg.items():
                    if v['String'] == string:
                        notation = v['Notation']
                        break

                for iter, a in enumerate(iterstring):

                    if self.raw_out:
                        if a in ['la_r', 'la_dr', 'la_d', 'la_dl', 'la_l', 'la_ul', 'la_u', 'la_ur', 'la_n']:
                            axis = 'la'
                            value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                            self.q3.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy'})
                            continue
                        elif a in ['ra_r', 'ra_dr', 'ra_d', 'ra_dl', 'ra_l', 'ra_ul', 'ra_u', 'ra_ur', 'ra_n']:
                            axis = 'ra'
                            value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                            self.q3.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy'})
                            continue
                        elif a in ['a_d','b_d','x_d','y_d','rt_d','lt_d','rb_d','lb_d',
                                    'dpu_d','dpr_d','dpd_d','dpl_d','start_d','back_d',
                                    'a_u','b_u','x_u','y_u','rt_u','lt_u','rb_u','lb_u',
                                    'dpu_u','dpr_u','dpd_u','dpl_u','start_u','back_u']:

                            for btn, down_up_pair in self.settings['analog configs']['xbox'].items():
                                d, u = down_up_pair
                                if d == a:
                                    value = 1
                                    button = btn
                                    break
                                elif u == a:
                                    value = 0
                                    button = btn
                                    break

                            try:
                                self.q3.put({'raw': "[event: {}, value: {}]\n".format(button, value), 'joy': 'vjoy'})
                                continue
                            except Exception as e:
                                self.q3.put({'error': "an error ({}) occurred while converting string item ({}) to its raw form.".format(e, a)})
                                continue

                    if iter > 0:
                        info = {'start over': False, 'action': ',', 'type': 0, 'time': 0, 'joy': 'vjoy', 'user input': (notation, string)}
                        self.update_queue(info)

                    combine = False
                    string2 = False

                    if a in list(self.settings["analog configs"]):
                        cfg = self.settings["analog configs"][a]

                    elif a == 'j_f':
                        cfg = self.fps
                    elif 'delay' in a:
                        a, t = a.split("(")
                        cfg = "".join(list(t)[0:-1])
                        cfg = float(cfg)


                    # deprecated till future version
                    # elif 'combine' in a:
                    #     a, cfg = a.split("(")
                    #     cfg = "".join(list(cfg)[0:-1])
                    #     acts = cfg.split(",")
                    #     bin = []
                    #     for i in acts:
                    #         i = i.replace(" ", "")
                    #         c = (i, flipx)
                    #         bin.append(c)
                    #     combine = True
                    # elif 'string' in a:
                    #     a, cfg = a.split("(")
                    #     act = "".join(list(cfg)[0:-1])
                    #     s = (self.act_cfg[act]["Notation"], self.act_cfg[act]["String"])
                    #     self.parse_action(s, hk=hk)
                    #     string2 = True

                    else:
                        cfg = None
                    # execute the action
                    # if combine == False and string2 == False:
                        # timestamp
                    ts = getattr(self.joy, str(a))(cfg, flipx=flipx)
                    # elif combine == True:
                    #     # timestamp
                    #     ts = self.joy.combine(bin)

                    # inform main process
                    if list(a)[-1] == 'u' or a in ['la_n','neutral','ra_n']:
                        type = 0
                    else:
                        type = 1

                    if a in ['delay', 'j_f']:
                        if a == 'j_f':
                            cfg = cfg / 1000

                        if cfg >= 0.005:
                            a = 'delay({})'.format(cfg)
                    # elif a == 'combine':

                    flips = {'la_r': 'la_l', 'la_dr': 'la_dl', 'la_ur': 'la_ul', 'la_l': 'la_r', 'la_dl': 'la_dr', 'la_ul': 'la_ur',
                            'ra_r': 'ra_l', 'ra_dr': 'ra_dl', 'ra_ur': 'ra_ul', 'ra_l': 'ra_r', 'ra_dl': 'ra_dr', 'ra_ul': 'ra_ur',
                            'dpl_u': 'dpr_u', 'dpl_d': 'dpr_d', 'dpr_u': 'dpl_u', 'dpr_d': 'dpl_d'}

                    if a in list(flips) and flipx == True:
                        a = flips[a]

                    a = "'{}'".format(a)
                    info = {'start over': False, 'action': a, 'joy': 'vjoy'}
                    self.update_queue(info)
                    # self.last_update = ts
                info = {'start over': False, 'action': ']\n', 'joy': 'vjoy', 'user input': (notation, string)}
                self.update_queue(info)

                # deprecated
                # if a == 'i_a_i':
                #     self.iai = True

    # deprecated
    # def start_delay(self):
    #     # inform client process that action is starting from beginning
    #     # 'start over' will start next line in out feed.
    #     begin = time.time()
    #     end = begin
    #
    #     info = {'start over': True, 'action': '[', 'type': 0, 'time': 0, 'joy': 'vjoy'}
    #     self.update_queue(info)
    #
    #     self.processIncoming()
    #
    #     t = float(self.start_delay_t)
    #
    #     i = 0
    #     while (end - begin) <= t:
    #         if i % 1000 == 0:
    #             self.processIncoming()
    #             if not self.playing:
    #                 break
    #
    #         time.sleep(0.001)
    #         end = time.time()
    #
    #     print("START DELAY = {}; st took: {} sec".format(self.start_delay_t, str(end - begin)))


    def toggle_play(self):
        if self.hks_enabled == True:
            if self.playing == True and self.client_informed == True:
                self.client_informed = False
                self.joy.neutral('bla')
                self.rest = True
                info = {'playing': False}
                self.update_queue(info)

            elif self.playing == False and self.client_informed == True:
                self.client_informed = False
                self.rest = False
                self.joy.neutral('bla')
                #print"toggle_play: self.playing = true")
                info = {'playing': True}
                self.update_queue(info)

    def switch_sides(self):
        #Left/right
        if self.hks_enabled == True:
            if self.facing == 'R':
                self.facing = 'L'
            else:
                self.facing = 'R'

            info = {'facing': self.facing}
            self.update_queue(info)
