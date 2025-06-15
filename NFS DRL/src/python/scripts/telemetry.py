import sys
import time
import datetime
import numpy as np
import pandas as pd

from track_gamestate import TrackGameState
from track_vehicle import TrackVehicle
from track_surface import TrackSurface
from track_lap import TrackLap
from track_gamepad import TrackKeyboard
from track_angle import TrackAngle
from press_keys import PressKey, ReleaseKey


def record_telemetry():
    # switch to game within x seconds
    time.sleep(1)
    # instantiate data
    tgs = TrackGameState()
    tv = TrackVehicle()
    ts = TrackSurface()
    tl = TrackLap()
    tg = TrackKeyboard()
    ta = TrackAngle()
        
    # initialize
    data = None
    data_telemetry = [] # array to store telemetry
    thetime = time.time()  # current time
    last_lap = 0  # initial value for last lap
    lap = 1  # initial value for current lap
    fps = 100 # tracking fps
    #looptime = time.time() # cuurent time for loop
    #telemetry_time = 7 # time to track teleetry in minutes
    telemetry_laps = 5 # lap up to which to track telemetry
    reset = False # reset every lap with same speed and location
    
    # 
    #while time.time() < (looptime + 60 * telemetry_time):
    while True:
        # check gamestate
        gamestate = tgs.track()
        # end tracking when restert or exit
        if gamestate != 6:
            break
        # get telemetry data
        lap = tl.track()
        data_vehicle = tv.track()
        data_surface = ts.track()
        data_gamepad = tg.track()
        data_angle = ta.track()
        nowtime = time.time()
        laptime = nowtime - thetime

        # on lap completion reset time
        if lap > last_lap:
            last_lap = lap
            if reset:
                # reset car to saved start location with hotkey
                # from NFSMW ExtraOps
                PressKey(0x1D) # ctrl key
                PressKey(0x02) # 1 key
                time.sleep(0.01)
                ReleaseKey(0x1D) # ctrl key
                ReleaseKey(0x02) # 1 key
            thetime = nowtime
            print(data)
            continue
        
        # combine data
        data = (data_vehicle + 
                data_surface + 
                (lap, laptime) + 
                data_gamepad +
                (data_angle, ))
        data_telemetry.append(data)
        # round floats to 2 fixed decimals
        data_print = tuple(map(lambda x: isinstance(x, float) and f'{x:7.2f}' or x, data))
        #print(data_print, end="\r")
        print(f"""x: {data_print[0]}, y: {data_print[1]}, z: {data_print[2]} 
speed: {data_print[3]}, angle: {hex(data_print[11])} 
surface_l: {data_print[4]}, surface_r: {data_print[5]} 
lap: {data_print[6]}, laptime: {data_print[7]} 
steering: {data_print[8]}, throttle: {data_print[9]}, brake: {data_print[10]}""")
        sys.stdout.write("\033[F"*5) # Cursor up 5 lines
        
        # only execute in fixed tick rate
        time.sleep(1/fps - ((time.time() - thetime) % 1/fps))
        
    # stop tracking of vehicle with shift+1 ingame
    #ReleaseKey(0x2A) # shift key
    #ReleaseKey(0x02) # 1 key  
          
    # save data
    df = pd.DataFrame(data_telemetry)
    df.columns = ["x", "y", "z", "speed", 
                  "surface_l", "surface_r",
                  "lap", "laptime", 
                  "steering", "throttle", "brake",
                  "angle"]
    csv_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_telemetry.csv")
    df.to_csv(csv_name, index=False)

if __name__ == "__main__":
    record_telemetry()