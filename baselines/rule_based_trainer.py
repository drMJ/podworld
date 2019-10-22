from podworld.envs import PodWorldEnv
from rl_loop import run_episode
from base_agent import BaseAgent 

import numpy as np
import math
from scipy.special import softmax

class RuleBasedAgent(BaseAgent):
    obj_rank = {
            PodWorldEnv.OBS_COLOR: -40.0,
            PodWorldEnv.AVAIL_FOOD_COLOR: 20.0,
            PodWorldEnv.NOOBJ_COLOR: 1.0
    }
    gamma = 0.9

    def reset(self, env):
        self.pixel_count = env.observation_space.shape[1]
        self.action_count = env.action_space.n
        self.pix2act = (self.action_count-1.0)/self.pixel_count

        self.weights = np.array([
            math.pow(RuleBasedAgent.gamma, 
                i-self.pixel_count if i >= self.pixel_count/2 else -i) \
                    for i in range(self.pixel_count)])

    def act(self, observation, reward, done):
        colors = observation[0,:]
        obj_ranks = [RuleBasedAgent.obj_rank.get(tuple(t), -2.0) for t in colors]
        obj_ranks_conv = np.array([np.roll(self.weights, shift=i).dot(obj_ranks) \
            for i in range(len(obj_ranks))])
        obj_ranks_conv_normed = obj_ranks_conv * 100.0 / (np.linalg.norm(obj_ranks_conv) + 1e-16)
        probabilities = softmax(-obj_ranks_conv_normed)
        goal_direction = np.random.choice(len(probabilities), p=probabilities)
        thrust_direction = goal_direction #(self.pixel_count/2 + goal_direction) % self.pixel_count
        action_val = int(self.pix2act * thrust_direction) + 1
        return action_val

env = PodWorldEnv(max_steps=10000, obs_mode='RGBA')
agent = RuleBasedAgent()

run_episode(env, agent, render=True)