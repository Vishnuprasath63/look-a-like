from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.upload_view, name='upload'),
    path('results/<int:match_id>/', views.results_view, name='results'),
    path('history/', views.history_view, name='history'),
]
