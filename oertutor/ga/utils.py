from oertutor.ga.models import *

def gene_factory(n):
    genes = []
    for i in range(n):
        genes.append(Gene(name="Gene %d" % (i,)))
    Gene.objects.bulk_create(genes)
    return genes

def retrieve_genes_by_name(names):
    genes = []
    for name in names:
        genes.append(Gene.objects.get(name=name))
    return genes

def chromosome_factory(genes):
    chromosome = Chromosome.objects.create(age=0)
    for index, gene in enumerate(genes):
        ChromosomeMembership.objects.create(
                gene = gene,
                chromosome = chromosome,
                index = index
        )
    return chromosome
