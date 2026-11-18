import os
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class DualingQNetwork(nn.Module):
    def __init__(self, learning_rate: float, savestate_file_name: str):
        super().__init__()
        self.savestate_dir: str = 'Savestates'
        self.savestate_file: str = os.path.join(self.savestate_dir, savestate_file_name)
        self.learning_rate: float = learning_rate
        #self.states:T.Tensor = None
        self.inputlayer: nn.Linear = nn.Linear(1144,2000)
        self.linearlayer2: nn.Linear = nn.Linear(2000,1000)
        self.linearlayer3: nn.Linear = nn.Linear(1000,512)
        self.valuelayer0: nn.Linear = nn.Linear(512,256)
        self.valuelayer1: nn.Linear = nn.Linear(256,64)
        self.valueoutputlayer: nn.Linear = nn.Linear(64,1)
        self.advantagelayer1: nn.Linear = nn.Linear(512,256)
        self.advantageoutputlayer: nn.Linear = nn.Linear(256, 184)

        self.optimizer: optim.Adam = optim.Adam(self.parameters(), lr=self.learning_rate)
        self.loss: nn.MSELoss = nn.MSELoss()
        self.device: T.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)




    def forward(self, states: T.Tensor) -> tuple[T.Tensor, T.Tensor]:

        states = states.to(self.device)
        #here are the first 3 layers
        # die inputdaten(states(als tensor)) werden in die erste lineare schicht gegeben und die ergebnisse der gewichtug wird gespeichert
        input: T.Tensor = self.inputlayer(states)
        input = F.relu(input) # das ergebniss der gewichte wird durch die relu funktion gegeben und gespeichert.
        secondlayer: T.Tensor = self.linearlayer2(input)
        secondlayer = F.relu(secondlayer)
        thirdlayer: T.Tensor = self.linearlayer3(secondlayer)
        thirdlayer = F.relu(thirdlayer)
        #here is the dualing part
        # the value stream
        valueinput1: T.Tensor = self.valuelayer0(thirdlayer)
        valueinput1 = F.relu(valueinput1)
        valueinput2: T.Tensor = self.valuelayer1(valueinput1)
        valueinput2 = F.relu(valueinput2)

        # no activation fuction for the output
        valueoutput: T.Tensor = self.valueoutputlayer(valueinput2)


        # the advantage stream
        advantageinput1: T.Tensor = self.advantagelayer1(thirdlayer)
        advantageinput1 = F.relu(advantageinput1)

        # no activation fuction for the output
        advantageoutput: T.Tensor = self.advantageoutputlayer(advantageinput1)

        return valueoutput, advantageoutput



    def combine_value_advantage(self, value: T.Tensor, advantage: T.Tensor) -> T.Tensor:
        # the q_values are the standart value v(s) and the advantage of an action (a)
        # the advantage is calculated by how good the pair values are compared to the average values
        # and the value is the value of the state so it is always present
        q_values: T.Tensor = value + advantage - advantage.mean(dim=-1, keepdim=True)
        # P.S. this is a heavily simplified version done by a LLM.
        # my version was python algorith based and not tensor based thus extremly slow the idea was the same though
        return q_values




    # i have to get back to this and unterstand how to save the model
    def save_savestate(self) -> None:
        print('... saving model ...')
        T.save(self.state_dict(), self.savestate_file)

    def load_savestate(self) -> None:
        print('... loading model ...')
        self.load_state_dict(T.load(self.savestate_file))