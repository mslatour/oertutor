from oertutor.tutor.models import *

def load_db():
    # Register curriculum
    curr, created = Curriculum.objects.get_or_create(
        title = "Become the Master of Nim",
        description = "In this topic you will learn everything that you need" +
            " to be a champion at the game NIM"
    )

    # Test
    test, created = Test.objects.get_or_create(title='Generic test')
    q1 = Question.factory(handle='q1',
        question="Question1", answer="Answer1")
    q2 = MultipleChoiceQuestion.factory(
            handle='q2',
            question="Question2",
            answer="Answer2",
            answer_list=(
                ('Answer1', 'The wrong answer'),
                ('Answer2', 'The right answer')))
    test.questions.add(q1)
    test.questions.add(q2)
    test.save()

    ########################
    # Knowledge Components #
    ########################
    kcs = {}

    # KC: Rules of the game
    test1 = Test.objects.create(title="Let's see what you know about the game.")
    test1.questions.add(MultipleChoiceQuestion.factory(
        handle='q1',
        question="Can you take objects from more than one stack",
        answer="no2",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("no1", "No, you can only take one object at a time"),
            ("no2", "No, you can only take objects from a single stack"),
            ("yes1", "Yes, you are allowed to do that"),
            ("yes2", "Yes, but only if there are not enough objects on one "+\
                    "stack"))))
    test1.questions.add(MultipleChoiceQuestion.factory(
        handle='q2',
        question="Bob and John are playing the normal version of a Nim game."+\
                " John takes the last object on table. Who won?",
        answer="john",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("bob", "Bob won"),
            ("john", "John won"),
            ("nobody", "Nobody won yet"),
            ("depends", "That depens on whether it was John's second turn"))))
    test1.questions.add(MultipleChoiceQuestion.factory(
        handle='q3',
        question="How many objects are you allowed to take away from a stack",
        answer="min1",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("exact1", "Exactly one object."),
            ("all", "You have to take all the objects of that stack that you"+\
                " chose."),
            ("min1", "You have to take at least one object."))))
    test1.save()
    kcs['rules'], created = KnowledgeComponent.objects.get_or_create(
        title = "Rules of the game",
        pretest = test1,
        posttest = test1,
        description = "How does the game work?",
        curriculum = curr
    )
    StudentCategory.objects.get_or_create(title="Rules Low", kc=kcs['rules'],
            upper_score=0.5)
    StudentCategory.objects.get_or_create(title="Rules High", kc=kcs['rules'],
            lower_score=0.5)

    # KC: Intuition on how to play
    test2 = Test.objects.create(title="Let's see what your intuition is about the game.")
    test2.questions.add(MultipleChoiceQuestion.factory(
        handle='q1',
        question="On the table are three stacks. The first stack is empty,\
        the second stack has two objects and the third stack has one object.\
        What is the best move to make?",
        answer="1from2",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1from2", "Take one object from the second stack"),
            ("2from2", "Take two objects from the second stack"),
            ("1from3", "Take one object from the third stack"))))
    test2.questions.add(MultipleChoiceQuestion.factory(
        handle='q2',
        question="On the table are three stacks. The first stack has two\
        objects. The second stack has two objects. The third stack has one object.\
        What is the best move to make?",
        answer="1from3",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1from1", "Take one object from the first stack"),
            ("2from1", "Take two objects from the first stack"),
            ("1from2", "Take one object from the second stack"),
            ("2from2", "Take two objects from the second stack"),
            ("1from3", "Take one object from the third stack"))))
    test2.questions.add(MultipleChoiceQuestion.factory(
        handle='q3',
        question="On the table are three stacks. All stacks have two objects.\
        What is the best move to make?",
        answer="2fromany",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1fromany", "Take one object from the any single stack"),
            ("2fromany", "Take two objects from the any single stack"))))
    test2.save()
    kcs['intuition'], created = KnowledgeComponent.objects.get_or_create(
        title = "Intuition",
        pretest = test2,
        posttest = test2,
        description = "Getting a feel for the game",
        curriculum = curr
    )
    StudentCategory.objects.get_or_create(title="Intuition Low", kc=kcs['intuition'],
            upper_score=0.5)
    StudentCategory.objects.get_or_create(title="Intuition High", kc=kcs['intuition'],
            lower_score=0.5)

    kcs['binary'], created = KnowledgeComponent.objects.get_or_create(
        title = "Binary numbers",
        pretest = test,
        posttest = test,
        description = "What are binary numbers?",
        curriculum = curr
    )
    StudentCategory.objects.get_or_create(title="Binary Low", kc=kcs['binary'],
            upper_score=0.5)
    StudentCategory.objects.get_or_create(title="Binary High", kc=kcs['binary'],
            lower_score=0.5)

    kcs['cancel2powers'], created = KnowledgeComponent.objects.get_or_create(
        title = "They come in pairs",
        pretest = test,
        posttest = test,
        description = "Cancel equal powers of 2",
        curriculum = curr
    )
    StudentCategory.objects.get_or_create(title="Cancel2Powers Low",
            kc=kcs['cancel2powers'], upper_score=0.5)
    StudentCategory.objects.get_or_create(title="Cancel2Powers High",
            kc=kcs['cancel2powers'], lower_score=0.5)

    kcs['nimsum'], created = KnowledgeComponent.objects.get_or_create(
        title = "Nim-sum",
        pretest = test,
        posttest = test,
        description = "Using XOR to win the game",
        curriculum = curr
    )
    StudentCategory.objects.get_or_create(title="Nimsum Low", kc=kcs['nimsum'],
            upper_score=0.5)
    StudentCategory.objects.get_or_create(title="Nimsum High", kc=kcs['nimsum'],
            lower_score=0.5)

    # Save knowledge components
    for kc in kcs:
        kcs[kc].save()

    # Create structure in the curriculum
    kcs['intuition'].antecedents.add(kcs['rules'])
    kcs['binary'].antecedents.add(kcs['intuition'])
    kcs['cancel2powers'].antecedents.add(kcs['binary'])
    kcs['nimsum'].antecedents.add(kcs['cancel2powers'])

    # Save structure
    for kc in kcs:
        kcs[kc].save()

    # Create resources
    Resource.factory(
        title = "Introducing the NIM game",
        source = "/static/html/oer_nim_rules_1.html",
        kc = kcs['rules']
    )

    Resource.factory(
        title = "NIM rules",
        source = "/static/html/oer_nim_rules_2.html",
        kc = kcs['rules']
    )

    Resource.factory(
        title = "The three things to know about NIM",
        source = "/static/html/oer_nim_rules_3.html",
        kc = kcs['rules']
    )

    Resource.factory(
        title = "The game NIM: in short",
        source = "/static/html/oer_nim_rules_4.html",
        kc = kcs['rules']
    )

    Resource.factory(
        title = "Play a game",
        source = "/static/html/oer_nim_intuition_1.html",
        kc = kcs['intuition']
    )

    Resource.factory(
        title = "Some example scenarios",
        source = "/static/html/oer_nim_intuition_2.html",
        kc = kcs['intuition']
    )

    Resource.factory(
        title = "Intuitive strategy",
        source = "/static/html/oer_nim_intuition_3.html",
        kc = kcs['intuition']
    )

    Resource.factory(
        title = "Example of pair canceling",
        source = "/static/html/oer3.html",
        kc = kcs['cancel2powers']
    )

    Resource.factory(
        title = "Learn about binary numbers",
        source = "/static/html/oer6.html",
        kc = kcs['binary']
    )
