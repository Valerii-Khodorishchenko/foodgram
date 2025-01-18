from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from recipe.apps import custom_admin_site


urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
