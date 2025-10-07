from typing import Iterable, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin


class RoleRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request: HttpRequest, view_func, view_args: Iterable, view_kwargs: dict) -> Optional[HttpResponse]:
        # Views can set allowed_roles = {"manager", "qa", "developer"}
        allowed_roles = getattr(view_func, 'allowed_roles', None)
        if allowed_roles is None:
            return None
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        if user.user_type not in allowed_roles:
            return JsonResponse({"detail": "Forbidden for role"}, status=403)
        return None
