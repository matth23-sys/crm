# backend/config/api_urls.py

from django.http import JsonResponse
from django.urls import path


def api_root(_request):
    return JsonResponse(
        {
            "name": "CRM Multi-Tenant API",
            "version": "v1",
            "status": "ok",
            "message": "API base operativa",
        }
    )


def api_v1_health(_request):
    return JsonResponse(
        {
            "status": "ok",
            "version": "v1",
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("v1/health/", api_v1_health, name="api-v1-health"),

    # Aquí irán luego los módulos versionados, por ejemplo:
    # path("v1/platform/tenants/", include("apps.platform.tenants.api.v1.urls")),
    # path("v1/platform/subscriptions/", include("apps.platform.subscriptions.api.v1.urls")),
    # path("v1/accounts/", include("apps.tenant.accounts.api.v1.urls")),
    # path("v1/clients/", include("apps.tenant.clients.api.v1.urls")),
    # path("v1/services/", include("apps.tenant.service_catalog.api.v1.urls")),
    # path("v1/workorders/", include("apps.tenant.workorders.api.v1.urls")),
]