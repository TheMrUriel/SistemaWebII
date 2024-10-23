from django.shortcuts import render

from django.http import HttpResponse


def home(request):
    return render(request, 'App/Inicio.html')

def log_in(request):
    return render(request, 'App/login.html')

def sign_up(request):
    return render(request, 'App/signup.html')