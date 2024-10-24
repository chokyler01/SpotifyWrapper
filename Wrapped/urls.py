from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wraps/', views.view_wraps, name='view_wraps'),
    path('wraps/delete/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('callback/', views.callback, name='callback'),
    path('spotify/link/', views.spotify_link, name='spotify_link'),  # Spotify link route
]
