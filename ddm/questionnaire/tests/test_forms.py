from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.forms import get_question_form
from ddm.questionnaire.models import OpenQuestion

User = get_user_model()


class TestOpenQuestionFormMinMaxValidation(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.form_class = get_question_form("open")

    def base_data(self, **overrides):
        data = {
            "name": "Test Question",
            "variable_name": "test_var",
            "page": 1,
            "index": 1,
            "text": "Question Text",
            "requirement_level": OpenQuestion.RequirementLevel.NOT_REQUIRED,
            "input_type": "text",
            "min_input_length": "",
            "max_input_length": "",
            "min_number_value": "",
            "max_number_value": "",
            "display": "small",
        }
        data.update(overrides)
        return data

    def test_form_includes_min_max_fields(self):
        form = self.form_class(instance=OpenQuestion(project=self.project))
        for field in (
            "min_input_length",
            "max_input_length",
            "min_number_value",
            "max_number_value",
        ):
            self.assertIn(field, form.fields)

    def test_min_input_length_greater_than_max_is_invalid(self):
        data = self.base_data(min_input_length=10, max_input_length=5)
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertFalse(form.is_valid())
        self.assertIn("min_input_length", form.errors)
        self.assertIn("max_input_length", form.errors)

    def test_min_number_value_greater_than_max_is_invalid(self):
        data = self.base_data(
            input_type="numbers", min_number_value=10, max_number_value=5
        )
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertFalse(form.is_valid())
        self.assertIn("min_number_value", form.errors)
        self.assertIn("max_number_value", form.errors)

    def test_valid_bounds_pass(self):
        data = self.base_data(min_input_length=5, max_input_length=10)
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_bounds_pass(self):
        data = self.base_data()
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertTrue(form.is_valid(), form.errors)
