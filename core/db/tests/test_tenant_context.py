# backend/core/db/tests/test_tenant_context.py

from types import SimpleNamespace

from django.test import SimpleTestCase

from core.db.tenant_context import (
    clear_current_tenant,
    get_current_tenant,
    get_current_tenant_alias,
    has_current_tenant,
    tenant_context,
)


class TenantContextTests(SimpleTestCase):
    def tearDown(self):
        clear_current_tenant()

    def test_tenant_context_sets_and_clears_values(self):
        tenant = SimpleNamespace(id=1, subdomain="acme")

        self.assertFalse(has_current_tenant())
        self.assertIsNone(get_current_tenant())
        self.assertIsNone(get_current_tenant_alias())

        with tenant_context(tenant=tenant, db_alias="tenant_acme"):
            self.assertTrue(has_current_tenant())
            self.assertEqual(get_current_tenant(), tenant)
            self.assertEqual(get_current_tenant_alias(), "tenant_acme")

        self.assertFalse(has_current_tenant())
        self.assertIsNone(get_current_tenant())
        self.assertIsNone(get_current_tenant_alias())


        