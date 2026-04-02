from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterator, TypeVar

from django.db import close_old_connections, connections, transaction

from .connection_factory import build_tenant_db_alias
from .exceptions import TenantConnectionNotRegisteredError
from .registry import is_connection_registered, register_tenant_connection
from .tenant_context import get_current_tenant_db_alias, tenant_context

T = TypeVar("T")


def get_current_tenant_alias_or_raise() -> str:
    return get_current_tenant_db_alias(required=True)


def get_connection(alias: str | None = None):
    using = alias or get_current_tenant_alias_or_raise()
    if using not in connections.databases:
        raise TenantConnectionNotRegisteredError(
            f"Connection alias '{using}' is not registered."
        )
    return connections[using]


def is_tenant_db_alias(alias: str) -> bool:
    return alias.startswith("tenant_")


@contextmanager
def using_tenant(
    tenant: Any,
    *,
    register_connection: bool = True,
) -> Iterator[str]:
    alias = register_tenant_connection(tenant) if register_connection else build_tenant_db_alias(tenant)

    close_old_connections()
    with tenant_context(tenant=tenant, db_alias=alias):
        yield alias


@contextmanager
def tenant_atomic(
    using: str | None = None,
    *,
    savepoint: bool = True,
    durable: bool = False,
) -> Iterator[None]:
    alias = using or get_current_tenant_alias_or_raise()
    with transaction.atomic(using=alias, savepoint=savepoint, durable=durable):
        yield


def tenant_using(queryset_or_manager, using: str | None = None):
    alias = using or get_current_tenant_alias_or_raise()
    return queryset_or_manager.using(alias)


def run_in_tenant_context(
    tenant: Any,
    callback: Callable[..., T],
    *args,
    **kwargs,
) -> T:
    with using_tenant(tenant) as _alias:
        return callback(*args, **kwargs)