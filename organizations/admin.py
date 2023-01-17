from django.contrib import admin
from .models import *
from authentication.models import User
# Register your models here.



class MemberInline(admin.TabularInline):
    model = Staff
    extra = 1
    can_delete = False
    can_add = True
    can_edit = False
    readonly_fields = fields = ('first_name', 'last_name', 'email', 'designation', 'created_at')
    # readonly_fields = fields = ("transaction_id", "Amount", "type", "source", "note", "created_at", "account_id")

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def email(self, obj):
        return obj.user.email

    def created_at(self, obj):
        return obj.created_at


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "staff_members", "created_at", "created_by"]
    inlines = [MemberInline]
    model = Organization

    def staff_members(self, obj):
        return Staff.objects.filter(organization = obj).count()


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "budget", "product", "organization", "created_at", "created_by", "is_active"]
    model = Project


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "created_at", "created_by"]
    model = ProductService




admin.site.register(SocialMedia)
admin.site.register(Location)
admin.site.register(Staff)
admin.site.register(ProductService, ProductAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)

