from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('alone/', views.alone, name='alone'),
    path('together/', views.together, name='together'),
    path('login/', views.login, name='login'),
    path('mypage/', views.my_page, name='mypage'),
    path('location/', views.location_view, name='location'),
    path('choose/', views.choose, name='choose'),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('enterinfo/', views.enterinfo, name='enterinfo'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('list/', views.reservation_list, name='reservation_list'),
    # path('customer/<int:customer_id>/', views.customer_info, name='customer_info'),
    path('logout/', views.logout_view, name='logout'),
]