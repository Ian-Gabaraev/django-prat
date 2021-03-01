from django.test import TransactionTestCase
from .utils import RevertTool
from .models import SimpleTrackedModel, SimpleUntrackedModel, \
    Snapshot, DummyParentModel, ComplexTrackedModel

import json


class GitPratTest(TransactionTestCase):

    @staticmethod
    def get_simple_dummy_object_unrelated() -> SimpleUntrackedModel:
        """
        Создание throwaway объекта SimpleModelDoesNotInheritGitPratIDModel

        """
        dummy_object = SimpleUntrackedModel.objects.create(  # noqa
            title="Random title", price=100)

        return dummy_object

    @staticmethod
    def get_simple_dummy_object_related() -> SimpleTrackedModel:
        """
        Создание throwaway объекта SimpleModel

        """
        dummy_object = SimpleTrackedModel.objects.create(  # noqa
            title="Random title", price=100)

        return dummy_object

    @staticmethod
    def get_complex_dummy_object_related() -> ComplexTrackedModel:
        """
        Создание throwaway объекта ComplexModel

        """
        dummy_relation = DummyParentModel.objects.create(field="Lorem ipsum")  # noqa
        dummy_complex_object = ComplexTrackedModel.objects.create(  # noqa
            title="Random title", price=100, dummy=dummy_relation)

        return dummy_complex_object

    @staticmethod
    def get_complex_dummy_object_un_related() -> SimpleTrackedModel:
        """
        Создание throwaway объекта ComplexModel

        """
        dummy_object = SimpleTrackedModel.objects.create(  # noqa
            title="Random title", price=100)

        return dummy_object

    def test_fails_on_snapshotting_non_revert_id_subclass(self):
        """
        Ожидается, что попытка сохранить объект модели,
        которая не наследует GitPratIDModel, вызовет ошибку

        """
        dummy_object = self.get_simple_dummy_object_unrelated()

        with self.assertRaises(ValueError):
            RevertTool.make_snapshot(dummy_object)

    def test_is_revertible_detect_revertible_models_correctly(self):
        """
        Ожидается, что метод is_revertible вернет True, если
        переданный аргумент является объектом наследника GitPratIDModel

        """

        self.assertTrue(
            RevertTool.is_revertible(self.get_simple_dummy_object_related())
        )

    def test_is_revertible_detect_non_revertible_models_correctly(self):
        """
        Ожидается, что метод is_revertible вернет False, если
        переданный аргумент не является объектом наследника GitPratIDModel

        """

        self.assertFalse(
            RevertTool.is_revertible(self.get_simple_dummy_object_unrelated())
        )

    def test_collects_fields_properly_simple_model(self):
        """
        Ожидается, что метод collect_fields вернет полный
        набор полей объекта SimpleModel, переданного в кач-ве аргумента

        """

        self.assertEqual(
            ["id", "git_prat_id", "title", "price"],
            RevertTool.collect_field_names(self.get_simple_dummy_object_related())
        )

    def test_make_snapshot_simple_model_accurate(self):
        """
        Ожидается, что возвращаемое значение метода
        make_snapshot имеет определенную структуру

        """
        dummy_object = self.get_simple_dummy_object_related()
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

    def test_make_snapshot_simple_store_successful(self):
        """
        Ожидается, что возвращаемый методом make_snapshot
        dictionary сохраняется в объект Snapshot
        без ошибок

        """
        dummy_object = self.get_simple_dummy_object_related()
        dummy_object_snapshot = RevertTool.make_snapshot(dummy_object)

        Snapshot.objects.create(snapshot=dummy_object_snapshot)  # noqa

    def test_collects_fields_properly_complex_model(self):
        """
        Ожидается, что метод collect_fields вернет полный
        набор полей объекта ComplexModel, переданного в кач-ве аргумента

        """

        self.assertEqual(
            ["id", "git_prat_id", "title", "price", "dummy"],
            RevertTool.collect_field_names(self.get_complex_dummy_object_related())
        )

    def test_make_snapshot_complex_model_accurate(self):
        """
        Ожидается, что возвращаемое значение метода
        make_snapshot имеет определенную структуру

        """
        dummy_complex_object = self.get_complex_dummy_object_related()

        print(dummy_complex_object.dummychildmodel_set.all())

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

    def test_has_parents_returns_true_for_complex_object(self):
        """
        Ожидается, что has_parents вернет True, если объект
        переданной в аргументах модели связан
        с прочей родительской моделью

        """

        self.assertTrue(RevertTool.has_parents(self.get_complex_dummy_object_related()))

    def test_has_parents_returns_false_for_complex_object(self):
        """
        Ожидается, что has_parents вернет False, если объект
        переданной в аргументах модели не связан
        с прочей родительской моделью

        """

        self.assertFalse(RevertTool.has_parents(self.get_complex_dummy_object_un_related()))

    def test_make_snapshot_complex_model_valid_json(self):
        """
        Ожидается, что снэпшот сложной модели конверитируется
        в JSON-formatted string

        """
        json.dumps(
            RevertTool.make_snapshot(self.get_complex_dummy_object_related()),
            indent=4)

    def test_revert_simple_model_one_step_successful(self):
        pass

    def test_revert_simple_model_arbitrary_step_successful(self):
        pass

    def test_revert_complex_model_one_step_successful(self):
        pass

    def test_revert_complex_model_arbitrary_step_successful(self):
        pass
