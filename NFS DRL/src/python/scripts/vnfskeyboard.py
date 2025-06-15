import time

from press_keys import PressKey, ReleaseKey


class VNfsKeyBoard:
    
    def __init__(self):
        self.kbd = 0
        
    def steer(self, x):
        """
        x (float): [-1, 1] -1 full left, +1 full right
        """
        if x > 0:
            ReleaseKey(0xCB)
            #time.sleep(1/60)
            PressKey(0xCD) # right
            #ReleaseKey(0xCD)
        else:
            ReleaseKey(0xCD)
            PressKey(0xCB) # left
            #ReleaseKey(0xCB)

    def accelerate(self, y):
        """
        y (float): [-1, 1] -1 full brake, +1 full throttle
        """
        if y > 0:
            ReleaseKey(0xD0)
            #time.sleep(1/60)
            PressKey(0xC8)
        else:
            ReleaseKey(0xD0)
            #time.sleep(1/60)
            PressKey(0xD0) # left

    #def brake(self, press):
    #    """
    #    press (bool): press or release brake
    #    """
    #    if press:
    #        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    #    else:
    #        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

    def update(self):
        """
        update state of gamepad with current values
        """
        pass

    def reset(self):
        """
        reset to default state, needs update after
        """
        ReleaseKey(0xCD)
        ReleaseKey(0xCB)
        ReleaseKey(0xC8)
        ReleaseKey(0x0D)

        
if __name__ == "__main__":
    vkb = VNfsKeyBoard()
    time.sleep(2)
    vkb.accelerate(1.0)
    vkb.update()
    time.sleep(2)
    #vkb.brake()
    vkb.update()