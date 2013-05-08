class Exercise:
    def __init__(self, student):
        self.student = student

    def render(self):
        raise NotImplementedError

    def input(self):
        raise NotImplementedError

class PedagogicalAction:
    def render(self):
        raise NotImplementedError

class RLExercise(Exercise):
    def __init__(self, student):
        super().__init__(self, student)

    def render(self):
        pass

    def state(self):
        raise NotImplementedError

class QLExcersie(RLExercise):
    def render(self):
        # look-up argmax_a Q(s,a)


class NimExercise(RLExercise):
    def __init__(self, student):
        super().__init__(self, student)

    def state(self):

