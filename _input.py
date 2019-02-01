import multiprocessing
from hook import kb
import time
import vjoy
import sys

class Inputter(multiprocessing.Process):
    """
    virtual xbox controller api
    """

    def __init__(self, args=None):
        super().__init__(target=self.vjoy_process)
        # queue for getting info from 1st process

        self.ui_vj, self.vj_ui, self.me_opp, self.opp_me, self.joy_n, self.is_opponent = args
        # is_opponent can be True or False, this is the vjoy for the user's opponent character


        self.running = True
        self.playing = False
        self.vjoy_on = False
        self.hks_enabled = False
        self.rest = True
        self.raw_out = False
        self.listener = None
        self.pressed = []
        self.all_playing = False
        # ignore action interval (set to False at end of loops)
        # self.iai = False
        #holds all hotkeys
        self.hotkeys = []
        # self.hk_names = []
        #holds all action strings
        self.strings = []
        # variable for making sure client process has been informed
        self.client_informed = False
        # self.start_delay_t = None
        self.joy = vjoy.VXBOX_Device(self.joy_n)

        vjr =   """
                Virtual XBOX 360 Joystick: {}
                Virtual Bus Driver Exists: {}
                """.format(self.joy, self.joy.isVBusExists())

        self.vj_ui.put({'vjoy report': vjr})

    def check_for_vbus(self):
        if self.joy.isVBusExists() == False:
            self.vj_ui.put({'vbusnotexist': False})
        else:
            return

    def processIncoming(self):
        # unpack data from queue

        # may need to find a more robust way of doing this. Test for speed
        #begin = time.time()
        while self.ui_vj.qsize():
            try:
                info = self.ui_vj.get(0)
                if info is not None:
                    try:
                        newcontact = info['new contact']
                        vjslen = len(list(self.me_opp)) + 1
                        self.me_opp[vjslen] = newcontact
                    except KeyError:
                        pass
                    try:
                        newmailman = info['new mailman']
                        vjslen = len(list(self.opp_me)) + 1
                        self.opp_me[vjslen] = newmailman
                    except KeyError:
                        pass
                    try:
                        self.actlist = info['actlist']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD FUCKING ERROR 80")
                        self.vj_ui.put({'error': e})
                    try:
                        self.raw_out = info['raw output']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD FUCKING ERROR 87")
                        self.vj_ui.put({'error': e})
                    try:
                        self.act_cfg = info['actcfg']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD FUCKING ERROR 94")
                        self.vj_ui.put({'error': e})

                    try:
                        playing = info['playing']
                        both = info['both']
                        if playing != self.playing:
                            self.rep = 0
                            self.all_playing = both
                        self.playing = playing
                        self.playing_once = info['once']
                        print("ONCE? ", info['once'])

                        self.refresh(playing=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD FUCKING ERROR 119")
                        self.vj_ui.put({'error': e})
                    try:
                        n = int(info['joy'])
                        self.refresh(joy=True, joy_n=n)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 127")
                        self.vj_ui.put({'error': e})
                    try:
                        self.settings = info['settings']
                        self.refresh(settings=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 136")
                        self.vj_ui.put({'error': e})
                    try:
                        self.custom_delays = info['delay vars']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 146")
                        self.vj_ui.put({'error': e})
                    try:
                        self.vjoy_on = info['vjoy on']
                        self.refresh(vjoy_on=True)
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 155")
                        self.vj_ui.put({'error': e})
                    try:
                        self.facing = info['facing']
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 162")
                        self.vj_ui.put({'error': e})
                    try:
                        _ = info['refresh']
                        self.refresh()
                    except KeyError as e:
                        pass
                    except Exception as e:
                        print("SOME WEIRD ERROR 170")
                        self.vj_ui.put({'error', e})
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
                        self.vj_ui.put({'error': e})
                    try:
                        if info['quit']:
                            sys.exit()
                    except KeyError as e:
                        pass
            except Exception as e:
                pass

    # mainly for resetting hotkeys
    def refresh(self, vjoy_on=False, settings=False, playing=False, once=False, actlist=None):
        if vjoy_on:
            if self.vjoy_on:
                # notifies client if vbus needs to be installed
                self.check_for_vbus()
                # turn on controller
                if not self.joy.is_on:
                    self.joy.TurnOn()
            else:
                self.joy.TurnOff()
                if self.listener != None:
                    self.listener.stop()
                    del self.listener
                    self.listener = None
                self.strings = []

        elif playing:
            if self.playing:
                print("REFRESH PLAYING")
                self.rest = False
                self.strings = self.actlist
            else:
                print("HUH")
                self.rest = True
                self.strings = []
            self.client_informed = True


        elif settings:
            if not self.is_opponent:
                self.defaultdir = self.settings['default direction']
            else:
                self.defaultdir = 'R' if self.settings['default direction'] == 'L' else 'L'

    def update_queue(self, info):
        if self.running == False:
            sys.exit()
        # place info on client process' queue
        self.vj_ui.put(info)

    def vjoy_process(self):
        """This loop runs while client process is alive."""

        while self.running:
            if self.playing:
                info = {'start over': True, 'action': '{}: ['.format(self.rep), 'joy': 'vjoy'}
                self.update_queue(info)
                for iter, string in enumerate(self.strings):
                    self.parse_action(string, ind=iter)
                info = {'start over': False, 'action': ']\n', 'joy': 'vjoy'}
                self.update_queue(info)
                if self.playing_once:
                    self.playing = False
                    self.playing_once = False
                    self.all_playing = False
                    self.vj_ui.put({'playing': False})
                self.rep += 1
            # check for msg from client every 0.2 seconds
            else:
                self.processIncoming()


    def parse_action(self, string, ind=0, protocol=False): #, hk=False

        if (self.facing == 'R' and self.defaultdir == 'L') or (self.facing == 'L' and self.defaultdir == 'R'):
            flipx = True
        else:
            flipx = False
        # only execute action if the hks are on (they are on whenever controller is on)
        if self.vjoy_on == True:
            # if hk == False:
                #((notation, string))
            try:
                if not protocol:
                    iterstring = string[1]
                    notation = string[0]
                else:
                    iterstring = string
                    notation = 'None'
            except TypeError as e:
                try:
                    iterstring = eval(string[1])
                except Exception as e:
                    self.vj_ui.put({'error': e})
                    return
            try:
                for iter, a in enumerate(iterstring):
                    # print("a: ", a)
                    if self.raw_out:
                        if a in ['la_r', 'la_dr', 'la_d', 'la_dl', 'la_l', 'la_ul', 'la_u', 'la_ur', 'la_n']:
                            axis = 'la'
                            value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                            self.vj_ui.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy', 'rep': iter})

                        elif a in ['ra_r', 'ra_dr', 'ra_d', 'ra_dl', 'ra_l', 'ra_ul', 'ra_u', 'ra_ur', 'ra_n']:
                            axis = 'ra'
                            value = (self.settings['analog configs'][a]['x fix'], self.settings['analog configs'][a]['y fix'])
                            self.vj_ui.put({'raw': "[event: {}, value: {}]\n".format(axis, value), 'joy': 'vjoy', 'rep': iter})

                        elif a in ['a_d','b_d','x_d','y_d','rt_d','lt_d','rb_d','lb_d',
                                    'dpu_d','dpr_d','dpd_d','dpl_d','start_d','back_d',
                                    'a_u','b_u','x_u','y_u','rt_u','lt_u','rb_u','lb_u',
                                    'dpu_u','dpr_u','dpd_u','dpl_u','start_u','back_u']:
                            for btn, down_up_pair in self.settings['button configs']['xbox'].items():
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
                                self.vj_ui.put({'raw': "[event: {}, value: {}]\n".format(button, value), 'joy': 'vjoy', 'rep': iter})

                            except Exception as e:
                                self.vj_ui.put({'error': "an error ({}) occurred while converting string item ({}) to its raw form.".format(e, a)})


                    if ind > 0:
                        info = {'start over': False, 'action': ',', 'type': 0, 'time': 0, 'joy': 'vjoy', 'user input': (notation, string)}
                        self.update_queue(info)

                    combine = False
                    string2 = False

                    self.processIncoming()

                    if a in list(self.settings["analog configs"]):
                        cfg = self.settings["analog configs"][a]

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
                        self.parse_action(s) #, hk=hk
                        string2 = True

                    else:
                        cfg = None

                    if self.rest == False and combine == False and string2 == False:
                        print("exec: ", str(a))
                        ts = getattr(self.joy, str(a))(cfg, flipx=flipx)
                        print("ts: ", ts)

                    elif self.rest == False and combine == True:
                        ts = self.joy.combine(bin)


                    if list(a)[-1] == 'u' or a in ['la_n', 'ra_n']:
                        type = 0
                    else:
                        type = 1

                    if a == 'delay':
                        if cfg >= 0.005:
                            a = 'delay({})'.format(cfg)

                    flips = {'la_r': 'la_l', 'la_dr': 'la_dl', 'la_ur': 'la_ul', 'la_l': 'la_r', 'la_dl': 'la_dr', 'la_ul': 'la_ur',
                            'ra_r': 'ra_l', 'ra_dr': 'ra_dl', 'ra_ur': 'ra_ul', 'ra_l': 'ra_r', 'ra_dl': 'ra_dr', 'ra_ul': 'ra_ur',
                            'dpl_u': 'dpr_u', 'dpl_d': 'dpr_d', 'dpr_u': 'dpl_u', 'dpr_d': 'dpl_d'}

                    if a in list(flips) and flipx == True:
                        a = flips[a]

                    info = {'start over': False, 'action': "'{}'".format(a), 'type': type, 'time': 0.1, 'joy': 'vjoy'}

                    if not self.raw_out:
                        self.update_queue(info)



            except Exception as e:
                self.vj_ui.put({'error': e})
                    #pass
