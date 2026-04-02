from __future__ import annotations

from django.conf import settings

from .tenant_context import get_current_tenant_db_alias


class MultiTenantDatabaseRouter:
    """
    Platform apps -> default/platform DB
    Tenant apps   -> current tenant DB alias
    """

    DEFAULT_PLATFORM_SYSTEM_APP_LABELS = {
        "admin",
        "auth",
        "contenttypes",
        "sessions",
    }

    def _platform_alias(self) -> str:
        return settings.MULTI_TENANCY_PLATFORM_DB_ALIAS

    def _platform_labels(self) -> set[str]:
        return set(getattr(settings, "PLATFORM_APP_LABELS", set())) | set(
            getattr(
                settings,
                "MULTI_TENANCY_PLATFORM_SYSTEM_APP_LABELS",
                self.DEFAULT_PLATFORM_SYSTEM_APP_LABELS,
            )
        )

    def _tenant_labels(self) -> set[str]:
        return set(getattr(settings, "TENANT_APP_LABELS", set()))

    def _tenant_prefix(self) -> str:
        return settings.MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX

    def _is_platform_app(self, app_label: str) -> bool:
        return app_label in self._platform_labels()

    def _is_tenant_app(self, app_label: str) -> bool:
        return app_label in self._tenant_labels()

    def _instance_db(self, hints: dict) -> str | None:
        instance = hints.get("instance")
        if instance is not None and getattr(instance._state, "db", None):
            return instance._state.db
        return None

    def _resolve_tenant_alias(self) -> str | None:
        required = getattr(settings, "MULTI_TENANCY_STRICT_ROUTING", True)
        return get_current_tenant_db_alias(required=required)

    def db_for_read(self, model, **hints):
        sticky_db = self._instance_db(hints)
        if sticky_db:
            return sticky_db

        app_label = model._meta.app_label

        if self._is_platform_app(app_label):
            return self._platform_alias()

        if self._is_tenant_app(app_label):
            return self._resolve_tenant_alias()

        return self._platform_alias()

    def db_for_write(self, model, **hints):
        sticky_db = self._instance_db(hints)
        if sticky_db:
            return sticky_db

        app_label = model._meta.app_label

        if self._is_platform_app(app_label):
            return self._platform_alias()

        if self._is_tenant_app(app_label):
            return self._resolve_tenant_alias()

        return self._platform_alias()

    def allow_relation(self, obj1, obj2, **hints):
        db1 = obj1._state.db or self.db_for_read(obj1.__class__, instance=obj1)
        db2 = obj2._state.db or self.db_for_read(obj2.__class__, instance=obj2)

        if db1 == db2:
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if self._is_platform_app(app_label):
            return db == self._platform_alias()

        if self._is_tenant_app(app_label):
            return db.startswith(self._tenant_prefix())

        return db == self._platform_alias()