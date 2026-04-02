# backend/core/db/utils.py

from __future__ import annotations

from contextlib import contextmanager

from django.db import transaction

from .tenant_context import get_current_tenant_alias


def get_tenant_db_alias(*, required: bool = True) -> str | None:
    return get_current_tenant_alias(required=required)


def using_current_tenant(queryset):
    alias = get_tenant_db_alias(required=True)
    return queryset.using(alias)


@contextmanager
def tenant_atomic(*, using: str | None = None):
    alias = using or get_tenant_db_alias(required=True)
    with transaction.atomic(using=alias):
        yield