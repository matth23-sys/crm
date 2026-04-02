# backend/core/db/routers.py

from __future__ import annotations

from django.conf import settings

from .exceptions import TenantContextMissingError
from .tenant_context import get_current_tenant_alias


class PlatformTenantRouter:
    """
    Router principal del proyecto.

    Reglas:
    - apps de plataforma -> default
    - apps tenant -> alias del tenant activo
    - sin tenant activo -> error si strict routing está activado
    """

    def db_for_read(self, model, **hints):
        return self._route_model(model)

    def db_for_write(self, model, **hints):
        return self._route_model(model)

    def allow_relation(self, obj1, obj2, **hints):
        db1 = getattr(obj1._state, "db", None)
        db2 = getattr(obj2._state, "db", None)

        if not db1 or not db2:
            return None

        if db1 == db2:
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        platform_app_labels = set(getattr(settings, "PLATFORM_APP_LABELS", set()))
        tenant_app_labels = set(getattr(settings, "TENANT_APP_LABELS", set()))
        platform_db_alias = getattr(settings, "MULTI_TENANCY_PLATFORM_DB_ALIAS", "default")
        tenant_prefix = getattr(settings, "MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX", "tenant_")

        if app_label in platform_app_labels:
            return db == platform_db_alias

        if app_label in tenant_app_labels:
            return db != platform_db_alias and db.startswith(tenant_prefix)

        return None

    def _route_model(self, model):
        app_label = model._meta.app_label

        platform_app_labels = set(getattr(settings, "PLATFORM_APP_LABELS", set()))
        tenant_app_labels = set(getattr(settings, "TENANT_APP_LABELS", set()))
        platform_db_alias = getattr(settings, "MULTI_TENANCY_PLATFORM_DB_ALIAS", "default")
        strict_routing = getattr(settings, "MULTI_TENANCY_STRICT_ROUTING", True)

        if app_label in platform_app_labels:
            return platform_db_alias

        if app_label in tenant_app_labels:
            alias = get_current_tenant_alias(required=False)

            if alias:
                return alias

            if strict_routing:
                raise TenantContextMissingError(
                    f"No hay tenant activo para enrutar el modelo '{model.__name__}'."
                )

            return platform_db_alias

        return None