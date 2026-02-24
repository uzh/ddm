from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ddm_auth/login.html'), name='ddm_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    urlpatterns += debug_toolbar_urls()