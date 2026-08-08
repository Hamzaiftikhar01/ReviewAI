from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def business_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'business'):
            messages.warning(request, "Please set up your business details first.")
            return redirect('business_setup')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
