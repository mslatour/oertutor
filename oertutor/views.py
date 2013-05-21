from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from django.shortcuts import render
import requests, json

def interface(request):
    return render(request, 'index.html')

def nim(request):
    return render(request, 'nim.html')
