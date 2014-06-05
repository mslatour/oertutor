from oertutor.monitor.helpers import *
from plot import plot
from oertutor.ga.simulate import *
from oertutor.ga.models import *

def plot_chromosome_ages(chromosomes, pop=None):
  ages = {}
  for chromosome in set(chromosomes):
    if pop is None:
      ages[chromosome_identity(chromosome)] = \
      len(gather_real_fitness_data(chromosome))
    else:
      ages[chromosome_identity(chromosome)] = \
        len(gather_real_fitness_data(chromosome, population=pop))
  ages = sorted(ages.values(), reverse=True)
  tab = TabularData([[index,age] for index,age in enumerate(ages)])
  plot(tab, xlabel = 'Sequence', ylabel='Number of evaluations', marker='o')

populations = Population.objects.all()
for pop in populations:
  print "Population %d" % (pop.pk,)
  chromosomes = []
  for generation in pop.generations.all():
    mem = GenerationMembership.objects.filter(generation=generation)
    chromosomes += [m.chromosome for m in mem]
  
  plot_chromosome_ages(chromosomes, pop=pop)


