from django.shortcuts import render
from decimal import Decimal
from oertutor.ga.models import *
from oertutor.tutor.models import Resource, StudentCategory, Student, Trial
from oertutor.log.models import LogEntry

def index(request):
    return render(request, 'monitor_index.html',{})

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
    return render(request, 'monitor_population_index.html', data)

def population(request, pop_id):
    mode = request.GET.get('mode', None)
    maxmode = request.GET.get('maxmode', None)
    population = Population.objects.get(pk=pop_id)
    if maxmode == "genbest":
        genbest = {}
        for generation in population.generations.all():
            best = generation.select_best_individuals()[0]
            mem = GenerationMembership.objects.get(
                    generation=generation, individual=best)
            genbest[generation.pk] = mem.fitness
    elif maxmode == "popbest":
        popbest = Decimal(0)
        for generation in population.generations.all():
            best = generation.select_best_individuals()[0]
            mem = GenerationMembership.objects.get(
                    generation=generation, individual=best)
            if popbest < Decimal(best.chromosome.fitness):
                popbest = best.chromosome.fitness

    data = {'generations':[], 'regret_data': []}
    for i, generation in enumerate(population.generations.all()):
        data['generations'].append({
            'id': generation.pk,
            'individuals':[]
        })
        for j, individual in enumerate(
                generation.select_best_individuals(num=30)):
            if mode == "avg":
                data['generations'][i]['individuals'].append({
                    'id': individual.pk,
                    'genes': [],
                    'fitness': Evaluation.fitness(
                        chromosome=individual.chromosome)
                })
            else:
                data['generations'][i]['individuals'].append({
                    'id': individual.pk,
                    'genes': [],
                    'fitness': individual.fitness(generation)
                })
            for gene in individual.chromosome.genes.order_by(
                        "chromosomemembership__index").all():
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
    if mode == "avg":
        # Running average container
        ravg = {}
        for evaluation in Evaluation.objects.filter(population=population):
            chromosome = evaluation.chromosome
            if maxmode == "genbest":
                maxvalue = Decimal(genbest[evaluation.generation.pk])
                mem = GenerationMembership.objects.get(
                        generation=evaluation.generation,
                        individual=evaluation.individual)
                value = Decimal(mem.fitness)
            elif maxmode == "popbest":
                maxvalue = Decimal(popbest)
                mem = GenerationMembership.objects.get(
                        generation=evaluation.generation,
                        individual=evaluation.individual)
                value = Decimal(mem.chromosome.fitness)
            else:
                maxvalue = 1
                value = Decimal(evaluation.value)

            if evaluation.chromosome in ravg:
                ravg[chromosome] = (
                    ravg[chromosome][0] + value,
                    ravg[chromosome][1] + Decimal(1))
            else:
                ravg[chromosome] = (value, Decimal(1))
            data['regret_data'].append(maxvalue-(
                ravg[chromosome][0]/ravg[chromosome][1]))

    else:
        for evaluation in Evaluation.objects.filter(population=population):
            if maxmode == "genbest":
                maxvalue = Decimal(genbest[evaluation.generation.pk])
                mem = GenerationMembership.objects.get(
                        generation=evaluation.generation,
                        individual=evaluation.individual)
                value = mem.fitness
            elif maxmode == "popbest":
                maxvalue = Decimal(popbest)
                mem = GenerationMembership.objects.get(
                        generation=evaluation.generation,
                        individual=evaluation.individual)
                value = mem.chromosome.fitness
            else:
                maxvalue = 1
                value = evaluation.value
            data['regret_data'].append(maxvalue-value)
    return render(request, 'monitor_population.html',data)

def student_index(request):
    data = {"students": []}
    phase_dict = dict(Student.PHASES)
    for student in Student.objects.all():
        trial = Trial.objects.filter(student=student, posttest_result=None)
        data['students'].append({
            "id": student.pk,
            "started": student.started,
            "updated": student.updated,
            "phase": phase_dict[student.phase],
            "kc": (str(trial[0].kc) if trial else None)
        })
    return render(request, 'monitor_student_index.html', data)

def student(request, student_id):
    student = Student.objects.get(pk=student_id)
    data = {"trials": []}
    for trial in Trial.objects.filter(student=student):
        data['trials'].append({
            "id": trial.pk,
            "kc": str(trial.kc),
            "category": trial.category,
            "pretest": (trial.pretest_result.score if
                trial.pretest_result is not None else None),
            "posttest": (trial.posttest_result.score if
                trial.posttest_result is not None else None),
            "sequence": (str(trial.sequence.pk) if
                trial.sequence is not None else None),
            "updated": trial.datetime
        })
    data['log_entries'] = LogEntry.objects.order_by('-pk').filter(
            student=student)
    return render(request, "monitor_student.html", data)

def log(request):
    entries = LogEntry.objects.order_by('-pk').all()
    return render(request, 'monitor_log.html', {'log_entries':entries})
