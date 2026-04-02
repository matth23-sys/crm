# backend/core/db/registry.py

from __future__ import annotations

from django.conf import settings
from django.db import connections

from .connection_factory import (
    build_tenant_database_config,
    build_tenant_db_alias,
)
from .exceptions import TenantDatabaseRegistrationError


def is_database_registered(alias: str) -> bool:
    return alias in settings.DATABASES


def register_tenant_database(
    tenant,
    *,
    alias: str | None = None,
    overwrite: bool = False,
) -> str:
    db_alias = alias or build_tenant_db_alias(tenant)
    default_alias = getattr(settings, "MULTI_TENANCY_PLATFORM_DB_ALIAS", "default")

    if db_alias == default_alias:
        raise TenantDatabaseRegistrationError(
            "El alias del tenant no puede ser igual al alias de plataforma."
        )

    if is_database_registered(db_alias) and not overwrite:
        return db_alias

    db_config = build_tenant_database_config(tenant)

    settings.DATABASES[db_alias] = db_config
    connections.databases[db_alias] = db_config

    return db_alias


def unregister_tenant_database(alias: str, *, close_connection: bool = True) -> None:
    default_alias = getattr(settings, "MULTI_TENANCY_PLATFORM_DB_ALIAS", "default")

    if alias == default_alias:
        raise TenantDatabaseRegistrationError(
            "No se puede remover el alias de la base principal de plataforma."
        )

    try:
        if close_connection and alias in connections:
            connections[alias].close()
    except Exception as exc:
        raise TenantDatabaseRegistrationError(
            f"No se pudo cerrar la conexión para el alias '{alias}'."
        ) from exc

    settings.DATABASES.pop(alias, None)
    connections.databases.pop(alias, None)