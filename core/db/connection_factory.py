from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Mapping

from django.conf import settings

from .exceptions import TenantConnectionConfigurationError


_ALIAS_SANITIZER_RE = re.compile(r"[^a-zA-Z0-9_]+")

TENANT_IDENTIFIER_ATTRS = ("db_alias", "slug", "uuid", "code", "id")
TENANT_DB_NAME_ATTRS = ("db_name", "database_name", "dbname")
TENANT_DB_USER_ATTRS = ("db_user", "database_user")
TENANT_DB_PASSWORD_ATTRS = ("db_password", "database_password")
TENANT_DB_HOST_ATTRS = ("db_host", "database_host")
TENANT_DB_PORT_ATTRS = ("db_port", "database_port")
TENANT_DB_OPTIONS_ATTRS = ("db_options", "database_options")
TENANT_DB_TEST_NAME_ATTRS = ("db_test_name", "database_test_name")


def _get_value(source: Any, keys: tuple[str, ...], default: Any = None) -> Any:
    if isinstance(source, Mapping):
        for key in keys:
            value = source.get(key)
            if value not in (None, ""):
                return value
        return default

    for key in keys:
        value = getattr(source, key, None)
        if value not in (None, ""):
            return value
    return default


def sanitize_alias(raw_alias: str) -> str:
    alias = _ALIAS_SANITIZER_RE.sub("_", str(raw_alias).strip().lower()).strip("_")
    if not alias:
        raise TenantConnectionConfigurationError("The generated tenant db alias is empty.")
    return alias


def build_tenant_db_alias(tenant: Any) -> str:
    prefix = settings.MULTI_TENANCY_TENANT_DB_ALIAS_PREFIX
    raw_identifier = _get_value(tenant, TENANT_IDENTIFIER_ATTRS)

    if raw_identifier in (None, ""):
        raise TenantConnectionConfigurationError(
            "Unable to build tenant db alias. Expected one of: "
            f"{', '.join(TENANT_IDENTIFIER_ATTRS)}"
        )

    raw_identifier = str(raw_identifier)
    if raw_identifier.startswith(prefix):
        return sanitize_alias(raw_identifier)

    return sanitize_alias(f"{prefix}{raw_identifier}")


def build_tenant_db_config(tenant: Any) -> dict[str, Any]:
    template = deepcopy(getattr(settings, "MULTI_TENANCY_TENANT_DB_TEMPLATE", {}))
    if not template:
        raise TenantConnectionConfigurationError(
            "MULTI_TENANCY_TENANT_DB_TEMPLATE is not configured in settings."
        )

    db_name = _get_value(tenant, TENANT_DB_NAME_ATTRS, default=template.get("NAME"))
    if not db_name:
        raise TenantConnectionConfigurationError(
            "Unable to build tenant DB config. Missing tenant database name."
        )

    config = deepcopy(template)
    config["NAME"] = db_name

    overrides = {
        "USER": _get_value(tenant, TENANT_DB_USER_ATTRS),
        "PASSWORD": _get_value(tenant, TENANT_DB_PASSWORD_ATTRS),
        "HOST": _get_value(tenant, TENANT_DB_HOST_ATTRS),
        "PORT": _get_value(tenant, TENANT_DB_PORT_ATTRS),
    }

    for key, value in overrides.items():
        if value not in (None, ""):
            config[key] = value

    db_options = _get_value(tenant, TENANT_DB_OPTIONS_ATTRS)
    if isinstance(db_options, Mapping):
        config["OPTIONS"] = {
            **config.get("OPTIONS", {}),
            **dict(db_options),
        }

    db_test_name = _get_value(tenant, TENANT_DB_TEST_NAME_ATTRS)
    if db_test_name:
        config.setdefault("TEST", {})
        config["TEST"]["NAME"] = db_test_name

    config.setdefault("CONN_MAX_AGE", 0)
    config.setdefault("CONN_HEALTH_CHECKS", False)

    return config