from oertutor.ga.algorithm import init_population, mutate, crossover
from oertutor.ga.models import Gene, Chromosome, Generation, Population
from oertutor.ga.exceptions import ImpossibleException
from django.db.models import Avg
from copy import copy
from decimal import Decimal
from datetime import datetime
import random

DEBUG_PROG = 0x1
DEBUG_STEP = 0x2
DEBUG_VALUE = 0x4
DEBUG = DEBUG_PROG

def create_fitness_fn(chromosomes, noise):
    return lambda c: random.gauss(
            float(sum([1 if x.pk % 2 == 0 else 0 for x in list(c)]) \
                / Decimal(len(c))), noise)


def clear_pool():
    Population.objects.all().delete()
    Generation.objects.all().delete()
    Chromosome.objects.all().delete()
    Gene.objects.all().delete()

def debug(message, mode):
    if DEBUG & mode:
        print "[%s] %s" % (datetime.now(), message)

def simulate(num_pool, noise, num_pop, num_iter, p_mutate):
    debug("Start", DEBUG_PROG)
    clear_pool()
    pool = Gene.factory(num_pool)
    debug("Generated %d genes in the pool" % (num_pool,), DEBUG_VALUE)
    fitness_fn = create_fitness_fn(pool, noise)
    population = simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn)
    debug("Stop", DEBUG_PROG)
    return population

def export_data(population, output=None):
    if output is not None:
        f = open(output, "w")
    for index, generation in enumerate(population.generations.all()):
        best = generation.fitness(generation.select_best_chromosome())
        worst = generation.fitness(generation.select_worst_chromosome())
        avg = generation.chromosomes.aggregate(
                avg=Avg("generationmembership__fitness"))['avg']
        if output is None:
            print "%d %f %f %f" % (index, worst, avg, best)
        else:
            f.write("%d %f %f %f\n" % (index, worst, avg, best))

def simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn):
    # Init population
    population = init_population(num_pop)
    debug("Population initialized", DEBUG_STEP)
    # Fetch generation
    generation = population.current_generation()
    debug("Generation: %s" % ([x for x in generation.chromosomes.all()],),
            DEBUG_VALUE)
    simulate_evaluate_generation(generation, fitness_fn)
    debug("First generation evaluated", DEBUG_STEP)
    for i in range(num_iter-1):
        debug("Iteration %d" % (i+1,), DEBUG_PROG)
        # survivor selection
        survivors = [copy(x) for x in
                generation.select_by_fitness_pdf(num_pop/2)]
        debug("%d survivors: %s" % (len(survivors), survivors), DEBUG_VALUE)
        # new generation
        generation = population.next_generation(survivors)
        for _ in range(num_pop-(num_pop/2)):
            if random.random() < p_mutate:
                debug("Mutate", DEBUG_STEP)
                # mutation
                generation.add_chromosomes([
                        mutate(generation.select_by_fitness_pdf(1)[0])])
            else:
                debug("Recombine", DEBUG_STEP)
                # parent selection
                parents = generation.select_by_fitness_pdf(2)
                debug("Parents selected: %s" % (parents,), DEBUG_VALUE)
                try:
                    generation.add_chromosomes(
                        crossover(parents[0], parents[1]))
                except ImpossibleException:
                    generation.add_chromosomes([
                        mutate(generation.select_by_fitness_pdf(1)[0])])
        debug("Generation complete", DEBUG_STEP)
        debug([x for x in generation.chromosomes.all()], DEBUG_VALUE)
        # evaluation
        simulate_evaluate_generation(generation, fitness_fn)
        debug("Generation %d evaluated" % (i+1,), DEBUG_STEP)
    return population

def simulate_evaluate_generation(generation, fitness_fn):
    # Loop until all chromosomes are evaluated
    while True:
        try:
            chromosome = generation.select_next_chromosome()
        except ValueError:
            break
        else:
            try:
                # Attempt to lock chromosome
                generation.lock_chromosome(chromosome)
            except ValueError:
                # Chromosome is already locked, find a new one
                continue
            else:
                # Evaluate chromosome
                fitness = fitness_fn(chromosome)
                # Store fitness
                generation.fitness(chromosome, fitness)
                # Unlock chromosome
                generation.unlock_chromosome(chromosome)
