from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wraps/', views.view_wraps, name='view_wraps'),
    #path('wraps/delete/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('callback/', views.callback, name='callback'),
    path('spotify/link/', views.spotify_link, name='spotify_link'),  # Spotify link route
    path('contact/', views.contact_view, name='contact'),  # Contact Developers route
    path('profile/', views.profile_view, name='profile'),
    path('choose_time/', views.choose_wrap_time, name='choose_wrap_time'),
    path('view_old_wrap/<int:wrap_id>/', views.view_old_wrap, name='view_old_wrap'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('friends/', views.friends_page, name='friends_page'),
    path('friends/<int:friend_id>/wraps/', views.view_friends_old_wrap, name='view_friends_old_wrap'),
    path('game/song_guess/', views.song_guess_game, name='song_guess_game'),
]
