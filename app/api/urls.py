from django.urls import path
from . import views

urlpatterns = [
    path('', views.PemiluPublicApiGenericView.as_view()),
    path('save', views.PemiluPostGenericView.as_view()),
    path('chart/range', views.PemiluChartRangeApiView.as_view()),
    path('chart/acc', views.PemiluChartAccumulationApiView.as_view()),
]
