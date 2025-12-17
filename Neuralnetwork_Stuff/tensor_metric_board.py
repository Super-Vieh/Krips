from torch.utils.tensorboard import SummaryWriter
import os
import time

class TensorMetricBoard:
    def __init__(self, log_dir:str = "TensorMetricBoard Logs"):
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_dir = os.path.join(log_dir, timestamp)
        self.writer = SummaryWriter(log_dir = file_dir)
    def log_turn(self,current_move,made_moves,valid_moves, epsilon, total_reward, total_loss, reward_loss_ratio, valid_moves_ratio):
        self.writer.add_scalar('turn/made_moves', made_moves, current_move)
        self.writer.add_scalar('turn/valid_moves', valid_moves, current_move)
        self.writer.add_scalar('turn/epsilon', epsilon, current_move)
        self.writer.add_scalar('turn/total_reward', total_reward, current_move)
        self.writer.add_scalar('turn/total_loss', total_loss, current_move)
        self.writer.add_scalar('turn/reward_loss_ratio', reward_loss_ratio, current_move)
        self.writer.add_scalar('turn/valid_moves_ratio', valid_moves_ratio, current_move)





    def close(self):
        self.writer.close()
