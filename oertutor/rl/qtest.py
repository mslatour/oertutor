import random
from oertutor.rl.learners import QLearner

# Constants mapping action names to numeric representations
RIGHT = 0x0
LEFT = 0x1
TOP = 0x2
DOWN = 0x3

class World(object):
    def __init__(self, start_state, transitions, rewards):
        """ Initialization of the true world
        start_state - The state in which the world begins.
                      The value can be any hashable value
        transitions - The true transition function from state and action to a 
                      probability distribution of new states.
                      The value can either be a function or dictionary
        rewards     - The true rewards function from state, action and the
                      new state to a reward.
                      The value can either be a function or dictionary
        """
        self.state = start_state
        if isinstance(transitions, dict):
            self.T = lambda s, a: transitions[s][a]
        else:
            self.T = transitions

        if isinstance(rewards, dict):
            self.R = lambda s, a, s2: rewards[s][a][s2]
        else:
            self.R = rewards

    def interact(self, action):
        state = self.state
        new_state = self._select_from_distribution( self.T(state,action) )
        reward = self.R(state, action, new_state)
        self.state = new_state
        return ( new_state, reward )

        
    def _select_from_distribution(self, distribution):
        thresh = random.random()
        surface = 0
        for event in distribution:
            surface += distribution[event]
            if surface >= thresh:
                return event
        

class Grid2DWorld(World):
    def __init__(self, start, dim, noise, reward_spots, default_reward=0):
        super(Grid2DWorld, self).__init__(start, self.transitions, self.rewards)
        self.xdim = dim[0]
        self.ydim = dim[1]
        self.reward_spots = reward_spots
        self.default_reward = default_reward
        self.noise = noise

    def rewards(self, state, action, new_state):
        if new_state in self.reward_spots:
            return self.reward_spots[new_state]
        else:
            return self.default_reward

    def transitions(self, state, action):
        T = {}
        if action == RIGHT:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[( (state[0]-1) % self.xdim, state[1])] = self.noise/4.0
            T[( state[0], (state[1]+1) % self.ydim )] = self.noise/4.0
            T[( state[0], (state[1]-1) % self.ydim )] = self.noise/4.0
            # set probability to go in the right direction
            T[( (state[0]+1) % self.xdim, state[1])] = 1.0-self.noise
        elif action == LEFT:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[( (state[0]+1) % self.xdim, state[1])] = self.noise/4.0
            T[( state[0], (state[1]+1) % self.ydim )] = self.noise/4.0
            T[( state[0], (state[1]-1) % self.ydim )] = self.noise/4.0
            # set probability to go in the right direction
            T[( (state[0]-1) % self.xdim, state[1])] = 1.0-self.noise
        elif action == TOP:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[( (state[0]+1) % self.xdim, state[1])] = self.noise/4.0
            T[( (state[0]-1) % self.xdim, state[1])] = self.noise/4.0
            T[( state[0], (state[1]-1) % self.ydim )] = self.noise/4.0
            # set probability to go in the right direction
            T[( state[0], (state[1]+1) % self.ydim )] = 1.0-self.noise
        elif action == DOWN:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[( (state[0]+1) % self.xdim, state[1])] = self.noise/4.0
            T[( (state[0]-1) % self.xdim, state[1])] = self.noise/4.0
            T[( state[0], (state[1]+1) % self.ydim )] = self.noise/4.0
            # set probability to go in the right direction
            T[( state[0], (state[1]-1) % self.ydim )] = 1.0-self.noise
        return T

gridworld = Grid2DWorld((0,0), (4,4), 0, {(0,3):10,(3,0):-10,(3,3):-10})
learner = QLearner(0.8,0.8)
learner.enter_world(gridworld, [RIGHT, LEFT, TOP, DOWN], (0,0))
print learner.history
