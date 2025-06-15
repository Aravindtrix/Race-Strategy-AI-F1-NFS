# import time
#
# from pymem import Pymem
# #from binascii import hexlify
#
#
# class TrackGamepad:
#
#     def __init__(self):
#         # address is memory address of current lap
#         self.pm =  Pymem("speed.exe")
#         pat = b"Logitech RumblePad 2 USB"
#         #pat = b"Controller \(XBOX 360 For Windows\)"
#         self.address = self.pm.pattern_scan_all(pat, return_multiple=True)[1]
#
#     def track(self):
#         lstick_x = -1 + 2 * ((self.pm.read_int(self.address + 288) / 0xFFFF))
#         rstick_y = 1 - 2 * self.pm.read_int(self.address + 820) / 0xFFFF
#         brake = self.pm.read_int(self.address + 320) / 0x80
#         return((lstick_x, rstick_y, brake))
#
# if __name__ == "__main__":
#     track_gamepad = TrackGamepad()
#     while True:
#         gamepad = track_gamepad.track()
#         gamepad_print = tuple(map(lambda x: isinstance(x, float) and f'{x:5.2f}' or x, gamepad))
#         print(gamepad_print, end="\r")
#
import keyboard
import time


class TrackKeyboard:

    def __init__(self):
        # Define the keys you want to monitor
        self.left_key = 'left'
        self.right_key = 'right'
        self.up_key = 'up'
        self.down_key = 'down'
        self.brake_key = 'space'  # Using space for brake

    def track(self):
        # Check if keys are pressed and assign values
        lstick_x = -1 if keyboard.is_pressed(self.left_key) else 1 if keyboard.is_pressed(self.right_key) else 0
        rstick_y = -1 if keyboard.is_pressed(self.down_key) else 1 if keyboard.is_pressed(self.up_key) else 0
        brake = 1 if keyboard.is_pressed(self.brake_key) else 0
        return (lstick_x, rstick_y, brake)


if __name__ == "__main__":
    track_keyboard = TrackKeyboard()
    while True:
        controls = track_keyboard.track()
        print("Steering: {}, Throttle: {}, Brake: {}".format(*controls), end="\r")
        time.sleep(0.1)  # Sampling rate, adjust as needed for responsiveness
