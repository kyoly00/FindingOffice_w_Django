from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from .forms import SignUpForm, LoginForm
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

def location_view(request):
    return render(request, 'location.html')

def alone_location(request):
    return render(request, 'alone_location.html')


# def recommendation(request):
#     return render(request, 'recommendation.html')

# views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import ShareOffice

@csrf_exempt
def enterinfo(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected')
        selected_offices = ShareOffice.objects.filter(id__in=selected_ids)
        selected_data = [(office.so_name, office.so_address) for office in selected_offices]

        return render(request, 'enterinfo.html', {'selected_data': selected_data})

    return redirect('recommendation')
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
        recommended_offices = recommend_offices(selected_facilities, facility_weights)
        return render(request, 'recommendation.html', {'offices': recommended_offices, 'user_selected_facilities': selected_facilities})

    return render(request, 'choose.html')

def delete_reservation(request, id):
    reservation = Reservation.objects.get(id=id)

    if request.method == "POST":
        reservation.delete()
        return redirect('reservation_list')

    return render(request, 'delete_confirm.html', {'reservation':reservation})