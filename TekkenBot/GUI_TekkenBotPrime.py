import tkinter as tk
from tkinter import ttk
from . import GUI_FrameDataOverlay as fdo
from . import GUI_TimelineOverlay as tlo
from . import GUI_Overlay as ovr
from . import GUI_CommandInputOverlay as cio
from . import GUI_MatchStatOverlay as mso
from . import GUI_DebugInfoOverlay as dio
from . import GUI_PunishCoachOverlay as pco
from . import ConfigReader
from ._FrameDataLauncher import FrameDataLauncher
from . import GUI_MasterOverlay as mast
import time
from enum import Enum
import sys
import os
from multiprocessing import Process


class GameHook(object):
    def __init__(self, master):
        self.overlay1 = None
        self.master = master
        self.color_scheme_config = ConfigReader.ConfigReader("color_scheme")
        self.changed_color_scheme("Current", False)

        self.stdout1 = sys.stdout
        self.stderr1 = sys.stderr
        self.stdout2 = sys.stdout
        self.stderr2 = sys.stderr
        self.var_print_frame_data_to_file = tk.BooleanVar(value=False)

        self.p1pos = (1950, 86)
        # self.p2pos = (1021, 200)




    def setup_textredirector(self, box):
        sys.stdout = TextRedirector(box, 'data', sys.stdout, self.write_to_overlay1, self.var_print_frame_data_to_file, "stdout1")
        sys.stderr = TextRedirector(box, 'data', sys.stderr, self.write_to_error1,self.var_print_frame_data_to_file,  "stderr1")


        # elif p == 2:
        # sys.stdout2 = TextRedirector(box, sys.stdout, self.write_to_overlay2,self.var_print_frame_data_to_file,  "stdout2")
        # sys.stderr2 = TextRedirector(box, sys.stderr, self.write_to_error2,self.var_print_frame_data_to_file,  "stderr2")
        self.launcher = FrameDataLauncher(False)
        # self.overlay1 = fdo.GUI_FrameDataOverlay(self.master, self.launcher, self.p1pos)
        # self.overlay2 = fdo.GUI_FrameDataOverlay(self.master, self.launcher, self.p2pos)
        self.mode = OverlayMode.CommandInput
        self.update_launcher()
        # self.overlay1.hide()
            # self.overlay2.hide()

    def write_to_overlay1(self, string):
        # if self.var_print_frame_data_to_file.get() and 'NOW:' in string:
        #     with open("TekkenData/frame_data_output.txt", 'a') as fa:
        #         fa.write(string +'\n')
        if self.overlay1 != None:
            self.overlay1.redirector.write(string)
        #if 'HIT' in string:
            #self.graph.redirector.write(string)
    def write_to_overlay2(self, string):
    #     # if self.var_print_frame_data_to_file.get() and 'NOW:' in string:
    #     #     with open("TekkenData/frame_data_output.txt", 'a') as fa:
    #     #         fa.write(string +'\n')
        if self.overlay2 != None:
            self.overlay2.redirector2.write(string)
        #if 'HIT' in string:
            #self.graph.redirector.write(string)

    def changed_color_scheme(self, section, do_reboot=True):
        for enum in fdo.ColorSchemeEnum:
            fdo.CurrentColorScheme.dict[enum] = self.color_scheme_config.get_property(section, enum.name, fdo.CurrentColorScheme.dict[enum])
            self.color_scheme_config.set_property("Current", enum.name, fdo.CurrentColorScheme.dict[enum])
        self.color_scheme_config.write()
        if do_reboot:
            self.reboot_overlay()

    def write_to_error1(self, string):
        self.stderr1.write(string)

    # def write_to_error2(self, string):
    #     self.stderr2.write(string)


    def stop_overlay(self):
        # for overlay in [self.overlay1, self.overlay2]:
        if self.overlay1 != None:
                overlay.toplevel.destroy()

        self.overlay1 = None
        # self.overlay2 = None

    def start_overlay(self):
        # if self.mode == OverlayMode.FrameData:
        #     self.overlay1 = fdo.GUI_FrameDataOverlay(self.master, self.launcher, self.p1pos)
        #     self.overlay1.hide()
        #     # self.overlay2 = fdo.GUI_FrameDataOverlay(self.master, self.launcher, self.p2pos)
        #     # self.overlay2.hide()
        #
        if self.mode == OverlayMode.CommandInput:
            self.overlay1 = cio.GUI_CommandInputOverlay(self.master, self.launcher, self.p1pos)
            self.overlay1.hide()
            # self.overlay2 = cio.GUI_CommandInputOverlay(self.master, self.launcher, self.p2pos)
            # self.overlay2.hide()
        # if self.mode == OverlayMode.Master:
        #     self.overlay1 = mast.GUI_Master(self.master, self.launcher, self.p1pos)
        #     self.overlay1.hide()


        # if self.mode == OverlayMode.PunishCoach:
        #     self.overlay1 = pco.GUI_PunishCoachOverlay(self, self.launcher)
        #     self.overlay1.hide()
        # if self.mode == OverlayMode.MatchupRecord:
        #     self.overlay1 = mso.GUI_MatchStatOverlay(self, self.launcher)
        #     self.overlay1.hide()
        # if self.mode == OverlayMode.DebugInfo:
        #     self.overlay1 = dio.GUI_DebugInfoOverlay(self.master, self.launcher, self.p1pos)
        #     self.overlay1.hide()
            # self.overlay2 = dio.GUI_DebugInfoOverlay(self.master, self.launcher, self.p2pos)
            # self.overlay2.hide()



    def update_launcher(self):
        # self.check_queue()
        time1 = time.time()
        successful_update = self.launcher.Update()

        if self.overlay1 != None:
            self.overlay1.update_location()
            # self.overlay2.update_location()
            if successful_update:
                self.overlay1.update_state()
                # self.overlay2.update_state()
        #self.graph.update_state()
        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)
        if self.launcher.gameState.gameReader.HasWorkingPID():
            self.master.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)
        else:
            self.master.after(1000, self.update_launcher)

    def on_closing(self):
        sys.stdout = self.stdout1
        sys.stderr = self.stderr1
        self.destroy()



class TextRedirector(object):
    def __init__(self, widget, type, stdout, callback_function, var_print_frame_data_to_file, tag="stdout"): #var_print_frame_data_to_file,
        self.widget = widget
        self.stdout = stdout
        self.tag = tag
        self.callback_function = callback_function
        self.var_print_frame_data_to_file = var_print_frame_data_to_file

    def write(self, str):

        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see('end')
        self.callback_function(str)

    def flush(self):
        pass

class OverlayMode(Enum):
    Off = 0
    FrameData = 1
    # Timeline = 2
    CommandInput = 3
    PunishCoach = 4
    MatchupRecord = 5
    DebugInfo = 6
    Master = 2

OverlayModeToDisplayName = {
    OverlayMode.Off : 'Off',
    OverlayMode.FrameData: 'Frame Data',
    OverlayMode.CommandInput: 'Command Inputs (and cancel window)',
    OverlayMode.PunishCoach: 'Punish Alarm (loud!)',
    OverlayMode.MatchupRecord: 'Matchup Stats',
    OverlayMode.DebugInfo: 'Debugging Variables',
    OverlayMode.Master: 'Master'
}

if __name__ == '__main__':
    app = GUI_TekkenBotPrime()
    #app.update_launcher()
    app.mainloop()
