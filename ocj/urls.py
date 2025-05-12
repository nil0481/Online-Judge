from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path("",index,name='f'),
    path('home/',index,name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('problems/', problems_view, name='problems'),
    path('problems/<int:pk>/', problem_detail),
    path('submission/', submission,name='submission'),
    path('submission/<int:pk>/', submission_detail),
    # path('problems/<int:pk>/run/', execute),
    path('problems/<int:problem_id>/verdict/', verdictPage, name='verdict'),
]
