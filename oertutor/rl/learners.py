from django.db.models import Max, Sum
from django.db import connection
from oertutor.rl.models import QValue
from concurrency.exceptions import RecordModifiedError
from django.core.exceptions import ObjectDoesNotExist
from time import sleep
import random

class QLearner:
    DEFAULT_POLICY = "max" # Options are [random, max]
    history = []
    label = ""
    
    def __init__(self, learning_rate, discount, epsilon):
        self.alpha = learning_rate
        self.gamma = discount
        self.epsilon = epsilon

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
                                                    state_desc=state, \
                                                    action=action, \
                                                    label=self.label, \
                                                    defaults={'value':0.0})
        return (obj, created)

    def state_confidence(self, state):
        try:
            obj = QValue.objects.values('state','label').annotate(belief=Sum('version')).\
                    get(state=hash(state), label=self.label)
            belief = obj["belief"]
        except ObjectDoesNotExist:
            belief = 0
        return belief

    
    def max_q_s_a(self, state):
        # Find the argmax_a[Q(s,a)] given the state
        try:
            obj = QValue.objects.filter(state=hash(state), label=self.label)\
                    .order_by('-value')[0]
        except IndexError:
            obj = None
        return obj

    def update(self, state, action, reward, new_state):
        # est_v is short for estimated value [in s']
        #   current implemented as max_a[ Q(s',a) ]
        max_qsa = self.max_q_s_a(new_state)
        est_v = max_qsa.value if max_qsa is not None else 0.0

        # The following loop is necessary for dealing with potential
        #  concurrency issues that can occur when multiple agents
        #  are updating the Q table at the same time.
        saved = False
        while not saved:
            # Fetch the QValue q we are going to update
            q, created = self.q(state, action)
            
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
        if self.epsilon is None:
            N = self.state_confidence(self.state)
            epsilon = 1.0/((N/100.0)+1)
        else:
            epsilon = self.epsilon

        if self.DEFAULT_POLICY == "max":
            if random.random() < epsilon:
                self.action = random.choice(self.actions)
            else:
                max_qsa = self.max_q_s_a(self.state)
                if max_qsa is not None:
                    self.action = max_qsa.action
                else:
                    self.action = random.choice(self.actions)
        elif self.DEFAULT_POLICY == "random":
            self.action = random.choice(self.actions)
        return self.action

    def observe(self, new_state, reward):
        state,action = self.history[-1]
        self.update(state, action, reward, new_state)
        self.state = new_state
