from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseRedirect
from decimal import Decimal
from oertutor.ga.web import *
from oertutor.tutor.helpers import select_trial, grade_test
from oertutor.helpers import select_curriculum
import requests, json
import random

from oertutor.settings import FEATURES

from oertutor.tutor.models import *

def tutor(request):
    student = Student.by_session(request.session)
    curriculum = select_curriculum(request)
    kcs = KnowledgeComponent.objects.filter(curriculum=curriculum)
    trial = select_trial(student, curriculum)
    if student.phase == Student.NEW:
        return render(request, 'new.html', {
            'kcs':kcs,
            'selected_kc': "start",
            'curriculum':curriculum,
        })
    elif student.phase == Student.INTRO:
        if trial is not None:
            kc = trial.kc
            return render(request, 'intro.html', {
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'title': kc.title,
                'description': kc.description,
                'curriculum':curriculum
            })
    elif student.phase == Student.SKIP:
        if trial is not None:
            kc = trial.kc
            return render(request, 'skip.html', {
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'curriculum':curriculum
            })
    elif student.phase == Student.PRETEST:
        if trial is not None:
            kc = trial.kc
            return render(request, 'test.html', {
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'curriculum':curriculum,
                'test': kc.pretest,
                'questions': kc.pretest.questions.all()
            })
    elif student.phase == Student.SEQUENCE:
        if trial is not None:
            kc = trial.kc
            if trial.sequence is None:
                trial.sequence = request_sequence(trial.category)
                trial.save()
            return render(request, 'resource.html', {
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'curriculum': curriculum,
                'resource': trial.sequence[trial.sequence_position].resource
            })
    elif student.phase == Student.POSTTEST:
        if trial is not None:
            kc = trial.kc
            return render(request, 'test.html', {
                'kcs':kcs,
                'selected_kc':kc.id if kc is not None else 0,
                'curriculum':curriculum,
                'test': kc.posttest,
                'questions': kc.posttest.questions.all()
            })
    elif student.phase == Student.DONE:
        return render(request, 'done.html', {
            'kcs':kcs,
            'selected_kc': "end",
            'curriculum':curriculum,
        })

def next_step(request):
    student = Student.by_session(request.session)
    curriculum = select_curriculum(request)
    trial = select_trial(student)
    if request.method == "POST":
        if student.phase == Student.PRETEST:
            if trial is not None:
                result = grade_test(request, student, trial.kc.pretest)
                trial.pretest_result = result
                if result.score == 1:
                    student.phase = Student.SKIP
                else:
                    trial.category = determine_student_category(trial.kc,
                        result.score, student)
                    student.phase = Student.SEQUENCE
                trial.save()
                student.save()
            return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.POSTTEST:
            if trial is not None:
                result = grade_test(request, student, trial.kc.posttest)
                trial.posttest_result=result
                trial.save()
                postscore = Decimal(result.score)
                prescore = Decimal(trial.pretest_result.score)
                nlg = (postscore-prescore) / (Decimal(1)-prescore)
                store_evaluation(trial.sequence, trial.category, nlg)
                next_trial = select_trial(student)
                if next_trial is not None:
                    student.phase = Student.INTRO
                    student.save()
                    return HttpResponseRedirect('/tutor/')
                else:
                    student.phase = Student.DONE
                    student.save()
                    return HttpResponseRedirect('/tutor')
    elif request.method == "GET":
        if student.phase == Student.NEW:
            if trial is not None:
                next_kc = trial.kc
                student.phase = Student.INTRO
                student.save()
                return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.INTRO:
            student.phase = Student.PRETEST
            student.save()
            return HttpResponseRedirect('/tutor')
        elif student.phase == Student.SKIP:
            if trial is not None:
                trial.posttest_result = trial.pretest_result
                trial.save()
                next_trial = select_trial(student)
                if next_trial is not None:
                    student.phase = Student.INTRO
                    student.save()
                    return HttpResponseRedirect('/tutor/')
                else:
                    student.phase = Student.DONE
                    student.save()
                    return HttpResponseRedirect('/tutor')
        elif student.phase == Student.SEQUENCE:
            if trial is not None:
                if (trial.sequence_position+1) < len(trial.sequence):
                    trial.sequence_position += 1
                    trial.save()
                else:
                    student.phase = Student.POSTTEST
                    student.save()
                return HttpResponseRedirect('/tutor')
    return HttpResponseRedirect('/tutor')


def determine_student_category(kc, score, student):
    cat = StudentCategory.objects.filter(kc=kc, lower_score__lte=score,
            upper_score__gt=score)[0]
    print "Student category", cat
    return cat

def observation(request):
    student = Student.by_session(request.session)
    if request.method == 'POST':
        for handle in request.POST:
            if handle in FEATURES:
                obs, created = Observation.objects.get_or_create(handle=handle)
                obs.value = request.POST.get(handle)
                obs.save()
            else:
                return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def load(request):
    categories = StudentCategory.objects.all()
    for category in categories:
        kc = category.kc
        resources = Resource.objects.filter(kc=kc)
        if len(resources) == 0:
            print "No resources for", kc
        else:
            init_population(category, list(resources))
    return HttpResponse("Done")
