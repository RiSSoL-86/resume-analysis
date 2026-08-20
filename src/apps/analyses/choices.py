from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class AnalysisStatus(models.IntegerChoices):
    """Enumerate lifecycle states of a resume analysis."""

    PENDING = 0, _("pending")
    PROCESSING = 1, _("processing")
    DONE = 2, _("done")
    FAILED = 3, _("failed")
