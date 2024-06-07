from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from home.forms import SignUpForm, LoginForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Reservation, ShareOffice, Location
from django.db.models import Count
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
# Create your views here.
def index(request):
    return render(request, 'index.html')

def alone(request):
    return render(request, 'reservation.html')

def together(request):
    return render(request, 'reservation.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                customer = Customer.objects.get(cus_email=email)
                if check_password(password, customer.cus_password):
                    # 로그인 성공 (세션에 사용자 정보 저장)
                    request.session['customer_email'] = customer.cus_email
                    return redirect('index')  # 로그인 성공 후 리디렉션
                else:
                    messages.error(request, 'Invalid password.')
            except Customer.DoesNotExist:
                messages.error(request, 'Invalid email.')
    else:
        form = LoginForm()

    return render(request, 'login_register.html', {'form': form})

def logout_view(request):
    if 'customer_email' in request.session:
        del request.session['customer_email']
    return redirect('login')  # 로그아웃 후 로그인 페이지로 리디렉션

def my_page(request):
    customer_email = request.session.get('customer_email')
    if not customer_email:
        return redirect('login')  # 로그인되어 있지 않으면 로그인 페이지로 리디렉션

    try:
        customer = Customer.objects.get(cus_email=customer_email)
    except Customer.DoesNotExist:
        return redirect('login')  # 고객 정보가 없으면 로그인 페이지로 리디렉션

    return render(request, 'mypage.html', {'customer': customer})

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
        cus_password = make_password(request.POST.get('cus_password'))
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

# def check_reservation(request):
#     return render(request, 'check_reservation.html')

def reservation_list(request):
    # 로그인한 사용자의 이메일을 가져옵니다.
    customer_email = request.session.get('customer_email')
    if not customer_email:
        return redirect('login')  # 로그인되어 있지 않으면 로그인 페이지로 리디렉션

    # 해당 사용자의 예약 정보를 가져옵니다.
    reservations = Reservation.objects.filter(cus_email=customer_email).select_related('cus_email', 'so_id')

    return render(request, 'check_reservation.html', {'reservations': reservations})

# def customer_info(request, customer_id):
#     customer = get_object_or_404(Customer, id=customer_id)
#     return render(request, 'mypage.html', {'customer': customer})

def ranking(request):
    top_offices = (Reservation.objects.values('so_id')
                   .annotate(count=Count('so_id'))
                   .order_by('-count')[:5])

    top_office_details = []
    for office in top_offices:
        try:
            share_office = ShareOffice.objects.get(id=office['so_id'])
            top_office_details.append({
                'name': share_office.so_name,
                'address': share_office.so_address,
                'count': office['count']
            })
        except ShareOffice.DoesNotExist:
            continue

    return render(request, 'index.html',{'top_offices':top_office_details})