from django.contrib import admin
from .models import *
# Register your models here.



class AdditionaluserinfoAdmin(admin.ModelAdmin):
    list_display = ('user','auth','name','additional_email','last_login')



admin.site.register(AdditionalUserInfo, AdditionaluserinfoAdmin)
admin.site.register(Startup)
admin.site.register(SupportBusiness)
admin.site.register(Filter)
admin.site.register(Tag)
admin.site.register(WatchPathHistory)
admin.site.register(FavPathLog)
admin.site.register(HitPathLog)
