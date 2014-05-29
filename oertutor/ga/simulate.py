from oertutor.ga.models import Population, Generation, Individual, \
        Chromosome, Gene, Evaluation
from oertutor.ga.algorithm import init_population, switch_generations
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga.utils import debug, DEBUG_VALUE, DEBUG_STEP, DEBUG_PROG, \
        DEBUG_SUITE
from django.db import reset_queries
from django.db.models import Avg, Min, Max
from decimal import Decimal
from difflib import SequenceMatcher
from pytz import timezone
from datetime import datetime
from math import factorial
from copy import copy
import matplotlib.pyplot as plt
from numpy import std
import cPickle as pickle
import random
import os
import json
import gc
import re

DEBUG = DEBUG_PROG | DEBUG_STEP
MIN_SOL_LEN = 3
MAX_SOL_LEN = 3

class Environment:

    def optimal(self):
        pass

    def fitness(self, chromosome):
        pass

class ModelSampleEnvironment(Environment):
    model = []
    noise = 0
    noise_history = []

    def __init__(self, model=[], noise=0):
        """
          model is a list of tuples (regex_string, value)
        """
        for pattern, value in model:
            self.model.append((re.compile(pattern), value))
        self.noise = noise

    def optimal(self, chromosome):
        match = str([gene.pk for gene in chromosome])
        for pattern, value in self.model:
            if value == 1 and pattern.match(match):
                return True
        return False

    def optimal_fitness(self, index=None):
        cap = index + 1 if index is not None else None
        return max(0, min(1,
            1+(sum(self.noise_history[:cap])/len(self.noise_history[:cap]))))

    def fitness(self, chromosome):
        match = str([int(gene.pk) for gene in chromosome])
        true_value = 0
        for pattern, value in self.model:
            if pattern.match(match):
                true_value = value
                break
        value = max(min(random.gauss(true_value, self.noise), 1), 0)
        self.noise_history.append(value-true_value)
        return value

class DistanceSampleEnvironment(Environment):
    solutions = None
    noise = 0
    noise_history = []

    def __init__(self, **kwargs):
        if 'noise' in kwargs:
            self.noise = kwargs['noise']
        if 'solutions' in kwargs:
            self.solutions = kwargs['solutions']
        else:
            # Retrieve or generate solutions
            if 'pool' in kwargs:
                pool = kwargs['pool']
            else:
                raise Exception('Provide either solutions or a gene pool')
            # Generate solutions
            if 'num_solutions' in kwargs and 'len_solution' in kwargs:
                # Ensure that sequences are not longer than possible
                if kwargs['len_solution'] > len(pool):
                    raise Exception('Not enough genes in the pool')
                self.solutions = []
                for _ in xrange(kwargs['num_solutions']):
                    seq = []
                    for _ in xrange(kwargs['len_solution']):
                        gene = random.choice(pool)
                        while gene in seq:
                            gene = random.choice(pool)
                        seq.append(gene)
                    self.solutions.append(seq)
            else:
                raise Exception('Provide num_solutions and len_solutions.')

    def optimal(self, chromosome):
        return list(chromosome) in self.solutions

    def optimal_fitness(self, index=None):
        cap = index + 1 if index is not None else None
        return max(0, min(1,
            1+(sum(self.noise_history[:cap])/len(self.noise_history[:cap]))))

    def fitness(self, chromosome):
        distance = max([SequenceMatcher(a=chromosome, b=s).ratio()
                        for s in self.solutions])
        value = max(min(random.gauss(distance, self.noise), 1), 0)
        self.noise_history.append(value-distance)
        return value

class TabularCell:
    values = []
    _cast = None

    def __init__(self, value=None, cast=None):
        self._cast = cast
        self.values = []
        if value is not None:
            self.append(value)

    def __int__(self):
        aggr = sum([int(value) for value in self.values])
        return aggr / len(self)

    def __long__(self):
        aggr = sum([long(value) for value in self.values])
        return aggr / long(len(self))

    def __float__(self):
        aggr = sum([float(value) for value in self.values])
        return aggr / float(len(self))

    def decimal(self):
        aggr = sum([Decimal(value) for value in self.values])
        return aggr / Decimal(len(self))

    def __str__(self):
        if self._cast in [float, int, long]:
            return str(self._cast(self))
        elif self._cast == Decimal:
            return str(self.decimal())
        elif self._cast == str:
            return ",".join(self.values)
        else:
            return ",".join([str(value) for value in self.values])

    def __repr__(self):
        return "TabularCell(%s)" % (self,)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def __reversed__(self):
        return reversed(self.tabular)

    def __contains__(self, item):
        return item in self.tabular

    def cast(self, cast=None):
        if cast is None:
            return self._cast
        elif cast != self._cast:
            self._cast = cast
            self.values = [self._cast(value) for value in self.values]

    def std(self):
        if self._cast == Decimal:
            return std([float(v) for v in self.values])
        else:
            return std(self.values)

    def append(self, value):
        if isinstance(value, TabularCell):
            if self._cast is None:
                self._cast = value.cast()

            if self._cast != value.cast:
                self.values += [self._cast(elem) for elem in value]
            else:
                self.values += list(value)
        else:
            if self._cast is None:
                self._cast = type(value)
                self.values.append(value)
            else:
                self.values.append(self._cast(value))

    def __getitem__(self, key):
        return self.tabular[key]

    def __setitem__(self, key, value):
        if isinstance(value, list):
            value = TabularData(value)
        self.tabular[key] = value

    def __delitem__(self, key):
        del self.tabular[key]


class TabularData:
    tabular = []
    labels = []
    pointer = 0

    def __init__(self, data=[], labels=[]):
        self.tabular = []
        self.labels = labels
        self.pointer = 0
        if isinstance(data, list):
            for elem in data:
                self.append(elem)
        else:
            raise ValueError("List expected, got %s" % (type(data),))

    def append(self, data):
        if isinstance(data, list):
            data = TabularData(data)
        elif not isinstance(data, TabularData):
            data = TabularCell(data)
        if self.pointer == len(self.tabular):
            self.tabular.append(data)
        else:
            if type(data) != type(self.tabular[self.pointer]):
                raise ValueError("Impossible to merge %s, %s" % (
                    type(data), type(self.tabular[self.pointer])))
            if isinstance(data, TabularData):
                for elem in data:
                    self.tabular[self.pointer].append(elem)
            else:
                self.tabular[self.pointer].append(data)
        self.pointer += 1

    def reset(self):
        self.pointer = 0
        for elem in self.tabular:
            if isinstance(elem, TabularData):
                elem.reset()

    def __copy__(self):
        tab = TabularData(copy(self.tabular))
        tab.labels = copy(self.labels)
        tab.pointer = self.pointer
        return tab

    def __getitem__(self, key):
        return self.tabular[key]

    def __setitem__(self, key, value):
        if isinstance(value, list):
            value = TabularData(value)
        self.tabular[key] = value

    def __delitem__(self, key):
        del self.tabular[key]

    def __add__(self, other):
        for elem in other:
            self.append(elem)
        return self

    def __radd__(self, other):
        return self.__add__(other)

    def __str__(self):
        return str(self.tabular)

    def __repr__(self):
        return "TabularData(%s)" % (self,)

    def __len__(self):
        return len(self.tabular)

    def __iter__(self):
        return iter(self.tabular)

    def __reversed__(self):
        return reversed(self.tabular)

    def __contains__(self, item):
        return item in self.tabular

    def __missing__(self, key):
        return self.tabular.__missing__(key)

class Exporter:
    output = None
    filename_pattern = "export_%s_%s_%s_%s.dat"

    def before(self, simulation, suite, analyzer, output_dir=None):
        if output_dir is not None:
            stamp = datetime.now(timezone('Europe/Amsterdam')).strftime(
                    "%Y-%m-%d-%H%M")
            path = self.filename_pattern % (suite, analyzer, simulation,
                    stamp)
            self.output = open(output_dir+path, 'w')

    def export(self, results, setups, suite, analyzer, output_dir=None):
        for simulation in setups:
            self.before(simulation, suite, analyzer, output_dir)
            self._export(results[simulation])
            self.after()

    def _export(self, results):
        if results.labels != []:
            self.output_line(" ".join(results.labels))
        for row in results:
            self.output_line(" ".join([str(c) for c in row]))

    def after(self):
        if self.output is not None:
            self.output.close()

    def output_line(self, line):
        if self.output is None:
            print line
        else:
            self.output.write("%s\n" % (line,))

class PickleExporter(Exporter):

    def __init__(self):
        self.filename_pattern = "export_%s_%s_%s_%s.pickle"

    def _export(self, results):
        if self.output is None:
            print pickle.dumps(results)
        else:
            pickle.dump(results, self.output)

class JoinedExporter(Exporter):
    def export(self, results, setups, suite, analyzer, output_dir=None):
        joined_results = TabularData()
        sorted_results = sorted(results.items(), key=lambda x: len(x[1]),
                reverse=True)

        labels = None
        for simulation, result in sorted_results:
            if labels is None:
                if len(result.labels) == 1:
                    labels = []
                else:
                    labels = [result.labels[0]]
            if len(result.labels) == 1:
                labels += [l+"-"+simulation for l in result.labels[:]]
            else:
                labels += [l+"-"+simulation for l in result.labels[1:]]

            for index, row in enumerate(result):
                row = copy(row)
                if index > (len(joined_results)-1):
                    joined_results.append(row)
                else:
                    if len(result.labels) == 1:
                       joined_results[index] += row[:]
                    else:
                       joined_results[index] += row[1:]
        joined_results.labels = labels
        self.before("joined", suite, analyzer, output_dir)
        self._export(joined_results)
        self.after()

class JoinedPickleExporter(JoinedExporter):

    def __init__(self):
        self.filename_pattern = "export_%s_%s_%s_%s.pickle"

    def _export(self, results):
        if self.output is None:
            print pickle.dumps(results)
        else:
            pickle.dump(results, self.output)

class Analyzer:
    def analyze(self, population, setup, environment, results=None):
        pass

class RegretAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["evaluation", "regret"]
        evaluations = enumerate(
            Evaluation.objects.order_by('pk').filter(population=population))
        optimal_expected_value = 0
        for index, evaluation in evaluations:
            optimal_expected_value *= index
            optimal_expected_value += Decimal(
                    environment.fitness(environment.optimal()))
            optimal_expected_value /= (index+1)
            results.append([index,
                min(1, max(0, optimal_expected_value-Decimal(evaluation.value)))])
            del optimal_expected_value
        del evaluations
        return results

class CumulativeRegretAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["evaluation", "regret"]
        regret = 0
        evaluations = enumerate(
            Evaluation.objects.order_by('pk').filter(population=population))
        for index, evaluation in evaluations:
            if environment.optimal(evaluation.chromosome):
                results.append([index, regret])
            else:
                optimal_expected_value = Decimal(
                        str(environment.optimal_fitness(index)))
                regret += min(1, max(0,
                    optimal_expected_value-Decimal(str(evaluation.value))))
                results.append([index, regret])
                del optimal_expected_value
        del evaluations
        return results

class ConvergenceAnalyzer(Analyzer):
    _threshold = 1

    def __init__(self, threshold=1):
        self._threshold = threshold

    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["convergence"]
        evaluations = enumerate(
            Evaluation.objects.order_by('pk').filter(population=population))
        counter = 0
        for index, evaluation in evaluations:
            if environment.optimal(evaluation.chromosome):
                counter += 1
                if counter == self._threshold:
                    break
            else:
                counter = 0
        results.append([float(index)])
        return results

class EvaluationAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["evaluation", "regret"]
        evaluations = enumerate(
                Evaluation.objects.filter(population=population))
        for index, evaluation in evaluations:
            results.append([index, evaluation.value])
        del evaluations
        return results

class EvaluationChoiceAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["evaluation", "chromosome"]
        evaluations = enumerate(
                Evaluation.objects.filter(population=population))
        for index, evaluation in evaluations:
            results.append([index, str(evaluation.chromosome)])
        del evaluations
        return results

    def combine(self, results):
        if len(results) == 0:
            return []
        return results[0]

class CoverageAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["evaluation", "coverage"]
        if "num_pool" in setup:
            num_pool = setup['num_pool']
        else:
            num_pool = len(population.pool)
        total = (Decimal(sum([factorial(num_pool)/factorial(num_pool-l)
            for l in xrange(1, num_pool+1)])))
        coverage = set([])
        generations = enumerate(population.generations.all())
        for index, generation in generations:
            for individual in generation.individuals.all():
                coverage.add(tuple(individual.chromosome))
            results.append([index, Decimal(len(coverage))/total])
        del generations
        del coverage
        del total
        return results

class FitnessAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["generation", "best", "average", "worst"]
        generations = enumerate(population.generations.all())
        for index, generation in generations:
            best = generation.individuals.aggregate(
                    max=Max("generationmembership__fitness"))['max']
            worst = generation.individuals.aggregate(
                    min=Min("generationmembership__fitness"))['min']
            avg = generation.individuals.aggregate(
                    avg=Avg("generationmembership__fitness"))['avg']
            results.append([index, best, avg, worst])
        del generations
        return results

class FitnessAllAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, results=None, **kwargs):
        if results is None:
            results = TabularData()
        results.labels = ["generation"]+[str(i) for i in xrange(1,
            population.current_generation().individuals.count()+1)]
        generations = enumerate(population.generations.all())
        for index, generation in generations:
            values = [index]
            for individual in generation.individuals.order_by(
                    '-generationmembership__fitness'):
                values.append(generation.fitness(individual))
            results.append(values)
        del values
        del individual
        del generations
        return results

class SimulationSuite:
    simulation_fn = (lambda x: x)
    output_dir = None
    label = None
    pool = None
    environments = {}
    default_setup = {}
    setups = {}
    analyzers = {}
    results = {}
    exporters = {}

    def __init__(self, simulation_fn, output_dir=None, label=None):
        self.simulation_fn = simulation_fn
        self.output_dir = output_dir
        if label is None:
            stamp = datetime.now(timezone('Europe/Amsterdam')).strftime(
                    "%Y-%m-%d-%H%M")
            self.label = "simulation_"+stamp
        else:
            self.label = label

    def save(self):
        if self.output_dir is not None:
            if self.output_dir[-1] == "/":
                self.output_dir = self.output_dir+self.label+"/"
            else:
                self.output_dir = self.output_dir+"/"+self.label+"/"
            os.makedirs(self.output_dir)
            f_setups = open(self.output_dir+"setups.json", "w")
            json.dump(self.setups, f_setups, indent=2)
            f_setups.close()
            del f_setups

    def set_pool(self, pool=None):
        if isinstance(pool, list):
            self.pool = pool
        elif isinstance(pool, int):
            self.pool = Gene.factory(pool)
        else:
            raise Exception('Provide either a list of genes of a pool size')

    def set_defaults(self, **kwargs):
        self.default_setup = kwargs

    def add_environment(self, environment, label=None):
        if label is None:
            label = "environment-%d" % (len(self.environments),)
        self.environments[label] = environment

    def add_simulation(self, setup, label=None):
        if label is None:
            label = "simulation-%d" % (len(self.setups),)
        self.setups[label] = setup

    def add_analyzer(self, analyzer, label=None):
        if label is None:
            label = "analyzer-%d" % (len(self.analyzers),)
        self.analyzers[label] = analyzer

    def add_exporter(self, exporter, on="all"):
        if on in self.exporters:
            self.exporters[on].append(exporter)
        else:
            self.exporters[on] = [exporter]

    def simulate(self, debug_mode=DEBUG_SUITE, repetitions=1):
        self.save()
        self.results = {}
        for environment in self.environments:
            debug("Entering %s" % (environment,), debug_mode & DEBUG_SUITE)
            for simulation in self.setups:
                for repetition in xrange(repetitions):
                    debug("Running %s [Repetition %d]" %
                            (simulation, repetition), debug_mode & DEBUG_SUITE)
                    population = self.simulation_fn(
                            debug_mode = debug_mode,
                            genes = self.pool,
                            fitness_fn = self.environments[environment].fitness,
                            **dict(
                                self.default_setup.items()
                                +self.setups[simulation].items()))
                    debug("Analyzing %s" % (simulation,), debug_mode & DEBUG_SUITE)
                    self.analyze(environment, simulation, population,
                            debug_mode)
                    del population
                    reset_queries()
                    clear(False)
            debug("Exporting", debug_mode & DEBUG_SUITE)
            self.export(environment)

    def analyze(self, environment, simulation, population, debug_mode):
        for analyzer in self.analyzers:
            if environment not in self.results:
                self.results[environment] = {}
            if analyzer not in self.results[environment]:
                self.results[environment][analyzer] = {}
            if simulation not in self.results[environment][analyzer]:
                self.results[environment][analyzer][simulation] = TabularData()

            debug("Running %s on %s in %s" % (analyzer, simulation,
                environment), debug_mode & DEBUG_SUITE)

            self.results[environment][analyzer][simulation].reset()
            self.analyzers[analyzer].analyze(
                population = population,
                setup = self.setups[simulation],
                environment = self.environments[environment],
                results = self.results[environment][analyzer][simulation])

    def export(self, environment):
        if len(self.environments) > 1:
            output_dir = self.output_dir + environment + "/"
            os.makedirs(output_dir)
        else:
            output_dir = self.output_dir

        for analyzer in self.results[environment]:
            if analyzer in self.exporters:
                for exporter in self.exporters[analyzer]:
                    exporter.export(self.results[environment][analyzer],
                            self.setups, self.label, analyzer, output_dir)
            if "all" in self.exporters:
                for exporter in self.exporters["all"]:
                    exporter.export(self.results[environment][analyzer],
                            self.setups, self.label, analyzer, output_dir)

def gen_solutions(num, pool, min_len=1, max_len=4):
    # Ensure that sequences are not longer than possible
    max_len = min(len(pool), max_len)
    solutions = []
    for _ in xrange(num):
        seq = []
        length = random.randint(min_len, max_len)
        for _ in xrange(length):
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


def clear(clear_genes=False):
    objs = Evaluation.objects.all()
    objs.delete()
    del objs
    objs = Generation.objects.all()
    objs.delete()
    del objs
    objs = Population.objects.all()
    objs.delete()
    del objs
    objs = Individual.objects.all()
    objs.delete()
    del objs
    objs = Chromosome.objects.all()
    objs.delete()
    del objs
    if clear_genes:
        objs = Gene.objects.all()
        objs.delete()
        del objs
    gc.collect()

def simulate( num_pool, noise, num_pop, num_iter, num_elite, p_mutate,
              episodes_factor, debug_mode=DEBUG, export_dir=None):
    debug("Start", debug_mode & DEBUG_PROG)
    clear(True)
    debug("Generated %d genes in the pool" % (num_pool,),
            debug_mode & DEBUG_VALUE)
    pool = Gene.factory(num_pool)
    solutions = gen_solutions(1, pool, MIN_SOL_LEN, MAX_SOL_LEN)
    debug("Generated solutions: %s" % (solutions,), debug_mode & DEBUG_PROG)
    fitness_fn = create_fitness_fn(solutions, noise)
    population = simulate_ga_loop(num_pop, num_iter, num_elite, p_mutate,
            fitness_fn, episodes_factor, debug_mode)
    debug("Stop", debug_mode & DEBUG_PROG)
    if export_dir is not None:
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

def simulate_ga_loop( num_pop, num_iter, num_elite, p_mutate, fitness_fn,
                      episodes_factor, genes=None,debug_mode=DEBUG):
    # Init population
    population = init_population(num_pop, genes=genes)
    debug("Population initialized", debug_mode & DEBUG_STEP)
    # Fetch generation
    generation = population.current_generation()
    debug("Generation: %s" % ([x for x in generation.individuals.all()],),
            debug_mode & DEBUG_VALUE)
    simulate_evaluate_generation(generation, num_pop*episodes_factor,
            fitness_fn, debug_mode)
    debug("First generation evaluated", debug_mode & DEBUG_STEP)
    for i in xrange(num_iter-1):
        debug("Iteration %d" % (i+1,), debug_mode & DEBUG_PROG)
        del generation
        generation = switch_generations(num_pop, num_elite, p_mutate,
                population, debug_mode)
        debug("Generation complete", debug_mode & DEBUG_STEP)
        debug([x for x in generation.individuals.all()],
                debug_mode & DEBUG_VALUE)
        # evaluation
        simulate_evaluate_generation(generation, num_pop*episodes_factor,
                fitness_fn, debug_mode)
        debug("Generation %d evaluated" % (i+1,), debug_mode & DEBUG_STEP)
    return population

def simulate_evaluate_generation( generation, episodes,
                                  fitness_fn, debug_mode=DEBUG):
    for _ in xrange(int(episodes)):
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
