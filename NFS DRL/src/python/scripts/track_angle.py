import time

from pymem import Pymem


class TrackAngle:
    
    def __init__(self):
        # address is memory address of current lap
        self.pm =  Pymem("speed.exe")
        
    def track(self):
        angle = self.pm.read_int(0x009B37A8) # state of game
        return(angle)
        
if __name__ == "__main__":
    track_angle = TrackAngle()
    while True:
        angle = track_angle.track()
        print(angle, end="\r")
