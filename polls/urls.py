from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
  path('trend', views.trend, name='trend'),
  path('trend_submit/', views.trend_submit, name='trend_submit'),
  path('algos/', views.algos, name='algos'),
  path('algos/<int:algo_id>', views.algo_detail, name='algo_detail'),
]