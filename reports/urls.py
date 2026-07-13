from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('<uuid:scan_id>/download/', views.download_report, name='download_report'),
]
