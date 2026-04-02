# backend/core/db/tests/test_connection_factory.py

from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from core.db.connection_factory import (
    build_tenant_database_config,
    build_tenant_db_alias,
)


@override_settings(
    MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX="tenant_",
)
class ConnectionFactoryTests(SimpleTestCase):
    def test_build_tenant_db_alias_uses_subdomain(self):
        tenant = SimpleNamespace(subdomain="Acme Roofing")
        self.assertEqual(build_tenant_db_alias(tenant), "tenant_acme_roofing")

    def test_build_tenant_database_config(self):
        tenant = SimpleNamespace(
            db_name="crm_tenant_acme",
            db_user="postgres",
            db_password="postgres",
            db_host="127.0.0.1",
            db_port="5432",
        )

        config = build_tenant_database_config(tenant)

        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["NAME"], "crm_tenant_acme")
        self.assertEqual(config["USER"], "postgres")
        self.assertEqual(config["PASSWORD"], "postgres")
        self.assertEqual(config["HOST"], "127.0.0.1")
        self.assertEqual(config["PORT"], "5432")
        self.assertTrue(config["ATOMIC_REQUESTS"])