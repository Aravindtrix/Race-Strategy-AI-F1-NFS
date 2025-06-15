import time
import numpy as np
from collections import deque
import gym
from gym import spaces
from matplotlib import pyplot as plt

from nfsmw import NfsMw


class NfsAiHotLap(gym.Env):
    """Custom Environment that follows gym interface"""

    metadata = {"render.modes": ["human"]}

    def __init__(self, pad):
        super(NfsAiHotLap, self).__init__()
        # init
        self.nfs = NfsMw()
        self.pad = pad
        self.last_lap = 1
        self.time_limit = 2*60 # TODO: Remove this hard limit
        self.total_completion = deque([0, 0], maxlen=2)
        self.steering = deque([0, 0, 0, 0, 0], maxlen=5)
        self.speed = deque([0, 0,], maxlen=2)
        self.laptime = deque([0, 0.1], maxlen=2)
        self.max_completion = 0

        # steering (left, right), accelerate (brake, throttle)
        # acceleration -0.4 is essentially braking, but not reversing
        self.action_space = spaces.Box(low=np.array([-1.0, -1.0]),
                                       high=np.array([1.0, 1.0]),
                                       shape=(2, ), dtype=np.float32)
        # for Heritage Heights and Lotus only!
        # x, y ,z limits vary for other tracks
        # speed max. 111m/s = ca. 400km/h
        # surface left, surface right (int actually 0:?)
        # angle -0.5pi, 0.5pi
        self.observation_space = spaces.Box(
            low=np.concatenate([np.array([0.0, 0.0, 0.0, 0]), # telemetry
                                np.zeros(181, dtype=np.float32), # lidar distance
                                #np.full(181, -np.pi/2, dtype=np.float32), # lidar pitch
                                np.full(5, -1, dtype=np.float32), # steering (last 5)
                                np.array([0.0, 0.0, 0, -1000.0]), # collision, reverse, airtime, correct track, acceleration
                                np.zeros(200, dtype=np.float32), # angle ahead
                                np.zeros(200, dtype=np.float32)]), # inverse radii ahead
            high=np.concatenate([np.array([111.0, 10.0, 10.0, 2 * np.pi]), # telemetry
                                 np.full(181, 300, dtype=np.float32), # lidar distance
                                 #np.full(181, np.pi/2, dtype=np.float32), # lidar pitch
                                 np.full(5, 1, dtype=np.float32), # steering (last 5)
                                 np.array([1.0, 1.0, 1, 1000.0]), # collision, reverse, airtime, correct track, acceleration
                                 np.full(200, 2*np.pi, dtype=np.float32), # angle ahead
                                 np.full(200, 2, dtype=np.float32)]), # inverse radii
            shape=(4 + 181 + 5 + 1 + 1 + 1 + 1 + 200 + 200,), dtype=np.float32
        )

    def step(self, action):
        # save t-1.. steering
        self.steering.append(action[0])
        # take action
        self.pad.steer(action[0])
        # discretize throttle
        self.pad.accelerate(self._step_throttle(action[1]))
        self.pad.update()
        # update telemetry
        self.nfs.update_telemetry()
        # get completion
        self.total_completion.append(self.nfs.lap_completion_weighted())
        # get delta in completion
        delta_completion = (self.total_completion[1] - self.total_completion[0])
        # stop reversing over finish to count std value = 0.000351
        delta_completion = delta_completion if delta_completion >= 0 else 0
        # set delta to zero if no new max completion was reached
        if (delta_completion > 0) and (self.total_completion[1] <= self.max_completion):
            delta_completion = 0
        # update max completion
        self.max_completion = max(self.total_completion[1], self.max_completion)
        # check for collision
        #collison = self.nfs.vehicle_collision()
        #speed = self.nfs.vehicle_telemetry()[3] / (345.0 / 3.6)
        # calculate reward
        reward = (1 + self.nfs.lap_on_correct_track()) / 2 * 10000 * delta_completion #* (1 + speed)
        # get next observation
        observation = self._observation()
        # check for done
        current_lap = self.nfs.lap()
        reason = None
        # lap completed
        if current_lap > self.last_lap:
            done = True
            reason = "lap_completed"
            self.last_lap = current_lap
        # 99.6% completed (avoid new lap, as it can cause the game to crash)
        elif self.nfs.lap_completion_weighted() >= 0.99:
            done = True
            reason = "lap_completed"
        # time limit reached
        elif self.nfs.laptime() >= self.time_limit: # time limit
            done = True
            reason = "time_limit"
        # vehicle reverses
        elif (self.nfs.vehicle_reverse() > 0):
            done = True
            reason = "vehicle_reverse"
        # HACK: wrong turn (left) in tunnel
        #elif (np.linalg.norm(self.nfs.vehicle_telemetry()[0:2] - np.array([214.1, 2012.7])) <= 8.0):
            #done = True
        else:
            done = False
        info = {"lap_time": self.nfs.laptime(), 
                "done_reason": reason}
        return observation, reward, done, info

    def reset(self):
        # reset controls
        self.pad.reset()
        self.pad.accelerate(1.0)
        self.pad.update()
        # reset max completion
        self.total_completion.append(0)
        self.max_completion = 0
        self.steering.append(0)
        self.speed.append(0)
        # max laps are limited to 127
        # hard reset required then
        if self.nfs.lap() >= 126:
            # restart race
            self.nfs.restart_race()
            # re-initialize game class
            self.nfs = NfsMw()
        self.nfs.reset_vehicle()
        time.sleep(0.5)
        #self.laptime = [0, 0.1]
        #self.total_completion = [0, 0]
        # reset vehicle
        # get observation
        observation = self._observation()
        return observation

    def render(self, mode="human"):
        img = self.nfs.screenshot()
        plt.imshow(img[:, :, 0:3][:, :, ::-1])
        plt.show()

    def close(self):
        # set pad to default state
        self.pad.reset()
        self.pad.update()

    def _observation(self):
        # update all telemetry data
        self.nfs.update_telemetry()
        telemetry = self.nfs.vehicle_telemetry()
        # get acceleration
        self.laptime.append(self.nfs.laptime())
        self.speed.append(telemetry[3])
        # acceleration
        accel = (self.speed[1] - self.speed[0]) / (self.laptime[1] - self.laptime[0])
        observation = np.concatenate([self.nfs.vehicle_telemetry(), # 7
                                      self.nfs.vehicle_lidar(1), # 181 lidar distance
                                      #self.nfs.vehicle_lidar(1)[1], # 181 lidar pitch
                                      np.array(self.steering), # 5
                                      np.array([self.nfs.vehicle_collision()]), # 1
                                      np.array([self.nfs.vehicle_reverse()]), #1
                                      #np.array([self.nfs.vehicle_airtime()]), # 1
                                      #np.array([self.nfs.lap_completion()]), # 1
                                      np.array([self.nfs.lap_on_correct_track()]), # 1
                                      np.array([accel]), # 1
                                      self.nfs.lap_angle_ahead(n_ahead=200), # 200
                                      self.nfs.lap_radii_ahead(n_ahead=200, inverse=True)]) # 200
        #get rid of x, y, z
        observation = observation[3:]
        return(observation)
    
    def _step_throttle(self, throttle):
        if throttle >= -1.000:
            new_throttle = -0.4 # brake
        if throttle >= -0.975:
            new_throttle = 0.7 # lift
        if throttle >= -0.950:
            new_throttle = 1.0 # full throttle
        return(new_throttle)