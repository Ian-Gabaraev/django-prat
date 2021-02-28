from django.db.models import Model
from .models import GitPratIDModel, GitPratModelDependency


class RevertTool:

    @staticmethod
    def is_revertible(model_object: Model) -> bool:
        return GitPratIDModel in model_object.__class__.__mro__

    @staticmethod
    def has_parents(model_object: Model) -> bool:

        return any(
            [
                isinstance(getattr(model_object, field_name), Model)
                for field_name in RevertTool.collect_field_names(model_object)
            ]
        )

    @staticmethod
    def has_children(model_object: Model) -> bool:
        pass

    @staticmethod
    def get_parent_fields(model_object: Model):

        return [
            getattr(model_object, field_name)
            for field_name in RevertTool.collect_field_names(model_object)
            if isinstance(getattr(model_object, field_name), Model)
        ]

    @staticmethod
    def collect_field_names(model_object: Model) -> list:

        return [
            field.__dict__.get('name')
            for field in model_object._meta.fields  # noqa
        ]

    @staticmethod
    def collect_simple_fields(model_object: Model):

        field_names = RevertTool.collect_field_names(model_object)

        return {
            field_name: getattr(model_object, field_name)
            for field_name in field_names
            if not isinstance(getattr(model_object, field_name), Model)
        }

    @staticmethod
    def collect_parent_fields(model_object: Model):

        field_names = RevertTool.collect_field_names(model_object)

        return {
            field_name: getattr(model_object, field_name)
            for field_name in field_names
            if isinstance(getattr(model_object, field_name), Model)
        }

    @staticmethod
    def backtrack_for_data(model_object: Model):

        pass

    @staticmethod
    def make_snapshot(model_object: Model):
        if not RevertTool.is_revertible(model_object):
            raise ValueError(""
                             "A model must inherit from GitPratIDModel"
                             "in order to be revertible "
                             "")

        basic_snapshot = RevertTool.collect_simple_fields(model_object)

        if not RevertTool.has_parents(model_object):
            return basic_snapshot
        else:
            pass
