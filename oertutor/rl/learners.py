from django.db.models import Max
from django.db import connection
from oertutor.rl.models import QValue
from concurrency.exceptions import RecordModifiedError
from time import sleep

class QLearner:
    def __init__(self, learning_rate, discount):
        self.alpha = learning_rate
        self.gamma = discount

    def q(self, state, action):
        # Return Q(s,a) if exists, otherwise create it with Q(s,a) = 0
        obj, created = QValue.objects.get_or_create(state=state, \
                                                    action=action, \
                                                    defaults={'value':0.0})
        return obj

    def get_max_q_value(self, state):
        # Find the maximum value given the state s, i.e. max_a[Q(s,a)]
        Qs = QValue.objects.filter(state__exact=state).annotate(Max('value'))
        if len(Qs) == 0:
            return 0
        else:
            return Qs[0].value__max

    def update(self, state, action, reward, state_prime):
        # est_v is short for estimated value [in s']
        #   current implemented as max_a[ Q(s',a) ]
        est_v = self.get_max_q_value(state_prime)

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
