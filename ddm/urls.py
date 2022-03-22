from django.urls import path, include

from ddm.views import (
    DataUpload, ProjectEntry, QuestionnaireDisplay, ProjectExit
)


participation_patterns = [
    path(r'intro/', ProjectEntry.as_view(), name='project-entry'),
    path(r'data-donation/', DataUpload.as_view(), name='data-donation'),
    path(r'questionnaire/', QuestionnaireDisplay.as_view(), name='questionnaire'),
    path(r'end/', ProjectExit.as_view(), name='project-exit')
]

urlpatterns = [
    path(r'<slug:slug>/', include(participation_patterns))
]
