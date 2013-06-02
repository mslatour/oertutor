from django.db.models import Max
from django.db import connection
from oertutor.rl.models import QValue
from concurrency.exceptions import RecordModifiedError
from time import sleep
import random

class QLearner:
    history = []
    
    def __init__(self, learning_rate, discount):
        self.alpha = learning_rate
        self.gamma = discount

    def enter_world(self, world, actions, start_state):
        self.actions = actions
        
        # Set start state
        self.state = start_state
        
        # Continue to take actions in the world untill a reward is received
        reward = 0
        while reward == 0:
            # Get action according to policy
            action = self.policy()
            # Store state,action in history
            self.history.append((self.state, action))
            # Interact with the world
            new_state, reward = world.interact(action)
            # Process the observed state and reward
            self.observe(new_state, reward)

    def q(self, state, action):
        # Return Q(s,a) if exists, otherwise create it with Q(s,a) = 0
        obj, created = QValue.objects.get_or_create(state=hash(state), \
                                                    action=action, \
                                                    defaults={'value':0.0})
        return obj

    def get_max_q_value(self, state):
        # Find the maximum value given the state s, i.e. max_a[Q(s,a)]
        Qs = QValue.objects.filter(state__exact=hash(state)).\
                annotate(Max('value'))
        if len(Qs) == 0:
            return 0
        else:
            return Qs[0].value__max

    def update(self, state, action, reward, new_state):
        # est_v is short for estimated value [in s']
        #   current implemented as max_a[ Q(s',a) ]
        est_v = self.get_max_q_value(new_state)

        # The following loop is necessary for dealing with potential
        #  concurrency issues that can occur when multiple agents
        #  are updating the Q table at the same time.
        saved = False
        while not saved:
            # Fetch the QValue q we are going to update
            q = self.q(state, action)
            
            # Update Q(s,a)
            q.value = self.alpha * \
                    ( reward + self.gamma * est_v - q.value )
            try:
                q.save()
                saved = True
            except RecordModifiedError:
                # Do hard rollback and try again
                cursor = connection.cursor()
                cursor.execute("ROLLBACK")
                del q

    def policy(self):
        self.action = random.choice(self.actions)
        return self.action

    def observe(self, new_state, reward):
        state,action = self.history[-1]
        self.update(state, action, reward, new_state)
        self.state = new_state
