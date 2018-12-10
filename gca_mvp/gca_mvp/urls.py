from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404, handler500
from supporting_business import views as sp_views

urlpatterns = [
                  url('admin/', include(admin.site.urls)),

                  url(r'^', include('supporting_business.urls')),

                  # url(r'^login/$', login, name='login', kwargs={'template_name': 'accounts/login.html'}),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = sp_views.error_404
handler500 = sp_views.error_500