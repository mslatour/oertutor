from oertutor.rl.models import QValue
from concurrency.exceptions import RecordModifiedError

class QLearner:
    def __init__(self, learning_rate, discount):
        self.alpha = learning_rate
        self.gamma = discount

    def q(self, state, action):
        return QValue.objects.get(state__exact=state, action__exact=action)
    
    def get_q_max_a(self, state):
        res = QValue.objects.filter(state__exact=state).aggregate(Max('value'))
        return res['value__max']

    def update(self, state, action, reward, state_prime):
        # est_v is short for estimated value [in s']
        #   current implemented as max_a[ Q(s',a) ]
        est_v = self.get_q_max_a(state_prime).value

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
                pass

