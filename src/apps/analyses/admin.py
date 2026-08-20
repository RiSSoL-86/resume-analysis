from typing import final

from django.contrib import admin

from apps.analyses.models import Analysis


@final
class AnalysisAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure resume analysis administration."""

    list_display = (
        "id",
        "candidate_name",
        "status",
        "model_name",
        "created_timestamp",
    )
    list_display_links = ("id", "candidate_name")
    list_filter = ("status",)
    search_fields = ("candidate_name", "id")
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    ordering = ("-created_timestamp",)


admin.site.register(Analysis, AnalysisAdmin)
