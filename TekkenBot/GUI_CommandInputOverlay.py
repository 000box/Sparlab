from . import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from .MoveInfoEnums import InputDirectionCodes
from .MoveInfoEnums import InputAttackCodes



class TextRedirector(object):
    def __init__(self, canvas, height):
        pass

    def write(self, str):
        pass


class GUI_CommandInputOverlay(GUI_Overlay.Overlay):

    symbol_map = {

        #InputDirectionCodes.u: '⇑',
        #InputDirectionCodes.uf: '⇗',
        #InputDirectionCodes.f: '⇒',
        #InputDirectionCodes.df: '⇘',
        #InputDirectionCodes.d: '⇓',
        #InputDirectionCodes.db: '⇙',
        #InputDirectionCodes.b: '⇐',
        #InputDirectionCodes.ub: '⇖',
        #InputDirectionCodes.N: '★',

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
        GUI_Overlay.Overlay.__init__(self, master, pos, "Tekken Bot: Command Input Overlay")
        self.launcher = launcher

        self.canvas = Canvas(self, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')
        self.canvas.pack(side='left')

        self.length = 120
        self.step = (self.w/self.length)
        self.p1_p2_gap = 30 + (self.w/2)
        self.p2x_start = 30 + (self.w/2)

        for i in range(int(self.length/2)):
            self.canvas.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
            self.canvas.create_line(i * self.step, 0, i * self.step, self.h, fill="red")
            self.canvas.create_text(i * self.step + (self.step / 2) + self.p1_p2_gap, 8, text = str(i), fill='snow')
            self.canvas.create_line(i * self.step + self.p1_p2_gap, 0, i * self.step + self.p1_p2_gap, self.h, fill="red")


        self.canvas

        self.redirector = TextRedirector(self.canvas, self.h)
        # self.redirector2 = TextRedirector(self.canvas2, self.h)

        self.stored_inputs1 = []
        self.stored_cancels1 = []
        self.stored_inputs2 = []
        self.stored_cancels2 = []

    def update_state(self):
        GUI_Overlay.Overlay.update_state(self)
        # if self.launcher.gameState.stateLog[-1].is_player_player_one:
        input1 = self.launcher.gameState.stateLog[-1].bot.GetInputState()
        cancelable1 = self.launcher.gameState.stateLog[-1].bot.is_cancelable
        bufferable1 = self.launcher.gameState.stateLog[-1].bot.is_bufferable
        parry1_1 = self.launcher.gameState.stateLog[-1].bot.is_parry_1
        parry2_1 = self.launcher.gameState.stateLog[-1].bot.is_parry_2
        # else:
        input2 = self.launcher.gameState.stateLog[-1].opp.GetInputState()
        cancelable2 = self.launcher.gameState.stateLog[-1].opp.is_cancelable
        bufferable2 = self.launcher.gameState.stateLog[-1].opp.is_bufferable
        parry1_2 = self.launcher.gameState.stateLog[-1].opp.is_parry_1
        parry2_2 = self.launcher.gameState.stateLog[-1].opp.is_parry_2
        frame_count = self.launcher.gameState.stateLog[-1].frame_count
        # print(input)

        self.update_input((input1, input2), (self.color_from_cancel_booleans(cancelable1, bufferable1, parry1_1, parry2_1), self.color_from_cancel_booleans(cancelable2, bufferable2, parry1_2, parry2_2)))

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

    def update_input(self, input, cancel_color):
        p1_tag, p2_tag = ("p1_input", "p2_input")
        self.stored_inputs1.append(input[0])
        self.stored_cancels1.append(cancel_color[0])
        self.stored_inputs2.append(input[1])
        self.stored_cancels2.append(cancel_color[1])

        if (len(self.stored_inputs1) >= self.length/2) or (len(self.stored_inputs2) >= self.length/2):
            self.stored_inputs1 = self.stored_inputs1[int(-self.length/2):]
            self.stored_cancels1= self.stored_cancels1[int(-self.length/2):]
            self.stored_inputs2 = self.stored_inputs2[int(-self.length/2):]
            self.stored_cancels2= self.stored_cancels2[int(-self.length/2):]

            if input[0] != self.stored_inputs1[-2] or input[1] != self.stored_inputs2[-2]:
                self.canvas.delete(p1_tag)
                self.canvas.delete(p2_tag)
                # print(self.stored_inputs)
                for i, ((direction_code1, attack_code1, rage_flag1), (direction_code2, attack_code2, rage_flag2)) in enumerate(zip(self.stored_inputs1, self.stored_inputs2)):
                    text1 = GUI_CommandInputOverlay.symbol_map[direction_code1]
                    text2 = attack_code1.name.replace('x', '').replace('N', '')
                    text3 = GUI_CommandInputOverlay.symbol_map[direction_code2]
                    text4 = attack_code2.name.replace('x', '').replace('N', '')
                    p2x = i * self.step + (self.step / 2) + self.p1_p2_gap
                    p1x = i * self.step + (self.step / 2)

                    self.canvas.create_text(p1x, 30, text=text1, fill='snow',  font=("Consolas", 12), tag=p1_tag)
                    print("P1: {} {} | P2: {} {}".format(text1, text2, text3, text4))
                    self.canvas.create_text(p1x, 55, text=text2, fill='snow',  font=("Consolas", 8), tag=p1_tag)

                    # if p2x > self.p2x_start:
                    self.canvas.create_text(p2x, 30, text=text3, fill='snow',  font=("Consolas", 12), tag=p2_tag)
                    self.canvas.create_text(p2x, 55, text=text4, fill='snow',  font=("Consolas", 8), tag=p2_tag)

                    x0 = i * self.step + 4
                    x1 = x0 + self.step - 8
                    x2 = (i * self.step + 4) + self.p1_p2_gap
                    x3 = (x2 + self.step - 8) + self.p1_p2_gap

                    self.canvas.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels1[i], tag=p1_tag)
                    self.canvas.create_rectangle(x2, 70, x3, self.h - 5, fill=self.stored_cancels2[i], tag=p2_tag)
                    print("_______________")
