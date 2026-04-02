from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db import close_old_connections, connections

from .connection_factory import build_tenant_db_alias, build_tenant_db_config
from .exceptions import (
    TenantConnectionNotRegisteredError,
    TenantConnectionRegistrationError,
)

logger = logging.getLogger(__name__)


def is_connection_registered(alias: str) -> bool:
    return alias in connections.databases


def register_tenant_connection(tenant: Any, *, overwrite: bool = False) -> str:
    alias = build_tenant_db_alias(tenant)
    db_config = build_tenant_db_config(tenant)

    if is_connection_registered(alias) and not overwrite:
        return alias

    if is_connection_registered(alias) and overwrite:
        close_connection(alias, forget_alias=False)

    connections.databases[alias] = db_config
    settings.DATABASES[alias] = db_config

    logger.debug("Tenant db connection registered: alias=%s", alias)
    return alias


def get_connection_settings(alias: str) -> dict:
    if alias not in connections.databases:
        raise TenantConnectionNotRegisteredError(
            f"Tenant connection alias '{alias}' is not registered."
        )
    return connections.databases[alias]


def close_connection(alias: str, *, forget_alias: bool = False) -> None:
    if alias not in connections.databases and not forget_alias:
        raise TenantConnectionNotRegisteredError(
            f"Tenant connection alias '{alias}' is not registered."
        )

    if alias in connections.databases:
        connection = connections[alias]
        connection.close()

        # Django cachea wrappers de conexión internamente.
        # Centralizamos aquí ese detalle para no dispersar acoplamiento interno.
        storage = getattr(connections, "_connections", None)
        if storage is not None and hasattr(storage, alias):
            delattr(storage, alias)

    if forget_alias:
        connections.databases.pop(alias, None)
        settings.DATABASES.pop(alias, None)

    close_old_connections()


def unregister_tenant_connection(alias: str) -> None:
    platform_alias = settings.MULTI_TENANCY_PLATFORM_DB_ALIAS
    if alias == platform_alias:
        raise TenantConnectionRegistrationError(
            f"Refusing to unregister the platform database alias '{platform_alias}'."
        )

    close_connection(alias, forget_alias=True)
    logger.debug("Tenant db connection unregistered: alias=%s", alias)