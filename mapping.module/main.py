from src.factory import app_factory
from src.common.logging import setup_logging


setup_logging()

app = app_factory()
