"""Integrate with admin module."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Review, Refer
from django.utils.html import mark_safe


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("email", "password", "profile_pic")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Access level",
            {"fields": ("is_staff_member", "is_organization", "is_endorser")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "email",
        "refer_id",
        "first_name",
        "last_name",
        "is_staff",
        "access_level",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    def access_level(self, obj):
        string = ""
        if obj.is_organization:
            string += f'<span class="badge  badge-pill  badge-success mx-1">Organization</span>'
        if obj.is_endorser:
            string += f'<span class="badge  badge-pill badge-dark mx-1" style="background-color:#c4380a">Endorser</span>'
        if obj.is_staff_member:
            string += f'<span class="badge  badge-pill text-white mx-1" style="background-color:#6726ff">Staff member</span>'

        return mark_safe(string)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ["star", "created_for", "created_by", "created_at"]
    model = Review


class ReferAdmin(admin.ModelAdmin):
    list_display = ["user_joined", "invited_by", "points", "register_at"]
    model = Refer


admin.site.register(Review, ReviewAdmin)
admin.site.register(Refer, ReferAdmin)
