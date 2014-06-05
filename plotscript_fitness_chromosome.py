from oertutor.monitor.helpers import *
from numpy import linspace
from oertutor.tutor.models import StudentCategory
from oertutor.ga.models import Chromosome
import matplotlib.pyplot as plt


def plot_fitness(chromosomes, pop=None, fontsize="x-large"):
  for index, chromosome in enumerate(chromosomes):
    if len(chromosomes) == 1:
      plt.subplot(1,1,1)
    elif len(chromosomes) <= 4:
      plt.subplot(2,2,index+1)
    elif len(chromosomes) <= 6:
      plt.subplot(3,2,index+1)
    elif len(chromosomes) <= 8:
      plt.subplot(4,2,index+1)
    else:
      plt.subplot(3,3,index+1)
    plt.gca().set_xlabel("Evaluation", fontsize=fontsize)
    plt.gca().set_ylabel("Fitness value", fontsize=fontsize)
    fitness_data = gather_real_fitness_data(chromosome, population=pop)
    avg_data = running_average(fitness_data)
    n = len(fitness_data)
    plt.axis([1,n+1, float(min(0,min(fitness_data),1)), 1])
    plt.plot(range(1,n+1), fitness_data, 'o-', markersize=6)
    plt.plot(range(1,n+1), avg_data)
    plt.tight_layout()
    for label in plt.gca().get_xticklabels():
        label.set_fontsize(fontsize)
    for label in plt.gca().get_yticklabels():
        label.set_fontsize(fontsize)
  plt.show()


from django.db.models import Count

for pop in Population.objects.all():
  ranking = Evaluation.objects.values('chromosome').filter(population=pop).annotate(c=Count("id")).order_by('-c')
  chromosomes = [Chromosome.objects.get(pk=rank["chromosome"]) for rank in ranking[0:8]]
  print "Population %d" % (pop.pk,)
  for chromosome in chromosomes:
    print "Chromosome %s" % (chromosome)
    plot_fitness([chromosome], pop=pop)


