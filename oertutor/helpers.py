from tutor.models import Curriculum, Resource

def select_knowledge_component(request, kcs, curriculum):
    select = request.GET.get('select',None)
    if select is None:
        selected_kc = None;
    elif select == "start":
        if len(kcs) > 0:
            selected_kc = kcs[0]
        else:
            selected_kc = None
    else:
        try:
            select = int(select)
        except ValueError:
            select = None

        if select in range(len(kcs)):
            selected_kc = kcs[select];
        else:
            selected_kc = None
    return selected_kc

def select_curriculum(request):
    curriculum = request.GET.get('curr',None)
    if curriculum is None:
        curriculum = Curriculum.objects.all()[0]
    else:
        try:
            curriculum = Curriculum.objects.get(pk=curriculum)
        except Curriculum.DoesNotExist:
            curriculum = Curriculum.objects.all()[0]
    return curriculum

def select_resources(request, kc):
    if kc is None:
        return []
    else:
        return Resource.objects.filter(kc=kc)

def bootstrap_export():
    from oertutor.ga.models import *
    from oertutor.tutor.models import *

    item_template = (
        "BootstrapEvaluation.objects.create("
        "sequence = \"%s\","
        "category = StudentCategory.objects.get(pk=%d),"
        "trial = Trial.objects.get(pk=%d),"
        "value = %.12f)"
    )

    mapping = {}
    for trial in Trial.objects.order_by('-pk').exclude(
            posttest_result=None).exclude(sequence=None):
        key = (trial.category.pk,trial.sequence.pk)
        if key in mapping:
            mapping[key].append(trial.pk)
        else:
            mapping[key] = [trial.pk]

    print "from oertutor.tutor.models import *"
    for evaluation in Evaluation.objects.all():
        sequence = evaluation.individual.bootstrap_str()
        try:
            trial = Trial.objects.get(evaluation=evaluation).pk
        except Trial.DoesNotExist:
            trial_key = (evaluation.population.pk, evaluation.individual.pk)
            if trial_key in mapping:
                trial = mapping[trial_key].pop()
                if len(mapping[trial_key]) == 0:
                  del mapping[trial_key]
            else:
                raise Exception("No trial found for evaluation %d" %
                        (evaluation.pk))
        print item_template % (sequence, evaluation.population.pk,
            trial, evaluation.value)
