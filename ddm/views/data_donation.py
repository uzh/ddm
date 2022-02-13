import json

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.safestring import SafeString
from django.template import RequestContext

from ddm.models import DonationBlueprint


class DataUpload(TemplateView):
    template_name = 'ddm/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ul_configs'] = SafeString(self.get_ul_configs())
        return context

    def get_ul_configs(self):
        # TODO: Adjust to only get DBPs associated with project.
        blueprints = DonationBlueprint.objects.all()
        ul_configs = []
        for bp in blueprints:
            ul_configs.append(bp.get_config())
        return json.dumps(ul_configs)

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        self.process_uploads(post_data)
        return render(RequestContext(request), 'ddm/test.html')

    def process_uploads(self, post_data):
        ul_keys = [k for k in post_data.keys() if 'data-ul-' in k]
        for k in ul_keys:
            ul_response = json.loads(post_data[k])
            try:
                bp = DonationBlueprint.objects.get(pk=ul_response['id'])
            except DonationBlueprint.DoesNotExist as e:
                # TODO: Log this error somewhere
                print(f'{e} With id={ul_response["id"]}')
                continue

            bp.process_donation(ul_response['data'])
