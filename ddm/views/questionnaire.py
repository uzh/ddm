import json

from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils import timezone

from ddm.models import QuestionBase, QuestionnaireResponse
from ddm.views import ProjectBaseView

import logging
logger = logging.getLogger(__name__)


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

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_response(request.POST['post_data'])
        redirect_url = reverse(self.steps[self.current_step],   # + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_response(self, response):
        response = json.loads(response)
        for question_id in response:
            try:
                question = QuestionBase.objects.get(pk=int(question_id))
            except QuestionBase.doesNotExist as e:
                logger.error(f'{e} – Question with id={question_id} '
                             'does not exist')
                continue
            except ValueError:
                logger.error('Received invalid question_id in '
                             f'questionnaire post_data: {e}')
                continue

            # TODO: Add method to question models: question.validate_response(response)

        self.save_response(response)

    def save_response(self, response):
        QuestionnaireResponse.objects.create(
            project=self.object,
            participant=self.participant,
            time_submitted=timezone.now(),
            data=response
        )
