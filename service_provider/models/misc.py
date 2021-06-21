from django.db import models
from django.contrib.auth.models import User

from .abstraction import *


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    display_name = models.CharField(max_length=200, null=False)
    gender = models.BooleanField(null=True)
    status = models.TextField(null=True, default="")

    class Meta:
        abstract = False
        db_table = "faceval_user"
        # ordering = ["date_added"]


class MLModel(DateTimeRecordModel, TagContainedModel, FileSystemRelatedModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    default = models.BooleanField(null=False, default=False)

    class Meta:
        abstract = False
        db_table = "model"


class PhotoBlog(DateTimeRecordModel, TagContainedModel, FileSystemRelatedModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    image = models.TextField(null=False)
    trained = models.BooleanField(null=False, default=False)
    score = models.FloatField(null=True)
    face_positions = models.TextField()
    title = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)

    class Meta:
        abstract = False
        db_table = "photo"
        ordering = ['-date_added']
