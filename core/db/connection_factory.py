# backend/core/db/connection_factory.py

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from django.conf import settings

from .exceptions import TenantDatabaseConfigurationError


def _read_tenant_value(tenant: Any, key: str, default=None):
    if isinstance(tenant, dict):
        return tenant.get(key, default)
    return getattr(tenant, key, default)


def _sanitize_alias_part(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    cleaned = cleaned.strip("_")

    if not cleaned:
        raise TenantDatabaseConfigurationError(
            "No se pudo construir un alias válido para la base de datos del tenant."
        )

    return cleaned


def build_tenant_db_alias(tenant: Any) -> str:
    prefix = getattr(settings, "MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX", "tenant_")

    raw_identifier = (
        _read_tenant_value(tenant, "db_alias")
        or _read_tenant_value(tenant, "slug")
        or _read_tenant_value(tenant, "subdomain")
        or _read_tenant_value(tenant, "schema_name")
        or _read_tenant_value(tenant, "id")
    )

    if raw_identifier in (None, ""):
        raise TenantDatabaseConfigurationError(
            "El tenant no tiene un identificador utilizable para construir db alias."
        )

    return f"{prefix}{_sanitize_alias_part(str(raw_identifier))}"


def build_tenant_database_config(tenant: Any) -> dict:
    default_engine = "django.db.backends.postgresql"
    default_host = "127.0.0.1"
    default_port = "5432"

    engine = _read_tenant_value(tenant, "db_engine", default_engine)
    name = _read_tenant_value(tenant, "db_name")
    user = _read_tenant_value(tenant, "db_user")
    password = _read_tenant_value(tenant, "db_password")
    host = _read_tenant_value(tenant, "db_host", default_host)
    port = str(_read_tenant_value(tenant, "db_port", default_port))
    options = deepcopy(_read_tenant_value(tenant, "db_options", {}) or {})
    conn_max_age = int(_read_tenant_value(tenant, "db_conn_max_age", 60))

    missing = []
    if not name:
        missing.append("db_name")
    if not user:
        missing.append("db_user")
    if password is None:
        missing.append("db_password")

    if missing:
        raise TenantDatabaseConfigurationError(
            f"Faltan campos requeridos de conexión tenant: {', '.join(missing)}."
        )

    return {
        "ENGINE": engine,
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": conn_max_age,
        "OPTIONS": options,
    }