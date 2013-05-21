from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
import requests, json
import random

from oertutor.tutor.models import OpenEducationalResource as OER

def tutor(request):
    oers = OER.objects.all();
    if len(oers) > 0:
        oer = random.choice(oers)
        settings = {"source": oer.source}
        return render(request, 'oer_html.html', settings)
    else:
        return render(request, 'index.html')
