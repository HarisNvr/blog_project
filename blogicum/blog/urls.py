from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('posts/<int:post_id>/', views.detail, name='post_detail'),
    path('posts/<int:post_id>/comment', views.add_comment,
         name='comment'),
    path('create_post/', views.posting, name='create_post'),
    path('posts/<int:pk>/edit', views.posting,
         name='edit_post'),
    path('posts/<int:pk>/delete', views.delete_post,
         name='delete_post'),
    path('category/<slug:category_slug>/', views.category,
         name='category_posts'),
    path('accounts/profile/<str:username>/', views.profile,
         name='profile'),
    path('edit_profile/<str:username>/', views.edit_profile,
         name='edit_profile'),
]
