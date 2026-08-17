import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Analysis",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid7,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_timestamp",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created at"
                    ),
                ),
                (
                    "updated_timestamp",
                    models.DateTimeField(
                        auto_now=True, verbose_name="updated at"
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "pending"),
                            (1, "processing"),
                            (2, "done"),
                            (3, "failed"),
                        ],
                        default=0,
                        verbose_name="status",
                    ),
                ),
                (
                    "candidate_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="candidate name",
                    ),
                ),
                (
                    "source_dossier",
                    models.JSONField(verbose_name="source dossier"),
                ),
                (
                    "analysis_result",
                    models.JSONField(
                        blank=True, null=True, verbose_name="analysis result"
                    ),
                ),
                (
                    "dashboard",
                    models.JSONField(
                        blank=True, null=True, verbose_name="dashboard"
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="model"
                    ),
                ),
                (
                    "error_message",
                    models.TextField(blank=True, verbose_name="error message"),
                ),
            ],
            options={
                "verbose_name": "analysis",
                "verbose_name_plural": "analyses",
                "ordering": ("-created_timestamp",),
            },
        ),
    ]
