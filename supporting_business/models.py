from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from datetime import date
import datetime

class InterestLog(models.Model):
    user = models.ForeignKey("AdditionalUserInfo")
    sb = models.ForeignKey("SupportBusiness")
    date = models.DateField()
    up_down = models.IntegerField(max_length=1)


class AdditionalUserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    auth = models.CharField(max_length=10, blank=True, null=True, default="")
    category = models.CharField(max_length=100, blank=True, null=True, default="")
    name = models.CharField(max_length=30, blank=True, null=True, default="")
    avatar = models.ImageField(upload_to='uploads/user/avatar', null=True, blank=True, default="")
    startup = models.CharField(max_length=30, blank=True, null=True, default="")
    agreement = models.BooleanField(default=True)
    position = models.CharField(max_length=20, blank=True, null=True, default="")
    tel = models.CharField(max_length=30, blank=True, null=True, default="")
    web = models.CharField(max_length=30, blank=True, null=True, default="")
    additional_email = models.CharField(max_length=100, blank=True, null=True, default="없음")
    department = models.CharField(max_length=30, blank=True, null=True, default="")
    belong_to = models.CharField(max_length=30, blank=True, null=True, default="")
    interest = models.ManyToManyField("SupportBusiness", blank=True, null=True)
    interest_startup = models.ManyToManyField("Startup", blank=True, null=True)
    interest_clip = models.ManyToManyField("Clip", blank=True, null=True)
    interest_course = models.ManyToManyField("Course", blank=True, null=True)
    interest_path = models.ManyToManyField("Path", blank=True, null=True)
    sns = models.CharField(max_length=100, blank=True, null=True)

    phone = models.CharField(max_length=100, blank=True, null=True, default="")
    boss = models.ForeignKey("AdditionalUserInfo", blank=True, null=True)

    facebook = models.CharField(max_length=1, blank=True, null=True)
    twitter = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return self.user.username

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

    def lowest_manager(self):
        if len(self.additionaluserinfo_set.all()) == 0:
            return self
        else:
            result = []
            for obj in self.additionaluserinfo_set.all():
                result.append(obj.lowest_manager())
            return result

    def highest_manager(self):
        if self.boss == None :
            return self
        else:
            return AdditionalUserInfo.objects.filter(pk=self.boss.id)[0].highest_manager()

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
    name = models.CharField(max_length=100, blank=True, null=True, )
    desc = models.TextField(blank=True, null=True, default="")
    short_desc = models.TextField(blank=True, null=True, default="")
    fund_status = models.TextField(blank=True, null=True, default="")
    service_products = models.TextField(blank=True, null=True, default="")
    employee_number = models.CharField(max_length=5, blank=True, null=True, default="")
    established_date = models.DateField(blank=True, null=True, )
    intro_text = models.TextField()
    logo = models.CharField(max_length=1000, blank=True, null=True)
    back_img = models.CharField(max_length=1000, blank=True, null=True)
    tag_string = models.CharField(max_length=1000, blank=True, null=True)
    youtube = models.CharField(max_length=300, blank=True, null=True)
    facebook = models.CharField(max_length=300, blank=True, null=True)
    insta = models.CharField(max_length=300, blank=True, null=True)

    address_0 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_1 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_2 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_detail_0 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_detail_1 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_detail_2 = models.CharField(max_length=400, default="", blank=True, null=True, )
    address_0_title = models.CharField(max_length=30, default="", blank=True, null=True, )
    address_1_title = models.CharField(max_length=30, default="", blank=True, null=True, )
    address_2_title = models.CharField(max_length=30, default="", blank=True, null=True, )
    business_file = models.CharField(max_length=300, default="", blank=True, null=True)
    website = models.CharField(max_length=300, default="", blank=True, null=True, )
    email = models.CharField(max_length=100, default="", blank=True, null=True, )
    category = models.CharField(max_length=200, default="", blank=True, null=True, )
    thumbnail = models.ImageField(upload_to='uploads/user/company', null=True, blank=True)
    # thumbnail =ProcessedImageField(
    #     upload_to='uploads/user/company',
    #     processors=[Thumbnail(121, 121)],  # 처리할 작업 목룍
    #     format='JPEG',  # 최종 저장 포맷
    #     options={'quality': 100})

    filter = models.ManyToManyField("Filter", blank=True, null=True)
    tag = models.ManyToManyField("Tag", blank=True, null=True)

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
    fund_before_year_0 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_1 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_2 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_3 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_4 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_5 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_6 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_7 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_8 = models.CharField(max_length=13, blank=True, null=True, default="")
    fund_before_year_9 = models.CharField(max_length=13, blank=True, null=True, default="")

    fund_before_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_3 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_4 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_5 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_6 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_7 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_8 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_9 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_0 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_1 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_2 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_3 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_4 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_5 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_6 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_7 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_8 = models.CharField(max_length=20, blank=True, null=True, default="")
    fund_before_agent_9 = models.CharField(max_length=20, blank=True, null=True, default="")

    def __str__(self):
        return "회사이름:" + self.name

    def get_absolute_url(self):
        return reverse('startup_detail', args=[self.id])



class Revenue(models.Model):
    startup = models.ForeignKey(Startup)
    year = models.CharField(max_length=5, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)

class Service(models.Model):
    startup = models.ForeignKey(Startup)
    img = models.CharField(max_length=300, null=True, blank=True, default="")
    intro = models.TextField()
    file = models.CharField(max_length=300, null=True, blank=True, default="")
    name = models.CharField(max_length=200, blank=True, null=True)
    show = models.CharField(max_length=10, blank=True, null=True)

class Fund(models.Model):
    startup = models.ForeignKey(Startup)
    year = models.CharField(max_length=5, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)
    agency = models.CharField(max_length=100, blank=True, null=True)
    step = models.CharField(max_length=100, blank=True, null= True)
    currency = models.CharField(max_length=4 , blank=True, null=True)

class TradeInfo(models.Model):
    startup = models.ForeignKey(Startup)
    year = models.CharField(max_length=5, blank=True, null=True)

    size = models.CharField(max_length=10, blank=True, null=True)

class Activity(models.Model):
    startup = models.ForeignKey(Startup)
    kind = models.CharField(max_length=100, blank=True, null= True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    text = models.TextField()
    img = models.CharField(max_length=300, blank=True, null=True)
    youtube = models.CharField(max_length=300, blank=True, null=True)

class ActivityLike(models.Model):
    activity = models.ForeignKey(Activity)
    user = models.ForeignKey(AdditionalUserInfo)
    like_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class Reply(models.Model):
    activity = models.ForeignKey(Activity)
    text = models.TextField()
    author = models.ForeignKey(Startup)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class History(models.Model):
    startup = models.ForeignKey(Startup)
    year = models.CharField(max_length=4, blank=True, null=True)
    month = models.CharField(max_length=2, blank=True, null= True)
    content = models.TextField()



class SupportBusiness(models.Model):
    user = models.ForeignKey("AdditionalUserInfo", blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True, default="")
    title_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    title_sub = models.CharField(max_length=300, blank=True, null=True, default="")
    title_sub_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    business_period_start = models.DateField(blank=True, null=True)
    business_period_end = models.DateField(blank=True, null=True)
    poster = models.CharField(max_length=1000, blank=True, null=True)
    relate_sb=models.ForeignKey("SupportBusiness",blank=True, null=True)
    short_desc = models.CharField(max_length=14, blank=True, null=True, default="")
    place = models.TextField(blank=True, null=True, default="")
    place_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    subject = models.TextField(blank=True, null=True, default="")
    subject_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    business_detail = models.TextField(blank=True, null=True, default="")
    business_detail_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    apply_start = models.DateTimeField(blank=True, null=True, )
    apply_end = models.DateTimeField(blank=True, null=True, )
    object = models.TextField(blank=True, null=True, default="")
    employee_num = models.IntegerField(blank=True, null=True, default=0)
    employee_lt_gt = models.CharField(blank=True, null=True, default="제한없음", max_length=4)
    object_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    condition = models.TextField(blank=True, null=True, default="")
    condition_tag = models.CharField(max_length=500, null=True, blank=True, default="")
    condition_etc = models.TextField(blank=True, null=True, default="")
    condition_etc_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    object_span = models.TextField(blank=True, null=True, default="")
    object_span_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    recruit_size = models.CharField(max_length=30, blank=True, null=True, default="")
    prefer = models.TextField(blank=True, null=True, default="")
    prefer_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    constraint = models.TextField(blank=True, null=True, default="")
    constraint_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    choose_method = models.TextField(blank=True, null=True, default="")
    icon_set = models.CharField(max_length=2, blank=True, null=True, default="")
    pro_0_choose = models.TextField(blank=True, null=True, default="")
    pro_0_choose_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    pro_0_start = models.DateField(blank=True, null=True)
    pro_0_end = models.DateField(blank=True, null=True)
    pro_0_open = models.DateField(blank=True, null=True)
    pro_0_criterion = models.TextField(blank=True, null=True, default="")
    pro_0_criterion_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    pro_1_choose = models.TextField(blank=True, null=True, default="")
    pro_1_choose_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    pro_1_start = models.DateField(blank=True, null=True)
    pro_1_end = models.DateField(blank=True, null=True)
    pro_1_open = models.DateField(blank=True, null=True)
    pro_1_criterion = models.TextField(blank=True, null=True, default="")
    pro_1_criterion_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    pro_2_choose = models.TextField(blank=True, null=True, default="")
    pro_2_choose_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    pro_2_start = models.DateField(blank=True, null=True)
    pro_2_end = models.DateField(blank=True, null=True)
    pro_2_open = models.DateField(blank=True, null=True)
    pro_2_criterion = models.TextField(blank=True, null=True, default="")
    pro_2_criterion_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    supply_content = models.TextField(blank=True, null=True, default="")
    supply_content_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    supply_condition = models.TextField(blank=True, null=True, default="")
    supply_condition_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    open_method= models.CharField(max_length=500, blank=True,null=True)
    ceremony = models.TextField( blank=True, null=True )
    etc = models.TextField()
    ceremony_start = models.DateField(blank=True, null=True)
    ceremony_end = models.DateField(blank=True, null=True)
    faq = models.TextField(blank=True, null=True, default="")
    faq_tag = models.CharField(max_length=500, blank=True, null=True, default="")
    additional_faq = models.TextField(blank=True, null=True, default="")
    etc = models.TextField(blank=True, null=True, default="")
    etc_file_title = models.CharField(max_length=1000, blank=True, null=True, default="")
    kind2_text = models.TextField(blank=True, null=True, default="")
    meta = models.CharField(max_length=1000, blank=True, null=True, default="")
    meta_file_info = models.CharField(max_length=1000, blank=True, null=True, default="")
    filter = models.ManyToManyField("Filter")
    due_status = models.CharField(max_length=2, blank=True, null=True)
    open_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    hit = models.IntegerField(default=0)
    finance_amount = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)
    confirm = models.BooleanField(default=True)
    is_blind = models.BooleanField(default=False)
    confirm_count = models.IntegerField(default=0, blank=True, null=True)
    confirm_list = models.ManyToManyField( "AdditionalUserInfo",  blank=True, null=True, related_name="confirm_list")
    pick_date = models.DateField(blank=True, null=True)
    step = models.CharField(blank=True, null=True, max_length=2)
    additional_file=models.CharField(blank=True, null=True, max_length=500)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('support', args=[self.id])
    def get_absolute_url_manage(self):
        return reverse('manage_support_detail', args=[self.id])
    def is_past_due(self):

        try:
            if self.apply_end > datetime.datetime.now():
                return "모집중"
            else:
                return "모집 마감"
        except:
            return ""

    def is_past(self):
        try:
            if datetime.datetime.now() < self.apply_end:
                return False
            else:
                return True
        except:
            return False

    def is_pre(self):
        try:
            if datetime.datetime.now() < self.apply_start:
                return True
            else:
                return False
        except:
            return False


    def manage_status(self):

        time_min = datetime.datetime.now()
        if self.confirm == True :
            return "승인대기중"

        if self.confirm == False and self.open_status == True and self.complete == False and self.apply_end > time_min and self.apply_start < time_min:
            return "공고중"
        if self.apply_end < datetime.datetime.now() and  self.confirm == False and self.open_status == True and self.complete == False :
            return "모집 마감"
        if self.confirm == False and self.open_status == False and self.complete == True :
            return "공고 종료"
        if self.confirm == False and self.open_status == False and self.complete == False:
            return "작성중"
        if self.apply_start > datetime.datetime.now():
            return  "공고 대기중"

    def is_blind_state(self):
        time_min = datetime.datetime.now()
        if self.is_blind == 1:
            return "블라인드"
        elif self.confirm==1:
            return ""
        elif self.confirm == False and self.open_status == True and self.complete == False and self.apply_end > time_min and self.apply_start < time_min and self.is_blind==False:
            return "노출"
        else:
            return ""



class Filter(models.Model):
    cat_0 = models.CharField(max_length=100)
    cat_1 = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        if self.cat_1 is not None:
            return self.cat_0 + "/" + self.cat_1 + "/" + self.name
        else:
            return self.cat_0 + "/" + self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BusinessTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Appliance(models.Model):
    sb = models.ForeignKey(SupportBusiness, blank=True, null=True)
    startup = models.ForeignKey(Startup, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True, default="")
    business_number = models.CharField(max_length=20, blank=True, null=True, default="")
    industry_category = models.CharField(max_length=100, blank=True, null=True, default="")
    found_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=400, blank=True, null=True, default="")
    repre_name = models.CharField(max_length=100, blank=True, null=True, default="")
    repre_tel = models.CharField(max_length=100, blank=True, null=True, default="")
    repre_email = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_name = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_tel = models.CharField(max_length=100, blank=True, null=True, default="")
    mark_email = models.CharField(max_length=100, blank=True, null=True, default="")
    keyword = models.CharField(max_length=1000, blank=True, null=True, default="")

    sns= models.CharField(max_length=300, blank=True, null=True, default="")
    total_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    hold_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    assurance_employee = models.CharField(max_length=20, blank=True, null=True, default="")
    filter = models.ManyToManyField("Filter")

    company_intro = models.TextField()
    business_intro = models.TextField()
    exp = models.TextField()

    kind = models.CharField(max_length=10, blank=True, null=True)
    keyword = models.CharField(max_length=1000, blank=True, null=True)
    homepage = models.CharField(max_length=100, blank=True, null=True)
    patent_file  = models.CharField(max_length=1000, blank=True, null=True, default="")
    trade_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    sub_patent_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    design_file = models.CharField(max_length=1000, blank=True, null=True, default="")

    service_category = models.CharField(max_length=200, blank=True, null=True, default="")
    service_name = models.CharField(max_length=100, blank=True, null=True, default="")
    service_intro = models.TextField(blank=True, null=True, default="")

    oversea = models.CharField(max_length=300, blank=True, null=True, default="")
    oversea_status = models.TextField(blank=True, null=True, default="")

    specification = models.TextField(blank=True, null=True, default="")
    intro = models.TextField(blank=True, null=True, default="")
    detail = models.TextField(blank=True, null=True, default="")

    patent_2_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    ppt_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    service_file = models.CharField(max_length=1000, blank=True, null=True, default="")
    cert_file = models.CharField(max_length=1000, blank=True, null=True, default="")

    ir_file = models.FileField(upload_to="gca/ir", blank=True, null=True, max_length=1000)
    business_file = models.FileField(upload_to="gca/business", blank=True, null=True, max_length=1000)
    tax_file = models.FileField(upload_to="gca/tax", blank=True, null=True, max_length=1000)
    fund_file = models.FileField(upload_to="gca/fund", blank=True, null=True, max_length=1000)
    ppt_file = models.FileField(upload_to="gca/ppt", blank=True, null=True, max_length=1000)
    etc_file = models.FileField(upload_to="gca/etc", blank=True, null=True, max_length=1000)
    etc_file_title = models.TextField(blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update_at = models.DateField(auto_now_add=True, blank=True, null=True)
    is_submit = models.BooleanField(default=False)
    pick_date = models.DateField(blank=True, null=True) # 선정일 = 게시일
    up_date = models.DateField(blank=True, null=True) # 승인 요청일
    writing_step = models.CharField(max_length=3, blank=True, null=True)

    class meta:
        get_latest_by = "updated_at"

    def is_awarded(self):
        if len(Award.objects.all().filter(sb=self.sb).filter(startup=self.startup)) > 0:
            return True
        else:
            return False

class RevenueInApplication(models.Model):
    application = models.ForeignKey(Appliance)
    year = models.CharField(max_length=5, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)

class TradeInApplication(models.Model):
    application = models.ForeignKey(Appliance)
    year = models.CharField(max_length=5, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)

class OverseaInApplication(models.Model):
    application = models.ForeignKey(Appliance)
    nation = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(0)

class Award(models.Model):
    sb = models.ForeignKey(SupportBusiness)
    startup = models.ForeignKey(Startup)
    name = models.CharField(max_length=100, blank=True, null=True)
    prize = models.CharField(max_length=100, blank=True, null=True)
    update_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class PageRate(models.Model):
    page = models.CharField(max_length=1000, blank=True, null=True)
    user = models.CharField(max_length=10, blank=True, null=True)
    rate = models.CharField(max_length=10, blank=True, null=True)


class Alarm(models.Model):
    user = models.ForeignKey(AdditionalUserInfo)
    content = models.CharField(max_length=500, blank=True, null=True)
    origin_sb = models.ForeignKey(SupportBusiness, blank=True, null=True)
    origin_st = models.ForeignKey(Startup, blank=True, null=True)
    category = models.CharField(max_length=2, blank=True, null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class DayUser(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class NewUser(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class Session(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class SessionPerUser(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class PageView(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class PagePerSession(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class AvgTimePerSession(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class ExpireTime(models.Model):
    count = models.IntegerField(default=0, blank=None, null=None)


class EmailConfirmation(models.Model):
    email = models.CharField(max_length=300)
    confirmation_code = models.CharField(max_length=300)
    confirm = models.BooleanField(default=False)
    
class HitLog(models.Model):
    sb = models.ForeignKey(SupportBusiness)
    user = models.ForeignKey("AdditionalUserInfo", blank=True, null=True )
    date = models.DateField(blank=True, null=True, default=datetime.datetime.now())

class startup_found(models.Model):
    year = models.CharField(max_length=4, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)

class startup_found_gg(models.Model):
    year = models.CharField(max_length=4, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)

class avg_employee(models.Model):
    year = models.CharField(max_length=4, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)

class avg_employee_gg(models.Model):
    year = models.CharField(max_length=4, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)


class EduFilter(models.Model):
    name= models.CharField(max_length=100, blank=True, null=True)

class Clip(models.Model):
    user= models.ForeignKey(AdditionalUserInfo)
    title = models.CharField(max_length=200, null=True, blank=True)
    youtube = models.CharField(max_length=100, null=True, blank=True)
    mov_address = models.CharField(max_length=200, null=True, blank=True)
    thumb = models.CharField(max_length=400, null=True, blank=True)
    filter = models.ManyToManyField(EduFilter)
    object = models.CharField(max_length=300, blank=True, null=True)
    info = models.TextField()
    play = models.IntegerField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return self.title

class Course(models.Model):
    user = models.ForeignKey(AdditionalUserInfo)
    title = models.CharField(max_length=200, null=True, blank=True)
    filter = models.ManyToManyField(EduFilter, blank=True, null=True)
    thumb = models.CharField(max_length=400, null=True, blank=True)
    rec_dur = models.CharField(max_length=300, blank=True, null=True)
    object = models.CharField(max_length=300, blank=True, null=True)
    info = models.TextField()
    clips = models.ManyToManyField(Clip)
    total_play = models.IntegerField( blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return self.title

class Path(models.Model):
    user = models.ForeignKey(AdditionalUserInfo)
    title = models.CharField(max_length=200, null=True, blank=True)
    filter = models.ManyToManyField(EduFilter, blank=True, null=True)
    thumb = models.CharField(max_length=400, null=True, blank=True)
    rec_dur = models.CharField(max_length=300, blank=True, null=True)
    object = models.CharField(max_length=300, blank=True, null=True)
    info = models.TextField()
    course = models.ManyToManyField(Course)
    total_play = models.IntegerField( blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.title

class HitClipLog(models.Model):
    clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)

class HitCourseLog(models.Model):
    course = models.ForeignKey(Course)
    clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)

class HitPathLog(models.Model):
    path = models.ForeignKey(Path)
    clip = models.ForeignKey(Clip)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(AdditionalUserInfo)



class  WatchClipHistory(models.Model):
    clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)

class  WatchCourseHistory(models.Model):
    course = models.ForeignKey(Course)
    clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)

class  WatchPathHistory(models.Model):
    Path = models.ForeignKey(Path)
    course = models.ForeignKey(Course)
    clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)

class FavPathLog(models.Model):
    Path = models.ForeignKey(Path)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)

class FavCourseLog(models.Model):
    Course = models.ForeignKey(Course)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)

class FavClipLog(models.Model):
    Clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)


class CompletedClip(models.Model):
    Clip = models.ForeignKey(Clip)
    user = models.ForeignKey(AdditionalUserInfo)
    date = models.DateField(auto_now_add=True)