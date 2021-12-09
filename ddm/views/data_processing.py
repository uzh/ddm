import csv
import json
import zipfile

from datetime import datetime
from dateutil import parser
from fuzzywuzzy import fuzz
from lxml import html

from django.http import (
    HttpResponseNotFound, Http404,JsonResponse, StreamingHttpResponse
)
from django.views.decorators.csrf import csrf_protect

from ddm import tools
from ddm.models import (
    Questionnaire, QuestionnaireResponse, Question,
    QuestionnaireSubmission,
    UploadedData, UploadedDataTemp, FileUploadItem, FileUploadQuestion
)
from ddm.settings import SQ_TIMEZONE
from ddm.tools import fill_variable_placeholder, get_or_none


# TODO: Replace with javascript parser.
@csrf_protect
def process_view(request):
    """
    TODO: Update function description
    Function that processes a submitted file
    """
    def process_json_file(file_content, file_upload_item):
        process_status = {
            'message': None,
            'status': 'Not processed'
        }

        # Validate field names.
        if not file_upload_item.fields_are_valid(file_content):
            message = (
                'Die hochgeladene Datei enthält Datenfelder, die nicht '
                'unterstützt werden. Bitte überprüfen Sie, ob die '
                'ausgewählte Datei der geforderten Datei entspricht.'
            )
            process_status['message'] = message
            process_status['status'] = 'failed_ul'
            return None, process_status

        extracted_data = file_upload_item.extract_data(file_content)
        process_status['status'] = 'complete_ul'
        return extracted_data, process_status

    def process_html_file(file_content):
        process_status = {
            'message': None,
            'status': 'Not processed'
        }
        extracted_data = []
        html_tree = html.fromstring(file_content)

        # Check if tree is not empty
        i = 0
        out_of_drange = 0
        if len(html_tree) > 0:
            cutoff_date = parser.parse('2021-06-01T00:00:00.000')

            elements = html_tree.xpath('.//div[@class="mdl-grid"]')
            for element in elements:
                i += 1

                # get relevant div
                main_div = element.xpath(
                    './/div[contains(@class, "content-cell") and '
                    'not(contains(@class, "mdl-typography--caption")) and '
                    'not(contains(@class, "mdl-typography--text-right"))]'
                )

                # extract date
                if len(main_div) > 0:
                    date_infos = main_div[0].xpath('text()')
                    if len(date_infos) > 0:
                        date_raw = date_infos[-1]
                        try:
                            date = parser.parse(date_raw, ignoretz=True, dayfirst=True)
                        except ValueError as e:
                            # print("HTML: Value error bei parser.parse.")
                            # log?
                            continue
                        if date < cutoff_date:
                            out_of_drange += 1
                            continue
                    else:
                        continue

                    # Extract title and titleUrl.
                    url_infos = main_div[0].xpath('.//a[1]')
                    title_infos = main_div[0].xpath('descendant-or-self::*[count(preceding-sibling::br) < 1 and not(self::br)]/text()[count(preceding-sibling::br) < 1 and not(self::br)]')

                    if len(url_infos) > 0:
                        title_url_text = url_infos[0].xpath('@href')
                        if len(title_url_text) > 0:
                            title_url = title_url_text[0]
                        else:
                            title_url = 'NA'
                    else:
                        title_url = 'NA'

                    if len(title_infos) > 0:
                        title_text = ' '.join(title_infos)

                        if len(title_text) > 0:
                            title = title_text
                        else:
                            title = 'NA'
                    else:
                        continue

                    extracted_data.append(
                        {'title': title, 'titleUrl': title_url, 'time': date_raw})
        else:
            message = 'Die enthaltene Datei entspricht nicht der erwarteten Struktur.'
            process_status['message'] = message
            process_status['status'] = 'failed_ul'

        if len(extracted_data) == 0:
            data_row = {'status': 'no data in file'}
            extracted_data.append(data_row)

            if i > 0 and out_of_drange == i:
                message = (
                    'Es wurden keine Daten extrahiert – Die Datei enthielt '
                    'keine Daten zu Aktivitäten, die nach dem 01.06.2021 '
                    'aufgezeichnet wurden.'
                )
                process_status['message'] = message
                process_status['status'] = 'failed_ul'
            else:
                process_status['status'] = 'failed_ul'
        else:
            process_status['status'] = 'complete_ul'
        return extracted_data, process_status

    def process_single_file(file_upload_item, file, submission, data, response,
                            content_extracted=False):

        if content_extracted is False:
            # Check file size.
            if file.size/1000 > file_upload_item.max_filesize:
                message = (
                    'Die ausgewählte Datei ist zu gross. Die maximal '
                    'zulässige Dateigrösse beträgt {}MB'.format(file_upload_item.max_filesize/1000)
                )
                data['message'] = message
                return data

            # Check file type.
            file_type = file_upload_item.check_filetype(file.content_type)
            if file_type is None:
                message = (
                    'Das Format der hochgeladenen Daten wird nicht '
                    'unterstützt - möglicherweise haben Sie beim Datenexport "HTML" anstelle von "JSON" ausgewählt. '
                    'Bitte überprüfen Sie das Format der Dateien im ZIP-File und fordern Sie Ihre Daten gegebenenfalls '
                    'erneut von Google im JSON-Format an.'
                )
                data['message'] = message
                return data

            file_content = file_upload_item.get_file_content(file, file_type)

            # Validate field names.
            if not file_upload_item.fields_are_valid(file_content):
                message = (
                    'Die hochgeladene Datei enthält Datenfelder, die nicht '
                    'unterstützt werden. Bitte überprüfen Sie, ob die '
                    'ausgewählte Datei der geforderten Datei entspricht.'
                )
                data['message'] = message
                return data

            # extract fields
            extracted_data = file_upload_item.extract_data(file_content)

        else:

            # Validate field names.
            if not file_upload_item.fields_are_valid(file):
                message = (
                    'Die hochgeladene Datei enthält Datenfelder, die nicht '
                    'unterstützt werden. Bitte überprüfen Sie, ob die '
                    'ausgewählte Datei der geforderten Datei entspricht.'
                )
                data['message'] = message
                data['status'] = 'failed_ul'
                return data

            extracted_data = file_upload_item.extract_data(file)

        # Create an upload id.
        upload_id = tools.generate_id(10)
        while UploadedData.objects.filter(upload_id=upload_id).exists():
            upload_id = tools.generate_id(10)

        # Save the extracted data.
        UploadedData.objects.create(
            questionnaire=submission.questionnaire,
            upload_id=upload_id,
            data=extracted_data,
            upload_time=datetime.now(tz=SQ_TIMEZONE)
        )

        # TODO: Check this part:
        # If consent is required to store data, store upload_id in Temp table
        if file_upload_item.file_upload_question.requires_consent:
            # register upload id in temporary table until consent is given
            # if consent is not given, the registered upload files will be
            # deleted after a specified time (e.g. 48 hours)
            UploadedDataTemp.objects.create(
                questionnaire=submission.questionnaire,
                upload_id=upload_id,
                time=datetime.now(tz=SQ_TIMEZONE)
            )
            pass

        # Update the response object.
        ## Check if a previous data upload exists for this response.
        if response.answer != '':
            previous_ul_id = response.answer

            previous_upload = get_or_none(
                UploadedData, upload_id=previous_ul_id,
                questionnaire=submission.questionnaire)
            if previous_upload is not None:
                previous_upload.delete()

            previous_temp_entry = get_or_none(
                UploadedDataTemp, upload_id=previous_ul_id,
                questionnaire=submission.questionnaire)
            if previous_temp_entry is not None:
                previous_temp_entry.delete()

        response.answer = upload_id
        response.save()

        data['status'] = 'complete_ul'
        data['upload_id'] = upload_id
        return data

    def read_zip_or_none(zip_file, content):
        try:
            extracted_content = zip_file.read(content)
            extracted_content = json.loads(extracted_content.decode("utf-8-sig"))
            return extracted_content
        except KeyError:
            return None

    def initialize_response(sub, file_upload_item):
        response = QuestionnaireResponse.objects.filter(
            submission=sub,
            variable=file_upload_item.variable).first()

        if response is None:
            response = QuestionnaireResponse(
                submission=sub,
                variable=file_upload_item.variable,
                answer=''
            )
            response.save()

        return response

    if request.method == 'POST':
        status = {
            'status': 'failed_ul',
            'message': None,
            'upload_id': None,
            'upload_mode': None,
            'uploaded_files': {}
        }

        # Get the related question object.
        uploader_id = request.POST['question_id']
        upload_question = Question.objects.get(pk=uploader_id)

        # Get the submission.
        q_session_identifier = 'quest-' + str(upload_question.page.questionnaire.pk)
        session_id = request.session[q_session_identifier]
        submission = QuestionnaireSubmission.objects.get(session_id=session_id)

        # Check if exactly one file is appended.
        files = request.FILES

        # Check if exactly one file has been uploaded
        if len(files) != 1:
            if len(files) > 1:
                status['message'] = (
                    'More than 1 file submitted. Only 1 file can be '
                    'submitted at once.'
                )
            else:
                msg = 'Es wurde keine Datei ausgewählt.'
                status['message'] = msg

            return JsonResponse(status)

        file = files['file']

        if upload_question.question_type == Question.TYPE_FILE_UL:
            # Check if a file upload item is attached to the question.
            file_uploader_set = upload_question.fileuploaditem_set.all()
            if len(file_uploader_set) == 0:
                message = (
                    'Es ist ein interner Fehler aufgetreten.'
                )
                status['message'] = message
                return JsonResponse(status)

            if upload_question.upload_mode == FileUploadQuestion.SF:
                status['upload_mode'] = 'single file'

                file_uploader = file_uploader_set[0]

                # Initialize the response.
                response = initialize_response(submission, file_uploader)

                # Process the file.
                status = process_single_file(
                    file_uploader, file, submission, status, response)

            elif upload_question.upload_mode == FileUploadQuestion.ZIP:
                status['upload_mode'] = 'multiple files'

                # Check if the uploaded file is a .zip file.
                if not zipfile.is_zipfile(file):
                    message = (
                        'Die hochgeladene Datei ist nicht im .zip Format. '
                        'Bitte überprüfen Sie die ausgewählte Datei und '
                        'versuchen Sie es erneut.'
                    )
                    status['message'] = message
                    return JsonResponse(status)
                else:
                    zip_file = zipfile.ZipFile(file, 'r')

                # Iterate over all files contained in the .zip file.
                for file_uploader in file_uploader_set:

                    # Initialize response and save value for failure as default.
                    response = initialize_response(submission, file_uploader)
                    response.answer = submission.questionnaire.missing_not_answered
                    response.save()

                    # Take multiple filenames into account.
                    filename = file_uploader.expected_filename
                    expected_filenames = filename.split(';')
                    ref_name = expected_filenames[0]
                    expected_filenames = [fname.lower() for fname in expected_filenames]

                    status['uploaded_files'][ref_name] = 'failed'
                    for fname in expected_filenames:
                        depth = fname.count('/')

                        # Account for 'folder/file' structures in expected_filenames
                        for path in zip_file.namelist():
                            reduced_path = path.rsplit('/', depth + 1)
                            reduced_path = '/'.join(reduced_path[depth:]).lower()

                            if len(reduced_path) == 0 or reduced_path.endswith('/'): #TODO: here the accepted file endings could also already be checked.
                                continue

                            if fuzz.ratio(fname, reduced_path) > 85:

                                # Try to extract the file.
                                if path.endswith('.json') and fname.endswith('.json'):
                                    file_content = zip_file.read(path)
                                    file_content = json.loads(file_content.decode("utf-8-sig"))
                                    extracted_data, file_status = process_json_file(file_content, file_uploader)

                                elif path.endswith('.html') and fname.endswith('.html'):
                                    with zip_file.open(path, 'r') as f:
                                        file_content = f.read().decode('utf-8-sig')
                                    extracted_data, file_status = process_html_file(file_content)

                                else:
                                    # include error message
                                    continue

                                # Handle extracted data.
                                if file_status['status'] == 'complete_ul':
                                    # Create an upload id.
                                    upload_id = tools.generate_id(10)
                                    while UploadedData.objects.filter(upload_id=upload_id).exists():
                                        upload_id = tools.generate_id(10)

                                    # Save the extracted data.
                                    UploadedData.objects.create(
                                        questionnaire=submission.questionnaire,
                                        upload_id=upload_id,
                                        data=extracted_data,
                                        upload_time=datetime.now(tz=SQ_TIMEZONE)
                                    )

                                    # Update the response object.
                                    # Check if a previous data upload exists for this response.
                                    if response.answer != '':
                                        previous_ul_id = response.answer

                                        previous_upload = get_or_none(
                                            UploadedData, upload_id=previous_ul_id,
                                            questionnaire=submission.questionnaire)
                                        if previous_upload is not None:
                                            previous_upload.delete()

                                        previous_temp_entry = get_or_none(
                                            UploadedDataTemp, upload_id=previous_ul_id,
                                            questionnaire=submission.questionnaire)
                                        if previous_temp_entry is not None:
                                            previous_temp_entry.delete()

                                    response.answer = upload_id
                                    response.save()

                                    status['status'] = 'complete_ul'
                                    status['upload_id'] = upload_id

                                if file_status['status'] == 'complete_ul':
                                    status['uploaded_files'][ref_name] = 'success'
                                    break
                                else:
                                    status['message'] = file_status['message']

                            else:
                                continue

                        if status['uploaded_files'][ref_name] == 'success':
                            break

                # Check if all requested files have been successfully uploaded.
                successes = []
                for file, s in status['uploaded_files'].items():
                    if s != 'success':
                        successes.append(0)
                    else:
                        successes.append(1)

                if sum(successes) == len(successes):
                    status['status'] = 'complete_ul'
                elif sum(successes) > 0:
                    status['status'] = 'partial_ul'
                    if status['message'] is None:
                        status['message'] = (
                            'In der hochgeladenen ZIP-Datei war nur eines der beiden Datenfiles enthalten. '
                            '<br><br>Die von Ihnen hochgeladene ZIP-Datei enthielt die folgenden Ordner und Dateien:'
                            f'<br>{[f for f in zip_file.namelist() if "." in f]}'
                        )

                elif sum(successes) == 0:
                    if status['message'] is None:
                        status['message'] = (
                            '<b>Beim Auslesen der Daten ist ein Fehler aufgetreten</b> <br> '
                            'Mögliche Gründe sind:<br>'
                            '- Die falsche ZIP-Datei wurde ausgewählt <br>'
                            '- Das Format der hochgeladenen Daten wird nicht unterstützt. <br>'
                            '- Die hochgeladenen Daten sind in einer Sprache, die von der Applikation nicht erkannt '
                            'wird.<br><br>'
                            'Die von Ihnen hochgeladene ZIP-Datei enthielt die folgenden Ordner und Dateien:'
                            f'<br>{[f for f in zip_file.namelist() if "." in f]}'
                        )
                    status['status'] = 'failed_ul'

        return JsonResponse(status)

    if request.method == 'GET':
        raise Http404()


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# TODO: Replace with updated export functionality.
@csrf_protect
def export_file(request):
    """Exports requested data as .csv file.

    Args:
        request (HttpRequest): The request to export the data.

    Returns:
        JsonResponse/HttpResponseNotFound:
    """
    if request.method == 'POST':

        data_source = request.POST['data_source']

        if data_source == 'questionnaire':
            q_id = request.POST['q_id']
            q = Questionnaire.objects.get(pk=q_id)

            # Create a list of response dictionaries.
            q_subs = q.questionnairesubmission_set.all()
            raw_data = []
            for sub in q_subs:
                raw_data.append(
                    sub.get_related_responses(submission_fields=True))

            # Create a dictionary containing header:header key:value pairs.
            q_vars = q.get_var_names(for_overview=True)
            q_vars += ['sub_session_id', 'sub_id',
                       'sub_time_started', 'sub_time_submitted',
                       'sub_completion_time', 'sub_completed',
                       'sub_user_agent', 'sub_last_submitted_page']
            dict_header = {k: k for k in q_vars}
            raw_data.insert(0, dict_header)

            # Initialize a generator.
            data_gen = (r for r in raw_data)

            # Initialize streaming response.
            pseudo_buffer = Echo()
            writer = csv.DictWriter(
                pseudo_buffer, fieldnames=q_vars,
                restval='NA', extrasaction='ignore')
            writer.writeheader()
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in data_gen),
                content_type='text/csv')

            # Prepare response.
            filename = (
                    data_source +
                    '_export_' +
                    datetime.now(tz=SQ_TIMEZONE).strftime("%Y%m%d_%H%M%S") +
                    '.csv'
            )
            response['filename'] = filename

            cont_disp = ('attachment; filename=' + filename)
            response['Content-Disposition'] = cont_disp

            return response

        elif data_source == 'fileupload':
            ul_item_id = request.POST['q_id']
            ul_item = FileUploadItem.objects.get(pk=ul_item_id)

            json_data = ul_item.export_data()

            filename = (
                    data_source +
                    '_export_' +
                    datetime.now(tz=SQ_TIMEZONE).strftime("%Y%m%d_%H%M%S") +
                    '.json'
            )

            response = JsonResponse(json_data, safe=False)
            response['Content-Disposition'] = (
                    'attachment; filename="' + filename + '"')
            response['success'] = True
            response['filename'] = filename
            return response

        else:
            return HttpResponseNotFound('error message')


@csrf_protect
def delete_questionnaire_responses(request):
    """Deletes all submissions, responses and uploaded data associated with
    a questionnaire.

    Args:
        request (HttpRequest): The request to delete the questionnaire.

    Returns:
        JsonResponse: {'msg': 'Responses deleted.'}
    """

    if request.method == 'POST':
        questionnaire_id = request.POST['q_id']
        questionnaire = Questionnaire.objects.get(pk=questionnaire_id)

        # Delete all questionnaire submissions and responses.
        questionnaire_submissions = questionnaire.questionnairesubmission_set.all()
        questionnaire_submissions.delete()

        # Delete all associated uploaded data.
        data_uploads = questionnaire.uploadeddata_set.all()
        data_uploads.delete()

        data_uploads_temp = questionnaire.uploadeddatatemp_set.all()
        data_uploads_temp.delete()

        response_data = {
            'msg': 'Responses deleted.'
        }
        return JsonResponse(response_data)
