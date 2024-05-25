from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def alone(request):
    return render(request, 'no-sidebar.html')

def together(request):
    return render(request, 'right-sidebar.html')