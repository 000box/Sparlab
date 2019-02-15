"""
A transparent frame data display that sits on top of Tekken.exe in windowed or borderless mode.
"""


import tkinter as tk
from tkinter import ttk
import sys
from enum import Enum
from . import GUI_Overlay
from .GUI_Overlay import CurrentColorScheme, ColorSchemeEnum
import win32gui
from .MoveInfoEnums import InputDirectionCodes
from .MoveInfoEnums import InputAttackCodes
from collections import Counter

class DataColumns(Enum):
    XcommX = 0
    XidX = 1
    name = 3
    XtypeXX = 4
    XstX = 5
    bloX = 6
    hitX = 7
    XchXX = 8
    act = 9
    T = 10
    tot = 11
    rec = 12
    opp = 13
    notes = 14

    def config_name():
        return "DataColumns"

DataColumnsToMenuNames = {
    DataColumns.XcommX : 'input command',
    DataColumns.XidX : 'internal move id number',
    DataColumns.name: 'internal move name',
    DataColumns.XtypeXX: 'attack type',
    DataColumns.XstX: 'startup frames',
    DataColumns.bloX: 'frame advantage on block',
    DataColumns.hitX: 'frame advantage on hit',
    DataColumns.XchXX: 'frame advantage on counter hit',
    DataColumns.act: 'active frame connected on / total active frames',
    DataColumns.T: 'how well move tracks during startup',
    DataColumns.tot: 'total number of frames in move',
    DataColumns.rec: 'frames before attacker can act',
    DataColumns.opp: 'frames before defender can act',
    DataColumns.notes: 'additional move properties',
}

class TextRedirector(object):
    def __init__(self, widget, type, stdout, style, fa_p1_var, fa_p2_var):
        self.stdout = stdout
        self.widget = widget
        self.type = type
        self.fa_p1_var = fa_p1_var
        self.fa_p2_var = fa_p2_var
        self.style = style
        if type == 'data':
            self.widget.tag_config("p1", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p1_text])
            self.widget.tag_config("p2", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p2_text])
        self.columns_to_print = [True] * len(DataColumns)

        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])

    def set_columns_to_print(self, booleans_for_columns):
        self.columns_to_print = booleans_for_columns
        self.populate_column_names(booleans_for_columns)

    def populate_column_names(self, booleans_for_columns):
        column_names = ""
        for i, enum in enumerate(DataColumns):
            col_name = enum.name.replace('X', '')
            col_len = len(col_name)
            global col_max_length
            col_max_length = 8
            if booleans_for_columns[i]:

                if col_len < col_max_length:
                    if col_len % 2 == 0:
                        needed_spaces = col_max_length - col_len
                        col_name = (" " * int(needed_spaces / 2)) + col_name + (" " * int(needed_spaces / 2))
                    else:
                        needed_spaces = col_max_length - col_len
                        col_name = (" " * int(needed_spaces / 2)) + col_name + (" " * int(needed_spaces / 2 + 1))


                col_name = '|' + col_name

                column_names += col_name
        self.set_first_column(column_names)

    def set_first_column(self, first_column_string):
        if self.type == 'data':
            self.widget.configure(state="normal")
            self.widget.delete("1.0", "2.0")
            self.widget.insert("1.0", first_column_string + '\n')
            self.widget.configure(state="disabled")


    def write(self, output_str):
        #self.stdout.write(output_str)
        if self.type == 'input':
            return

        lines = int(self.widget.index('end-1c').split('.')[0])
        max_lines = 5
        if lines > max_lines:
            r = lines - max_lines
            for _ in range(r):
                self.widget.configure(state="normal")
                self.widget.delete('2.0', '3.0')
                self.widget.configure(state="disabled")

        if 'NOW:' in output_str:

            data = output_str.split('NOW:')[0]
            fa = output_str.split('NOW:')[1][:3]

            if '?' not in fa:
                if int(fa) <= -14:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_very_punishible])
                elif int(fa) <= -10:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_punishible])
                elif int(fa) <= -5:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_safe_minus])
                elif int(fa) < 0:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])
                else:
                    self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_plus])

            text_tag = None
            if "p1:" in output_str:
                self.fa_p1_var.set(fa)
                data = data.replace('p1:', '')
                text_tag = 'p1'
            else:
                self.fa_p2_var.set(fa)
                data = data.replace('p2:', '')
                text_tag = 'p2'

            if '|' in output_str and self.type == 'data':
                out = ""
                for i, col in enumerate(data.split('|')):
                    if self.columns_to_print[i]:
                        col_value = col.replace(' ', '')
                        col_value_len = len(col_value)

                        if col_value_len < col_max_length:
                            if col_value_len % 2 == 0:
                                needed_spaces = col_max_length - col_value_len
                                col_value = (" " * int(needed_spaces / 2)) + col_value + (" " * int(needed_spaces / 2))
                            else:
                                needed_spaces = col_max_length - col_value_len
                                col_value = (" " * int(needed_spaces / 2 + 1)) + col_value + (" " * int(needed_spaces / 2))

                        out += '|' + col_value

                print("\n" + data)


                out += "\n"
                self.widget.configure(state="normal")
                self.widget.insert("end", out, text_tag)
                self.widget.configure(state="disabled")
                self.widget.see('0.0')
                self.widget.yview('moveto', '.02')


# class GUI_CommandInputOverlay(GUI_Overlay.Overlay):
#
#     symbol_map = {

        #InputDirectionCodes.u: '⇑',
        #InputDirectionCodes.uf: '⇗',
        #InputDirectionCodes.f: '⇒',
        #InputDirectionCodes.df: '⇘',
        #InputDirectionCodes.d: '⇓',
        #InputDirectionCodes.db: '⇙',
        #InputDirectionCodes.b: '⇐',
        #InputDirectionCodes.ub: '⇖',
        #InputDirectionCodes.N: '★',

        # InputDirectionCodes.u : '↑',
        # InputDirectionCodes.uf: '↗',
        # InputDirectionCodes.f: '→',
        # InputDirectionCodes.df: '↘',
        # InputDirectionCodes.d: '↓',
        # InputDirectionCodes.db: '↙',
        # InputDirectionCodes.b: '←',
        # InputDirectionCodes.ub: '↖',
        # InputDirectionCodes.N: '★',
        # InputDirectionCodes.NULL: '!'
#
#     }
#
#
#     def __init__(self, master, launcher, pos):
#         GUI_Overlay.Overlay.__init__(self, master, pos, "Tekken Bot: Command Input Overlay")
#         self.launcher = launcher
#
#         self.canvas = tk.Canvas(self, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')
#         self.canvas.pack()
#
#         self.length = 60
#         self.step = self.w/self.length
#         for i in range(self.length):
#             self.canvas.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
#             self.canvas.create_line(i * self.step, 0, i * self.step, self.h, fill="red")
#
#
#         self.redirector1 = TextRedirector(self.canvas, self.h)\
#
#         self.stored_inputs1 = []
#         self.stored_cancels1 = []
#
#
#     def update_state(self):
#         GUI_Overlay.Overlay.update_state(self)
#         if self.launcher.gameState.stateLog[-1].is_player_player_one:
#             input = self.launcher.gameState.stateLog[-1].bot.GetInputState()
#             cancelable = self.launcher.gameState.stateLog[-1].bot.is_cancelable
#             bufferable = self.launcher.gameState.stateLog[-1].bot.is_bufferable
#             parry1 = self.launcher.gameState.stateLog[-1].bot.is_parry_1
#             parry2 = self.launcher.gameState.stateLog[-1].bot.is_parry_2
#         else:
#             input = self.launcher.gameState.stateLog[-1].opp.GetInputState()
#             cancelable = self.launcher.gameState.stateLog[-1].opp.is_cancelable
#             bufferable = self.launcher.gameState.stateLog[-1].opp.is_bufferable
#             parry1 = self.launcher.gameState.stateLog[-1].opp.is_parry_1
#             parry2 = self.launcher.gameState.stateLog[-1].opp.is_parry_2
#         frame_count = self.launcher.gameState.stateLog[-1].frame_count
#         #print(input)
#         self.update_input(input, self.color_from_cancel_booleans(cancelable, bufferable, parry1, parry2))
#
#     def color_from_cancel_booleans(self, cancelable, bufferable, parry1, parry2):
#         if parry1:
#             fill_color = 'orange'
#         elif parry2:
#             fill_color = 'yellow'
#         elif bufferable:
#             fill_color = 'MediumOrchid1'
#         elif cancelable:
#             fill_color = 'SteelBlue1'
#         else:
#             fill_color = 'firebrick1'
#         return fill_color
#
#     def update_input1(self, input, cancel_color):
#         input_tag = "inputs"
#         self.stored_inputs1.append(input)
#         self.stored_cancels1.append(cancel_color)
#         if len(self.stored_inputs1) >= self.length:
#             self.stored_inputs1 = self.stored_inputs1[-self.length:]
#             self.stored_cancels1 = self.stored_cancels[-self.length:]
#             if input != self.stored_inputs1[-2]:
#                 self.canvas1.delete(input_tag)
#
#                 #print(self.stored_inputs)
#                 for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs1):
#                     self.canvas1.create_text(i * self.step + (self.step / 2), 30, text=GUI_CommandInputOverlay.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
#                     self.canvas1.create_text(i * self.step + (self.step / 2), 55, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)
#                     x0 = i * self.step + 4
#                     x1 = x0 + self.step - 8
#                     self.canvas1.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels1[i], tag=input_tag)
#
#     def update_input2(self, input, cancel_color):
#         input_tag = "inputs"
#         self.stored_inputs2.append(input)
#         self.stored_cancels2.append(cancel_color)
#         if len(self.stored_inputs2) >= self.length:
#             self.stored_inputs2 = self.stored_inputs2[-self.length:]
#             self.stored_cancels2 = self.stored_cancels2[-self.length:]
#             if input != self.stored_inputs2[-2]:
#                 self.canvas2.delete(input_tag)
#
#                 #print(self.stored_inputs)
#                 for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs1):
#                     self.canvas2.create_text(i * self.step + (self.step / 2), 30, text=GUI_CommandInputOverlay.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
#                     self.canvas2.create_text(i * self.step + (self.step / 2), 55, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)
#                     x0 = i * self.step + 4
#                     x1 = x0 + self.step - 8
#                     self.canvas.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels2[i], tag=input_tag)

class GUI_Master(GUI_Overlay.Overlay):



    symbol_map = {
                    InputDirectionCodes.u : '↑',
                    InputDirectionCodes.uf: '↗',
                    InputDirectionCodes.f: '→',
                    InputDirectionCodes.df: '↘',
                    InputDirectionCodes.d: '↓',
                    InputDirectionCodes.db: '↙',
                    InputDirectionCodes.b: '←',
                    InputDirectionCodes.ub: '↖',
                    InputDirectionCodes.N: '★',
                    InputDirectionCodes.NULL: '!'

                }

    def __init__(self, master, launcher, pos):

        GUI_Overlay.Overlay.__init__(self, master, pos, "Tekken Bot: Master Overlay")

        self.show_live_framedata = self.tekken_config.get_property(GUI_Overlay.DisplaySettings.config_name(), GUI_Overlay.DisplaySettings.tiny_live_frame_data_numbers.name, True)

        #self.launcher = FrameDataLauncher(self.enable_nerd_data)
        self.launcher = launcher


        self.s = ttk.Style()
        self.s.theme_use('alt')
        # self.s.configure('.', background=self.background_color)
        # self.s.configure('.', foreground=CurrentColorScheme.dict[ColorSchemeEnum.advantage_text])
        #
        #
        # self.s.configure('TFrame', background=self.tranparency_color)
        self.fa_p1_var, fa_p1_label = self.create_frame_advantage_label()
        self.fa_p2_var, fa_p2_label = self.create_frame_advantage_label()


        if self.show_live_framedata:
            self.l_live_recovery = self.create_live_recovery(fa_p1_label)
            self.r_live_recovery = self.create_live_recovery(fa_p2_label)


        self.text = tk.Text(self, width=10, height=10)
        self.text.pack(side='top', fill='both', expand=1)
        self.text.configure(background=self.background_color)
        self.text.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        #
        self.stdout = sys.stdout
        self.redirector = TextRedirector(self.text, 'data', self.stdout, self.s, self.fa_p1_var, self.fa_p2_var)

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        # self.text.insert("1.0", "{:^5}|{:^8}|{:^9}|{:^7}|{:^5}|{:^5}|{:^8}|{:^5}|{:^5}|{:^7}|{:^5}|{}\n".format(" input ", "type", "startup", "block", "hit", "CH", "active", "track", "tot", "rec", "stun", "notes"))
        self.redirector.populate_column_names(self.get_data_columns())


        self.text.configure(state="disabled")


        self.canvas1 = tk.Canvas(self, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')
        self.canvas1.pack(side='bottom', expand=1, fill='both')
        self.redirector1 = TextRedirector(self.canvas1, 'input', self.stdout, self.s, self.fa_p1_var, self.fa_p2_var)

        self.length = 60
        self.step = self.w/self.length
        for i in range(self.length):
            self.canvas1.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
            self.canvas1.create_line(i * self.step, 0, i * self.step, self.h, fill="red")


        self.stored_inputs1 = []
        self.stored_cancels1 = []

        self.canvas2 = tk.Canvas(self, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')
        self.canvas2.pack(side='bottom', expand=1, fill='both')
        self.redirector2 = TextRedirector(self.canvas2, 'input', self.stdout, self.s, self.fa_p1_var, self.fa_p2_var)
        # self.redirector.set_columns_to_print(self.get_data_columns())

        for i in range(self.length):
            self.canvas2.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
            self.canvas2.create_line(i * self.step, 0, i * self.step, self.h, fill="red")


        self.stored_inputs2 = []
        self.stored_cancels2 = []

        self.set_columns_to_print(self.get_data_columns())


    def get_tekken_window(self):
        def callback(hwnd, extra):
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y


    def get_data_columns(self):
        booleans_for_columns = []
        for enum in DataColumns:
            bool = self.tekken_config.get_property(DataColumns.config_name(), enum.name, True)
            booleans_for_columns.append(bool)
        return booleans_for_columns


    def create_live_recovery(self, parent):
        live_recovery_var = tk.StringVar()
        live_recovery_var.set('??')
        live_recovery_label = tk.Label(parent, textvariable=live_recovery_var, font=("Segoe UI", 12), width=5, anchor='c')

        #live_recovery_label.grid(row=0, column=col, sticky =S+W)
        live_recovery_label.pack(side='left')

        return live_recovery_var

    def create_frame_advantage_label(self):
        frame_advantage_var = tk.StringVar()
        frame_advantage_var.set('?')
        frame_advantage_label = tk.Label(self, textvariable=frame_advantage_var, font=("Consolas", 44), width=4, anchor='c',
                                        borderwidth=1, relief='ridge')
        frame_advantage_label.pack(side='left', anchor='nw')
        return frame_advantage_var, frame_advantage_label

    def create_attack_type_label(self, col):
        attack_type_var = tk.StringVar()
        attack_type_var.set('?')
        attack_type_label = tk.Label(self, textvariable=attack_type_var, font=("Verdana", 12), width=10, anchor='c',
                                    borderwidth=4, relief='ridge')
        attack_type_label.grid(row=1, column=col)
        return attack_type_var

    def create_textbox(self, col):
        textbox = Text(self, font=("Consolas", 11), wrap=NONE, highlightthickness=0, pady=0, relief='flat')
        textbox.grid(row=0, column=col, rowspan=2, sticky=N + S + W + E)
        textbox.configure(background=self.background_color)
        textbox.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        return textbox


    def set_columns_to_print(self, columns_to_print):
        self.redirector1.set_columns_to_print(columns_to_print)
        self.redirector2.set_columns_to_print(columns_to_print)

    def update_column_to_print(self, enum, value):
        self.tekken_config.set_property(DataColumns.config_name(), enum.name, value)
        self.write_config_file()

    def update_state(self):
        GUI_Overlay.Overlay.update_state(self)

        if self.show_live_framedata:
            if len(self.launcher.gameState.stateLog) > 1:
                l_recovery = str(self.launcher.gameState.GetOppFramesTillNextMove() - self.launcher.gameState.GetBotFramesTillNextMove())
                r_recovery = str(self.launcher.gameState.GetBotFramesTillNextMove() - self.launcher.gameState.GetOppFramesTillNextMove())
                if not '-' in l_recovery:
                    l_recovery = '+' + l_recovery

                if not '-' in r_recovery:
                    r_recovery = '+' + r_recovery
                self.l_live_recovery.set(l_recovery)
                self.r_live_recovery.set(r_recovery)


        if self.launcher.gameState.stateLog[-1].is_player_player_one:
            input = self.launcher.gameState.stateLog[-1].bot.GetInputState()
            cancelable = self.launcher.gameState.stateLog[-1].bot.is_cancelable
            bufferable = self.launcher.gameState.stateLog[-1].bot.is_bufferable
            parry1 = self.launcher.gameState.stateLog[-1].bot.is_parry_1
            parry2 = self.launcher.gameState.stateLog[-1].bot.is_parry_2
        else:
            input = self.launcher.gameState.stateLog[-1].opp.GetInputState()
            cancelable = self.launcher.gameState.stateLog[-1].opp.is_cancelable
            bufferable = self.launcher.gameState.stateLog[-1].opp.is_bufferable
            parry1 = self.launcher.gameState.stateLog[-1].opp.is_parry_1
            parry2 = self.launcher.gameState.stateLog[-1].opp.is_parry_2
        frame_count = self.launcher.gameState.stateLog[-1].frame_count
        # print(input)
        self.update_input1(input, self.color_from_cancel_booleans(cancelable, bufferable, parry1, parry2))
        self.update_input2(input, self.color_from_cancel_booleans(cancelable, bufferable, parry1, parry2))

    def color_from_cancel_booleans(self, cancelable, bufferable, parry1, parry2):
        if parry1:
            fill_color = 'orange'
        elif parry2:
            fill_color = 'yellow'
        elif bufferable:
            fill_color = 'MediumOrchid1'
        elif cancelable:
            fill_color = 'SteelBlue1'
        else:
            fill_color = 'firebrick1'
        return fill_color

    def update_input1(self, input, cancel_color):
        input_tag = "inputs"
        self.stored_inputs1.append(input)
        self.stored_cancels1.append(cancel_color)
        if len(self.stored_inputs1) >= self.length:
            self.stored_inputs1 = self.stored_inputs1[-self.length:]
            self.stored_cancels1 = self.stored_cancels1[-self.length:]
            if input != self.stored_inputs1[-2]:
                self.canvas1.delete(input_tag)

                #print(self.stored_inputs)
                for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs1):
                    self.canvas1.create_text(i * self.step + (self.step / 2), 30, text=GUI_Master.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
                    self.canvas1.create_text(i * self.step + (self.step / 2), 55, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)
                    x0 = i * self.step + 4
                    x1 = x0 + self.step - 8
                    self.canvas1.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels1[i], tag=input_tag)

    def update_input2(self, input, cancel_color):
        input_tag = "inputs"
        self.stored_inputs2.append(input)
        self.stored_cancels2.append(cancel_color)
        if len(self.stored_inputs2) >= self.length:
            self.stored_inputs2 = self.stored_inputs2[-self.length:]
            self.stored_cancels2 = self.stored_cancels2[-self.length:]
            if input != self.stored_inputs2[-2]:
                self.canvas2.delete(input_tag)

                #print(self.stored_inputs)
                for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs2):
                    self.canvas2.create_text(i * self.step + (self.step / 2), 30, text=GUI_Master.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
                    self.canvas2.create_text(i * self.step + (self.step / 2), 55, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)
                    x0 = i * self.step + 4
                    x1 = x0 + self.step - 8
                    self.canvas2.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels2[i], tag=input_tag)
