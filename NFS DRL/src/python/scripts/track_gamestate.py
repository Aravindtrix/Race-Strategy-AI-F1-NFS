import time

from pymem import Pymem


class TrackGameState:
    
    def __init__(self):
        # address is memory address of current lap
        self.pm =  Pymem("speed.exe")
        
    def track(self):
        """
        track the state of the game
        3: menu
        4: loading
        6: race
        others unknown
        """
        gamestate = self.pm.read_int(0x00925E90) # state of game
        return(gamestate)
        
if __name__ == "__main__":
    track_gamestate = TrackGameState()
    while True:
        gamestate = track_gamestate.track()
        print(gamestate, end="\r")
