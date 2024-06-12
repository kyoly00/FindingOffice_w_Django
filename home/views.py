from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from .forms import SignUpForm, LoginForm, ReservationForm, CustomerUpdateForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Customer, Reservation, ShareOffice
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from urllib import parse
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
import json
import numpy as np
from scipy.linalg import eig
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



def location_view(request):
    return render(request, 'location.html')

def alone_location(request):
    return render(request, 'alone_location.html')

# views.py
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
            print(f"Selected office ID: {selected_office_id}")
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
        request.session['selected_facilities'] = selected_facilities
        num_facilities = len(selected_facilities)
        rank_options = list(range(1, num_facilities + 1))        # 세션에 저장
        return render(request, 'enter_weights.html', {
            'selected_facilities': selected_facilities,
        'rank_options': rank_options})

def recommend_offices(selected_facilities, weights):
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

    all_offices = ShareOffice.objects.all()
    scores = []

    for office in all_offices:
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
        recommended_offices = recommend_offices(selected_facilities, facility_weights)

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