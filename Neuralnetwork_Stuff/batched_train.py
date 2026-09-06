"""Batched DQN-Trainingsschritt: B Spiele -> EIN forward/backward/Adam.

Kernidee (aus der Analyse): Der Kostenfaktor war das Netz-Compute (forward/backward/
Adam) pro Schritt. Statt 100 einzelner Forwards wird hier ein Batch (B,2288) in
einem Durchlauf verarbeitet -> die Kernel-Launches werden amortisiert.
Die Spiel-Logik/Encoding bleiben CPU (billig), das Netz läuft auf device (cpu/xpu/cuda).
"""
import torch as T

from Neuralnetwork_Stuff.qualing_q_learning import DualingQNetwork

# Aktions-Grammatik (identisch zu agent.py)
DICT_ACTION1 = {0:"K0",1:"S1",2:"S2",3:"S3",4:"S4",5:"S5",6:"S6",7:"S7",8:"S8",9:"A0",10:"A1",11:"A2"}
DICT_ACTION2 = {0:"K0",1:"S1",2:"S2",3:"S3",4:"S4",5:"S5",6:"S6",7:"S7",8:"S8",
                9:"M1",10:"M2",11:"M3",12:"M4",13:"M5",14:"M6",15:"M7",16:"M8",
                17:"A0",18:"A1",19:"A2",20:"G0"}


def q_grid(net: DualingQNetwork, states: T.Tensor) -> T.Tensor:
    """states (B,2288) -> Q-Grid (B,12,21)."""
    v, a1, a2 = net(states)
    return net.combine_value_advantage(v, a1, a2)


def best_actions(q: T.Tensor) -> T.Tensor:
    """q (B,12,21) -> (B,) beste flache Aktions-Indizes (s*21+t)."""
    return q.reshape(q.shape[0], -1).argmax(1)


def decode_index(idx: int) -> str:
    """Flacher Index (0..251) -> Zug-String (z.B. 'A0M1')."""
    s, t = idx // 21, idx % 21
    return DICT_ACTION1[s] + DICT_ACTION2[t]


def batched_update(net, optimizer, states, act_idx, rewards, next_states,
                   gamma: float = 0.9, device: str = 'cpu'):
    """Ein batched DQN-Schritt über B Spiele.

    states/next_states: (B,2288); act_idx: (B,) flache Aktion; rewards: (B,).
    loss = ((r + gamma*max Q(s') - Q(s,a))^2).mean() ; dann backward + optimizer.step.
    """
    states = states.to(device)
    next_states = next_states.to(device)
    rewards = rewards.to(device)
    B = states.shape[0]

    q = q_grid(net, states)                              # (B,12,21)
    qa = q.reshape(B, -1)[T.arange(B, device=device), act_idx.to(device)]  # (B,)
    q_next = q_grid(net, next_states).reshape(B, -1).max(1).values         # (B,)
    target = rewards + gamma * q_next
    loss = ((target - qa) ** 2).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss
