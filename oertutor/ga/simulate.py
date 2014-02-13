from oertutor.ga.models import Population, Generation, Individual, \
        Chromosome, Gene, Evaluation
from oertutor.ga.algorithm import init_population, switch_generations
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga.utils import debug, DEBUG_VALUE, DEBUG_STEP, DEBUG_PROG, \
        DEBUG_SUITE
from django.db.models import Avg, Min, Max
from decimal import Decimal
from difflib import SequenceMatcher
from pytz import timezone
from datetime import datetime
from math import factorial
import random
import os
import json

DEBUG = DEBUG_PROG | DEBUG_STEP
MIN_SOL_LEN = 3
MAX_SOL_LEN = 3

class Environment:

    def optimal(self):
        pass

    def fitness(self, chromosome):
        pass

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
                for _ in range(kwargs['num_solutions']):
                    seq = []
                    for _ in range(kwargs['len_solution']):
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

class Exporter:
    output = None

    def before(self, simulation, suite, analyzer, output_dir=None):
        if output_dir is not None:
            stamp = datetime.now(timezone('Europe/Amsterdam')).strftime(
                    "%Y-%m-%d-%H%M")
            path = "export_%s_%s_%s_%s.dat" % (suite, analyzer, simulation,
                    stamp)
            self.output = open(output_dir+path, 'w')

    def export(self, results, setups, suite, analyzer, output_dir=None):
        for simulation in setups:
            self.before(simulation, suite, analyzer, output_dir)
            self._export(results[simulation])
            self.after()

    def _export(self, results):
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

class JoinedExporter(Exporter):
    def export(self, results, setups, suite, analyzer, output_dir=None):
        joined_results = None
        sorted_results = sorted(results.items(), key=lambda x: len(x[1]),
                reverse=True)
        for simulation, result in sorted_results:
            for index, row in enumerate(result):
                if index == 0:
                    if joined_results is None:
                        joined_results = [[result[0][0]]]
                    joined_results[0] += [l+"-"+simulation
                            for l in result[0][1:]]
                else:
                    if index > (len(joined_results)-1):
                        joined_results.append(row)
                    else:
                        joined_results[index] += row[1:]
        self.before("joined", suite, analyzer, output_dir)
        self._export(joined_results)
        self.after()

class Analyzer:
    def analyze(self, population, setup):
        pass

    def combine(self, results):
        if len(results) == 1:
            return results[0]
        result_iter = iter(results)
        results1 = next(result_iter)
        for i, results2 in enumerate(result_iter):
            if results1 == results2:
                return results1
            elif len(results1) != len(results2):
                raise Exception('Result sets have different size')
            results1 = self.combine_aux(i, results1, results2)
        return results1

    def combine_aux(self, i, results1, results2):
        results = []
        for index, elem1 in enumerate(results1):
            elem2 = results2[index]
            if elem1 == elem2:
                results.append(elem1)
            elif not (
                isinstance(elem1, type(elem2))
                or (
                    isinstance(elem1, (int, float, Decimal)) and
                    isinstance(elem2, (int, float, Decimal))
                )
            ):
                raise Exception('Elements must have the same type.')
            elif isinstance(elem1, list):
                results.append(self.combine_aux(i, elem1, elem2))
            elif isinstance(elem1, (int, float, Decimal)):
                results.append(
                        ((i+1)*Decimal(str(elem1))+Decimal(str(elem2)))/(i+2))
            else:
                print elem1, elem2
                raise Exception('Elements cannot be combined.')
        return results

class RegretAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, **kwargs):
        results = [["evaluation", "regret"]]
        evaluations = Evaluation.objects.filter(population=population)
        optimal_expected_value = 0
        for index, evaluation in enumerate(evaluations):
            optimal_expected_value *= index
            optimal_expected_value += Decimal(
                    environment.fitness(environment.optimal()))
            optimal_expected_value /= (index+1)
            results.append([index,
                min(1, max(0, optimal_expected_value-Decimal(evaluation.value)))])
        return results

class CumulativeRegretAnalyzer(Analyzer):
    def analyze(self, population, setup, environment, **kwargs):
        results = [["evaluation", "regret"]]
        regret = 0
        evaluations = Evaluation.objects.filter(population=population)
        for index, evaluation in enumerate(evaluations):
            if environment.optimal(evaluation.chromosome):
                results.append([index, regret])
            else:
                optimal_expected_value = Decimal(
                        str(environment.optimal_fitness(index)))
                regret += min(1, max(0,
                    optimal_expected_value-Decimal(str(evaluation.value))))
                results.append([index, regret])
        return results

class EvaluationAnalyzer(Analyzer):
    def analyze(self, population, setup, **kwargs):
        results = [["evaluation", "regret"]]
        evaluations = Evaluation.objects.filter(population=population)
        for index, evaluation in enumerate(evaluations):
            results.append([index, evaluation.value])
        return results

class EvaluationChoiceAnalyzer(Analyzer):
    def analyze(self, population, setup, **kwargs):
        results = [["evaluation", "chromosome"]]
        evaluations = Evaluation.objects.filter(population=population)
        for index, evaluation in enumerate(evaluations):
            results.append([index, str(evaluation.chromosome)])
        return results

    def combine(self, results):
        if len(results) == 0:
            return []
        return results[0]

class CoverageAnalyzer(Analyzer):
    def analyze(self, population, setup, **kwargs):
        results = [["generation", "coverage"]]
        num_pool = setup['num_pool']
        total = (Decimal(sum([factorial(num_pool)/factorial(num_pool-l)
            for l in range(1, num_pool+1)])))
        coverage = set([])
        for index, generation in enumerate(population.generations.all()):
            for individual in generation.individuals.all():
                coverage.add(tuple(individual.chromosome))
            results.append([index, Decimal(len(coverage))/total])
        return results

class FitnessAnalyzer(Analyzer):
    def analyze(self, population, setup, **kwargs):
        results = [["generation", "best", "average", "worst"]]
        for index, generation in enumerate(population.generations.all()):
            best = generation.individuals.aggregate(
                    max=Max("generationmembership__fitness"))['max']
            worst = generation.individuals.aggregate(
                    min=Min("generationmembership__fitness"))['min']
            avg = generation.individuals.aggregate(
                    avg=Avg("generationmembership__fitness"))['avg']
            results.append([index, best, avg, worst])
        return results

class FitnessAllAnalyzer(Analyzer):
    def analyze(self, population, setup, **kwargs):
        results = [["generation"]+[str(i) for i in range(1,
            population.current_generation().individuals.count()+1)]]
        for index, generation in enumerate(population.generations.all()):
            values = [index]
            for individual in generation.individuals.order_by(
                    '-generationmembership__fitness'):
                values.append(generation.fitness(individual))
            results.append(values)
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
                for repetition in range(repetitions):
                    debug("Running %s [Repetition %d]" % (simulation,repetition),
                            debug_mode & DEBUG_SUITE)
                    population = self.simulation_fn(
                            debug_mode = debug_mode,
                            fitness_fn = self.environments[environment].fitness,
                            **dict(
                                self.default_setup.items()
                                +self.setups[simulation].items()))
                    debug("Analyzing %s" % (simulation,), debug_mode & DEBUG_SUITE)
                    self.analyze(environment, simulation, population)
                    clear(False)
                debug('Combining %d repetitions' % (repetitions, ),
                        debug_mode & DEBUG_SUITE)
                for analyzer in self.results[environment]:
                    self.results[environment][analyzer][simulation] = \
                        self.analyzers[analyzer].combine(
                            self.results[environment][analyzer][simulation])
            debug("Exporting", debug_mode & DEBUG_SUITE)
            self.export(environment)

    def analyze(self, environment, simulation, population):
        for analyzer in self.analyzers:
            if environment not in self.results:
                self.results[environment] = {}
            if analyzer not in self.results[environment]:
                self.results[environment][analyzer] = {}
            if simulation not in self.results[environment][analyzer]:
                self.results[environment][analyzer][simulation] = []

            self.results[environment][analyzer][simulation].append(
                    self.analyzers[analyzer].analyze(
                        population = population,
                        setup = self.setups[simulation],
                        environment = self.environments[environment]))

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


def clear(clear_genes=False):
    Evaluation.objects.all().delete()
    Generation.objects.all().delete()
    Population.objects.all().delete()
    Individual.objects.all().delete()
    Chromosome.objects.all().delete()
    if clear_genes:
        Gene.objects.all().delete()

def simulate( num_pool, noise, num_pop, num_iter,
              episodes_factor, debug_mode=DEBUG, export_dir=None):
    debug("Start", debug_mode & DEBUG_PROG)
    clear(True)
    debug("Generated %d genes in the pool" % (num_pool,),
            debug_mode & DEBUG_VALUE)
    pool = Gene.factory(num_pool)
    solutions = gen_solutions(1, pool, MIN_SOL_LEN, MAX_SOL_LEN)
    debug("Generated solutions: %s" % (solutions,), debug_mode & DEBUG_PROG)
    fitness_fn = create_fitness_fn(solutions, noise)
    population = simulate_ga_loop(num_pop, num_iter, fitness_fn,
            episodes_factor, debug_mode)
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

def simulate_ga_loop( num_pop, num_iter, fitness_fn,
                      episodes_factor, debug_mode=DEBUG):
    # Init population
    population = init_population(num_pop)
    debug("Population initialized", debug_mode & DEBUG_STEP)
    # Fetch generation
    generation = population.current_generation()
    debug("Generation: %s" % ([x for x in generation.individuals.all()],),
            debug_mode & DEBUG_VALUE)
    simulate_evaluate_generation(generation, num_pop*episodes_factor,
            fitness_fn, debug_mode)
    debug("First generation evaluated", debug_mode & DEBUG_STEP)
    for i in range(num_iter-1):
        debug("Iteration %d" % (i+1,), debug_mode & DEBUG_PROG)
        generation = switch_generations(num_pop, population, debug_mode)
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
    for _ in range(int(episodes)):
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
