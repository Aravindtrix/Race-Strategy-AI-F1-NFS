import time
import numpy as np
from stable_baselines3 import SAC

#from nfsmw import NfsMw
from vnfskeyboard import VNfsKeyBoard
from env import NfsAiHotLap

# init gamepad before launch of game
# important as otherwise gamepad uis not recognized
pad = VNfsKeyBoard()

# start NFSMW and start race now
# Quick Race -> Custom Race -> Circuit
# NFSMW ExtraOps required to ahve more than 6 laps
# Heritage Heights
# Laps: 127
# Traffic Level: None 
# Opponents:0
# Difficulty: Easy (irrelevant)
# Catch Up: Off (irrelevant)
# Transmission: Automatic (Manual does not give any advantage in the game)

# # try it out
nfsmwai = NfsAiHotLap(pad)
nfsmwai.close()
#
# do some random stuff
# time.sleep(5)
# for episode in range(2):
#     observation = nfsmwai.reset()
#     time.sleep(0.05)
#     done = False
#     total_reward = 0
#     while not done:
#         time.sleep(1/30)
#         action = nfsmwai.action_space.sample()
#         observation, reward, done, info = nfsmwai.step(action)
#         print(round(reward, 5), end="\n")
# nfsmwai.close()

# load model
model = SAC.load("../sac_nfsmwai_1678522910/best_model_7580610.zip",  # 610 best
                 custom_objects={"device": "cpu",
                                 "buffer_size": 50000})
#model = SAC.load("sac_nfsmwai_1677251871/best_model_4920000.zip") # 418 hat 1:10s
model.set_env(nfsmwai)

time.sleep(3)
fps_limit = 25
now = time.time()
obs = nfsmwai.reset()
while True:
    start_time = time.time()
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = nfsmwai.step(action)
    action_print = np.round(action, 2)
    fps = 1.0 / (time.time() - start_time)
    print(f"steering: {action_print[0]:5.2f}, "
          f"throttle: {nfsmwai._step_throttle(action_print[1]):5.2f}, "
          f"ai_fps: {fps:5.2f}",
          end="\r")
    #if done:
      #obs = nfsmwai.reset()
    # only execute in fixed tick rate
    time.sleep(1/fps_limit - ((time.time() - now) % 1/fps_limit))
nfsmwai.close()
