from django.urls import path, include

from ddm.views import admin, participation_flow
from ddm.views.apis import ExceptionAPI, ProjectDataAPI, ParticipantAPI


participation_flow_patterns = [
    path(r'briefing/', participation_flow.BriefingView.as_view(), name='briefing'),
    path(r'data-donation/', participation_flow.DataDonationView.as_view(), name='data-donation'),
    path(r'questionnaire/', participation_flow.QuestionnaireView.as_view(), name='questionnaire'),
    path(r'debriefing/', participation_flow.DebriefingView.as_view(), name='debriefing')
]

question_patterns = [
    path(r'', admin.QuestionnaireOverview.as_view(), name='questionnaire-overview'),
    path(r'<slug:question_type>/create/', admin.QuestionCreate.as_view(), name='question-create'),
    path(r'<slug:question_type>/<int:pk>/edit/', admin.QuestionEdit.as_view(), name='question-edit'),
    path(r'<slug:question_type>/<int:pk>/delete/', admin.QuestionDelete.as_view(), name='question-delete'),
    path(r'<slug:question_type>/<int:pk>/items/', admin.ItemEdit.as_view(), name='question-items'),
    path(r'<slug:question_type>/<int:pk>/scale/', admin.ScaleEdit.as_view(), name='question-scale'),
]

instruction_patterns = [
    path(r'', admin.InstructionOverview.as_view(), name='instruction-overview'),
    path(r'create/', admin.InstructionCreate.as_view(), name='instruction-create'),
    path(r'<int:pk>/edit/', admin.InstructionEdit.as_view(), name='instruction-edit'),
    path(r'<int:pk>/delete/', admin.InstructionDelete.as_view(), name='instruction-delete'),
]

data_donation_patterns = [
    path(r'', admin.data_donations.DataDonationOverview.as_view(), name='data-donation-overview'),
    path(r'blueprint/create/', admin.BlueprintCreate.as_view(), name='blueprint-create'),
    path(r'blueprint/<int:pk>/edit/', admin.BlueprintEdit.as_view(), name='blueprint-edit'),
    path(r'blueprint/<int:pk>/delete/', admin.BlueprintDelete.as_view(), name='blueprint-delete'),
    path(r'file-uploader/create/', admin.FileUploaderCreate.as_view(), name='file-uploader-create'),
    path(r'file-uploader/<int:pk>/edit/', admin.FileUploaderEdit.as_view(), name='file-uploader-edit'),
    path(r'file-uploader/<int:pk>/delete/', admin.FileUploaderDelete.as_view(), name='file-uploader-delete'),
    path(r'file-uploader/<int:file_uploader_pk>/instructions/', include(instruction_patterns)),
]

admin_patterns = [
    path(r'', admin.ProjectList.as_view(), name='project-list'),
    path(r'create/', admin.ProjectCreate.as_view(), name='project-create'),
    path(r'<int:pk>/', admin.ProjectDetail.as_view(), name='project-detail'),
    path(r'<int:pk>/edit/', admin.ProjectEdit.as_view(), name='project-edit'),
    path(r'<int:pk>/delete/', admin.ProjectDelete.as_view(), name='project-delete'),
    path(r'<int:pk>/briefing/', admin.BriefingEdit.as_view(), name='briefing-edit'),
    path(r'<int:pk>/debriefing/', admin.DebriefingEdit.as_view(), name='debriefing-edit'),
    path(r'<int:pk>/token/', admin.ProjectAPITokenView.as_view(), name='project-token'),
    path(r'<int:project_pk>/questionnaire/', include(question_patterns)),
    path(r'<int:project_pk>/data-donation/', include(data_donation_patterns)),
    path(r'<int:project_pk>/logs/', admin.ProjectLogsView.as_view(), name='project-logs'),
]

authentication_patterns = [
    path(r'register/', admin.DdmRegisterResearchProfileView.as_view(), name='ddm-register-researcher'),
    path(r'no-permission/', admin.DdmNoPermissionView.as_view(), name='ddm-no-permission'),
]

urlpatterns = [
    path(r'<slug:slug>/', include(participation_flow_patterns)),
    path(r'projects/', include(admin_patterns)),
    path(r'auth/', include(authentication_patterns)),
    path(r'<int:pk>/data/', ProjectDataAPI.as_view(), name='ddm-data-api'),
    path(r'<int:pk>/exceptions/', ExceptionAPI.as_view(), name='ddm-exceptions-api'),
    path(r'<int:pk>/delete-participant/<slug:participant_id>', ParticipantAPI.as_view(), name='ddm-participant-api'),
]
