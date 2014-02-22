from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseRedirect
from oertutor.ga.web import *
from oertutor.tutor.helpers import select_knowledge_component
import requests, json
import random

from oertutor.settings import FEATURES

from oertutor.tutor.models import Student, Observation

"""
retrieve student
kc = determineKC()
if method == get:
    if phase(student, kc) == start or pretest
        return pre-test
    if phase == sequence:
        determine sequence
else:
    if phase == pretest:
        store results
        determing category
        move to phase sequence
    if phase == sequence:
        determine sequence
check if there are KC's left to do.
let kc be the next open KC
check if the student performed a pretest for kc
if not, present a pretest
"""
"""
def tutor(request):
    student = Student.by_session(request.session)
    if student.phase == Student.NEW:
        student.phase = Student.PRETEST
        student.save()
        return HttpResponse(student.phase)
        # Generate pretest HTML
    elif student.phase == Student.PRETEST:
        if request.method == 'POST':
            # Store pretest result, determine 
        student.phase = Student.SEQUENCE
        student.save()
        return HttpResponse(student.phase)

        sequence = request_sequence(student.population)
        student.phase = Student.SEQUENCE
        student.sequence = sequence
        student.save()
        # Generate sequence HTML
        
        oers = OER.objects.all();
        if len(oers) > 0:
            oer = random.choice(oers)
            settings = {"source": oer.source}
            return render(request, 'oer_html.html', settings)
        else:
            return render(request, 'index.html')
        
    elif student.phase == Student.SEQUENCE:
        return HttpResponse(student.phase)
"""
def tutor(request):
    student = Student.by_session(request.session)
    if student.phase == Student.NEW:
        return HttpResponseRedirect('/tutor/next')
    elif student.phase == Student.PRETEST:
        kc = select_knowledge_component(student)
        test(request, kc.pretest)
        return HttpResponse("pretest")
    elif student.phase == Student.SEQUENCE:
        return HttpResponse("sequence")
    elif student.phase == Student.POSTTEST:
        return HttpResponse("posttest")
    elif student.phase == Student.DONE:
        return HttpResponse("done")

def test(request, test):
    for question in test.questions.all():
        print question.question

def next_step(request):
    student = Student.by_session(request.session)
    if request.method == "POST":
        if student.phase == Student.PRETEST:
            print "store pretest", request.POST
            student.phase = Student.SEQUENCE
            student.save()
            return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.POSTTEST:
            print "store posttest", request.POST
            print "calculate normalized learning gain"
            next_kc = select_knowledge_component(student)
            if next_kc is not None:
                t = Trial.objects.create(student=student, kc=next_kc)
                student.phase = Student.PRETEST
                student.save()
                print "present KC:", next_kc
                return HttpResponseRedirect('/tutor/')
            else:
                print "move student to done"
                student.phase = Student.DONE
                student.save()
                return HttpResponseRedirect('/tutor')
    elif request.method == "GET":
        if student.phase == Student.NEW:
            print "Send student to first KC"
            next_kc = select_knowledge_component(student)
            if next_kc is not None:
                student.phase = Student.PRETEST
                student.save()
                print "present KC:", next_kc
                return HttpResponseRedirect('/tutor/')
        elif student.phase == Student.SEQUENCE:
            student.phase = Student.POSTTEST
            student.save()
            print "Send student to post test"
            return HttpResponseRedirect('/tutor')
    return HttpResponseRedirect('/tutor')


def determine_student_category(kc, student):
    return StudentCategory.objects.all()[0]

def tutor_sequence(kc, student):
    category = determine_student_category(kc, student)
    sequence = request_sequence(category)
    return sequence

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
