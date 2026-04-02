from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any, Iterator

from .exceptions import (
    TenantContextNotSetError,
    TenantDatabaseAliasNotSetError,
)


_active_tenant: ContextVar[Any | None] = ContextVar("active_tenant", default=None)
_active_tenant_db_alias: ContextVar[str | None] = ContextVar("active_tenant_db_alias", default=None)
_active_tenant_identifier: ContextVar[str | None] = ContextVar("active_tenant_identifier", default=None)


@dataclass(frozen=True)
class TenantContextTokens:
    tenant_token: Token
    db_alias_token: Token
    identifier_token: Token


def _resolve_tenant_identifier(tenant: Any) -> str | None:
    for attr in ("slug", "uuid", "code", "id"):
        value = getattr(tenant, attr, None)
        if value not in (None, ""):
            return str(value)
    if isinstance(tenant, dict):
        for key in ("slug", "uuid", "code", "id"):
            value = tenant.get(key)
            if value not in (None, ""):
                return str(value)
    return None


def set_current_tenant(
    tenant: Any,
    db_alias: str,
    *,
    tenant_identifier: str | None = None,
) -> TenantContextTokens:
    if tenant is None:
        raise TenantContextNotSetError("Cannot activate tenant context without a tenant object.")
    if not db_alias:
        raise TenantDatabaseAliasNotSetError("Cannot activate tenant context without a db alias.")

    resolved_identifier = tenant_identifier or _resolve_tenant_identifier(tenant)

    return TenantContextTokens(
        tenant_token=_active_tenant.set(tenant),
        db_alias_token=_active_tenant_db_alias.set(db_alias),
        identifier_token=_active_tenant_identifier.set(resolved_identifier),
    )


def reset_current_tenant(tokens: TenantContextTokens) -> None:
    _active_tenant.reset(tokens.tenant_token)
    _active_tenant_db_alias.reset(tokens.db_alias_token)
    _active_tenant_identifier.reset(tokens.identifier_token)


def clear_current_tenant() -> None:
    _active_tenant.set(None)
    _active_tenant_db_alias.set(None)
    _active_tenant_identifier.set(None)


def get_current_tenant(*, required: bool = False) -> Any | None:
    tenant = _active_tenant.get()
    if required and tenant is None:
        raise TenantContextNotSetError("No active tenant found in the current execution context.")
    return tenant


def get_current_tenant_db_alias(*, required: bool = False) -> str | None:
    db_alias = _active_tenant_db_alias.get()
    if required and not db_alias:
        raise TenantDatabaseAliasNotSetError(
            "No active tenant database alias found in the current execution context."
        )
    return db_alias


def get_current_tenant_identifier() -> str | None:
    return _active_tenant_identifier.get()


def has_active_tenant() -> bool:
    return get_current_tenant() is not None and bool(get_current_tenant_db_alias())


@contextmanager
def tenant_context(
    tenant: Any,
    db_alias: str,
    *,
    tenant_identifier: str | None = None,
) -> Iterator[None]:
    tokens = set_current_tenant(
        tenant=tenant,
        db_alias=db_alias,
        tenant_identifier=tenant_identifier,
    )
    try:
        yield
    finally:
        reset_current_tenant(tokens)