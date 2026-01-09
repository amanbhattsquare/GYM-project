from django.shortcuts import redirect
from django.urls import reverse
from apps.superadmin.models import Gym
from django.conf import settings

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to admin, superadmin, and static/media files without a gym_id
        if (
            request.path.startswith('/admin/') or
            request.path.startswith('/superadmin/') or
            request.path.startswith(settings.STATIC_URL) or
            request.path.startswith(settings.MEDIA_URL)
        ):
            return self.get_response(request)

        # Allow access to login/logout pages
        # Assuming login/logout URLs are named 'login' and 'logout'
        login_url = reverse('login')
        logout_url = reverse('logout')
        index_url = reverse('index')
        if request.path in [login_url, logout_url, index_url]:
            return self.get_response(request)

        gym_id = request.session.get('gym_id')
        role = request.session.get('role')

        if role == 'superadmin':
            request.gym = None
            return self.get_response(request)

        if not gym_id:
            return redirect(login_url)

        try:
            gym = Gym.objects.get(id=gym_id)
            request.gym = gym
        except Gym.DoesNotExist:
            return redirect(login_url)

        response = self.get_response(request)
        return response