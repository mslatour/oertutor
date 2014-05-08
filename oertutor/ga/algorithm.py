from copy import copy
from oertutor.ga.models import Population, Generation, Individual, \
        Chromosome, Gene
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga.utils import debug, DEBUG_VALUE, DEBUG_STEP, pdf_sample
from oertutor.ga.settings import *
from oertutor.ga import signals
import random

def init_population(num, population=None, genes=None):
    """
    Initialize a new population with a first generation. The generation
    consists of individuals with chromosomes of length 1.

    Arguments:
      num  - Number of individuals in each generation of the population.
      population - The population to init, default: a new one.
      genes - Genes to add to the population, default: all genes.

    Returns:
      The created or used population
    """
    if genes is None:
        if population is not None:
            genes = population.pool
        else:
            genes = Gene.objects.all()
    if population is None:
        population = Population.objects.create()
        for gene in genes:
            population.pool.add(gene)
        population.save()

    individuals = []
    # Mapping to lookup chromosomes by its gene member
    chromosomes_gene_map = {}
    n_genes = len(genes)
    # If there is enough room in the population for all the genes
    if len(genes) <= num:
        # Include each gene at least ones in the population
        for gene in genes:
            chromosome = Chromosome.factory([gene], population)
            chromosomes_gene_map[gene] = chromosome
            individuals.append(Individual.factory(chromosome))
        # Substract the number of added genes of the total number of
        # individuals to add in total for this generation.
        num -= n_genes
    # If the number of positions left to fill is bigger than zero
    if num > 0:
        # Determine sum apriori_value, for normalizing
        apriori_sum = sum([gene.apriori_value for gene in genes])
        # If the sum is zero, then take uniform sample
        if apriori_sum == 0:
            # For each position in the generation left to fill
            for _ in range(num):
                gene = random.choice(genes)
                # Append a individual with a chromosome containing the
                # uniformly sampled gene, try to fetch chromosome from mapping
                if gene in chromosomes_gene_map:
                    individuals.append(Individual.factory(
                        chromosomes_gene_map[gene]))
                else:
                    chromosome = Chromosome.factory([gene], population)
                    chromosomes_gene_map[gene] = chromosome
                    individuals.append(Individual.factory(chromosome))
        # If the sum is above zero, take sample according to the distribution
        # given by the apriori values of the genes.
        elif apriori_sum > 0:
            # For each position in the generation left to fill
            for _ in range(num):
                # Wheel pin
                pin = random.random()
                # Wheel turn
                turn = 0
                # Wheel section picked
                pick = None
                for gene in genes:
                    turn += float(gene.apriori_value)/apriori_sum
                    if turn >= pin:
                        pick = gene
                        break
                # Append a individual with a chromosome containing the
                # sampled gene, try to fetch chromosome from mapping
                if pick in chromosomes_gene_map:
                    individuals.append(Individual.factory(
                        chromosomes_gene_map[pick]))
                else:
                    chromosome = Chromosome.factory([pick], population)
                    chromosomes_gene_map[pick] = chromosome
                    individuals.append(Individual.factory(chromosome))
        else:
            raise ValueError('Sum of gene apriori values was negative.')
    # Add an initial generation to the population containing the sampled chromosomes.
    Generation.factory(individuals, population)
    return population

def switch_generations(num_pop, num_elite, p_mutate, population, DEBUG=0x0):
    # Fetch current generation
    generation = population.current_generation()
    # Elitism
    elite = list(generation.select_best_individuals(num_elite))
    debug("%d elite members: %s" % (len(elite), elite), DEBUG & DEBUG_VALUE)
    signals.ga_elite.send(sender=population, generation=generation,
            elite=elite)
    num_elites = len(elite)
    if num_elites >= num_pop:
        return population.next_generation(elite[:num_pop])

    # Survivor selection
    survivors = [copy(x) for x in generation.select_by_fitness_pdf(
        num_pop-num_elites)]
    debug("%d survivors: %s" % (len(survivors), survivors), DEBUG & DEBUG_VALUE)

    # Immigration
    immigrants = []
    for pop in population.neighbours.all():
        immigrants.append(pop.migrate())
    if len(immigrants) > 0:
        # Select worst individual
        worst_survivor = sorted(survivors, key=lambda s: s.chromosome.fitness)[0]
        # Select immigrant according to the PDF based on the fitness values
        immigrant = pdf_sample(1, immigrants+[worst_survivor],
                lambda x: max(x.fitness(),0))[0]
        if not immigrant.pk == worst_survivor.pk:
            index = survivors.index(worst_survivor)
            survivors.remove(worst_survivor)
            try:
                lookalike = Chromosome.get_by_genes(immigrant.chromosome, population)
            except ValueError as e:
                signals.ga_err.send(
                    sender=e,
                    msg=str(e),
                    location="ga.algorithm.immigrate")
            except ImpossibleException:
                pass
            else:
                immigrant.chromosome = lookalike
                immigrant.save()
            signals.ga_immigrate.send(sender=population, generation=generation,
                    worst_individual=worst_survivor, immigrant=immigrant)
        else:
            immigrant = None
    else:
        immigrant = None
    offspring = []
    mapping = {}
    # From the intermediate generation to the new generation
    for index in range(len(survivors)/2):
        parents = survivors[2*index:2*(index+1)]
        debug("Parents selected: %s" % (parents,), DEBUG & DEBUG_VALUE)
        try:
            childs, mapping = crossover(parents[0].chromosome,
                    parents[1].chromosome, population, mapping)
            offspring += childs
        except ImpossibleException:
            # If no children can be created, just keep the parents
            offspring += [p.chromosome for p in parents]

    # Add any individuals that have not mated as their own offspring, this will
    # happen when the number of survivors is an odd number
    offspring += [s.chromosome for s in survivors[len(offspring):]]

    if immigrant is None:
        nxt_generation = elite
    else:
        nxt_generation = elite+[immigrant]
    for member in offspring:
        if random.random() < p_mutate:
            try:
                mutation, mapping = mutate(member, population, mapping)
                nxt_generation.append(Individual.factory(mutation))
                debug("Mutate %s" % (member,), DEBUG & DEBUG_STEP)
            except ImpossibleException:
                nxt_generation.append(Individual.factory(member))
        else:
            nxt_generation.append(Individual.factory(member))

    # New generation
    generation = population.next_generation(nxt_generation[:num_pop])
    return generation

def test_validity(chromosome):
    return (
        len(set(chromosome)) == len(chromosome)
        and len(chromosome) >= MIN_LEN
        and len(chromosome) <= MAX_LEN)

def mutate(chromosome, population, mapping={}):
    functions = [mutate_swap, mutate_add, mutate_delete]
    while functions != []:
        func = random.choice(functions)
        try:
            mutation = func(chromosome, population)
        except ImpossibleException:
            functions.remove(func)
        else:
            if tuple(mutation) not in mapping:
                try:
                    new_chromosome = Chromosome.get_by_genes(mutation, population)
                    new_chromosome.parents.add(chromosome)
                    new_chromosome.save()
                except ValueError as e:
                    signals.ga_err.send(
                        sender=e,
                        msg=str(e),
                        location="ga.algorithm.mutate")
                except ImpossibleException:
                    # No match found
                    new_chromosome = Chromosome.factory(
                            mutation, population, [chromosome])
                    mapping[tuple(mutation)] = new_chromosome
                    return (new_chromosome, mapping)
                else:
                    mapping[tuple(mutation)] = new_chromosome
                    return (new_chromosome, mapping)
            else:
                new_chromosome = mapping[tuple(mutation)]
                new_chromosome.parents.add(chromosome)
                new_chromosome.save()
                return (new_chromosome, mapping)
    raise ImpossibleException

def mutate_swap(chromosome, population):
    """
    Perform a swap mutation on the chromosome by randomly selecting two
    distinct positions in the chromosome. The genes on the two positions in
    the chromosome are then swapped (i.e. the index property is swapped). The
    swap takes place in a copy of the input chromosome in order to have both.
    The new mutated chromosome is linked to the input chromosome via the parent
    property.

    Arguments:
      chromosome - The chromosome to be mutated, of at least length 2.

    Raises:
      ImpossibleException if the chromosome is not long enough

    Returns:
      mutated chromosome (copy)
    """
    # Retrieve length of the chromosome
    length = len(chromosome)
    # Make sure the chromosome has enough items to swap
    if length < 2:
        raise ImpossibleException
    # Pick two random indexes
    i = random.randrange(length)
    j = random.randrange(length)
    # Ensure the two indexes are different
    while j == i:
        j = random.randrange(length)
    # Fetch the list of genes from the chromosome
    genes = list(chromosome)
    # Swap genes
    genes[i] = chromosome[j]
    genes[j] = chromosome[i]
    return genes

def mutate_add(chromosome, population):
    """
    Perform an add mutation to the chromosome by adding a new gene to the
    chromosome from the pool. Genes in the chromosome are unique.

    Arguments:
      chromosome - The chomosome parent to mutate

    Raises:
      ImpossibleException if no gene can be selected to add that is not already
                          present or when the resulting mutate doesn't pass
                          the validity test.

    Returns:
      The created mutation
    """
    # Collect the primary keys of the genes already present
    exclude = [gene.pk for gene in chromosome]
    # Fetch population
    try:
        # Select a random gene that is not already present
        gene = population.random_pool_choice(exclude)
    except ValueError:
        raise ImpossibleException
    else:
        # Fetch the list of genes from the chromosome
        genes = list(chromosome)
        # Add randomly selected gene to the gene list
        genes.append(gene)
        if test_validity(genes):
            return genes
        else:
            raise ImpossibleException

def mutate_delete(chromosome, population):
    """
    Perform a delete mutation to the chromosome by removing a random gene from
    the chromosome.

    Arguments:
      chromosome - The chomosome parent to mutate

    Raises:
      ImpossibleException if the resulting mutate doesn't pass the validity test

    Returns:
      The created mutation
    """
    # Fetch the list of genes from the chromosome
    genes = list(chromosome)
    # Randomly select a gene from the gene list
    gene = random.choice(genes)
    # Remove randomly selected gene from the gene list
    genes.remove(gene)
    if test_validity(genes):
        return genes
    else:
        raise ImpossibleException

def crossover(parent1, parent2, population, mapping={}):
    """
    Crossover wrapper function that picks the crossover operation.
    """
    functions = [one_point_crossover, append_crossover]
    for func in functions:
        try:
            childs = func(parent1, parent2, population)
        except ImpossibleException:
            continue
        else:
            chromosomes = []
            for child in childs:
                if tuple(child) not in mapping:
                    try:
                        chromosome = Chromosome.get_by_genes(child, population)
                        chromosome.parents.add(parent1)
                        chromosome.parents.add(parent2)
                        chromosome.save()
                    except ValueError as e:
                        signals.ga_err.send(
                            sender=e,
                            msg=str(e),
                            location="ga.algorithm.crossover")
                    except ImpossibleException:
                        # No match found
                        chromosome = Chromosome.factory(child,
                                population, [parent1, parent2])
                        mapping[tuple(child)] = chromosome
                        chromosomes.append(chromosome)
                    else:
                        mapping[tuple(child)] = chromosome
                        chromosomes.append(chromosome)
                else:
                    chromosomes.append(mapping[tuple(child)])
            return (chromosomes, mapping)
    raise ImpossibleException

def append_crossover(parent1, parent2, population):
    """
    Perform an append crossover by appending the genes of both parents in the
    two possible orderings. The resulting childs are checked by test_validity.

    Arguments:
      parent1 - Chromosome
      parent2 - A different chromosome (although this is not checked)

    Raises:
      ImpossibleException if no valid chromosomes could be created

    Returns:
      A tuple of two new chromosomes
    """
    # Retrieve genes from parents
    genes1 = list(parent1)
    genes2 = list(parent2)
    # Construct the sequences of genes for both children
    child1 = genes1+genes2
    child2 = genes2+genes1
    if test_validity(child1) and test_validity(child2):
        return (child1, child2)
    else:
        raise ImpossibleException

def one_point_crossover(parent1, parent2, population):
    """
    Perform a one point crossover operation for two parents that could differ
    in length. Because of that, a different point is chosen in each parent that
    is guaranteed to fall within the length of the parent. After randomly
    selecting the points, both parents are split up in two parts each. These
    parts are then recombined into two new children, while maintaining the
    relative position of the parts (i.e. the first part of each child was
    the first part of one of the parents).

    The implementation actually generates all possible combinations that adhere
    to the constraints given by test_validity. A random selection is then made
    from the list of valid candidates.

    Arguments:
      parent1 - Chromosome
      parent2 - A different chromosome (although this is not checked)

    Raises:
      ImpossibleException if no valid chromosomes could be created

    Returns:
      A tuple of two new chromosomes
    """
    candidates = []
    for i in range(1, len(parent1)):
        for j in range(1, len(parent2)):
            # Split up genes
            child1 = parent1[:i]+parent2[j:]
            child2 = parent2[:j]+parent1[i:]
            if test_validity(child1) and test_validity(child2):
                candidates.append((child1, child2))
    if candidates == []:
        raise ImpossibleException
    elif len(candidates) == 1:
        # Convert lists of genes to chromosome instances
        return (candidates[0][0], candidates[0][1])
    else:
        candidate = random.choice(candidates)
        return (candidate[0], candidate[1])
