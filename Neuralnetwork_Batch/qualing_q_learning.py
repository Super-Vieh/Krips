import os

import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


def select_device() -> T.device:
    if T.cuda.is_available():
        return T.device("cuda:0")
    if hasattr(T, "xpu") and T.xpu.is_available():
        return T.device("xpu")
    return T.device("cpu")


class DualingQNetwork(nn.Module):
    def __init__(self, learning_rate: float, savestate_file_name: str) -> None:
        super().__init__()
        self.savestate_dir: str = "Savestates"
        self.savestate_file: str = os.path.join(self.savestate_dir, savestate_file_name)
        self.learning_rate: float = learning_rate
        self.inputlayer: nn.Linear = nn.Linear(1144, 2000)
        self.linearlayer2: nn.Linear = nn.Linear(2000, 1000)
        self.linearlayer3: nn.Linear = nn.Linear(1000, 512)
        self.valuelayer0: nn.Linear = nn.Linear(512, 256)
        self.valuelayer1: nn.Linear = nn.Linear(256, 64)
        self.valueoutputlayer: nn.Linear = nn.Linear(64, 1)
        self.advantagelayer1: nn.Linear = nn.Linear(512, 256)
        self.advantageOutput1: nn.Linear = nn.Linear(256, 12)
        self.advantageOutput2: nn.Linear = nn.Linear(268, 21)

        self.optimizer: optim.Adam = optim.Adam(self.parameters(), lr=self.learning_rate)
        self.loss: nn.MSELoss = nn.MSELoss()
        self.device: T.device = select_device()
        self.to(self.device)

    def forward(self, states: T.Tensor) -> tuple[T.Tensor, T.Tensor, T.Tensor]:
        if states.dim() != 2:
            raise ValueError("Expected states with shape (N, 1144)")
        states = states.to(self.device)
        input: T.Tensor = F.relu(self.inputlayer(states))
        secondlayer: T.Tensor = F.relu(self.linearlayer2(input))
        thirdlayer: T.Tensor = F.relu(self.linearlayer3(secondlayer))

        valueinput1: T.Tensor = F.relu(self.valuelayer0(thirdlayer))
        valueinput2: T.Tensor = F.relu(self.valuelayer1(valueinput1))
        valueoutput: T.Tensor = self.valueoutputlayer(valueinput2)

        advantageinput1: T.Tensor = F.relu(self.advantagelayer1(thirdlayer))
        avantage1: T.Tensor = self.advantageOutput1(advantageinput1)
        advantageinput2: T.Tensor = T.cat((avantage1, advantageinput1), dim=1)
        avantage2: T.Tensor = self.advantageOutput2(advantageinput2)

        return valueoutput, avantage1, avantage2

    def combine_value_advantage(
        self,
        value: T.Tensor,
        advantage1: T.Tensor,
        advantage2: T.Tensor,
    ) -> T.Tensor:
        adv1: T.Tensor = advantage1.unsqueeze(2)
        adv2: T.Tensor = advantage2.unsqueeze(1)
        pair_mean: T.Tensor = (adv1 + adv2) / 2
        overall_mean: T.Tensor = pair_mean.mean(dim=(1, 2), keepdim=True)
        q_values: T.Tensor = value.unsqueeze(2) + pair_mean - overall_mean
        return q_values

    def q_values(self, states: T.Tensor) -> T.Tensor:
        value, advantage1, advantage2 = self.forward(states)
        return self.combine_value_advantage(value, advantage1, advantage2)

    def save_savestate(self) -> None:
        T.save(self.state_dict(), self.savestate_file)

    def load_savestate(self, map_location=None) -> None:
        self.load_state_dict(T.load(self.savestate_file, map_location=map_location))
