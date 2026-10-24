from django.shortcuts import render


def home(request):
    return render(request, 'frontend/dashboard.html')


def events(request):
    return render(request, 'frontend/dashboard.html')


def dashboard(request):
    return render(request, 'frontend/dashboard.html')
