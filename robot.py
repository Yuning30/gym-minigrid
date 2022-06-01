import copy
import torch
import numpy as np
import gym_minigrid
import gym
from dsl import *


class NegativeReward(Exception):
    pass

# single karel robot
class MiniGridRobot:
    def __init__(self, task, seed=999, max_steps=100):
        
        self.task = task
        self.seed = seed
        self.max_steps = max_steps
        self.steps = 0

        self.env = gym.make(self.task)

        self.reward = 0

    def update_reward(self, reward_in):
        self.reward += reward_in
    
    def make_step(self):
        self.steps += 1
    
    def no_fuel(self):
        return self.max_steps < self.steps
    