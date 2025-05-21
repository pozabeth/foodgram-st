from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import UserSubscription, User


class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "date_joined")

    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("avatar",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("first_name", "last_name", "email", "avatar")}),
    )
    empty_value_display = "-пусто-"


@admin.register(UserSubscription)
class CustomSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author", "created")
    search_fields = (
        "user__username",
        "author__username",
        "user__email",
        "author__email",
    )
    list_filter = ("created",)
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)


if admin.site.is_registered(Group):
    admin.site.unregister(Group)
admin.site.register(Group)
