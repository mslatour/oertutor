from django.db import models

class Gene(models.Model):
    name = models.CharField(max_length=255)

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

    def get_gene_by_index(self, index):
        try:
            gene = self.genes.get(chromosomemembership__index=index)
        except Gene.DoesNotExist:
            return False
        else:
            return gene

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
