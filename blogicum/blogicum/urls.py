from django.contrib import admin
from django.urls import include, path
from django.conf import settings

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_failure'

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
