from django.urls import path
from . import views

urlpatterns = [
    path('lpu-recipes/', views.SendLpuRecipesView.as_view()),
    path('pharm-mol/', views.SendPharmMolView.as_view()),
]
