from django.contrib import admin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following', )
    empty_value_display = '-пусто-'
