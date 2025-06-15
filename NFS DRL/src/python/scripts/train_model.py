import time
import torch as th
from stable_baselines3 import SAC

#from nfsmw import NfsMw
from vnfskeyboard import VNfsKeyBoard
from env import NfsAiHotLap
from callback import NfsmwAiCallback, NfsmwAiEpisodeCallback

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

# try it out
nfsmwai = NfsAiHotLap(pad)
nfsmwai.close()

# name model
model_name = f"sac_nfsmwai_{round(time.time())}"
#model_name = "sac_nfsmwai_1677495033"

# define callbacks
checkpoint_callback = NfsmwAiCallback(save_path=model_name, save_freq=15)
episode_callback = NfsmwAiEpisodeCallback(save_path=model_name)

# create model
#model = SAC("MlpPolicy", nfsmwai, verbose=2, tensorboard_log="tensorboard_logs",
#            gamma=0.985, batch_size=512, buffer_size=3000000)
# load model
custom_objects = {"gamma": 0.98, "buffer_size": 2000000, "batch_size": 4096, "device": "cuda",
                  "seed": 7, "train_freq": (1, "episode")}
                 # "buffer_size": 2000000}
#model = SAC.load("sac_nfsmwai_1677777786/best_model_7580000.zip", custom_objects=custom_objects)
model = SAC.load("../sac_nfsmwai_1678522910/best_model_7580610.zip", custom_objects=custom_objects)

# patch ent_coef
model.ent_coef = 0.03
model.ent_coef_optimizer = None
model.ent_coef_tensor = th.tensor(float(model.ent_coef), device=model.device)

model.set_env(nfsmwai)

# train
time.sleep(5)
model.learn(total_timesteps=1e7, tb_log_name=model_name, log_interval=1,
            callback=[episode_callback, checkpoint_callback])
#model.save(f"sac_nfsmwai_{round(time.time())}")

# stop steering inputs
nfsmwai.close()
