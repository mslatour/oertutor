from django.db import models
from datetime import datetime
from oertutor.ga.utils import pdf_sample
from oertutor.ga.exceptions import ImpossibleException
from oertutor.ga import signals
from copy import deepcopy
import random

class Gene(models.Model):#{{{
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
        return "<%s: %s>" % (self.__class__.__name__, self.pk)#}}}

class Chromosome(models.Model):#{{{
    genes = models.ManyToManyField('Gene', through='ChromosomeMembership',
            related_name='chromosomes')
    parents = models.ManyToManyField('self', related_name='children')
    fitness = models.DecimalField(null=True, max_digits=10, decimal_places=9)
    age = models.PositiveIntegerField(default=0)

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

    @staticmethod
    def get_by_genes(genes):
        """
        Lookup the chromosome instance that has the given list of genes. In
        order to be a match, a chromosome need to have the exact same genes on
        the same locations and no additional genes.

        Raises:
          ImpossibleException if no chromosome could be matched

        Returns:
          The matched chromosome
        """
        # Define base query
        base_query = ChromosomeMembership.objects
        # Shortlist container for promising candidates
        shortlist = None
        # Fetch candidates for each gene membership
        for index, gene in enumerate(genes):
            candidates = [mem.chromosome for mem in
                    base_query.filter(gene=gene, index=index)]
            if shortlist is None:
                shortlist = candidates
            else:
                # For all currently found lookalikes
                for lookalike in list(shortlist):
                    # If they are not similar for this gene
                    if lookalike not in candidates:
                        # Remove them from the list of lookalikes
                        shortlist.remove(lookalike)
        # Make sure no supersets are kept
        length = len(genes)
        shortlist = filter(lambda x: len(x)==length, shortlist)
        #TODO: ensure that the chromosomes exist in this population
        # If there are no lookalikes left that met every criteria
        if len(shortlist) == 0:
            raise ImpossibleException('No matches found.')
        elif len(shortlist) > 1:
            raise ValueError("Multiple matches found for %s" %
                    (genes,))
        else:
            return shortlist[0]

    @staticmethod
    def merge_lookalike(chromosome):
        """
        This method tries to find a lookalike of the provided chromosome
        based on the gene configuration and merges them both by replacing all
        references in all tables with the provided chromosome. If no lookalike
        can be found then an exception is raised. It is assumed that the
        chromosome provided is not evaluated yet. If multiple lookalikes are
        found then an exception is raised.

        Raises:
          ImpossibleException if there are no lookalikes.
          ValueError if there are multiple lookalikes
        """
        # Define base query
        base_query = ChromosomeMembership.objects.exclude(
                chromosome=chromosome)
        # Fetch gene memberships
        members = ChromosomeMembership.objects.filter(chromosome=chromosome)
        # Shortlist container for promising candidates
        shortlist = None
        # Fetch candidates for each gene membership
        for mem in members:
            candidates = [mem.chromosome for mem in
                    base_query.filter(gene=mem.gene, index=mem.index)]
            if shortlist is None:
                shortlist = candidates
            else:
                # For all currently found lookalikes
                for lookalike in list(shortlist):
                    # If they are not similar for this gene
                    if lookalike not in candidates:
                        # Remove them from the list of lookalikes
                        shortlist.remove(lookalike)
        # Make sure no supersets are kept
        length = len(members)
        lookalikes = filter(lambda x: len(x)==length, shortlist)
        # If there are no lookalikes left that met every criteria
        if len(lookalikes) == 0:
            raise ImpossibleException('No lookalikes found.')
        elif len(lookalikes) > 1:
            raise ValueError("Multiple lookalikes found for %s" %
                    (chromosome,))
        else:
            lookalike = lookalikes[0]
            chromosome.age = lookalike.age
            chromosome.fitness = lookalike.fitness
            chromosome.save()
            # Update chromosome references in individuals
            Individual.objects.filter(chromosome=lookalike).update(
                    chromosome=chromosome)
            if lookalike.age > 0:
                # Update chromosome references in evaluations
                Evaluation.objects.filter(chromosome=lookalike).update(
                        chromosome=chromosome)
                # Update chromosome references in generation memberships
                GenerationMembership.objects.filter(chromosome=lookalike).\
                        update(chromosome=chromosome)
            # Delete lookalike which also deletes gene membership entries
            lookalike.delete()

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

    def __copy__(self):
        # Create a chromosome with the same age
        copy = Chromosome.objects.create(age=self.age, fitness=self.fitness)
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
            self.genes.order_by("chromosomemembership__index")]))#}}}

class ChromosomeMembership(models.Model):#{{{
    gene = models.ForeignKey('Gene')
    chromosome = models.ForeignKey('Chromosome')
    index = models.PositiveIntegerField()#}}}

class Individual(models.Model):#{{{
    chromosome = models.ForeignKey('Chromosome')
    locked = models.DateField(null=True)

    @staticmethod
    def factory(chromosome):
        return Individual.objects.create(chromosome=chromosome)

    @staticmethod
    def release_oldest_lock():
        obj = Individual.objects.exclude(locked=None).order_by('locked')
        try:
            obj.unlock()
        except ImpossibleException:
            pass

    def fitness(self, generation=None):
        """
        Return the fitness value of this individual. The fitness is defined as
        the average of the fitness values observed for the chromosome linked to
        this individual. If a specific generation was provided, the average
        fitness of the related chromosome in that generation is returned.
        Otherwise the fitness is averaged over all observations over time.

        Arguments:
          generation - The generation instance in which the fitness value needs
                       to have been observed. Default: None.

        Returns:
          The average fitness value of the related chromosome within the given
          scope.
        """
        return Evaluation.fitness(chromosome=self.chromosome, generation=generation)

    def lock(self):
        """
        Lock the individual to prevent it from being chosen twice. This could
        happen because the individual could be presented to a user before
        evaluation can occur, this means that multiple asynchronous events
        could attempg to use the same chromosome. Individual are locked within
        a particular generation.

        Raises:
          ImpossibleException if this individual is already locked.
        """
        now = datetime.now()
        updated = Individual.objects.filter(
                pk=self.pk, locked__isnull=True).update(locked=now)
        if updated == 0:
            raise ImpossibleException("Individual is already locked.")
        else:
            # Make sure the local copy is also updated
            self.locked = now

    def unlock(self):
        """
        Unlock the individual. See also `Individual.lock'.

        Raises:
          ImpossibleException if this individual is not locked.
        """
        updated = Individual.objects.filter(
                pk=self.pk, locked__isnull=False).update(locked=None)
        if updated == 0:
            raise ImpossibleException("Individual is already unlocked.")
        else:
            # Make sure the local copy is also updated
            self.locked = None

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.chromosome)

    def __getitem__(self, key):
        return self.chromosome[key]

    def __iter__(self):
        return iter(self.chromosome)

    def __repr__(self):
        return "%d::{%s}" % (self.pk, self.chromosome)

    def __deepcopy__(self):
        return Individual.factory(deepcopy(self.chromosome))

    def __copy__(self):
        return Individual.factory(self.chromosome)#}}}

class Evaluation(models.Model):#{{{
    chromosome = models.ForeignKey('Chromosome', related_name='+')
    individual = models.ForeignKey('Individual', related_name='+')
    generation = models.ForeignKey('Generation', related_name='+')
    population = models.ForeignKey('Population', related_name='+')
    #TODO link to student
    value = models.DecimalField(null=True, max_digits=10, decimal_places=9)

    @staticmethod
    def factory(generation, individual, fitness):
        chromosome = individual.chromosome
        Evaluation.objects.create(
                generation=generation,
                individual=individual,
                chromosome=chromosome,
                population=generation.population,
                value=fitness)
        # Fetch aggregated fitness of the chromosome
        aggregate = Evaluation.fitness(chromosome=chromosome,
                population=generation.population)
        GenerationMembership.objects.filter(
                chromosome=chromosome,
                generation=generation).update(
                        fitness=aggregate,
                        age=models.F('age')+1)
        chromosome.age = chromosome.age + 1
        chromosome.fitness = aggregate
        chromosome.save()

    @staticmethod
    def fitness(**filters):
        objs = Evaluation.objects.filter(**filters)
        return objs.aggregate(avg=models.Avg('value'))['avg']

#}}}

class GenerationMembership(models.Model):#{{{
    individual = models.ForeignKey('Individual')
    chromosome = models.ForeignKey('Chromosome')
    generation = models.ForeignKey('Generation')
    fitness = models.DecimalField(null=True, max_digits=10, decimal_places=9)
    age = models.PositiveIntegerField(default=0)
#}}}

class Generation(models.Model):#{{{
    individuals = models.ManyToManyField('Individual',
        through='GenerationMembership', related_name='+')
    population = models.ForeignKey('Population', related_name='generations')

    @staticmethod
    def factory(individuals, population):
        """
        Factory takes a list of individuals as input and returns a generation
        containing those individuals.

        Arguments:
          individuals - List of individuals.

        Returns:
          The created generation
        """
        generation = Generation.objects.create(population=population)
        generation.add_individuals(individuals)
        return generation

    def add_chromosomes(self, chromosomes):
        """
        Add a list of chromosomes to this generation in the form of
        individuals.

        Arguments
          chromosomes - A list of chromosomes
        """
        self.add_individuals([Individual.factory(c) for c in chromosomes])

    def add_individuals(self, individuals):
        """
        Add a list of individuals to this generation.

        Arguments
          individuals - A list of individuals
        """
        for individual in individuals:
            GenerationMembership.objects.create(
                    individual=individual,
                    generation=self,
                    chromosome=individual.chromosome,
                    fitness=individual.chromosome.fitness,
                    age=individual.chromosome.age
            )

    def delete_individual(self, individual):
        """
        Delete a individual from the generation.

        Arguments:
          individual - The individual to be deleted.

        Raises:
          KeyError if the individual is not part of the generation.
        """
        try:
            mem = GenerationMembership.objects.get(individual=individual,
                    generation=self)
        except GenerationMembership.DoesNotExist:
            raise KeyError("Unknown individual in this generation.")
        else:
            mem.delete()

    def select_by_fitness_pdf(self, num, exclude=None):
        """
        Select num individual from the generation with the pdf based on the
        fitness values of the individual. Optionally a list of individuals can
        be excluded from the pool beforehand by their primary keys.

        Arguments:
          num - The number of samples.
          exclude - A list of primary keys to skip. Default: None.

        Returns:
          The list of num sampled individuals
        """
        if exclude is not None:
            members = GenerationMembership.objects.exclude(pk__in=exclude)
        else:
            members = GenerationMembership.objects
        # Only look at individuals in this generation
        members = members.filter(generation=self)
        samples = pdf_sample(num, members,
                lambda x: x.fitness if x.fitness is not None else 0)
        return [sample.individual for sample in samples]

    def select_best_individuals(self, num=1):
        """
        Selects the num best individuals in this generation.

        Arguments:
          num - The number of individuals to return. Default: 1.

        Returns:
          The list of the num best individuals.
        """
        return  self.individuals.order_by(
                '-generationmembership__fitness')[0:num]

    def select_worst_individuals(self, num=1):
        """
        Selects the n worst individuals in this generation.

        Arguments:
          num - The number of individuals to return. Default: 1.

        Returns:
          The worst individual of this generation
            or a list of the n worst individuals depending on num.
        """
        individuals = self.individuals.order_by(
                'generationmembership__fitness')[0:num]
        if num == 1:
            return individuals[0]
        else:
            return individuals

    def select_next_individual(self, honour_locks=True):
        """
        Select the next individual using USB-1.
        By default it also honours locks, meaning that
        individuals that are locked will also not be chosen.
        This can be disabled.

        Arguments:
          honour_locks - Don't pick locked individuals. Default: True.

        Raises:
          ImpossibleException if no unlocked individual is available.

        Returns:
          The next individual to be evaluated.
        """
        # Select all individuals that do not have a fitness value yet
        members = GenerationMembership.objects.filter(generation=self)
        if honour_locks:
            # Further demand the individual to not be locked
            members.filter(individual__locked=None)
        if len(members) == 0:
            raise ImpossibleException("No individual available in this generation.")
        else:
            # Order the individuals by the UCB value
            try:
                sorted_members = sorted(members, key=
                    lambda x: (x.fitness + (1/x.age)) if x.age > 0 else 'Inf',
                    reverse=True)
            except Exception as e:
                print members
                for member in members:
                    print member.pk, member.age, member.fitness, member.individual
                raise e
            return sorted_members[0].individual

    def fitness(self, individual, fitness=None):
        """
        Set or retrieve the fitness value of an individual in this generation.
        The fitness is retrieved using the Evaluation.fitness method.

        To get the fitness of an individual:
        f = generation.fitness(individual)

        To set the fitness of an individual:
        generation.fitness(individual, f)

        Arguments:
          individual - An individual instance in this generation
          fitness - The fitness value, leave empty to get. Default: None.

        Returns:
          Either the fitness value or nothing
        """
        if fitness is None:
            return GenerationMembership.objects.get(generation=self,
                    individual=individual).fitness
        else:
            Evaluation.factory(self, individual, fitness)
#}}}

class Population(models.Model):#{{{
    pool = models.ManyToManyField('Gene', null=True, related_name='+')

    @staticmethod
    def factory(individuals):
        """
        Factory that takes a list of individuals as input and returns a
        population with a first generation that contains these individuals.
        """
        population = Population.objects.create()
        generation = Generation.factory(individuals, population)
        return population

    def random_pool_choice(self, exclude=None):
        """
        Select a random Gene instance from the pool.
        Possibly after excluding a list of genes by their primary keys.

        Arguments:
          exclude - List of primary keys. Default: None.

        Raises:
          ValueError if there are no genes, or all genes are excluded.

        Returns:
          A randomly selected gene instance
        """
        if exclude is not None:
            genes = self.pool.exclude(pk__in=exclude)
        else:
            genes = self.pool.all()
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

    def current_generation(self):
        """
        Returns current generation by means of the primary key.
        """
        return self.generations.latest('pk')

    def next_generation(self, individuals=None):
        """
        Move to a new generation in this population. Optionally a list of
        individuals can be provided as an initial set of individuals for that
        generation.

        Arguments:
          individuals - A list of individuals to include in the generation.
                        Default: None.

        Returns:
          The created new generation.
        """
        if individuals is None:
            generation = Generation.factory([], self)
        else:
            generation = Generation.factory(individuals, self)
        signals.ga_next_generation.send(sender=self, generation=generation)
        return generation

    def immigrate(self, immigrants):
        """
        Immigrate one of several immigrants into the population
        by replacing the worst individual. Selection is done on a wheel
        where the fitness score of an individual determines the surface.
        Arguments:
        immigrants - List of dictionaries,
                       containing the keys "fitness" and "individual"
        """
        # Select immigrant according to the PDF based on the fitness values
        immigrant = pdf_sample(1, immigrants,
                lambda x: x.fitness if x.fitness is not None else 0)
        # Select current generation
        generation = self.current_generation()
        # Select worst individual in that generation
        worst_individual = generation.select_worst_individuals()
        # Remove the worst individual from the generation
        generation.delete_individual(worst_individual)
        # Immigrate the picked immigrant
        generation.add_individuals([immigrant])
        signals.ga_immigrate.send(sender=self, generation=generation,
                worst_individual=worst_individual, immigrant=immigrant)

    def migrate(self):
        """
        Select the best chromosome to offer for migration
        """
        # Select current generation
        generation = self.current_generation()
        # Return best chromosome
        return generation.select_best_individuals()[0]#}}}
