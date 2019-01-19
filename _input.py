import multiprocessing
from hook import keyboard
import time
import vjoy
import logging

logging.basicConfig(level=logging.INFO)


class Inputter(multiprocessing.Process):
    """
    This is for inputting hotkeys and 'bot' commands to virtual xbox controller api
    """

    def __init__(self, args=None):
        super().__init__(target=self.key_listener)
        # queue for getting info from 1st process
        self.q1, self.q2, self.q3, self.joy_n, self.joy_type = args

        self.running = True
        self.playing = False
        self.vjoy_on = False
        self.hks_enabled = False
        self.rest = True
        # ignore action interval (set to False at end of loops)
        self.iai = False
        #holds all hotkeys
        self.hotkeys = []
        self.hk_names = []
        #holds all action strings
        self.strings = []
        self.pending = []
        # variable for making sure client process has been informed
        self.client_informed = False

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
                        self.act_cfg = info['actcfg']
                    except KeyError as e:
                        pass
                        #print(e)
                    try:
                        self.hks_enabled = info['hks enabled']
                        self.refresh()
                    except KeyError as e:
                        pass

                    try:
                        self.playing = info['playing']

                        if self.playing == True:
                            #logging.info('self.playing = True')
                            self.rest = False
                            #print"self.playing = True")
                            #if self.strings == []:
                            self.strings = info['actlist']
                        else:
                            #logging.info('self.playing = False')
                            self.rest = True
                            #print"self.playing = False")
                            self.strings = []

                        self.client_informed = True
                        self.pending = []

                    except KeyError as e:
                        pass
                        #print("PLAYING EXCEPTION: ", e)

                    try:
                        n = int(info['joy'])
                        #print("joy number: ", n)
                        if n != self.joy_n:
                            self.joy = vjoy.VXBOX_Device(n)

                    except KeyError as e:
                        pass

                    try:
                        self.settings = info['settings']
                        self.fps = int(self.settings['fps'])
                        self.defaultdir = self.settings['default direction']
                        self.joy_type = self.settings['virtual joy type']
                        self.act_int_t = float(self.settings['Fixed Delay'])
                        self.start_delay_t = float(self.settings['Start Delay'])
                    except KeyError as e:
                        #print("SETTINGS: ", e)
                        pass
                    try:
                        self.custom_delays = info['delay vars']
                        #print"new custom delays: ", self.custom_delays)
                        self.fps = int(self.custom_delays['fps'])
                        self.act_int_t = float(self.custom_delays['Fixed Delay'])
                        self.start_delay_t = float(self.custom_delays['Start Delay'])
                        # print("action interval: {}; custom delays: {}".format(self.act_int_t, self.custom_delays))
                    except KeyError as e:
                        #print("custom delay error: ", e)
                        pass

                    try:
                        self.vjoy_on = info['vjoy on']
                        self.refresh()
                    except KeyError as e:
                        pass
                        # print("vjoy on: ", e)
                    try:
                        self.facing = info['facing']
                    except KeyError as e:
                        #print("FACING: ", e)
                        pass
                    try:
                        _ = info['refresh']
                        self.refresh()
                    except:
                        pass

                    try:
                        if info['vjoy on'] == True:
                            # print("turn vjoy ON")
                            # throw error if bus driver doesn't exist
                            self.check_for_vbus()
                            # turn on controller
                            self.joy.TurnOn()
                            self.vjoy_on = True
                        else:
                            # print("turn vjoy OFF")
                            #print"hks off")
                            # turn off controller
                            self.joy.TurnOff()
                            self.vjoy_on = False
                            # unbind hotkeys
                            for k in self.hotkeys:
                                try:
                                    keyboard.remove_hotkey(k)
                                except:
                                    pass
                            # empty containers
                            self.strings = []
                            self.hotkeys = []
                            self.hk_names = []

                    except KeyError as e:
                        msg = "{} (out): {}".format(type(e).__name__, e.args)
                        # print("HKS (In): ", msg)



            except Exception as e:
                msg = "{}: {}".format(type(e).__name__, e.args)
                # print("Inp Process Inc: ", msg)

        # end = time.time()
        # print("P2 Process Incoming speed: ", end - begin)

    def endApplication(self):
        self.running = False

    # mainly for resetting hotkeys
    def refresh(self):
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

    def key_listener(self):
        """This loop runs while client process is alive."""

        while self.running:
            if self.playing == True:
                self.start_delay()

                for iter, string in enumerate(self.strings):
                    self.parse_action(string, ind=iter)
                    try:
                        last_update = time.time()
                        ts = self.joy.action_interval(self.act_int_t, ignore=self.iai)
                        time_bw_events = round(ts - last_update, 3)
                        if time_bw_events >= 0.001:
                            info = {'start over': False, 'action': 'delay({})'.format(time_bw_events), 'type': 0, 'time': 0, 'joy': 'vjoy'}
                            self.update_queue(info)

                    except Exception as e:
                        logging.warning('Fixed Delay Error')
                        # print("ACTION INTERVAL ERROR: ", e)
                        #pass

            self.iai = False

            # check for msg from client every 0.2 seconds
            if self.playing == False:
                time.sleep(0.1)
                self.processIncoming()



    def perform_hk(self, notation, string):
        if self.hks_enabled == True:
            info = {'start over': True, 'action': 'delay(0.0)', 'type': 0, 'time': 0, 'joy': 'vjoy', 'user input': (notation, string)}
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
                except Exception as e:
                    logging.warning('Iterstring needs to be evaluated')
                    iterstring = eval(string[1])

                try:

                    for iter, a in enumerate(iterstring):

                        # print("A: ", a)
                        combine = False
                        string2 = False
                        # print("a: ", a)
                        # begin = time.time()
                        self.processIncoming()
                        # tot = time.time() - begin
                        # print("processincomingtime: ", tot)
                        # print("(AUTO) a: {}".format(a))
                        if a in list(self.custom_delays):
                            f = self.custom_delays[iterstring]
                            # print("self.custom_delays[iterstring]: ", f)
                            t = float(f)
                            # print("iterstring: {}, t: {}".format(iterstring, t))
                            #print"f = {}; delay for: {}".format(f,t))
                            #logging.info('delaying for {} s; a = {}, string: {}'.format(t, a, string))
                            ts = self.joy.delay_for(t)

                            # time_bw_events = ts - self.last_update
                            a = 'delay({})'.format(t)
                            info = {'startover': False, 'action': a, 'type': type, 'time': t, 'joy': 'vjoy'}
                            self.update_queue(info)
                            # self.last_update = ts
                            return

                        elif a in list(self.settings["analog configs"]):
                            # print("{} settings: {}".format(a, self.settings[a]))
                            #logging.info('This is an analog action ({})'.format(a))
                            cfg = self.settings["analog configs"][a]
                        elif a == 'j_f':
                            #logging.info('This is a j_f')
                            cfg = self.fps
                            # print("fps: ", cfg)
                        elif 'delay' in a:
                            #logging.info('This is a delay')
                            a, t = a.split("(")

                            cfg = "".join(list(t)[0:-1])
                            if cfg in list(self.custom_delays):
                                cfg = self.custom_delays[cfg]
                            else:
                                cfg = float(cfg)

                        elif 'combine' in a:
                            #logging.info('This is a combine')
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
                            #logging.info('This is a string')
                            a, cfg = a.split("(")
                            act = "".join(list(cfg)[0:-1])
                            s = (self.act_cfg[act]["Notation"], self.act_cfg[act]["String"])
                            self.parse_action(s, hk=hk)
                            string2 = True

                        else:
                            #logging.info('This is a button')
                            cfg = None

                        if self.rest == False and combine == False and string2 == False:
                            #logging.info('Sending to joystick: a={}, cfg={}, flipx={}'.format(a, cfg, flipx))
                            ts = getattr(self.joy, str(a))(cfg, flipx=flipx)

                        elif self.rest == False and combine == True:
                            #logging.info('Combining {}'.format(bin))
                            ts = self.joy.combine(bin)

                        else:
                            logging.info('Action {} (string: {}) did not get filtered. Rest = {}, combine = {}, string2 = {}'.format(a, string, self.rest, combine, string2))


                        if list(a)[-1] == 'u' or a == 'la_n':
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
                        info = {'start over': False, 'action': a, 'type': type, 'time': 0.1, 'joy': 'vjoy'}
                        self.update_queue(info)
                        # self.last_update = ts



                    if a == 'i_a_i':
                        self.iai = True
                except Exception as e:
                    logging.warning(e)
                    #pass

            else:
                logging.info('This is a hotkey action')
                # self.last_update = time.time()
                iterstring = string
                # print("(HK) iterstring: ", iterstring)
                for a in iterstring:
                    combine = False
                    string2 = False
                    # load configs from settings to pass as arg
                    # print("(HK) a: ", a)


                    if a in list(self.settings["analog configs"]):
                        # print("{} settings: {}".format(a, self.settings[a]))
                        #logging.info('This is an analog action ({})'.format(a))
                        cfg = self.settings["analog configs"][a]


                    elif a == 'j_f':
                        cfg = self.fps
                        # a = 'delay({})'.
                        # print("fps: ", cfg)
                    elif 'delay' in a:
                        a, t = a.split("(")
                        cfg = "".join(list(t)[0:-1])
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
                    # execute the action
                    if combine == False and string2 == False:
                        # timestamp
                        ts = getattr(self.joy, str(a))(cfg, flipx=flipx)
                    elif combine == True:
                        # timestamp
                        ts = self.joy.combine(bin)

                    # inform main process
                    if list(a)[-1] == 'u' or a == 'la_n':
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



                    info = {'start over': False, 'action': a, 'type': type, 'time': 0.1, 'joy': 'vjoy'}
                    self.update_queue(info)
                    # self.last_update = ts
                if a == 'i_a_i':
                    self.iai = True


    def start_delay(self):
        # inform client process that action is starting from beginning
        # 'start over' will start next line in out feed.
        info = {'start over': True, 'action': 'delay(0.0)', 'type': 0, 'time': 0, 'joy': 'vjoy'}
        self.update_queue(info)

        self.processIncoming()
        whol = int(self.start_delay_t)

        xtra = float(self.start_delay_t) - whol
        #print("whol: {}, xtra: {}".format(whol, xtra))
        #print"xtra: ", xtra)
        for i in range(whol):
            # print("processIncoming")
            self.processIncoming()
            if self.playing == False:
                return
            time.sleep(0.5)

            self.processIncoming()
            if self.playing == False:
                return
            time.sleep(0.5)

        time.sleep(xtra)



    def toggle_play(self):
        # play/pause
        #logging.info('Toggle Play')
        if self.hks_enabled == True:
            if self.playing == True and self.client_informed == True:
                self.client_informed = False
                self.joy.neutral('bla')
                self.rest = True
                #print"toggle_play: self.playing = false")
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
