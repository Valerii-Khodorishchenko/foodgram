from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from recipe.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('recipes/', include('recipe.urls')),
    path('s/<str:short_id>/', redirect_short_link, name='recipe-short-url')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
