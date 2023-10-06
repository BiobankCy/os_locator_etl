from django.db import models


class EtlConfiguration(models.Model):
    name = models.CharField(max_length=200)
    open_specimen_host = models.CharField(max_length=1000)
    open_specimen_user = models.CharField(max_length=1000)
    open_specimen_pass = models.CharField(max_length=1000)
    open_specimen_query_id = models.CharField(max_length=1000)
    bridgehead_host = models.CharField(max_length=1000)
    bridgehead_user = models.CharField(max_length=1000)
    bridgehead_pass = models.CharField(max_length=1000)
    celery_frequency_hours = models.PositiveSmallIntegerField(default=0)
    celery_task_id = models.CharField(max_length=1000, blank=True, null=True)
    mapping_config = models.TextField(max_length=10000, default="{}")

    def __str__(self):
        return self.name
