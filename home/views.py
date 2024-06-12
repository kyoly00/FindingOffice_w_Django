from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, ReservationForm, CustomerUpdateForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Reservation, ShareOffice
from django.db.models import Count
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest
from .forms import ReservationForm

from urllib import parse
from urllib.request import urlopen, Request as URLRequest
from urllib.parse import urlencode
from urllib.error import HTTPError
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

import pprint
import math

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
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)  # 로그인
                    request.session['cus_email'] = email # 세션에 사용자 이메일 저장

                customer = Customer.objects.get(cus_email=email)
                if check_password(password, customer.cus_password):
                    # 로그인 성공 (세션에 사용자 정보 저장)
                    request.session['cus_email'] = email
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
    customer_email = request.session.get('cus_email')
    if not customer_email:
        return redirect('login')  # 로그인되어 있지 않으면 로그인 페이지로 리디렉션

    try:
        customer = Customer.objects.get(cus_email=customer_email)
    except Customer.DoesNotExist:
        return redirect('login')  # 고객 정보가 없으면 로그인 페이지로 리디렉션

    return render(request, 'mypage.html', {'customer': customer})

def update_customer(request):
    customer_email = request.session.get('cus_email')
    if not customer_email:
        return redirect('login')

    try:
        customer = Customer.objects.get(cus_email = customer_email)
    except Customer.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, '회원 정보가 성공적으로 수정되었습니다.')
            return redirect('mypage')

        else:
            messages.error(request,'유효하지 않은 입력입니다.')
    else:
        form = CustomerUpdateForm(instance=customer)

    return render(request, 'update_customer.html', {'form':form})

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

        # 이동 시간 차이를 계산하기 위한 딕셔너리 초기화
        travel_time_diffs = {so_id: 0 for so_id in sorted_so_ids}

        # 각 지점의 이동 시간 차이를 계산
        for so_id in sorted_so_ids:
            times = [time_info['travel_time_seconds'] for i in travel_times for time_info in travel_times[i] if
                     time_info['so_id'] == so_id]
            if len(times) > 1:
                travel_time_diffs[so_id] = max(times) - min(times)
            else:
                travel_time_diffs[so_id] = float('inf')  # 이동 시간이 하나인 경우 차이를 무한대로 설정

        # 이동 시간 차이가 작은 순서대로 정렬
        sorted_final_so_ids = sorted(travel_time_diffs, key=travel_time_diffs.get)[:10]

        return sorted_final_so_ids


def address_to_lat_lng(addresses, people_counts):
    all_latitude = []
    all_longitude = []

    # people_counts가 정수일 경우 리스트로 변환
    if people_counts == 1:
        people_counts = [people_counts] * len(addresses)

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

                    if len(people_counts) == 1:
                        break

                    for j in range(people_counts[i]):
                        all_latitude.append(latitude)
                        all_longitude.append(longitude)
            else:
                print(f'Response error, rescode:{rescode}')
                latitude, longitude = None, None

    if len(people_counts) == 1: return latitude, longitude
    else: return all_latitude, all_longitude

def finding_together(request):
    addresses = []
    people_counts = []
    people_num = 0

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
                people_num += int(people)
            else:
                break

            count += 1

        all_latitude, all_longitude = address_to_lat_lng(addresses, people_counts)

        # 데이터가 비어 있지 않을 때만 최적 위치를 찾기
        if all_latitude and all_longitude:
            optimal_shareoffices = finding_optimal(all_latitude, all_longitude)
        else:
            optimal_shareoffices = []

        # 세션에 offices 저장
        request.session['offices_together'] = optimal_shareoffices
        request.session['all_people_num'] = people_num

        # recommend_offices 함수로 리디렉션
        return redirect('choose')

    return render(request, 'location.html')

def alone_location(request):
    try:
        # alone_location.html에서 주소와 인원수 받아와 리스트로 저장
        if request.method == 'POST':
            print(request.POST)
            address_key = f'address1'

            address = request.POST.get(address_key)

            finding_range = 5

            latitude, longitude = address_to_lat_lng([address], 1)

            optimal_shareoffices = finding_alone(latitude=latitude, longitude=longitude,
                                                 finding_range=finding_range)

            # 세션에 offices 저장
            request.session['offices_location'] = optimal_shareoffices

            return redirect('choose')
    except Customer.DoesNotExist:
        messages.error(request, 'Customer not found.')
        return redirect('choose_func')
    return render(request, 'alone_location.html')

def recommendation(request):
    if request.method == 'POST':
        selected_ids_str = request.POST.get('selected')
        selected_ids = int(selected_ids_str)
        print(selected_ids)
        request.session['selected_office_ids'] = selected_ids  # 선택한 오피스 ID를 세션에 저장
        selected_offices = ShareOffice.objects.filter(id=selected_ids)

        selected_data = [(office.id, office.so_name, office.so_address) for office in selected_offices]

        print(f"Selected office IDs: {selected_ids}")

        return render(request, 'enterinfo.html', {'selected_data': selected_data, 'form': ReservationForm()})

    return redirect('recommendation')

def enterinfo(request):
    selected_office_ids = request.session.get('selected_office_ids')
    if not selected_office_ids:
        messages.error(request, 'No office selected.')
        return redirect('recommendation')

    selected_offices = ShareOffice.objects.filter(id=selected_office_ids)
    selected_data = [(office.id, office.so_name, office.so_address) for office in selected_offices]

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        print(f"POST data: {request.POST}")  # 디버깅용 출력
        if form.is_valid():
            selected_office_id = request.POST.get('office_ids')
            try:
                selected_office = ShareOffice.objects.get(id=selected_office_id)
            except ShareOffice.DoesNotExist:
                messages.error(request, f"Office with ID {selected_office_id} does not exist.")
                return redirect('enterinfo')
              
            cus_email = request.session.get('cus_email')
            try:
                customer = Customer.objects.get(cus_email=cus_email)
            except Customer.DoesNotExist:
                messages.error(request, 'Customer does not exist.')
                return redirect('enterinfo')

            # 예약 데이터베이스에 저장
            reservation = form.save(commit=False)
            reservation.so_id = selected_office
            reservation.cus_email = customer  # ForeignKey로 연결된 Customer 객체 저장
            reservation.re_people = request.session.get('all_people_num')
            reservation.save()

            messages.success(request, '예약이 완료되었습니다.')  # 예약 성공 메시지 추가
            return redirect('choose_func')  # 예약 완료 후 리디렉션
        else:
            print(form.errors)
            messages.error(request, '유효하지 않은 입력입니다.')

    else:
        form = ReservationForm(initial={'office_ids': selected_office_ids})

    return render(request, 'enterinfo.html', {'form': form, 'selected_data': selected_data})


@login_required
def reservation_list(request):
    cus_email = request.session.get('cus_email')
    if cus_email:
        reservations = Reservation.objects.filter(cus_email__cus_email=cus_email).select_related('so_id')
    else:
        reservations = []
    context = {
        'reservations': reservations
    }
    return render(request, 'check_reservation.html', context)

def sign_up(request):
    if request.method == 'POST':
        cus_password = make_password(request.POST.get('cus_password'))
        cus_name = request.POST.get('cus_name')
        cus_gender = request.POST.get('cus_gender')
        cus_email = request.POST.get('cus_email')
        cus_company = request.POST.get('cus_company')
        cus_phone = request.POST.get('cus_phone')
        cus_address = request.POST.get('cus_address')

        address = [cus_address]
        latitude, longitude = address_to_lat_lng(address, 1)


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

        return redirect('login')

    return render(request, 'login_register.html')

# def check_reservation(request):
#     return render(request, 'check_reservation.html')

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

def finding_alone(latitude, longitude, finding_range):
    latitudes = []
    longitudes = []

    latitude = float(latitude)
    longitude = float(longitude)
    latitude_change = finding_range / 111.0
    longitude_change = finding_range / (111.0 * math.cos(math.radians(latitude)))

    latitudes.append(latitude + latitude_change)
    latitudes.append(latitude - latitude_change)
    longitudes.append(longitude + longitude_change)
    longitudes.append(longitude - longitude_change)

    print('latitudes: ', latitudes, 'longitudes: ', longitudes)
    location_dicts = get_addresses_in_range(latitudes, longitudes)

    # 이동 시간을 저장할 딕셔너리 초기화
    travel_times = {i: [] for i in range(1, len(location_dicts) + 1)}

    # 각 위치 쌍에 대해 Google Maps Directions API를 호출하여 이동 시간 계산
    for j, loc in enumerate(location_dicts):
        so_lat = loc['so_lat']
        so_lng = loc['so_lng']

        # URL 파라미터 인코딩
        params = {
            'origin': f"{latitude},{longitude}",
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

def choose_func(request):
    if request.method == 'POST':
        finding_option = request.POST.get('finding_option')
        if finding_option == 'near_finding':
            try:
                cus_email = request.session.get('cus_email')
                customer = Customer.objects.get(cus_email=cus_email)
                cus_latitude = customer.cus_latitude
                cus_longitude = customer.cus_longitude

                finding_range = 5

                optimal_shareoffices = finding_alone(latitude=cus_latitude, longitude=cus_longitude, finding_range=finding_range)
                print(optimal_shareoffices)

                # 세션에 offices_alone 저장
                request.session['offices_alone'] = optimal_shareoffices

                return redirect('choose')
            except Customer.DoesNotExist:
                messages.error(request, 'Customer not found.')
                return redirect('choose_func')

        elif finding_option == 'together_finding':
            return redirect('finding_together')

        elif finding_option == 'location_finding':
            return redirect('alone_location')


    return render(request, 'choose_func.html')

def choose(request):
    if request.method == 'GET':
        return render(request, 'choose.html')
    elif request.method == 'POST':
        selected_facilities = request.POST.getlist('facilities')
        request.session['selected_facilities'] = selected_facilities
        num_facilities = len(selected_facilities)
        rank_options = list(range(1, num_facilities + 1))        # 세션에 저장
        return render(request, 'enter_weights.html', {
            'selected_facilities': selected_facilities,
        'rank_options': rank_options})

def recommend_offices(request, selected_facilities, weights):
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

    if request.session.get('offices_alone'):
        office_ids = request.session.get('offices_alone', [])
    elif request.session.get('offices_together'):
        office_ids = request.session.get('offices_together', [])
    else:
        office_ids = request.session.get('offices_location', [])

    offices = ShareOffice.objects.filter(id__in=office_ids)
    scores = []

    for office in offices:
        score = 0
        office_facilities = []
        for facility in selected_facilities:
            model_field = facility_mapping.get(facility)
            if model_field and getattr(office, model_field):
                score += weights[facility]
                office_facilities.append(facility)
        office.facilities = office_facilities
        scores.append((office, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [office for office, score in scores]


def calculate_weights(request):
    if request.method == 'POST':
        selected_facilities = request.POST['selected_facilities'].split(',')
        num_facilities = len(selected_facilities)

        # 순위 수집 및 정렬
        ranks = []
        for facility in selected_facilities:
            rank = int(request.POST[f'rank_{facility}'])
            ranks.append((facility, rank))
        ranks.sort(key=lambda x: x[1])

        # 순위에 반비례하여 가중치 할당
        weights = np.array([1 / rank for facility, rank in ranks])

        # 가중치 정규화
        weights /= np.sum(weights)

        return render(request, 'recommendation.html',
                      {'weights': weights, 'facilities': [facility for facility, rank in ranks]})
    else:
        raise ValueError("지원되지 않는 요청 방법입니다.")


def calculate_weights_view(request):
    selected_facilities = request.session.get('selected_facilities', [])
    num_facilities = len(selected_facilities)

    if request.method == 'POST':
        ranks = []
        try:
            for facility in selected_facilities:
                rank = int(request.POST.get(f'rank_{facility}'))
                if rank <= 0 or rank > num_facilities:
                    return HttpResponseBadRequest("순위는 1부터 선택된 편의시설의 수까지여야 합니다.")
                ranks.append((facility, rank))
        except ValueError:
            return HttpResponseBadRequest("순위는 숫자여야 합니다.")

        ranks.sort(key=lambda x: x[1])

        # 순위에 반비례하여 가중치 할당
        weights = np.array([1 / rank for facility, rank in ranks])

        # 가중치 정규화
        weights /= np.sum(weights)

        facility_weights = dict(zip([facility for facility, rank in ranks], weights))

        # 추천 사무실 로직
        recommended_offices = recommend_offices(request, selected_facilities, facility_weights)

        return render(request, 'recommendation.html',
                      {'offices': recommended_offices, 'user_selected_facilities': selected_facilities})


    return render(request, 'choose.html')

def delete_reservation(request, id):
    reservation = Reservation.objects.get(id=id)

    if request.method == "POST":
        reservation.re_cancel = True
        reservation.re_cancel_date = timezone.now()
        reservation.save()
        return redirect('reservation_list')

    return render(request, 'delete_confirm.html', {'reservation':reservation})

def delete_customer(request):
    customer_email = request.session.get('cus_email')
    customer = Customer.objects.get(cus_email=customer_email)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, '회원 탈퇴가 완료되었습니다.')
        return redirect('login')  # 회원 탈퇴 후 메인 페이지로 리디렉션

    return render(request, 'cus_delete_confirm.html')