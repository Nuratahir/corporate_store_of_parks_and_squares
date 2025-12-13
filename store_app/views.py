from django.shortcuts import render
from django.http import HttpResponse

def start_page(request):
    return render(request, "store_app/start_page.html")

def ordering(request):
    return render(request, "store_app/ordering.html")

def personal_account(request):
    return render(request, "store_app/personal_account.html")

def login(request):
    return render(request, "store_app/login.html")

def registration(request):
    return render(request, "store_app/registration.html")

