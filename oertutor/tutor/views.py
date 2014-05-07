from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from decimal import Decimal
from oertutor.ga.web import init_population, request_sequence, store_evaluation
from oertutor.tutor.helpers import select_trial
from oertutor.tutor import signals
from oertutor.helpers import select_curriculum
from oertutor.tutor.models import KnowledgeComponent, Student, \
        StudentCategory, Resource, BootstrapEvaluation
from django.forms.models import modelform_factory

def aws_mt(request):
    hit_id = request.GET.get('hitId', None)
    assignment_id = request.GET.get('assignmentId', None)
    if hit_id is not None and assignment_id is not None:
        if assignment_id == "ASSIGNMENT_ID_NOT_AVAILABLE":
            curriculum = select_curriculum(request)
            kcs = KnowledgeComponent.objects.order_by('pk').filter(
                    curriculum=curriculum)
            return render(request, 'new.html', {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc': "start",
                'progress': 0,
                'curriculum':curriculum,
                "preview": True
            })
        else:
            if request.session.get("student", None) is None:
                student = Student.by_session(request.session)
                request.session['origin'] = "aws-mt"
                request.session['aws_mt_submit_url'] = settings.AWS_MT_SUBMIT_URL
                request.session['aws_mt_assignmentId'] = assignment_id
                signals.tutor_session_origin.send(
                        sender=request.session,
                        origin='aws-mt',
                        data={'hitId':hit_id, 'assignmentId': assignment_id,
                            'workerId': request.GET.get('workerId', 'none')},
                        student=student)
    return HttpResponseRedirect('/tutor/')

def tutor(request):
    student = Student.by_session(request.session)
    curriculum = select_curriculum(request)
    kcs = KnowledgeComponent.objects.order_by('pk').filter(
            curriculum=curriculum)
    trial = select_trial(student, curriculum)
    if student.phase == Student.DONE:
        progress = 100
    elif student.phase == Student.EXAM:
        progress = int(round(float(len(kcs)+1)/((len(kcs)+2))*100))
    elif student.phase == Student.NEW:
        progress = 0
    elif trial is not None:
        location = list(kcs).index(trial.kc)
        progress = int(round((float(location+1)/(len(kcs)+2))*100))
    else:
        progress = None
    if student.phase == Student.NEW:
        return render(request, 'new.html', {
            'url': request.build_absolute_uri(),
            'kcs':kcs,
            'selected_kc': "start",
            'progress': progress,
            'curriculum':curriculum,
        })
    elif student.phase == Student.INTRO:
        if trial is not None:
            kc = trial.kc
            return render(request, 'intro.html', {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'progress': progress,
                'title': kc.title,
                'description': kc.description,
                'curriculum':curriculum
            })
    elif student.phase == Student.SKIP:
        if trial is not None:
            kc = trial.kc
            return render(request, 'skip.html', {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'progress': progress,
                'curriculum':curriculum
            })
    elif student.phase == Student.PRETEST:
        if trial is not None:
            kc = trial.kc
            if kc.pretest.template is None:
                template = "test.html"
            else:
                template = kc.pretest.template
            return render(request, template, {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'progress': progress,
                'curriculum':curriculum,
                'test': kc.pretest,
                'questions': kc.pretest.questions.all()
            })
    elif student.phase == Student.SEQUENCE:
        if trial is not None:
            kc = trial.kc
            if trial.sequence is None:
                sequence = None
                while sequence is not None:
                    sequence = request_sequence(trial.category)
                    # Attempt to find bootstrap value
                    bootstraps = BootstrapEvaluation.objects.\
                        order_by('pk').filter(
                            sequence = sequence.bootstrap_str()
                            category = trial.category,
                            used = False)
                    if len(bootstraps) > 0:
                        print "bootstrapping %s in %s" % (sequence, category)
                        bootstrap = bootstraps[0]
                        signals.ga_bootstrap_evaluation.send(
                                sender=category,
                                sequence=sequence,
                                bootstrap=bootstrap)
                        evaluation = store_evaluation(sequence, category,
                                bootstrap.value)
                        bootstrap.trial.evaluation = evaluation
                        bootstrap.trial.save()
                        bootstrap.used = True
                        bootstrap.save()
                        sequence = None
                # Assign sequence to student
                trial.sequence = sequence
                trial.save()
            return render(request, 'resource.html', {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'progress': progress,
                'curriculum': curriculum,
                'resource': trial.sequence[trial.sequence_position].resource
            })
    elif student.phase == Student.POSTTEST:
        if trial is not None:
            kc = trial.kc
            if kc.posttest.template is None:
                template = "test.html"
            else:
                template = kc.posttest.template
            return render(request, template, {
                'url': request.build_absolute_uri(),
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'progress': progress,
                'curriculum':curriculum,
                'test': kc.posttest,
                'questions': kc.posttest.questions.all()
            })
    elif student.phase == Student.EXAM:
        if curriculum.exam.template is None:
            template = "test.html"
        else:
            template = curriculum.exam.template
        return render(request, template, {
            'url': request.build_absolute_uri(),
            'kcs':kcs,
            'selected_kc': "exam",
            'progress': progress,
            'curriculum':curriculum,
            'test': curriculum.exam,
            'questions':curriculum.exam.questions.all()
        })
    elif student.phase == Student.DONE:
        return render(request, 'done.html', {
            'url': request.build_absolute_uri(),
            'kcs':kcs,
            'selected_kc': "end",
            'progress': progress,
            'curriculum':curriculum,
        })

def next_step(request):
    student = Student.by_session(request.session)
    curriculum = select_curriculum(request)
    trial = select_trial(student)
    if request.method == "POST":
        if student.phase == Student.PRETEST:
            if trial is not None:
                result = trial.kc.pretest.grade(request.POST, student)
                trial.pretest_result = result
                if result.score == 1:
                    student.phase = Student.SKIP
                else:
                    trial.category = determine_student_category(trial.kc,
                        result.score, student)
                    student.phase = Student.SEQUENCE
                trial.save()
                student.save(update_fields=["phase"])
            return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.POSTTEST:
            if trial is not None:
                result = trial.kc.posttest.grade(request.POST, student)
                trial.posttest_result = result
                postscore = Decimal(result.score)
                prescore = Decimal(trial.pretest_result.score)
                nlg = (postscore-prescore) / (Decimal(1)-prescore)
                evaluation = store_evaluation(trial.sequence, trial.category, nlg)
                trial.evaluation = evaluation
                trial.save()
                next_trial = select_trial(student)
                if next_trial is not None:
                    student.phase = Student.INTRO
                elif curriculum.exam is not None:
                    student.phase = Student.EXAM
                else:
                    student.phase = Student.DONE
                student.save(update_fields=["phase"])
                return HttpResponseRedirect('/tutor')
        elif student.phase == Student.EXAM:
            if curriculum.exam is not None:
                result = curriculum.exam.grade(request.POST, student)
                student.phase = Student.DONE
                student.save(update_fields=["phase"])
                return HttpResponseRedirect('/tutor')
        elif student.phase == Student.DONE:
            Form = modelform_factory(
                Student,
                fields=("preskill","postskill","comments"))
            form = Form(request.POST, instance=student)
            form.save()
            return HttpResponseRedirect('/tutor')
    elif request.method == "GET":
        if student.phase == Student.NEW:
            if trial is not None:
                student.phase = Student.INTRO
                student.save(update_fields=["phase"])
                return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.INTRO:
            student.phase = Student.PRETEST
            student.save(update_fields=["phase"])
            return HttpResponseRedirect('/tutor')
        elif student.phase == Student.SKIP:
            if trial is not None:
                trial.posttest_result = trial.pretest_result
                trial.save()
                next_trial = select_trial(student)
                if next_trial is not None:
                    student.phase = Student.INTRO
                elif curriculum.exam is not None:
                    student.phase = Student.EXAM
                else:
                    student.phase = Student.DONE
                student.save(update_fields=["phase"])
                return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.SEQUENCE:
            if trial is not None:
                if (trial.sequence_position+1) < len(trial.sequence):
                    trial.sequence_position += 1
                    trial.save()
                else:
                    student.phase = Student.POSTTEST
                    student.save(update_fields=["phase"])
                return HttpResponseRedirect('/tutor')
    return HttpResponseRedirect('/tutor')


def determine_student_category(kc, score, student):
    cat = StudentCategory.objects.filter(kc=kc, lower_score__lte=score,
            upper_score__gt=score)[0]
    return cat

def forget(request):
    request.session.clear()
    return HttpResponseRedirect('/tutor')

def load(request):
    from oertutor.curricula.nim import load_db
    load_db()
    categories = StudentCategory.objects.all()
    for category in categories:
        kc = category.kc
        resources = Resource.objects.filter(kc=kc)
        if len(resources) == 0:
            continue
        else:
            init_population(category, list(resources))
    return HttpResponse("Done")
