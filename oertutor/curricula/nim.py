from oertutor.tutor.models import Curriculum, KnowledgeComponent, Resource, \
    Test

def load_db():
    # Register curriculum
    curr, created = Curriculum.objects.get_or_create(
        title = "Become the Master of Nim",
        description = "In this topic you will learn everything that you need" +
            " to be a champion at the game NIM"
    )

    # Test
    test, created = Test.objects.get_or_create(title='Generic test')

    # Knowledge Components
    kcs = {}
    kcs['rules'], created = KnowledgeComponent.objects.get_or_create(
        title = "Rules of the game",
        pretest = test,
        posttest = test,
        description = "How does the game work?",
        curriculum = curr
    )

    kcs['intuition'], created = KnowledgeComponent.objects.get_or_create(
        title = "Intuition",
        pretest = test,
        posttest = test,
        description = "Getting a feel for the game",
        curriculum = curr
    )

    kcs['binary'], created = KnowledgeComponent.objects.get_or_create(
        title = "Binary numbers",
        pretest = test,
        posttest = test,
        description = "What are binary numbers?",
        curriculum = curr
    )

    kcs['cancel2powers'], created = KnowledgeComponent.objects.get_or_create(
        title = "They come in pairs",
        pretest = test,
        posttest = test,
        description = "Cancel equal powers of 2",
        curriculum = curr
    )

    kcs['xor'], created = KnowledgeComponent.objects.get_or_create(
        title = "It is one or the other",
        pretest = test,
        posttest = test,
        description = "Learning the XOR operation",
        curriculum = curr
    )

    kcs['nimsum'], created = KnowledgeComponent.objects.get_or_create(
        title = "Nim-sum",
        pretest = test,
        posttest = test,
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
        kc = kcs['rules']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "NIM rules",
        source = "/static/html/oer4.html",
        kc = kcs['rules']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Play a game",
        source = "/static/html/oer5.html",
        kc = kcs['intuition']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Example of pair canceling",
        source = "/static/html/oer3.html",
        kc = kcs['cancel2powers']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "Learn about binary numbers",
        source = "/static/html/oer6.html",
        kc = kcs['binary']
    )
    if created:
        resource.save()

    resource, created = Resource.objects.get_or_create(
        title = "What is this XOR?",
        source = "/static/html/oer7.html",
        kc = kcs['xor']
    )
    if created:
        resource.save()
