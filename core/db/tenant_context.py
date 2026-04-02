# backend/core/db/tenant_context.py

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Iterator, Optional

from .exceptions import TenantContextMissingError


_current_tenant: ContextVar[Optional[Any]] = ContextVar("current_tenant", default=None)
_current_tenant_alias: ContextVar[Optional[str]] = ContextVar(
    "current_tenant_alias",
    default=None,
)


@dataclass(frozen=True)
class TenantContextSnapshot:
    tenant: Any | None
    db_alias: str | None


def set_current_tenant(*, tenant: Any, db_alias: str) -> TenantContextSnapshot:
    if not db_alias:
        raise ValueError("db_alias es obligatorio.")

    _current_tenant.set(tenant)
    _current_tenant_alias.set(db_alias)

    return TenantContextSnapshot(tenant=tenant, db_alias=db_alias)


def get_current_tenant() -> Any | None:
    return _current_tenant.get()


def get_current_tenant_alias(*, required: bool = False) -> str | None:
    alias = _current_tenant_alias.get()

    if required and not alias:
        raise TenantContextMissingError(
            "No existe tenant activo en el contexto actual."
        )

    return alias


def has_current_tenant() -> bool:
    return bool(_current_tenant.get() and _current_tenant_alias.get())


def clear_current_tenant() -> None:
    _current_tenant.set(None)
    _current_tenant_alias.set(None)


@contextmanager
def tenant_context(*, tenant: Any, db_alias: str) -> Iterator[TenantContextSnapshot]:
    if not db_alias:
        raise ValueError("db_alias es obligatorio para crear tenant_context.")

    tenant_token = _current_tenant.set(tenant)
    alias_token = _current_tenant_alias.set(db_alias)

    try:
        yield TenantContextSnapshot(tenant=tenant, db_alias=db_alias)
    finally:
        _current_tenant.reset(tenant_token)
        _current_tenant_alias.reset(alias_token)