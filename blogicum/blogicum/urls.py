from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages'))
]
