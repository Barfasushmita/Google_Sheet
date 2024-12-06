from django.urls import path
from .views import fetch_data
from .views import index

urlpatterns = [
    path('data/', fetch_data, name='fetch_data'),
    path('index/', index, name='index'),
]
