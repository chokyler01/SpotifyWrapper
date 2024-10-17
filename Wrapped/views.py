from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import SpotifyWrap



def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('view_wraps')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('view_wraps')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')


@login_required
def view_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return render(request, 'wraps.html', {'wraps': wraps})


@login_required
def delete_wrap(request, wrap_id):
    wrap = SpotifyWrap.objects.get(id=wrap_id, user=request.user)
    if wrap:
        wrap.delete()
    return redirect('view_wraps')


@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('register')
    return render(request, 'delete_account.html')
