from django.db import models
from django.utils import timezone
from uuid import uuid4


def get_uuid_as_str() -> str:
    return str(uuid4())


class TrackedModelBase(models.Model):
    git_prat_id = models.CharField(max_length=128,
                                   default=get_uuid_as_str)

    class Meta:
        abstract = True


class SimpleTrackedModel(TrackedModelBase):
    title = models.CharField(default="",
                             max_length=256)
    price = models.PositiveIntegerField(default=0)


class DummyParentModel(models.Model):
    field = models.CharField(default="",
                             max_length=64)


class ComplexTrackedModel(TrackedModelBase):
    title = models.CharField(default="",
                             max_length=256)
    price = models.PositiveIntegerField(default=0)
    dummy = models.ForeignKey(to=DummyParentModel,
                              null=True,
                              on_delete=models.SET_NULL)


class SimpleChildModel(models.Model):
    complex_tracked_model = models.ForeignKey(
        to=ComplexTrackedModel,
        null=True,
        on_delete=models.SET_NULL)


class SimpleUntrackedModel(models.Model):
    title = models.CharField(default="",
                             max_length=256)
    price = models.PositiveIntegerField(default=0)


class Snapshot(models.Model):
    snapshot = models.JSONField(default=dict)
    when_saved = models.DateTimeField(default=timezone.now)


class GitPrat(models.Model):
    git_prat_id = models.CharField(default="",
                                   max_length=128)
    snapshots = models.ManyToManyField(to=Snapshot,
                                       blank=True)
