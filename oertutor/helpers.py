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
