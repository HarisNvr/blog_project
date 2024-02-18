from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'is_published')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_published')


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category',
                    'pub_date', 'location', 'is_published')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)



