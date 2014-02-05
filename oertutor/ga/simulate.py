from oertutor.ga.models import Population, Generation, Individual, \
        Chromosome, Gene, Evaluation
from oertutor.ga.algorithm import init_population, switch_generations
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga.utils import debug, DEBUG_VALUE, DEBUG_STEP, DEBUG_PROG
from django.db.models import Avg, Min, Max
from decimal import Decimal
from difflib import SequenceMatcher
from pytz import timezone
from datetime import datetime
from math import factorial
import random

DEBUG = DEBUG_PROG | DEBUG_STEP
MIN_SOL_LEN = 3
MAX_SOL_LEN = 3
EPISODES_FACTOR = 2

def gen_solutions(num, pool, min_len=1, max_len=4):
    # Ensure that sequences are not longer than possible
    max_len = min(len(pool), max_len)
    solutions = []
    for _ in range(num):
        seq = []
        length = random.randint(min_len, max_len)
        for _ in range(length):
            gene = random.choice(pool)
            while gene in seq:
                gene = random.choice(pool)
            seq.append(gene)
        solutions.append(seq)
    return solutions

def create_fitness_fn(solutions, noise):
    return (lambda c:
        max(
            min(
                random.gauss(
                    max([SequenceMatcher(a=c,b=s).ratio() for s in solutions]),
                    noise),
                1
            ),
            0
        ))


def clear_pool():
    Evaluation.objects.all().delete()
    Generation.objects.all().delete()
    Population.objects.all().delete()
    Individual.objects.all().delete()
    Chromosome.objects.all().delete()
    Gene.objects.all().delete()

def simulate(num_pool, noise, num_pop, num_iter, p_mutate, debug_mode=DEBUG,
        export_dir=None):
    debug("Start", debug_mode & DEBUG_PROG)
    clear_pool()
    pool = Gene.factory(num_pool)
    debug("Generated %d genes in the pool" % (num_pool,),
            debug_mode & DEBUG_VALUE)
    solutions = gen_solutions(1, pool, MIN_SOL_LEN, MAX_SOL_LEN)
    debug("Generated solutions: %s" % (solutions,), debug_mode & DEBUG_PROG)
    fitness_fn = create_fitness_fn(solutions, noise)
    population = simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn,
            debug_mode)
    debug("Stop", debug_mode & DEBUG_PROG)
    if export_dir is not None:
        debug("Exporting fitness data", debug_mode & DEBUG_PROG)
        export_fitness_data(population,
                export_dir+"/fitness_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting fitness [all] data", debug_mode & DEBUG_PROG)
        export_fitness_all_data(population,
                export_dir+"/fitness_all_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting regret data", debug_mode & DEBUG_PROG)
        export_regret_data(population,
                export_dir+"/regret_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting coverage data", debug_mode & DEBUG_PROG)
        export_coverage_data(population, num_pool,
                export_dir+"/coverage_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting chromosome track data", debug_mode & DEBUG_PROG)
        export_chromosome_track_data(population,
                export_dir+"/chromosome_track_%s_%d_%f_%d_%d.dat" % (
                    datetime.now(
                        timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                        num_pool,
                        noise,
                        num_pop,
                        num_iter))
    debug("Done", debug_mode & DEBUG_PROG)
    return population

def export_regret_data(population, output=None):
    labels = ["evaluation", "regret"]
    if output is not None:
        out = open(output, "w")
        out.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    evaluations = Evaluation.objects.filter(population=population)
    for index, evaluation in enumerate(evaluations):
        if output is None:
            print "%d %f" % (index, 1-evaluation.value)
        else:
            out.write("%d %f\n" % (index, 1-evaluation.value))
    if output is not None:
        out.close()

def export_chromosome_track_data(population, output=None):
    if output is not None:
        out = open(output, "w")
    mapping = {}
    for index, generation in enumerate(population.generations.all()):
        for individual in generation.individuals.all():
            chromosome = individual.chromosome
            if tuple(chromosome) in mapping:
                mapping[tuple(chromosome)].append(
                 (index,generation.fitness(individual)))
            else:
                mapping[tuple(chromosome)] = [(index,
                    generation.fitness(individual))]
    items = sorted(mapping.items(), key=lambda x: len(x[1]), reverse=True)
    for item in items:
        if output is None:
            print "%s >> %s" % (item[0], item[1])
        else:
            out.write("%s >> %s\n" % (item[0], item[1]))
    if output is not None:
        out.close()
    return mapping

def export_coverage_data(population, num_pool, output=None):
    total = Decimal(sum([factorial(num_pool)/factorial(num_pool-l) for l in range(
        1, num_pool+1)]))
    labels = ["generation", "coverage"]
    if output is not None:
        out = open(output, "w")
        out.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    coverage = set([])
    for index, generation in enumerate(population.generations.all()):
        for individual in generation.individuals.all():
            coverage.add(tuple(individual.chromosome))
        if output is None:
            print "%d %f" % (index, Decimal(len(coverage))/total)
        else:
            out.write("%d %f\n" % (index, Decimal(len(coverage))/total))
    if output is not None:
        out.close()

def export_fitness_all_data(population, output=None):
    labels = ["generation"]+[str(i) for i in range(1,
        population.current_generation().individuals.count()+1)]
    if output is not None:
        out = open(output, "w")
        out.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    for index, generation in enumerate(population.generations.all()):
        values = [index]
        for individual in generation.individuals.order_by(
                '-generationmembership__fitness'):
            values.append(generation.fitness(individual))
        if output is None:
            print ("%d"+(" %f"*(len(values)-1))) % tuple(values)
        else:
            out.write(("%d"+(" %f"*(len(values)-1))+"\n") % tuple(values))
    if output is not None:
        out.close()

def export_fitness_data(population, output=None):
    labels = ["generation", "best", "average", "worst"]
    if output is not None:
        out = open(output, "w")
        out.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    for index, generation in enumerate(population.generations.all()):
        best = generation.individuals.aggregate(
                max=Max("generationmembership__fitness"))['max']
        worst = generation.individuals.aggregate(
                min=Min("generationmembership__fitness"))['min']
        avg = generation.individuals.aggregate(
                avg=Avg("generationmembership__fitness"))['avg']
        if output is None:
            print "%d %f %f %f" % (index, best, avg, worst)
        else:
            out.write("%d %f %f %f\n" % (index, best, avg, worst))
    if output is not None:
        out.close()

def simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn, debug_mode=DEBUG):
    # Init population
    population = init_population(num_pop)
    debug("Population initialized", debug_mode & DEBUG_STEP)
    # Fetch generation
    generation = population.current_generation()
    debug("Generation: %s" % ([x for x in generation.individuals.all()],),
            debug_mode & DEBUG_VALUE)
    simulate_evaluate_generation(generation, num_pop*EPISODES_FACTOR,
            fitness_fn, debug_mode)
    debug("First generation evaluated", debug_mode & DEBUG_STEP)
    for i in range(num_iter-1):
        debug("Iteration %d" % (i+1,), debug_mode & DEBUG_PROG)
        generation = switch_generations(num_pop, population, debug_mode)
        debug("Generation complete", debug_mode & DEBUG_STEP)
        debug([x for x in generation.individuals.all()],
                debug_mode & DEBUG_VALUE)
        # evaluation
        simulate_evaluate_generation(generation, num_pop*EPISODES_FACTOR,
                fitness_fn, debug_mode)
        debug("Generation %d evaluated" % (i+1,), debug_mode & DEBUG_STEP)
    return population

def simulate_evaluate_generation(generation, episodes, fitness_fn,
        debug_mode=DEBUG):
    for _ in range(episodes):
        try:
            individual = generation.select_next_individual()
        except ImpossibleException:
            continue
        else:
            # Evaluate the individual
            fitness = fitness_fn(individual.chromosome)
            debug("Fitness of %s = %f" % (individual, fitness),
                    debug_mode & DEBUG_VALUE)
            # Store fitness
            generation.fitness(individual, fitness)
