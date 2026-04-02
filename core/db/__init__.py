# backend/core/db/__init__.py

from .tenant_context import (
    TenantContextSnapshot,
    clear_current_tenant,
    get_current_tenant,
    get_current_tenant_alias,
    has_current_tenant,
    set_current_tenant,
    tenant_context,
)
from .connection_factory import (
    build_tenant_database_config,
    build_tenant_db_alias,
)
from .registry import (
    is_database_registered,
    register_tenant_database,
    unregister_tenant_database,
)

__all__ = [
    "TenantContextSnapshot",
    "clear_current_tenant",
    "get_current_tenant",
    "get_current_tenant_alias",
    "has_current_tenant",
    "set_current_tenant",
    "tenant_context",
    "build_tenant_database_config",
    "build_tenant_db_alias",
    "is_database_registered",
    "register_tenant_database",
    "unregister_tenant_database",
]