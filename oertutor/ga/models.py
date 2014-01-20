from django.db import models
from random import random

class Gene(models.Model):
    apriori_value = models.IntegerField(default=0)

    @staticmethod
    def factory(num):
        """
        Factory takes number num and returns num new genes.
        Genes are created in bulk.
        """
        genes = []
        for i in range(num):
            genes.append(Gene())
        Gene.objects.bulk_create(genes)
        return genes

    @staticmethod
    def get_by_pks(pks):
        if isinstance(pks, list):
            genes = []
            for pk in pks:
                try:
                    gene = Gene.objects.get(pk=pk)
                except Gene.DoesNotExist:
                    raise KeyError("Gene(%s) is not a known Gene" % pk)
                else:
                    genes.append(gene)
            return genes
        else:
            raise TypeError("Input must be a list of primary keys.")

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.pk)

class Chromosome(models.Model):
    genes = models.ManyToManyField('Gene', through='ChromosomeMembership',
            related_name='chromosomes')
    age = models.PositiveIntegerField(default=0)
    parents = models.ManyToManyField('self', related_name='children')

    @staticmethod
    def factory(genes, parents=None):
        # Set default value for parents, if not provided.
        parents = [] if parents is None else parents
        chromosome = Chromosome.objects.create(age=0)
        for index, gene in enumerate(genes):
            ChromosomeMembership.objects.create(
                    gene = gene,
                    chromosome = chromosome,
                    index = index
            )
        for parent in parents:
            chromosome.parents.add(parent)
        chromosome.save()
        return chromosome

    def __len__(self):
        return self.genes.all().count()

    def __getitem__(self, key):
        if isinstance(key, int):
            try:
                gene = self.genes.get(chromosomemembership__index=key)
            except Gene.DoesNotExist:
                raise KeyError("There is no gene at index %d." % (key,))
            else:
                return gene
        elif isinstance(key, slice):
            genes = []
            # Generata all possible indices
            indices = range(len(self))
            # Loop through a slice of the indices
            for index in indices[key]:
                genes.append(self[index])
            return genes
        else:
            raise TypeError("Key should be an integer")

    def __iter__(self):
        return self.genes.order_by("chromosomemembership__index").iterator()

    def swap_genes(self, gene1, gene2):
        """
        Swap the positions of gene1 and gene2
        Arguments:
          gene1 - Gene instance that is a member of this chromosome.
          gene2 - Gene instance that is a member of this chromosome.
        """
        # Fetch memberships of gene1 and gene2
        try:
            gene1_mem = ChromosomeMembership.objects.get(
                    chromosome=self, gene=gene1)
            gene2_mem = ChromosomeMembership.objects.get(
                    chromosome=self, gene=gene2)
        except ChromosomeMembership.DoesNotExist:
            return False
        # Swap index propery of gene1 and gene2 with XOR swap algorithm
        gene1_mem.index = gene1_mem.index ^ gene2_mem.index
        gene2_mem.index = gene1_mem.index ^ gene2_mem.index
        gene1_mem.index = gene1_mem.index ^ gene2_mem.index
        # Save changes to gene1 and gene2 memberships
        gene1_mem.save()
        gene2_mem.save()
        return True

    def replace_gene(self, gene1, gene2, check=True):
        """
        Replace gene1 with gene2
        Arguments:
          gene1 - Gene instance that is a member of this chromosome.
          gene2 - Gene instance that is not a member of this chromosome.
          check - Boolean indicating if membership should be checked.
        """
        # If membership should be checked
        if check:
            # Note: membership of gene1 need not be check here, as it will be
            # checked by the try-except block. So only check for gene2.
            # Gene2 must not be a member, or else return False
            if self.genes.filter(chromosomemembership__gene=gene2).count():
                return False
        # Delete gene1
        try:
            mem = ChromosomeMembership.objects.get(chromosome=self, gene=gene1)
        except Gene.DoesNotExist:
            return False
        else:
            # Store index of gene1
            index = mem.index
            # Delete gene1 from the chromosome
            mem.delete()
        # Add gene2 at the index of gene1
        ChromosomeMembership.objects.create(
                gene = gene2,
                chromosome = self,
                index = index
        )
        return True

    def append_gene(self, gene, check=True):
        """
        Add gene to this chromosome
        Arguments:
          gene - Gene instance that is not a member of this chromosome.
          check - Boolean indicating if membership should be checked.
        """
        # If membership should be checked
        if check:
            # Gene must not be a member, or else return False
            if self.genes.filter(chromosomemembership__gene=gene).count():
                return False
        # Set new index to length of this chromosome before addition
        index = self.genes.count()
        # Add gene at new index
        ChromosomeMembership.objects.create(
                gene = gene,
                chromosome = self,
                index = index
        )
        return True

    def delete_gene(self, gene, shift=True):
        """
        Delete gene from this chromosome
        Arguments:
          gene - Gene instance that is a member of this chromosome.
          shift - Boolean indicating if the genes after the delete gene should
                  be automatically shiften back one index.
        """
        # Delete gene
        try:
            mem = ChromosomeMembership.objects.get(chromosome=self, gene=gene)
        except Gene.DoesNotExist:
            return False
        else:
            # Store index of gene in this chromosome
            index = mem.index
            # Delete gene from the chromosome
            mem.delete()
        # If auto shifting
        if shift:
            others = ChromosomeMembership.objects.filter(chromosome=self,
                    index__gt=index)
            for other in others:
                other.index -= 1
                other.save()
        return True

    def __copy__(self):
        # Create a chromosome with the same age
        copy = Chromosome.objects.create(age=self.age)
        # Add the same genes to the new chromosome
        for member in ChromosomeMembership.objects.filter(chromosome=self):
            ChromosomeMembership.objects.create(
                    gene = member.gene,
                    chromosome = copy,
                    index = member.index
            )
        # Add the same parents to the new chromosome
        for parent in self.parents.all():
            copy.parents.add(parent)
        return copy

    def __deepcopy__(self):
        self.__copy__(self)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return str([str(gene) for gene in
            self.genes.order_by("chromosomemembership__index")])

class ChromosomeMembership(models.Model):
    gene = models.ForeignKey('Gene')
    chromosome = models.ForeignKey('Chromosome')
    index = models.PositiveIntegerField()

class Generation(models.Model):
    chromosomes = models.ManyToManyField('Chromosome',
            through='GenerationMembership')

    @staticmethod
    def factory(chromosomes):
        generation = Generation.objects.create()
        for chromosome in chromosomes:
            GenerationMembership.objects.create(
                    chromosome=chromosome,
                    generation=generation
            )
        return generation

    def select_worst_chromosome(self):
        return (self.chromosomes.values('chromosome')
                .aggregate(models.Min('fitness')))

    def select_best_chromosome(self):
        return (self.chromosomes.values('chromosome')
                .aggregate(models.Max('fitness')))

    def delete_chromosome(self, chromosome):
        try:
            mem = GenerationMembership.objects.get(chromosome=chromosome,
                    generation=self)
        except GenerationMembership.DoesNotExist:
            raise ValueError("Unknown chromosome in this generation.")
        else:
            mem.delete()

class GenerationMembership(models.Model):
    chromosome = models.ForeignKey('Chromosome')
    generation = models.ForeignKey('Generation')
    fitness = models.DecimalField(null=True, max_digits=10, decimal_places=9)

class Population(models.Model):
    generations = models.ManyToManyField('Generation')

    @staticmethod
    def factory(chromosomes):
        """
        Factory that takes a list of chromosomes (chromosomes) as input and
        returns a population with a first generation that contains these
        chromosomes.
        """
        population = Population.objects.create()
        generation = Generation.factory(chromosomes)
        population.generations.add(generation)
        return population

    def immigrate(self, immigrants):
        """
        Immigrate one of several immigrants into the population
        by replacing the worst chromosome. Selection is done on a wheel
        where the fitness score of an chromosome determines the surface.
        Arguments:
        immigrants - List of dictionaries,
                       containing the keys "fitness" and "chromosome"
        """
        # Determine sum fitness, for normalizing
        fitness_sum = sum([immigrant.fitness if immigrant is not None else 0 \
                for immigrant in immigrants])
        # Sum must be a nonzero and positive number
        if not fitness_sum > 0:
            raise ValueError("Sum fitness of immigrants should be above zero.")
        # Wheel pin
        pin = random()
        # Wheel turn
        turn = 0
        # Wheel section picked
        pick = None
        for immigrant in immigrants:
            turn += float(immigrant.fitness)/fitness_sum
            if turn >= pin:
                pick = immigrant
                break
        # Select current generation
        generation = self.generations.latest('pk')
        # Select worst chromosome in that generation
        worst_chromosome = generation.select_worst_chromosome()
        # Remove the worst chromosome from the generation
        generation.delete_chromosome(worst_chromosome)
        # Immigrate the picked immigrant
        generation.add_chromosome(pick)

    def migrate(self):
        """
        Select the best chromosome to offer for migration
        """
        # Select current generation
        generation = self.generations.latest('pk')
        # Return best chromosome
        return generation.select_best_chromosome()
