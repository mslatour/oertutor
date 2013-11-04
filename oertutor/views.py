from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
from random import choice
import requests, json

from tutor.models import KnowledgeComponent
from helpers import *

def interface(request):
    curriculum = select_curriculum(request)
    kcs = KnowledgeComponent.objects.filter(curriculum=curriculum)
    kc = select_knowledge_component(request, kcs, curriculum)
    resources = select_resources(request, kc)
    if len(resources) > 0:
        return render(request, 'resource.html', {
            'kcs':kcs,
            'selected_kc':kc.id if kc is not None else 0,
            'resource':choice(resources),
            'curriculum':curriculum
        })
    else:
        return render(request, 'index.html', {
            'kcs':kcs,
            'selected_kc':kc.id if kc is not None else 0,
            'curriculum':curriculum
        })

def nim(request):
    return render(request, 'nim.html')
