from typing import final, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.analyses.choices import AnalysisStatus
from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel


@final
class Analysis(UUIDAbstractModel, TimestampedAbstractModel):
    """Store a resume analysis produced from a candidate dossier."""

    status = models.PositiveSmallIntegerField(
        _("status"),
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.PENDING,
    )
    candidate_name = models.CharField(
        _("candidate name"), max_length=255, blank=True
    )
    source_dossier = models.JSONField(_("source dossier"))
    analysis_result = models.JSONField(
        _("analysis result"), null=True, blank=True
    )
    dashboard = models.JSONField(_("dashboard"), null=True, blank=True)
    model_name = models.CharField(_("model"), max_length=100, blank=True)
    error_message = models.TextField(_("error message"), blank=True)

    class Meta:
        """Configure ordering and human-readable names."""

        verbose_name = _("analysis")
        verbose_name_plural = _("analyses")
        ordering = ("-created_timestamp",)

    @override
    def __str__(self) -> str:
        """Return a readable label for admin and logs."""
        return (
            f"{self.candidate_name or self.pk} — {self.get_status_display()}"
        )
