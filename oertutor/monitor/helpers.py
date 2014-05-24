from decimal import Decimal
from oertutor.ga.models import *
from oertutor.tutor.models import *

def gather_fitness_data(chromosome):
    fitness_data = []
    for evaluation in Evaluation.objects.filter(chromosome=chromosome):
        fitness_data.append(evaluation.value)
    return fitness_data

def gather_regret_data(population, mode=None):
    regret_data = []
    # Initialization of mode-specific variables
    if mode == "genbest":
        genbest = {}
        for generation in population.generations.all():
            best = generation.select_best_individuals()[0]
            mem = GenerationMembership.objects.get(
                    generation=generation, individual=best)
            genbest[generation.pk] = mem.fitness
    elif mode == "popbest":
        popbest = Decimal(0)
        for generation in population.generations.all():
            best = generation.select_best_individuals()[0]
            mem = GenerationMembership.objects.get(
                    generation=generation, individual=best)
            if popbest < Decimal(best.chromosome.fitness):
                popbest = best.chromosome.fitness
    elif mode == "avg":
        ravg = {}

    # Gathering mode-specific regret values
    for evaluation in Evaluation.objects.filter(population=population):
        if mode == "genbest":
            maxvalue = Decimal(genbest[evaluation.generation.pk])
            mem = GenerationMembership.objects.get(
                    generation=evaluation.generation,
                    individual=evaluation.individual)
            value = mem.fitness
        elif mode == "popbest":
            maxvalue = Decimal(popbest)
            mem = GenerationMembership.objects.get(
                    generation=evaluation.generation,
                    individual=evaluation.individual)
            value = mem.chromosome.fitness
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
            value = ravg[chromosome][0]/ravg[chromosome][1]
        else:
            maxvalue = 1
            value = evaluation.value
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
