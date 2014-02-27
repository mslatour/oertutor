from oertutor.tutor.models import Curriculum, KnowledgeComponent, Trial, \
        Question, StudentAnswer, TestResult

def select_trial(student, curriculum=None):
    if curriculum is None:
        curriculum = Curriculum.objects.all()[0]

    current = Trial.objects.filter(student=student, curriculum=curriculum,
            posttest_result=None)
    if len(current) > 0:
        return current[0]
    else:
        done = [t.kc for t in Trial.objects.filter(student=student,
            posttest_result__isnull=False)]
        left = KnowledgeComponent.objects.filter(curriculum=curriculum).exclude(
                pk__in=[kc.id for kc in done])
        done = set(done)
        if len(left) > 0:
            next_kc = None
            for kc in left:
                if done.issuperset(set(kc.antecedents.all())):
                    return Trial.objects.create(student=student, kc=kc,
                            curriculum=curriculum)
            raise Exception('KC graph is not fully reachable')
        else:
            return None

def grade_test(request, student, test):
    score = 0.0
    result = TestResult.objects.create(test=test, student=student)
    for question in test.questions.all():
        answer = request.POST.get(question.handle, "")
        StudentAnswer.objects.create(question=question, testresult=result,
                student=student, answer=answer)
        if answer == question.answer:
            score += 1.0
    score /= test.questions.count()
    result.score = score
    result.save()
    return result

