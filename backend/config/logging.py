# backend/config/logging.py

import logging
import os


class ProjectContextFilter(logging.Filter):
    """
    Agrega contexto mínimo a cada log.
    Más adelante podrá enriquecerse desde middleware con request_id y tenant.
    """

    def filter(self, record):
        record.environment = os.getenv("APP_ENV", "local")
        record.request_id = getattr(record, "request_id", "-")
        record.tenant = getattr(record, "tenant", "-")
        return True


LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "project_context": {
            "()": "config.logging.ProjectContextFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s | %(levelname)s | %(name)s | "
                "env=%(environment)s | req=%(request_id)s | tenant=%(tenant)s | "
                "%(message)s"
            )
        },
        "simple": {
            "format": "%(levelname)s | %(name)s | %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["project_context"],
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}