import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, redirect
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from ddm.models import QuestionBase, QuestionnaireResponse, DataDonation
from ddm.views import ProjectBaseView

import logging
logger = logging.getLogger(__name__)


class QuestionnaireDisplay(ProjectBaseView):
    template_name = 'ddm/public/questionnaire.html'
    view_name = 'questionnaire'

    def render_to_response(self, context, **response_kwargs):
        # Check if there are any questions to display.
        if not len(context['q_config']) > 2:
            self.project_session['steps'][self.view_name]['state'] = 'completed'
            curr_step = self.steps.index(self.view_name)
            target = self.steps[curr_step + 1]
            return redirect(target, slug=self.object.slug)
        else:
            return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q_config = self.get_question_config()
        context['q_config'] = json.dumps(q_config)
        return context

    def get_question_config(self):
        q_config = []
        questions = QuestionBase.objects.filter(project=self.object)
        for question in questions:
            try:
                donation = DataDonation.objects.get(
                    blueprint=question.blueprint,
                    participant=self.participant
                )
                if donation.data:
                    q_config.append(question.get_config(self.participant))
            except ObjectDoesNotExist:
                logger.error(
                    f'No donation found for participant {self.participant.pk} '
                    f'and blueprint {question.blueprint.pk}.'
                )

        return q_config

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_response(request.POST)
        redirect_url = reverse(self.steps[self.current_step + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_response(self, response):
        try:
            post_data = json.loads(response['post_data'])
        except MultiValueDictKeyError:
            logger.error(f'POST did not contain expected key "post_data".')
            return

        for question_id in post_data:
            try:
                question = QuestionBase.objects.get(pk=int(question_id))
            except QuestionBase.doesNotExist:
                logger.error(f'Question with id={question_id} does not exist.')
                continue
            except ValueError:
                logger.error(
                    f'Received invalid question_id ({question_id}) in '
                    f'questionnaire post_data.'
                )
                continue

            question.validate_response(response[question_id])

        self.save_response(response)

    def save_response(self, response):
        QuestionnaireResponse.objects.create(
            project=self.object,
            participant=self.participant,
            time_submitted=timezone.now(),
            data=response
        )
