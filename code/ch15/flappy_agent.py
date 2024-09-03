import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import random
import numpy as np
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, lr, gamma,input_dim, hidden_dim, output_dim):
        self.gamma = gamma
        self.hidden_size = hidden_dim
        self.model = Linear_QNet(input_dim, self.hidden_size, output_dim)
        self.target_model = Linear_QNet(input_dim, self.hidden_size,output_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.SmoothL1Loss()
        self.copy_model()

    def copy_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        action = torch.unsqueeze(action, -1)
        reward = torch.tensor(reward, dtype=torch.float)
        done = torch.tensor(done, dtype=torch.long)

        Q_value = self.model(state).gather(-1, action).squeeze()
        Q_value_next = self.target_model(next_state).detach().max(-1)[0]
        target =  (reward + self.gamma * Q_value_next * (1 - done)).squeeze()

        self.optimizer.zero_grad()
        loss = self.criterion(Q_value,target)
        loss.backward()
        self.optimizer.step()

class Agent:
    def __init__(self,nS,nA,max_explore=100, gamma = 0.9,
                max_memory=5000, lr=0.001, hidden_dim=128):
        self.max_explore = max_explore 
        self.memory = deque(maxlen=max_memory) 
        self.nS = nS
        self.nA = nA
        self.n_game = 0
        self.trainer = QTrainer(lr, gamma, self.nS, hidden_dim, self.nA)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) 

    def train_long_memory(self,batch_size):
        if len(self.memory) > batch_size:
            mini_sample = random.sample(self.memory, batch_size) # list of tuples
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        states = np.array(states)
        next_states = np.array(next_states)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state, n_game, explore=True):
        state = torch.tensor(state, dtype=torch.float)
        prediction = self.trainer.model(state).detach().numpy().squeeze()
        epsilon = self.max_explore - n_game
        if explore and random.randint(0, self.max_explore) < epsilon:
            prob = np.exp(prediction)/np.exp(prediction).sum()
            final_move = np.random.choice(len(prob), p=prob)
        else:
            final_move = prediction.argmax()
        return final_move