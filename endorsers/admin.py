from django.contrib import admin
from .models import *


class EndorserAdmin(admin.ModelAdmin):
    list_display = ["name", "followers", "created_at", "created_by"]
    model = Endorser

    def name(self, obj):
        return obj.created_by.getFullName()



# Register your models here.
admin.site.register(Endorser, EndorserAdmin)
admin.site.register(Order)
admin.site.register(Application)
admin.site.register(Approval)
admin.site.register(OrderUpdate)

