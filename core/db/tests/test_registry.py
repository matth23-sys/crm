# backend/core/db/tests/test_registry.py

from types import SimpleNamespace

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.db.registry import is_database_registered, register_tenant_database


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "crm_platform",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    },
    MULTI_TENANCY_PLATFORM_DB_ALIAS="default",
    MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX="tenant_",
)
class TenantRegistryTests(SimpleTestCase):
    def test_register_tenant_database(self):
        tenant = SimpleNamespace(
            subdomain="acme",
            db_name="crm_tenant_acme",
            db_user="postgres",
            db_password="postgres",
            db_host="127.0.0.1",
            db_port="5432",
        )

        alias = register_tenant_database(tenant)

        self.assertEqual(alias, "tenant_acme")
        self.assertTrue(is_database_registered(alias))
        self.assertIn(alias, settings.DATABASES)