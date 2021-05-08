import gym
import random
import numpy as np
import itertools

NUM_BOTTLES = 2

def keyActionsDics():
    l = list(itertools.product(list(range(0, NUM_BOTTLES)), repeat=2))
    # l =  list(itertools.permutations(list(range(0, nBottles)), 2))
    return dict(zip(range(len(l)),l)), dict(zip(l, range(len(l))))

def run():
    env = gym.make("gym_basic:basic-v0")

    dicta, dicti = keyActionsDics()

    action_space_size = len(dicta)
    state_space_size = env.observation_space.n

    q_table = np.zeros((state_space_size, action_space_size))

    num_episodes = 1000
    max_steps_per_episode = 10 # but it won't go higher than 1

    learning_rate = 0.1
    discount_rate = 0.99

    exploration_rate = 1
    max_exploration_rate = 1
    min_exploration_rate = 0.01

    exploration_decay_rate = 0.01 #if we decrease it, will learn slower

    rewards_all_episodes = []

    # Q-Learning algorithm
    for episode in range(num_episodes):
        print("********* EPISODE {} *********".format(episode))
        state = env.reset()
        
        done = False
        rewards_current_episode = 0
        
        for step in range(max_steps_per_episode):
            env.render()

            # Exploration -exploitation trade-off
            exploration_rate_threshold = random.uniform(0,1)
            if exploration_rate_threshold > exploration_rate: 
                action = np.argmax(q_table[state,:])
                action = dicta[action]
            else:
                action = env.action_space.sample()
            
            new_state, reward, done, info = env.step(action)
            action = dicti[action]

            # Update Q-table for Q(s,a)
            q_table[state, action] = (1 - learning_rate) * q_table[state, action] + \
                learning_rate * (reward + discount_rate * np.max(q_table[new_state,:]))
            
            state = new_state
            rewards_current_episode += reward
            
            if done == True: 
                print("Found Solution")
                env.render()
                break
                
        # Exploration rate decay
        exploration_rate = min_exploration_rate + \
            (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate * episode)
        
        rewards_all_episodes.append(rewards_current_episode)
        
    # Calculate and print the average reward per 10 episodes
    rewards_per_thousand_episodes = np.split(np.array(rewards_all_episodes), num_episodes / 100)
    count = 100
    print("********** Average  reward per thousand episodes **********\n")

    for r in rewards_per_thousand_episodes:
        print(count, ": ", str(sum(r / 100)))
        count += 100
        
    # Print updated Q-table
    print(dicta)
    print("\n\n********** Q-table **********\n")
    print(q_table)