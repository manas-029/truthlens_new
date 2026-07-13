from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_upload, name='scan_upload'),
    path('scan/url/', views.scan_from_url, name='scan_from_url'),
    path('scan/<uuid:scan_id>/', views.scan_result, name='scan_result'),
    path('scan/<uuid:scan_id>/status/', views.scan_status, name='scan_status'),
    path('scan/<uuid:scan_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('scan/<uuid:scan_id>/delete/', views.delete_scan, name='delete_scan'),
    path('live-check/', views.live_check, name='live_check'),
]
