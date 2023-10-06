# Create your tasks here
import datetime

from celery import shared_task

from core.models import EtlConfiguration
from core.etl_runner import EtlRunner


@shared_task(bind=True)
def run_configuration_task(self, config_id, should_schedule_next_run=False):
    self.update_state(state="STARTED")
    config = EtlConfiguration.objects.get(id=config_id)

    # Schedule the next run if needed
    if should_schedule_next_run and config.celery_frequency_hours:
        eta = datetime.datetime.utcnow() + datetime.timedelta(
            hours=config.celery_frequency_hours
        )
        celery_task_id = run_configuration_task.apply_async(
            args=(config.id, True), eta=eta
        )
        config.celery_task_id = celery_task_id
        config.save()

    return EtlRunner(config=config).run()
