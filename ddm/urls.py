from django.urls import path, include

from ddm import views
from ddm import admin_views
from ddm.models import Question, Page, Trigger

ddm_admin_patterns = [
    path(
        'questionnaires',
        admin_views.QuestionnaireList.as_view(),
        name='questionnaire-list'
    ),
    path(
        'questionnaires/create',
        admin_views.QuestionnaireCreate.as_view(),
        name='questionnaire-create'
    ),
    path(
        'questionnaires/<int:pk>/delete/',
        admin_views.QuestionnaireDelete.as_view(),
        name='questionnaire-delete'
    ),
    path(
        'questionnaires/<int:pk>/',
        admin_views.QuestionnaireGeneralSettingsUpdate.as_view(),
        name='questionnaire-settings'
    ),

    # structure
    path(
        'questionnaires/<int:pk>/structure',
        admin_views.QuestionnaireStructureUpdate.as_view(),
        name='questionnaire-structure'
    ),

    # triggers
    path(
        'questionnaires/<int:pk>/triggers',
        admin_views.QuestionnaireTriggerList.as_view(),
        name='questionnaire-triggers'
    ),
    path(
        'triggers/tokengenerator/create/q=<int:q>',
        admin_views.TokenGeneratorCreate.as_view(),
        name=(Trigger.TYPE_TOKEN_GENERATOR + '-create')
    ),
    path(
        'triggers/tokengenerator/<int:pk>',
        admin_views.TokenGeneratorUpdate.as_view(),
        name=(Trigger.TYPE_TOKEN_GENERATOR + '-update')
    ),
    path(
        'triggers/varfromdata/create/q=<int:q>',
        admin_views.VariablesFromDataCreate.as_view(),
        name=(Trigger.TYPE_VAR_FROM_DATA + '-create')
    ),
    path(
        'triggers/varfromdata/<int:pk>',
        admin_views.VariablesFromDataUpdate.as_view(),
        name=(Trigger.TYPE_VAR_FROM_DATA + '-update')
    ),
    path(
        'triggers/email/create/q=<int:q>',
        admin_views.EmailTriggerCreate.as_view(),
        name=(Trigger.TYPE_EMAIL + '-create')
    ),
    path(
        'triggers/email/<int:pk>',
        admin_views.EmailTriggerUpdate.as_view(),
        name=(Trigger.TYPE_EMAIL + '-update')
    ),
    path(
        'triggers/cleanupload/create/q=<int:q>',
        admin_views.CleanUploadTriggerCreate.as_view(),
        name=(Trigger.TYPE_CLEAN_UL_DATA + '-create')
    ),
    path(
        'triggers/cleanupload/<int:pk>',
        admin_views.CleanUploadTriggerUpdate.as_view(),
        name=(Trigger.TYPE_CLEAN_UL_DATA + '-update')
    ),

    # external variable
    path(
        'questionnaires/<int:pk>/external_variables',
        admin_views.ExternalVariablesList.as_view(),
        name='externalvariables-list'
    ),

    # responses
    path(
        'questionnaires/<int:pk>/responses',
        admin_views.QuestionnaireResponseView.as_view(),
        name='questionnaire-responses'
    ),

    # uploads
    path(
        'questionnaires/<int:pk>/uploads',
        admin_views.UploadedDataView.as_view(),
        name='uploaded-data'
    ),

    # pages
    path(
        'questionnaires/<int:q>/questionpage/create/',
        admin_views.QuestionPageCreate.as_view(),
        name=(Page.PAGE_TYPE_QUESTION + '-create')
    ),
    path(
        'questionnaires/<int:q>/questionpage/<int:pk>/update',
        admin_views.QuestionPageUpdate.as_view(),
        name=(Page.PAGE_TYPE_QUESTION + '-update')
    ),
    path(
        'questionnaires/<int:q>/questionpage/<int:pk>/delete',
        admin_views.QuestionPageDelete.as_view(),
        name=(Page.PAGE_TYPE_QUESTION + '-delete')
    ),
    path(
        'questionnaires/<int:q>/endpage/create/',
        admin_views.EndPageCreate.as_view(),
        name=(Page.PAGE_TYPE_END + '-create')
    ),
    path(
        'questionnaires/<int:q>/endpage/<int:pk>/update',
        admin_views.EndPageUpdate.as_view(),
        name=(Page.PAGE_TYPE_END + '-update')
    ),
    path(
        'questionnaires/<int:q>/endpage/<int:pk>/delete',
        admin_views.EndPageDelete.as_view(),
        name=(Page.PAGE_TYPE_END + '-delete')
    ),

    # Filter
    path(
        'filter/<slug:filter_target>/<int:target_id>/',
        admin_views.update_filter,
        name='filter-update'
    ),
]

ddm_question_patterns = [
    # Open Question
    path(
        'openquestion/create/p=<int:p>',
        admin_views.OpenQuestionCreate.as_view(),
        name=(Question.TYPE_OPEN + '-create')
    ),
    path(
        'openquestion/<int:pk>/update',
        admin_views.OpenQuestionUpdate.as_view(),
        name=(Question.TYPE_OPEN + '-update')
    ),

    # Transition Question
    path(
        'transitionquestion/create/p=<int:p>',
        admin_views.TransitionQuestionCreate.as_view(),
        name=(Question.TYPE_TRANSITION + '-create')
    ),
    path(
        'transitionquestion/<int:pk>/update',
        admin_views.TransitionQuestionUpdate.as_view(),
        name=(Question.TYPE_TRANSITION + '-update')
    ),

    # Single Choice Question
    path(
        'singlechoice/create/p=<int:p>',
        admin_views.SingleChoiceQuestionCreate.as_view(),
        name=(Question.TYPE_SC + '-create')
    ),
    path(
        'singlechoice/<int:pk>/update',
        admin_views.SingleChoiceQuestionUpdate.as_view(),
        name=(Question.TYPE_SC + '-update')
    ),

    # Multi Choice Question
    path(
        'multichoice/create/p=<int:p>',
        admin_views.MultiChoiceQuestionCreate.as_view(),
        name=(Question.TYPE_MC + '-create')
    ),
    path(
        'multichoice/<int:pk>/update',
        admin_views.MultiChoiceQuestionUpdate.as_view(),
        name=(Question.TYPE_MC + '-update')
    ),

    # List Question
    path(
        'listquestion/create/p=<int:p>',
        admin_views.ListQuestionCreate.as_view(),
        name=(Question.TYPE_LIST + '-create')
    ),
    path(
        'listquestion/<int:pk>/update',
        admin_views.ListQuestionUpdate.as_view(),
        name=(Question.TYPE_LIST + '-update')
    ),

    # Matrix Question
    path(
        'matrixquestion/create/p=<int:p>',
        admin_views.MatrixQuestionCreate.as_view(),
        name=(Question.TYPE_MATRIX + '-create')
    ),
    path(
        'matrixquestion/<int:pk>/update',
        admin_views.MatrixQuestionUpdate.as_view(),
        name=(Question.TYPE_MATRIX + '-update')
    ),

    # Differential Question
    path(
        'differentialquestion/create/p=<int:p>',
        admin_views.DifferentialQuestionCreate.as_view(),
        name=(Question.TYPE_DIFFERENTIAL + '-create')
    ),
    path(
        'differentialquestion/<int:pk>/update',
        admin_views.DifferentialQuestionUpdate.as_view(),
        name=(Question.TYPE_DIFFERENTIAL + '-update')
    ),

    # File Upload
    path(
        'uploadquestion/create/p=<int:p>',
        admin_views.FileUploadQuestionCreate.as_view(),
        name=(Question.TYPE_FILE_UL + '-create')
    ),
    path(
        'uploadquestion/<int:pk>/update',
        admin_views.FileUploadQuestionUpdate.as_view(),
        name=(Question.TYPE_FILE_UL + '-update')
    ),

    # File Feedback
    path(
        'feedbackquestion/create/p=<int:p>',
        admin_views.FileFeedbackCreate.as_view(),
        name=(Question.TYPE_FILE_FEEDBACK + '-create')
    ),
    path(
        'feedbackquestion/<int:pk>/update',
        admin_views.FileFeedbackUpdate.as_view(),
        name=(Question.TYPE_FILE_FEEDBACK + '-update')
    ),
]

admin_patterns = [
    path(
        'processors/fpro',
        views.process_view,
        name='file-processor'
    ),
    path(
        'processors/fexp',
        views.export_file,
        name='file-export'
        ),
    path(
        'processors/response_delete',
        views.delete_questionnaire_responses,
        name='delete-responses'
        ),
]

public_patterns = [
    path(
        'survey/<str:slug>',
        views.display_questionnaire,
        name='public-questionnaire'
    ),
    path(
        'survey/admission/<str:slug>',
        views.questionnaire_admission,
        name='questionnaire-admission'
    ),
    path(
        'survey/continue/<str:slug>',
        views.questionnaire_continue,
        name='questionnaire-continue'
    ),
]

urlpatterns = [
    path('admin/surquest/', include(admin_patterns)),
    path('', include(public_patterns)),
    path('ddm/', include(ddm_admin_patterns)),
    path('ddm/questionnaires/<int:q>/questions/', include(ddm_question_patterns)),
]
