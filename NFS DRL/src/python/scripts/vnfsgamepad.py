import vgamepad as vg
import time


class VNfsGamePad:
    
    def __init__(self):
        # initialize gamepad
        self.gamepad = vg.VX360Gamepad()
        
    def steer(self, x):
        """
        x (float): [-1, 1] -1 full left, +1 full right
        """
        self.gamepad.left_joystick_float(x_value_float=x, y_value_float=0.0)

    def accelerate(self, y):
        """
        y (float): [-1, 1] -1 full brake, +1 full throttle
        """
        self.gamepad.right_joystick_float(x_value_float=0.0, y_value_float=y)

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
        self.gamepad.update()

    def reset(self):
        """
        reset to default state, needs update after
        """
        self.gamepad.reset() 

        
if __name__ == "__main__":
    vgp = VNfsGamePad()
    time.sleep(2)
    vgp.throttle(1.0)
    vgp.update()
    time.sleep(2)
    vgp.brake()
    vgp.update()



