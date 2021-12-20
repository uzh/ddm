from ddm.models import (
    Questionnaire, QuestionPage, EndPage, SingleChoiceQuestion,
    MultiChoiceQuestion, OpenQuestion, QuestionItem,
)
from django.test import TestCase


class TestQuestionnaireModel(TestCase):
    """
    """

    @classmethod
    def setUpTestData(cls):
        # Create questionnaire.
        cls.questionnaire = Questionnaire.objects.create(
            name='Test Questionnaire',
            description='Just to test',
            slug='test-slug'
        )

        # Create pages related to the questionnaire.
        cls.question_page_one = QuestionPage.objects.create(
            questionnaire=cls.questionnaire,
            name='Question Page One'
        )
        cls.question_page_two = QuestionPage.objects.create(
            questionnaire=cls.questionnaire,
            name='Question Page Two'
        )
        cls.end_page = EndPage.objects.create(
            questionnaire=cls.questionnaire,
            name='End Page'
        )

        # For each page, create a question and question items.
        cls.sc_question = SingleChoiceQuestion.objects.create(
            page=cls.question_page_one,
            name='SC Question',
            variable_name='var_sc_question'
        )
        cls.mc_question = MultiChoiceQuestion.objects.create(
            page=cls.question_page_two,
            name='MC Question',
        )
        cls.open_question = OpenQuestion.objects.create(
            page=cls.end_page,
            name='Open Question',
            variable_name='var_open_question'
        )

        # Create Items for Questions.
        cls.sc_item_a = QuestionItem.objects.create(
            question=cls.sc_question,
            variable_name='var_sc_item_a',
            index=1,
            value=1
        )
        cls.mc_item_a = QuestionItem.objects.create(
            question=cls.mc_question,
            variable_name='var_mc_item_a',
            answer='MC Choice A',
            index=1,
            value=1
        )
        cls.mc_item_b = QuestionItem.objects.create(
            question=cls.mc_question,
            variable_name='var_mc_item_b',
            answer='MC Choice B',
            index=2,
            value=2
        )

    def test_questionnaire_str(self):
        """ Tests the __str__ of the Questionnaire model. """
        self.assertEqual(str(self.questionnaire), 'Test Questionnaire')

    def test_session_identifier(self):
        """ Tests the session identifier of the Questionnaire model. """
        self.assertEqual(self.questionnaire.get_session_identifier(),
                         'quest-' + str(self.questionnaire.pk))

    def test_missing_values_list(self):
        """ Tests that the list of missing values of the Questionnaire model
        is returned correctly. """
        miss_not_string = self.questionnaire.get_missing_values()
        self.assertCountEqual(miss_not_string, [-77, -66, -88])

        miss_as_string = self.questionnaire.get_missing_values(as_string=True)
        self.assertCountEqual(miss_as_string, ['-77', '-66', '-88'])

    def test_get_page_indices(self):
        """ Tests the returned list of indices of all related pages. """
        expected_page_indices = [
            self.question_page_one.pk,
            self.question_page_two.pk,
            self.end_page.pk
        ]
        page_indices = self.questionnaire.get_page_indices()
        self.assertCountEqual(page_indices, expected_page_indices)

    def test_get_questions(self):
        """ Tests that the set of all related questions is returned. """
        expected_questions = [
            repr(self.sc_question),
            repr(self.mc_question),
            repr(self.open_question)
        ]
        questions = self.questionnaire.get_questions()
        self.assertQuerysetEqual(questions, expected_questions)

    def test_get_var_names(self):
        """ Test the returned list of names of all associated variables. """
        # TODO: Create tests with other definitions of function parameters.
        expected_var_names = [
            self.sc_question.variable_name, self.open_question.variable_name,
            self.sc_item_a.variable_name, self.mc_item_a.variable_name,
            self.mc_item_b.variable_name,
        ]
        var_names = self.questionnaire.get_var_names()
        self.assertCountEqual(var_names, expected_var_names)

    def test_get_variables_for_filter(self):
        """ Tests the correct list of variables is returned for a question. """
        expected_var_selection = [
            (self.mc_item_a.variable_name,
             f'{self.mc_item_a.variable_name}: {self.mc_item_a.answer}'),
            (self.mc_item_b.variable_name,
             f'{self.mc_item_b.variable_name}: {self.mc_item_b.answer}'),
            (self.open_question.variable_name,
             f'{self.open_question.variable_name}: {self.open_question.name}'),
        ]
        var_selection = self.questionnaire.get_variables_for_filter(self.sc_question)
        self.assertCountEqual(var_selection, expected_var_selection)

    def test_get_submission_stats(self):
        """ Tests that the correct submission statistics are returned. """
        # Test case for questionnaire without submissions.
        expected_stats = {'total': 0, 'completed': 0, 'completion_rate': None}
        stats = self.questionnaire.get_submission_stats()
        self.assertDictEqual(stats, expected_stats)

        # Test case for questionnaire with submissions.
        #TODO: Add test case with submissions. Needs related pages, questions, and submissions.
        pass
