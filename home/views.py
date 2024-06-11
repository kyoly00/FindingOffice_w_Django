from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Reservation, ShareOffice
from django.db.models import Count
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest

from urllib import parse
from urllib.request import urlopen, Request as URLRequest
from urllib.parse import urlencode
from urllib.error import HTTPError
import pprint

import json
import numpy as np
from scipy.linalg import eig

import os
from dotenv import load_dotenv

load_dotenv()

Client_ID = os.getenv('CLIENT_ID')
Client_KEY = os.getenv('CLIENT_KEY')
google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')

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

def get_addresses_in_range(latitudes, longitudes):
    # 특정 범위 내의 데이터 조회
    min_lat = min(map(float, latitudes))
    max_lat = max(map(float, latitudes))
    min_lng = min(map(float, longitudes))
    max_lng = max(map(float, longitudes))

    # 데이터베이스에서 범위 내의 데이터를 가져옵니다.
    locations = ShareOffice.objects.filter(
        so_latitude__lte=max_lat,
        so_latitude__gte=min_lat,
        so_longitude__lte=max_lng,
        so_longitude__gte=min_lng
    )

    # 공유오피스의 id, 위도, 경도를 딕셔너리에 저장
    locations_dicts = [
        {
            "so_id": location.id,
            "so_lat": float(location.so_latitude),
            "so_lng": float(location.so_longitude)
        }
        for location in locations
    ]

    return locations_dicts

def finding_optimal(latitudes, longitudes):
    location_dicts = get_addresses_in_range(latitudes, longitudes)

    # 이동 시간을 저장할 딕셔너리 초기화
    travel_times = {i: [] for i in range(1, len(location_dicts) + 1)}

    # 각 위치 쌍에 대해 Google Maps Directions API를 호출하여 이동 시간 계산
    for i in range(len(latitudes)):
        for j, loc in enumerate(location_dicts):
            so_lat = loc['so_lat']
            so_lng = loc['so_lng']

            # URL 파라미터 인코딩
            params = {
                'origin': f"{latitudes[i]},{longitudes[i]}",
                'destination': f"{so_lat},{so_lng}",
                'mode': 'transit',
                'transit_routing_preference': 'fewer_transfers',
                'key': google_map_api_key
            }
            endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
            url = endpoint + urlencode(params)

            response = urlopen(url).read()
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
        return sorted_so_ids

def location_view(request):
    addresses = []
    people_counts = []

    # location.html에서 주소와 인원수 받아와 리스트로 저장
    if request.method == 'POST':
        count = 1
        while True:
            address_key = f'address{count}'
            people_key = f'people{count}'

            address = request.POST.get(address_key)
            people = request.POST.get(people_key)

            if address and people:
                addresses.append(address)
                people_counts.append(int(people))
            else:
                break

            count += 1

        all_latitude = []
        all_longitude = []

        for i in range(len(addresses)):
            address = addresses[i]
            api_url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query='
            add_urlenc = parse.quote(address)  # URL Encoding
            url = api_url + add_urlenc

            loc_request = URLRequest(url)
            loc_request.add_header('X-NCP-APIGW-API-KEY-ID', Client_ID)
            loc_request.add_header('X-NCP-APIGW-API-KEY', Client_KEY)

            try:
                response = urlopen(loc_request)

            except HTTPError as e:
                print('HTTP Error')
                latitude, longitude = None, None

            else:
                rescode = response.getcode()

                if rescode == 200:
                    response_body = response.read().decode('utf-8')
                    response_body = json.loads(response_body)

                    if not response_body['addresses']:
                        print('No result')
                    else:
                        latitude = response_body['addresses'][0]['y']
                        longitude = response_body['addresses'][0]['x']
                        for j in range(people_counts[i]):
                            all_latitude.append(latitude)
                            all_longitude.append(longitude)
                else:
                    print(f'Response error, rescode:{rescode}')
                    latitude, longitude = None, None

        # 데이터가 비어 있지 않을 때만 최적 위치를 찾기
        if all_latitude and all_longitude:
            optimal_shareoffices = finding_optimal(all_latitude, all_longitude)
        else:
            optimal_shareoffices = []

        # 세션에 offices 저장
        request.session['offices'] = optimal_shareoffices
        print(optimal_shareoffices)

        # recommend_offices 함수로 리디렉션
        return redirect('choose')

    return render(request, 'location.html')

def alone_location(request):
    return render(request, 'alone_location.html')

def recommendation(request):
    return render(request, 'recommendation.html')

def enterinfo(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected')
        # selected_items 예시: ['John Doe, 30', 'Jane Smith, 25']c

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

        address = cus_address
        api_url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query='
        add_urlenc = parse.quote(address)  # URL Encoding
        url = api_url + add_urlenc

        request = URLRequest(url)
        request.add_header('X-NCP-APIGW-API-KEY-ID', Client_ID)
        request.add_header('X-NCP-APIGW-API-KEY', Client_KEY)

        try:
            response = urlopen(request)

        except HTTPError as e:
            print('HTTP Error')
            latitude, longitude = None, None

        else:
            rescode = response.getcode()

            if rescode == 200:
                response_body = response.read().decode('utf-8')
                response_body = json.loads(response_body)

                if response_body['addresses'] == []:
                    print('No result')
                else:
                    latitude = response_body['addresses'][0]['y']
                    longitude = response_body['addresses'][0]['x']

                    # 새로운 Customer 인스턴스 생성 및 저장
                    customer = Customer(
                        cus_password=cus_password,
                        cus_name=cus_name,
                        cus_gender=cus_gender,
                        cus_email=cus_email,
                        cus_company=cus_company,
                        cus_phone=cus_phone,
                        cus_address=cus_address,
                        cus_latitude=latitude,
                        cus_longitude=longitude
                    )
                    customer.save()

            else:
                print(f'Response error, rescode:{rescode}')
                latitude, longitude = None, None

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

def choose(request):
    if request.method == 'GET':
        return render(request, 'choose.html')
    elif request.method == 'POST':
        selected_facilities = request.POST.getlist('facilities')
        request.session['selected_facilities'] = selected_facilities  # 세션에 저장
        return render(request, 'enter_weights.html', {'selected_facilities': selected_facilities})

def recommend_offices(offices, selected_facilities, weights):
    facility_mapping = {
        'ac': 'so_ac',
        'cafe': 'so_cafe',
        'printer': 'so_printer',
        'parcel_sndng_posbl': 'so_parcel_sndng_posbl',
        'doorlock': 'so_doorlock',
        'elect_outlet': 'so_elect_outlet',
        'fax': 'so_fax',
        'n24h_oper': 'so_n24h_oper',
        'n365d_oper': 'so_n365d_oper',
        'heater': 'so_heater',
        'parkng_posbl': 'so_parkng_posbl',
        'cmnuse_lounge': 'so_cmnuse_lounge',
        'cmnuse_kitchen': 'so_cmnuse_kitchen',
        'rooftop': 'so_rooftop',
        'refreshments_provd': 'so_refreshments_provd',
        'indivdl_locker': 'so_indivdl_locker',
        'tv': 'so_tv',
        'wboard': 'so_wboard',
        'wifi': 'so_wifi',
        'bath_fclty': 'so_bath_fclty'
    }

    scores = []

    for office in offices:
        score = 0
        office_facilities = []
        for facility in selected_facilities:
            model_field = facility_mapping[facility]
            if getattr(office, model_field):
                score += weights[facility]
                office_facilities.append(facility)
        office.facilities = office_facilities
        scores.append((office, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [office for office, score in scores]

def calculate_weights(matrix):
    if not matrix.shape[0] == matrix.shape[1]:
        raise ValueError("Input matrix must be square.")
    if not np.issubdtype(matrix.dtype, np.number):
        raise ValueError("Matrix data type must be numeric.")

    eigvals, eigvecs = eig(matrix)
    eigvals = eigvals.real
    max_eigval_index = np.argmax(eigvals)
    weights = eigvecs[:, max_eigval_index].real
    if np.sum(weights) == 0:
        raise ValueError("Sum of weights is zero, cannot normalize.")
    weights = weights / np.sum(weights)
    return weights

def calculate_weights_view(request):
    office_ids = request.session.get('offices', [])
    offices = ShareOffice.objects.filter(id__in=office_ids)

    if request.method == 'POST':
        selected_facilities = request.session.get('selected_facilities', [])
        num_facilities = len(selected_facilities)
        matrix = np.ones((num_facilities, num_facilities), dtype=float)

        for i, facility1 in enumerate(selected_facilities):
            for j, facility2 in enumerate(selected_facilities):
                if i < j:
                    try:
                        importance = float(request.POST.get(f'importance_{facility1}_{facility2}', 1))
                        if importance == 0:
                            return HttpResponseBadRequest("중요도는 0이 될 수 없습니다.")
                        matrix[i, j] = importance
                        matrix[j, i] = 1 / importance
                    except ValueError:
                        return HttpResponseBadRequest("중요도는 숫자여야 합니다.")

        try:
            weights = calculate_weights(matrix)
        except ValueError as e:
            return render(request, 'error.html', {'error_message': str(e)})

        facility_weights = dict(zip(selected_facilities, weights))
        recommended_offices = recommend_offices(offices, selected_facilities, facility_weights)
        return render(request, 'recommendation.html', {'offices': recommended_offices, 'user_selected_facilities': selected_facilities})

    return render(request, 'choose.html')

def delete_reservation(request, id):
    reservation = Reservation.objects.get(id=id)

    if request.method == "POST":
        reservation.delete()
        return redirect('reservation_list')

    return render(request, 'delete_confirm.html', {'reservation':reservation})