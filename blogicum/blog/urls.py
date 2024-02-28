from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views

static_img = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'blog'

post_urls = [
    path('<int:post_id>/', views.detail,
         name='post_detail'),
    path('<int:post_id>/comment', views.create_comment,
         name='comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>',
         views.delete_comment,
         name='delete_comment'),
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/edit/', views.edit_post,
         name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post,
         name='delete_post'),
]

urlpatterns = [path('', views.homepage, name='homepage'),
               path('posts/', include(post_urls)),
               path('category/<slug:category_slug>/', views.category,
                    name='category_posts'),
               path('profile/<str:username>/', views.profile_view,
                    name='profile'),
               path('edit_profile/', views.edit_profile,
                    name='edit_profile')] + static_img
