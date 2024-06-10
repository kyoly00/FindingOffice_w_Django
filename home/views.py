from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from .forms import SignUpForm, LoginForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Reservation, ShareOffice
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required

from urllib import parse
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import json

import os
from dotenv import load_dotenv

load_dotenv()

Client_ID = os.getenv('CLIENT_ID')
Client_KEY = os.getenv('CLIENT_KEY')

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
    if 'customer_id' in request.session:
        del request.session['customer_id']
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

def range_limit(latitudes, longitudes):
    max_lat, max_lng = max(latitudes), max(longitudes)
    min_lat, min_lng = min(latitudes), min(longitudes)
    return max_lat, max_lng, min_lat, min_lng

def call

def finding_optimal(origin):
    # 이동 시간을 저장할 딕셔너리 초기화
    travel_times = {i: [] for i in range(1, len(location_dicts) + 1)}

    # 각 위치 쌍에 대해 Google Maps Directions API를 호출하여 이동 시간 계산
    for j, loc in enumerate(location_dicts):
        so_lat = loc['so_lat']
        so_lng = loc['so_lng']

        # URL 파라미터 인코딩
        params = {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{so_lat},{so_lng}",
            'mode': how_to_go,
            'transit_routing_preference': 'fewer_transfers',
            'key': Client_Secret
        }
        endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
        url = endpoint + urllib.parse.urlencode(params)

        response = urllib.request.urlopen(url).read()
        response_json = json.loads(response)

        # 이동 시간 추출
        if response_json["status"] == "OK":
            travel_time_seconds = response_json["routes"][0]["legs"][0]["duration"]["value"]
            # 각 이동 시간에 대한 정보를 딕셔너리에 저장
            travel_times[j + 1].append({
                "so_id": loc['so_id'],  # 목적지 id
                "travel_time_seconds": travel_time_seconds  # 이동 시간 (초)
            })
        else:
            print("Error:", response_json["status"])
            print("URL:", url)  # 오류가 발생한 URL 출력
            print("Response:", response_json)  # 응답 출력

    # 목적지별 총 이동 시간을 계산
    total_travel_times = {loc['so_id']: 0 for loc in location_dicts}

    for i in travel_times:
        for time_info in travel_times[i]:
            so_id = time_info['so_id']
            travel_time_seconds = time_info['travel_time_seconds']
            total_travel_times[so_id] += travel_time_seconds

    # 총 이동 시간이 작은 10개의 so_id를 반환
    sorted_so_ids = sorted(total_travel_times, key=total_travel_times.get)[:10]
    print("Top 10 SO IDs with minimum total travel time:", sorted_so_ids)

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
    reservations = Reservation.objects.select_related('cus_email', 'so_id')
    context = {
        'reservations': reservations
    }
    return render(request, 'check_reservation.html', context)

# def customer_info(request, customer_id):
#     customer = get_object_or_404(Customer, id=customer_id)
#     return render(request, 'mypage.html', {'customer': customer})

def choose_func(request):
    if request.method == 'POST':
        finding_option = request.POST.get('finding_option')

        if finding_option == 'near_finding':
            try:
                customer = Customer.objects.get(cus_email=request.user.email)
                cus_latitude = customer.cus_latitude
                cus_longitude = customer.cus_lognitude
                return redirect('choose')  # 적절한 뷰로 리다이렉트
            except Customer.DoesNotExist:
                messages.error(request, 'Customer not found.')
                return redirect('choose_func')

        elif finding_option in ['together_finding', 'location_finding']:
            return redirect('location_view')  # address.html로 이동

    return render(request, 'choose_func.html')  # 기본적으로 폼을 다시 렌더링