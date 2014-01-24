from django.db import models
from datetime import datetime
from oertutor.ga.utils import pdf_sample
import random

class Gene(models.Model):
    apriori_value = models.IntegerField(default=0)

    @staticmethod
    def factory(num):
        """
        Factory takes number num and returns num new genes.
        """
        genes = []
        for _ in range(num):
            genes.append(Gene.objects.create())
        return genes

    @staticmethod
    def get_by_pks(primary_keys):
        """
        Retrieve a list of genes by their primary keys.

        Arguments:
          primary_keys - List of primary keys

        Raises:
          KeyError if one of the primary keys doesn't refer to a gene
          TypeError if the input is not a list of values

        Returns:
          A list of gene instances
        """
        if isinstance(primary_keys, list):
            genes = []
            for primary_key in primary_keys:
                try:
                    gene = Gene.objects.get(pk=primary_key)
                except Gene.DoesNotExist:
                    raise KeyError("Gene(%s) is not a known Gene" % primary_key)
                else:
                    genes.append(gene)
            return genes
        else:
            raise TypeError("Input must be a list of primary keys.")

    @staticmethod
    def random_choice(exclude=None):
        """
        Select a random Gene instance.
        Possibly after excluding a list of genes by their primary keys.

        Arguments:
          exclude - List of primary keys. Default: None.

        Raises:
          ValueError if there are no genes, or all genes are excluded.

        Returns:
          A randomly selected gene instance
        """
        if exclude is not None:
            genes = Gene.objects.exclude(pk__in=exclude)
        else:
            genes = Gene.objects.all()
        # There must be genes left to choose
        if len(genes) == 0:
            raise ValueError("No genes left to choose from.")
        return random.choice(genes)

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
        """
        Factory takes a list of genes as input and returns a chromosome
        instance that contains the provided genes. The genes are stored in the
        chromosome in the order of the provided list. Optionally a list of
        parents can be provided that will be linked to the new chromosome. The
        relationships between the genes and the chromosome are created in bulk.

        Arguments:
          genes - A list of genes
          parents - A list of parent chromosomes. Default: None.

        Returns:
          The created chromosome.
        """
        chromosome = Chromosome.objects.create(age=0)
        for index, gene in enumerate(genes):
            ChromosomeMembership.objects.create(
                    gene = gene,
                    chromosome = chromosome,
                    index = index)
        if parents is not None:
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
            # Generate all possible indices
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

    def fitness(self):
        fitness = Decimal(0)
        for generation in self.generations:
            fitness += generation.fitness(self)
        fitness /= len(self.generations)
        return fitness

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
        return self.__copy__()

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "%d::%s" % (self.pk, str([str(gene) for gene in
            self.genes.order_by("chromosomemembership__index")]))

class ChromosomeMembership(models.Model):
    gene = models.ForeignKey('Gene')
    chromosome = models.ForeignKey('Chromosome')
    index = models.PositiveIntegerField()

class Generation(models.Model):
    chromosomes = models.ManyToManyField('Chromosome',
            through='GenerationMembership', related_name='generations')

    @staticmethod
    def factory(chromosomes):
        """
        Factory takes a list of chromosomes as input and returns a generation
        containing those chromosomes.

        Arguments:
          chromosomes - List of chromosomes

        Returns:
          The created generation
        """
        generation = Generation.objects.create()
        for chromosome in chromosomes:
            GenerationMembership.objects.create(
                    chromosome=chromosome,
                    generation=generation)
        return generation

    def add_chromosomes(self, chromosomes):
        """
        Add a list of chromosomes to this generation.

        Arguments
          chromosomes - A list of chromosomes
        """
        for chromosome in chromosomes:
            GenerationMembership.objects.create(
                    chromosome=chromosome,
                    generation=self)

    def delete_chromosome(self, chromosome):
        """
        Delete a chromosome from the generation.

        Arguments:
          chromosome - The chromosome to be deleted.

        Raises:
          KeyError if the chromosome is not part of the generation.
        """
        try:
            mem = GenerationMembership.objects.get(chromosome=chromosome,
                    generation=self)
        except GenerationMembership.DoesNotExist:
            raise KeyError("Unknown chromosome in this generation.")
        else:
            mem.delete()

    def select_by_fitness_pdf(self, num, exclude=None):
        """
        Select num chromosomes from the generation with the pdf based on the
        fitness values of the chromosomes. Optionally a list of chromosomes can
        be excluded from the pool beforehand by their primary keys.

        Arguments:
          num - The number of samples.
          exclude - A list of primary keys to skip. Default: None.

        Returns:
          The list of num sampled chromosomes
        """
        if exclude is not None:
            members = GenerationMembership.objects.exclude(pk__in=exclude)
        else:
            members = GenerationMembership.objects.all()
        samples = pdf_sample(num, members,
                lambda x: x.fitness if x.fitness is not None else 0)
        return [sample.chromosome for sample in samples]

    def select_worst_chromosome(self, n=1):
        """
        Selects the n chromosomes in this generation with the worse fitness.

        Arguments:
          n - The number of chromosomes to return. Default: 1.

        Raises:
          KeyError is no chromosomes exist in this generation

        Returns:
          The worst chromosome of this generation
            or a list of the n worst chromosomes
        """
        try:
            mem = (GenerationMembership.objects
                    .filter(generation=self).order_by('fitness')[0:n])
        except IndexError:
            raise KeyError('No chromosomes exists in this generation')
        else:
            if n == 1:
                return mem[0].chromosome
            else:
                return [m.chromosome for m in mem]

    def select_best_chromosome(self, n=1):
        """
        Selects the n chromosomes in this generation with the best fitness.

        Arguments:
          n - The number of chromosomes to return. Default: 1.

        Raises:
          KeyError is no chromosomes exist in this generation

        Returns:
          The best chromosome of this generation
            or a list of the n best chromosomes
        """
        try:
            mem = (GenerationMembership.objects
                    .filter(generation=self).order_by('-fitness')[0:n])
        except GenerationMembership.DoesNotExist:
            raise KeyError('No chromosomes exists in this generation')
        else:
            if n == 1:
                return mem[0].chromosome
            else:
                return [m.chromosome for m in mem]

    def select_next_chromosome(self, honour_locks=True):
        """
        Select the next chromosome that has not been evaluated yet. The list is
        not ordered, since the order in which chromosomes are evaluated doesn't
        matter for the genetic algorithm, assuming all chromosomes need to be
        evaluated eventuall. By default it also honours locks, meaning that
        chromosomes that are locked will also not be chosen.
        This can be disabled.

        Arguments:
          honour_locks - Don't pick locked chromosomes. Default: True.

        Raises:
          ValueError if no chromosome is available anymore.

        Returns:
          The next chromosome that is available.
        """
        # Select all chromosomes that do not have a fitness value yet
        if honour_locks:
            mem = GenerationMembership.objects.filter(fitness=None, locked=None)
        else:
            mem = GenerationMembership.objects.filter(fitness=None)
        if len(mem) == 0:
            raise ValueError("No chromosome available in this generation.")
        else:
            return mem[0].chromosome

    def fitness(self, chromosome, fitness=None):
        """
        Set or retrieve the fitness value of a chromosome is this generation.

        To get the fitness of a chromosome:
        f = generation.fitness(chromosome)

        To set the fitness of a chromosome:
        generation.fitness(chromosome, f)

        Arguments:
          chromosome - A chromosome instance in this generation
          fitness - The fitness value, leave empty to get. Default: None.

        Returns:
          Either the fitness value or nothing
        """
        try:
            mem = GenerationMembership.objects.get(chromosome=chromosome,
                    generation=self)
        except GenerationMembership.DoesNotExist:
            raise KeyError("Chromosome is not a member of this generation.")
        else:
            if fitness is None:
                return mem.fitness
            else:
                mem.fitness = round(fitness, 9)
                mem.save()

    def lock_chromosome(self, chromosome):
        """
        Lock the chromosome to prevent it from being chosen twice. This could
        happen because the chromosomes could be presented to a user before
        evaluation can occur, this means that multiple asynchronous events
        could attempt to use the same chromosome. Chromosomes are locked within
        a particular generation.

        Arguments:
          chromosome - The chromosome to lock.
        """
        try:
            mem = GenerationMembership.objects.get(chromosome=chromosome,
                generation=self)
        except GenerationMembership.DoesNotExist:
            raise KeyError("Chromosome is not a member of this generation.")
        else:
            if mem.locked is not None:
                raise ValueError("Chromosome is already locked.")
            mem.locked = datetime.now()
            mem.save()

    def unlock_chromosome(self, chromosome):
        """
        Unlock the chromosome. See also `Generation.lock_chromosome'.

        Arguments:
          chromosome - The chromosome to unlock.
        """
        try:
            mem = GenerationMembership.objects.get(chromosome=chromosome,
                generation=self)
        except GenerationMembership.DoesNotExist:
            raise KeyError("Chromosome is not a member of this generation.")
        else:
            if mem.locked is None:
                raise ValueError("Chromosome is not locked.")
            mem.locked = None
            mem.save()

class GenerationMembership(models.Model):
    chromosome = models.ForeignKey('Chromosome')
    generation = models.ForeignKey('Generation')
    fitness = models.DecimalField(null=True, max_digits=10, decimal_places=9)
    locked = models.DateField(null=True)

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

    def current_generation(self):
        """
        Returns current generation by means of the primary key.
        """
        return self.generations.latest('pk')

    def next_generation(self, chromosomes=None):
        """
        Move to a new generation in this population. Optionally a list of
        chromosones can be provided as an initial set of individuals for that
        generation.

        Arguments:
          chromosomes - A list of chromosomes to include in the generation.
                        Default: None.

        Returns:
          The created new generation.
        """
        if chromosomes is None:
            generation = Generation.factory([])
        else:
            generation = Generation.factory(chromosomes)
        self.generations.add(generation)
        return generation

    def immigrate(self, immigrants):
        """
        Immigrate one of several immigrants into the population
        by replacing the worst chromosome. Selection is done on a wheel
        where the fitness score of an chromosome determines the surface.
        Arguments:
        immigrants - List of dictionaries,
                       containing the keys "fitness" and "chromosome"
        """
        # Select immigrant according to the PDF based on the fitness values
        immigrant = pdf_sample(1, immigrants,
                lambda x: x.fitness if x.fitness is not None else 0)
        # Select current generation
        generation = self.current_generation()
        # Select worst chromosome in that generation
        worst_chromosome = generation.select_worst_chromosome()
        # Remove the worst chromosome from the generation
        generation.delete_chromosome(worst_chromosome)
        # Immigrate the picked immigrant
        generation.add_chromosome(immigrant)

    def migrate(self):
        """
        Select the best chromosome to offer for migration
        """
        # Select current generation
        generation = self.current_generation()
        # Return best chromosome
        return generation.select_best_chromosome()
