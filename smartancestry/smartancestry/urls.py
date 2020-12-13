from django.conf.urls import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/data/index')),
    url(r'^/$', RedirectView.as_view(url='/data/index')),
    url(r'^data/', include('data.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    path('admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.MEDIA_URL + 'images/favicon.ico')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
