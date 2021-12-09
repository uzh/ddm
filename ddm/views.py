import csv
import json
import zipfile

from datetime import datetime
from dateutil import parser
from fuzzywuzzy import fuzz
from lxml import html

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404,
    JsonResponse, StreamingHttpResponse
)
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from ddm import tools
from ddm.models import (
    Questionnaire, QuestionnaireResponse, Question,
    QuestionnaireSubmission, QuestionnaireAccessToken,
    Page, Variable, MultiChoiceQuestion,
    UploadedData, UploadedDataTemp, FileUploadItem, FileUploadQuestion
)
from ddm.settings import SQ_TIMEZONE
from ddm.tools import fill_variable_placeholder, get_or_none


class QuestionnaireOverview(LoginRequiredMixin, TemplateView):
    """View that is integrated into the admin panel.
    """

    model = Questionnaire
    template = ''

    fields = [
        'name',
        'description',
        'date_created',
    ]


class QuestionnaireThankYou(TemplateView):
    """Simple template view displaying a thank you page.
    """

    template_name = "ddm/questionnaire/thankyou.html"


class QuestionnaireAlreadyCompleted(TemplateView):
    """Simple template view displaying an "already completed" notification.
    """

    template_name = "ddm/questionnaire/already_completed.html"


# Helper function for other views
def populate_external_vars(questionnaire, submission, request, mode):
    """Populates the external variables of a questionnaire from url parameters
    and data associated to tokens.

    Args:
        questionnaire (Questionnaire): A questionnaire instance.
        submission (QuestionnaireSubmission): A QuestionnaireSubmission
            instance.
        request (HttpRequest): The request to render a questionnaire.
        mode (str): Must be 'url' or 'token'.
            When mode is 'url' the external variables will be populated based on
            parameters provided in the url.
            When mode is 'token' the external variables will be populated based
            on the provided token.

    Returns:
        None
    """

    if mode == 'url':
        external_vars = questionnaire.externalvariable_set.filter(source='url')
    elif mode == 'token':
        external_vars = questionnaire.externalvariable_set.filter(source='token')
    else:
        # TODO: raise error
        return

    for var in external_vars:
        save_response = True
        # Check for variables with tokens as source.
        if var.source == var.STOKEN:
            token = submission.access_token
            token_data = QuestionnaireAccessToken.objects.get(token=token).data
            if isinstance(token_data, dict):
                if var.related_parameter in token_data:
                    value = token_data[var.related_parameter]
                else:
                    value = questionnaire.missing_not_answered
            else:
                value = questionnaire.missing_invalid
        # Check for variables with URL parameters as source.
        elif var.source == var.SURLPARA:
            value = request.GET.get(
                var.related_parameter, questionnaire.missing_not_answered)
        else:
            # TODO: catch error
            save_response = False
            pass

        if save_response:
            response = QuestionnaireResponse(
                submission=submission,
                variable=var.variable,
                answer=value
            )
            response.save()
    return


# DISPLAY QUESTIONNAIRE AND HELPER FUNCTIONS
def get_validated_response_list(questions_to_validate, post_data, submission):
    """Validates the responses related to a given set of questions.

    Args:
        questions_to_validate (list): A list of Questions instances to validate.
        post_data (dict): The POST data retrieved from a request instance.
        submission (QuestionnaireSubmission): A QuestionnaireSubmission
            instance.

    Returns:
        list: A list of validated response items. Each response item has the
        following structure:

        {'submission': submission,
         'variable': related_variable,
         'answer': response value}
    """

    # Validate responses.
    validated_responses = []
    for question in questions_to_validate:
        question_responses = question.create_question_response(post_data)
        validated_responses += question_responses

    # Prepare validated responses so that they can be saved afterwards.
    response_items = []
    for response in validated_responses:
        related_variable = Variable.objects.get(
            name=response['var_name'],
            questionnaire=submission.questionnaire
        )

        response_items.append(
            {'submission': submission,
             'variable': related_variable,
             'answer': response['value']}
        )

    return response_items


def save_or_update_responses(response_list):
    """Saves or updates validated responses.

    If a response instance already exists it is update and created otherwise.

    Args:
        response_list (list): A list of responses as generated by the
            get_validated_response_list() function.

    Returns:
        None
    """

    for response in response_list:
        existing_response = QuestionnaireResponse.objects.filter(
            submission=response['submission'],
            variable=response['variable']).first()

        if existing_response is not None:
            existing_response.answer = response['answer']
            existing_response.save()
        else:
            new_response = QuestionnaireResponse(
                submission=response['submission'],
                variable=response['variable'],
                answer=response['answer']
            )
            new_response.save()

    return


def get_required_but_missing(question_set, post_data):
    """Checks for missing question responses in the POST data.

    Args:
        question_set (QuerySet): A set of questions for which it will be checked
            if a response exists in the post_data.
        post_data (django.http.QueryDict): The POST data retrieved from a
            request instance.

    Returns:
        list: A list containing the names of variables that are required but
            are missing in the POST data.
    """

    var_names = []
    var_names_fixed = []
    for question in question_set:
        if question.required:
            # Add variable identifier (variable_name).
            if hasattr(question, 'variable_name'):
                var_name = question.variable_name
                var_names.append(var_name)

            # Extra validation for file upload questions.
            elif isinstance(question, FileUploadQuestion):
                var_name = 'upload-' + str(question.pk)
                if post_data[var_name] == '':
                    var_names_fixed.append(var_name)

            else:
                question_items = question.questionitem_set.all()

                # Exclude multi-choice items.
                if not isinstance(question, MultiChoiceQuestion):
                    for item in question_items:
                        var_name = item.variable_name
                        var_names.append(var_name)

    required_but_missing = list(set(var_names) - set(post_data.keys()))
    required_but_missing = list(set(required_but_missing))
    required_but_missing += var_names_fixed

    return required_but_missing


def create_new_submission(request, questionnaire):
    """Create a new submission instance for a questionnaire.

    Args:
        request (HttpRequest): The request to render a questionnaire.
        questionnaire (Questionnaire): The requested questionnaire instance.

    Returns:
        QuestionnaireSubmission: A new questionnaire submission instance.
    """

    # Generate a session id.
    session_id = tools.generate_id(8, letters=False)
    while QuestionnaireSubmission.objects.filter(session_id=session_id).exists():
        session_id = tools.generate_id(8, letters=False)

    # Create a new session.
    questionnaire_session_id = questionnaire.get_session_identifier()
    request.session[questionnaire_session_id] = session_id

    # Create a new submission.
    submission = QuestionnaireSubmission(
        questionnaire=questionnaire,
        session_id=session_id,
        time_started=datetime.now(tz=SQ_TIMEZONE)
    )
    submission.save()

    return submission


def get_or_create_submission(request, questionnaire):
    """Get or create a QuestionnaireSubmission instance.

    Check if an existing QuestionnaireSubmission instance is already associated
    with a questionnaire request. If yes, return the existing submission
    instance. If no, create a new instance.

    Args:
        request (HttpRequest): The request to render a questionnaire.
        questionnaire (Questionnaire): The requested questionnaire instance.

    Returns:
        QuestionnaireSubmission: Submission instance for this questionnaire
        request.
    """

    questionnaire_session_id = questionnaire.get_session_identifier()
    if questionnaire_session_id in request.session:
        # Get the submission instance registered in the current session.
        session_id = request.session[questionnaire_session_id]
        submission = get_or_none(QuestionnaireSubmission, session_id=session_id)

        # Create a new submission if none has been created yet.
        if submission is None:
            submission = create_new_submission(request, questionnaire)
            populate_external_vars(
                questionnaire, submission, request, mode='url')

    else:
        # Create a new submission.
        submission = create_new_submission(request, questionnaire)
        # Populate external variables from URL parameters.
        populate_external_vars(questionnaire, submission, request, mode='url')

    return submission


def get_current_page_index(submission, questionnaire):
    """Get the index of the questionnaire page that should be rendered next.

    Args:
        questionnaire (Questionnaire): The questionnaire from which the page
            index should be determined.
        submission (QuestionnaireSubmission): The submission instance of the
            current survey respondent.

    Returns:
        int: Index of the page that should be rendered next.
    """

    page_indices = questionnaire.get_page_indices()

    current_page_index = submission.current_page
    if current_page_index is None:
        current_page_index = min(page_indices)
    elif current_page_index == submission.last_submitted_page:
        current_page_index += 1

    # Make sure that the current page is in 'page_indices'. This step accounts
    # for non-consecutive page numbering.
    # TODO: Force consecutiveness in page numbers and adjust/discard this check here
    while current_page_index not in page_indices:
        current_page_index += 1
        if current_page_index > max(page_indices):
            # TODO: raise error
            break

    return current_page_index


def add_questions_to_context(context, questions_to_add, submission):
    """Add information about a set of questions to the context.

     Args:
        context (dict): The context dictionary that should be updated.
        questions_to_add (list): A list of Question instances.
        submission (QuestionnaireSubmission): A QuestionnaireSubmission
            instance.

    Returns:
        dict: The updated context.
    """

    context['template_var_names'] = []
    context['all_variables'] = []
    context['initial_data'] = {}
    context['filtered_out_variables'] = []

    context['file_data'] = None
    context['file_fields'] = None

    for question in questions_to_add:
        # Retrieve the variable names needed for the question template.
        if hasattr(question, 'variable_name'):
            context['template_var_names'].append(question.variable_name)
        else:
            context['template_var_names'].append('q-' + str(question.pk))

        # Get the response variables belonging to this question.
        all_variables = question.get_response_variables(var_form='regular')
        context['all_variables'] += all_variables

        # Get the initial data for this question.
        context['initial_data'].update(question.get_saved_responses(submission))

        # TODO: Improve! Current solution seems rough.
        if question.question_type == 'filefeedback':
            # Get the data related to the file feedback question.
            if question.display_upload_table:
                file_data = question.get_table_data(submission)
                context['file_data'] = file_data['data']
                context['file_fields'] = file_data['table_fields']

        # Get variables that must be filtered out.
        filtered_out = question.get_filtered_variable_names(submission)
        context['filtered_out_variables'] += filtered_out

    return context


def display_questionnaire(request, slug):
    """Displays a questionnaire.

    Renders a requested questionnaire. The questionnaire page to be rendered is
    determined from progress information stored in the session cookie.

    Args:
        request (HttpRequest): The request to render the questionnaire.
        slug (str): Public URL identifier of of the questionnaire.

    Returns:
        HttpResponse: The rendered questionnaire.
    """

    # Define which template will be used to display the questionnaire.
    template = 'ddm/questionnaire/display.html'

    # Initialize a context variable.
    context = {}

    # Get the questionnaire object and related information.
    questionnaire = get_object_or_404(Questionnaire, slug=slug)
    context['questionnaire'] = questionnaire

    # If the questionnaire does not contain any pages,
    # render an 'inactive' template.
    if not questionnaire.page_set.all().exists():
        template = 'ddm/questionnaire/inactive.html'
        return render(request, template)

    if request.method == 'GET':

        # Check if the questionnaire is currently active.
        if not questionnaire.active:
            template = 'ddm/questionnaire/inactive.html'
            return render(request, template)

        # Retrieve the submission instance related to the questionnaire.
        submission = get_or_create_submission(request, questionnaire)

        # Check if the questionnaire has already been completed.
        if submission.completed:
            template = 'ddm/questionnaire/already_completed.html'
            return render(request, template)

        # Check if access to the questionnaire is granted.
        if questionnaire.accessibility != 'public':
            if submission.access_token is None:
                return redirect('questionnaire-admission', slug=slug)

        # Determine which page should be rendered.
        page_determined = False
        while not page_determined:
            submission.current_page = get_current_page_index(
                submission, questionnaire)
            page = Page.objects.get(
                questionnaire=questionnaire,
                index=submission.current_page
            )

            # Check if the current page is an end page.
            if page.page_type == Page.PAGE_TYPE_END:
                context['last_page'] = True
            else:
                context['last_page'] = False

            # Get the set of questions belonging to the current page.
            questions_on_page = page.question_set.all()
            context['questions'] = questions_on_page

            # Add information related to the questions to the context.
            context = add_questions_to_context(
                context, questions_on_page, submission)

            # Check whether there are questions to display or if all questions
            # on the page are filtered out.
            if len(set(context['template_var_names']) -
                   set(context['filtered_out_variables'])) != 0:
                # There are questions to be displayed so the loop is terminated.
                page_determined = True
            else:
                # All questions on the page are filtered out. Therefore, for all
                # filtered out variables, save the value for
                # 'missing_not_answered' in the respective response.
                pseudo_post_data = {}
                for var in context['all_variables']:
                    pseudo_post_data[var] = questionnaire.missing_not_seen

                # Validate pseudo post data.
                response_items = get_validated_response_list(
                    questions_on_page, pseudo_post_data, submission)

                # Save the validated responses.
                save_or_update_responses(response_items)

                # Update page index.
                if submission.step_back:
                    submission.current_page = submission.last_submitted_page - 1
                    submission.last_submitted_page -= 1
                else:
                    submission.last_submitted_page = submission.current_page

                # TODO: Create a loop termination check, e.g. with first or last page.

        # Execute the triggers that must be executed before the page is loaded.
        page.execute_triggers('before', submission)

        # Add to the context if the back button should be displayed.
        if page.index == min(questionnaire.get_page_indices()):
            context['show_back_button'] = False
        else:
            context['show_back_button'] = page.show_back_button

        # Compute the percentage of progress for the graphical progress bar.
        progress = submission.current_page / max(questionnaire.get_page_indices()) * 100
        context['progress'] = progress

        # Save submission and add to context
        submission.save()
        context['submission'] = submission

        # Add final information to the context.
        context['missing_filtered_value'] = questionnaire.missing_not_seen

        return render(request, template, context)

    if request.method == 'POST':
        post_data = request.POST.copy()

        # Retrieve the submission instance.
        submission = get_or_create_submission(request, questionnaire)
        current_page_index = submission.current_page

        # Check if the 'back' or 'next' button has been clicked.
        if 'submit-back' in request.POST:
            # Update the submission instance.
            submission.current_page = submission.last_submitted_page - 1
            submission.last_submitted_page -= 1
            submission.step_back = True
            submission.save()
            return HttpResponseRedirect(request.path_info)

        elif 'submit-next' in request.POST:
            submission.step_back = False

            page = Page.objects.get(
                questionnaire=questionnaire, index=current_page_index)
            questions_on_page = page.question_set.all()
            context['questions'] = questions_on_page

            # Get a list of required but missing variables.
            required_but_missing = get_required_but_missing(questions_on_page,
                                                            post_data)
            context['required_but_missing'] = required_but_missing

            # If one or more inputs are required but missing, reload the site
            # and display error messages.
            if len(required_but_missing) > 0:
                # Check if the page is an end page.
                if page.page_type == Page.PAGE_TYPE_END:
                    context['last_page'] = True
                else:
                    context['last_page'] = False

                # Add information to context.
                filtered_out_variables = []
                for question in questions_on_page:
                    filtered_out_variables += question.get_filtered_variable_names(submission)
                    if question.question_type == Question.TYPE_FILE_FEEDBACK:
                        if question.display_upload_table:
                            ffb_data = question.get_table_data(submission)
                            context['file_data'] = ffb_data['data']
                            context['file_fields'] = ffb_data['table_fields']
                context['filtered_vars'] = filtered_out_variables

                # Save the submission and add it to the context.
                submission.save()
                context['submission'] = submission

                # Add final information to the context.
                context['initial_data'] = post_data
                context['missing_filtered_value'] = questionnaire.missing_not_seen

                return render(request, template, context)

            # Validate the post data and get a list of valid response items.
            response_items = get_validated_response_list(questions_on_page,
                                                         post_data,
                                                         submission)

            # Save or update all response instances.
            save_or_update_responses(response_items)

            # TODO: Add a better description of what's happening here.
            # Update entries in UploadedDataTemp.
            questions_on_page = page.question_set.all()
            for question in questions_on_page:
                if question.question_type == Question.TYPE_FILE_FEEDBACK:
                    question.update_data_entries(submission)

            # Execute the triggers that must be executed after the page has been
            # submitted.
            page.execute_triggers('after', submission)

            # Update submission instance and render the next page.
            if page.page_type == Page.PAGE_TYPE_END:
                # Close the submission instance.
                submission.close_submission(post_data)

                if page.redirect:
                    target_url = page.redirect_url
                    target_url = fill_variable_placeholder(
                        target_url, submission)
                    return redirect(target_url)

                else:
                    # Render the thank you template.
                    template = 'ddm/questionnaire/thankyou.html'
                    return render(request, template)

            else:
                # Update the submission instance.
                submission.last_submitted_page = current_page_index
                submission.save()

                # Redirect to the next question page.
                return HttpResponseRedirect(request.path_info)


def questionnaire_admission(request, slug):
    """Renders a questionnaire's admission page.

    Args:
        request (HttpRequest): The request to render the questionnaire.
        slug (str): Public URL identifier of of the questionnaire.

    Returns:
        HttpResponse: The rendered questionnaire admission page.
    """

    questionnaire = get_object_or_404(Questionnaire, slug=slug)
    q_session_identifier = 'quest-' + str(questionnaire.pk)
    template = 'ddm/questionnaire/admission.html'

    if request.method == 'GET':
        # Check if the questionnaire is active.
        if not questionnaire.active:
            return redirect('public-questionnaire', slug=slug)

        # Check if a session has already been started.
        if q_session_identifier not in request.session:
            return redirect('public-questionnaire', slug=slug)
        else:
            session_id = request.session[q_session_identifier]

        # Get the submission instance related to the current session.
        sub = QuestionnaireSubmission.objects.get(session_id=session_id)

        # If there is already an access token registered with the submission,
        # redirect to the questionnaire. Otherwise, render the admission site.
        if sub.access_token is not None:
            return redirect('public-questionnaire', slug=slug)
        else:
            return render(request, template)

    if request.method == 'POST':
        # Check if the submitted token is valid.
        post_data = request.POST.copy()
        submitted_token = post_data['access_token']
        valid_tokens = QuestionnaireAccessToken.objects.filter(
            questionnaire=questionnaire)

        # If the submitted token is valid and active, the user is redirected
        # to the questionnaire. Otherwise, return to the admission page and
        # display an error message.
        if valid_tokens.filter(token=submitted_token).exists():
            matched_token = valid_tokens.get(token=submitted_token)

            if matched_token.active:
                # Save the used token in the submission instance.
                session_id = request.session[q_session_identifier]
                sub = QuestionnaireSubmission.objects.get(
                    session_id=session_id)
                sub.access_token = submitted_token
                sub.save()

                # Populate external variables from URL parameters.
                populate_external_vars(
                    sub.questionnaire, sub, request, mode='token')

                return redirect('public-questionnaire', slug=slug)

            else:
                error_message = (
                    'Der Zugangscode "{submitted_token}" wurde bereits verwendet und ist '
                    'nicht länger aktiv.'
                )

        else:
            error_message = (
                'Der Zugangscode "{submitted_token}" ist leider '
                'ungültig.'
            )

        context = {'error_message': error_message}
        return render(request, template, context)


def questionnaire_continue(request, slug):
    """Renders a continuation page.

    Args:
        request (HttpRequest): The request to render the questionnaire.
        slug (str): Public URL identifier of of the questionnaire.

    Returns:
        HttpResponse: The rendered continuation page.
    """

    questionnaire = get_object_or_404(Questionnaire, slug=slug)
    q_session_identifier = 'quest-' + str(questionnaire.pk)
    template = 'ddm/questionnaire/continuation.html'

    if request.method == 'GET':
        # Check if the questionnaire is active.
        if not questionnaire.active:
            return redirect('public-questionnaire', slug=slug)

        # Check if the questionnaire allows continuation.
        if not questionnaire.enable_continuation:
            return redirect('public-questionnaire', slug=slug)
        else:
            return render(request, template)

    if request.method == 'POST':
        # Check if a session has already been initiated.
        if q_session_identifier in request.session:
            initial_session_id = request.session[q_session_identifier]
        else:
            initial_session_id = None

        # Check if the token is valid.
        post_data = request.POST.copy()
        submitted_token = post_data['access_token']

        valid_tokens = QuestionnaireAccessToken.objects.filter(
            questionnaire=questionnaire)

        if valid_tokens.filter(token=submitted_token).exists():
            matched_token = valid_tokens.get(token=submitted_token)

            if matched_token.active:
                continued_session = None
                # Get the linked session to continue.
                token_data = matched_token.data
                if isinstance(token_data, dict):
                    if 'int_session_id' in token_data:
                        continued_session = token_data['int_session_id']
                    else:
                        continued_session = None

                if continued_session is None:
                    return redirect('public-questionnaire', slug=slug)
                else:
                    request.session[q_session_identifier] = continued_session

                    # Delete the old submission instance.
                    if initial_session_id is not None:
                        sub = QuestionnaireSubmission.objects.get(
                            session_id=initial_session_id)
                        sub.delete()

                return redirect('public-questionnaire', slug=slug)

            else:
                error_message = (
                    f'Der Zugangscode "{submitted_token}" wurde bereits verwendet und ist '
                    'nicht länger aktiv.'
                )

        else:
            error_message = (
                f'Der Zugangscode "{submitted_token}" ist leider '
                'ungültig.'
            )

        context = {'error_message': error_message}
        return render(request, template, context)


# TODO: Relocate file handlers to a separate .py file.
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
                data = process_single_file(
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
