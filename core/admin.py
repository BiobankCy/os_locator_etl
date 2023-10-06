import datetime
import json

from django.contrib import admin
from django.core.checks import messages

from core.models import EtlConfiguration
from core.tasks import run_configuration_task
from os_locator_etl.celery import app

admin.site.site_header = "OpenSpecimen Locator ETL"
admin.site.site_title = "OpenSpecimen Locator ETL"
admin.site.index_title = "OpenSpecimen Locator ETL"


@admin.register(EtlConfiguration)
class RunConfigurationAdmin(admin.ModelAdmin):
    selected_configuration: EtlConfiguration = None

    actions = (
        "run",
        "schedule",
        "unschedule",
    )

    @admin.action(description="Run configuration(s)")
    def run(self, request, queryset):
        for run_configuration in queryset.all():
            config = EtlConfiguration.objects.get(id=run_configuration.id)
            mapping_config = json.loads(config.mapping_config)
            run_configuration_task.apply_async(args=(run_configuration.id, False))

        self.message_user(request, f"Run configuration(s): {len(queryset)}")

    @admin.action(description="Schedule configuration(s)")
    def schedule(self, request, queryset):
        for run_configuration in queryset.all():
            if run_configuration.celery_task_id:
                app.control.revoke(run_configuration.celery_task_id)

            if run_configuration.celery_frequency_hours:
                eta = datetime.datetime.utcnow() + datetime.timedelta(
                    hours=run_configuration.celery_frequency_hours
                )
            else:
                self.message_user(
                    request,
                    f"Skipping, no frequency found: {run_configuration.name}",
                    level=messages.ERROR,
                )
                continue

            celery_task_id = run_configuration_task.apply_async(
                args=(run_configuration.id, True), eta=eta
            )
            run_configuration.celery_task_id = celery_task_id
            run_configuration.save()

        self.message_user(request, f"Scheduled configuration(s): {len(queryset)}")

    @admin.action(description="Unscheduled configuration(s)")
    def unschedule(self, request, queryset):
        for run_configuration in queryset.all():
            if run_configuration.celery_task_id:
                app.control.revoke(run_configuration.celery_task_id)
                run_configuration.celery_task_id = None
                run_configuration.save()

        self.message_user(request, f"Revoke configuration(s): {len(queryset)}")
