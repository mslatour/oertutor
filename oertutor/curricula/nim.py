from oertutor.tutor.models import *

def load_db():
    # Create final exam
    exam = Test.objects.create(title="Game", template="nim_game_exam.html")
    exam.questions.add(NimQuestion.factory(
        handle='g1',
        question='[1,2]',
        answer='[1]1:1,[-1]0:1,[1]1:1'))
    exam.questions.add(NimQuestion.factory(
        handle='g2',
        question='[2,3,2]',
        answer='[1]1:3,[-1]0:1,[1]2:1,[-1]0:1,[1]2:1'))
    exam.questions.add(NimQuestion.factory(
        handle='g3',
        question='[4,5,6]',
        answer='[1]1:3,[-1]0:4,[1]2:4,[-1]1:1,[1]2:1,[-1]1:1,[1]2:1 '))
    exam.questions.add(NimQuestion.factory(
        handle='g4',
        question='[1,3,4,5]',
        answer='[1]1:3,[-1]0:1,[1]3:1,[-1]2:3,[1]3:3,[-1]2:1,[1]3:1 '))
    exam.questions.add(NimQuestion.factory(
        handle='g5',
        question='[10,4,6,9]',
        answer='[1]3:1,[-1]0:9,[1]3:5,[-1]0:1,[1]3:1,[-1]1:4,[1]2:4,[-1]2:1,[1]3:1,[-1]2:1,[1]3:1'))
    exam.save()
    # Register curriculum
    curr, created = Curriculum.objects.get_or_create(
        title = "Become the Master of Nim",
        description = (
            "<div class='panel panel-default'>"
            "<div class='panel-heading'>Welcome</div>"
            "<div class='panel-body'>"
            "In this curriculum you will learn how to become the Master of"
            " Nim. Nim is a game that you can play anywhere with two players"
            " and several stacks of objects (e.g. coins). After these simple"
            " steps you will be unbeatable."
            "</div>"
            "</div>"
            "<div class='panel panel-default'>"
            "<div class='panel-heading'>How does it work?</div>"
            "<div class='panel-body'>"
            "<ol>"
            "<li>Learning Nim is divided in four topics</li>"
            "<li>A topic contains one or more explanations</li>"
            "<li>Topics start and end with a few questions</li>"
            "<li>Try to answer the questions to your best effort, if you"
            " really don't know the answer you can always indicate that.</li>"
            "<li>After the four steps you'll be given the chance to show off"
            " your skills in a series of Nim games.</li>"
            "<li>And then you are ready to challenge your friends.</li>"
            "</ol>"
            "</div>"
            "</div>"
        ),
        exam = exam
    )

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
        description = (
            "First things first, let's talk about the rules of the game."
        ),
        curriculum = curr
    )
    low,c = StudentCategory.objects.get_or_create(title="Rules Low",
            kc=kcs['rules'], upper_score=0.5)
    high,c = StudentCategory.objects.get_or_create(title="Rules High",
            kc=kcs['rules'], lower_score=0.5)
    low.neighbours.add(high)
    low.save()
    high.neighbours.add(low)
    high.save()

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
            ("1fromany", "Take one object from any single stack"),
            ("2fromany", "Take two objects from any single stack"))))
    test2.save()
    kcs['intuition'], created = KnowledgeComponent.objects.get_or_create(
        title = "Intuition",
        pretest = test2,
        posttest = test2,
        description = (
            "Before we get down to the strategies, let's first build up some "
            "intuition about Nim. We'll look at some of the simpler situations "
            "that you will face when playing.<br /><br />"
            "As with each topic, you'll be asked some questions to determine "
            "what you already knew about the topic. Then the rules will be "
            "explained to you. After which you'll be asked some questions to "
            "see what you've learned."
        ),
        curriculum = curr
    )
    low,c = StudentCategory.objects.get_or_create(title="Intuition Low",
            kc=kcs['intuition'], upper_score=0.5)
    high,c = StudentCategory.objects.get_or_create(title="Intuition High",
            kc=kcs['intuition'], lower_score=0.5)
    low.neighbours.add(high)
    low.save()
    high.neighbours.add(low)
    high.save()

    # KC: Binary numbers
    test3 = Test.objects.create(title="What do you know about binary numbers?")
    test3.questions.add(MultipleChoiceQuestion.factory(
        handle='q1',
        question="What is the binary representation of the decimal number 10?",
        answer="1010",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("0010", "0010"),
            ("1000", "1000"),
            ("1010", "1010"),
            ("1111111111", "1111111111"),
            ("0000000010", "0000000010"))))
    test3.questions.add(MultipleChoiceQuestion.factory(
        handle='q2',
        question="What is the decimal representation of the binary number 1000",
        answer="8",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1", "1"),
            ("4", "4"),
            ("8", "8"),
            ("1000","1000"))))
    test3.questions.add(MultipleChoiceQuestion.factory(
        handle='q3',
        question="Which number is bigger, the binary number 1001 or the decimal number 1001?",
        answer="dec",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("bin", "The binary number is bigger."),
            ("dec", "The decimal number is bigger."),
            ("eq", "They are equal."))))
    test3.save()
    kcs['binary'], created = KnowledgeComponent.objects.get_or_create(
        title = "Binary numbers",
        pretest = test3,
        posttest = test3,
        description = (
            "Now that we have some intuition about how to play the game, let's "
            "prepare ourselves for the ultimate strategy that you'll learn in "
            "the last step. The winning strategy takes advantages of patterns "
            "in the nim stacks. These patterns show themselves when you write "
            "the stacks down as binary numbers. So let's first learn a thing "
            "or two about how to do that."
            "<br /><br />"
            "As with each topic, you'll be asked some questions to determine "
            "what you already knew about the topic. Then the rules will be "
            "explained to you. After which you'll be asked some questions to "
            "see what you've learned."
        ),
        curriculum = curr
    )
    low,c = StudentCategory.objects.get_or_create(title="Binary Low",
            kc=kcs['binary'], upper_score=0.5)
    high,c = StudentCategory.objects.get_or_create(title="Binary High",
            kc=kcs['binary'], lower_score=0.5)
    low.neighbours.add(high)
    low.save()
    high.neighbours.add(low)
    high.save()

    test4 = Test.objects.create(title="Can you see the patterns?")
    test4.questions.add(MultipleChoiceQuestion.factory(
        handle='q1',
        question="On the table are three stacks. The first stack has 10\
        objects. The second stack has 8 objects. The third stack has 6 objects.\
        From which stack do you take objects when making an optimal move?",
        answer="3",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1", "The first stack."),
            ("2", "The second stack."),
            ("3", "The third stack."),
            ("any", "Any stack will do."))))
    test4.questions.add(MultipleChoiceQuestion.factory(
        handle='q2',
        question="On the table are three stacks. The first stack has 10\
        objects. The second stack has 8 objects. The third stack has 6 objects.\
        How many objects will you take from a stack when making an optimal move?",
        answer="4",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("2", "Two objects."),
            ("4", "Four objects."),
            ("6", "Six objects."),
            ("8", "Eight objects."))))
    test4.questions.add(MultipleChoiceQuestion.factory(
        handle='q3',
        question="On the table are five stacks. The first stack has 9\
        objects, the second 8, the third 7, the fourth 6 and the fift stack\
        has 5 objects. Which move will you make?",
        answer="5",
        template="question/radio-vertical.html",
        answer_list=(
            ("null", "I have no idea."),
            ("1", "Nine objects from the first stack."),
            ("2", "Eight objects from the second stack."),
            ("3", "Seven objects from the third stack."),
            ("4", "Six objects from the fourth stack."),
            ("5", "Five objects from the fift stack."))))
    test4.save()
    kcs['nimsum'], created = KnowledgeComponent.objects.get_or_create(
        title = "Doing some Nim magic",
        pretest = test4,
        posttest = test4,
        description = (
            "You can win any nim game that is winnable by applying the right "
            "strategy. Now that you have learned how to see numbers in their "
            "binary form, you are ready to see patterns in the Nim stacks that"
            " others won't. These patterns will inform you from which stack "
            "you should take objects and how many."
            "<br /><br />"
            "As with each topic, you'll be asked some questions to determine "
            "what you already knew about the topic. Then the rules will be "
            "explained to you. After which you'll be asked some questions to "
            "see what you've learned."
        ),
        curriculum = curr
    )
    low,c = StudentCategory.objects.get_or_create(title="NimSum Low",
            kc=kcs['nimsum'], upper_score=0.5)
    high,c = StudentCategory.objects.get_or_create(title="NimSum High",
            kc=kcs['nimsum'], lower_score=0.5)
    low.neighbours.add(high)
    low.save()
    high.neighbours.add(low)
    high.save()

    # Save knowledge components
    for kc in kcs:
        kcs[kc].save()

    # Create structure in the curriculum
    kcs['intuition'].antecedents.add(kcs['rules'])
    kcs['binary'].antecedents.add(kcs['intuition'])
    kcs['nimsum'].antecedents.add(kcs['binary'])

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
        title = "Showing a basic strategy",
        source = "/static/html/oer_nim_intuition_4.html",
        kc = kcs['intuition']
    )

    Resource.factory(
        title = "Learn about binary numbers",
        source = "/static/html/oer_nim_binary_1.html",
        kc = kcs['binary']
    )

    Resource.factory(
        title = "Examples of binary numbers",
        source = "/static/html/oer_nim_binary_2.html",
        kc = kcs['binary']
    )

    Resource.factory(
        title = "Binary numbers made easy",
        source = "/static/html/oer_nim_binary_3.html",
        kc = kcs['binary']
    )

    Resource.factory(
        title = "Definition of binary numbers",
        source = "/static/html/oer_nim_binary_4.html",
        kc = kcs['binary']
    )

    Resource.factory(
        title = "Introducing pair canceling",
        source = "/static/html/oer_nim_pair_canceling_1.html",
        kc = kcs['nimsum']
    )

    Resource.factory(
        title = "An example of pair canceling",
        source = "/static/html/oer_nim_pair_canceling_2.html",
        kc = kcs['nimsum']
    )

    Resource.factory(
        title = "An example of pair canceling",
        source = "/static/html/oer_nim_xor_1.html",
        kc = kcs['nimsum']
    )
