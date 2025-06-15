import time

from pymem import Pymem


class TrackSurface:
    
    def __init__(self):
        # address is changing, use pattern search to find
        self.pm =  Pymem("speed.exe")
        # for this to work car has to be on surface and stand still
        pat = b"\x05\x00\x00\x00\x05\x00{11}\xDC\x05\x00\x00\xDC\x05\x00\x00"
        self.address = self.pm.pattern_scan_all(pat)
        
    def track(self):
        """
        track road surface:
        0: grass
        1: concrete
        2: cobble
        3: ?
        4: ?
        5: asphalt
        """
        surface_left = self.pm.read_int(self.address)
        surface_right = self.pm.read_int(self.address + 4)
        return((surface_left, surface_right))
        
if __name__ == "__main__":
    track_surface = TrackSurface()
    while True:
        surface = track_surface.track()
        print(surface, end="\r")



