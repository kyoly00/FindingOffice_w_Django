from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
def index(request):
    return render(request, 'index.html')

def alone(request):
    return render(request, 'reservation.html')

def together(request):
    return render(request, 'reservation.html')

def login(request):
    return render(request, 'login_register.html')

def mypage(request):
    return render(request, 'mypage.html')

def location_view(request):
    return render(request, 'location.html')

def choose(request):
    return render(request, 'choose.html')

def recommendation(request):
    return render(request, 'recommendation.html')

def enterinfo(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected')
        # selected_items 예시: ['John Doe, 30', 'Jane Smith, 25']

        # 데이터를 분리하여 context로 넘깁니다.
        selected_data = [item.split(', ') for item in selected_items]
        context = {
            'selected_data': selected_data,
        }
        return render(request, 'enterinfo.html', context)
    return render(request, 'recommendation.html')