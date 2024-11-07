from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='ddm-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='ddm-logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # path('__debug__/', include('debug_toolbar.urls')),  # Added for debugging purposes
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
