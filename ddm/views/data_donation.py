import json

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.safestring import SafeString
from django.views.decorators.cache import cache_page
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator

from ddm.models import DonationBlueprint, ZippedBlueprint
import zipfile

import logging
logger = logging.getLogger(__name__)


@method_decorator(cache_page(0), name='dispatch')
class DataUpload(TemplateView):
    template_name = 'ddm/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ul_configs'] = SafeString(self.get_ul_configs())
        return context

    def get_ul_configs(self):
        # TODO: Adjust to only get BPs associated with project. With SLUG in view url -> maybe use detailview
        ul_configs = []
        zipped_bps = ZippedBlueprint.objects.all()
        for bp in zipped_bps:
            ul_configs.append(bp.get_config())

        blueprints = DonationBlueprint.objects.filter(zip_blueprint__isnull=True)
        for bp in blueprints:
            ul_configs.append({
                'ul_type': 'singlefile',
                'blueprints': [bp.get_config()]
            })
        return json.dumps(ul_configs)

    def post(self, request, *args, **kwargs):
        self.process_uploads(request.FILES)
        return render(request, 'ddm/test.html', status=204)

    @staticmethod
    def process_uploads(files):
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
                logger.error(f'{e} – Donation blueprint with id={bp_id} does not exist')
                return

            bp.process_donation(bp_data)
