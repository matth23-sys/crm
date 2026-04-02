# backend/core/db/exceptions.py

class TenantContextMissingError(RuntimeError):
    """No existe tenant activo en el contexto actual."""


class TenantDatabaseConfigurationError(RuntimeError):
    """La configuración del tenant para la base de datos es inválida o incompleta."""


class TenantDatabaseRegistrationError(RuntimeError):
    """Ocurrió un error al registrar o remover dinámicamente una base de datos tenant."""