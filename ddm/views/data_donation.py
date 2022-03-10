import json

from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.safestring import SafeString
from django.views.decorators.cache import cache_page
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator

from ddm.models import DonationBlueprint, ZippedBlueprint
from ddm.views import ProjectBaseView
import zipfile

import logging
logger = logging.getLogger(__name__)


@method_decorator(cache_page(0), name='dispatch')
class DataUpload(ProjectBaseView):
    template_name = 'ddm/public/data_donation.html'
    view_name = 'data-donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ul_configs'] = SafeString(self.get_ul_configs())
        return context

    def get_ul_configs(self):
        ul_configs = []

        zipped_bps = ZippedBlueprint.objects.filter(project=self.object)
        for bp in zipped_bps:
            ul_configs.append({
                'ul_type': 'zip',
                'name': bp.name,
                'blueprints': bp.get_configs(),
                'instructions': bp.get_instructions()
            })

        blueprints = DonationBlueprint.objects.filter(
            project=self.object,
            zip_blueprint__isnull=True)
        for bp in blueprints:
            ul_configs.append({
                'ul_type': 'singlefile',
                'name': bp.name,
                'blueprints': [bp.get_config()],
                'instructions': bp.get_instructions()
            })
        return json.dumps(ul_configs)

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_uploads(request.FILES)
        redirect_url = reverse(self.steps[self.current_step + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_uploads(self, files):
        # Check if expected file in request.FILES.
        try:
            file = files['post_data']
        except MultiValueDictKeyError as err:
            logger.error(f'Did not receive expected file. {err}')
            return

        # Check if file is a zip file.
        if not zipfile.is_zipfile(file):
            logger.error('Received file is not a zip file.')
            return

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, 'r')
        if 'ul_data.json' not in unzipped_file.namelist():
            logger.error('"ul_data.json" is not in namelist.')
            return

        # Process donation data.
        file_data = json.loads(unzipped_file.read('ul_data.json').decode('utf-8'))
        for ul in file_data.keys():
            bp_id = ul
            bp_data = file_data[ul]
            try:
                bp = DonationBlueprint.objects.get(pk=bp_id)
            except DonationBlueprint.DoesNotExist as e:
                logger.error(
                    f'{e} – Donation blueprint with id={bp_id} does not exist')
                return

            bp.process_donation(bp_data, self.participant)
