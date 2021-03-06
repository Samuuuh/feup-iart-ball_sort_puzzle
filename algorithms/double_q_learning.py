# -- Imports -- #

import gym
import numpy as np
import random

# -- Personal Libraries -- #

from algorithms import Algorithm
from utils import Logger


class DoubleQLearning(Algorithm):
    """
    A class to use to run the Double-Q_learning algorithm

    Attributes
    ----------
    env: Environment
        - OpenAI Gym environment

    data: list of parameters
        - list containing the necessary parameters for the class

    algorithmType: Algorithm
        - Chosen algorithm

    render: Render
        - OpenAI Gym environment rendering

    verbose: bool
        - Boolean value used for printing the values obtained in the algorithm
    
    logger: Logger
        - logger class for printing the values obtained from the algorithm
    
    q_table: List of lists of doubles
        - Q-table containing the values fo the actions of the Q-learning algorithm

    rewards_all_episodes: List of int
        - list containing the rewards values from all episodes

    """
    def __init__(self, env, data, algorithmType, render, verbose):
        """
        Constructor method for initialzing the Double-Q-Learning algorithm
        """
        super().__init__(env, data, algorithmType, render, verbose)
        
        self.logger = Logger("DoubleQLearning")

        # Set the action and state spaces
        action_space_size = self.env.action_space.n
        state_space_size = self.env.observation_space.n

        # Create Q-table
        self.q_table_one = np.zeros((state_space_size, action_space_size))
        self.q_table_two = np.zeros((state_space_size, action_space_size))

        # List of rewards
        self.rewards_all_episodes = []


    def finishLog(self):
        """
        Closes the logger from printing more values
        """
        return self.logger.closeLogs()

    def run(self):
        """
        Method for running the Double-Q-Learning algorithm
        """

        # Double Q-Learning algorithm
        for episode in range(self.num_episodes):
            if self.verbose: Logger.newEpisode(episode)

            # Reset the environment
            done = False
            state = self.env.reset()
            rewards_current_episode = 0
            
            for step in range(self.max_steps_per_episode):
                if self.render: self.env.render()

                # Get a move
                validMoves = self.env.game.getValid()
                exploration_rate_threshold = random.uniform(0, 1)

                # Choose the best action
                if exploration_rate_threshold > self.exploration_rate:
                    q_table = self.q_table_one[state,:] + self.q_table_two[state,:]
                    action = self.env.argMax(validMoves, q_table)
                else:
                    action = self.env.validSample(validMoves)

                # Take the action and observe the outcome state and reward
                new_state, reward, done, info = self.env.step(action)

                # Coose one qTable and Update
                p = np.random.random()
                if (p < 0.5):
                    # Update 1
                    self.q_table_one[state, action] =  self.q_table_one[state, action] + \
                        self.learning_rate * (reward + self.discount_rate * np.max(self.q_table_two[new_state, :]) - \
                        self.q_table_one[state, action])
                else:
                    # Update 2
                    self.q_table_two[state, action] =  self.q_table_two[state, action] + \
                        self.learning_rate * (reward + self.discount_rate * np.max(self.q_table_one[new_state, :]) - \
                        self.q_table_two[state, action])
                
                state = new_state
                rewards_current_episode += reward
                
                if done: 
                    if self.verbose: 
                        Logger.finishStep(step)
                        self.env.render()
                    break
                    
            # Exploration rate decay
            # Reduce exploration rate (epsilon), because we need less and less exploration
            self.exploration_rate = self.min_exploration_rate + \
                (self.max_exploration_rate - self.min_exploration_rate) * np.exp(-self.exploration_decay_rate * episode)
            
            self.rewards_all_episodes.append(rewards_current_episode)
            
            if self.render: self.env.render()
            self.logger.writeLog(episode, rewards_current_episode)
            
        # Calculate and print the average reward per 10 episodes
        rewards_per_thousand_episodes = np.split(np.array(self.rewards_all_episodes), self.num_episodes / 100)

        count = 100
        for r in rewards_per_thousand_episodes:
            self.logger.writeAvgRewards(count, r)
            if self.verbose: Logger.printAvgRewards(count, r)
            count += 100

        if self.verbose: Logger.finish(self.rewards_all_episodes, self.num_episodes, self.exploration_rate)