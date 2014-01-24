from oertutor.ga.algorithm import init_population, mutate, crossover,\
        switch_generations
from oertutor.ga.models import Gene, Chromosome, Generation, Population
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga.utils import debug, DEBUG_VALUE, DEBUG_STEP, DEBUG_PROG
from django.db.models import Avg
from copy import copy
from decimal import Decimal
from difflib import SequenceMatcher
from pytz import timezone
from datetime import datetime
from math import factorial
import random

DEBUG = DEBUG_PROG | DEBUG_STEP
MIN_SOL_LEN = 2
MAX_SOL_LEN = 2

def gen_chromosomes(num, pool, min_len=1, max_len=4):
    # Ensure that sequences are not longer than possible
    max_len = min(len(pool), max_len)
    chromosomes = []
    for _ in range(num):
        seq = []
        length = random.randint(min_len, max_len)
        for _ in range(length):
            gene = random.choice(pool)
            while gene in seq:
                gene = random.choice(pool)
            seq.append(gene)
        chromosomes.append(Chromosome.factory(seq))
    return chromosomes

def create_fitness_fn(solutions, noise):
    return lambda c: random.gauss(max([
            SequenceMatcher(a=c,b=s).ratio() for s in solutions]), noise)

def clear_pool():
    Population.objects.all().delete()
    Generation.objects.all().delete()
    Chromosome.objects.all().delete()
    Gene.objects.all().delete()

def simulate(num_pool, noise, num_pop, num_iter, p_mutate, DEBUG=0x0,
        export_dir=None):
    debug("Start", DEBUG & DEBUG_PROG)
    clear_pool()
    pool = Gene.factory(num_pool)
    debug("Generated %d genes in the pool" % (num_pool,), DEBUG & DEBUG_VALUE)
    solutions = gen_chromosomes(1, pool,MIN_SOL_LEN,MAX_SOL_LEN)
    debug("Generated solutions: %s" % (solutions,), DEBUG & DEBUG_VALUE)
    fitness_fn = create_fitness_fn(solutions, noise)
    population = simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn,
            DEBUG)
    debug("Stop", DEBUG & DEBUG_PROG)
    if export_dir is not None:
        debug("Exporting fitness data", DEBUG & DEBUG_PROG)
        export_fitness_data(population,
                export_dir+"/fitness_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting fitness [all] data", DEBUG & DEBUG_PROG)
        export_fitness_all_data(population,
                export_dir+"/fitness_all_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting coverage data", DEBUG & DEBUG_PROG)
        export_coverage_data(population, num_pool,
                export_dir+"/coverage_%s_%d_%f_%d_%d.dat" % (datetime.now(
                    timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                    num_pool,
                    noise,
                    num_pop,
                    num_iter))
        debug("Exporting chromosome track data", DEBUG & DEBUG_PROG)
        export_chromosome_track_data(population,
                export_dir+"/chromosome_track_%s_%d_%f_%d_%d.dat" % (
                    datetime.now(
                        timezone('Europe/Amsterdam')).strftime("%Y-%m-%d-%H%M"),
                        num_pool,
                        noise,
                        num_pop,
                        num_iter))
    debug("Done", DEBUG & DEBUG_PROG)
    return population

def export_chromosome_track_data(population, output=None):
    if output is not None:
        f = open(output, "w")
    mapping = {}
    for index, generation in enumerate(population.generations.all()):
        for chromosome in generation.chromosomes.all():
            if tuple(chromosome) in mapping:
                mapping[tuple(chromosome)].append(
                 (index,generation.fitness(chromosome)))
            else:
                mapping[tuple(chromosome)] = [(index, generation.fitness(chromosome))]
    items = sorted(mapping.items(), key=lambda x: len(x[1]), reverse=True)
    for item in items:
        if output is None:
            print "%s >> %s" % (item[0], item[1])
        else:
            f.write("%s >> %s\n" % (item[0], item[1]))
    if output is not None:
        f.close()
    return mapping

def export_coverage_data(population, num_pool, output=None):
    total = Decimal(sum([factorial(num_pool)/factorial(num_pool-l) for l in range(
        1, num_pool+1)]))
    labels = ["generation", "coverage"]
    if output is not None:
        f = open(output, "w")
        f.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    coverage = set([])
    for index, generation in enumerate(population.generations.all()):
        for chromosome in generation.chromosomes.all():
            coverage.add(tuple(chromosome))
        if output is None:
            print "%d %f" % (index, Decimal(len(coverage))/total)
        else:
            f.write("%d %f\n" % (index, Decimal(len(coverage))/total))
    if output is not None:
        f.close()


def export_fitness_all_data(population, output=None):
    labels = ["generation"]+[str(i) for i in range(1,
        population.current_generation().chromosomes.count()+1)]
    if output is not None:
        f = open(output, "w")
        f.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    for index, generation in enumerate(population.generations.all()):
        values = [index]
        for chromosome in generation.chromosomes.order_by(
                '-generationmembership__fitness'):
            values.append(generation.fitness(chromosome))
        if output is None:
            print ("%d"+(" %f"*(len(values)-1))) % tuple(values)
        else:
            f.write(("%d"+(" %f"*(len(values)-1))+"\n") % tuple(values))
    if output is not None:
        f.close()

def export_fitness_data(population, output=None):
    labels = ["generation", "best", "average", "worst"]
    if output is not None:
        f = open(output, "w")
        f.write(" ".join(labels)+"\n")
    else:
        print " ".join(labels)
    for index, generation in enumerate(population.generations.all()):
        best = generation.fitness(generation.select_best_chromosome())
        worst = generation.fitness(generation.select_worst_chromosome())
        avg = generation.chromosomes.aggregate(
                avg=Avg("generationmembership__fitness"))['avg']
        if output is None:
            print "%d %f %f %f" % (index, best, avg, worst)
        else:
            f.write("%d %f %f %f\n" % (index, best, avg, worst))
    if output is not None:
        f.close()

def simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn, DEBUG=0x0):
    # Init population
    population = init_population(num_pop)
    debug("Population initialized", DEBUG & DEBUG_STEP)
    # Fetch generation
    generation = population.current_generation()
    debug("Generation: %s" % ([x for x in generation.chromosomes.all()],),
            DEBUG & DEBUG_VALUE)
    simulate_evaluate_generation(generation, fitness_fn)
    debug("First generation evaluated", DEBUG & DEBUG_STEP)
    for i in range(num_iter-1):
        debug("Iteration %d" % (i+1,), DEBUG & DEBUG_PROG)
        generation = switch_generations(num_pop, population, DEBUG)
        debug("Generation complete", DEBUG & DEBUG_STEP)
        debug([x for x in generation.chromosomes.all()], DEBUG & DEBUG_VALUE)
        # evaluation
        simulate_evaluate_generation(generation, fitness_fn)
        debug("Generation %d evaluated" % (i+1,), DEBUG & DEBUG_STEP)
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
