from __future__ import annotations


class MultiTenancyError(Exception):
    """Base error for multi-tenant database infrastructure."""


class TenantContextError(MultiTenancyError):
    """Base error for tenant context issues."""


class TenantContextNotSetError(TenantContextError):
    """Raised when tenant-scoped code runs without an active tenant."""


class TenantDatabaseAliasNotSetError(TenantContextError):
    """Raised when the active tenant db alias is missing."""


class TenantConfigurationError(MultiTenancyError):
    """Base error for invalid tenant database configuration."""


class TenantConnectionConfigurationError(TenantConfigurationError):
    """Raised when a tenant lacks enough DB configuration to build a connection."""


class TenantConnectionRegistrationError(MultiTenancyError):
    """Raised when a tenant DB connection cannot be registered or removed."""


class TenantConnectionNotRegisteredError(MultiTenancyError):
    """Raised when code tries to use a tenant DB alias that is not registered."""


class TenantRoutingError(MultiTenancyError):
    """Raised when the router cannot safely decide the target database."""