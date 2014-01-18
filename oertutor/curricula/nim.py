from oertutor.tutor.models import Curriculum, KnowledgeComponent, TutorMove, Resource

def load_db():
    # Register curriculum
    curr, created = Curriculum.objects.get_or_create(
        title = "Nim",
        description = "In this topic you will learn everything that you need" +
            " to be a champion at the mathematical game NIM"
    )

    # Register tutor moves
    elicit, created = TutorMove.objects.get_or_create(title="Elicit")
    elicit.save()
    tell, created = TutorMove.objects.get_or_create(title="Tell")
    tell.save()

    # Knowledge Components
    kcs = {}
    kcs['rules'], created = KnowledgeComponent.objects.get_or_create(
        title = "Rules of the game",
        description = "How does the game work?",
        curriculum = curr
    )

    kcs['intuition'], created = KnowledgeComponent.objects.get_or_create(
        title = "Intuition",
        description = "Getting a feel for the game",
        curriculum = curr
    )

    kcs['binary'], created = KnowledgeComponent.objects.get_or_create(
        title = "Binary numbers",
        description = "What are binary numbers?",
        curriculum = curr
    )

    kcs['cancel2powers'], created = KnowledgeComponent.objects.get_or_create(
        title = "They come in pairs",
        description = "Cancel equal powers of 2",
        curriculum = curr
    )

    kcs['xor'], created = KnowledgeComponent.objects.get_or_create(
        title = "It is one or the other",
        description = "Learning the XOR operation",
        curriculum = curr
    )

    kcs['nimsum'], created = KnowledgeComponent.objects.get_or_create(
        title = "Nim-sum",
        description = "Using XOR to win the game",
        curriculum = curr
    )

    # Save knowledge components
    for kc in kcs:
        kcs[kc].save()

    # Create structure in the curriculum
    kcs['intuition'].antecedents.add(kcs['rules'])
    kcs['binary'].antecedents.add(kcs['intuition'])
    kcs['cancel2powers'].antecedents.add(kcs['binary'])
    kcs['xor'].antecedents.add(kcs['cancel2powers'])
    kcs['nimsum'].antecedents.add(kcs['xor'])

    # Save structure
    for kc in kcs:
        kcs[kc].save()

    # Create resources
    resource, created = Resource.objects.get_or_create(
        title = "Rules of NIM game",
        source = "/static/html/oer1.html",
        tm = tell,
        kc = kcs['rules']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "NIM rules",
        source = "/static/html/oer4.html",
        tm = tell,
        kc = kcs['rules']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Play a game",
        source = "/static/html/oer5.html",
        tm = elicit,
        kc = kcs['intuition']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Example of pair canceling",
        source = "/static/html/oer3.html",
        tm = tell,
        kc = kcs['cancel2powers']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Learn about binary numbers",
        source = "/static/html/oer6.html",
        tm = tell,
        kc = kcs['binary']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "What is this XOR?",
        source = "/static/html/oer7.html",
        tm = tell,
        kc = kcs['xor']
    )
    if created:
        resource.save()
