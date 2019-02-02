
import sys
import os
from ctypes import *
import time


dll_path = os.path.dirname(__file__) + os.sep + "vXboxInterface.dll"

try:
    vj = cdll.LoadLibrary(dll_path)
except OSError:
    sys.exit("Unable to load controller SDK DLL. Ensure that {} is present".format("vXboxInterface.dll"))



class VXBOX_Device(object):
    def __init__(self, rID=None):
        self.id = rID
        self.is_on = False


    def a_d(self, cfg, flipx=None):
        result = vj.SetBtnA(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def a_u(self, cfg, flipx=None):
        result = vj.SetBtnA(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def b_d(self, cfg, flipx=None):
        result = vj.SetBtnB(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def b_u(self, cfg, flipx=None):
        result = vj.SetBtnB(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def x_d(self, cfg, flipx=None):
        result = vj.SetBtnX(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def x_u(self, cfg, flipx=None):
        result = vj.SetBtnX(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def y_d(self, cfg, flipx=None):
        result = vj.SetBtnY(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def y_u(self, cfg, flipx=None):
        result = vj.SetBtnY(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def rb_d(self, cfg, flipx=None):
        result = vj.SetBtnRB(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def rb_u(self, cfg, flipx=None):
        result = vj.SetBtnRB(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def lb_d(self, cfg, flipx=None):
        result = vj.SetBtnLB(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def lb_u(self, cfg, flipx=None):
        result = vj.SetBtnLB(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def start_d(self, cfg, flipx=None):
        state = True
        result = vj.SetBtnStart(self.id, state)
        if result == False:
            return False
        else:
            return time.time()

    def start_u(self, cfg, flipx=None):
        state = False
        result = vj.SetBtnStart(self.id, state)
        if result == False:
            return False
        else:
            return time.time()

    def back_d(self, cfg, flipx=None):
        result = vj.SetBtnBack(self.id, True)
        if result == False:
            return False
        else:
            return time.time()

    def back_u(self, cfg, flipx=None):
        result = vj.SetBtnBack(self.id, False)
        if result == False:
            return False
        else:
            return time.time()

    def rt_d(self, cfg, flipx=None):
        result = vj.SetTriggerR(self.id, 255)
        if result == False:
            return False
        else:
            return time.time()

    def rt_u(self, cfg, flipx=None):
        result = vj.SetTriggerR(self.id, 0)
        if result == 0:
            return False
        else:
            return time.time()

    def lt_d(self, cfg, flipx=None):
        result = vj.SetTriggerL(self.id, 255)
        if result == False:
            return False
        else:
            return time.time()

    def lt_u(self, cfg, flipx=None):
        result = vj.SetTriggerL(self.id, 0)
        if result == 0:
            return False
        else:
            return time.time()

    def ls_d(self, cfg, flipx=None):
        result = vj.SetBtnLT(self.id, True)
        if result == 0:
            return False
        else:
            return time.time()

    def ls_u(self, cfg, flipx=None):
        result = vj.SetBtnLT(self.id, False)
        if result == 0:
            return False
        else:
            return time.time()

    def rs_d(self, cfg, flipx=None):
        result = vj.SetBtnRT(self.id, True)
        if result == 0:
            return False
        else:
            return time.time()

    def rs_u(self, cfg, flipx=None):
        result = vj.SetBtnRT(self.id, False)
        if result == 0:
            return False
        else:
            return time.time()


    def dpu_d(self, cfg, flipx=None):
        result = vj.SetDpadUp(self.id)
        if result == False:
            return False
        else:
            return time.time()

    def dpu_u(self, cfg, flipx=None):
        res = vj.SetDpadOff(self.id)
        if res == True:
            return time.time()
        else:
            return res

    def dpr_d(self, cfg, flipx=None):
        if flipx == True:
            result = vj.SetDpadRight(self.id)
        else:
            result = vj.SetDpadRight(self.id)

        if result == False:
            return False
        else:
            return time.time()

    def dpr_u(self, cfg, flipx=None):
        res = vj.SetDpadOff(self.id)
        if res == True:
            return time.time()
        else:
            return res

    def dpl_d(self, cfg, flipx=None):
        if flipx == True:
            result = vj.SetDpadLeft(self.id)
        else:
            result = vj.SetDpadLeft(self.id)
        if result == False:
            return False
        else:
            return time.time()

    def dpl_u(self, cfg, flipx=None):
        res = vj.SetDpadOff(self.id)
        if res == True:
            return time.time()
        else:
            return res

    def dpd_d(self, cfg, flipx=None):
        result = vj.SetDpadDown(self.id)
        if result == False:
            return False
        else:
            return time.time()

    def dpd_u(self, cfg, flipx=None):
        res = vj.SetDpadOff(self.id)
        if res == True:
            return time.time()
        else:
            return res

    def la_dr(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_r(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_ur(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_l(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_ul(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_u(self, cfg, flipx=None):
        return self.la(cfg)

    def la_dl(self, cfg, flipx=None):
        if flipx == True:
            return self.la(cfg, flipx=flipx)
        return self.la(cfg)

    def la_d(self, cfg, flipx=None):
        return self.la(cfg)

    def la_n(self, cfg, flipx=None):
        result = vj.SetAxisY(self.id, 0)
        result = vj.SetAxisX(self.id, 0)
        if result == True:
            return time.time()
        else:
            return result


    def ra_dr(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_r(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_ur(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_dr(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_ul(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_u(self, cfg, flipx=None):
        return self.ra(cfg)

    def ra_dl(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_d(self, cfg, flipx=None):
        return self.ra(cfg)

    def ra_l(self, cfg, flipx=None):
        if flipx == True:
            return self.ra(cfg, flipx=flipx)
        return self.ra(cfg)

    def ra_n(self, cfg, flipx=None):
        result = vj.SetAxisRy(self.id, 0)
        result = vj.SetAxisRx(self.id, 0)
        if result == True:
            return time.time()
        else:
            return result


    def la(self, state, flipx=False):
        x, y = (int(state['x fix']), int(state['y fix']))


        result = vj.SetAxisY(self.id, y)

        if result == False:
            print("bad result: x,y = {}".format(str(x, y)))
            return False

        xval = x if flipx == False else -x
        result = vj.SetAxisX(self.id, xval)

        if result == False:
            print("bad result: x,y = {}".format(str(x, y)))
            return False

        return time.time()

    def ra(self, state, flipx=False):
        x, y = (int(state['x fix'] * 65536), int(state['y fix'] * 65536))

        result = vj.SetAxisRy(self.id, hex(y))

        if result == False:
            # print("bad result: hexy = {}".format(hexy))
            return False

        xval = x if flipx == False else -x
        result = vj.SetAxisRx(self.id, hex(xval))

        if result == False:
            return False

        return time.time()

    def delay(self, t, flipx=None):
        try:
            time.sleep(t)
        except ValueError:
            pass
        return time.time()


    def neutral(self, cfg, flipx=None):
        vj.SetBtnA(self.id,False)
        vj.SetBtnB(self.id,False)
        vj.SetBtnX(self.id,False)
        vj.SetBtnY(self.id,False)
        vj.SetBtnRB(self.id,False)
        vj.SetBtnLB(self.id,False)
        vj.SetBtnStart(self.id,False)
        vj.SetBtnBack(self.id,False)
        vj.SetTriggerR(self.id,0)
        vj.SetTriggerL(self.id,0)
        vj.SetDpadOff(self.id)
        vj.SetAxisX(self.id,0)
        vj.SetAxisY(self.id,0)
        vj.SetAxisRx(self.id,0)
        vj.SetAxisRy(self.id,0)
        return time.time()

    def isControllerOwned(self, cfg):
        return self.isControllerOwned(self.id)

    def isControllerExists(self, cfg):
        return self.isControllerExists(self.id)

    def TurnOff(self):
        try:
            if self.is_on == True:
                self.is_on = False
                vj.UnPlug(self.id)
                return True
        except:
            return False

    def TurnOn(self):
        try:
            if self.is_on == False:
                vj.PlugIn(self.id)
                self.is_on = True
                print("joystick turned on successfully")
                return True
        except Exception as e:
            print("CANNOT TURN ON JOYSTICK due to error: ", e)
            # print("controller already on or taken")
            return False

    def reset(self, cfg):
        self.TurnOff(self.id)
        # print("RESETTING...")
        time.sleep(3)
        return self.TurnOn(self.id)


    def __del__(self):
        # print("DEL")
        # free up the controller before losing access
        self.TurnOff()

    def isVBusExists(self):
        result = vj.isVBusExists(self.id)

        if result == False:
            return False
        else:
            return True

    def isControllerOwned(self, n):
        return vj.isControllerOwned(n)

    def isControllerExists(self, n):
        return vj.isControllerExists(n)

    def GetNumEmptyBusSlots(self, n):
        return vj.GetNumEmptyBusSlots(UCHAR * nSlots)
