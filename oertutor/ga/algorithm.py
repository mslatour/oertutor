from copy import copy
from oertutor.ga.models import Chromosome, Gene, Population
from oertutor.ga.exceptions import ImpossibleException

import random

def init_population(num, cls=Gene):
    """
    Initialize a new population with a first generation. The generation
    consists of chromosomes of length 1.

    Arguments:
      num  - Number of chromosomes in each generation of the population.
      cls  - Class, the model of the genes. Default: Gene

    Returns:
      The created population
    """
    chromosomes = []
    genes = cls.objects.all()
    n_genes = len(genes)
    # If there is enough room in the population for all the genes
    if len(genes) <= num:
        # Include each gene at least ones in the population
        for gene in genes:
            chromosomes.append(Chromosome.factory([gene]))
        # Substract the number of added genes of the total number of
        # chromosomes to add in total for this generation.
        num -= n_genes
    # If the number of positions left to fill is bigger than zero
    if num > 0:
        # Determine sum apriori_value, for normalizing
        apriori_sum = sum([gene.apriori_value for gene in genes])
        # If the sum is zero, then take uniform sample
        if apriori_sum == 0:
            # For each position in the generation left to fill
            for _ in range(num):
                # Append a chromosome with a uniformly sampled gene
                chromosomes.append(Chromosome.factory(
                    [random.choice(genes)]))
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
                # Append a chromosome with the sampled gene
                chromosomes.append(Chromosome.factory([pick]))
        else:
            raise ValueError('Sum of gene apriori values was negative.')
    # Create and return a new population with an initial generation containing
    # the sampled chromosomes.
    return Population.factory(chromosomes)

def test_validity(chromosome):
    return len(set(chromosome)) == len(chromosome)

def mutate(chromosome):
    functions = [mutate_swap, mutate_add]
    while functions != []:
        fn = random.choice(functions)
        try:
            mutation = fn(chromosome)
        except ImpossibleException:
            functions.remove(fn)
        else:
            return mutation
    raise ImpossibleException

def mutate_swap(chromosome):
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
    # Copy chromosome to later mutate it
    mutation = copy(chromosome)
    # Swap genes
    mutation.swap_genes(mutation[i], mutation[j])
    # Set parent of the mutation to the original
    mutation.parents.clear()
    mutation.parents.add(chromosome)
    return mutation

def mutate_add(chromosome):
    """
    Perform an add mutation to the chromosome by adding a new gene to the
    chromosome from the pool. Genes in the chromosome are unique.
    """
    # Collect the primary keys of the genes already present
    exclude = [gene.pk for gene in chromosome]
    try:
        # Select a random gene that is not already present
        gene = Gene.random_choice(exclude)
    except ValueError as e:
        raise ImpossibleException
    else:
        # Copy chromosome to later mutate it
        mutation = copy(chromosome)
        # Add randomly selected gene to the chromosome
        # Note: the append check need not be performed in this case
        mutation.append_gene(gene, False)
        return mutation

def crossover(parent1, parent2):
    """
    Crossover wrapper function that picks the crossover operation.
    """
    functions = [one_point_crossover, append_crossover]
    for fn in functions:
        try:
            childs = fn(parent1, parent2)
        except ImpossibleException:
            continue
        else:
            return childs
    raise ImpossibleException

def append_crossover(parent1, parent2):
    """
    Perform an append crossover by appending the genes of both parents in the
    two possible ordernings. The resulting childs are checked by test_validity.

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
    # Create children
    child1 = Chromosome.factory(genes1+genes2, [parent1, parent2])
    child2 = Chromosome.factory(genes2+genes1, [parent1, parent2])
    if test_validity(child1) and test_validity(child2):
        return (child1, child2)
    else:
        raise ImpossibleException

def one_point_crossover(parent1, parent2):
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
        child1 = Chromosome.factory(candidates[0][0], [parent1, parent2])
        child2 = Chromosome.factory(candidates[0][1], [parent1, parent2])
        return (child1,child2)
    else:
        candidate = random.choice(candidates)
        # Convert lists of genes to chromosome instances
        child1 = Chromosome.factory(candidate[0], [parent1, parent2])
        child2 = Chromosome.factory(candidate[1], [parent1, parent2])
        return (child1,child2)
