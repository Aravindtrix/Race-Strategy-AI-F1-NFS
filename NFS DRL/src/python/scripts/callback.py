import logging
from pathlib import Path
from stable_baselines3.common.callbacks import BaseCallback


class NfsmwAiCallback(BaseCallback):

    def __init__(self, save_path, save_freq=20000, verbose=1):
        super(NfsmwAiCallback, self).__init__(verbose)
        self.save_freq = save_freq
        self.save_path = Path(save_path)

    def _init_callback(self):
        if self.save_path is not None:
            self.save_path.mkdir(parents=True, exist_ok=True)

    def _on_step(self):
        if self.model._n_updates % self.save_freq == 0:
            model_path = self.save_path / f"best_model_{self.model._n_updates}"
            self.model.save(model_path)
        return True

class NfsmwAiEpisodeCallback(BaseCallback):

    def __init__(self, save_path, verbose=1):
        super(NfsmwAiEpisodeCallback, self).__init__(verbose)
        self.save_path = Path(save_path)
        self.log_path = self.save_path / "info.log"
        self.best_lap_time = float("inf")

    def _init_callback(self):
        if self.save_path is not None:
            self.save_path.mkdir(parents=True, exist_ok=True)

        # set up logger
        self.nfsmwai_logger = logging.getLogger("nfsmwai")
        log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = logging.FileHandler(self.log_path, mode="a")
        file_handler.setFormatter(log_formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self.nfsmwai_logger.addHandler(file_handler)
        self.nfsmwai_logger.addHandler(console_handler)
        self.nfsmwai_logger.setLevel(logging.DEBUG)

    def _on_step(self):
        episode_num = self.model._episode_num
        n_updates = self.model._n_updates
        #env = self.training_env
        done = self.locals["dones"][0]
        if done:
            info = self.locals["infos"][0]
            is_complete = info['done_reason'] == "lap_completed"
            is_best = info['lap_time'] < self.best_lap_time
            is_sane = info['lap_time'] >= 1
            if is_complete & is_best & is_sane:
                self.best_lap_time = info['lap_time']
            log_msg = (f"n_updates: {n_updates}, " 
                       f"episode: {episode_num}, "
                       f"done_reason: {info['done_reason']}, "
                       f"lap_time: {info['lap_time']}, "
                       f"new_best_laptime: {is_best}, "
                       f"current_best_lap_time: {self.best_lap_time}")
            self.nfsmwai_logger.info(log_msg)
        #print(episode_num, n_updates, done, info["lap_time"], info["done_reason"])
        return True

