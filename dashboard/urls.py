from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('export.csv', views.export_history_csv, name='export_csv'),
    path('bulk-delete/', views.bulk_delete_scans, name='bulk_delete'),
]
