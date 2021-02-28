from django.db import models
from django.utils import timezone
from uuid import uuid4


def make_uuid_as_str():
    return str(uuid4())


class GitPratModelDependency:
    ...


class GitPratIDModel(models.Model):
    git_prat_id = models.CharField(max_length=128, default=make_uuid_as_str)

    class Meta:
        abstract = True


class SimpleModel(GitPratIDModel):
    title = models.CharField(default="", max_length=256)
    price = models.PositiveIntegerField(default=0)


class DummyParentModel(models.Model, GitPratModelDependency):
    field = models.CharField(default="", max_length=64)


class ComplexModel(GitPratIDModel):
    title = models.CharField(default="", max_length=256)
    price = models.PositiveIntegerField(default=0)
    dummy = models.ForeignKey(to=DummyParentModel, null=True, on_delete=models.SET_NULL)


class DummyChildModel(models.Model):
    complex_model = models.ForeignKey(to=ComplexModel, null=True, on_delete=models.SET_NULL)


class SimpleModelDoesNotInheritGitPratIDModel(models.Model):
    title = models.CharField(default="", max_length=256)
    price = models.PositiveIntegerField(default=0)


class Snapshot(models.Model):
    snapshot = models.JSONField(default=dict)
    when_saved = models.DateTimeField(default=timezone.now)


class GitPrat(models.Model):
    git_prat_id = models.CharField(default="", max_length=128)
    snapshots = models.ManyToManyField(to=Snapshot, blank=True)

