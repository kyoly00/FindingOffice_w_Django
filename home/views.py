from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
def index(request):
    return render(request, 'index.html')

def alone(request):
    return render(request, 'reserve_page.html')

def together(request):
    return render(request, 'reserve_page.html')

def login(request):
    return render(request, 'login_register.html')

def mypage(request):
    return render(request, 'mypage.html')
