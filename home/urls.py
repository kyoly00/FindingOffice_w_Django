from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('alone/', views.alone, name='alone'),
    path('together/', views.together, name='together'),
    path('login/', views.login, name='login'),
    path('mypage/', views.mypage, name='mypage'),
]