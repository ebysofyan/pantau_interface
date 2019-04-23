from django.urls import path
from . import views

urlpatterns = [
    path('', views.PemiluPublicApiGenericView.as_view()),
    path('save', views.PemiluPostGenericView.as_view()),
    path('chart', views.PemiluChartApiView.as_view()),
]
