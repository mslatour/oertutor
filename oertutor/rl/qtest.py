import random
import time
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
        go_right = lambda s: ((s[0]+1) % self.xdim, s[1])
        go_left = lambda s: ((s[0]-1) % self.xdim, s[1])
        go_up = lambda s: (s[0], (s[1]+1) % self.ydim)
        go_down = lambda s: (s[0], (s[1]-1) % self.ydim)
        if action == RIGHT:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[go_left(state)] = self.noise/4.0
            T[go_up(state)] = self.noise/4.0
            T[go_down(state)] = self.noise/4.0
            # set probability to go in the right direction
            T[go_right(state)] = 1.0-self.noise
        elif action == LEFT:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[go_right(state)] = self.noise/4.0
            T[go_up(state)] = self.noise/4.0
            T[go_down(state)] = self.noise/4.0
            # set probability to go in the right direction
            T[go_left(state)] = 1.0-self.noise
        elif action == TOP:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[go_right(state)] = self.noise/4.0
            T[go_left(state)] = self.noise/4.0
            T[go_down(state)] = self.noise/4.0
            # set probability to go in the right direction
            T[go_up(state)] = 1.0-self.noise
        elif action == DOWN:
            # set probability to stay in the same location
            T[state] = self.noise/4.0
            # set probability to go in the wrong direction
            T[go_right(state)] = self.noise/4.0
            T[go_left(state)] = self.noise/4.0
            T[go_up(state)] = self.noise/4.0
            # set probability to go in the right direction
            T[go_down(state)] = 1.0-self.noise
        return T

    def pp_learned(self, learner):
        actions = [u'\u2192',u'\u2190',u'\u2191',u'\u2193']
        cell = 5
        pp = ""
        for y in range(self.ydim-1,-1,-1):
            line = []
            for x in range(self.xdim):
                if (x,y) in self.reward_spots:
                    line.append(str(self.reward_spots[(x,y)]).center(cell))
                else:
                    max_qsa = learner.max_q_s_a((x,y))
                    if max_qsa is None:
                        line.append("?".center(cell))
                    else:
                        line.append(actions[max_qsa.action].center(cell))
            line = "| %s |" % " | ".join(line)
            pp += line + "\n"
            pp += "-"*len(line) + "\n"
        print "-"*len(line)
        print pp

def test(uncertainty, epsilon):
    gridworld = Grid2DWorld((0,0), (5,5), uncertainty, \
            {(4,4):10})
    learner = QLearner(0.8,0.8,epsilon)
    if epsilon is not None:
        print "Uncertainty: %f, Epsilon: %f" % (uncertainty,epsilon)
        learner.label = "%f,%f,(5,5)" % (uncertainty, epsilon)
    else:
        print "Uncertainty: %f, Epsilon: auto" % (uncertainty,)
        learner.label = "%f,auto, (5,5)" % (uncertainty,)
    for i in range(100):
        learner.enter_world(gridworld, [RIGHT, LEFT, TOP, DOWN], (0,0))
        learner.history = []
        gridworld.state = (0,0)
    gridworld.pp_learned(learner)

for uncertainty in [0.0,0.2,0.4,0.6]:
    test(uncertainty, None);
    for epsilon in [0.1,0.2,0.4,0.6]:
        test(uncertainty, epsilon);
