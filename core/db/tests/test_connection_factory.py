from django.test import SimpleTestCase, override_settings

from core.db.connection_factory import build_tenant_db_alias, build_tenant_db_config


@override_settings(
    MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX="tenant_",
    MULTI_TENANCY_TENANT_DB_TEMPLATE={
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
    },
)
class ConnectionFactoryTests(SimpleTestCase):
    def test_build_tenant_db_alias(self):
        tenant = {"slug": "acme-roofing"}
        self.assertEqual(build_tenant_db_alias(tenant), "tenant_acme_roofing")

    def test_build_tenant_db_config(self):
        tenant = {
            "slug": "acme",
            "db_name": "crm_tenant_acme",
            "db_user": "acme_user",
            "db_password": "secret",
        }

        config = build_tenant_db_config(tenant)

        self.assertEqual(config["NAME"], "crm_tenant_acme")
        self.assertEqual(config["USER"], "acme_user")
        self.assertEqual(config["PASSWORD"], "secret")
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")