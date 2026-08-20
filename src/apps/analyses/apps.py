from typing import final

from django.apps import AppConfig


@final
class AnalysesConfig(AppConfig):
    """Configure the analyses application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analyses"
