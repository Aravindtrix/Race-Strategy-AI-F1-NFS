import time

from pymem import Pymem


class TrackVehicle:
    
    def __init__(self):
        # address is memory address of current lap
        self.pm =  Pymem("speed.exe")
        
    def track(self):
        x = self.pm.read_float(0x00914560) # x-coordinate
        y = self.pm.read_float(0x00914564) # y-coordinate
        z = self.pm.read_float(0x00914568) # z-coordinate
        speed = self.pm.read_float(0x009142C8) # speed
        #angle = hex(self.pm.read_int(0x098A0D88)) # angle
        return((x, y, z, speed))
        
if __name__ == "__main__":
    track_vecicle = TrackVerhicle()
    while True:
        vehicle = track_vehicle.track()
        print(lap, end="\r")
