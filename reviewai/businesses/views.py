from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BusinessForm
from .models import Business

@login_required
def business_setup_view(request):
    # If the user already has a business, redirect to dashboard
    if hasattr(request.user, 'business'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            messages.success(request, f"Business '{business.name}' has been successfully created!")
            return redirect('dashboard')
    else:
        form = BusinessForm()
        
    return render(request, 'businesses/setup.html', {'form': form})

@login_required
def business_settings_view(request):
    # Enforce having a business
    if not hasattr(request.user, 'business'):
        return redirect('business_setup')
        
    business = request.user.business
    
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, "Business settings updated successfully.")
            return redirect('business_settings')
    else:
        form = BusinessForm(instance=business)
        
    return render(request, 'businesses/settings.html', {'form': form, 'business': business})
