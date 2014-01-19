from random import randrange
from copy import copy
from oertutor.ga.models import Chromosome

def mutate(chromosome):
    return mutate_swap(chromosome)

def mutate_swap(chromosome):
    # Retrieve length of the chromosome
    length = len(chromosome)
    # Make sure the chromosome has enough items to swap
    if length < 2:
        raise ValueError("Chromosome must have length of two or more.")
    # Pick two random indexes
    g1 = randrange(length)
    g2 = randrange(length)
    # Ensure the two indexes are different
    while g2 == g1:
        g2 = randrange(length)
    # Copy chromosome to later mutate it
    mutation = copy(chromosome)
    # Swap genes
    mutation.swap_genes(mutation[g1], mutation[g2])
    # Set parent of the mutation to the original
    mutation.parents.clear()
    mutation.parents.add(chromosome)
    return mutation

def crossover(parent1, parent2):
    # Randomly pick crossover point for parent1
    p1 = randrange(1,len(parent1))
    # Randomly pick crossover point for parent2
    p2 = randrange(1,len(parent2))
    # Split up genes
    genes11 = parent1[:p1]
    genes12 = parent1[p1:]
    genes21 = parent2[:p2]
    genes22 = parent2[p2:]
    # Create children
    child1 = Chromosome.factory(genes11+genes22, [parent1, parent2])
    child2 = Chromosome.factory(genes21+genes12, [parent1, parent2])
    return (child1, child2)
