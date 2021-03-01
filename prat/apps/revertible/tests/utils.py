from django.db.models import Model
from .models import TrackedModelBase


class RevertTool:

    @staticmethod
    def is_revertible(model_object: Model) -> bool:

        return TrackedModelBase in model_object.__class__.__mro__

    @staticmethod
    def has_parents(model_object: Model) -> bool:

        return any(
            [
                isinstance(getattr(model_object, field_name), Model)
                for field_name in RevertTool.collect_field_names(model_object)
            ]
        )

    @staticmethod
    def count_children(model_object: Model) -> list:

        return [
            getattr(model_object, f"{child_model_name.lower()}_set").count()
            for child_model_name in model_object.TrackingData.children  # noqa
        ]

    @staticmethod
    def has_children_metadata(model_object: Model) -> bool:

        return hasattr(model_object, "TrackingData") and hasattr(model_object.TrackingData, "children")

    @staticmethod
    def has_children(model_object: Model) -> bool:

        return RevertTool.has_children_metadata(model_object) and any(RevertTool.count_children(model_object))

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
    def collect_children(model_object: Model):

        result = []

        for child_table_name in getattr(model_object.TrackingData, "children"):

            for child_table_object in getattr(model_object, f"{child_table_name.lower()}_set").all():
                result.append(RevertTool.backtrack_for_data(child_table_object))

        print(result)

    @staticmethod
    def backtrack_for_data(model_object: Model, result=dict()):  # noqa

        field_names = RevertTool.collect_field_names(model_object)

        model_obj_as_dictionary = {
            field_name: getattr(model_object, field_name)
            for field_name in field_names
        }

        for key, value in model_obj_as_dictionary.items():
            if isinstance(value, Model):
                result[key] = {}
                RevertTool.backtrack_for_data(value, result[key])
            else:
                result[key] = value

        return result

    @staticmethod
    def make_snapshot(model_object: Model):
        if not RevertTool.is_revertible(model_object):
            raise ValueError(""
                             "A model must inherit from GitPratIDModel"
                             "in order to be revertible"
                             "")

        if not RevertTool.has_parents(model_object):
            return RevertTool.collect_simple_fields(model_object)
        else:
            return RevertTool.backtrack_for_data(model_object)
