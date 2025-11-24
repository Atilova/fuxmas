import logging
import logging.config

from src.common.config import service_config


_LOG_LEVEL = service_config.log_level.upper()
_ACCESS_LOG_LEVEL = (
    logging.INFO if service_config.enabled_access_logs else logging.WARNING
)


def setup_logging():
     logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "formatter": "default",
                "class": "logging.StreamHandler",
            },
            "access": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "level": _ACCESS_LOG_LEVEL,
            },
        },
        "loggers": {
            "uvicorn.error": {
                "handlers": ["console"],
                "level": _LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": _LOG_LEVEL,
        }
    })
