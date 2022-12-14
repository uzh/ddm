from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ddm/project_admin/auth/login.html'), name='ddm-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='ddm-logout')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
