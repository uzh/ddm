from django.urls import path

from ddm.participation import views


app_name = 'ddm_participation'
urlpatterns = [
    path(r'', views.participation_redirect_view, name='redirect'),
    path(r'briefing/', views.BriefingView.as_view(), name='briefing'),
    path(r'data-donation/', views.DataDonationView.as_view(), name='datadonation'),
    path(r'questionnaire/', views.QuestionnaireView.as_view(), name='questionnaire'),
    path(r'debriefing/', views.DebriefingView.as_view(), name='debriefing'),
    path(r'continue/', views.ContinuationView.as_view(), name='continuation'),
    path(r'inactive/', views.ProjectInactiveView.as_view(), name='project_inactive')
]
