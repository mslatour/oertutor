from decimal import Decimal
from oertutor.ga.models import *
from oertutor.tutor.models import *

def chromosome_identity(chromosome):
  return str([str(gene) for gene in
    chromosome.genes.order_by("chromosomemembership__index")])

def gather_real_fitness_data(chromosome, **kwargs):
  '''
    function to clean up the mess of bad immigration
  '''
  values = []
  identity = chromosome_identity(chromosome)
  for evaluation in Evaluation.objects.filter(**kwargs):
    if chromosome_identity(evaluation.chromosome) == identity:
      values.append(evaluation.value)
  return values

def determine_real_fitness(**kwargs):
  values = gather_real_fitness_data(**kwargs)
  return sum(values)/Decimal(len(values))

def gather_fitness_data(chromosome, population=None):
    fitness_data = []
    if population is None:
        evaluations = Evaluation.objects.filter(chromosome=chromosome)
    else:
        evaluations = Evaluation.objects.filter(chromosome=chromosome,
            population=population)

    for evaluation in evaluations:
        fitness_data.append(evaluation.value)
    return fitness_data

def gather_regret_data(population, mode=None, alternative=False):
    regret_data = []
    # Initialization of mode-specific variables
    popbest = Decimal(0)
    genbest = {}
    popbest_i = None
    genbest_i = {}
    c_fitness = {}
    for generation in population.generations.all():
        genbest[generation.pk] = Decimal(0)
        genbest_i[generation.pk] = None
        chromosomes = set([])
        for evaluation in Evaluation.objects.filter(generation=generation):
            chromosomes.add(evaluation.chromosome)
        for chromosome in chromosomes:
            if alternative:
                fitness = determine_real_fitness(chromosome=chromosome,
                        population=population)
                c_fitness[chromosome_identity(chromosome)] = fitness
            else:
                fitness = chromosome.fitness
            if fitness is not None:
                if popbest < Decimal(fitness):
                    genbest[generation.pk] = Decimal(fitness)
                    genbest_i[generation.pk] = chromosome
                    popbest = Decimal(fitness)
                    popbest_i = chromosome
                elif genbest[generation.pk] < Decimal(fitness):
                    genbest[generation.pk] = Decimal(fitness)
                    genbest_i[generation.pk] = chromosome
    print 'popbest: %s (%.12f)' % (popbest_i, popbest)
    if mode == "avg":
        ravg = {}

    # Gathering mode-specific regret values
    for evaluation in Evaluation.objects.filter(population=population):
        if alternative:
            value = c_fitness.get(
                    chromosome_identity(evaluation.chromosome),None)
            if value is None:
                print evaluation.pk, evaluation.chromosome, population
        else:
            value = evaluation.individual.chromosome.fitness

        if mode == "genbest":
            maxvalue = genbest[evaluation.generation.pk]
        elif mode == "popbest":
            maxvalue = popbest
        elif mode == "avg":
            maxvalue = 1
            eval_value = evaluation.value
            chromosome = evaluation.chromosome

            if chromosome in ravg:
                ravg[chromosome] = (
                    ravg[chromosome][0] + eval_value,
                    ravg[chromosome][1] + Decimal(1))
            else:
                ravg[chromosome] = (eval_value, Decimal(1))
            value = Decimal(ravg[chromosome][0]/ravg[chromosome][1])
        else:
            maxvalue = 1
        regret_data.append(maxvalue-value)
    return regret_data

def gather_bootstrap_progress_data(category):
    progress_data = []
    total = float(BootstrapEvaluation.objects.filter(
            category=category).count())
    used = 0
    for trial in Trial.objects.filter(category=category).exclude(
            evaluation=None):
        if BootstrapEvaluation.objects.filter(trial=trial).exists():
            used += 1
        progress_data.append(used/total)
    return progress_data

def running_average(data):
    avg_data = []
    total = 0
    count = 0
    for datum in data:
        total += datum
        count += 1
        avg_data.append(total/Decimal(count))
    return avg_data

def cumulativy_data(data):
    cumul_data = []
    for datum in data:
        if cumul_data == []:
            cumul_data.append(datum)
        else:
            cumul_data.append(datum+cumul_data[-1])
    return cumul_data
