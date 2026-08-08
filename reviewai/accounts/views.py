from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegistrationForm, LoginForm, ProfileForm
from businesses.models import Business

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to ReviewAI, {user.full_name}! Let's set up your business.")
            return redirect('business_setup')
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Check if business is set up
                if hasattr(user, 'business'):
                    messages.success(request, f"Welcome back, {user.full_name}!")
                    return redirect('dashboard')
                else:
                    messages.warning(request, "Please set up your business details first.")
                    return redirect('business_setup')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        
        # Check which form was submitted
        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile details have been updated.")
                return redirect('profile_view')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, "Your password has been changed successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "Password change failed. Please review the errors below.")
    else:
        profile_form = ProfileForm(instance=user)
        password_form = PasswordChangeForm(user)
        
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/profile.html', context)
