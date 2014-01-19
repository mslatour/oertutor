from django.db import models

class Gene(models.Model):
    name = models.CharField(max_length=255)

    @staticmethod
    def factory(n):
        """
        Factory takes number n and returns n new genes.
        Each gene i is named according to the template "Gene %d" % (i,)
        Genes are created in bulk.
        """
        genes = []
        for i in range(n):
            genes.append(Gene(name="Gene %d" % (i,)))
        Gene.objects.bulk_create(genes)
        return genes

    @staticmethod
    def get_by_name(names):
        if isinstance(names, list):
            genes = []
            for name in names:
                if not isinstance(name, str):
                    raise TypeError("Input must be of type string or "+
                            "list of strings.")
                try:
                    gene = Gene.objects.get(name=name)
                except Gene.DoesNotExist:
                    raise KeyError("Key [%s] is not a known Gene" % (name))
                else:
                    genes.append(gene)
            return genes
        elif isinstance(names, str):
            try:
                gene = Gene.objects.get(name=names)
            except Gene.DoesNotExist:
                raise KeyError("Key [%s] is not a known Gene" % (names))
            else:
                return gene
        else:
            raise TypeError("Input must be of type string or list of strings.")

    def __str__(self):
        return self.__repr__();

    def __unicode__(self):
        return self.__repr__();

    def __repr__(self):
        return "<Gene:\"%s\">" % (self.name,)

class Chromosome(models.Model):
    genes = models.ManyToManyField('Gene', through='ChromosomeMembership',
            related_name='chromosomes')
    age = models.PositiveIntegerField(default=0)
    parents = models.ManyToManyField('self', related_name='children')

    @staticmethod
    def factory(genes, parents=[]):
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
                raise KeyError("There is no gene at index %d." % (index,))
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
                    chromosome=self, gene=gene1);
            gene2_mem = ChromosomeMembership.objects.get(
                    chromosome=self, gene=gene2);
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
        return self.__repr__();

    def __unicode__(self):
        return self.__repr__();

    def __repr__(self):
        return str([str(gene) for gene in
            self.genes.order_by("chromosomemembership__index")])

class ChromosomeMembership(models.Model):
    gene = models.ForeignKey('Gene')
    chromosome = models.ForeignKey('Chromosome')
    index = models.PositiveIntegerField();

class Generation(models.Model):
    chromosomes = models.ManyToManyField('Chromosome',
            through='GenerationMembership')

class GenerationMembership(models.Model):
    chromosome = models.ForeignKey('Chromosome')
    generation = models.ForeignKey('Generation')
    fitness = models.DecimalField(max_digits=10, decimal_places=9)

class Population(models.Model):
    generations = models.ManyToManyField('Generation')
