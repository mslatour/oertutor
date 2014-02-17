from oertutor.ga.models import *
from oertutor.ga.algorithm import *

MAX_EPISODES = 10;

class State:
    """
    Store state information of the current user.
    """
    pass

def request_sequence(population_id):
    population = Population.objects.get(pk=population_id)
    generation = population.current_generation()
    # Determine number of stored evaluations:
    eval_count = Evaluation.objects.filter(generation=generation).count()
    # If not enough evaluations have been stored
    if eval_count < MAX_EPISODES:
        # Try to select the next (available) individual
        try:
            return generation.select_next_individual()
        except ImpossibleException:
            # State: only locked options left, take into account the possibility
            # that the expected evaluations are not coming anymore.
            # Solution: Release oldest lock
            Individual.release_oldest_lock()
            return request_sequence(population)
    else:
        # State: Enough evaluations performed for this generation
        # Solution: Move to next generation
        # TODO: Find a way to prevent multiple users triggering this
        switch_generations(NUM_POP, NUM_ELITE, P_MUTATE, population)
        return request_sequence(population)

def store_evaluation(sequence_id, generation_id, evaluation):
    individual = Individual.objects.get(pk=sequence_id)
    generation = Generation.objects.get(pk=generation_id)
    Evaluation.factory(generation, individual, evaluation)
