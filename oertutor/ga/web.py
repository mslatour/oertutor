from oertutor.ga.models import *
from oertutor.ga import algorithm as galg

MAX_EPISODES = 4;
NUM_POP = 4;
NUM_ELITE = 2;
P_MUTATE = 0.05;

def init_population(population, genes):
    galg.init_population(NUM_POP, population, genes)

def request_sequence(population):
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
        galg.switch_generations(NUM_POP, NUM_ELITE, P_MUTATE, population)
        return request_sequence(population)

def store_evaluation(individual, population, evaluation):
    Evaluation.factory(population.current_generation(), individual, evaluation)
