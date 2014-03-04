from django.shortcuts import render
from oertutor.ga.models import *
from oertutor.tutor.models import Resource, StudentCategory

def index(request):
    return render(request, 'ga_monitor_index.html',{})

def population_index(request):
    data = {"populations":[]}
    for population in Population.objects.all():
        try:
            category = population.studentcategory
        except StudentCategory.DoesNotExist:
            data['populations'].append({
                "id": population.pk,
                "title": "Population %d" % (population.pk,)
            })
        else:
            data['populations'].append({
                "id": category.pk,
                "title": category.title
            })
    return render(request, 'ga_monitor_population_index.html', data)

def population(request, pop_id):
    population = Population.objects.get(pk=pop_id)
    data = {'generations':[], 'regret_data': []}
    for i, generation in enumerate(population.generations.all()):
        data['generations'].append({
            'id': generation.pk,
            'individuals':[]
        })
        for j, individual in enumerate(
                generation.select_best_individuals(num=30)):
            data['generations'][i]['individuals'].append({
                'id': individual.pk,
                'genes': [],
                'fitness': individual.fitness(generation)
            })
            for gene in individual.chromosome.genes.all():
                try:
                    resource = gene.resource
                except Resource.DoesNotExist:
                    data['generations'][i]['individuals'][j]['genes'].append(
                        {'id': gene.pk, 'title': 'Gene %d' % (gene.pk,), 'link':None}
                    )
                else:
                    data['generations'][i]['individuals'][j]['genes'].append(
                        {'id': gene.pk, 'title': resource.title, 'link':resource.source}
                    )
    for evaluation in Evaluation.objects.filter(population=population):
        data['regret_data'].append(1-evaluation.value)
    return render(request, 'ga_monitor_population.html',data)

def student(request):
    pass
