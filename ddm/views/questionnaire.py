import json

from ddm.models import QuestionBase
from ddm.views import ProjectBaseView


class QuestionnaireDisplay(ProjectBaseView):
    template_name = 'ddm/questionnaire.html'
    view_name = 'questionnaire'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q_config = self.get_question_config()
        context['q_config'] = json.dumps(q_config)
        return context

    def get_question_config(self):
        q_config = []
        questions = QuestionBase.objects.filter(project=self.object)
        for question in questions:
            q_config.append(question.get_config(self.participant))
        return q_config
