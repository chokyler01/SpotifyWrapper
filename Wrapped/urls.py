# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wraps/', views.view_wraps, name='view_wraps'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('callback/', views.callback, name='callback'),
    path('spotify/link/', views.spotify_link, name='spotify_link'),
    path('contact/', views.contact_view, name='contact'),
    path('profile/', views.profile_view, name='profile'),
    path('choose_time/', views.choose_wrap_time, name='choose_wrap_time'),
    path('add_friend/', views.add_friend_view, name='add_friend'),
    path('wrap/<int:wrap_id>/toggle_visibility/', views.update_wrap_visibility, name='toggle_visibility'),
    path('shared_wraps/', views.view_shared_wraps, name='shared_wraps'),
]
