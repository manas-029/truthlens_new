from django.urls import path
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    path('datasets/', views.datasets_page, name='datasets'),
    path('models/', views.models_page, name='models'),
    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
]
