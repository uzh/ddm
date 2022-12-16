from django.urls import path, include

from ddm.views import admin, participation_flow
from ddm.views.exception_api import ExceptionAPI
from ddm.views.download_api import ProjectDataView


participation_flow_patterns = [
    path(r'intro/', participation_flow.EntryView.as_view(), name='project-entry'),
    path(r'data-donation/', participation_flow.DataDonationView.as_view(), name='data-donation'),
    path(r'questionnaire/', participation_flow.QuestionnaireView.as_view(), name='questionnaire'),
    path(r'end/', participation_flow.ExitView.as_view(), name='project-exit')
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

blueprint_patterns = [
    path(r'', admin.data_donations.ProjectBlueprintList.as_view(), name='blueprint-list'),
    path(r'blueprint/create/', admin.BlueprintCreate.as_view(), name='blueprint-create'),
    path(r'blueprint/<int:pk>/edit/', admin.BlueprintEdit.as_view(), name='blueprint-edit'),
    path(r'blueprint/<int:pk>/delete/', admin.BlueprintDelete.as_view(), name='blueprint-delete'),
    path(r'blueprint-container/create/', admin.BlueprintContainerCreate.as_view(), name='blueprint-container-create'),
    path(r'blueprint-container/<int:pk>/edit/', admin.BlueprintContainerEdit.as_view(), name='blueprint-container-edit'),
    path(r'blueprint-container/<int:pk>/delete/', admin.BlueprintContainerDelete.as_view(), name='blueprint-container-delete'),
    path(r'<slug:blueprint_type>/<int:blueprint_pk>/instructions/', include(instruction_patterns)),
]

admin_patterns = [
    path(r'', admin.ProjectList.as_view(), name='project-list'),
    path(r'create/', admin.ProjectCreate.as_view(), name='project-create'),
    path(r'<int:pk>/', admin.ProjectDetail.as_view(), name='project-detail'),
    path(r'<int:pk>/edit/', admin.ProjectEdit.as_view(), name='project-edit'),
    path(r'<int:pk>/delete/', admin.ProjectDelete.as_view(), name='project-delete'),
    path(r'<int:pk>/welcome-page/', admin.WelcomePageEdit.as_view(), name='welcome-page-edit'),
    path(r'<int:pk>/end-page/', admin.EndPageEdit.as_view(), name='end-page-edit'),
    path(r'<int:project_pk>/questionnaire/', include(question_patterns)),
    path(r'<int:project_pk>/donation-blueprints/', include(blueprint_patterns)),
    path(r'<int:project_pk>/exceptions/', admin.ExceptionList.as_view(), name='project-exceptions'),
]

authentication_patterns = [
    path(r'register/', admin.DdmRegisterResearchProfileView.as_view(), name='ddm-register-researcher'),
    path(r'no-permission/', admin.DdmNoPermissionView.as_view(), name='ddm-no-permission'),
]

urlpatterns = [
    path(r'<slug:slug>/', include(participation_flow_patterns)),
    path(r'projects/', include(admin_patterns)),
    path(r'auth/', include(authentication_patterns)),
    path(r'<int:pk>/download/', ProjectDataView.as_view(), name='ddm-download-api'),
    path(r'<int:pk>/exceptions', ExceptionAPI.as_view(), name='ddm-exceptions-api'),
]
