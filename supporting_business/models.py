

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from datetime import date
import datetime


class FavoriteLog(models.Model):
    user = models.ForeignKey("AdditionalUserInfo")
    support_business = models.ForeignKey("SupportBusiness", blank=True, null=True)
    startup =models.ForeignKey("Startup", blank=True, null=True)
    clip =models.ForeignKey("Clip", blank=True, null=True)
    course =models.ForeignKey("Course", blank=True, null=True)
    path =models.ForeignKey("Path", blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    up_down = models.IntegerField(max_length=1)


class AdditionalUserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    auth = models.CharField(max_length=10, blank=True, null=True, default="")
    is_superuser = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='uploads/user/avatar', null=True, blank=True, default="")
    own_startup = models.OneToOneField("Startup", blank=True, null=True, default="" , related_name="own_startup")
    agreement = models.BooleanField(default=True)
    repre_name = models.CharField(max_length=30, blank=True, null=True, default="")
    repre_tel = models.CharField(max_length=30, blank=True, null=True, default="")
    repre_email = models.CharField(max_length=100, default="", blank=True, null=True, )
    mng_name = models.CharField(max_length=30, blank=True, null=True, default="")
    mng_tel = models.CharField(max_length=100, default="", blank=True, null=True, )
    mng_phone = models.CharField(max_length=100, default="", blank=True, null=True, )
    mng_email = models.CharField(max_length=100, default="", blank=True, null=True, )
    mng_position = models.CharField(max_length=20, blank=True, null=True, default="")
    mng_bonbu = models.CharField(max_length=20, blank=True, null=True)
    mng_kikwan = models.CharField(max_length=20, blank=True, null=True)
    mng_team = models.CharField(max_length=20, blank=True, null=True)
    # mng_department = models.CharField(max_length=30, blank=True, null=True, default="")
    # mng_belong_to = models.CharField(max_length=30, blank=True, null=True, default="")
    mng_boss = models.ForeignKey("AdditionalUserInfo", blank=True, null=True)
    mng_date_joined_ymd = models.DateTimeField(auto_now_add=True)
    mng_website = models.CharField(max_length=100, blank=True, null=True)
    favorite = models.ManyToManyField("SupportBusiness", blank=True, null=True)
    favorite_startup = models.ManyToManyField("Startup", blank=True, null=True)
    favorite_clip = models.ManyToManyField("Clip", blank=True, null=True)
    favorite_course = models.ManyToManyField("Course", blank=True, null=True)
    favorite_path = models.ManyToManyField("Path", blank=True, null=True)
    sns = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=1, blank=True, null=True)
    twitter = models.CharField(max_length=1, blank=True, null=True)
    class Meta:
        verbose_name="회원 관리"
        verbose_name_plural="회원 관리"
    def __str__(self):
        return self.user.username

    def get_user_id(self):
        return self.user.username
    def get_user_mng_name(self):
        print(self.mng_name)
        if self.mng_name !="" or self.mng_name != None :
            return self.mng_name
        else:
            print(self.user.startup.repre_name)
            return self.user.startup.repre_name
    def last_login(self):
        return self.user.last_login
    def account_stage(self):
        depth = self.get_depth()
        if depth == 0 :
            return '경영진'
        elif depth == 1:
            return '최고 관리자'
        elif depth == 2:
            return '기관장'
        elif depth == 3:
            return '실무 매니저'




    def has_boss(self):
        if self.boss is not None:
            return True
        else:
            return False

    def get_depth(self):
        dep = 0
        target = self
        while target.has_boss():
            dep = dep+1
            target = target.boss

        return dep

    def has_child(self):
        if len(self.additionaluserinfo_set.all()) == 0:
            return False
        else:
            return True

    def child_list(self):
        result_set = []
        if len(self.additionaluserinfo_set.all()) == 0:
            if len(result_set) != 0 :
                pass
            else:
                result_set.append(self)
        else:
            for r in self.additionaluserinfo_set.all():
                result_set.extend(r.child_list())
        return result_set

    def get_child_stage(self):
        print("hererer")
        depth = self.get_depth()-1
        if depth == -1:
            return '최고 관리자'
        elif depth == 0:
            return '기관장'
        elif depth == 1:
            return '실무 매니저'
        else :
            return ''


# 기업 정보에 대한 데이터베이스 항목
class Startup(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    company_name = models.CharField(max_length=100, blank=True, null=True, )
    company_intro = models.TextField(blank=True, null=True, default="")
    established_date = models.DateField(blank=True, null=True, )
    logo = models.CharField(max_length=1000, blank=True, null=True) #파일
    back_img = models.CharField(max_length=1000, blank=True, null=True)#파일
    company_short_desc = models.CharField(max_length=1000, blank=True, null=True)
    company_intro = models.CharField(max_length=1000, blank=True, null=True)
    company_youtube = models.CharField(max_length=300, blank=True, null=True, default="")
    company_facebook = models.CharField(max_length=300, blank=True, null=True, default="")
    company_instagram = models.CharField(max_length=300, blank=True, null=True, default="")
    company_website = models.CharField(max_length=300, default="", blank=True, null=True, )
    address_0 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_1 = models.CharField(max_length=400, default="", blank=True, null=True, )
    repre_name = models.CharField(max_length=100, default="", blank=True, null=True, )
    repre_email = models.CharField(max_length=100, default="", blank=True, null=True, )
    repre_tel = models.CharField(max_length=100, default="", blank=True, null=True, )
    mark_name = models.CharField(max_length=100, default="", blank=True, null=True, )
    mark_email = models.CharField(max_length=100, default="", blank=True, null=True, )
    mark_tel = models.CharField(max_length=100, default="", blank=True, null=True, )
    selected_company_filter_list = models.ManyToManyField("SupportBusinessFilter", blank=True, null=True, db_table='company_filter_with_startup'  )
    company_keyword =  models.CharField(max_length=300, default="", blank=True, null=True, )
    company_total_employee  =  models.CharField(max_length=20, blank=True, null=True, default="")
    company_hold_employee =  models.CharField(max_length=20, blank=True, null=True, default="")
    company_assurance_employee  = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    ip_chk =models.BooleanField(default=True)
    revenue_chk = models.BooleanField(default=True)
    export_chk = models.BooleanField(default=True)
    company_invest_chk = models.BooleanField(default=True)
    company_kind = models.CharField(max_length=10, blank=True, null=True)
    attached_ip_file = models.CharField(max_length=500, null=True, blank=True)  # 파일
    attached_ir_file= models.CharField(max_length=500, null=True, blank=True)#파일
    attached_cert_file = models.CharField(max_length=500, null=True, blank=True)#파일
    attached_tax_file = models.CharField(max_length=500, null=True, blank=True)#파일
    attached_fund_file = models.CharField(max_length=500, null=True, blank=True)#파일
    attached_ppt_file = models.CharField(max_length=500, null=True, blank=True)#파일
    attached_etc_file = models.CharField(max_length=500, null=True, blank=True)#파일
    #tag_string = models.CharField(max_length=1000, blank=True, null=True)
    field_list = []
    present_obj = {}
    class Meta:
        verbose_name="스타트업 관리"
        verbose_name_plural="스타트업 관리"

    def __init__(self, *args, **kwargs):
        super(Startup, self).__init__( *args, **kwargs)
        data = Startup._meta.get_fields()
        for da in data:
            try:
                if not da.related_model:
                    self.field_list.append(da.name)
                    self.present_obj[da.name] = getattr(self, da.name)
            except Exception as e:
                print(e)
                pass
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        changed_set = {}
        for field in self.field_list:
            try:
                if getattr(self, field) != self.present_obj[field] :
                    changed_set[field] = getattr(self, field)
            except Exception as e:
                print(e)
                pass
        super(Startup, self).save(force_insert, force_update, *args, **kwargs)
        try:
            for field in self.field_list:
                setattr(self, field, getattr(self, field) )
        except Exception as e:
            print(e)
            pass
        return changed_set


class Service(models.Model):
    startup = models.ForeignKey(Startup)
    service_img = models.CharField(max_length=300, null=True, blank=True, default="")#파일
    service_intro = models.TextField()
    service_file = models.CharField(max_length=300, null=True, blank=True, default="")#파일
    service_name = models.CharField(max_length=200, blank=True, null=True)
    field_list = []
    present_obj = {}
    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        data = Service._meta.get_fields()
        for da in data:
            try:
                if not da.related_model:
                    self.field_list.append(da.name)
                    self.present_obj[da.name] = getattr(self, da.name)
            except Exception as e:
                print(e)
                pass
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        changed_set = {}
        for field in self.field_list:
            try:
                if getattr(self, field) != self.present_obj[field]:
                    changed_set[field] = getattr(self, field)
            except Exception as e:
                print(e)
                pass
        super(Service, self).save(force_insert, force_update, *args, **kwargs)
        try:
            for field in self.field_list:
                setattr(self, field, getattr(self, field))
        except Exception as e:
            print(e)
            pass
        return changed_set


class CompanyInvest(models.Model):
    startup = models.ForeignKey(Startup)
    company_invest_year = models.DateField(max_length=5, blank=True, null=True)
    company_invest_size = models.CharField(max_length=10, blank=True, null=True)
    company_invest_agency = models.CharField(max_length=100, blank=True, null=True)
    field_list = []
    present_obj = {}
    def __init__(self, *args, **kwargs):
        super(CompanyInvest, self).__init__(*args, **kwargs)
        data = CompanyInvest._meta.get_fields()
        for da in data:
            try:
                if not da.related_model:
                    self.field_list.append(da.name)
                    self.present_obj[da.name] = getattr(self, da.name)
            except Exception as e:
                print(e)
                pass
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        changed_set = {}
        for field in self.field_list:
            try:
                if getattr(self, field) != self.present_obj[field]:
                    changed_set[field] = getattr(self, field)
            except Exception as e:
                print(e)
                pass
        super(CompanyInvest, self).save(force_insert, force_update, *args, **kwargs)
        try:
            for field in self.field_list:
                setattr(self, field, getattr(self, field))
        except Exception as e:
            print(e)
            pass
        return changed_set
class Activity(models.Model):
    startup = models.ForeignKey(Startup)
    company_activity_created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    company_activity_text = models.TextField(max_length=1000)
    company_activity_img = models.CharField(max_length=300, blank=True, null=True)#파일
    company_activity_youtube = models.CharField(max_length=300, blank=True, null=True)
    field_list = []
    present_obj = {}
    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)
        data = Activity._meta.get_fields()
        for da in data:
            try:
                if not da.related_model:
                    self.field_list.append(da.name)
                    self.present_obj[da.name] = getattr(self, da.name)
            except Exception as e:
                print(e)
                pass
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        changed_set = {}
        for field in self.field_list:
            try:
                if getattr(self, field) != self.present_obj[field]:
                    changed_set[field] = getattr(self, field)
            except Exception as e:
                print(e)
                pass
        super(Activity, self).save(force_insert, force_update, *args, **kwargs)
        try:
            for field in self.field_list:
                setattr(self, field, getattr(self, field))
        except Exception as e:
            print(e)
            pass
        return changed_set

class ActivityLike(models.Model):
    activity = models.ForeignKey(Activity)
    company_activity_user = models.ForeignKey(AdditionalUserInfo)
    company_activity_like_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class Reply(models.Model):
    activity = models.ForeignKey(Activity)
    company_activity_text = models.TextField()
    company_activity_author = models.ForeignKey(Startup)
    company_activity_created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class History(models.Model):
    startup = models.ForeignKey(Startup)
    company_history_year = models.CharField(max_length=10, blank=True, null=True)
    company_history_month = models.CharField(max_length=2, blank=True, null= True)
    company_history_content = models.TextField()
    field_list = []
    present_obj = {}
    def __init__(self, *args, **kwargs):
        super(History, self).__init__(*args, **kwargs)
        data = History._meta.get_fields()
        for da in data:
            try:
                if not da.related_model:
                    self.field_list.append(da.name)
                    self.present_obj[da.name] = getattr(self, da.name)
            except Exception as e:
                print(e)
                pass
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        changed_set = {}
        for field in self.field_list:
            try:
                if getattr(self, field) != self.present_obj[field]:
                    changed_set[field] = getattr(self, field)
            except Exception as e:
                print(e)
                pass
        super(History, self).save(force_insert, force_update, *args, **kwargs)
        try:
            for field in self.field_list:
                setattr(self, field, getattr(self, field))
        except Exception as e:
            print(e)
            pass
        return changed_set

class SupportBusinessFilter(models.Model):
    cat_0 = models.CharField(max_length=100)
    cat_1 = models.CharField(max_length=100, blank=True, null=True)
    filter_name = models.CharField(max_length=100)

#
# class IntellectualProperty(models.Model):
#     startup = models.ForeignKey("Startup")
#     ip_file = models.CharField(max_length=200, blank=True, null=True)#파일
#     name = models.CharField(max_length=200, blank=True, null=True)

#공고문
class SupportBusiness(models.Model):
    support_business_author = models.ForeignKey("AdditionalUserInfo", blank=True, null=True)
    selected_support_business_filter_list = models.ManyToManyField("SupportBusinessFilter", db_table='company_filter_with_supportbusiness')
    support_business_created_at_ymdt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    support_business_name = models.CharField(max_length=300, blank=True, null=True, default="")
    support_business_name_tag = models.CharField(max_length=300, blank=True, null=True, default="")
    support_business_name_sub = models.CharField(max_length=300, blank=True, null=True, default="")
    support_business_poster = models.CharField(max_length=1000, blank=True, null=True)#파일
    support_business_relate_support_business=models.ForeignKey("SupportBusiness",blank=True, null=True)
    support_business_short_desc = models.CharField(max_length=200, blank=True, null=True, default="")
    support_business_subject = models.TextField(blank=True, null=True, )
    support_business_detail = models.TextField(blank=True, null=True, )
    support_business_apply_start_ymd = models.DateTimeField(blank=True, null=True, )
    support_business_apply_end_ymdt = models.DateTimeField(blank=True, null=True, )
    support_business_object = models.TextField(blank=True, null=True, default="")
    support_business_recruit_size = models.CharField(max_length=30, blank=True, null=True, default="")
    support_business_employee_condition = models.IntegerField(blank=True, null=True, default=0)
    support_business_prefer = models.TextField(blank=True, null=True, default="")
    support_business_constraint = models.TextField(blank=True, null=True, default="")
    support_business_choose_method = models.TextField(blank=True, null=True, default="")
    support_business_pro_0_choose = models.TextField(blank=True, null=True, default="")
    support_business_pro_0_start_ymd = models.DateField(blank=True, null=True)
    support_business_pro_0_end_ymd = models.DateField(blank=True, null=True)
    support_business_pro_0_open_ymd = models.DateField(blank=True, null=True)
    support_business_pro_0_criterion = models.TextField(blank=True, null=True, default="")
    support_business_pro_1_choose = models.TextField(blank=True, null=True, default="")
    support_business_pro_1_start_ymd = models.DateField(blank=True, null=True)
    support_business_pro_1_end_ymd = models.DateField(blank=True, null=True)
    support_business_pro_1_open_ymd = models.DateField(blank=True, null=True)
    support_business_pro_1_criterion = models.TextField(blank=True, null=True, default="")
    support_business_pro_1_check = models.BooleanField(default=False )
    support_business_pro_2_choose = models.TextField(blank=True, null=True, default="")
    support_business_pro_2_start_ymd = models.DateField(blank=True, null=True)
    support_business_pro_2_end_ymd = models.DateField(blank=True, null=True)
    support_business_pro_2_open_ymd = models.DateField(blank=True, null=True)
    support_business_pro_2_criterion = models.TextField(blank=True, null=True, default="")
    support_business_pro_2_check = models.BooleanField(default=False )

    support_business_supply_content = models.TextField(blank=True, null=True, default="")


    mng_support_business_step_6_etc_input = models.TextField()
    support_business_ceremony_start_ymd = models.DateField(blank=True, null=True)
    support_business_ceremony_end_ymd = models.DateField(blank=True, null=True)
    support_business_faq = models.TextField(blank=True, null=True, default="")
    support_business_additional_faq = models.TextField(blank=True, null=True, default="")

    mng_support_business_step_6_etc_input_chk = models.BooleanField(default=False)
    support_business_ceremony_chk = models.BooleanField(default=False)
    support_business_faq_chk = models.BooleanField(default=False)
    support_business_additional_faq_chk = models.BooleanField(default=False)
    support_business_etc_input_chk=models.CharField(blank=True, null=True, max_length=100)



    support_business_meta = models.CharField(max_length=1000, blank=True, null=True, default="")

    support_business_update_at_ymdt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    support_business_hit = models.IntegerField(default=0)
    support_business_complete = models.BooleanField(default=False)
    support_business_award_date_ymd = models.DateField(blank=True, null=True)
    support_business_meta_0=models.CharField(blank=True, null=True, max_length=100)
    mng_support_business_step_3_etc_input_mojipjogun = models.CharField(max_length=100, blank=True, null=True)
    mng_support_business_step_3_etc_input_mojipgenre = models.CharField(max_length=100, blank=True, null=True)
    mng_support_business_step_3_etc_input_mojipjogun_chk = models.BooleanField(default=False)
    mng_support_business_step_3_etc_input_mojipgenre_chk = models.BooleanField(default=False)

    support_business_status = models.CharField(max_length=10, blank=True, null=True)
    support_business_prefer_chk = models.BooleanField(default=False)
    support_business_constraint_chk = models.BooleanField(default=False)#파일
    support_business_etc_file_title_mng = models.CharField(max_length=1000, blank=True, null=True, default="")
    support_business_appliance_form = models.CharField(max_length=100, blank=True, null=True, default="")
    support_business_poster_data_url = models.TextField( blank=True, null=True, default="")
    support_business_raw_filter_text = models.CharField(max_length=3000, null=True, default="", blank=True)
    class Meta:
        verbose_name="지원사업 관리"
        verbose_name_plural="지원사업 관리"
    def __str__(self):
        return self.support_business_name

    def get_author(self):
        return self.support_business_author

    def get_name(self):
        return self.support_business_name


class SupportBusinessAttachedFiles(models.Model):
    support_business = models.ForeignKey("SupportBusiness")
    file_path = models.CharField(max_length=500, blank=True, null=True)

#지원서
class Appliance(models.Model):
    support_business = models.ForeignKey(SupportBusiness, blank=True, null=True) #
    startup = models.ForeignKey(Startup, blank=True, null=True)#
    company_name = models.CharField(max_length=100, blank=True, null=True, default="")#
    established_date = models.DateField(blank=True, null=True)#
    address_0 = models.CharField(max_length=400, blank=True, null=True, default="")#
    address_1 = models.CharField(max_length=400, blank=True, null=True, default="")#
    repre_name = models.CharField(max_length=100, blank=True, null=True, default="")#
    repre_tel = models.CharField(max_length=100, blank=True, null=True, default="")#
    repre_email = models.CharField(max_length=100, blank=True, null=True, default="")#
    mark_name = models.CharField(max_length=100, blank=True, null=True, default="")#
    mark_tel = models.CharField(max_length=100, blank=True, null=True, default="")#
    mark_email = models.CharField(max_length=100, blank=True, null=True, default="")#
    company_keyword = models.CharField(max_length=1000, blank=True, null=True, default="")
    company_total_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    company_hold_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    company_assurance_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    selected_company_filter_list = models.ManyToManyField("SupportBusinessFilter" , db_table='company_filter_with_appliance' )
    company_intro = models.TextField()
    raw_filter_list = models.CharField(max_length=3000, blank=True, null=True)
    revenue_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    company_kind = models.CharField(max_length=10, blank=True, null=True)
    company_website = models.CharField(max_length=100, blank=True, null=True)#
    attached_ppt_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_cert_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_ir_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_tax_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_fund_file =  models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_ip_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_etc_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    etc_file_title_by_mng = models.TextField(blank=True, null=True)
    company_instagram = models.CharField(max_length=200, blank=True, null=True, default="")#
    company_youtube = models.CharField(max_length=300, blank=True, null=True, default="")#
    company_facebook = models.CharField(max_length=300, blank=True, null=True, default="")#
    appliance_created_at_ymdt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    appliance_update_at_ymdt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_submit = models.BooleanField(default=False)
    img_data_url = models.TextField()
    is_applied_to_company_info = models.BooleanField(default=False)
    class meta:
        get_latest_by = "updated_at"


class ApplianceInvest(models.Model):
    applicance = models.ForeignKey("Appliance")
    company_invest_year = models.DateField(max_length=5, blank=True, null=True)
    company_invest_size = models.CharField(max_length=10, blank=True, null=True)
    company_invest_agency = models.CharField(max_length=100, blank=True, null=True)
class ApplianceHistory(models.Model):
    appliance = models.ForeignKey("Appliance")
    company_history_year = models.CharField(max_length=10, blank=True, null=True)
    company_history_month = models.CharField(max_length=2, blank=True, null= True)
    company_history_content = models.TextField()


#선정자
class Award(models.Model):
    support_business = models.ForeignKey(SupportBusiness)
    startup = models.ForeignKey(Startup)
    award_update_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Alarm(models.Model):
    user = models.ForeignKey(AdditionalUserInfo)
    alarm_content = models.CharField(max_length=500, blank=True, null=True)
    alarm_origin_support_business = models.ForeignKey(SupportBusiness, blank=True, null=True)
    alarm_origin_st = models.ForeignKey(Startup, blank=True, null=True)
    alarm_category = models.CharField(max_length=2, blank=True, null=True)
    alarm_read = models.BooleanField(default=False)
    alarm_created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    alarm_detail_content = models.TextField(blank=True, null=True)
    alarm_startup_url = models.CharField(max_length=100, blank=True, null=True)

# class DayUser(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)
#
#
# class NewUser(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)
#
#
# class Session(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)


class ApplianceService(models.Model):
    startup = models.ForeignKey(Startup)
    appliance = models.ForeignKey(Appliance)
    service_name = models.CharField(max_length=300, blank=True, null=True)
    service_intro = models.TextField()
    service_img = models.CharField(max_length=300, null=True, blank=True, default="")  # 파일
    service_file = models.CharField(max_length=300, null=True, blank=True, default="")  # 파일

#
# class SessionPerUser(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)
#
#
# class PageView(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)
#
#
# class PagePerSession(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)
#
#
#
# class ExpireTime(models.Model):
#     count = models.IntegerField(default=0, blank=None, null=None)


class EmailConfirmation(models.Model):
    email = models.CharField(max_length=300)
    confirmation_code = models.CharField(max_length=300)
    confirm = models.BooleanField(default=False)
    
class HitLog(models.Model):
    support_business = models.ForeignKey(SupportBusiness)
    user = models.ForeignKey("AdditionalUserInfo", blank=True, null=True )
    date = models.DateField(auto_now_add=True)


class EduFilter(models.Model):
    name= models.CharField(max_length=100, blank=True, null=True)


class Clip(models.Model):
    clip_user = models.ForeignKey(AdditionalUserInfo)
    clip_title = models.CharField(max_length=200, null=True, blank=True)
    clip_youtube = models.CharField(max_length=100, null=True, blank=True)
    clip_mov_url = models.CharField(max_length=200, null=True, blank=True)
    clip_thumb = models.CharField(max_length=400, null=True, blank=True)
    clip_filter = models.ManyToManyField(EduFilter)
    clip_object = models.CharField(max_length=300, blank=True, null=True)
    clip_info = models.TextField()
    clip_play = models.IntegerField(blank=True, null=True)
    clip_created_at = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.clip_title

    def get_title(self):
        if self.clip_title == None or self.clip_title == "":
            return "제목이 없습니다."
        else:
            return self.clip_title

    def get_author(self):
        try:
            return self.clip_user.user.startup.repre_name
        except:
            return self.clip_user.mng_name
    def get_created_date(self):
        return self.clip_created_at


class Course(models.Model):
    course_user = models.ForeignKey(AdditionalUserInfo)
    course_title = models.CharField(max_length=200, null=True, blank=True)
    course_filter = models.ManyToManyField(EduFilter, blank=True, null=True)
    course_thumb = models.CharField(max_length=400, null=True, blank=True)
    course_rec_dur = models.CharField(max_length=300, blank=True, null=True)
    course_object = models.CharField(max_length=300, blank=True, null=True)
    course_info = models.TextField()
    course_clips = models.ManyToManyField(Clip)
    course_total_play = models.IntegerField( blank=True, null=True)
    course_created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return self.course_title


class Path(models.Model):
    path_user = models.ForeignKey(AdditionalUserInfo)
    path_title = models.CharField(max_length=200, null=True, blank=True)
    path_filter = models.ManyToManyField(EduFilter, blank=True, null=True)
    path_thumb = models.CharField(max_length=400, null=True, blank=True)
    path_rec_dur = models.CharField(max_length=300, blank=True, null=True)
    path_object = models.CharField(max_length=300, blank=True, null=True)
    path_info = models.TextField()
    path_course = models.ManyToManyField(Course)
    path_total_play = models.IntegerField( blank=True, null=True)
    path_created_at = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.path_title

class HitClipLog(models.Model):
    hit_clip = models.ForeignKey(Clip)
    hit_clip_user = models.ForeignKey(AdditionalUserInfo, blank=True, null=True)
    hit_clip_date = models.DateField(auto_now_add=True)


class HitCourseLog(models.Model):
    hit_course = models.ForeignKey(Course)
    hit_course_clip = models.ForeignKey(Clip)
    hit_course_user = models.ForeignKey(AdditionalUserInfo)
    hit_course_date = models.DateField(auto_now_add=True)

class HitPathLog(models.Model):
    hit_path = models.ForeignKey(Path)
    hit_path_clip = models.ForeignKey(Clip)
    hit_path_course = models.ForeignKey(Course)
    hit_path_user = models.ForeignKey(AdditionalUserInfo)
    hit_path_date = models.DateField(auto_now_add=True)


class  WatchHistory(models.Model):
    watch_path = models.ForeignKey(Path, null=True, blank=True)
    watch_course = models.ForeignKey(Course, null=True, blank=True)
    watch_clip = models.ForeignKey(Clip, null=True, blank=True)
    watch_user = models.ForeignKey(AdditionalUserInfo)
    watch_date = models.DateField(auto_now_add=True)



class CompletedClip(models.Model):
    complete_clip = models.ForeignKey(Clip)
    complete_user = models.ForeignKey(AdditionalUserInfo)
    complete_date = models.DateField(auto_now_add=True)
class CompletedCourse(models.Model):
    complete_course = models.ForeignKey(Course)
    complete_user = models.ForeignKey(AdditionalUserInfo)
    complete_date = models.DateField(auto_now_add=True)
class CompletedPath(models.Model):
    complete_path = models.ForeignKey(Path)
    complete_user = models.ForeignKey(AdditionalUserInfo)
    complete_date = models.DateField(auto_now_add=True)






class ApplianceSnapShot(models.Model):
    support_business = models.ForeignKey(SupportBusiness, blank=True, null=True)
    startup = models.ForeignKey(Startup, blank=True, null=True)
    companay_name = models.CharField(max_length=100, blank=True, null=True, default="")
    established_date = models.DateField(blank=True, null=True)
    address_0 = models.CharField(max_length=400, blank=True, null=True, default="")
    address_1 = models.CharField(max_length=400, blank=True, null=True, default="")
    repre_name = models.CharField(max_length=100, blank=True, null=True, default="")
    repre_tel = models.CharField(max_length=100, blank=True, null=True, default="")
    repre_email = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_name = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_tel = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_email = models.CharField(max_length=100, blank=True, null=True, default="")
    company_keyword = models.CharField(max_length=1000, blank=True, null=True, default="")
    company_total_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    company_hold_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    company_assurance_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    selected_company_filter_list = models.ManyToManyField("SupportBusinessFilter",db_table='company_filter_with_appliance_snapshot')
    company_intro = models.TextField()
    raw_filter_list = models.CharField(max_length=3000, blank=True, null=True)
    revenue_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    revenue_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    revenue_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")

    export_before_year_0 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_1 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_year_2 = models.CharField(max_length=5, blank=True, null=True, default="")
    export_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    export_before_nation_2 = models.CharField(max_length=20, blank=True, null=True, default="")

    company_kind = models.CharField(max_length=10, blank=True, null=True)
    company_keyword = models.CharField(max_length=1000, blank=True, null=True)
    company_website = models.CharField(max_length=100, blank=True, null=True)
    company_intro = models.TextField(blank=True, null=True, default="")

    attached_ppt_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_cert_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_ir_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_tax_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_fund_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_ip_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    attached_etc_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    etc_file_title_by_mng = models.TextField(blank=True, null=True)
    company_instagram = models.CharField(max_length=200, blank=True, null=True)
    company_youtube = models.CharField(max_length=300, blank=True, null=True)
    company_facebook = models.CharField(max_length=300, blank=True, null=True)
    appliance_created_at_ymdt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    appliance_update_at_ymdt = models.DateField(auto_now_add=True, blank=True, null=True)
    is_submit = models.BooleanField(default=False)





class StatTable(models.Model):
    stat_user =  models.ForeignKey("AdditionalUserInfo")
    stat_name =  models.CharField(max_length=32, null=True,blank=True)
    stat_json = models.TextField()
    stat_timestamp = models.DateTimeField(auto_now_add=True)

class RegisteredChannel(models.Model):
    clip = models.ForeignKey("Clip", null=True, blank=True)
    course = models.ForeignKey("Course", null=True, blank=True)
    path = models.ForeignKey("Path", null=True, blank=True)
    channel_user= models.ForeignKey("AdditionalUserInfo")
    date = models.DateField(auto_now_add=True)




class VisitedSupportBusiness(models.Model):
    visited_timestamp = models.DateField(auto_now_add=True)
    visited_support_business = models.ForeignKey("SupportBusiness")
    visited_usr = models.ForeignKey("AdditionalUserInfo", null=True, blank=True)
    visited_usr_filter = models.ManyToManyField("FilterForStatics")

class FavoredSupportBusiness(models.Model):
    favored_support_business = models.ForeignKey("SupportBusiness")
    favored_usr = models.ForeignKey("AdditionalUserInfo")
    favored_timestamp = models.DateField(auto_now_add=True)
    favored_usr_filter = models.ManyToManyField("FilterForStatics")

class SupportBusinessApplicant(models.Model):
    applicant_timestamp = models.DateField(auto_now_add=True)
    applicant_support_business = models.ForeignKey("SupportBusiness")
    applicant_usr = models.ForeignKey("AdditionalUserInfo")
    applicant_usr_filter = models.ManyToManyField("FilterForStatics")

class SupportBusinessAwarded(models.Model):
    awarded_timestamp = models.DateField(auto_now_add=True)
    awarded_support_business = models.ForeignKey("SupportBusiness")
    awarded_usr = models.ForeignKey("AdditionalUserInfo")
    awarded_usr_filter = models.ManyToManyField("FilterForStatics")



class LineGraphTable(models.Model):
    linegraph_support_business = models.ForeignKey("SupportBusiness")
    linegraph_date = models.DateField(auto_now_add=True)
    linegraph_visitied = models.IntegerField(default=0)
    linegraph_favored = models.IntegerField(default=0)
    linegraph_applicant = models.IntegerField(default=0)
    linegraph_user_id_list = models.CharField(max_length=30, blank=True, null=True)


class FilterForStatics(models.Model):
    cat_0 = models.CharField(max_length=100)
    cat_1 = models.CharField(max_length=100, blank=True, null=True)
    filter_name = models.CharField(max_length=100)


class QuaterTableSupportBusiness(models.Model):
    qt_support_business_author = models.ForeignKey(AdditionalUserInfo)
    qt_support_business = models.ForeignKey(SupportBusiness)
    qt_support_business_status = models.IntegerField()
    qt_support_business_approved_date_ymd= models.DateField(auto_now_add=True)


class CountingTable(models.Model):
    support_business = models.ForeignKey("SupportBusiness")
    date = models.DateField(null=True, blank=True)
    hit_num = models.IntegerField(default=0)
    fav_num = models.IntegerField(default=0)
    apply_num = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class CountingStartupListTable(models.Model):
    support_business = models.ForeignKey("SupportBusiness")
    all_startup_list = models.TextField( blank=True, null=True)
    hit_startup_list = models.TextField( blank=True, null=True)
    fav_startup_list = models.TextField( blank=True, null=True)
    applied_startup_list = models.TextField( blank=True, null=True)
    awarded_startup_list = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class CountingFilterListTable(models.Model):
    support_business = models.ForeignKey("SupportBusiness")
    all_filter = models.TextField( blank=True, null=True)
    hit_filter = models.TextField( blank=True, null=True)
    fav_filter = models.TextField( blank=True, null=True)
    applied_filter = models.TextField( blank=True, null=True)
    awarded_filter = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRINGCountingTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    date = models.DateField(null=True, blank=True)
    hit_num = models.IntegerField(default=0)
    fav_num = models.IntegerField(default=0)
    apply_num = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRINGCountingStartupListTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    all_startup_list = models.TextField( blank=True, null=True)
    hit_startup_list = models.TextField( blank=True, null=True)
    fav_startup_list = models.TextField( blank=True, null=True)
    applied_startup_list = models.TextField( blank=True, null=True)
    awarded_startup_list = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRINGCountingFilterListTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    all_filter = models.TextField( blank=True, null=True)
    hit_filter = models.TextField( blank=True, null=True)
    fav_filter = models.TextField( blank=True, null=True)
    applied_filter = models.TextField( blank=True, null=True)
    awarded_filter = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRENDCountingTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    date = models.DateField(null=True, blank=True)
    hit_num = models.IntegerField(default=0)
    fav_num = models.IntegerField(default=0)
    apply_num = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRENDCountingStartupListTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    all_startup_list = models.TextField( blank=True, null=True)
    hit_startup_list = models.TextField( blank=True, null=True)
    fav_startup_list = models.TextField( blank=True, null=True)
    applied_startup_list = models.TextField( blank=True, null=True)
    awarded_startup_list = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class OPRENDCountingFilterListTable(models.Model):
    opr = models.ForeignKey("AdditionalUserInfo")
    all_filter = models.TextField( blank=True, null=True)
    hit_filter = models.TextField( blank=True, null=True)
    fav_filter = models.TextField( blank=True, null=True)
    applied_filter = models.TextField( blank=True, null=True)
    awarded_filter = models.TextField( blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now())

class GATable(models.Model):
    string_data=models.TextField()

class ClipCountingTable(models.Model):
    clip = models.ForeignKey("Clip")
    string_data=models.TextField()
class CourseCountingTable(models.Model):
    course = models.ForeignKey("Course")
    string_data=models.TextField()
class PathCountingTable(models.Model):
    path = models.ForeignKey("Path")
    string_data=models.TextField()

class MainContents(models.Model):
    support_business = models.TextField(blank=True, null=True)
    clip = models.TextField(blank=True, null=True)
    course = models.TextField(blank=True, null=True)
    path =models.TextField(blank=True, null=True)

class  WriteCSRFTokens(models.Model):
    csrf_token=models.CharField(max_length=300)
    expired_at_ymdt = models.DateTimeField()