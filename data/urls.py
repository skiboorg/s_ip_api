from django.urls import path,include
from . import views

urlpatterns = [
    path('items', views.GetItems.as_view()),
    path('item', views.GetItem.as_view()),

]
