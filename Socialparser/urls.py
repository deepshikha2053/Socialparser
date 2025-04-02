
from django.contrib import admin
from django.urls import path, include
from socialmfparser import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('socialmfparser.urls')),
    path('generate-report/', views.generate_forensic_report, name='generate_forensic_report'),
]
