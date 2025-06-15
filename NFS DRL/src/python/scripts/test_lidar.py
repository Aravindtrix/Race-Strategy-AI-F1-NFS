import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nfsmw import NfsMw

# create api class
nfsmw = NfsMw()

# check lidar
nfsmw.update_telemetry()
lidar = nfsmw._lidar(1)
#lidar = lidar_pitch[0]
#pitch = lidar_pitch[1]
#scr = nfsmw.screenshot()
direction_vehicle = nfsmw.vehicle_telemetry()[6]
print(direction_vehicle * 180/np.pi)

num_lidar = lidar.shape[0]

# substract car angle to keep stable direction
theta = (np.linspace(0, 180, num_lidar, dtype=int) / 180 * np.pi) % (2*np.pi)
#theta = (theta - 1/3 * np.pi) % (2 * np.pi) # correct rotation
#theta = (theta - 1/4 * np.pi) % (2 * np.pi) # correct axis angle
#theta = (theta - 0.75 * np.pi) % (2 * np.pi) # flip
r = lidar

#r = np.arange(0, 2, 0.01)
#theta = 2 * np.pi * r

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.scatter(theta, r)
#ax.set_rmax(2)
#ax.set_rticks([0.5, 1, 1.5, 2])  # Less radial ticks
#ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
#ax.grid(True)

ax.set_title("A line plot on a polar axis", va='bottom')
plt.show()

# grows fucking clockwise
#np.arctan2(np.array([0, 1, 1, 1, -1]), np.array([-1, -1, 0, 1, 1])) * 180/np.pi + 180

#360 - (np.arctan2(np.array([0, 1, 1, 1, -1]), np.array([-1, -1, 0, 1, 1])) * 180/np.pi + 180)
# telemetry grows fucking anti clockwise
a = 200
#s = 200
angle_ahead = nfsmw.lap_angle_ahead(a)
sub_min = 0.010299839780270085
factor = 1.033463170012458
#angle_ahead = (angle_ahead - sub_min) * factor
#theta = (angle_ahead + 0.5 * np.pi) % (2 * np.pi)
theta = angle_ahead
r = np.arange(0, a)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.scatter(theta, r)
plt.show()

nfsmw.update_telemetry()
angle_ahead = nfsmw.lap_angle_ahead(a)
plt.plot(angle_ahead)
plt.plot(pd.Series(angle_ahead).rolling(10, 1).mean())
plt.show()

# check lap radii ahead
nfsmw.update_telemetry()
radii_ahead = nfsmw.lap_radii_ahead(200, inverse=True)
#radii_ahead = pd.Series(radii_ahead).rolling(50, 1).mean()
plt.plot(radii_ahead)
plt.show()

# check angles from game
angle_arr = []
while True:
    nfsmw.update_telemetry()
    angle = nfsmw.vehicle_telemetry()[6] / (2 * np.pi) * 0xFFFF
    angle_arr.append(angle)
    print(angle, end="\r")

angle_arr_np = np.array(angle_arr)
angle_arr_np.min() #21
angle_arr_np.max() #64370

nfsmw = nfsmwai.nfs
while True:
    nfsmw.update_telemetry()
    print(nfsmw.lap_completion_weighted(), end="\r")