from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm


class TruthLensLoginView(LoginView):
    template_name = 'auth/login.html'


class TruthLensLogoutView(LogoutView):
    next_page = '/'


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to TruthLens! Your account is ready.')
            return redirect('dashboard:home')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})
