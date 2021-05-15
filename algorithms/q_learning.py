import gym
import random
import numpy as np
import csv

import time

from utils.logger import Logger
    
class QLearning:
    def __init__(self, env, data):
        self.env = env
        self.render = False
        self.logger = Logger("QLearning")
        # Set the action and state spaces
        self.dicta, self.dicti = self.env.game.actions
        action_space_size = len(self.dicta)
        state_space_size = self.env.observation_space.n

        # Create Q-table
        self.q_table = np.zeros((state_space_size, action_space_size))

        # Set hyperparameters for Q-learning
        # Defining the different parameters
        self.num_episodes = data['num_episodes']
        self.max_steps_per_episode = data['max_steps_per_episode']

        self.learning_rate = data['learning_rate'] # Alpha
        self.discount_rate = data['discount_rate'] # Gamma

        self.exploration_rate = data['exploration_rate']  # Epsilon
        self.max_exploration_rate = data['max_exploration_rate'] # Max Epsilon
        self.min_exploration_rate = data['min_exploration_rate'] # Min Epsilon
        self.exploration_decay_rate = data['exploration_decay_rate'] # Decay Rate

        # List of rewards
        self.rewards_all_episodes = []

    def run(self):
        # Q-Learning algorithm
        for episode in range(self.num_episodes):
            print("-> EPISODE {} <-".format(episode))

            # Reset the environment
            state = self.env.reset()
            done = False
            rewards_current_episode = 0
            
            start_time = time.time()
            for step in range(self.max_steps_per_episode):
                # Visualizing the training
                if self.render: self.env.render()


                exploration_rate_threshold = random.uniform(0,1)
                if exploration_rate_threshold > self.exploration_rate: 
                    action = np.argmax(self.q_table[state,:])
                else:
                    action = self.env.action_space.sample()
                
                # Take the action and observe the outcome state and reward
                new_state, reward, done, info = self.env.step(action)

                # Update Q-table for Q(s,a)
                # Q(s,a):= Q(s,a) + lr [R(s,a) + gamma * max Q(s',a') - Q(s,a)]
                # qtable[new_state,:] : all the actions we can take from new state
                self.q_table[state, action] = self.q_table[state, action] + \
                    self.learning_rate * (reward + self.discount_rate * np.max(self.q_table[new_state, :]) - self.q_table[state, action])
                
                # Our new state is state
                state = new_state
                rewards_current_episode += reward
                
                # If done : finish episode
                if done == True: 
                    print("Found Solution")
                    if render: self.env.render()
                    break
                    
            # Exploration rate decay
            # Reduce exploration rate (epsilon), because we need less and less exploration
            self.exploration_rate = self.min_exploration_rate + \
                (self.max_exploration_rate - self.min_exploration_rate) * np.exp(-self.exploration_decay_rate * episode)
            
            self.rewards_all_episodes.append(rewards_current_episode)
            end_time = time.time()
            elapsed = end_time - start_time
            self.logger.writeLog(episode, rewards_current_episode)
            
        # Calculate and print the average reward per 10 episodes
        rewards_per_thousand_episodes = np.split(np.array(self.rewards_all_episodes), self.num_episodes / 100)
        count = 100

        for r in rewards_per_thousand_episodes:
            self.logger.writeAvgRewards(count, r)
            count += 100
            
        # Print updated Q-table
        # Save Q-Table
        # np.savetxt('2darray.csv', self.q_table, delimiter=',', fmt='%d')

        print("Performace: " +  str(sum(self.rewards_all_episodes)/self.num_episodes))
        print("Exploration Rate: ", self.exploration_rate)