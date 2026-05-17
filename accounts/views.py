import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .oracle_auth import SESSION_KEY, call_get_user_detail

logger = logging.getLogger(__name__)


def login_view(request):
    if request.session.get(SESSION_KEY):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            info = call_get_user_detail(username, password)
        except Exception:
            logger.exception('Oracle auth error for username=%r', username)
            info = None

        if info:
            request.session[SESSION_KEY] = info
            return redirect(request.GET.get('next', 'dashboard'))

        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
