import json

from ddm.models import QuestionBase
from ddm.views import ProjectBaseView


class QuestionnaireDisplay(ProjectBaseView):
    template_name = 'ddm/questionnaire.html'
    view_name = 'questionnaire'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get question config
        q_config = [
            {'question': 1, 'type': 'single_choice', 'text': 'Choose one!',
             'items': [{'id': 1, 'label': 'Single Choice 1', 'value': 1, 'index': 1, 'random': False},
                       {'id': 2, 'label': 'Single Choice 2', 'value': 2, 'index': 2, 'random': False}]},
            {'question': 2, 'type': 'multi_choice', 'text': 'Choose the ones you like!',
             'items': [{'id': 3, 'label': 'Multi Choice 1', 'index': 1, 'random': False},
                       {'id': 4, 'label': 'Multi Choice 2', 'index': 2, 'random': False}]},
            {'question': 3, 'type': 'open', 'text': 'Write a sentence.',
             'options': {'max_length': None, 'display': 'regular'}},
            {'question': 4, 'type': 'matrix', 'text': 'Text for a matrix question!',
             'items': [{'id': 5, 'label': 'Matrix Item 1', 'index': 1, 'random': False},
                       {'id': 6, 'label': 'Matrix Item 2', 'index': 2, 'random': False}],
             'scale': [{'label': 'Scale Point A', 'index': 1, 'value': 1},
                       {'label': 'Scale Point B', 'index': 2, 'value': 2}]},
            {'question': 5, 'type': 'semantic_diff', 'text': 'Text for a semantic differential!',
             'items': [{'id': 7, 'label_left': 'Diff 1 Left', 'label_right': 'Diff 1 right', 'index': 1, 'random': False},
                       {'id': 8, 'label_left': 'Diff 2 Left', 'label_right': 'Diff 2 right', 'index': 2, 'random': False}],
             'scale': [{'label': 'Scale Point 1', 'index': 1, 'value': 1},
                       {'label': 'Scale Point 2', 'index': 2, 'value': 2}]},
            {'question': 6, 'type': 'transition', 'text': 'This is just some text. No action required!'}
        ]
        context['q_config'] = json.dumps(q_config)
        return context

    def get_question_config(self):
        q_config = []
        questions = QuestionBase.objects.filter(project=self.object)
        for question in questions:
            q_config.append(question.get_config())
        return q_config
