from oertutor.ga.models import *
from oertutor.ga import algorithm as galg
from oertutor.ga.settings import *
from oertutor.ga import signals

def init_population(population, genes):
    galg.init_population(NUM_POP, population, genes)

def request_sequence(population):
    generation = population.current_generation()
    # Determine number of stored evaluations:
    eval_count = Evaluation.objects.filter(generation=generation).count()
    # If not enough evaluations have been stored
    if eval_count < NUM_EPISODES:
        try:
            individual = generation.select_next_individual()
        except ImpossibleException:
            # State: only locked options left, take into account the possibility
            # that the expected evaluations are not coming anymore.
            Individual.release_oldest_lock()
            return request_sequence(population)
        else:
            return individual
    else:
        # State: Enough evaluations performed for this generation
        galg.switch_generations(NUM_POP, NUM_ELITE, P_MUTATE, population)
        return request_sequence(population)

def store_evaluation(individual, population, evaluation):
    return Evaluation.factory(population.current_generation(),
        individual, evaluation)
