from django.test import TransactionTestCase
from .utils import RevertTool
from .models import SimpleTrackedModel, SimpleUntrackedModel, \
    Snapshot, SimpleParentModel, ComplexTrackedModel, SimpleChildModel

import json


class GitPratTest(TransactionTestCase):

    @staticmethod
    def get_simple_untracked_model_object() -> SimpleUntrackedModel:
        """
        Создание throwaway объекта SimpleUntrackedModel

        """
        dummy_object = SimpleUntrackedModel.objects.create(  # noqa
            title="Random title",
            price=100)

        return dummy_object

    @staticmethod
    def get_simple_tracked_model_object() -> SimpleTrackedModel:
        """
        Создание throwaway объекта SimpleTrackedModel

        """
        dummy_object = SimpleTrackedModel.objects.create(  # noqa
            title="Random title",
            price=100)

        return dummy_object

    @staticmethod
    def get_complex_tracked_model_object() -> ComplexTrackedModel:
        """
        Создание throwaway объекта ComplexTrackedModel

        """
        parent = SimpleParentModel.objects.create(field="Lorem ipsum")  # noqa
        complex_object = ComplexTrackedModel.objects.create(  # noqa
            title="Random title",
            price=100,
            dummy=parent)

        return complex_object

    @staticmethod
    def get_complex_tracked_model_object_with_child() -> ComplexTrackedModel:
        """
        Создание throwaway объекта ComplexTrackedModel

        """
        parent = SimpleParentModel.objects.create(field="Lorem ipsum")  # noqa
        complex_object = ComplexTrackedModel.objects.create(  # noqa
            title="Random title",
            price=100,
            dummy=parent)

        SimpleChildModel.objects.create(
            title="Child models title",
            complex_tracked_model=complex_object)

        return complex_object

    def test_fails_on_snapshotting_untracked_model_object(self):
        """
        Ожидается, что попытка сохранить объект модели,
        которая не наследует TrackedModelBase, вызовет ошибку

        """
        dummy_object = self.get_simple_untracked_model_object()

        with self.assertRaises(ValueError):
            RevertTool.make_snapshot(dummy_object)

    def test_detects_tracked_models_correctly(self):
        """
        Ожидается, что метод is_revertible вернет True, если
        переданный аргумент является объектом наследника TrackedModelBase

        """

        self.assertTrue(
            RevertTool.is_revertible(self.get_simple_tracked_model_object())
        )

    def test_detects_non_revertible_models_correctly(self):
        """
        Ожидается, что метод is_revertible вернет False, если
        переданный аргумент не является объектом наследника TrackedModelBase

        """

        self.assertFalse(
            RevertTool.is_revertible(self.get_simple_untracked_model_object())
        )

    def test_collects_fields_properly_simple_model(self):
        """
        Ожидается, что метод collect_fields вернет полный
        набор полей объекта SimpleModel, переданного в кач-ве аргумента

        """

        self.assertEqual(
            ["id", "git_prat_id", "title", "price"],
            RevertTool.collect_field_names(self.get_simple_tracked_model_object())
        )

    def test_makes_accurate_snapshot_for_simple_tracked_model_object(self):
        """
        Ожидается, что возвращаемое значение метода
        make_snapshot имеет определенную структуру

        """
        dummy_object = self.get_simple_tracked_model_object()
        dummy_object_snapshot = RevertTool.make_snapshot(dummy_object)

        self.assertEqual(
            {
                "id": dummy_object.id,  # noqa
                "git_prat_id": str(dummy_object.git_prat_id),
                "title": dummy_object.title,
                "price": dummy_object.price
            },
            dummy_object_snapshot
        )

    def test_stores_simple_tracked_model_object_snapshot_successfully(self):
        """
        Ожидается, что возвращаемый методом make_snapshot
        dictionary сохраняется в объект Snapshot
        без ошибок

        """
        dummy_object = self.get_simple_tracked_model_object()
        dummy_object_snapshot = RevertTool.make_snapshot(dummy_object)

        Snapshot.objects.create(snapshot=dummy_object_snapshot)  # noqa

    def test_collects_complex_tracked_model_object_fields_accurately(self):
        """
        Ожидается, что метод collect_fields вернет полный
        набор полей объекта ComplexTrackedModel, переданного в кач-ве аргумента

        """

        self.assertEqual(
            ["id", "git_prat_id", "title", "price", "dummy"],
            RevertTool.collect_field_names(self.get_complex_tracked_model_object())
        )

    def test_snapshots_complex_model_object_accurately(self):
        """
        Ожидается, что возвращаемое значение метода
        make_snapshot имеет определенную структуру

        """
        dummy_complex_object = self.get_complex_tracked_model_object()

        self.assertEqual(
            {
                "id": dummy_complex_object.id,  # noqa
                "git_prat_id": str(dummy_complex_object.git_prat_id),  # noqa
                "title": dummy_complex_object.title,
                "price": dummy_complex_object.price,
                'dummy': {
                    'id': dummy_complex_object.dummy.id,  # noqa
                    'field': dummy_complex_object.dummy.field,  # noqa
                }
            },
            RevertTool.make_snapshot(dummy_complex_object)
        )

    def test_has_parents_method_returns_true_for_complex_object(self):
        """
        Ожидается, что has_parents вернет True, если объект
        переданной в аргументах модели связан
        с прочей родительской моделью

        """

        self.assertTrue(RevertTool.has_parents(self.get_complex_tracked_model_object()))

    def test_has_parents_returns_false_for_simple_object(self):
        """
        Ожидается, что has_parents вернет False, если объект
        переданной в аргументах модели не связан
        с прочей родительской моделью

        """

        self.assertFalse(RevertTool.has_parents(self.get_simple_tracked_model_object()))

    def test_complex_tracked_model_object_snapshot_converts_into_valid_json(self):
        """
        Ожидается, что снэпшот сложной модели конверитируется
        в JSON-formatted string

        """
        json.dumps(
            RevertTool.make_snapshot(self.get_complex_tracked_model_object()),
            indent=4)

    def test_has_children_method_returns_false_for_complex_object_without_child(self):
        """
        Ожидается, что has_children вернет True, если объект
        переданной в аргументах модели не связан
        с прочей детской моделью

        """

        self.assertFalse(RevertTool.has_children(self.get_complex_tracked_model_object()))

    def test_has_children_method_returns_true_for_complex_object_with_child(self):
        """
        Ожидается, что has_children вернет True, если объект
        переданной в аргументах модели связан
        с прочей детской моделью

        """

        self.assertTrue(RevertTool.has_children(self.get_complex_tracked_model_object_with_child()))

    def test_revert_simple_model_one_step_successful(self):
        pass

    def test_revert_simple_model_arbitrary_step_successful(self):
        pass

    def test_revert_complex_model_one_step_successful(self):
        pass

    def test_revert_complex_model_arbitrary_step_successful(self):
        pass
