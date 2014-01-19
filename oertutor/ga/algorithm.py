from random import randrange
from copy import copy

def mutate(chromosome):
    return mutate_swap(chromosome)

def mutate_swap(chromosome):
    # Retrieve length of the chromosome
    length = chromosome.genes.count()
    # Make sure the chromosome has enough items to swap
    if length < 2:
        return False
    # Pick two random indexes
    g1 = randrange(length)
    g2 = randrange(length)
    # Ensure the two indexes are different
    while g2 == g1:
        g2 = randrange(length)
    # Retrieve gene1
    gene1 = chromosome.get_gene_by_index(g1)
    # Retrieve gene2
    gene2 = chromosome.get_gene_by_index(g2)
    # Copy chromosome to later mutate it
    mutation = copy(chromosome)
    # Swap genes
    mutation.swap_genes(gene1, gene2)
    # Set parent of new chromosome to the original
    mutation.parents.clear()
    mutation.parents.add(chromosome)
    return mutation
