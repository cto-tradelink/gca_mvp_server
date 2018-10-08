from django.contrib import admin
from .models import *


class AdditionalUserInfoAdmin(admin.ModelAdmin):
    list_display = ('get_user_id','auth','get_user_mng_name',)


class ClipAdmin(admin.ModelAdmin):
    list_display = ('get_clip_title','get_author','get_created_date',)


class SupportBusinessAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_author')

# Register your models here.

admin.site.register(Startup)
admin.site.register(SupportBusiness,SupportBusinessAdmin )

admin.site.register(HitPathLog)
admin.site.register(AdditionalUserInfo, AdditionalUserInfoAdmin)
admin.site.register(Clip)
admin.site.register(Course)
admin.site.register(Path)
