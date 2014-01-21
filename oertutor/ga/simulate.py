from oertutor.ga.algorithm import init_population, mutate, crossover
from oertutor.ga.models import Gene, Chromosome, Generation, Population
import random
from copy import copy

def create_fitness_fn(chromosomes, noise):
    fitness_values = range(100*len(chromosomes))
    random.shuffle(fitness_values)
    fitness_assigned = {}
    for index, chromosome in enumerate(chromosomes):
        fitness_assigned[chromosome.pk] = fitness_values[index]
    print "Fitness function values: %s" % (fitness_assigned,)
    return lambda x: random.random()
    return (lambda chromosome:
                random.gauss(fitness_assigned[chromosome.pk], noise))

def clear_pool():
    Population.objects.all().delete()
    Generation.objects.all().delete()
    Chromosome.objects.all().delete()
    Gene.objects.all().delete()

def simulate(num_pool, noise, num_pop, num_iter, p_mutate):
    clear_pool()
    print "Cleared pool"
    pool = Gene.factory(num_pool)
    print "Generated %d genes in the pool" % (num_pool,)
    fitness_fn = create_fitness_fn(pool, noise)
    population = simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn)
    return population

def simulate_ga_loop(num_pop, num_iter, p_mutate, fitness_fn):
    # Init population
    population = init_population(num_pop)
    print "Population initialized"
    # Fetch generation
    generation = population.current_generation()
    print "Generation: %s" % ([x for x in generation.chromosomes.all()],)
    simulate_evaluate_generation(generation, fitness_fn)
    print "First generation evaluated"
    for i in range(num_iter-1):
        print "Iteration %d" % (i,)
        # survivor selection
        survivors = [copy(x) for x in
                generation.select_by_fitness_pdf(num_pop/2)]
        print "%d survivors: %s" % (len(survivors), survivors)
        # new generation
        generation = population.next_generation(survivors)
        for _ in range(num_pop-(num_pop/2)):
            if random.random() < p_mutate:
                print "Mutate!"
                # mutation
                generation.add_chromosomes([
                        mutate(generation.select_by_fitness_pdf(1)[0])])
            else:
                print "Recombine!"
                # parent selection
                parents = generation.select_by_fitness_pdf(2)
                print "Parents selected: %s" % (parents,)
                generation.add_chromosomes(
                        crossover(parents[0], parents[1]))
        print "Generation complete"
        print [x for x in generation.chromosomes.all()]
        # evaluation
        simulate_evaluate_generation(generation, fitness_fn)
        print "Generation %d evaluated" % (i,)
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
