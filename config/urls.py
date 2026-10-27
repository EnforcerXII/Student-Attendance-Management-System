from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"}, status=200)
    except Exception as exc:
        return JsonResponse({"status": "unhealthy", "database": str(exc)}, status=503)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("health/", health_check, name="health_check"),
    path("administration/", include("administration.urls")),
    path("", include("accounts.urls")),
    path("attendance/", include("attendance.urls")),
]