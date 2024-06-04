from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from .forms import SignUpForm
from django.contrib import messages
from .models import Customer
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

def sign_up(request):
    if request.method == 'POST':
        cus_password = request.POST.get('cus_password')
        cus_name = request.POST.get('cus_name')
        cus_gender = request.POST.get('cus_gender')
        cus_email = request.POST.get('cus_email')
        cus_company = request.POST.get('cus_company')
        cus_phone = request.POST.get('cus_phone')
        cus_address = request.POST.get('cus_address')

        # 새로운 Customer 인스턴스 생성 및 저장
        customer = Customer(
            cus_password=cus_password,
            cus_name=cus_name,
            cus_gender=cus_gender,
            cus_email=cus_email,
            cus_company=cus_company,
            cus_phone=cus_phone,
            cus_address=cus_address,
        )
        customer.save()
        messages.success(request, 'Account created successfully!')
        return redirect('login')

    return render(request, 'login_register.html')