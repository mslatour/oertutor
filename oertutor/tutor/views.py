from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import requests, json
import random
from oertutor.rl.learners import QLearner

from oertutor.settings import FEATURES

from oertutor.tutor.models import Resource as OER
from oertutor.tutor.models import Observation

def tutor(request):
    oers = OER.objects.all();
    if len(oers) > 0:
        oer = random.choice(oers)
        settings = {"source": oer.source}
        return render(request, 'oer_html.html', settings)
    else:
        return render(request, 'index.html')

def observation(request):
    learner = request.session.get("learner", None)
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
