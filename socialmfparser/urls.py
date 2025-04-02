from django.urls import path
from . import views

urlpatterns = [
    path('generate-report/', views.generate_forensic_report, name='generate-report'),
]
