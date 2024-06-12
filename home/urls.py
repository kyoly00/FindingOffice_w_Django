from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('alone/', views.alone, name='alone'),
    path('together/', views.together, name='together'),
    path('login/', views.login, name='login'),
    path('mypage/', views.my_page, name='mypage'),
    path('update_customer/', views.update_customer, name='update_customer'),
    path('delete_customer/', views.delete_customer, name='delete_customer'),
    path('location/', views.location_view, name='location'),
    path('choose/', views.choose, name='choose'),
    path('calculate_weights/', views.calculate_weights_view, name='calculate_weights'),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('enterinfo/', views.enterinfo, name='enterinfo'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('list/', views.reservation_list, name='reservation_list'),
    path('logout/', views.logout_view, name='logout'),
    path('ranking/', views.ranking, name='ranking'),
    path('choose_func/', views.choose_func, name='choose_func'),
    path('alone_location/', views.alone_location, name='alone_location'),
    path('delete/<int:id>',views.delete_reservation,name='delete_reservation'),
]