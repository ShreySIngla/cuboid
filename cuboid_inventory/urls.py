from django.urls import path
from .views import *
from . import views

urlpatterns = [
    # ... Your existing URL patterns
    path('register',register_user, name='register-user'),
    path('login',login_user, name='login-user'),
    path('logout', views.logout_view, name='logout'),
    path('add-box',add_box, name='add-box'),
    path('update-box',update_box, name='update-box'),
    path('list-all-box',list_all_boxes, name='list-all-box'),
    path('list-my-box',list_my_boxes, name='list-my-box'),
    path('delete-box',delete_box, name='delete-box'),
    
]