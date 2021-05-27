from django.db import models
from datetime import datetime


class DateTimeRecordModel(models.Model):
    date_added = models.DateTimeField(null=False, default=datetime.utcnow)

    class Meta:
        abstract = True


class TagContainedModel(models.Model):
    tag = models.CharField(max_length=20, null=True)

    class Meta:
        abstract = True


class FileSystemRelatedModel(models.Model):
    path = models.TextField(null=False)

    class Meta:
        abstract = True
