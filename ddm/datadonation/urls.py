from django.urls import path, include

from ddm.datadonation import views


instruction_patterns = (
    [
        path(
            r'',
            views.InstructionOverview.as_view(),
            name='overview'
        ),
        path(
            r'create/',
            views.InstructionCreate.as_view(),
            name='create'
        ),
        path(
            r'<int:pk>/edit/',
            views.InstructionEdit.as_view(),
            name='edit'
        ),
        path(
            r'<int:pk>/delete/',
            views.InstructionDelete.as_view(),
            name='delete'
        ),
    ],
    'instructions'
)

blueprint_patterns = (
    [
        path(
            r'create/',
            views.BlueprintCreate.as_view(),
            name='create'
        ),
        path(
            r'<int:pk>/edit/',
            views.BlueprintEdit.as_view(),
            name='edit'
        ),
        path(
            r'<int:pk>/delete/',
            views.BlueprintDelete.as_view(),
            name='delete'
        ),
    ],
    'blueprints'
)

uploader_patterns = (
    [
        path(
            r'create/',
            views.FileUploaderCreate.as_view(),
            name='create'
        ),
        path(
            r'<int:pk>/edit/',
            views.FileUploaderEdit.as_view(),
            name='edit'
        ),
        path(
            r'<int:pk>/delete/',
            views.FileUploaderDelete.as_view(),
            name='delete'
        ),
    ],
    'uploaders'
)

app_name = 'ddm_datadonation'
urlpatterns = [
    path(
        r'',
        views.DataDonationOverview.as_view(),
        name='overview'
    ),
    path(
        r'blueprint/',
        include(blueprint_patterns)
    ),
    path(
        r'file-uploader/',
        include(uploader_patterns)
    ),
    path(
        r'file-uploader/<int:file_uploader_pk>/instructions/',
        include(instruction_patterns)
    ),
    path(
        'download/<slug:participant_id>',
        views.DonationDownloadView.as_view(),
        name='download_donation'
    )
]
