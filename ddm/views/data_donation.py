import json

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.safestring import SafeString
from django.views.decorators.cache import cache_page
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator

from ddm.models import DonationBlueprint, ZippedBlueprint
import zipfile


@method_decorator(cache_page(0), name='dispatch')
class DataUpload(TemplateView):
    template_name = 'ddm/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ul_configs'] = SafeString(self.get_ul_configs())
        return context

    def get_ul_configs(self):
        # TODO: Adjust to only get BPs associated with project.
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

    def validate_request_files(self, files):
        # Check if expected file in request.FILES.
        try:
            file = files['post_data']
        except MultiValueDictKeyError as err:
            print(err.args)

        # Check if file is a zip file.
        if not zipfile.is_zipfile(file):
            # TODO: raise/log error
            print('Received file is not a zip file.')
            pass

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, 'r')
        if 'ul_data.json' not in unzipped_file.namelist():
            # TODO: raise/log error
            print('"ul_data.json" not in namelist.')
            pass

        return unzipped_file

    def process_uploads(self, files):
        unzipped_file = self.validate_request_files(files)
        file_data = json.loads(unzipped_file.read('ul_data.json').decode('utf-8'))

        for ul in file_data.keys():
            bp_id = ul
            bp_data = file_data[ul]
            try:
                bp = DonationBlueprint.objects.get(pk=bp_id)
            except DonationBlueprint.DoesNotExist as e:
                # TODO: Log this error somewhere
                print(f'{e} – With id={bp_id} does not exist')
                continue

            bp.process_donation(bp_data)
