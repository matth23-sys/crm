from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from core.db.routers import MultiTenantDatabaseRouter
from core.db.tenant_context import clear_current_tenant, tenant_context


class PlatformModel:
    _meta = SimpleNamespace(app_label="tenants")


class TenantModel:
    _meta = SimpleNamespace(app_label="clients")


@override_settings(
    MULTI_TENANCY_PLATFORM_DB_ALIAS="default",
    MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX="tenant_",
    MULTI_TENANCY_STRICT_ROUTING=True,
    PLATFORM_APP_LABELS={"tenants", "subscriptions", "platform_accounts", "provisioning"},
    TENANT_APP_LABELS={"clients", "accounts", "workorders"},
)
class RouterTests(SimpleTestCase):
    def setUp(self):
        self.router = MultiTenantDatabaseRouter()

    def tearDown(self):
        clear_current_tenant()

    def test_platform_model_routes_to_default(self):
        self.assertEqual(self.router.db_for_read(PlatformModel), "default")
        self.assertEqual(self.router.db_for_write(PlatformModel), "default")

    def test_tenant_model_routes_to_active_tenant_alias(self):
        tenant = {"id": 1, "slug": "acme"}
        with tenant_context(tenant=tenant, db_alias="tenant_acme"):
            self.assertEqual(self.router.db_for_read(TenantModel), "tenant_acme")
            self.assertEqual(self.router.db_for_write(TenantModel), "tenant_acme")

    def test_allow_migrate(self):
        self.assertTrue(self.router.allow_migrate("default", "tenants"))
        self.assertFalse(self.router.allow_migrate("tenant_acme", "tenants"))
        self.assertTrue(self.router.allow_migrate("tenant_acme", "clients"))
        self.assertFalse(self.router.allow_migrate("default", "clients"))