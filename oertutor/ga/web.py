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
            if attempt_bootstrap(individual, population):
                return request_sequence(population)
            else:
                return individual
    else:
        # State: Enough evaluations performed for this generation
        galg.switch_generations(NUM_POP, NUM_ELITE, P_MUTATE, population)
        return request_sequence(population)

def attempt_bootstrap(individual, population):
    # Calculate chromosome hash
    chromosome = str([int(g.pk) for g in individual.chromosome.genes.all()])
    bootstraps = BootstrapEvaluation.objects.order_by('pk').filter(
        chromosome=chromosome, population=population, used=False)
    if len(bootstraps) == 0:
        return False
    else:
        bootstrap = bootstraps[0]
        signals.ga_bootstrap_evaluation.send(
                sender=population,
                generation=population.current_generation(),
                individual=individual,
                bootstrap=bootstrap)
        store_evaluation(individual, population, bootstrap.value)
        bootstrap.used = True
        bootstrap.save()
        return True

def store_evaluation(individual, population, evaluation):
    Evaluation.factory(population.current_generation(), individual, evaluation)
