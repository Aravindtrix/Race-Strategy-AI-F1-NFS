import time

from pymem import Pymem


class TrackLap:
    
    def __init__(self):
        # address is changing, use pattern search to find first lap only!
        pat = b".\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00....\x00\xcd\xcd\xcd....\x00\x00\x00"
        self.pm =  Pymem("speed.exe")
        self.address = self.pm.pattern_scan_all(pat) + 8
        
    def track(self):
        lap = self.pm.read_int(self.address) # current lap
        return(lap)
        
if __name__ == "__main__":
    track_lap = TrackLap()
    while True:
        lap = track_lap.track()
        print(lap, end="\r")
