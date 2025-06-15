import time
import numpy as np
import pandas as pd
from scipy import spatial

from track_gamestate import TrackGameState
from track_vehicle import TrackVehicle
from track_angle import TrackAngle
from track_surface import TrackSurface
from track_lap import TrackLap
from press_keys import PressKey, ReleaseKey
from windowinterface import WindowInterface

class NfsMw():

    def __init__(self):
        self.tgs = TrackGameState()
        self.tv = TrackVehicle()
        self.ta = TrackAngle()
        self.ts = TrackSurface()
        self.tl = TrackLap()
        # initialize gamestate
        self.gamestate = 0
        # get current time on creation for tracking lap
        self.thetime = time.time()
        # initialize laps
        self.current_lap = 1
        # for screenshots
        self.windowinterface = WindowInterface()
        # telemetry
        self.telemetry = None
        # DataFrame for reference trajectories
        self.df_border_l = None
        self.df_border_r = None
        self.df_traj = None
        # KDTree for reference trajectory
        self.kd = None
        self.kdr = None
        self.kdl = None
        self.kdw = None
        # angles for scaling
        self.interp_angle = None
        self._trajectory()

    def state(self):
        # gamesate
        self.gamestate = self.tgs.track()
        return(self.gamestate)
    
    def update_telemetry(self):
        """update all relevant telemetry data"""
        # coordinates and speed
        x, y, z, speed = self.tv.track()
        # ground surface
        sfc_l, sfc_r = self.ts.track()
        # angle
        direction = self._angle_rotate(self.ta.track())
        # create telemetry
        self.telemetry = np.array([x, y, z, speed, sfc_l, sfc_r, direction])

    def vehicle_telemetry(self):
        return(self.telemetry)

    def vehicle_border_detector(self, return_index=False):
        # get coordinate of car
        telemetry = self.telemetry
        # calculate distance to closest left/right border
        distance_l, idx_l = self.kdl.query(telemetry[0:3])
        distance_r, idx_r = self.kdr.query(telemetry[0:3])
        distance_border = np.array([distance_l, distance_r])
        if return_index:
            distance_border = (np.array([distance_l, distance_r]), 
                               np.array([idx_l, idx_r]))
        return(distance_border)

    def vehicle_lidar(self, resolution_degree=1):
        lidar = self._lidar(resolution_degree)
        return(lidar)

    def vehicle_collision(self):
        collison = int(np.min(self.vehicle_border_detector()) < 0.5)
        return(collison)

    def vehicle_airtime(self):
        telemetry = self.telemetry
        distance, idx = self.kdl.query(telemetry[0:3])
        z_distance = max(telemetry[2] - self.df_border_l.iloc[idx]["z"], 0)
        return(z_distance)

    def vehicle_reverse(self, rev_angle_threshold=0.6*np.pi):
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        vehicle_direction = telemetry[6]
        trajectory_direction = self._angle_rotate(self.df_traj.iloc[idx]["angle"])
        #print(vehicle_direction, trajectory_direction)
        diff_direction = (vehicle_direction - trajectory_direction) % (2*np.pi)
        reverse = int((diff_direction >= rev_angle_threshold) & # left-side
                      (diff_direction <= (2*np.pi - rev_angle_threshold))) # right side
        #reverse = int(np.abs(vehicle_direction - trajectory_direction) > rev_angle_threshold)
        #print(reverse, vehicle_direction*180/np.pi, trajectory_direction*180/np.pi, diff_direction*180/np.pi)
        return(reverse)

    def lap(self):
        # current lap
        self.current_lap = self.tl.track()
        return(self.current_lap)

    def laptime(self):
        nowtime = time.time()
        laptime = nowtime - self.thetime
        return(laptime)

    def lap_completion(self):
        """
        xy: array with [x, y] coordinates
        """
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        completed = idx / self.kd.n
        return(completed)
    
    def lap_completion_weighted(self):
        """
        xy: array with [x, y] coordinates
        """
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3], k=2)
        idx_weighted = np.average(idx, weights = 1 / (distance + 1e-16))
        completed = idx_weighted / self.kd.n
        return(completed)
    
    def lap_distance_completion(self):
        """
        xy: array with [x, y] coordinates
        """
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        completed = self.df_traj.iloc[idx]["distance_completion"]
        return(completed)
    
    def lap_on_correct_track(self):
        # if car takes the correct side before/after the tunnel
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        distance_w, idx_w = self.kdw.query(telemetry[0:3])
        correct_track = int(distance_w >= distance)
        return correct_track

    def lap_angle_ahead(self, n_ahead=150):
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        n_t = self.df_traj.shape[0]
        # approx 100m ahead
        range_t = np.arange(idx, idx + n_ahead) % n_t
        df_traj_angle = self.df_traj.iloc[range_t].copy()
        # get expanding mean of angles
        df_traj_angle["direction"] = self._angle_rotate(df_traj_angle["angle_smooth"])#.expanding().mean()
        # get n_cample samples from n_ahead points
        #idx_sample = np.clip(np.linspace(0, n_ahead - 1, n_samples, dtype=int), 0, n_t-1)
        # get direction samples
        #direction_samples = df_traj_angle.iloc[idx_sample]["direction"]
        direction_samples = df_traj_angle["direction"]
        # return array
        return(direction_samples.values)
    
    def lap_radii_ahead(self, n_ahead=150, inverse=True):
        telemetry = self.telemetry
        distance, idx = self.kd.query(telemetry[0:3])
        n_t = self.df_traj.shape[0]
        # approx 100m ahead
        range_t = np.arange(idx, idx + n_ahead) % n_t
        df_traj_radii = self.df_traj.iloc[range_t].copy()
        radius_samples = df_traj_radii["radius"]
        if inverse:
            radius_samples = 1 / (df_traj_radii["radius"] + 1e-16)
        # return array
        return(radius_samples.values)

    def reset_laptime(self):
        self.thetime = time.time()

    def reset_vehicle(self):
        # reset car to saved start location with hotkey
        # from NFSMW ExtraOps
        PressKey(0x1D) # ctrl key
        PressKey(0x02) # 1 key
        time.sleep(0.01)
        ReleaseKey(0x1D) # ctrl key
        ReleaseKey(0x02) # 1 key
        self.reset_laptime()

    def restart_race(self):
        # reset the whole race and start at lap 1 again
        PressKey(0x01) # ESC
        time.sleep(0.1)
        ReleaseKey(0x01)
        time.sleep(1)
        PressKey(0xCD) # right
        time.sleep(0.1)
        ReleaseKey(0xCD)
        time.sleep(1)
        PressKey(0x1C) # return
        time.sleep(0.1)
        ReleaseKey(0x1C)
        time.sleep(1)
        PressKey(0xCB) # left
        time.sleep(0.1)
        ReleaseKey(0xCB)
        time.sleep(1)
        PressKey(0x1C) # return
        time.sleep(0.1)
        ReleaseKey(0x1C)
        time.sleep(4) # wait for race to start

    def screenshot(self):
        img = self.windowinterface.screenshot()
        return(img)

    def _trajectory(self):
        # TODO: move to proper file format maybe
        df_rf = pd.read_csv("../data/reference_telemetry_heritage_heights.csv")
        # min-max scale angle
        #max_angle = df_rf["angle"].max()
        #min_angle = df_rf["angle"].min()
        #self.interp_angle = interp1d([min_angle, max_angle],[0, 0xFFFF])
        # subsets are border trajectories and main trajectory
        self.df_border_l = df_rf[df_rf["lap"] == 1].reset_index(drop=True).copy()
        self.df_border_r = df_rf[df_rf["lap"] == 2].reset_index(drop=True).copy()
        # enhance borders (left)
        self.df_border_l.index = self.df_border_l.index * 4
        self.df_border_l = self.df_border_l.reindex(range(self.df_border_l.index.max() + 1))
        self.df_border_l[["x", "y", "z"]] = self.df_border_l[["x", "y", "z"]].interpolate()
        # enhance borders (right)
        self.df_border_r.index = self.df_border_r.index * 4
        self.df_border_r = self.df_border_r.reindex(range(self.df_border_r.index.max() + 1))
        self.df_border_r[["x", "y", "z"]] = self.df_border_r[["x", "y", "z"]].interpolate()
        # get wrong and trajectories
        self.df_wrong = df_rf[df_rf["lap"] == 3].reset_index(drop=True).copy()
        # get trajectory
        self.df_traj = df_rf[df_rf["lap"] == 0].reset_index(drop=True).copy()
        # smooth angle
        self.df_traj["angle_smooth"] = self.df_traj["angle"].rolling(10, 1).mean()
        # add distance completion stuff
        self.df_traj[["x_next", "y_next"]] = self.df_traj[["x", "y"]].shift(1)
        self.df_traj["delta_distance"] = np.linalg.norm(self.df_traj[["x", "y"]].values - 
                                                        self.df_traj[["x_next", "y_next"]].values, 
                                                        axis=1)
        self.df_traj["distance_completion"] = (self.df_traj["delta_distance"].cumsum() / 
                                               self.df_traj["delta_distance"].sum())
        self.df_traj["distance_completion"].fillna(0, inplace=True)
        self.df_traj.drop(columns=["x_next", "y_next", "delta_distance"], inplace=True)
        # add curve radius stuff
        self.df_traj[["xb", "yb"]] = self.df_traj[["x", "y"]].shift(1)
        self.df_traj[["xc", "yc"]] = self.df_traj[["x", "y"]].shift(2)
        a = np.linalg.norm(self.df_traj[["x", "y"]].values - self.df_traj[["xb", "yb"]].values, axis=1)
        b = np.linalg.norm(self.df_traj[["xb", "yb"]].values - self.df_traj[["xc", "yc"]].values, axis=1)
        c = np.linalg.norm(self.df_traj[["x", "y"]].values - self.df_traj[["xc", "yc"]].values, axis=1)
        # https://en.wikipedia.org/wiki/Circumscribed_circle
        self.df_traj["radius"] = a*b*c / (np.sqrt((a+b+c)*(-a+b+c)*(a-b+c)*(a+b-c)) + 1e-16)
        self.df_traj["radius"].fillna(1800, inplace=True)
        self.df_traj["radius"] = self.df_traj["radius"].rolling(50, 1).mean()
        self.df_traj.drop(columns=["xb", "yb", "xc", "yc"], inplace=True)
        # build KDTree (exclude last 5 to start with 0 than 99,
        # because finish waypoint may be closer than start waypoint
        self.kd = spatial.KDTree(self.df_traj[["x", "y", "z"]][:-5])
        self.kdl = spatial.KDTree(self.df_border_l[["x", "y", "z"]])
        self.kdr = spatial.KDTree(self.df_border_r[["x", "y", "z"]])
        self.kdw = spatial.KDTree(self.df_wrong[["x", "y", "z"]])

    def _angle_rotate(self, angle):
        """
        nfsmw uses rotated coordinate system axis for angle
        see analyze.R. offset around 20 degrees = 0.3491 rad

        returns: angle in radians as angle between (-1, 0) and
        car direction from 0 up to 2pi (0 up to 360 degrees)
        """
        # min max scale angle to 0xFFFF
        # does not seem to got all the way up to OxFFF
        # angle is value from 0x0000 to 0xFFFF in game from data type
        # but max recorded is like up to 0xFB90 only
        angle = angle / 0xFB90 * 2 * np.pi
        # coordinate system seems orthogonal to track
        # rotate and give correct value in radians
        #angle = (angle - k_rotation_rad) % (2 * np.pi)
        return(angle)

    def _lidar(self, resolution_degree=1):
        # get telemetry
        telemetry = self.telemetry
        # get closest border
        distance, idx = self.vehicle_border_detector(return_index=True)
        # get indices for left and right border
        idx_l = idx[0] 
        idx_r = idx[1] 
        # get max lentgth of border trajectoreis
        n_l = self.df_border_l.shape[0]
        n_r = self.df_border_r.shape[0]
        # 300 points forward = roughly 200m, 50 backwards (border is discrete, closest boarder could be behind)
        range_l = np.arange(max(idx_l - 50 * 4, 0), idx_l + 300 * 4) % n_l
        range_r = np.arange(max(idx_r - 50 * 4, 0), idx_r + 300 * 4) % n_r
        df_next_border_l = self.df_border_l.iloc[range_l][["x", "y"]]
        df_next_border_r = self.df_border_r.iloc[range_r][["x", "y"]]
        # concatenate together
        df_next_border = pd.concat([df_next_border_l, df_next_border_r])
        # calculate distances
        df_next_border["distance"] = np.linalg.norm(df_next_border - telemetry[0:2], axis=1)
        # calculate pitch angle (i.e. border is relatively down or up)
        #df_next_border["pitch"] = np.arcsin((df_next_border["z"] - telemetry[2]) / df_next_border["distance"])
        #df_next_border["pitch"] = 0
        # calculate direction with coordinate system [0, 2pi] counter-clockwise
        df_next_border["direction_border"] = np.pi - np.arctan2(df_next_border["x"] - telemetry[0], df_next_border["y"] - telemetry[1]) #(0, 2pi)
        # calculate direction relative to car
        df_next_border["direction_vehicle"] = (df_next_border["direction_border"] - telemetry[6]) % (2*np.pi)# 6 = direction, modulo to transform
        # get only few discrete points
        resolution = resolution_degree/180 * np.pi # 15 dgerees
        df_next_border["direction_vehicle_d"] = (round(df_next_border["direction_vehicle"] / resolution) * resolution * 180/np.pi)
        # always get the nearest boundary in each direction
        df_lidar_l = df_next_border.groupby("direction_vehicle_d")["distance"].min().reset_index().copy()
        #df_lidar_l = df_next_border.loc[df_next_border.groupby("direction_vehicle_d")["distance"].idxmin()].reset_index().copy()
        #df_next_border.drop(columns=)
        #df_lidar_l = df_next_border.sort_values("distance").drop_duplicates("direction_vehicle_d", keep="first").reset_index().copy()
        #print(df_lidar_l)
        #df_next_border.reset_index(inplace=True)
        #df_next_border["cnt"] = (df_next_border.sort_values("distance")
        #                                       .groupby("direction_vehicle_d")
        #                                       .cumcount())
        #df_lidar_l = df_next_border[df_next_border["cnt"] == 0].reset_index().copy()
        #df_lidar_l = df_lidar_l[["distance", "pitch"]].copy()
        df_lidar_l["direction_vehicle_d"] = round(df_lidar_l["direction_vehicle_d"]).astype(int)
        # homogenous structure (ensure always same number of values) only look ahead so only 180 degrees noit 360
        num_structure = int(180/resolution_degree + 1)
        structure = pd.DataFrame({"direction_vehicle_d": np.linspace(0, 180, num_structure, dtype=int)})
        structure = structure.merge(df_lidar_l, on="direction_vehicle_d", how="left")
        # interpolate for missing values in-between as borders are discrete
        structure["distance"].interpolate(inplace=True)
        # fill values with minumin (usually close on right side)
        #structure["distance"].fillna(method="bfill", inplace=True)
        structure["distance"].fillna(200, inplace=True)
        # interpolate for missing values in-between as borders are discrete
        #structure["pitch"].interpolate(inplace=True)
        # interpolate for missing values in-between as borders are discrete
        #structure["pitch"].fillna(method="bfill", inplace=True)
        #structure["pitch"].fillna(0, inplace=True)
        # return numpy array
        return(structure["distance"].values)
        #return(structure["distance"].values)
