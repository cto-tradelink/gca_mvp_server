



# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from django.contrib.auth.views import login as auth_login
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.templatetags.socialaccount import get_providers
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added, pre_social_login
from .models import *
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
import inspect
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.core.files.uploadedfile import SimpleUploadedFile
import pdfkit
import datetime
from datetime import timedelta
from django.http import JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
import json
from django.core import serializers
from celery import shared_task
from supporting_business.tasks import *
import xlwt
import io
import urllib
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.db import connection
from django.contrib import messages
import copy
from django.views.decorators.csrf import csrf_exempt
import itertools
def repeated_email(request):
    return HttpResponse("이미 가입된 이메일 입니다. 다른 방법으로 로그인 하세요.")


def login_user3(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # try:
            #     AdditionalUserInfo(user=request.user).save()
            # except:
            #     pass
            # print("here")




            try:
                if str(user.additionaluserinfo.auth) == "4" or (user.additionaluserinfo.auth) == "5":

                    print(user.additionaluserinfo.name + "매니져님 로그인 하였음.")
                    return redirect("dashboard")
                else:
                    return redirect('index')
            except:
                return redirect('index')
        else:
            return HttpResponse('로그인 실패. 다시 시도 해보세요.')
    else:
        providers = []
        for provider in get_providers():
            # social_app속성은 provider에는 없는 속성입니다.
            try:
                provider.social_app = SocialApp.objects.get(provider=provider.id, sites=settings.SITE_ID)
            except SocialApp.DoesNotExist:
                provider.social_app = None
        providers.append(provider)
        login_form = LoginForm()
    return render(request, 'pc/accounts/login.html', {"form": login_form})

def logout_user(request):
    logout(request)
    return redirect('search')



@csrf_exempt
def vue_login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                if str(user.additionaluserinfo.auth) == "4" or (user.additionaluserinfo.auth) == "5":
                    print(user.additionaluserinfo.name + "매니져님 로그인 하였음.")
                    if len(user.additionaluserinfo.additionaluserinfo_set.all())>0:
                        return JsonResponse({"result":"success", "user":"ma","id":user.additionaluserinfo.id})
                    return JsonResponse({"result":"success","user": "m","id":user.additionaluserinfo.id})
                else:
                    return JsonResponse({"result":"success","user":"u","id":user.additionaluserinfo.id})
            except:
                return JsonResponse({})
        else:
            return JsonResponse({"result":'로그인 실패. 다시 시도 해보세요.'})



def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # try:
            #     AdditionalUserInfo(user=request.user).save()
            # except:
            #     pass
            # print("here")


            try:
                if str(user.additionaluserinfo.auth) == "4" or (user.additionaluserinfo.auth) == "5":

                    print(user.additionaluserinfo.name + "매니져님 로그인 하였음.")
                    return redirect("dashboard")
                else:
                    return redirect('index')
            except:
                return redirect('index')
        else:
            return HttpResponse('로그인 실패. 다시 시도 해보세요.')
    else:
        providers = []
        for provider in get_providers():
            # social_app속성은 provider에는 없는 속성입니다.
            try:
                provider.social_app = SocialApp.objects.get(provider=provider.id, sites=settings.SITE_ID)
            except SocialApp.DoesNotExist:
                provider.social_app = None
        providers.append(provider)
        login_form = LoginForm()
    return render(request, 'pc/accounts/login.html', {"form": login_form})

def qs_al(qs, startup, user):
    sp= qs
    startup = Startup.objects.get(user=user)
    for s in sp:
        k = list(set((s.filter.all())).intersection(startup.filter.all()))
        s.k_val = len(k)

    sp =sorted(sp, key=lambda q: (q.k_val) , reverse=True)
    final_sp = []
    for q in sp:
        if q.k_val != 0:
            final_sp.append(q)

    pk_list = []
    for q in final_sp:
        pk_list.append(q.id)
    clauses = ' '.join(
        ['WHEN supporting_business_supportbusiness.id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
    ordering = 'CASE %s END' % clauses
    queryset = SupportBusiness.objects.filter(pk__in=pk_list).extra(select={'ordering': ordering},
                                                                    order_by=('ordering',))
    sp = queryset

    return sp;


def index(request):
    today_min = datetime.datetime.now()
    total_sb = SupportBusiness.objects.all().distinct()
    total_amount_list = SupportBusiness.objects.all()
    many_view = SupportBusiness.objects.order_by("-hit").filter(open_status=1).filter(is_blind=False).filter(
        apply_start__lt=today_min).filter(apply_end__gt=today_min).distinct()[:3]
    random = SupportBusiness.objects.all().filter(open_status=1).filter(apply_start__lt=today_min).filter(apply_end__gt=today_min).filter(
        is_blind=False).order_by("?").distinct()[:3]

    sum = 0
    #for t in total_amount_list:
    #    sum += t.finance_amount
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")

    today_min = datetime.datetime.now()
    if request.user.is_authenticated():

        if len(AdditionalUserInfo.objects.all().filter(user=request.user)) == 0:
            AdditionalUserInfo(user=request.user).save()
        try:
            interest = request.user.additionaluserinfo.interest.all()
        except:
            interest = ""
        print(interest)

        if len(Startup.objects.all().filter(user=request.user)) != 0:
            startup = Startup.objects.get(user=request.user)
            filter_string = request.user.startup.filter.all()
            em = request.user.startup.employee_number
            if em == None or em == "":
                em = 0;
            sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
            k = []
            for f in filter_string:
                k.append(str(f.id))
            startup_filter = startup.filter.all()
            sb_total =qs_al(sp , startup, request.user)
            sb_0 = qs_al( sp.filter(filter__cat_1="자금지원").distinct()         , startup, request.user)
            sb_1 = qs_al( sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct()  , startup, request.user)
            sb_2 = qs_al( sp.filter(filter__cat_1="교육").distinct()           , startup, request.user)
            sb_3 = qs_al( sp.filter(filter__cat_1="판로").distinct()           , startup, request.user)
            sb_4 = qs_al( sp.filter(filter__cat_1="네트워킹").distinct()         , startup, request.user)
            sb_5 = qs_al( sp.filter(filter__cat_1="공간지원").distinct()         , startup, request.user)
            sb_6 = qs_al( sp.filter(filter__cat_1="기타지원").distinct()         , startup, request.user)
            sb_7 = qs_al( sp.filter(filter__cat_1="피칭").distinct()           , startup, request.user)
        else:
            k = []
            sb_0 = ""
            sb_1 = ""
            sb_2 = ""
            sb_3 = ""
            sb_4 = ""
            sb_5 = ""
            sb_6 = ""
            sb_total = ""
            sb_7 = ""
        return render(request, 'pc/index.html', {
            "form": "", "random": random, "interest": interest,
            "filter_0": filter_0, "filter_1": filter_1,
            "filter_2": filter_2, "filter_3": filter_3,
            "filter_4": filter_4, "filter_5": filter_5,
            "filter_6": filter_6, "filter_7": filter_7,
            "filter_8": filter_8, "filter_9": filter_9,
            "filter_10": filter_10, "filter_11": filter_11,
            "sb_0": sb_0, "sb_1": sb_1, "sb_2": sb_2, "sb_3": sb_3, "sb_4": sb_4,
            "sb_5": sb_5, "sb_6": sb_6,
            "sb_total": sb_total,
            "many_view": many_view,
            "total": total_sb,
            "sum": sum, "sb_7": sb_7,
            "filter_string": ",".join(k)
        })
    else:
        return render(request, 'pc/index.html', {"form": "", "random": random,
                                                 "many_view": many_view,
                                                 "total": total_sb,
                                                 "sum": sum,
                                                 })


def matching_business(request):
    if request.user.is_authenticated():
        if (len(Startup.objects.all().filter(user=request.user)) == 0):
            return render(request, 'pc/matching_temporary.html')
        else:
            return redirect("index")
    else:
        return render(request, 'pc/matching_temporary.html')


def startup_list(request):
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    qs = Startup.objects.all()
    if request.GET.get("filter", ",") != ",":

        filter_string = request.GET.get("filter").split(",")
        if filter_string == [""]:
            filter_string = []
        em = request.GET.get("em", 0)
        q_obj = Q()
        filter_list = []
        for f in filter_string:
            filter_list.append(Filter.objects.get(id=f))
        for filter in filter_list:
            if filter.cat_0 != "조건" and filter.cat_1 != "업력":
                # q_obj.add(Q(filter__id=filter.id), Q.AND)
                qs = qs.filter(filter=filter)
        if Filter.objects.filter(cat_0="조건").filter(cat_1="업력").filter(name="제한없음")[0] not in filter_list:
            for filter in filter_list:
                if filter.cat_0 == "조건" and filter.cat_1 == "업력":
                    qs = qs.filter(filter=filter)
        if (em != 0):
            qs = qs.filter(Q(employee_number__lte=em) | Q(employee_number__lte=""))
    if (request.GET.get("search", "") != ""):
        word = request.GET.get("search")
        qs = qs.filter(Q(name__contains=word) | Q(desc__contains=word) | Q(short_desc__contains=word) | Q(
            tag__name__contains=word)).distinct()
    elif (request.GET.get("search", "") == "" and request.GET.get("filter", ",") == ","):
        qs = Startup.objects.all()
    return render(request, 'pc/startup_list.html', {"qs": qs,
                                                    "filter_0": filter_0, "filter_1": filter_1,
                                                    "filter_2": filter_2, "filter_3": filter_3,
                                                    "filter_4": filter_4, "filter_5": filter_5,
                                                    "filter_6": filter_6, "filter_7": filter_7,
                                                    "filter_8": filter_8, "filter_9": filter_9,
                                                    "filter_10": filter_10, "filter_11": filter_11,
                                                    })


def startup_detail(request, id):
    startup = get_object_or_404(Startup, id=id)
    return render(request, 'pc/startup_detail.html', {"startup": startup})


def new_startup(request):
    if len(Startup.objects.all().filter(user=request.user)) != 0:
        data = Startup.objects.all().filter(user=request.user)[0]
        name = data.name
        found_date = data.established_date
        address = data.address
        employee = data.employee_number
        email = data.email
        website = data.website
        field = data.category
    else:
        field = ""
        name = ""
        found_date = ""
        address = ""
        employee = ""
        email = ""
        website = ""
    form_0 = NewStartupUp(initial={
        "name": name,
        "field": field,
        "found_date": found_date,
        "location": address,
        "employee": employee,
        "email": email,
        "website": website
    })
    form_1 = NewStartupBot

    return render(request, 'pc/new_company.html', {"form_up": form_0, "form_bot": form_1})


def startup_edit(request):
    if request.method == "POST":
        form_data_0 = NewStartupUp(request.POST)
        form_data_1 = NewStartupBot(request.POST)

        if form_data_0.is_valid() and form_data_1.is_valid():
            if len(Startup.objects.all().filter(user=request.user)) != 0:
                target = Startup.objects.all().filter(user=request.user)[0]
                target.name = form_data_0.cleaned_data["name"]
                target.found_date = form_data_0.cleaned_data["found_date"]
                target.address = form_data_0.cleaned_data["location"]
                target.category = form_data_0.cleaned_data["field"]
                target.employee = form_data_0.cleaned_data["employee"]
                target.email = form_data_0.cleaned_data["email"]
                target.website = form_data_0.cleaned_data["website"]
                target.keyword = form_data_1.cleaned_data["keyword"]
                target.save()
            else:
                Startup(
                    user=request.user,
                    name=form_data_0.cleaned_data["name"],
                    category=form_data_0.cleaned_data["field"],
                    established_date=form_data_0.cleaned_data["found_date"],
                    address=form_data_0.cleaned_data["location"],
                    employee=form_data_0.cleaned_data["employee"],
                    email=form_data_0.cleaned_data["email"],
                    website=form_data_0.cleaned_data["website"]
                ).save()
    return redirect("new_startup")


def edit_mypage(request):
    if request.method == "POST":
        form_data_0 = MyPageUp(request.POST)
        form_data_1 = MyPageBot(request.POST)
        if form_data_0.is_valid() and form_data_1.is_valid():
            user = AdditionalUserInfo.objects.all().filter(user=request.user)
            if (len(user) != 0):
                target = AdditionalUserInfo.objects.get(user=request.user)
                target.tel = form_data_1.cleaned_data["phone"]
                target.name = form_data_0.cleaned_data["name"]
                target.additional_email = form_data_0.cleaned_data["additional_email"]
                target.save()
            else:
                AdditionalUserInfo(
                    user=request.user,
                    tel=form_data_1.cleaned_data["phone"],
                    name=form_data_0.cleaned_data["name"],
                    additional_email=form_data_0.cleaned_data["additional_email"]
                ).save()

        return redirect("edit_mypage")

    else:
        user = AdditionalUserInfo.objects.all().filter(user=request.user)
        id = request.user.username
        if (len(user) != 0):
            name = user[0].name
            tel = user[0].tel
            agree = user[0].agreement
            additional_email = user[0].additional_email
        else:
            name = ""
            tel = ""
            agree = ""
        form_0 = MyPageUp(initial={
            "id": id,
            "name": name
        })
        form_1 = MyPageBot(initial={
            "phone": tel,
            "agree": agree,
            "additional_email": additional_email,
        })
        email_confirm = 0
        if additional_email != "" and len(
                EmailConfirmation.objects.all().filter(email=additional_email).filter(confirm=True)) != 0:
            email_confirm = 1

        return render(request, 'pc/edit_mypage.html',
                      {"form_up": form_0, "form_bot": form_1, "email_confirm": email_confirm})


def mypage(request):
    #if len(Startup.objects.all().filter(user=request.user)) == 0:
    #    return redirect("company_profile")
    #else:
    try:
         qs_int = request.user.additionaluserinfo.interest.all()
         qs_write = Appliance.objects.all().filter(startup=request.user.startup).filter(is_submit=False)
         qs_com = Appliance.objects.all().filter(startup=request.user.startup).filter(is_submit=True).filter(
             sb__complete=0)
         award_list = []
         q_obj = Q()
         q_obj_not = Q()

         if Award.objects.all().filter(startup=request.user.startup):
             for award in Award.objects.all().filter(startup=request.user.startup):
                 q_obj |= Q(sb_id=award.sb_id)
                 q_obj_not |= Q(sb_id=award.sb_id)
             qs_result_win = Appliance.objects.all().filter(sb__complete=1).filter(startup=request.user.startup).filter(
                 q_obj)
         else:
             qs_result_win = ""

         lose_arr = []
         for qs in Appliance.objects.all().filter(startup=request.user.startup).filter(sb__complete=1).filter(
                 is_submit=True):
             if len(Award.objects.all().filter(startup=request.user.startup).filter(sb_id=qs.sb_id)) == 0:
                 lose_arr.append(qs)
    except Exception as e:
        qs_int = request.user.additionaluserinfo.interest.all()
        qs_write =""
        qs_com =""
        award_list = []
        q_obj = Q()
        q_obj_not = Q()
        qs_result_win = ""

        lose_arr = []

    return render(request, 'pc/mypage_apply.html', {"qs_int": qs_int,
                                                    "qs_write": qs_write,
                                                        "qs_com": qs_com,
                                                        "qs_result_win": qs_result_win,
                                                        "qs_result_lose": lose_arr,
                                                        })


def support(request, id):
    today_min = datetime.datetime.now()
    support = get_object_or_404(SupportBusiness, id=id)
    sp = get_object_or_404(SupportBusiness, id=id)
    random = SupportBusiness.objects.all().filter(open_status=1).filter(
        apply_start__lt=today_min).filter(apply_end__gt=today_min).filter(is_blind=False).exclude(id=sp.id).order_by("?")[0]
    if request.user.is_authenticated:
        if request.user.additionaluserinfo.auth!="4" and request.user.additionaluserinfo.auth!="5":
            support.hit = support.hit + 1
            support.save()
            HitLog(sb=support).save()
    else:
        support.hit = support.hit + 1
        support.save()
        HitLog(sb=support).save()
    total_win=""
    try:
        print("here")
        if request.user.is_authenticated and request.user.startup:
            interest = request.user.additionaluserinfo.interest.all()
            alarm_set = Alarm.objects.all().filter(origin_sb=support).filter(user=request.user.additionaluserinfo)
            alarm_set.update(read=True)
        else:
            interest = ""
        apply_status = Appliance.objects.all().filter(startup=request.user.startup).filter(sb=support).order_by("-id")
        print(apply_status)
        if len(apply_status) != 0:
            status = "true"
            app = apply_status[0].id
            is_submit = apply_status[0].is_submit
        else:
            status = "false"
            app = ""
            is_submit = ""
    except Exception as e:
        print(e)
        status = "false"
        app = ""
        is_submit = ""
        interest = ""
    hitlog = []
    date_arr = []
    applog = []
    for k in range(1, 30):
        from_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k + 1)
        to_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k)
        date_arr.append(from_da.isoformat().split("T")[0])
        hitlog.append(len(HitLog.objects.all().filter(date__gt=to_da).filter(sb=sp).filter(date__lte=from_da)))
        applog.append(
            len(Appliance.objects.all().filter(sb=sp).filter(update_at__gt=to_da).filter(update_at__lt=from_da)))
    if support.relate_sb != None:
        hit_log_rel_sb = []
        hit_day_arr_rel_sb = []
        app_dat_rel_sb = []
        for k in range(0, ( support.relate_sb.apply_end-support.relate_sb.apply_start).days +1 ):
            hit_day_arr_rel_sb.append( (support.relate_sb.apply_start + datetime.timedelta(days=k) ).isoformat().split("T")[0])
            hit_log_rel_sb.append(len(HitLog.objects.all().filter(sb=support.relate_sb).filter(date__gte=support.relate_sb.apply_start + datetime.timedelta(days=k)).filter(date__lt=support.relate_sb.apply_start + datetime.timedelta(days=k+1))))
            app_dat_rel_sb.append(
                len(Appliance.objects.all().filter(sb=support.relate_sb).filter(update_at__gt=support.relate_sb.apply_start + datetime.timedelta(days=k)).filter(update_at__lt=support.relate_sb.apply_start + datetime.timedelta(days=k+1))))
        print(hit_day_arr_rel_sb)
        print(hit_log_rel_sb)
        winner_list = Award.objects.all().filter(sb=support.relate_sb)
        total_app = len(Appliance.objects.all().filter(sb=support.relate_sb))
        total_view = len(HitLog.objects.all().filter(sb=support.relate_sb).filter(date__gte=support.relate_sb.apply_start).filter(date__lte=support.relate_sb.apply_end))
        total_win = len(winner_list)
        q_obj = Q()
        if len(winner_list) != 0:
            for winner in winner_list:
                q_obj |= Q(startup_id=winner.startup) & Q(sb=support.relate_sb)
            win_filter = []
            for a in winner_list:
                for f in a.startup.filter.all():
                    if f.cat_1 != "소재지" and f.cat_1 != "기업형태" and f.cat_0 !="지원형태":
                        win_filter.append(f.name)
            win_dict = {i: win_filter.count(i) for i in win_filter}
            print(win_dict)
            local_filter = []
            for a in winner_list:
                for f in a.startup.filter.all():
                    if f.cat_1 == "소재지":
                        local_filter.append(f.name)
            win_local_dict = {i: local_filter.count(i) for i in local_filter}
            case_filter = []
            for a in winner_list:
                for f in a.startup.filter.all():
                    if f.cat_1 == "기업형태":
                        case_filter.append(f.name)
            win_case_dict = {i: case_filter.count(i) for i in case_filter}
            ap_winner = Appliance.objects.all().filter(q_obj)
            re_0 = zip(hit_day_arr_rel_sb, hit_log_rel_sb)
            re_1 = zip( hit_day_arr_rel_sb, app_dat_rel_sb)
        else:
            total_app=""
            total_view=""
            ap_winner = ""
            win_case_dict = ""
            win_dict = ""
            win_local_dict = []
            hit_log_rel_sb =[]
            hit_day_arr_rel_sb = []
            app_dat_rel_sb=[]
            re_0 = ""
            re_1 =""
            total_win=""

    else:
        ap_winner = ""
        win_case_dict = ""
        win_dict = ""
        win_local_dict = ""
        total_app = ""
        total_view = ""
        ap_winner = ""
        win_case_dict = ""
        win_dict = ""
        win_local_dict = []
        hit_log_rel_sb = []
        total_win=""
        re_0=""
        re_1=""

    return render(request, 'pc/support_back.html',
                  {"random": random, "is_submit": is_submit, "support": support, "status": status, "app": app,"hitlog":hitlog,"applog":applog, "date_arr":date_arr,
                   "total_view":total_view, "total_app":total_app,"total_win":total_win,
                   "hit_log_rel_sb":hit_log_rel_sb, "hit_day_arr_rel_sb":re_0,"app_dat_rel_sb":re_1,
                   "interest": interest,"ap_winner":ap_winner,"win_case_dict":win_case_dict,"win_dict":win_dict,"win_local_dic":win_local_dict})


@login_required
def manage_support_detail(request, id):
    try:
        if request.user.additionaluserinfo.category == "1":
            support = get_object_or_404(SupportBusiness, id=id)
            return render(request, "pc/manage_support_detail.html", {"support": support, "id": id})
        else:
            return HttpResponse('권한 없음.')
    except Exception as e:
        print(e)
        return HttpResponse('권한 없음.')


@login_required
def new_support(request):
    print(inspect.getmembers(request.user))
    try:
        if request.user.additionaluserinfo.category == "1":
            if request.method == "POST":
                form = SupportForm(request.POST)
                print(form)
                print(form.is_valid())
                if form.is_valid():
                    support = form.save(commit=False)
                    support.open_date = timezone.localtime(timezone.now()).date()
                    support.createdate = timezone.localtime(timezone.now()).date()
                    support.hit = 0
                    support.apply_num = 0
                    support.author = request.user
                    support.save()
                    if (request.POST.get("filter") != ""):
                        filter_list = request.POST.get("filter").split(",")
                        for filter in filter_list:
                            support.filter.add(Filter.objects.get(id=filter))
                            support.save()
                        return redirect('support', id=support.id)
            else:
                form = SupportForm()
                filter_0 = Filter.objects.all().filter(cat_0="기본장르")
                filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
                filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
                filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
                filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
                filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
                filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
                filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
                filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
                filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
                filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
                filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
                filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
                filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
                filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
                filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
                filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
                filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
                filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
                return render(request, 'pc/new_support_business.html',
                              {"form": form,
                               "filter_0": filter_0,
                               "filter_1": filter_1,
                               "filter_2": filter_2,
                               "filter_3": filter_3,
                               "filter_4": filter_4,
                               "filter_5": filter_5,
                               "filter_6": filter_6,
                               "filter_7": filter_7,
                               "filter_8": filter_8,
                               "filter_9": filter_9,
                               "filter_10": filter_10,
                               "filter_11": filter_11,
                               "filter_12": filter_12,
                               "filter_13": filter_13,
                               "filter_14": filter_14,
                               "filter_15": filter_15,
                               "filter_16": filter_16,
                               "filter_17": filter_17,
                               "filter_18": filter_18,
                               })
        else:
            return HttpResponse('권한 없음.')
    except Exception as e:
        print(e)
        return HttpResponse('권한 없음.')


def company_profile_new(request):
    if len(Startup.objects.all().filter(user=request.user)) != 0:
        return redirect("company_profile_edit")
    if request.method == "POST":
        print(request.POST)
        fu = NewStartupUp(request.POST)
        fb = NewStartupBot(request.POST)
        if fu.is_valid() and fb.is_valid():
            startup = Startup(
                user=request.user,
                name=fu.cleaned_data["name"],
                desc=fb.cleaned_data["desc"],

                established_date=fu.cleaned_data["established_date"],
                category=fu.cleaned_data["category"],
                address_0=fu.cleaned_data["address_0"],
                address_detail_0=fu.cleaned_data["address_0_detail"],
                address_0_title=fu.cleaned_data["address_0_title"],
                address_1=fu.cleaned_data["address_1"],
                address_detail_1=fu.cleaned_data["address_1_detail"],
                address_1_title=fu.cleaned_data["address_1_title"],
                address_2=fu.cleaned_data["address_2"],
                address_detail_2=fu.cleaned_data["address_2_detail"],
                address_2_title=fu.cleaned_data["address_2_title"],
                employee_number=fu.cleaned_data["employee_number"],
                email=fu.cleaned_data["email"],
                website=fu.cleaned_data["website"],
                service_products=fb.cleaned_data["service_products"],
                short_desc=fb.cleaned_data["short_desc"],
                revenue_before_year_0=fb.cleaned_data["revenue_before_year_0"],
                revenue_before_year_1=fb.cleaned_data["revenue_before_year_1"],
                revenue_before_year_2=fb.cleaned_data["revenue_before_year_2"],
                revenue_before_0=fb.cleaned_data["revenue_before_0"],
                revenue_before_1=fb.cleaned_data["revenue_before_1"],
                revenue_before_2=fb.cleaned_data["revenue_before_2"],
                export_before_year_0=fb.cleaned_data["export_before_year_0"],
                export_before_year_1=fb.cleaned_data["export_before_year_1"],
                export_before_year_2=fb.cleaned_data["export_before_year_2"],
                export_before_0=fb.cleaned_data["export_before_0"],
                export_before_1=fb.cleaned_data["export_before_1"],
                export_before_2=fb.cleaned_data["export_before_2"],
                fund_before_0=fb.cleaned_data["fund_before_0"],
                fund_before_1=fb.cleaned_data["fund_before_1"],
                fund_before_2=fb.cleaned_data["fund_before_2"],
                fund_before_3=fb.cleaned_data["fund_before_3"],
                fund_before_4=fb.cleaned_data["fund_before_4"],
                fund_before_5=fb.cleaned_data["fund_before_5"],
                fund_before_6=fb.cleaned_data["fund_before_6"],
                fund_before_7=fb.cleaned_data["fund_before_7"],
                fund_before_8=fb.cleaned_data["fund_before_8"],
                fund_before_9=fb.cleaned_data["fund_before_9"],
                fund_before_year_0=fb.cleaned_data["fund_before_year_0"],
                fund_before_year_1=fb.cleaned_data["fund_before_year_1"],
                fund_before_year_2=fb.cleaned_data["fund_before_year_2"],
                fund_before_year_3=fb.cleaned_data["fund_before_year_3"],
                fund_before_year_4=fb.cleaned_data["fund_before_year_4"],
                fund_before_year_5=fb.cleaned_data["fund_before_year_5"],
                fund_before_year_6=fb.cleaned_data["fund_before_year_6"],
                fund_before_year_7=fb.cleaned_data["fund_before_year_7"],
                fund_before_year_8=fb.cleaned_data["fund_before_year_8"],
                fund_before_year_9=fb.cleaned_data["fund_before_year_9"],
                fund_before_agent_0=fb.cleaned_data["fund_before_agent_0"],
                fund_before_agent_1=fb.cleaned_data["fund_before_agent_1"],
                fund_before_agent_2=fb.cleaned_data["fund_before_agent_2"],
                fund_before_agent_3=fb.cleaned_data["fund_before_agent_3"],
                fund_before_agent_4=fb.cleaned_data["fund_before_agent_4"],
                fund_before_agent_5=fb.cleaned_data["fund_before_agent_5"],
                fund_before_agent_6=fb.cleaned_data["fund_before_agent_6"],
                fund_before_agent_7=fb.cleaned_data["fund_before_agent_7"],
                fund_before_agent_8=fb.cleaned_data["fund_before_agent_8"],
                fund_before_agent_9=fb.cleaned_data["fund_before_agent_9"]

            )
            startup.save()
            try:
                startup.thumbnail = request.FILES["FILE_TAG"]
            except:
                pass
            filter_list = request.POST.get("filter_list").split(",")
            for f in filter_list:
                if f != "":
                    startup.filter.add(Filter.objects.get(id=f))
            tag_list = fb.cleaned_data["keyword"].split("#")[1:]
            for t in tag_list:
                tag, created = Tag.objects.get_or_create(name=t)
                startup.tag.add(tag)
        return redirect("company_profile")
    else:
        print("new")
        form_up_basic = NewStartupUp(
            initial={
                "uid": "none"
            }
        )
        form_bot_basic = NewStartupBot
        int_sup = Filter.objects.all().filter(cat_0="지원형태")
        filter_0 = Filter.objects.all().filter(cat_0="기본장르")
        filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
        filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
        filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
        filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
        filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
        filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
        filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
        filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
        filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
        filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
        filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
        filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
        filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
        filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
        filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
        filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
        filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
        filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
        email_confirm=0
        return render(request, "pc/edit_company.html",
                      {"form_basic": form_up_basic, "form_basic_bot": form_bot_basic, "int_sup": int_sup,
                       "filter_0": filter_0,
                       "filter_1": filter_1,
                       "filter_2": filter_2,
                       "filter_3": filter_3,
                       "filter_4": filter_4,
                       "filter_5": filter_5,
                       "filter_6": filter_6,
                       "filter_7": filter_7,
                       "filter_8": filter_8,
                       "filter_9": filter_9,
                       "filter_10": filter_10,
                       "filter_11": filter_11,
                       "filter_12": filter_12,
                       "filter_13": filter_13,
                       "filter_14": filter_14,
                       "filter_15": filter_15,
                       "filter_16": filter_16,
                       "filter_17": filter_17,
                       "filter_18": filter_18,
                       "email_confirm":email_confirm
                       })


def company_profile_edit(request):
    if request.method == "POST":
        fu = NewStartupUp(request.POST)
        fb = NewStartupBot(request.POST)
        if request.method == "POST":
            fu = NewStartupUp(request.POST)
            fb = NewStartupBot(request.POST)
            print(fu)
            print(fb)
            if fu.is_valid() and fb.is_valid():
                startup = Startup.objects.all().get(id=request.POST.get("uid"))
                startup.user = request.user
                startup.name = fu.cleaned_data["name"]
                startup.desc = fb.cleaned_data["desc"]
                startup.established_date = fu.cleaned_data["established_date"]
                startup.category = fu.cleaned_data["category"]
                startup.address_0 = fu.cleaned_data["address_0"]
                startup.address_detail_0 = fu.cleaned_data["address_0_detail"]
                startup.address_0_title = fu.cleaned_data["address_0_title"]
                startup.address_1 = fu.cleaned_data["address_1"]
                startup.address_detail_1 = fu.cleaned_data["address_1_detail"]
                startup.address_1_title = fu.cleaned_data["address_1_title"]
                startup.address_2 = fu.cleaned_data["address_2"]
                startup.address_detail_2 = fu.cleaned_data["address_2_detail"]
                startup.address_2_title = fu.cleaned_data["address_2_title"]
                startup.employee_number = fu.cleaned_data["employee_number"]
                startup.email = fu.cleaned_data["email"]
                startup.website = fu.cleaned_data["website"]
                startup.service_products = fb.cleaned_data["service_products"]
                startup.short_desc = fb.cleaned_data["short_desc"]
                # startup.fund_status = fb.cleaned_data["fund_status"]
                startup.revenue_before_year_0 = fb.cleaned_data["revenue_before_year_0"]
                startup.revenue_before_year_1 = fb.cleaned_data["revenue_before_year_1"]
                startup.revenue_before_year_2 = fb.cleaned_data["revenue_before_year_2"]
                startup.revenue_before_0 = fb.cleaned_data["revenue_before_0"]
                startup.revenue_before_1 = fb.cleaned_data["revenue_before_1"]
                startup.revenue_before_2 = fb.cleaned_data["revenue_before_2"]
                startup.export_before_year_0 = fb.cleaned_data["export_before_year_0"]
                startup.export_before_year_1 = fb.cleaned_data["export_before_year_1"]
                startup.export_before_year_2 = fb.cleaned_data["export_before_year_2"]
                startup.export_before_0 = fb.cleaned_data["export_before_0"]
                startup.export_before_1 = fb.cleaned_data["export_before_1"]
                startup.export_before_2 = fb.cleaned_data["export_before_2"]
                startup.fund_before_0 = fb.cleaned_data["fund_before_0"]
                startup.fund_before_1 = fb.cleaned_data["fund_before_1"]
                startup.fund_before_2 = fb.cleaned_data["fund_before_2"]
                startup.fund_before_3 = fb.cleaned_data["fund_before_3"]
                startup.fund_before_4 = fb.cleaned_data["fund_before_4"]
                startup.fund_before_5 = fb.cleaned_data["fund_before_5"]
                startup.fund_before_6 = fb.cleaned_data["fund_before_6"]
                startup.fund_before_7 = fb.cleaned_data["fund_before_7"]
                startup.fund_before_8 = fb.cleaned_data["fund_before_8"]
                startup.fund_before_9 = fb.cleaned_data["fund_before_9"]
                startup.fund_before_year_0 = fb.cleaned_data["fund_before_year_0"]
                startup.fund_before_year_1 = fb.cleaned_data["fund_before_year_1"]
                startup.fund_before_year_2 = fb.cleaned_data["fund_before_year_2"]
                startup.fund_before_year_3 = fb.cleaned_data["fund_before_year_3"]
                startup.fund_before_year_4 = fb.cleaned_data["fund_before_year_4"]
                startup.fund_before_year_5 = fb.cleaned_data["fund_before_year_5"]
                startup.fund_before_year_6 = fb.cleaned_data["fund_before_year_6"]
                startup.fund_before_year_7 = fb.cleaned_data["fund_before_year_7"]
                startup.fund_before_year_8 = fb.cleaned_data["fund_before_year_8"]
                startup.fund_before_year_9 = fb.cleaned_data["fund_before_year_9"]
                startup.fund_before_agent_0 = fb.cleaned_data["fund_before_agent_0"]
                startup.fund_before_agent_1 = fb.cleaned_data["fund_before_agent_1"]
                startup.fund_before_agent_2 = fb.cleaned_data["fund_before_agent_2"]
                startup.fund_before_agent_3 = fb.cleaned_data["fund_before_agent_3"]
                startup.fund_before_agent_4 = fb.cleaned_data["fund_before_agent_4"]
                startup.fund_before_agent_5 = fb.cleaned_data["fund_before_agent_5"]
                startup.fund_before_agent_6 = fb.cleaned_data["fund_before_agent_6"]
                startup.fund_before_agent_7 = fb.cleaned_data["fund_before_agent_7"]
                startup.fund_before_agent_8 = fb.cleaned_data["fund_before_agent_8"]
                startup.fund_before_agent_9 = fb.cleaned_data["fund_before_agent_9"]
                startup.save()
                filter_list = request.POST.get("filter_list").split(",")
                startup.filter.clear()
                for f in filter_list:
                    if f != "":
                        startup.filter.add(Filter.objects.get(id=f))
                tag_list = fb.cleaned_data["keyword"].split("#")[1:]
                startup.tag.clear()
                for t in tag_list:
                    tag, created = Tag.objects.get_or_create(name=t)
                    startup.tag.add(tag)
            return redirect("company_profile")
    else:
        filter_qs = request.user.startup.filter.all()
        filter_list = [filter_qs.id for filter_qs in filter_qs]
        tag_qs = request.user.startup.tag.all()
        tag_list = [tag_qs.name for tag_qs in tag_qs]
        form_up_basic = NewStartupUp(
            initial={
                "uid": request.user.startup.id,
                "name": request.user.startup.name,
                "established_date": request.user.startup.established_date,
                "category": request.user.startup.category,
                "address_0": request.user.startup.address_0,
                "address_1": request.user.startup.address_1,
                "address_2": request.user.startup.address_2,
                "address_0_title": request.user.startup.address_0_title,
                "address_1_title": request.user.startup.address_1_title,
                "address_2_title": request.user.startup.address_2_title,
                "address_0_detail": request.user.startup.address_detail_0,
                "address_1_detail": request.user.startup.address_detail_1,
                "address_2_detail": request.user.startup.address_detail_2,
                "employee_number": request.user.startup.employee_number,
                "email": request.user.startup.email,
                "website": request.user.startup.website,

            }
        )
        form_bot_basic = NewStartupBot(
            initial={
                "desc": request.user.startup.desc,
                "service_products": request.user.startup.service_products,
                "short_desc": request.user.startup.short_desc,
                "fund_status": request.user.startup.fund_status,
                "export_before_year_0": request.user.startup.export_before_year_0,
                "export_before_year_1": request.user.startup.export_before_year_1,
                "export_before_year_2": request.user.startup.export_before_year_2,
                "export_before_0": request.user.startup.export_before_0,
                "export_before_1": request.user.startup.export_before_1,
                "export_before_2": request.user.startup.export_before_2,
                "revenue_before_0": request.user.startup.revenue_before_0,
                "revenue_before_1": request.user.startup.revenue_before_1,
                "revenue_before_2": request.user.startup.revenue_before_2,
                "revenue_before_year_0": request.user.startup.revenue_before_year_0,
                "revenue_before_year_1": request.user.startup.revenue_before_year_1,
                "revenue_before_year_2": request.user.startup.revenue_before_year_2,
                "fund_before_0": request.user.startup.fund_before_0,
                "fund_before_1": request.user.startup.fund_before_1,
                "fund_before_2": request.user.startup.fund_before_2,
                "fund_before_3": request.user.startup.fund_before_3,
                "fund_before_4": request.user.startup.fund_before_4,
                "fund_before_5": request.user.startup.fund_before_5,
                "fund_before_6": request.user.startup.fund_before_6,
                "fund_before_7": request.user.startup.fund_before_7,
                "fund_before_8": request.user.startup.fund_before_8,
                "fund_before_9": request.user.startup.fund_before_9,
                "fund_before_year_0": request.user.startup.fund_before_year_0,
                "fund_before_year_1": request.user.startup.fund_before_year_1,
                "fund_before_year_2": request.user.startup.fund_before_year_2,
                "fund_before_year_3": request.user.startup.fund_before_year_3,
                "fund_before_year_4": request.user.startup.fund_before_year_4,
                "fund_before_year_5": request.user.startup.fund_before_year_5,
                "fund_before_year_6": request.user.startup.fund_before_year_6,
                "fund_before_year_7": request.user.startup.fund_before_year_7,
                "fund_before_year_8": request.user.startup.fund_before_year_8,
                "fund_before_year_9": request.user.startup.fund_before_year_9,
                "fund_before_agent_0": request.user.startup.fund_before_agent_0,
                "fund_before_agent_1": request.user.startup.fund_before_agent_1,
                "fund_before_agent_2": request.user.startup.fund_before_agent_2,
                "fund_before_agent_3": request.user.startup.fund_before_agent_3,
                "fund_before_agent_4": request.user.startup.fund_before_agent_4,
                "fund_before_agent_5": request.user.startup.fund_before_agent_5,
                "fund_before_agent_6": request.user.startup.fund_before_agent_6,
                "fund_before_agent_7": request.user.startup.fund_before_agent_7,
                "fund_before_agent_8": request.user.startup.fund_before_agent_8,
                "fund_before_agent_9": request.user.startup.fund_before_agent_9,
            }
        )
        int_sup = Filter.objects.all().filter(cat_0="지원형태")
        filter_0 = Filter.objects.all().filter(cat_0="기본장르")
        filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
        filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
        filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
        filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
        filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
        filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
        filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
        filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
        filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
        filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
        filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
        filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
        filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
        filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
        filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
        filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
        filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
        filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
        email_confirm = 0
        if request.user.startup.email != "" and len(
                EmailConfirmation.objects.all().filter(email=request.user.startup.email).filter(confirm=True)) != 0:
            email_confirm = 1
        print(email_confirm)
        return render(request, "pc/edit_company.html", {
            "email_confirm": email_confirm,
            "form_basic": form_up_basic, "form_basic_bot": form_bot_basic,
            "filter_list": filter_list,
            "tag_list": tag_list,
            "int_sup": int_sup,
            "filter_0": filter_0,
            "filter_1": filter_1,
            "filter_2": filter_2,
            "filter_3": filter_3,
            "filter_4": filter_4,
            "filter_5": filter_5,
            "filter_6": filter_6,
            "filter_7": filter_7,
            "filter_8": filter_8,
            "filter_9": filter_9,
            "filter_10": filter_10,
            "filter_11": filter_11,
            "filter_12": filter_12,
            "filter_13": filter_13,
            "filter_14": filter_14,
            "filter_15": filter_15,
            "filter_16": filter_16,
            "filter_17": filter_17,
            "filter_18": filter_18,
        })


def new_apply(request):
    return render(request, "pc/new_apply.html")


def my_profile(request):
    return render(request, "pc/mypage.html")


def my_profile_edit(request):
    if request.method == "POST":
        if request.POST.get("pre_pass") != "":
            if request.POST.get("new_pass") != request.POST.get("pre_pass") :
                user = User.objects.get(id=request.user.id)
                if request.POST.get("new_pass") == request.POST.get("new_pass_conf") and user.check_password(
                        request.POST.get("pre_pass")):
                    user.set_password(request.POST.get("new_pass"))
                    user.save()
                    update_session_auth_hash(request, user)
            else:
                messages.warning(request, "변경하려는 비밀번호가 과거의 비밀번호와 동일합니다.")
                return redirect("my_profile_edit")
        fu = MyPageUp(request.POST)
        fb = MyPageBot(request.POST)
        print(fu)
        print(fb)
        if fu.is_valid() and fb.is_valid():
            if len(AdditionalUserInfo.objects.all().filter(user=request.user)) != 0:
                additionaluserinfo = AdditionalUserInfo.objects.get(id=fu.cleaned_data["uid"])
                additionaluserinfo.name = fu.cleaned_data["name"]
                additionaluserinfo.tel = fb.cleaned_data["tel"]
                additionaluserinfo.agreement = fb.cleaned_data["agreement"]
                additionaluserinfo.additional_email = fb.cleaned_data["additional_email"]
                additionaluserinfo.save();
            else:
                AdditionalUserInfo(
                    user=request.user,
                    name=fu.cleaned_data["name"],
                    tel=fb.cleaned_data["tel"],
                    agreement=fb.cleaned_data["agreement"],
                    additional_email=fb.cleaned_data["additional_email"],
                ).save()
        return redirect("my_profile")


    else:
        if len(AdditionalUserInfo.objects.all().filter(user=request.user)) == 0:
            form_up = MyPageUp(
                initial={
                    "uid": "none"
                }
            )
            form_bot = MyPageBot(
                initial={
                }
            )
            return render(request, "pc/mypage_edit.html", {"fu": form_up, "fb": form_bot})
        else:
            form_up = MyPageUp(
                initial={
                    "name": AdditionalUserInfo.objects.get(user=request.user).name,
                    "uid": AdditionalUserInfo.objects.get(user=request.user).id
                }
            )
            form_bot = MyPageBot(
                initial={
                    "tel": AdditionalUserInfo.objects.get(user=request.user).tel,
                    "additional_email": AdditionalUserInfo.objects.get(user=request.user).additional_email,
                    "agreement": AdditionalUserInfo.objects.get(user=request.user).agreement,
                    "position": AdditionalUserInfo.objects.get(user=request.user).position
                }
            )

            email_confirm = 0
            if AdditionalUserInfo.objects.get(user=request.user).additional_email != "" and len(
                    EmailConfirmation.objects.all().filter(
                        email=AdditionalUserInfo.objects.get(user=request.user).additional_email).filter(
                        confirm=True)) != 0:
                email_confirm = 1
            print(email_confirm)

            return render(request, "pc/mypage_edit.html",
                          {"fu": form_up, "fb": form_bot, "email_confirm": email_confirm})


def manage_mypage(request):
    if request.method == "POST":
        info = AdditionalUserInfo.objects.all().get(user=request.user)
        form_data = ManagerForm(request.POST)
        if form_data.is_valid():
            info.name = form_data.cleaned_data["name"]
            info.position = form_data.cleaned_data["position"]
            info.tel = form_data.cleaned_data["tel"]
            info.web = form_data.cleaned_data["web"]
            info.save()
        return redirect("manage_mypage")

    else:
        add_info = AdditionalUserInfo.objects.all().filter(user=request.user)
        if (len(add_info) != 0):
            form = ManagerForm(initial={
                "name": add_info[0].name,
                "position": add_info[0].position,
                "tel": add_info[0].tel,
                "web": add_info[0].web
            })
            # 정보가 있다면
        else:
            # 정보가 없으면
            form = ManagerForm
        return render(request, 'pc/manager_mypage.html', {"form": form})


@login_required
def manage_support(request):
    try:
        if request.user.additionaluserinfo.category == "1":
            qs = SupportBusiness.objects.all().filter(author=request.user)
            return render(request, "pc/manage_support_list.html", {"qs": qs})
        else:
            return HttpResponse('권한 없음.')
    except Exception as e:
        print(e)
        return HttpResponse('권한 없음.')


def search(request):
    today_min = datetime.datetime.now()
    if request.user.is_authenticated:
        interest = request.user.additionaluserinfo.interest.all()
    else:
        interest = ""
    num_0 = len(
        SupportBusiness.objects.filter(filter__cat_1="자금지원").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_1 = len(
        SupportBusiness.objects.filter(filter__cat_1="엑셀러레이팅 투자연계").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_2 = len(
        SupportBusiness.objects.filter(filter__cat_1="교육").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_3 = len(
        SupportBusiness.objects.filter(filter__cat_1="판로").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_4 = len(
        SupportBusiness.objects.filter(filter__cat_1="네트워킹").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_5 = len(
        SupportBusiness.objects.filter(filter__cat_1="기타지원").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    num_6 = len(
        SupportBusiness.objects.filter(filter__cat_1="공간지원").filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min))
    try:
        cat = request.GET.get("cat", "")
        print(cat)
        if cat == "0":
            qs = SupportBusiness.objects.filter(filter__cat_1="자금지원").filter(is_blind=False).filter(
                open_status=1).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "1":
            qs = SupportBusiness.objects.filter(filter__cat_1="엑셀러레이팅 투자연계").filter(is_blind=False).filter(
                open_status=1).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "2":
            qs = SupportBusiness.objects.filter(filter__cat_1="교육").filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "3":
            qs = SupportBusiness.objects.filter(filter__cat_1="판로").filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "4":
            qs = SupportBusiness.objects.filter(filter__cat_1="네트워킹").filter(open_status=1).filter(
                is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "5":
            qs = SupportBusiness.objects.filter(filter__cat_1="기타지원").filter(open_status=1).filter(
                is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "6":
            qs = SupportBusiness.objects.filter(filter__cat_1="공간지원").filter(open_status=1).filter(
                is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
        elif cat == "":
            qs = SupportBusiness.objects.all().order_by("-id").filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
    except Exception as e:
        qs = SupportBusiness.objects.all().order_by("-id")
    return render(request, 'pc/search.html', {
        "num_0": num_0,
        "num_1": num_1,
        "num_2": num_2,
        "num_3": num_3,
        "num_4": num_4,
        "num_5": num_5,
        "num_6": num_6,
        "qs": qs,
        "interest": interest
    })



def qs_su(qs, filter_set):
    sp = qs

    for s in sp:
        k = list(set((s.filter.all())).intersection(filter_set))
        s.k_val = len(k)
        print(s.k_val)
    sp =sorted(sp, key=lambda q: (q.k_val) , reverse=True)
    final_sp = []
    for q in sp:
        if q.k_val != 0:
            final_sp.append(q)

    pk_list = []

    for q in final_sp:
        pk_list.append(q.id)

    clauses = ' '.join(
        ['WHEN supporting_business_supportbusiness.id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
    ordering = 'CASE %s END' % clauses
    queryset = SupportBusiness.objects.filter(pk__in=pk_list).extra(select={'ordering': ordering},
                                                                    order_by=('ordering',))
    sp = queryset

    return sp;

def support_list(request):
    today_min = datetime.datetime.now()
    if request.user.is_authenticated:
        interest = request.user.additionaluserinfo.interest.all()
    else:
        interest = ""

    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
    filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
    filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
    filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
    filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
    filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
    filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
    filter_19 = Filter.objects.all().filter(cat_0="지원형태", cat_1="피칭")
    if request.GET.get("cat", "") == "":
        if request.GET.get("filter", "") == "":
            sp = SupportBusiness.objects.filter(open_status=1).filter(apply_start__lt=today_min).filter(is_blind=False).filter(apply_end__gt=today_min)
            if request.GET.get("em", "") != "":
                sp = sp.filter(employee_num__gte=request.GET.get("em"))
            if request.GET.get("q") != "":
                q = request.GET.get("q", "")
                sp = sp.filter(Q(title__contains=q) | Q(short_desc__contains=q) | Q(object__contains=q) | Q(
                    condition__contains=q) | Q(prefer__contains=q) | Q(condition__contains=q)).distinct()
            all = len(sp.distinct())
            num_0 = len(sp.filter(filter__cat_1="자금지원").distinct())
            num_1 = len(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct())
            num_2 = len(sp.filter(filter__cat_1="교육").distinct())
            num_3 = len(sp.filter(filter__cat_1="판로").distinct())
            num_4 = len(sp.filter(filter__cat_1="네트워킹").distinct())
            num_5 = len(sp.filter(filter__cat_1="기타지원").distinct())
            num_6 = len(sp.filter(filter__cat_1="공간지원").distinct())
            num_7 = len(sp.filter(filter__cat_1="피칭").distinct())
            qs_0 = sp.filter(filter__cat_1="자금지원").distinct()
            qs_1 = sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct()
            qs_2 = sp.filter(filter__cat_1="교육").distinct()
            qs_3 = sp.filter(filter__cat_1="판로").distinct()
            qs_4 = sp.filter(filter__cat_1="네트워킹").distinct()
            qs_5 = sp.filter(filter__cat_1="공간지원").distinct()
            qs_6 = sp.filter(filter__cat_1="기타지원").distinct()
            qs_7 = sp.filter(filter__cat_1="피칭").distinct()
            detail_0 = len(sp.filter(filter__id=48).distinct())
            detail_1 = len(sp.filter(filter__id=49).distinct())
            detail_2 = len(sp.filter(filter__id=50).distinct())
            detail_3 = len(sp.filter(filter__id=51).distinct())
            detail_4 = len(sp.filter(filter__id=52).distinct())
            detail_5 = len(sp.filter(filter__id=53).distinct())
            detail_6 = len(sp.filter(filter__id=54).distinct())
            detail_7 = len(sp.filter(filter__id=55).distinct())
            detail_8 = len(sp.filter(filter__id=56).distinct())
            detail_9 = len(sp.filter(filter__id=57).distinct())
            detail_10 = len(sp.filter(filter__id=58).distinct())
            detail_11 = len(sp.filter(filter__id=64).distinct())
            detail_12 = len(sp.filter(filter__id=65).distinct())
            detail_13 = len(sp.filter(filter__id=59).distinct())
            detail_14 = len(sp.filter(filter__id=60).distinct())
            detail_15 = len(sp.filter(filter__id=61).distinct())
            detail_16 = len(sp.filter(filter__id=62).distinct())
            detail_17 = len(sp.filter(filter__id=63).distinct())
            detail_18 = len(sp.filter(filter__id=68).distinct())
            detail_19 = len(sp.filter(filter__id=70).distinct())
            return render(request, 'pc/search_filter.html',
                          {"all": all,
                           "interest": interest,
                           "filter_0": filter_0, "filter_1": filter_1, "filter_2": filter_2,
                           "filter_3": filter_3, "filter_4": filter_4, "filter_5": filter_5,
                           "filter_6": filter_6, "filter_7": filter_7, "filter_8": filter_8,
                           "filter_9": filter_9, "filter_10": filter_10, "filter_11": filter_11,
                           "filter_12": filter_12, "filter_13": filter_13, "filter_14": filter_14,
                           "filter_15": filter_15, "filter_16": filter_16, "filter_17": filter_17,
                           "filter_18": filter_18, "filter_19": filter_19, "num_0": num_0, "num_1": num_1,
                           "num_2": num_2, "num_3": num_3, "num_4": num_4,
                           "num_5": num_5, "num_6": num_6, "qs_0": qs_0, "num_7": num_7,
                           "qs_1": qs_1,
                           "qs_2": qs_2,
                           "qs_3": qs_3,
                           "qs_4": qs_4,
                           "qs_5": qs_5,
                           "qs_6": qs_6, "qs_7": qs_7,
                           "detail_0": detail_0,
                           "detail_1": detail_1,
                           "detail_2": detail_2,
                           "detail_3": detail_3,
                           "detail_4": detail_4,
                           "detail_5": detail_5,
                           "detail_6": detail_6,
                           "detail_7": detail_7,
                           "detail_8": detail_8,
                           "detail_9": detail_9,
                           "detail_10": detail_10,
                           "detail_11": detail_11,
                           "detail_12": detail_12,
                           "detail_13": detail_13,
                           "detail_14": detail_14,
                           "detail_15": detail_15,
                           "detail_16": detail_16,
                           "detail_17": detail_17,
                           "detail_18": detail_18,
                           "detail_19": detail_19,
                           }
                          )
        else:  # 필터를 선택한 경우
            q_objects = Q()
            sp = SupportBusiness.objects.all().filter(open_status=1).filter(apply_start__lt=today_min).filter(
                is_blind=False).filter(apply_end__gt=today_min)
            filter_string = request.GET.get("filter", "").split(",")
            em = request.GET.get("em")
            if em == "":
                em = 0
            if len(filter_string) != 0:
                sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
                    apply_start__lt=today_min).filter(apply_end__gt=today_min)
                filter_arr = []
                for t in filter_string:
                    try:
                        filter_arr.append(Filter.objects.get(id=t))
                    except:
                        print("pass")

                if em != 0:
                    sp.filter(Q(employee_num__gte=int(em)) | Q(employee_num=int(0)))
            else:
                if em != 0:
                    sp.filter(Q(employee_num__gte=int(em)) | Q(employee_num=int(0)))
            if request.GET.get("q") != "":
                q = request.GET.get("q", "")
                sp = sp.filter(Q(title__contains=q) | Q(short_desc__contains=q) | Q(object__contains=q) | Q(
                    condition__contains=q) | Q(prefer__contains=q) | Q(condition__contains=q))

            all = len(qs_su(sp.distinct(), filter_arr))
            num_0 = len(qs_su(sp.filter(filter__cat_1="자금지원").distinct()                        , filter_arr)          )
            num_1 = len(qs_su(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct()                  , filter_arr)         )
            num_2 = len(qs_su(sp.filter(filter__cat_1="교육").distinct()     , filter_arr)         )
            num_3 = len(qs_su(sp.filter(filter__cat_1="판로").distinct()     , filter_arr)         )
            num_4 = len(qs_su(sp.filter(filter__cat_1="네트워킹").distinct()   , filter_arr)         )
            num_5 = len(qs_su(sp.filter(filter__cat_1="기타지원").distinct()   , filter_arr)         )
            num_6 = len(qs_su(sp.filter(filter__cat_1="공간지원").distinct()   , filter_arr)         )
            detail_0 = len(qs_su(sp.filter(filter__id=48).distinct()      , filter_arr)    )
            detail_1 = len(qs_su(sp.filter(filter__id=49).distinct()      , filter_arr)    )
            detail_2 = len(qs_su(sp.filter(filter__id=50).distinct()      , filter_arr)    )
            detail_3 = len(qs_su(sp.filter(filter__id=51).distinct()      , filter_arr)    )
            detail_4 = len(qs_su(sp.filter(filter__id=52).distinct()      , filter_arr)    )
            detail_5 = len(qs_su(sp.filter(filter__id=53).distinct()      , filter_arr)    )
            detail_6 = len(qs_su(sp.filter(filter__id=54).distinct()      , filter_arr)    )
            detail_7 = len(qs_su(sp.filter(filter__id=55).distinct()      , filter_arr)    )
            detail_8 = len(qs_su(sp.filter(filter__id=56).distinct()      , filter_arr)    )
            detail_9 = len(qs_su(sp.filter(filter__id=57).distinct()      , filter_arr)    )
            detail_10 = len(qs_su(sp.filter(filter__id=58).distinct()     , filter_arr)    )
            detail_11 = len(qs_su(sp.filter(filter__id=64).distinct()     , filter_arr)    )
            detail_12 = len(qs_su(sp.filter(filter__id=65).distinct()     , filter_arr)    )
            detail_13 = len(qs_su(sp.filter(filter__id=59).distinct()     , filter_arr)    )
            detail_14 = len(qs_su(sp.filter(filter__id=60).distinct()     , filter_arr)    )
            detail_15 = len(qs_su(sp.filter(filter__id=61).distinct()     , filter_arr)    )
            detail_16 = len(qs_su(sp.filter(filter__id=62).distinct()     , filter_arr)    )
            detail_17 = len(qs_su(sp.filter(filter__id=63).distinct()     , filter_arr)    )
            detail_18 = len(qs_su(sp.filter(filter__id=68).distinct()     , filter_arr)    )
            detail_19 = len(qs_su(sp.filter(filter__id=70).distinct()     , filter_arr)    )

            try:
                qs_0 =qs_su(sp.filter(filter__cat_1="자금지원").distinct()                   ,filter_arr)
                qs_1 =qs_su(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct()            ,filter_arr)
                qs_2 =qs_su(sp.filter(filter__cat_1="교육").distinct()                     ,filter_arr)
                qs_3 =qs_su(sp.filter(filter__cat_1="판로").distinct()                     ,filter_arr)
                qs_4 =qs_su(sp.filter(filter__cat_1="네트워킹").distinct()                   ,filter_arr)
                qs_5 =qs_su(sp.filter(filter__cat_1="공간지원").distinct()                   ,filter_arr)
                qs_6 =qs_su(sp.filter(filter__cat_1="기타지원").distinct()                   ,filter_arr)

            except:
                qs = SupportBusiness.objects.all().order_by("-id").filter(is_blind=False).filter(open_status=True)

            return render(request, 'pc/search_filter.html',
                          {"all": all,
                           "interest": interest,
                           "filter_0": filter_0, "filter_1": filter_1,
                           "filter_2": filter_2, "filter_3": filter_3, "filter_4": filter_4,
                           "filter_5": filter_5, "filter_6": filter_6, "filter_7": filter_7,
                           "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10,
                           "filter_11": filter_11, "filter_12": filter_12, "filter_13": filter_13,
                           "filter_14": filter_14, "filter_15": filter_15, "filter_16": filter_16,
                           "filter_17": filter_17, "filter_18": filter_18, "num_0": num_0,
                           "num_1": num_1, "num_2": num_2, "num_3": num_3,
                           "num_4": num_4, "num_5": num_5, "num_6": num_6,
                           "qs_0": qs_0,
                           "qs_1": qs_1,
                           "qs_2": qs_2,
                           "qs_3": qs_3,
                           "qs_4": qs_4,
                           "qs_5": qs_5,
                           "qs_6": qs_6,
                           "detail_0": detail_0,
                           "detail_1": detail_1,
                           "detail_2": detail_2,
                           "detail_3": detail_3,
                           "detail_4": detail_4,
                           "detail_5": detail_5,
                           "detail_6": detail_6,
                           "detail_7": detail_7,
                           "detail_8": detail_8,
                           "detail_9": detail_9,
                           "detail_10": detail_10,
                           "detail_11": detail_11,
                           "detail_12": detail_12,
                           "detail_13": detail_13,
                           "detail_14": detail_14,
                           "detail_15": detail_15,
                           "detail_16": detail_16,
                           "detail_17": detail_17,  "detail_18": detail_18,  "detail_19": detail_19,
                           }
                          )

    elif request.GET.get("cat", "-1") != "-1":
        filter_string = request.GET.get("filter", "").split(",")
        em = request.GET.get("em")
        if em == "":
            em = 0
        sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min)
        if len(filter_string) != 0 and filter_string != [""]:
            sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)
            filter_arr = []
            for t in filter_string:
                try:
                    filter_arr.append(Filter.objects.get(id=t))
                except:
                    print("pass")
            #if em != 0:
            #    sp.filter(Q(employee_num__gte=em) | Q(employee_num=0))
        else:
            sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
                apply_start__lt=today_min).filter(apply_end__gt=today_min)

            filter_arr=[]
            for f in Filter.objects.all():
                filter_arr.append(f)
        if request.GET.get("q") != "":
            q = request.GET.get("q", "")
            sp = sp.filter(
                Q(title__contains=q) | Q(short_desc__contains=q) | Q(object__contains=q) | Q(condition__contains=q) | Q(
                    prefer__contains=q) | Q(condition__contains=q))
        print(len(sp))
        all = len(qs_su(sp.distinct(),filter_arr))
        num_0 = len(qs_su(sp.filter(filter__cat_1="자금지원").distinct()                    , filter_arr)           )
        num_1 = len(qs_su(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct()             , filter_arr)           )
        num_2 = len(qs_su(sp.filter(filter__cat_1="교육").distinct()                    , filter_arr)             )
        num_3 = len(qs_su(sp.filter(filter__cat_1="판로").distinct()                      , filter_arr)           )
        num_4 = len(qs_su(sp.filter(filter__cat_1="네트워킹").distinct()                     , filter_arr)           )
        num_5 = len(qs_su(sp.filter(filter__cat_1="기타지원").distinct()                    , filter_arr)           )
        num_6 = len(qs_su(sp.filter(filter__cat_1="공간지원").distinct()                    , filter_arr)           )
        num_7 = len(qs_su(sp.filter(filter__cat_1="피칭").distinct()                      , filter_arr)           )
        detail_0 = len(qs_su(sp.filter(filter__id=48).distinct()  , filter_arr)         )
        detail_1 = len(qs_su(sp.filter(filter__id=49).distinct()  , filter_arr)         )
        detail_2 = len(qs_su(sp.filter(filter__id=50).distinct()  , filter_arr)         )
        detail_3 = len(qs_su(sp.filter(filter__id=51).distinct()  , filter_arr)         )
        detail_4 = len(qs_su(sp.filter(filter__id=52).distinct()  , filter_arr)         )
        detail_5 = len(qs_su(sp.filter(filter__id=53).distinct()  , filter_arr)         )
        detail_6 = len(qs_su(sp.filter(filter__id=54).distinct()  , filter_arr)         )
        detail_7 = len(qs_su(sp.filter(filter__id=55).distinct()  , filter_arr)         )
        detail_8 = len(qs_su(sp.filter(filter__id=56).distinct()  , filter_arr)         )
        detail_9 = len(qs_su(sp.filter(filter__id=57).distinct()  , filter_arr)         )
        detail_10 = len(qs_su(sp.filter(filter__id=58).distinct()    , filter_arr)      )
        detail_11 = len(qs_su(sp.filter(filter__id=64).distinct()    , filter_arr)      )
        detail_12 = len(qs_su(sp.filter(filter__id=65).distinct()    , filter_arr)      )
        detail_13 = len(qs_su(sp.filter(filter__id=59).distinct()    , filter_arr)      )
        detail_14 = len(qs_su(sp.filter(filter__id=60).distinct()    , filter_arr)      )
        detail_15 = len(qs_su(sp.filter(filter__id=61).distinct()    , filter_arr)      )
        detail_16 = len(qs_su(sp.filter(filter__id=62).distinct()    , filter_arr)      )
        detail_17 = len(qs_su(sp.filter(filter__id=63).distinct()    , filter_arr)      )
        detail_18 = len(qs_su(sp.filter(filter__id=68).distinct()    , filter_arr)      )
        detail_19 = len(qs_su(sp.filter(filter__id=70).distinct()    , filter_arr)      )
        print("들어가기전")
        print(len(sp))
        if request.GET.get("cat") == "0":
            cat = "자금지원"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "1":
            cat = "엑셀러레이팅 투자연계"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "2":
            cat = "교육"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "3":
            cat = "판로"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "4":
            cat = "네트워킹"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "5":
            cat = "공간지원"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)

        elif request.GET.get("cat") == "7":
            cat = "피칭"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "6":
            cat = "기타지원"
            fs = Filter.objects.all().filter(cat_1=cat)
            qs = qs_su(sp.filter(filter__cat_1=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "1_1":
            cat = "자금지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "1_2":
            cat = "R&D지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "2_1":
            cat = "엑셀러레이팅 프로그램"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "2_2":
            cat = "데모데이 프로그램(투자연계)"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "3_1":
            cat = "교육 프로그램"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "3_2":
            cat = "전문가 양성 프로그램"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "4_1":
            cat = "해외 진출 지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "4_2":
            cat = "전시회 참가지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "4_3":
            cat = "유통지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "5_1":
            cat = "네트워킹 프로그램"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "5_2":
            cat = "전문가 컨설팅&멘토링"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "5_3":
            cat = "데모데이 프로그램(네트워킹)"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "6_1":
            cat = "스타트업 오피스 지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "6_2":
            cat = "가상오피스 지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "7_1":
            cat = "기업피칭"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "8_1":
            cat = "마케팅지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "8_2":
            cat = "퍼블리싱 지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)

        elif request.GET.get("cat") == "8_3":
            cat = "B2B 상담 지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)

        elif request.GET.get("cat") == "8_4":
            cat = "번역지원"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)
        elif request.GET.get("cat") == "8_5":
            cat = "공간/장비"
            fs = Filter.objects.all().filter(name=cat)
            qs = qs_su(sp.filter(filter__name=cat).distinct(), filter_arr)


        return render(request, 'pc/search_support.html',
                      {"all": all,
                       "interest": interest,
                       "fs": fs, "filter_0": filter_0, "filter_1": filter_1,
                       "filter_2": filter_2, "filter_3": filter_3, "filter_4": filter_4,
                       "filter_5": filter_5, "filter_6": filter_6, "filter_7": filter_7,
                       "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10,
                       "filter_11": filter_11, "filter_12": filter_12, "filter_13": filter_13,
                       "filter_14": filter_14, "filter_15": filter_15, "filter_16": filter_16,
                       "filter_17": filter_17, "filter_18": filter_18, "num_0": num_0,
                       "num_1": num_1, "num_2": num_2, "num_3": num_3,
                       "num_4": num_4, "num_5": num_5, "num_6": num_6, "num_7": num_7,
                       "qs": qs,
                       "detail_0": detail_0,
                       "detail_1": detail_1,
                       "detail_2": detail_2,
                       "detail_3": detail_3,
                       "detail_4": detail_4,
                       "detail_5": detail_5,
                       "detail_6": detail_6,
                       "detail_7": detail_7,
                       "detail_8": detail_8,
                       "detail_9": detail_9,
                       "detail_10": detail_10,
                       "detail_11": detail_11,
                       "detail_12": detail_12,
                       "detail_13": detail_13,
                       "detail_14": detail_14,
                       "detail_15": detail_15,
                       "detail_16": detail_16,
                       "detail_17": detail_17,
                       "detail_18": detail_18, "detail_19": detail_19,
                       }
                      )


def company_profile(request):
    if len(Startup.objects.all().filter(user=request.user)) != 0:
        return render(request, "pc/company_profile.html")
    else:
        return redirect("company_profile_new")


@receiver(user_signed_up)
def social_user_added_test_2(request, user, sociallogin, **kwargs):
    if sociallogin.account.provider == "naver":
        email = sociallogin.account.extra_data["email"]
        name = sociallogin.account.extra_data["name"]
    if sociallogin.account.provider == "kakao":
        name = sociallogin.account.extra_data["properties"]["nickname"]
        email = sociallogin.account.extra_data["kaccount_email"]
    if sociallogin.account.provider == "facebook":
        print(sociallogin.account.extra_data)
        email = sociallogin.account.extra_data["email"]
        name = sociallogin.account.extra_data["name"]
    user.username = email
    user.save()

    AdditionalUserInfo(user=user, name=name).save()
    print(user)


@receiver(social_account_added)
def social_user_added_test(request, sociallogin, **kwargs):
    print(inspect.getmembers(sociallogin.account.provider))
    if sociallogin.account.provider == "naver":
        print("네이버로 로그인 하였습니다.")
    if sociallogin.account.provider == "Kakao":
        print("카카오로 로그인 하였습니다.")

    print("hello!")


@receiver(pre_social_login)
def pre_social_user_added(request, sociallogin, **kwargs):
    print(request)
    try:
        print(inspect.getmembers(sociallogin))
        print(inspect.getmembers(sociallogin.account))
        print(sociallogin.account.extra_data)
    except:
        pass


def pdfver_support(request, id):
    support = get_object_or_404(SupportBusiness, id=id)
    return render(request, "pc/pdf_support_detail.html", {"support": support})


import subprocess
import os.path


def pdf(request, id):
    # config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    # pdf = pdfkit.from_url('http://gconnect.kr/pdfver_support/' + str(id), False, configuration=config, options= {'javascript-delay':'1000',"load-error-handling":"ignore"})
    url = "http://gconnect.kr/pdfver_support/" + str(id)
    subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf", shell=True, check=True)
    print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
    with open(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="result.pdf"'
        k = k + 1
        return response


def profile_thumbnail(request):
    addinfo = AdditionalUserInfo.objects.all().get(user=request.user)
    addinfo.avatar = request.FILES["FILE_TAG"]
    addinfo.save()
    string = (addinfo.avatar.url)
    return HttpResponse(string)


def company_thumbnail(request):
    print("here2")
    print(request.POST)
    print(request.FILES)
    startup = Startup.objects.get(user=request.user)
    startup.thumbnail = request.FILES["fileObj"]
    startup.save()
    string = (startup.thumbnail.url)
    return HttpResponse(string)


def matching(request):
    num_0 = len(
        SupportBusiness.objects.filter(filter__cat_1="자금지원").filter(open_status=1))
    num_1 = len(
        SupportBusiness.objects.filter(filter__cat_1="엑셀러레이팅 투자연계").filter(open_status=1))
    num_2 = len(
        SupportBusiness.objects.filter(filter__cat_1="교육").filter(open_status=1))
    num_3 = len(
        SupportBusiness.objects.filter(filter__cat_1="판로").filter(open_status=1))
    num_4 = len(
        SupportBusiness.objects.filter(filter__cat_1="네트워킹").filter(open_status=1))
    num_5 = len(
        SupportBusiness.objects.filter(filter__cat_1="기타지원").filter(open_status=1))
    num_6 = len(
        SupportBusiness.objects.filter(filter__cat_1="공간지원").filter(open_status=1))
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
    filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
    filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
    filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
    filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
    filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
    filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")

    return render(request, "pc/matching.html",
                  {
                      "filter_0": filter_0,
                      "filter_1": filter_1,
                      "filter_2": filter_2,
                      "filter_3": filter_3,
                      "filter_4": filter_4,
                      "filter_5": filter_5,
                      "filter_6": filter_6,
                      "filter_7": filter_7,
                      "filter_8": filter_8,
                      "filter_9": filter_9,
                      "filter_10": filter_10,
                      "filter_11": filter_11,
                      "filter_12": filter_12,
                      "filter_13": filter_13,
                      "filter_14": filter_14,
                      "filter_15": filter_15,
                      "filter_16": filter_16,
                      "filter_17": filter_17,
                      "filter_18": filter_18,
                      "num_0": num_0,
                      "num_1": num_1,
                      "num_2": num_2,
                      "num_3": num_3,
                      "num_4": num_4,
                      "num_5": num_5,
                      "num_6": num_6,
                      "qs": qs
                  })


import string
import random

@csrf_exempt
def signup(request):
    print(request.is_ajax())
    if request.is_ajax():
        print("here")
        if request.POST.get("type") == "confirm":
            target = request.POST.get("val")
            random_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            try:
                send_mail(
                '[G-connect] 인증메일입니다.',
                '인증코드는 [' + random_code + "] 입니다.",
                'neogelon@gmail.com',
                [target],
                fail_silently=False,
                )
                EmailConfirmation(
                    email=target,
                    confirmation_code=random_code
                ).save()
                return HttpResponse("ok")
            except Exception as e:
                print(e)
                return HttpResponse("none")

        elif request.POST.get("type") == "confirm2":
            if EmailConfirmation.objects.all().filter(email=request.POST.get("target")).order_by("-id")[
                0].confirmation_code == request.POST.get("confirmation_code"):
                EmailConfirmation.objects.all().filter(email=request.POST.get("target")).update(confirm = True)

                return HttpResponse("ok")
            else:
                return HttpResponse("no")

    if request.method == "POST":
        form = LoginForm(request.POST)


        if form.is_valid() and \
                        EmailConfirmation.objects.all().filter(email=form.cleaned_data["username"]).order_by("-id")[
                            0].confirmation_code == request.POST.get("confirmation_code"):
            user = User.objects.create_user(username=form.cleaned_data["username"],
                                            password=form.cleaned_data["password"])
            EmailConfirmation.objects.all().filter(email=form.cleaned_data["username"]).order_by("-id")[0].confirm = True
            if user is not None:

                AdditionalUserInfo(user=user).save()
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])

                if user is not None:
                    login(request, user)

                    messages.success(request, '회원님 환영합니다!')
                return redirect("/")
            else:
                return False
    else:
        form = LoginForm
    return render(request, "pc/accounts/signup.html", {"form": form})


def category(request, category):
    today_min = datetime.datetime.now()
    try:
        interest = request.user.additionaluserinfo.interest.all()
    except:
        interest = ""
    startup = Startup.objects.get(user=request.user);
    filter_string = request.user.startup.filter.all()
    k = []
    for f in filter_string:
        k.append(str(f.id))
    startup = Startup.objects.get(user=request.user);
    startup_filter = startup.filter.all()
    q_obj = Q()
    em = startup.employee_number
    if em == None or em == "":
        em = 0
    sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(apply_start__lt=today_min).filter(apply_end__gt=today_min)
    if len(startup_filter) != 0:
        print("here")
        filter_string = request.user.startup.filter.all()
        em = request.user.startup.employee_number
        if em == None or em == "":
            em = 0;
        sp = SupportBusiness.objects.all().filter(open_status=1).filter(is_blind=False).filter(
            apply_start__lt=today_min).filter(apply_end__gt=today_min)
        startup = Startup.objects.get(user=request.user)

    else:
        sp=sp.filter(id__lt=0)
    result = {}
    if category == "finance":
        result["fs"] = Filter.objects.all().filter(cat_1="자금지원")
        result["qs"] = qs_al(sp.filter(filter__cat_1="자금지원").distinct(), startup, request.user)
    if category == "accel":
        result["fs"] = Filter.objects.all().filter(cat_1="엑셀러레이팅 투자연계")
        result["qs"] = qs_al(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct(), startup, request.user)
    if category == "edu":
        result["fs"] = Filter.objects.all().filter(cat_1="교육")
        result["qs"] = qs_al(sp.filter(filter__cat_1="교육").distinct(), startup, request.user)
    if category == "channel":
        result["fs"] = Filter.objects.all().filter(cat_1="판로")
        result["qs"] = qs_al(sp.filter(filter__cat_1="판로").distinct(), startup, request.user)
    if category == "network":
        result["fs"] = Filter.objects.all().filter(cat_1="네트워킹")
        result["qs"] = qs_al(sp.filter(filter__cat_1="네트워킹").distinct(), startup, request.user)
    if category == "space":
        result["fs"] = Filter.objects.all().filter(cat_1="공간지원")
        result["qs"] = qs_al(sp.filter(filter__cat_1="공간지원").distinct(), startup, request.user)
    if category == "piching":
        result["fs"] = Filter.objects.all().filter(cat_1="피칭")
        result["qs"] = qs_al(sp.filter(filter__cat_1="피칭").distinct(), startup, request.user)
    if category == "etc":
        result["fs"] = Filter.objects.all().filter(cat_1="기타지원")
        result["qs"] = qs_al(sp.filter(filter__cat_1="기타지원").distinct(), startup, request.user)
    final = "final"
    sb_total = len(result["qs"])
    sb_0 = qs_al(sp.filter(filter__cat_1="자금지원").distinct()        , startup, request.user)
    sb_1 = qs_al(sp.filter(filter__cat_1="엑셀러레이팅 투자연계").distinct() , startup, request.user)
    sb_2 = qs_al(sp.filter(filter__cat_1="교육").distinct()          , startup, request.user)
    sb_3 = qs_al(sp.filter(filter__cat_1="판로").distinct()          , startup, request.user)
    sb_4 = qs_al(sp.filter(filter__cat_1="네트워킹").distinct()        , startup, request.user)
    sb_5 = qs_al(sp.filter(filter__cat_1="공간지원").distinct()        , startup, request.user)
    sb_6 = qs_al(sp.filter(filter__cat_1="기타지원").distinct()        , startup, request.user)
    sb_7 = qs_al(sp.filter(filter__cat_1="피칭").distinct()          , startup, request.user)
    many_view = SupportBusiness.objects.filter(open_status=1).filter(is_blind=False).filter(
        apply_start__lt=today_min).filter(apply_end__gt=today_min).order_by("-hit").distinct()[:3]
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
    filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
    filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
    filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
    filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
    filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
    filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
    filter_19 = Filter.objects.all().filter(cat_0="지원형태", cat_1="피칭")
    final = "final"
    random = SupportBusiness.objects.all().filter(is_blind=False).filter(open_status=True).filter(
        apply_start__lt=today_min).filter(apply_end__gt=today_min).order_by("?").distinct()[:3]
    return render(request, "pc/category.html",
                  {"result": result, "final": final, "sb_total": sb_total,
                   "filter_string": ",".join(k),
                   "sb_0": sb_0, "sb_1": sb_1, "sb_2": sb_2, "sb_3": sb_3, "interest": interest,
                   "sb_4": sb_4, "sb_5": sb_5, "sb_6": sb_6, "sb_7": sb_7, "many_view": many_view,
                   "filter_0": filter_0,
                   "filter_1": filter_1,
                   "filter_2": filter_2,
                   "filter_3": filter_3,
                   "filter_4": filter_4,
                   "filter_5": filter_5,
                   "filter_6": filter_6,
                   "filter_7": filter_7,
                   "filter_8": filter_8,
                   "filter_9": filter_9,
                   "filter_10": filter_10,
                   "filter_11": filter_11,
                   "filter_12": filter_12,
                   "filter_13": filter_13,
                   "filter_14": filter_14,
                   "filter_15": filter_15,
                   "filter_16": filter_16,
                   "filter_17": filter_17,
                   "filter_18": filter_18, "filter_19": filter_19,
                   "random": random,
                   })


def category_last_depth(request, category, id):
    today_min = datetime.datetime.now()
    startup = Startup.objects.get(user=request.user);
    startup_filter = startup.filter.all()
    q_obj = Q()
    if len(startup_filter) != 0:
        for filter in startup_filter:
            if filter.id < 48:
                q_obj |= Q(filter__id=filter.id)
    else:
        q_obj |= Q(filter__id__gte=0)
    sb_total = SupportBusiness.objects.filter(open_status=1).filter(apply_start__lt=today_min).filter(
        is_blind=False).filter(q_obj).distinct()
    sb_0 = SupportBusiness.objects.filter(filter__cat_1="자금지원").filter(open_status=1).filter(
        apply_start__lt=today_min).filter(is_blind=False).filter(q_obj).distinct()
    sb_1 = SupportBusiness.objects.filter(filter__cat_1="엑셀러레이팅 투자연계").filter(open_status=1).filter(
        apply_start__lt=today_min).filter(is_blind=False).filter(q_obj).distinct()
    sb_2 = SupportBusiness.objects.filter(filter__cat_1="교육").filter(open_status=1).filter(
        apply_start__lt=today_min).filter(is_blind=False).filter(q_obj).distinct()
    sb_3 = SupportBusiness.objects.filter(filter__cat_1="판로").filter(open_status=1).filter(
        apply_start__lt=today_min).filter(is_blind=False).filter(q_obj).distinct()
    sb_4 = SupportBusiness.objects.filter(filter__cat_1="네트워킹").filter(apply_start__lt=today_min).filter(
        is_blind=False).filter(q_obj).distinct()
    sb_5 = SupportBusiness.objects.filter(filter__cat_1="공간지원").filter(apply_start__lt=today_min).filter(
        is_blind=False).filter(q_obj).distinct()
    sb_6 = SupportBusiness.objects.filter(filter__cat_1="기타지원").filter(apply_start__lt=today_min).filter(
        is_blind=False).filter(q_obj).distinct()
    result = {}
    result["fs"] = Filter.objects.all().filter(id=id)
    result["qs"] = SupportBusiness.objects.all().filter(apply_start__lt=today_min).filter(is_blind=False).filter(
        filter__id=id)
    final = "final"
    print(sb_0)
    return render(request, "pc/category.html", {"result": result, "final": final, "sb_total": sb_total,
                                                "sb_0": sb_0, "sb_1": sb_1, "sb_2": sb_2, "sb_3": sb_3,
                                                "sb_4": sb_4, "sb_5": sb_5, "sb_6": sb_6,
                                                })


def apply(request, id):
    today_min = datetime.datetime.now()
    if request.method == "POST":
        print("this")
        form = ApplianceForm(request.POST, request.FILES)
        print(request.POST)
        print(request.FILES)
        if form.is_valid() and SupportBusiness.objects.get(id=id).apply_end > today_min:
            ap = form.save(commit=True)
            print(ap)
            print( form.cleaned_data["total_employ"] )

            ap.sb = SupportBusiness.objects.get(id=id)
            ap.startup = request.user.startup
            ap.save()
            s = Startup.objects.get(user=request.user)
            s.name = form.cleaned_data["name"] if form.cleaned_data["name"] is not None and form.cleaned_data["name"]!="" else  s.name
            s.established_date = form.cleaned_data["found_date"] if form.cleaned_data["found_date"] is not None and form.cleaned_data["found_date"]!="" else s.established_date
            s.address_0 = form.cleaned_data["address"] if form.cleaned_data["address"] is not None and form.cleaned_data["address"] !="" else s.address_0
            s.category = form.cleaned_data["service_category"]  if  form.cleaned_data["service_category"] is not None and  form.cleaned_data["service_category"] !="" else s.category
            s.user.additionaluserinfo.name = form.cleaned_data["repre_name"] if  form.cleaned_data["repre_name"] is not None and form.cleaned_data["repre_name"] != "" else  s.user.additionaluserinfo.name
            s.user.additionaluserinfo.tel = form.cleaned_data["repre_tel"] if form.cleaned_data["repre_tel"] is not None  and form.cleaned_data["repre_tel"]!="" else s.user.additionaluserinfo.tel
            s.user.additionaluserinfo.username = form.cleaned_data["repre_email"] if form.cleaned_data["repre_email"] is not None and form.cleaned_data["repre_email"] !="" else s.user.additionaluserinfo.username
            s.user.startup.website = form.cleaned_data["website"] if  form.cleaned_data["website"] is not None  and form.cleaned_data["website"]!="" else s.user.startup.website
            s.service_products = form.cleaned_data["service_intro"] if form.cleaned_data["service_intro"] is not None and form.cleaned_data["service_intro"]!="" else s.service_products
            s.desc = form.cleaned_data["intro"] if form.cleaned_data["intro"] is not None and  form.cleaned_data["intro"]!="" else  s.desc

            s.employee_number = form.cleaned_data["total_employ"] if  form.cleaned_data["total_employ"] is not None and form.cleaned_data["total_employ"]!="" else s.employee_number
            s.export_before_year_0 = form.cleaned_data["export_before_year_0"] if  form.cleaned_data["export_before_year_0"] is not None and form.cleaned_data["export_before_year_0"]!="" else s.export_before_year_0
            s.export_before_year_1 = form.cleaned_data["export_before_year_1"] if  form.cleaned_data["export_before_year_1"] is not None and form.cleaned_data["export_before_year_1"]!="" else s.export_before_year_1
            s.export_before_year_2 = form.cleaned_data["export_before_year_2"] if  form.cleaned_data["export_before_year_2"] is not None and form.cleaned_data["export_before_year_2"]!="" else s.export_before_year_2
            s.export_before_0 = form.cleaned_data["export_before_0"]  if   form.cleaned_data["export_before_0"]  is not None and     form.cleaned_data["export_before_0"] !="" else  s.export_before_0
            s.export_before_1 = form.cleaned_data["export_before_1"]  if   form.cleaned_data["export_before_1"]  is not None and     form.cleaned_data["export_before_1"] !="" else s.export_before_1
            s.export_before_2 = form.cleaned_data["export_before_2"]  if   form.cleaned_data["export_before_2"]  is not None and     form.cleaned_data["export_before_2"] !="" else s.export_before_2
            s.revenue_before_0 = form.cleaned_data["revenue_before_0"] if  form.cleaned_data["revenue_before_0"] is not None and     form.cleaned_data["revenue_before_0"]!="" else s.revenue_before_0
            s.revenue_before_1 = form.cleaned_data["revenue_before_1"] if  form.cleaned_data["revenue_before_1"] is not None and     form.cleaned_data["revenue_before_1"]!="" else s.revenue_before_1
            s.revenue_before_2 = form.cleaned_data["revenue_before_2"] if  form.cleaned_data["revenue_before_2"] is not None and     form.cleaned_data["revenue_before_2"]!="" else s.revenue_before_2
            s.revenue_before_year_0 = form.cleaned_data["revenue_before_year_0"]  if  form.cleaned_data["revenue_before_year_0"]  is not None and form.cleaned_data["revenue_before_year_0"] !="" else   s.revenue_before_year_0
            s.revenue_before_year_1 = form.cleaned_data["revenue_before_year_1"]  if  form.cleaned_data["revenue_before_year_1"]  is not None and form.cleaned_data["revenue_before_year_1"] !="" else   s.revenue_before_year_1
            s.revenue_before_year_2 = form.cleaned_data["revenue_before_year_2"]  if  form.cleaned_data["revenue_before_year_2"]  is not None and form.cleaned_data["revenue_before_year_2"] !="" else   s.revenue_before_year_2
            s.fund_before_0 = form.cleaned_data["fund_before_0"]    if form.cleaned_data["fund_before_0"] is not None and form.cleaned_data["fund_before_0"] != "" else   s.fund_before_0
            s.fund_before_1 = form.cleaned_data["fund_before_1"]    if form.cleaned_data["fund_before_1"] is not None and form.cleaned_data["fund_before_1"] != "" else   s.fund_before_1
            s.fund_before_2 = form.cleaned_data["fund_before_2"]    if form.cleaned_data["fund_before_2"] is not None and form.cleaned_data["fund_before_2"] != "" else   s.fund_before_2
            s.fund_before_3 = form.cleaned_data["fund_before_3"]    if form.cleaned_data["fund_before_3"] is not None and form.cleaned_data["fund_before_3"] != "" else   s.fund_before_3
            s.fund_before_4 = form.cleaned_data["fund_before_4"]    if form.cleaned_data["fund_before_4"] is not None and form.cleaned_data["fund_before_4"] != "" else   s.fund_before_4
            s.fund_before_5 = form.cleaned_data["fund_before_5"]    if form.cleaned_data["fund_before_5"] is not None and form.cleaned_data["fund_before_5"] != "" else   s.fund_before_5
            s.fund_before_6 = form.cleaned_data["fund_before_6"]    if form.cleaned_data["fund_before_6"] is not None and form.cleaned_data["fund_before_6"] != "" else   s.fund_before_6
            s.fund_before_7 = form.cleaned_data["fund_before_7"]    if form.cleaned_data["fund_before_7"] is not None and form.cleaned_data["fund_before_7"] != "" else   s.fund_before_7
            s.fund_before_8 = form.cleaned_data["fund_before_8"]    if form.cleaned_data["fund_before_8"] is not None and form.cleaned_data["fund_before_8"] != "" else   s.fund_before_8
            s.fund_before_9 = form.cleaned_data["fund_before_9"]    if form.cleaned_data["fund_before_9"] is not None and form.cleaned_data["fund_before_9"] != "" else   s.fund_before_9
            s.fund_before_year_0 = form.cleaned_data["fund_before_year_0"]    if  form.cleaned_data["fund_before_year_0"]  is not None and form.cleaned_data["fund_before_year_0"] !="" else  s.fund_before_year_0
            s.fund_before_year_1 = form.cleaned_data["fund_before_year_1"]    if  form.cleaned_data["fund_before_year_1"]  is not None and form.cleaned_data["fund_before_year_1"] !="" else  s.fund_before_year_1
            s.fund_before_year_2 = form.cleaned_data["fund_before_year_2"]    if  form.cleaned_data["fund_before_year_2"]  is not None and form.cleaned_data["fund_before_year_2"] !="" else  s.fund_before_year_2
            s.fund_before_year_3 = form.cleaned_data["fund_before_year_3"]    if  form.cleaned_data["fund_before_year_3"]  is not None and form.cleaned_data["fund_before_year_3"] !="" else  s.fund_before_year_3
            s.fund_before_year_4 = form.cleaned_data["fund_before_year_4"]    if  form.cleaned_data["fund_before_year_4"]  is not None and form.cleaned_data["fund_before_year_4"] !="" else  s.fund_before_year_4
            s.fund_before_year_5 = form.cleaned_data["fund_before_year_5"]    if  form.cleaned_data["fund_before_year_5"]  is not None and form.cleaned_data["fund_before_year_5"] !="" else  s.fund_before_year_5
            s.fund_before_year_6 = form.cleaned_data["fund_before_year_6"]    if  form.cleaned_data["fund_before_year_6"]  is not None and form.cleaned_data["fund_before_year_6"] !="" else  s.fund_before_year_6
            s.fund_before_year_7 = form.cleaned_data["fund_before_year_7"]    if  form.cleaned_data["fund_before_year_7"]  is not None and form.cleaned_data["fund_before_year_7"] !="" else  s.fund_before_year_7
            s.fund_before_year_8 = form.cleaned_data["fund_before_year_8"]    if  form.cleaned_data["fund_before_year_8"]  is not None and form.cleaned_data["fund_before_year_8"] !="" else  s.fund_before_year_8
            s.fund_before_year_9 = form.cleaned_data["fund_before_year_9"]    if  form.cleaned_data["fund_before_year_9"]  is not None and form.cleaned_data["fund_before_year_9"] !="" else  s.fund_before_year_9
            s.fund_before_agent_0 = form.cleaned_data["fund_before_agent_0"]  if  form.cleaned_data["fund_before_agent_0"] is not None and form.cleaned_data["fund_before_agent_0"]!="" else   s.fund_before_agent_0
            s.fund_before_agent_1 = form.cleaned_data["fund_before_agent_1"]  if  form.cleaned_data["fund_before_agent_1"] is not None and form.cleaned_data["fund_before_agent_1"]!="" else   s.fund_before_agent_1
            s.fund_before_agent_2 = form.cleaned_data["fund_before_agent_2"]  if  form.cleaned_data["fund_before_agent_2"] is not None and form.cleaned_data["fund_before_agent_2"]!="" else   s.fund_before_agent_2
            s.fund_before_agent_3 = form.cleaned_data["fund_before_agent_3"]  if  form.cleaned_data["fund_before_agent_3"] is not None and form.cleaned_data["fund_before_agent_3"]!="" else   s.fund_before_agent_3
            s.fund_before_agent_4 = form.cleaned_data["fund_before_agent_4"]  if  form.cleaned_data["fund_before_agent_4"] is not None and form.cleaned_data["fund_before_agent_4"]!="" else   s.fund_before_agent_4
            s.fund_before_agent_5 = form.cleaned_data["fund_before_agent_5"]  if  form.cleaned_data["fund_before_agent_5"] is not None and form.cleaned_data["fund_before_agent_5"]!="" else   s.fund_before_agent_5
            s.fund_before_agent_6 = form.cleaned_data["fund_before_agent_6"]  if  form.cleaned_data["fund_before_agent_6"] is not None and form.cleaned_data["fund_before_agent_6"]!="" else   s.fund_before_agent_6
            s.fund_before_agent_7 = form.cleaned_data["fund_before_agent_7"]  if  form.cleaned_data["fund_before_agent_7"] is not None and form.cleaned_data["fund_before_agent_7"]!="" else   s.fund_before_agent_7
            s.fund_before_agent_8 = form.cleaned_data["fund_before_agent_8"]  if  form.cleaned_data["fund_before_agent_8"] is not None and form.cleaned_data["fund_before_agent_8"]!="" else   s.fund_before_agent_8
            s.fund_before_agent_9 = form.cleaned_data["fund_before_agent_9"]  if  form.cleaned_data["fund_before_agent_9"] is not None and form.cleaned_data["fund_before_agent_9"]!="" else   s.fund_before_agent_9
            s.save()
            for filter in s.filter.all():
                print(filter.name)
                if (filter.cat_0 != "지원형태"):
                    s.filter.remove(filter)
            print(request.POST.get("filter"))
            for filter in request.POST.get("filter").split(","):
                try:
                    print(filter)
                    s.filter.add(Filter.objects.get(id=filter))
                    print(s.filter.all())
                except:
                    print("error")
            if request.is_ajax():
                return HttpResponse(reverse("apply_edit", kwargs={"id": ap.id, "sbid": ap.sb_id}) + "?status=s")
            else:
                return redirect(reverse("apply_edit", kwargs={"id": ap.id, "sbid": ap.sb_id}) + "?status=s")

    if request.user.is_authenticated:
        # SupportBusiness.objects.get(id=id).applicant.add(request.user.startup)
        sp = SupportBusiness.objects.get(id=id)
        form = ApplianceForm(initial={
            "name": request.user.startup.name,
            "found_date": request.user.startup.established_date,
            "address": request.user.startup.address_0,
            "repre_name": request.user.additionaluserinfo.name,
            "repre_tel": request.user.additionaluserinfo.tel,
            "repre_email": request.user.username,
            "website": request.user.startup.website,
            "service_intro": request.user.startup.service_products,
            "intro": request.user.startup.desc,
            "total_employ": request.user.startup.employee_number,
            "service_category": request.user.startup.category,
            "export_before_year_0": request.user.startup.export_before_year_0,
            "export_before_year_1": request.user.startup.export_before_year_1,
            "export_before_year_2": request.user.startup.export_before_year_2,
            "export_before_0": request.user.startup.export_before_0,
            "export_before_1": request.user.startup.export_before_1,
            "export_before_2": request.user.startup.export_before_2,
            "revenue_before_0": request.user.startup.revenue_before_0,
            "revenue_before_1": request.user.startup.revenue_before_1,
            "revenue_before_2": request.user.startup.revenue_before_2,
            "revenue_before_year_0": request.user.startup.revenue_before_year_0,
            "revenue_before_year_1": request.user.startup.revenue_before_year_1,
            "revenue_before_year_2": request.user.startup.revenue_before_year_2,
            "fund_before_0": request.user.startup.fund_before_0,
            "fund_before_1": request.user.startup.fund_before_1,
            "fund_before_2": request.user.startup.fund_before_2,
            "fund_before_3": request.user.startup.fund_before_3,
            "fund_before_4": request.user.startup.fund_before_4,
            "fund_before_5": request.user.startup.fund_before_5,
            "fund_before_6": request.user.startup.fund_before_6,
            "fund_before_7": request.user.startup.fund_before_7,
            "fund_before_8": request.user.startup.fund_before_8,
            "fund_before_9": request.user.startup.fund_before_9,
            "fund_before_year_0": request.user.startup.fund_before_year_0,
            "fund_before_year_1": request.user.startup.fund_before_year_1,
            "fund_before_year_2": request.user.startup.fund_before_year_2,
            "fund_before_year_3": request.user.startup.fund_before_year_3,
            "fund_before_year_4": request.user.startup.fund_before_year_4,
            "fund_before_year_5": request.user.startup.fund_before_year_5,
            "fund_before_year_6": request.user.startup.fund_before_year_6,
            "fund_before_year_7": request.user.startup.fund_before_year_7,
            "fund_before_year_8": request.user.startup.fund_before_year_8,
            "fund_before_year_9": request.user.startup.fund_before_year_9,
            "fund_before_agent_0": request.user.startup.fund_before_agent_0,
            "fund_before_agent_1": request.user.startup.fund_before_agent_1,
            "fund_before_agent_2": request.user.startup.fund_before_agent_2,
            "fund_before_agent_3": request.user.startup.fund_before_agent_3,
            "fund_before_agent_4": request.user.startup.fund_before_agent_4,
            "fund_before_agent_5": request.user.startup.fund_before_agent_5,
            "fund_before_agent_6": request.user.startup.fund_before_agent_6,
            "fund_before_agent_7": request.user.startup.fund_before_agent_7,
            "fund_before_agent_8": request.user.startup.fund_before_agent_8,
            "fund_before_agent_9": request.user.startup.fund_before_agent_9,
        })
        submit = "false"
        recent_ap = Appliance.objects.all().filter(startup=request.user.startup)
        filter_string = request.user.startup.filter.all()
        k = []
        for f in filter_string:
            k.append(str(f.id))
        filter_0 = Filter.objects.all().filter(cat_0="기본장르")
        filter_1 = Filter.objects.all().filter(cat_0="영역")
        filter_2 = Filter.objects.all().filter(cat_1="기업형태")
    return render(request, "pc/apply.html",
                  {"support": sp, "filter_string": ",".join(k), "submit": submit, "form": form, "filter_0": filter_0,
                   "filter_1": filter_1, "filter_2": filter_2,
                   "save_status": "false",
                   "recent_ap": recent_ap})


def apply_edit(request, id, sbid):
    today_min = datetime.datetime.now()
    if request.GET.get("status") == "s":
        save_status = "true"
        submit = "false"
    else:
        submit = "false"
        save_status = "false"
    if request.method == "POST":
        ap = ApplianceForm(request.POST, request.FILES, instance=Appliance.objects.get(id=id))
        form = ApplianceForm(request.POST, request.FILES, instance=Appliance.objects.get(id=id))
        print(form.is_valid())
        if ap.is_valid() and SupportBusiness.objects.get(id=sbid).apply_end > today_min:
            model = ap.save(commit=False)
            model.sb_id = sbid
            model.save()
            model.startup = request.user.startup
            model.save()
            print(form.cleaned_data["total_employ"])

            s = Startup.objects.get(user=request.user)
            s.name = form.cleaned_data["name"] if form.cleaned_data["name"] is not None and form.cleaned_data["name"]!="" else  s.name
            s.established_date = form.cleaned_data["found_date"] if form.cleaned_data[
                                                                        "found_date"] is not None and form.cleaned_data["found_date"]!="" else s.established_date
            s.address_0 = form.cleaned_data["address"] if form.cleaned_data["address"] is not None and form.cleaned_data["address"] !="" else s.address_0
            s.category = form.cleaned_data["service_category"] if form.cleaned_data["service_category"] is not None and form.cleaned_data["service_category"]!="" else s.category
            s.user.additionaluserinfo.name = form.cleaned_data["repre_name"] if form.cleaned_data["repre_name"] is not None and form.cleaned_data["repre_name"]!="" else  s.user.additionaluserinfo.name
            s.user.additionaluserinfo.tel = form.cleaned_data["repre_tel"] if form.cleaned_data["repre_tel"] is not None and form.cleaned_data["repre_tel"]!="" else s.user.additionaluserinfo.tel
            s.user.additionaluserinfo.username = form.cleaned_data["repre_email"] if form.cleaned_data["repre_email"] is not None and  form.cleaned_data["repre_email"] !="" else s.user.additionaluserinfo.username
            s.user.startup.website = form.cleaned_data["website"] if form.cleaned_data["website"] is not None and form.cleaned_data["website"]!="" else  s.user.startup.website
            s.service_products = form.cleaned_data["service_intro"] if form.cleaned_data["service_intro"] is not None and  form.cleaned_data["service_intro"]!="" else s.service_products
            s.desc = form.cleaned_data["intro"] if form.cleaned_data["intro"] is not None and  form.cleaned_data["intro"]!="" else  s.desc
            s.employee_number = form.cleaned_data["total_employ"] if form.cleaned_data["total_employ"] is not None and form.cleaned_data["total_employ"]!= "" else s.employee_number
            s.export_before_year_0 = form.cleaned_data["export_before_year_0"] if form.cleaned_data["export_before_year_0"] is not None  and form.cleaned_data["export_before_year_0"] !="" else s.export_before_year_0
            s.export_before_year_1 = form.cleaned_data["export_before_year_1"] if form.cleaned_data["export_before_year_1"] is not None and form.cleaned_data["export_before_year_1"]!="" else s.export_before_year_1
            s.export_before_year_2 = form.cleaned_data["export_before_year_2"] if form.cleaned_data["export_before_year_2"] is not None and form.cleaned_data["export_before_year_2"] !="" else  s.export_before_year_2
            s.export_before_0 = form.cleaned_data["export_before_0"] if form.cleaned_data["export_before_0"] is not None else  s.export_before_0
            s.export_before_1 = form.cleaned_data["export_before_1"] if form.cleaned_data["export_before_1"] is not None else  s.export_before_1
            s.export_before_2 = form.cleaned_data["export_before_2"] if form.cleaned_data["export_before_2"] is not None else  s.export_before_2
            s.revenue_before_0 = form.cleaned_data["revenue_before_0"] if form.cleaned_data["revenue_before_0"] is not None else  s.revenue_before_0
            s.revenue_before_1 = form.cleaned_data["revenue_before_1"] if form.cleaned_data["revenue_before_1"] is not None else  s.revenue_before_1
            s.revenue_before_2 = form.cleaned_data["revenue_before_2"] if form.cleaned_data["revenue_before_2"] is not None else  s.revenue_before_2
            s.revenue_before_year_0 = form.cleaned_data["revenue_before_year_0"] if form.cleaned_data[ "revenue_before_year_0"] is not None else   s.revenue_before_year_0
            s.revenue_before_year_1 = form.cleaned_data["revenue_before_year_1"] if form.cleaned_data["revenue_before_year_1"] is not None else   s.revenue_before_year_1
            s.revenue_before_year_2 = form.cleaned_data["revenue_before_year_2"] if form.cleaned_data["revenue_before_year_2"] is not None else   s.revenue_before_year_2
            s.fund_before_0 = form.cleaned_data["fund_before_0"] if form.cleaned_data["fund_before_0"] is not None else   s.fund_before_0
            s.fund_before_1 = form.cleaned_data["fund_before_1"] if form.cleaned_data["fund_before_1"] is not None else   s.fund_before_1
            s.fund_before_2 = form.cleaned_data["fund_before_2"] if form.cleaned_data["fund_before_2"] is not None else   s.fund_before_2
            s.fund_before_3 = form.cleaned_data["fund_before_3"] if form.cleaned_data["fund_before_3"] is not None else   s.fund_before_3
            s.fund_before_4 = form.cleaned_data["fund_before_4"] if form.cleaned_data["fund_before_4"] is not None else   s.fund_before_4
            s.fund_before_5 = form.cleaned_data["fund_before_5"] if form.cleaned_data["fund_before_5"] is not None else   s.fund_before_5
            s.fund_before_6 = form.cleaned_data["fund_before_6"] if form.cleaned_data["fund_before_6"] is not None else   s.fund_before_6
            s.fund_before_7 = form.cleaned_data["fund_before_7"] if form.cleaned_data["fund_before_7"] is not None else   s.fund_before_7
            s.fund_before_8 = form.cleaned_data["fund_before_8"] if form.cleaned_data["fund_before_8"] is not None else   s.fund_before_8
            s.fund_before_9 = form.cleaned_data["fund_before_9"] if form.cleaned_data["fund_before_9"] is not None else   s.fund_before_9
            s.fund_before_year_0 = form.cleaned_data["fund_before_year_0"] if form.cleaned_data["fund_before_year_0"] is not None else  s.fund_before_year_0
            s.fund_before_year_1 = form.cleaned_data["fund_before_year_1"] if form.cleaned_data["fund_before_year_1"] is not None else  s.fund_before_year_1
            s.fund_before_year_2 = form.cleaned_data["fund_before_year_2"] if form.cleaned_data["fund_before_year_2"] is not None else  s.fund_before_year_2
            s.fund_before_year_3 = form.cleaned_data["fund_before_year_3"] if form.cleaned_data["fund_before_year_3"] is not None else  s.fund_before_year_3
            s.fund_before_year_4 = form.cleaned_data["fund_before_year_4"] if form.cleaned_data["fund_before_year_4"] is not None else  s.fund_before_year_4
            s.fund_before_year_5 = form.cleaned_data["fund_before_year_5"] if form.cleaned_data["fund_before_year_5"] is not None else  s.fund_before_year_5
            s.fund_before_year_6 = form.cleaned_data["fund_before_year_6"] if form.cleaned_data["fund_before_year_6"] is not None else  s.fund_before_year_6
            s.fund_before_year_7 = form.cleaned_data["fund_before_year_7"] if form.cleaned_data["fund_before_year_7"] is not None else  s.fund_before_year_7
            s.fund_before_year_8 = form.cleaned_data["fund_before_year_8"] if form.cleaned_data["fund_before_year_8"] is not None else  s.fund_before_year_8
            s.fund_before_year_9 = form.cleaned_data["fund_before_year_9"] if form.cleaned_data["fund_before_year_9"] is not None else  s.fund_before_year_9
            s.fund_before_agent_0 = form.cleaned_data["fund_before_agent_0"] if form.cleaned_data["fund_before_agent_0"] is not None else   s.fund_before_agent_0
            s.fund_before_agent_1 = form.cleaned_data["fund_before_agent_1"] if form.cleaned_data["fund_before_agent_1"] is not None else   s.fund_before_agent_1
            s.fund_before_agent_2 = form.cleaned_data["fund_before_agent_2"] if form.cleaned_data["fund_before_agent_2"] is not None else   s.fund_before_agent_2
            s.fund_before_agent_3 = form.cleaned_data["fund_before_agent_3"] if form.cleaned_data["fund_before_agent_3"] is not None else   s.fund_before_agent_3
            s.fund_before_agent_4 = form.cleaned_data["fund_before_agent_4"] if form.cleaned_data["fund_before_agent_4"] is not None else   s.fund_before_agent_4
            s.fund_before_agent_5 = form.cleaned_data["fund_before_agent_5"] if form.cleaned_data["fund_before_agent_5"] is not None else   s.fund_before_agent_5
            s.fund_before_agent_6 = form.cleaned_data["fund_before_agent_6"] if form.cleaned_data["fund_before_agent_6"] is not None else   s.fund_before_agent_6
            s.fund_before_agent_7 = form.cleaned_data["fund_before_agent_7"] if form.cleaned_data["fund_before_agent_7"] is not None else   s.fund_before_agent_7
            s.fund_before_agent_8 = form.cleaned_data["fund_before_agent_8"] if form.cleaned_data["fund_before_agent_8"] is not None else   s.fund_before_agent_8
            s.fund_before_agent_9 = form.cleaned_data["fund_before_agent_9"] if form.cleaned_data["fund_before_agent_9"] is not None else   s.fund_before_agent_9
            s.save()
            if request.POST.get("is_submit") == "true":
                model.is_submit = 1
                model.save()
                save_status = "true"
                submit = "true"
            for filter in s.filter.all():
                if (filter.cat_0 != "지원형태"):
                    s.filter.remove(filter)
            for filter in request.POST.get("filter").split(","):
                try:
                    s.filter.add(Filter.objects.get(id=filter))
                except:
                    print("error")

    filter_string = request.user.startup.filter.all()
    k = []
    for f in filter_string:
        k.append(str(f.id))

    recent_ap = Appliance.objects.all().filter(startup=request.user.startup).exclude(id=id)
    form = ApplianceForm(instance=Appliance.objects.get(id=id))
    sp = SupportBusiness.objects.get(id=Appliance.objects.get(id=id).sb_id)
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    filter_2 = Filter.objects.all().filter(cat_1="기업형태")
    return render(request, "pc/apply.html",
                  {"support": sp, "save_status": save_status, "id": id, "submit": submit, "filter_string": ",".join(k),
                   "form": form, "filter_2": filter_2, "filter_0": filter_0, "filter_1": filter_1,
                   "recent_ap": recent_ap})


def add_interest(request):
    if request.user.is_authenticated:
        if SupportBusiness.objects.get(
                id=request.POST.get("val")) not in request.user.additionaluserinfo.interest.all():
            request.user.additionaluserinfo.interest.add(SupportBusiness.objects.get(id=request.POST.get("val")))
            return HttpResponse("ok-add")
        else:
            request.user.additionaluserinfo.interest.remove(SupportBusiness.objects.get(id=request.POST.get("val")))
            return HttpResponse("ok-remove")


def manager(request):
    if request.user.is_authenticated() and (
                    request.user.additionaluserinfo.auth == "4" or request.user.additionaluserinfo.auth == "5"):
        return render(request, "pc/manager/manager_account.html")
    else:
        return redirect("index")


def manager_edit(request):
    if request.user.is_authenticated:
        if request.user.additionaluserinfo.auth != "4" and request.user.additionaluserinfo.auth != "5":
            return redirect("index")
    else:
        return redirect("login")
    if request.method == "POST":
        form_data = ManagerAccountForm(request.POST)
        if form_data.is_valid():
            target = AdditionalUserInfo.objects.get(user=request.user)
            target.name = form_data.cleaned_data["name"]
            target.tel = form_data.cleaned_data["tel"]
            target.department = form_data.cleaned_data["department"]
            target.belong_to = form_data.cleaned_data["belong_to"]
            target.position = form_data.cleaned_data["position"]
            target.web = form_data.cleaned_data["web"]
            target.save()
            return redirect("manager")
    form_ac = ManagerAccountForm(initial={
        "name": request.user.additionaluserinfo.name,
        "tel": request.user.additionaluserinfo.tel,
        "department": request.user.additionaluserinfo.department,
        "belong_to": request.user.additionaluserinfo.belong_to,
        "position": request.user.additionaluserinfo.position,
        "web": request.user.additionaluserinfo.web
    })
    return render(request, "pc/manager/manager_account_edit.html", {"form": form_ac})


def total(request):
    qs = SupportBusiness.objects.order_by("-id").distinct()
    return render(request, "pc/manager/total.html", {"qs": qs})


def sb_list(request):
    today_min = datetime.datetime.now()
    qs_0 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(open_status=0).filter(
        confirm=False).filter(complete=False)
    qs_0_1 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(open_status=0).filter(
        confirm=True)
    qs_0_3 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(open_status=1).filter(
        confirm=False).filter(apply_start__gt=today_min)
    qs_1 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(open_status=1).filter(
        apply_end__gt=today_min).filter(apply_start__lt=today_min)
    qs_2 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(open_status=1).filter(
        complete=0).filter(apply_end__lt=today_min)
    qs_3 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(complete=1)
    qs_4 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo)
    qs_5 = SupportBusiness.objects.all().filter(user=request.user.additionaluserinfo).filter(is_blind=True)

    return render(request, "pc/manager/sb_manage_list.html",
                  {"qs_0_1": qs_0_1, "qs_0": qs_0, "qs_1": qs_1, "qs_2": qs_2, "qs_3": qs_3, "qs_4": qs_4,
                   "qs_0_3": qs_0_3,"qs_5":qs_5,
                   "cat": request.GET.get("cat")})


def sb_list_all(request):
    print("here!!!")
    today_min = datetime.datetime.now()
    cat = request.GET.get("cat","0")
    if request.user.additionaluserinfo.auth=="5":
        son_list = request.user.additionaluserinfo.additionaluserinfo_set.all()
        print(son_list)
        son_pk_list = []
        q_obj = Q()
        for son in son_list:
            q_obj |= Q(confirm_list__id=son.id)
        qs_b = SupportBusiness.objects.all().exclude(confirm_list__id = request.user.additionaluserinfo.id).filter(
            q_obj).distinct()|SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__gt=today_min).filter(apply_start__lt=today_min).filter(is_blind=True).filter(q_obj).distinct()|SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()|\
        SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__lt=today_min).filter(
            is_blind=True).distinct() | SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()|SupportBusiness.objects.all().filter(complete=True).filter(apply_end__lt=today_min).filter(is_blind=True).distinct()|SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()

        if cat == "0":
            qs = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__gt=today_min).filter(apply_start__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__gt=today_min).filter(apply_start__lt=today_min).filter(is_blind=True).filter(q_obj).distinct()|SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()

        if cat=="1":
            qs = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__lt=today_min).filter(is_blind=True).distinct()|SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()

        if cat == "2":
            qs = SupportBusiness.objects.all().filter(complete=True).filter(apply_end__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(complete=True).filter(apply_end__lt=today_min).filter(is_blind=True).distinct()|SupportBusiness.objects.all().filter(confirm=True).filter(q_obj).distinct()

        if cat == "3":
            qs = SupportBusiness.objects.all().filter(q_obj).distinct()
            qs_b = qs_b
    elif request.user.additionaluserinfo.auth=="4":
        son_list=request.user.additionaluserinfo.additionaluserinfo_set.all()|AdditionalUserInfo.objects.all().filter(name=request.user.additionaluserinfo.name)

        son_pk_list=[]
        q_obj = Q()
        q_obj |= Q(confirm_list__id=request.user.additionaluserinfo.id)
        for son in son_list:
            son_pk_list.append(son.id)
            q_obj |= Q(confirm_list__id=son.id)
        qs_b = SupportBusiness.objects.all().exclude(confirm_list__id=request.user.additionaluserinfo.id).filter(q_obj)

        if cat == "0":
            qs = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__gt=today_min).filter(
                apply_start__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__gt=today_min).filter(
                apply_start__lt=today_min).filter(is_blind=True).filter(q_obj).distinct()
        if cat == "1":
            qs = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(open_status=True).filter(apply_end__lt=today_min).filter(
                is_blind=True).filter(q_obj).distinct()

        if cat == "2":
            qs = SupportBusiness.objects.all().filter(complete=True).filter(apply_end__lt=today_min).filter(q_obj).distinct()
            qs_b = SupportBusiness.objects.all().filter(complete=True).filter(apply_end__lt=today_min).filter(
                is_blind=True).filter(q_obj).distinct()
        if cat == "3":
            qs = SupportBusiness.objects.all().filter(confirm_list__in = son_list).filter(q_obj).distinct()

            #qs = SupportBusiness.objects.all().exclude(Q(complete=False) & Q(open_status=False) & Q(confirm=False))
            qs_b = qs_b.filter(confirm=True).filter(q_obj).distinct()
    return render(request, "pc/manager/sb_manage_list_"+cat+".html",
                  {"qs":qs,"qs_b":qs_b})


def sb_detail(request, id):
    applicant = Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id))
    sp = SupportBusiness.objects.get(id=id)
    sp = SupportBusiness.objects.get(id=id)
    sp_inter = AdditionalUserInfo.objects.all().filter(interest=sp)
    hitlog = []
    date_arr = []
    applog = []
    for k in range(1, 30):
        from_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k + 1)
        to_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k)
        date_arr.append(from_da.isoformat().split("T")[0])
        hitlog.append(len(HitLog.objects.all().filter(date__gt=to_da).filter(sb=sp).filter(date__lte=from_da)))
        applog.append(
            len(Appliance.objects.all().filter(sb=sp).filter(update_at__gt=to_da).filter(update_at__lt=from_da)))
    ap_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 != "소재지" and f.cat_1 != "기업형태":
                ap_filter.append(f.name)
    ap_dict = {i: ap_filter.count(i) for i in ap_filter}
    local_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 == "소재지":
                local_filter.append(f.name)
    local_dict = {i: local_filter.count(i) for i in local_filter}
    case_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 == "기업형태":
                case_filter.append(f.name)
    case_dict = {i: case_filter.count(i) for i in case_filter}

    return render(request, "pc/manager/sn_manage_detail.html",
                  {"ap": applicant, "sp": sp, "inter": sp_inter, "filter_pi": ap_dict, "local_filter_pi": local_dict,
                   "case_filter_pi": case_dict,
                   "hitlog": hitlog, "date_arr": date_arr, "applog": applog})


def sb_detail_pdf(request, id):
    applicant = Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id))
    sp = SupportBusiness.objects.get(id=id)
    sp_inter = AdditionalUserInfo.objects.all().filter(interest=sp)




    return render(request, "pc/manager/sn_manage_detail_pdf.html", {"ap": applicant, "support": sp, "inter": sp_inter})


from django.db.models import Sum
from django.db.models.functions import Coalesce

from oauth2client.service_account import ServiceAccountCredentials
import os
def dashboard(request):
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

    #KEY_FILEPATH = 'c:/gcaprj.json'
    KEY_FILEPATH = '/home/ubuntu/workspace/supporting_business/gcaprj.json'

    key = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILEPATH, SCOPE).get_access_token().access_token
    print(key)
    today_min = datetime.datetime.now()
    total = len(SupportBusiness.objects.all().filter(Q(open_status=1) | Q(complete=1)))

    ing = len(SupportBusiness.objects.all().filter(open_status=1).filter(apply_end__gte=today_min).filter(
        apply_start__lt=today_min).filter(is_blind=False))
    #진행중인사업

    # 사업당 참가 기업수 평균 : 지원서 / 사업수
    # 사업당 선정 기업수 평균 : award 갯수 / 사업수
    avg_apply_ent = len(Appliance.objects.all()) / total
    avg_award_ent = len(Award.objects.all()) / total


    total_startup = len(Startup.objects.all())  # 총 기업회원수
    total_person = len(AdditionalUserInfo.objects.all().exclude(Q(auth="4") | Q(auth=5)))
    avg_apply = len(Appliance.objects.all()) / total_startup
    # 기업회원 1개당 평균 사업 참가수
    avg_award = len(Award.objects.all()) / total_startup

    qs_0 = SupportBusiness.objects.all().filter(open_status=False).filter(confirm=True).order_by("-id").filter(
        is_blind=False)
    qs_1 = SupportBusiness.objects.all().filter(Q(is_blind=True)).order_by("-id")

    avg_em = Startup.objects.all().aggregate(Sum("employee_number"))["employee_number__sum"] / total_startup
    total_rev = (Startup.objects.all().aggregate(Sum("revenue_before_0"))["revenue_before_0__sum"] + \
                Startup.objects.all().aggregate(Sum("revenue_before_1"))["revenue_before_1__sum"] + \
                Startup.objects.all().aggregate(Sum("revenue_before_2"))["revenue_before_2__sum"])/total_startup
    total_fund = (Startup.objects.all().aggregate(Sum("fund_before_0"))["fund_before_0__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_1"))["fund_before_1__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_2"))["fund_before_2__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_3"))["fund_before_3__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_4"))["fund_before_4__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_5"))["fund_before_5__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_6"))["fund_before_6__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_7"))["fund_before_7__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_8"))["fund_before_8__sum"] + \
                 Startup.objects.all().aggregate(Sum("fund_before_9"))["fund_before_9__sum"])/total_startup
    total_exp = (Startup.objects.all().aggregate(Sum("export_before_0"))["export_before_0__sum"] + \
                Startup.objects.all().aggregate(Sum("export_before_1"))["export_before_1__sum"] + \
                Startup.objects.all().aggregate(Sum("export_before_2"))["export_before_2__sum"])/total_startup

    total_select_com = len((Startup.objects.all().filter(award__sb_id__gte=0).distinct()))
    ventur_num = startup_found.objects.all().order_by("year")
    ventur_num_gg = startup_found_gg.objects.all().order_by("year")

    em_num = avg_employee.objects.all().order_by("year")
    em_num_gg = avg_employee_gg.objects.all().order_by("year")

    if total_select_com == 0:
        total_select_com_avg=0
        total_apply_com_avg=0
        sel_avg_em=0
        sel_total_rev=0
        sel_total_fund=0
        sel_total_exp=0
    else:
        total_select_com_avg = len(Award.objects.all()) / total_select_com
        total_apply_com_avg = len(Appliance.objects.all()) / len((Startup.objects.all().filter(award__sb_id__gte=0)))
        sel_avg_em = \
            (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                precio=Coalesce(Sum("employee_number"), 0))[
                "precio"] / total_select_com


        sel_total_rev = (int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_0"), 0))[
            "precio"]) + \
                    int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                        precio=Coalesce(Sum("revenue_before_1"), 0))[
                            "precio"]) + \
                    int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                        precio=Coalesce(Sum("revenue_before_2"), 0))[
                            "precio"]))/total_select_com
        sel_total_fund = (int(
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_0"), 0))[
            "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_1"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_2"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_3"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_4"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_5"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_6"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_7"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_8"), 0))[
                             "precio"]) + \
                     int((Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
                         precio=Coalesce(Sum("fund_before_9"), 0))[
                             "precio"]))/total_select_com
        sel_total_exp = (int( (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("export_before_0"), 0))[
            "precio"]))/total_select_com
    # int((Startup.objects.all().filter(award__sb_id__gte=0)).aggregate(Sum("export_before_1"))["export_before_1__sum"])
    # (Startup.objects.all().filter(award__sb_id__gte=0)).aggregate(Sum("export_before_2"))["export_before_2__sum"]

    local_num = len((Startup.objects.all().filter(filter__name="경기도기업").distinct()))
    lcoal_select_com_avg = len(Award.objects.all()) / local_num
    local_apply_com_avg = len(Appliance.objects.all()) / local_num
    local_avg_em = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("employee_number"), 0))[
            "precio"] / local_num

    print(Startup.objects.all().filter(filter__name="경기도기업").distinct().aggregate(
        precio=Coalesce(Sum("employee_number"), 0))[
              "precio"])
    print(Startup.objects.all().filter(filter__name="경기도기업").distinct())
    print(local_avg_em)
    print(local_num)
    local_total_rev = \
        ((Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_0"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_1"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_2"), 0))[
            "precio"])/local_num
    local_total_fund = \
        ((Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_0"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_1"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_2"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_3"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_4"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_5"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_6"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_7"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_8"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("fund_before_9"), 0))[
            "precio"])/local_num
    local_total_exp = \
        ((Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_0"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_1"), 0))[
            "precio"] + \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_2"), 0))[
            "precio"])/local_num
    sel_rev_0 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_0"), 0))[
            "precio"]

    sel_rev_1 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_1"), 0))[
            "precio"]

    sel_rev_2 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_2"), 0))[
            "precio"]

    sel_exp_0 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("export_before_0"), 0))[
            "precio"]

    sel_exp_1 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("export_before_1"), 0))[
            "precio"]

    sel_exp_2 = \
        (Startup.objects.all().filter(award__sb_id__gte=0)).distinct().aggregate(
            precio=Coalesce(Sum("export_before_2"), 0))[
            "precio"]

    local_rev_0 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_0"), 0))[
            "precio"]
    local_rev_1 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_1"), 0))[
            "precio"]
    local_rev_2 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("revenue_before_2"), 0))[
            "precio"]
    local_exp_0 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_0"), 0))[
            "precio"]
    local_exp_1 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_1"), 0))[
            "precio"]
    local_exp_2 = \
        (Startup.objects.all().filter(filter__name="경기도기업")).distinct().aggregate(
            precio=Coalesce(Sum("export_before_2"), 0))[
            "precio"]
    fund = {}
    fund["2017"] = 0
    fund["2016"] = 0
    fund["2015"] = 0
    for s in Startup.objects.all():
        if s.fund_before_year_0 != "" and s.fund_before_year_0 != None:
            if str(s.fund_before_year_0)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_0)[0:4]] = fund[str(s.fund_before_year_0)[0:4]] + int(s.fund_before_0)
        if s.fund_before_year_1 != "" and s.fund_before_year_1 != None:
            if str(s.fund_before_year_1)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_1)[0:4]] = fund[str(s.fund_before_year_1)[0:4]] + int(s.fund_before_1)
        if s.fund_before_year_2 != "" and s.fund_before_year_2 != None:
            if str(s.fund_before_year_2)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_2)[0:4]] = fund[str(s.fund_before_year_2)[0:4]] + int(s.fund_before_2)
        if s.fund_before_year_3 != "" and s.fund_before_year_3 != None:
            if str(s.fund_before_year_3)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_3)[0:4]] = fund[str(s.fund_before_year_3)[0:4]] + int(s.fund_before_3)
        if s.fund_before_year_4 != "" and s.fund_before_year_4 != None:
            if str(s.fund_before_year_4)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_4)[0:4]] = fund[str(s.fund_before_year_4)[0:4]] + int(s.fund_before_4)
        if s.fund_before_year_5 != "" and s.fund_before_year_5 != None:
            if str(s.fund_before_year_5)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_5)[0:4]] = fund[str(s.fund_before_year_5)[0:4]] + int(s.fund_before_5)
        if s.fund_before_year_6 != "" and s.fund_before_year_6 != None:
            if str(s.fund_before_year_6)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_6)[0:4]] = fund[str(s.fund_before_year_6)[0:4]] + int(s.fund_before_6)
        if s.fund_before_year_7 != "" and s.fund_before_year_7 != None:
            if str(s.fund_before_year_7)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_7)[0:4]] = fund[str(s.fund_before_year_7)[0:4]] + int(s.fund_before_7)
        if s.fund_before_year_8 != "" and s.fund_before_year_8 != None:
            if str(s.fund_before_year_8)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_8)[0:4]] = fund[str(s.fund_before_year_8)[0:4]] + int(s.fund_before_8)
        if s.fund_before_year_9 != "" and s.fund_before_year_9 != None:
            if str(s.fund_before_year_9)[0:4] in ["2017", "2016", "2015"]:
                fund[str(s.fund_before_year_9)[0:4]] = fund[str(s.fund_before_year_9)[0:4]] + int(s.fund_before_9)

    sel_fund = {}
    sel_fund["2017"] = 0
    sel_fund["2016"] = 0
    sel_fund["2015"] = 0
    for s in Startup.objects.all().filter(award__sb_id__gte=0).distinct():
        if s.fund_before_year_0 != "" and s.fund_before_year_0 != None:
            if str(s.fund_before_year_0)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_0)[0:4]] = sel_fund[str(s.fund_before_year_0)[0:4]] + int(
                    s.fund_before_0)
        if s.fund_before_year_1 != "" and s.fund_before_year_1 != None:
            if str(s.fund_before_year_1)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_1)[0:4]] = sel_fund[str(s.fund_before_year_1)[0:4]] + int(
                    s.fund_before_1)
        if s.fund_before_year_2 != "" and s.fund_before_year_2 != None:
            if str(s.fund_before_year_2)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_2)[0:4]] = sel_fund[str(s.fund_before_year_2)[0:4]] + int(
                    s.fund_before_2)
        if s.fund_before_year_3 != "" and s.fund_before_year_3 != None:
            if str(s.fund_before_year_3)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_3)[0:4]] = sel_fund[str(s.fund_before_year_3)[0:4]] + int(
                    s.fund_before_3)
        if s.fund_before_year_4 != "" and s.fund_before_year_4 != None:
            if str(s.fund_before_year_4)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_4)[0:4]] = sel_fund[str(s.fund_before_year_4)[0:4]] + int(
                    s.fund_before_4)
        if s.fund_before_year_5 != "" and s.fund_before_year_5 != None:
            if str(s.fund_before_year_5)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_5)[0:4]] = sel_fund[str(s.fund_before_year_5)[0:4]] + int(
                    s.fund_before_5)
        if s.fund_before_year_6 != "" and s.fund_before_year_6 != None:
            if str(s.fund_before_year_6)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_6)[0:4]] = sel_fund[str(s.fund_before_year_6)[0:4]] + int(
                    s.fund_before_6)
        if s.fund_before_year_7 != "" and s.fund_before_year_7 != None:
            if str(s.fund_before_year_7)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_7)[0:4]] = sel_fund[str(s.fund_before_year_7)[0:4]] + int(
                    s.fund_before_7)
        if s.fund_before_year_8 != "" and s.fund_before_year_8 != None:
            if str(s.fund_before_year_8)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_8)[0:4]] = sel_fund[str(s.fund_before_year_8)[0:4]] + int(
                    s.fund_before_8)
        if s.fund_before_year_9 != "" and s.fund_before_year_9 != None:
            if str(s.fund_before_year_9)[0:4] in ["2017", "2016", "2015"]:
                sel_fund[str(s.fund_before_year_9)[0:4]] = sel_fund[str(s.fund_before_year_9)[0:4]] + int(
                    s.fund_before_9)
    local_fund = {}
    local_fund["2017"] = 0
    local_fund["2016"] = 0
    local_fund["2015"] = 0
    for s in Startup.objects.all().filter(address_0__istartswith="경기"):
        if s.fund_before_year_0 != "" and s.fund_before_year_0 != None:
            if str(s.fund_before_year_0)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_0)[0:4]] = local_fund[str(s.fund_before_year_0)[0:4]] + int(
                    s.fund_before_0)
        if s.fund_before_year_1 != "" and s.fund_before_year_1 != None:
            if str(s.fund_before_year_1)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_1)[0:4]] = local_fund[str(s.fund_before_year_1)[0:4]] + int(
                    s.fund_before_1)
        if s.fund_before_year_2 != "" and s.fund_before_year_2 != None:
            if str(s.fund_before_year_2)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_2)[0:4]] = local_fund[str(s.fund_before_year_2)[0:4]] + int(
                    s.fund_before_2)
        if s.fund_before_year_3 != "" and s.fund_before_year_3 != None:
            if str(s.fund_before_year_3)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_3)[0:4]] = local_fund[str(s.fund_before_year_3)[0:4]] + int(
                    s.fund_before_3)
        if s.fund_before_year_4 != "" and s.fund_before_year_4 != None:
            if str(s.fund_before_year_4)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_4)[0:4]] = local_fund[str(s.fund_before_year_4)[0:4]] + int(
                    s.fund_before_4)
        if s.fund_before_year_5 != "" and s.fund_before_year_5 != None:
            if str(s.fund_before_year_5)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_5)[0:4]] = local_fund[str(s.fund_before_year_5)[0:4]] + int(
                    s.fund_before_5)
        if s.fund_before_year_6 != "" and s.fund_before_year_6 != None:
            if str(s.fund_before_year_6)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_6)[0:4]] = local_fund[str(s.fund_before_year_6)[0:4]] + int(
                    s.fund_before_6)
        if s.fund_before_year_7 != "" and s.fund_before_year_7 != None:
            if str(s.fund_before_year_7)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_7)[0:4]] = local_fund[str(s.fund_before_year_7)[0:4]] + int(
                    s.fund_before_7)
        if s.fund_before_year_8 != "" and s.fund_before_year_8 != None:
            if str(s.fund_before_year_8)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_8)[0:4]] = local_fund[str(s.fund_before_year_8)[0:4]] + int(
                    s.fund_before_8)
        if s.fund_before_year_9 != "" and s.fund_before_year_9 != None:
            if str(s.fund_before_year_9)[0:4] in ["2017", "2016", "2015"]:
                local_fund[str(s.fund_before_year_9)[0:4]] = local_fund[str(s.fund_before_year_9)[0:4]] + int(
                    s.fund_before_9)

    all_rev_0 = Startup.objects.all().aggregate(precio=Coalesce(Sum("revenue_before_0"), 0))[
        "precio"]
    all_rev_1 = Startup.objects.all().aggregate(Sum("revenue_before_1"))[
        "revenue_before_1__sum"]
    all_rev_2 = Startup.objects.all().aggregate(Sum("revenue_before_2"))[
        "revenue_before_2__sum"]
    print(all_rev_0)
    print(all_rev_1)
    print(all_rev_2)
    all_exp_0 = Startup.objects.all().aggregate(Sum("export_before_0"))[
        "export_before_0__sum"]
    all_exp_1 = Startup.objects.all().aggregate(Sum("export_before_1"))[
        "export_before_1__sum"]
    all_exp_2 = Startup.objects.all().aggregate(Sum("export_before_2"))[
        "export_before_2__sum"]

    date_arr = []
    day_user = DayUser.objects.all().order_by("-id")[:7]
    q_new = NewUser.objects.all().order_by("-id")[:7]
    q_session_user = SessionPerUser.objects.all().order_by("-id")[:7]
    session = Session.objects.all().order_by("-id")[:7]
    q_pv = PageView.objects.all().order_by("-id")[:7]
    page_per_session = PagePerSession.objects.all().order_by("-id")[:7]
    for k in range(1, 8):
        date = datetime.datetime.now() + datetime.timedelta(days=k * -1)
        date_arr.append(date)
        print(date)

    return render(request, "pc/manager/dashboard2.html",
                  { "key":key, "venture_num":ventur_num,"em_num":em_num,"em_num_gg":em_num_gg,"venture_num_gg":ventur_num_gg,
                      "date_arr": date_arr, "q_day": day_user, "q_new": q_new, "q_session_user": q_session_user,
                      "q_session": session, "q_pv": q_pv, "page_per_session": page_per_session,
                      "fund_gr": fund, "sel_fund_gr": sel_fund, "local_fund_gr": local_fund,
                      "total": total, "ing": ing, "avg_apply_ent": avg_apply_ent, "avg_award_ent": avg_award_ent,
                      "total_startup": total_startup, "avg_em": avg_em, "total_rev": total_rev,
                      "total_fund": total_fund,
                      "total_person": total_person, "avg_apply": avg_apply, "avg_award": avg_award,
                      "total_exp": total_exp,
                      "total_select_com": total_select_com, "total_select_com_avg": total_select_com_avg,
                      "total_apply_com_avg": total_apply_com_avg, "sel_avg_em": sel_avg_em,
                      "sel_total_rev": sel_total_rev, "sel_total_fund": sel_total_fund, "sel_total_exp": sel_total_exp,
                      "local_num": local_num,
                      "local_avg_em": local_avg_em, "lcoal_select_com_avg": lcoal_select_com_avg,
                      "local_apply_com_avg": local_apply_com_avg, "local_total_rev": local_total_rev,
                      "local_total_fund": local_total_fund, "local_total_exp": local_total_exp,
                      "sel_rev_0": sel_rev_0, "sel_rev_1": sel_rev_1, "sel_rev_2": sel_rev_2,
                      "sel_exp_0": sel_exp_0, "sel_exp_1": sel_exp_1, "sel_exp_2": sel_exp_2,
                      "local_rev_0": local_rev_0, "local_rev_1": local_rev_1, "local_rev_2": local_rev_2,
                      "local_exp_0": local_exp_0, "local_exp_1": local_exp_1, "local_exp_2": local_exp_2,
                      "all_rev_0": all_rev_0, "all_rev_1": all_rev_1, "all_rev_2": all_rev_2,
                      "all_exp_0": all_exp_0, "all_exp_1": all_exp_1,
                      "all_exp_2": all_exp_2,
                      "qs_0": qs_0, "qs_1": qs_1,
                  })


def write(request):
    form = SupportBusinessForm()
    if request.method == "POST":
        form = SupportBusinessForm(request.POST)

        if form.is_valid():
            print("get_form")
            sb = form.save(commit=False)
            sb.user = request.user.additionaluserinfo
            sb.confirm_count= 0
            if request.POST.get("relate_sp") != "":
                sb.relate_sb = SupportBusiness.objects.get(id=request.POST.get("relate_sp"))
            else:
                sb.relate_sb = None
            if sb.employee_num != 0:
                sb.employee_lt_gt = "lte"
            sb.save()
            print("sb_save")
            for f in request.POST.get("filter").split(","):
                sb.filter.add(Filter.objects.get(id=f))
            if(request.POST.get("obj")=="save"):
                return redirect("sb_edit", id=sb.id)
            else:
                return HttpResponseRedirect("/manager/support/edit/"+str(sb.id)+"?result=preview")

    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    filter_2 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_3 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_4 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_5 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_6 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_7 = Filter.objects.all().filter(cat_0="지원형태", )
    today_min = datetime.datetime.now()
    ap = SupportBusiness.objects.all().filter(complete=True)
    print("here")
    return render(request, "pc/manager/write_sb.html", {"form": form,
                                                        "filter_0": filter_0,
                                                        "filter_1": filter_1,
                                                        "filter_2": filter_2,
                                                        "filter_3": filter_3,
                                                        "filter_4": filter_4,
                                                        "filter_5": filter_5,
                                                        "filter_6": filter_6,
                                                        "filter_7": filter_7,
                                                        "ap":ap
                                                        })


def sb_edit(request, id):
    print(datetime.datetime.now())
    ap = SupportBusiness.objects.all().filter(complete=True)
    sb_origin=SupportBusiness.objects.get(id=id)
    form = SupportBusinessForm(instance=SupportBusiness.objects.get(id=id))

    if request.method == "POST":
        form = SupportBusinessForm(request.POST, instance=SupportBusiness.objects.get(id=id))
        print(form.is_valid())

        if form.is_valid():
            print("here2")
            sb = form.save(commit=False)
            sb.user = SupportBusiness.objects.get(id=id).user
            sb.meta_file_info = SupportBusiness.objects.get(id=id).meta_file_info
            if sb_origin.complete==True:
                sb.complete=True
            if request.POST.get("relate_sp") !="":
                sb.relate_sb = SupportBusiness.objects.get(id=request.POST.get("relate_sp"))
            else:
                sb.relate_sb= None
            if sb.employee_num != 0:
                sb.employee_lt_gt = "lte"
            sb.save()
            sb.filter.clear()
            for f in request.POST.get("filter").split(","):
                sb.filter.add(Filter.objects.get(id=f))
            if (request.POST.get("obj") == "save"):
                print("herer")
                return redirect("sb_edit", id=sb.id)
            else:
                if request.POST.get("obj") == "manager":
                    return redirect("/manager/")
                else:
                    return redirect("/manager/support/edit/"+str(sb.id)+"/?result=preview")
    status = request.POST.get("obj","")
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    filter_2 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_3 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_4 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_5 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_6 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_7 = Filter.objects.all().filter(cat_0="지원형태", )
    sb = SupportBusiness.objects.get(id=id)
    return render(request, "pc/manager/write_sb.html", {"form": form,"status":status,"support":sb,
                                                        "filter_0": filter_0,
                                                        "filter_1": filter_1,
                                                        "filter_2": filter_2,
                                                        "filter_3": filter_3,
                                                        "filter_4": filter_4,
                                                        "filter_5": filter_5,
                                                        "filter_6": filter_6,
                                                        "filter_7": filter_7,
                                                        "sb": sb,
                                                        "ap":ap
                                                        })


def example(request, id):
    save_status = False
    if request.method == "POST":
        sb = SupportBusiness.objects.get(id=id)
        sb.meta_file_info = request.POST.get("meta")
        sb.save()
        save_status = True
        if request.POST.get("is_open") == "true":
            sb.confirm_list.clear()
            sb.confirm_list.add(request.user.additionaluserinfo)
            sb.open_status = False
            sb.confirm = True
            sb.save()
            make_alarm.delay(sb.id,"3", request.user.additionaluserinfo.boss.id)
            return redirect('/manager/sb_list/?cat=confirm')
        status = request.POST.get("obj")
        if(status == "preview"):
            return redirect("/manager/sb_example/"+str(sb.id)+"/?result=preview")
    next_url = request.POST.get("next_url", "")
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    filter_2 = Filter.objects.all().filter(cat_0="조건")
    support = SupportBusiness.objects.get(id=id)
    form = ApplianceForm


    return render(request, "pc/manager/example.html",
                  {"form": form, "filter_1": filter_1, "filter_0": filter_0, "save_status": save_status,
                   "next_url": next_url,"filter_2": filter_2, "support": support})


def pick_winner(request, id):
    if request.method == "POST":
        winner_list = request.POST.get("winner_list").split(",")
        sp = SupportBusiness.objects.get(id=request.POST.get("sp"))
        Award.objects.all().filter(sb=sp).delete()
        sp.open_status = 0
        sp.complete = 1
        sp.is_blind = False
        sp.save()
        try:
            for winner in winner_list:
                print(winner)
                print(Appliance.objects.get(id=winner).startup)
                Award(
                    sb=sp, startup=Startup.objects.get(id=Appliance.objects.get(id=winner).startup.id),
                ).save()
                make_alarm.delay(sp.id, "1")


        except Exception as e:
            print(e)
    sp = SupportBusiness.objects.get(id=id)
    applicant = Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id)).filter(is_submit=True)
    winner_list = Award.objects.all().filter(sb=sp)
    sp_inter = AdditionalUserInfo.objects.all().filter(interest=sp)
    q_obj = Q()

    if len(winner_list) != 0:

        for winner in winner_list:
            q_obj |= Q(startup_id=winner.startup) & Q(sb_id=sp.id)

        win_filter = []
        for a in winner_list:
            for f in a.startup.filter.all():
                if f.cat_1 != "소재지" and f.cat_1 != "기업형태":
                    win_filter.append(f.name)
        win_dict = {i: win_filter.count(i) for i in win_filter}
        local_filter = []
        for a in winner_list:
            for f in a.startup.filter.all():
                if f.cat_1 == "소재지":
                    local_filter.append(f.name)
        win_local_dict = {i: local_filter.count(i) for i in local_filter}

        case_filter = []
        for a in winner_list:
            for f in a.startup.filter.all():
                if f.cat_1 == "기업형태":
                    case_filter.append(f.name)
        win_case_dict = {i: case_filter.count(i) for i in case_filter}

        ap_winner = Appliance.objects.all().filter(q_obj)

    else:
        ap_winner = ""
        win_case_dict = ""
        win_dict = ""
        win_local_dict = ""
    hitlog = []
    date_arr = []
    applog = []
    applicant = Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id)).filter(is_submit=True)
    for k in range(1, 30):
        from_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k + 1)
        to_da = datetime.datetime.now() + datetime.timedelta(days=-1 * k)
        date_arr.append(from_da.isoformat().split("T")[0])
        hitlog.append(len(HitLog.objects.all().filter(date__gt=to_da).filter(sb=sp).filter(date__lte=from_da)))
        applog.append(
            len(Appliance.objects.all().filter(sb=sp).filter(update_at__gt=to_da).filter(update_at__lt=from_da)))

    ap_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 != "소재지" and f.cat_1 != "기업형태":
                ap_filter.append(f.name)
    ap_dict = {i: ap_filter.count(i) for i in ap_filter}
    local_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 == "소재지":
                local_filter.append(f.name)
    local_dict = {i: local_filter.count(i) for i in local_filter}

    case_filter = []
    for a in applicant:
        for f in a.startup.filter.all():
            if f.cat_1 == "기업형태":
                case_filter.append(f.name)
    case_dict = {i: case_filter.count(i) for i in case_filter}

    return render(request, "pc/manager/pick_winner.html",
                  {"sp": sp, "ap": applicant, "ap_winner": ap_winner, "hitlog": hitlog, "inter": sp_inter,
                   "filter_pi": ap_dict, "local_filter_pi": local_dict,
                   "case_filter_pi": case_dict, "win_case_dict": win_case_dict, "win_dict": win_dict,
                   "win_local_dict": win_local_dict,
                   "applog": applog, "date_arr": date_arr})


def save_filter(request):
    data = request.POST.get("val")
    request.user.startup.filter.clear()
    for filter in request.user.startup.filter.all():
        if filter.cat_0 != "지원형태":
            request.user.startup.filter.delete(filter)
    for f in data.split(","):
        try:
            request.user.startup.filter.add(Filter.objects.get(id=f))
        except:
            pass
    request.user.startup.employee_number = (
        (request.POST.get("em").replace("명 이하", "").replace("명 이상", "").replace("제한없음", "0")))
    request.user.startup.save()

    return HttpResponse("ok")


def sb_preview(request, id):
    support = get_object_or_404(SupportBusiness, id=id)
    return render(request, 'pc/support_back.html', {"support": support})


def load_recent_appliance(request):
    if request.method == "POST":
        print("hrer")
        qs = Appliance.objects.filter(id=request.POST.get("ap"))
        qs_json = serializers.serialize('json', qs)
        return HttpResponse(qs_json, content_type='application/json')


def rate_page(request):
    PageRate(page=request.POST.get("page"), user=request.POST.get("user"), rate=request.POST.get("rate")).save()


def apply_preview(request, sbid, id):
    try:
        recent_ap = Appliance.objects.all().filter(startup=request.user.startup)
    except:
        recent_ap = ""
    form = Appliance.objects.get(id=id)
    current_ap = Appliance.objects.get(id=id)
    sp = SupportBusiness.objects.get(id=Appliance.objects.get(id=id).sb_id)
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    try:
        filter_string = request.user.startup.filter.all()
    except:
        filter_string = ""
    k = []
    for f in filter_string:
        k.append(str(f.id))
    return render(request, "pc/appliance_preview.html",
                  {"support": sp, "filter_string": ",".join(k), "form": form, "filter_0": filter_0,
                   "filter_1": filter_1, "recent_ap": recent_ap, "current_ap": current_ap})


def apply_preview_pdf(request, sbid, id):
    try:
        recent_ap = Appliance.objects.all().filter(startup=request.user.startup)
    except:
        recent_ap = ""
    print("print here")
    form = Appliance.objects.get(id=id)
    current_ap = Appliance.objects.get(id=id)
    sp = SupportBusiness.objects.get(id=Appliance.objects.get(id=id).sb_id)
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")
    try:
        filter_string = request.user.startup.filter.all()
    except:
        filter_string = ""
    k = []
    for f in filter_string:
        k.append(str(f.id))
    return render(request, "pc/appliance_preview_pdf.html",
                  {"support": sp, "filter_string": ",".join(k), "form": form, "filter_0": filter_0,
                   "filter_1": filter_1, "recent_ap": recent_ap, "current_ap": current_ap})


def apply_preview_doc(request, sbid):
    form = ApplianceForm()

    sp = SupportBusiness.objects.get(id=sbid)
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역")

    return render(request, "pc/apply.html",
                  {"support": sp, "form": form, "filter_0": filter_0,
                   "filter_1": filter_1})


def get_alarm_status(request):

    if request.user.additionaluserinfo.auth == "5" or  request.user.additionaluserinfo.auth == "4":
        if request.user.additionaluserinfo.auth == "5":
            noti = (Alarm.objects.all().filter(user=request.user.additionaluserinfo).filter(category=3).filter(read=False))
            noti_data = {}
            noti_data["title"] = []
            noti_data["sbid"] = []
            for no in noti:
                if no.origin_sb.title not in noti_data["title"]:
                    noti_data["title"].append(no.origin_sb.title)
                    noti_data["sbid"].append(no.origin_sb.id)
            return JsonResponse({"noti": noti_data})
        else:
            noti = (
            Alarm.objects.all().filter(user=request.user.additionaluserinfo).filter(category=2).filter(read=False))
            noti_data = {}
            noti_data["title"] = []
            noti_data["sbid"] = []
            for no in noti:
                if no.origin_sb.title not in noti_data["title"]:
                    noti_data["title"].append(no.origin_sb.title)
                    noti_data["sbid"].append(no.origin_sb.id)
            return JsonResponse({"noti": noti_data})

    else:
        noti = (Alarm.objects.all().filter(user=request.user.additionaluserinfo).filter(category=0).filter(read=False))
        noti_data = {}
        noti_data["title"] = []
        noti_data["sbid"] = []
        for no in noti:
            if no.origin_sb.title not in noti_data["title"] :
                noti_data["title"].append(no.origin_sb.title)
                noti_data["sbid"].append(no.origin_sb.id)
        step = ((Alarm.objects.all().filter(user=request.user.additionaluserinfo).filter(category=1).filter(read=False)))
        step_data = {}
        step_data["title"] = []
        step_data["sbid"] = []

        for no in step:
            if no.origin_sb.title not in step_data["title"]:
                step_data["title"].append(no.origin_sb.title)
                step_data["sbid"].append(no.origin_sb.id)

        return JsonResponse({"noti": noti_data, "step": step_data})


def get_all_award(request, sbid):
    award_list = Award.objects.all().filter(sb_id=sbid)
    ap_list = Award.objects.all().filter(sb_id=sbid)
    zip_filename = "%s.zip" % (
        str(ap_list[0].sb.apply_end).split("-")[
            0] + "_" + ap_list[0].sb.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list:
        zip_subdir = "applicance"
        url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(
            Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].id)
        subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
        print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")

        if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
            zip_path = os.path.join(ap.startup.name + "/지원서.pdf")
            zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
            print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
            time.sleep(1)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].business_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].business_file.path)
            zip_path = os.path.join(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].startup.name + "/사업자등록증." +
                fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].business_file.path,
                     zip_path)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].fund_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].fund_file.path, zip_path)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].etc_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].etc_file.path, zip_path)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ir_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ir_file.path, zip_path)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ppt_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].ppt_file.path, zip_path)
        if Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].tax_file != "":
            fdir, fname = os.path.split(
                Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(Appliance.objects.all().filter(startup=ap.startup).filter(sb_id=sbid)[0].tax_file.path, zip_path)
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("선정자 리스트")
    sheet.write(0, 0, "순서")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "업종")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "사업자 등록번호")
    sheet.write(0, 5, "이메일")
    sheet.write(0, 6, "대표 전화번호")
    sheet.write(0, 7, "필터")
    k = 1
    for a in ap_list:
        sheet.write(k, 0, k)
        sheet.write(k, 1, a.startup.name)
        sheet.write(k, 2, a.startup.category)
        sheet.write(k, 3, a.startup.user.additionaluserinfo.name)
        sheet.write(k, 4, Appliance.objects.all().filter(sb_id=sbid).filter(startup_id=a.startup.id)[0].business_number)
        sheet.write(k, 5, a.startup.user.username)
        sheet.write(k, 6, a.startup.user.additionaluserinfo.tel)
        filter_list = a.startup.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.name)
        sheet.write(k, 7, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    zf.writestr("전체 리스트.xls", f.getvalue())

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


def get_all_inter(request, sbid):
    award_list = Startup.objects.all().filter(user__additionaluserinfo__interest=SupportBusiness.objects.get(id=sbid))
    print(award_list)
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("선정자 리스트")
    sheet.write(0, 0, "순서")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "업종")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "이메일")
    sheet.write(0, 5, "대표 전화번호")
    sheet.write(0, 6, "필터")
    k = 1
    for a in award_list:
        sheet.write(k, 0, k)
        sheet.write(k, 1, a.name)
        sheet.write(k, 2, a.category)
        sheet.write(k, 3, a.user.additionaluserinfo.name)
        sheet.write(k, 4, a.user.username)
        sheet.write(k, 5, a.user.additionaluserinfo.tel)
        filter_list = a.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.name)
        sheet.write(k, 6, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "관심 지정 스타트업 리스트_" + SupportBusiness.objects.get(id=sbid).title + ".xls", safe='')
    book.save(response)

    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")

    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response


import os
import tempfile
from zipfile import ZipFile
import shutil


def appliance_download(request, apid):
    ap = apid
    ap_target = Appliance.objects.get(id=ap)
    # filenames = ["temp_folder/" + business_file.name.split("/")[-1], ]
    zip_subdir = "applicance"
    zip_filename = "%s.zip" % (
        str(ap_target.sb.apply_end).split("-")[
            0] + "_" + ap_target.sb.title + "_" + ap_target.startup.name + "_" + ap_target.startup.user.additionaluserinfo.name)
    s = io.BytesIO()
    url = "http://gconnect.kr/grant/" + str(ap_target.sb_id) + "/" + str(apid)
    print(url)
    subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf", shell=True, check=True)
    print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
    zf = ZipFile(s, "w")
    if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
        zip_path = os.path.join("지원서.pdf")
        zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
        print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
    if ap_target.business_file != "":
        fdir, fname = os.path.split(ap_target.business_file.path)
        zip_path = os.path.join("사업자등록증." + fname.split(".")[-1])
        zf.write(ap_target.business_file.path, zip_path)
    if ap_target.fund_file != "":
        fdir, fname = os.path.split(ap_target.fund_file.path)
        zip_path = os.path.join("투자증명서." + fname.split(".")[-1])
        zf.write(ap_target.fund_file.path, zip_path)
    if ap_target.etc_file != "":
        fdir, fname = os.path.split(ap_target.etc_file.path)
        zip_path = os.path.join("기타첨부파일." + fname.split(".")[-1])
        zf.write(ap_target.etc_file.path, zip_path)
    if ap_target.ir_file != "":
        fdir, fname = os.path.split(ap_target.ir_file.path)
        zip_path = os.path.join("사업소개서." + fname.split(".")[-1])
        zf.write(ap_target.ir_file.path, zip_path)
    if ap_target.ppt_file != "":
        fdir, fname = os.path.split(ap_target.ppt_file.path)
        zip_path = os.path.join("ppt파일." + fname.split(".")[-1])
        zf.write(ap_target.ppt_file.path, zip_path)
    if ap_target.tax_file != "":
        fdir, fname = os.path.split(ap_target.tax_file.path)
        zip_path = os.path.join("납세증명서." + fname.split(".")[-1])
        zf.write(ap_target.tax_file.path, zip_path)
    # for fpath in filenames:
    #     # Calculate path for file in zip
    #     fdir, fname = os.path.split(fpath)
    #     zip_path = os.path.join(zip_subdir, fname)
    #
    #     # Add file, at correct path
    #     zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


import time


def appliance_all_download(request, sb):
    ap_list = Appliance.objects.filter(sb_id=sb)
    zip_filename = "%s.zip" % (
        str(ap_list[0].sb.apply_end).split("-")[
            0] + "_" + ap_list[0].sb.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list:
        zip_subdir = "applicance"
        url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(ap.id)
        subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
        print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
        if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
            zip_path = os.path.join(ap.startup.name + "/지원서.pdf")
            zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
            print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
            time.sleep(1)
        if ap.business_file != "":
            fdir, fname = os.path.split(ap.business_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업자등록증." + fname.split(".")[-1])
            zf.write(ap.business_file.path, zip_path)
        if ap.fund_file != "":
            fdir, fname = os.path.split(ap.fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(ap.fund_file.path, zip_path)
        if ap.etc_file != "":
            fdir, fname = os.path.split(ap.etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(ap.etc_file.path, zip_path)
        if ap.ir_file != "":
            fdir, fname = os.path.split(ap.ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(ap.ir_file.path, zip_path)
        if ap.ppt_file != "":
            fdir, fname = os.path.split(ap.ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(ap.ppt_file.path, zip_path)
        if ap.tax_file != "":
            fdir, fname = os.path.split(ap.tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(ap.tax_file.path, zip_path)
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원자 리스트")
    sheet.write(0, 0, "순서")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "업종")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "사업자 등록번호")
    sheet.write(0, 5, "이메일")
    sheet.write(0, 6, "대표 전화번호")
    sheet.write(0, 7, "필터")
    k = 1
    for a in ap_list:
        sheet.write(k, 0, k)
        sheet.write(k, 1, a.startup.name)
        sheet.write(k, 2, a.startup.category)
        sheet.write(k, 3, a.startup.user.additionaluserinfo.name)
        sheet.write(k, 4, Appliance.objects.all().filter(sb_id=sb).filter(startup_id=a.startup.id)[0].business_number)
        sheet.write(k, 5, a.startup.user.username)
        sheet.write(k, 6, a.startup.user.additionaluserinfo.tel)
        filter_list = a.startup.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.name)
        sheet.write(k, 7, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    zf.writestr("전체 리스트.xls", f.getvalue())

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp




def startup_sb_manage(request):
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
    filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
    filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
    filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
    filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
    filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
    filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
    if request.GET.get("filter", "") == "" and request.GET.get("em", 0) == 0:
        qs = Startup.objects.all()
        return render(request, "pc/manager/startup_account_list.html",
                      {"qs": qs, "filter_0": filter_0, "filter_1": filter_1, "filter_2": filter_2, "filter_3": filter_3,
                       "filter_4": filter_4, "filter_5": filter_5, "filter_6": filter_6, "filter_7": filter_7,
                       "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10, "filter_11": filter_11,
                       "filter_12": filter_12, "filter_13": filter_13, "filter_14": filter_14, "filter_15": filter_15,
                       "filter_16": filter_16, "filter_17": filter_17, "filter_18": filter_18})
    else:
        qs = Startup.objects.all()
        print("here")
        em = request.GET.get("em", "0")

        if request.GET.get("filter", ",") != ",":
            filter_string = request.GET.get("filter").split(",")
            if filter_string == [""]:
                filter_string = []

            q_obj = Q()
            filter_list = []
            for f in filter_string:
                filter_list.append(Filter.objects.get(id=f))
            print(filter_list)
            for filter in filter_list:
                if filter.cat_0 != "조건" and filter.cat_1 != "업력":
                    # q_obj.add(Q(filter__id=filter.id), Q.AND)
                    qs = qs.filter(filter=filter)
            if Filter.objects.filter(cat_0="조건").filter(cat_1="업력").filter(name="제한없음")[0] not in filter_list:
                for filter in filter_list:
                    if filter.cat_0 == "조건" and filter.cat_1 == "업력":
                        qs = qs.filter(filter=filter)

        if (em != str(0)):
            print(em)
            qs = qs.filter(employee_number__lte=int(em))
        if (request.GET.get("search", "") != ""):
            word = request.GET.get("search")
            qs = qs.filter(Q(name__contains=word) | Q(desc__contains=word) | Q(short_desc__contains=word) | Q(
                tag__name__contains=word)).distinct()
        elif (request.GET.get("search", "") == "" and request.GET.get("filter", ",") == ","):
            qs = Startup.objects.all()

        return render(request, "pc/manager/startup_account_list.html",
                      {"qs": qs, "filter_0": filter_0, "filter_1": filter_1, "filter_2": filter_2,
                       "filter_3": filter_3, "filter_4": filter_4, "filter_5": filter_5, "filter_6": filter_6,
                       "filter_7": filter_7,
                       "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10, "filter_11": filter_11,
                       "filter_12": filter_12, "filter_13": filter_13, "filter_14": filter_14, "filter_15": filter_15,
                       "filter_16": filter_16,
                       "filter_17": filter_17, "filter_18": filter_18})



def startup_sb_manage_all(request):
    filter_0 = Filter.objects.all().filter(cat_0="기본장르")
    filter_1 = Filter.objects.all().filter(cat_0="영역", cat_1="창작")
    filter_2 = Filter.objects.all().filter(cat_0="영역", cat_1="IT 관련")
    filter_3 = Filter.objects.all().filter(cat_0="영역", cat_1="창업")
    filter_4 = Filter.objects.all().filter(cat_0="영역", cat_1="제조/융합 관련")
    filter_5 = Filter.objects.all().filter(cat_0="영역", cat_1="신규사업")
    filter_6 = Filter.objects.all().filter(cat_0="영역", cat_1="기타")
    filter_7 = Filter.objects.all().filter(cat_0="조건", cat_1="업력")
    filter_8 = Filter.objects.all().filter(cat_0="조건", cat_1="구성원")
    filter_9 = Filter.objects.all().filter(cat_0="조건", cat_1="소재지")
    filter_10 = Filter.objects.all().filter(cat_0="조건", cat_1="기업형태")
    filter_11 = Filter.objects.all().filter(cat_0="조건", cat_1="기업단계")
    filter_12 = Filter.objects.all().filter(cat_0="지원형태", cat_1="자금지원")
    filter_13 = Filter.objects.all().filter(cat_0="지원형태", cat_1="엑셀러레이팅 투자연계")
    filter_14 = Filter.objects.all().filter(cat_0="지원형태", cat_1="교육")
    filter_15 = Filter.objects.all().filter(cat_0="지원형태", cat_1="판로")
    filter_16 = Filter.objects.all().filter(cat_0="지원형태", cat_1="네트워킹")
    filter_17 = Filter.objects.all().filter(cat_0="지원형태", cat_1="기타지원")
    filter_18 = Filter.objects.all().filter(cat_0="지원형태", cat_1="공간지원")
    if request.GET.get("filter", "") == "":
        qs = Startup.objects.all()
        return render(request, "pc/manager/startup_list.html",
                      {"qs": qs, "filter_0": filter_0, "filter_1": filter_1, "filter_2": filter_2, "filter_3": filter_3,
                       "filter_4": filter_4, "filter_5": filter_5, "filter_6": filter_6, "filter_7": filter_7,
                       "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10, "filter_11": filter_11,
                       "filter_12": filter_12, "filter_13": filter_13, "filter_14": filter_14, "filter_15": filter_15,
                       "filter_16": filter_16, "filter_17": filter_17, "filter_18": filter_18})
    else:
        qs = Startup.objects.all()
        if request.GET.get("filter", ",") != ",":
            filter_string = request.GET.get("filter").split(",")
            if filter_string == [""]:
                filter_string = []
            em = request.GET.get("em", 0)
            q_obj = Q()
            filter_list = []
            for f in filter_string:
                filter_list.append(Filter.objects.get(id=f))
            print(filter_list)
            for filter in filter_list:
                if filter.cat_1 != "업력":
                    # q_obj.add(Q(filter__id=filter.id), Q.AND)
                    qs = qs.filter(filter=filter)

            if Filter.objects.filter(cat_0="조건").filter(cat_1="업력").filter(name="제한없음")[0] not in filter_list:
                for filter in filter_list:
                    if filter.cat_0 == "조건" and filter.cat_1 == "업력":
                        qs = qs.filter(filter=filter)
        em = request.GET.get("em", 0)
        if (em != 0):
            print(em)
            qs = qs.filter(Q(employee_number__lte=int(em)))
            print(qs)
        if (request.GET.get("search", "") != ""):
            word = request.GET.get("search")
            qs = qs.filter(Q(name__contains=word) | Q(desc__contains=word) | Q(short_desc__contains=word) | Q(
                tag__name__contains=word)).distinct()
        elif (request.GET.get("search", "") == "" and request.GET.get("filter", ",") == ","):
            qs = Startup.objects.all()

        return render(request, "pc/manager/startup_list.html",
                      {"qs": qs, "filter_0": filter_0, "filter_1": filter_1, "filter_2": filter_2,
                       "filter_3": filter_3, "filter_4": filter_4, "filter_5": filter_5, "filter_6": filter_6,
                       "filter_7": filter_7,
                       "filter_8": filter_8, "filter_9": filter_9, "filter_10": filter_10, "filter_11": filter_11,
                       "filter_12": filter_12, "filter_13": filter_13, "filter_14": filter_14, "filter_15": filter_15,
                       "filter_16": filter_16, "filter_17": filter_17, "filter_18": filter_18})


def startup_p_manage_all(request):
    qs = AdditionalUserInfo.objects.all().exclude(Q(auth="4") | Q(auth=5))
    return render(request, "pc/manager/startup_person_list.html",
                  {"qs": qs})


def pick_winner_pdf(request, id):
    sp = SupportBusiness.objects.get(id=id)
    applicant = Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id)).filter(is_submit=True)
    winner_list = Award.objects.all().filter(sb=sp)
    q_obj = Q()
    print("here")
    if len(winner_list) != 0:
        for winner in winner_list:
            q_obj |= Q(startup_id=winner.startup) & Q(sb_id=sp.id)
        ap_winner = Appliance.objects.all().filter(q_obj)
    else:
        ap_winner = ""
    return render(request, "pc/manager/pick_winner_pdf.html", {"sp": sp, "ap": applicant, "ap_winner": ap_winner})


def pdf_down_pick_winner(request, id):
    url = "http://gconnect.kr/manage/pick_winner_pdf/" + str(id)
    subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf", shell=True, check=True)
    print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
    with open(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % urllib.parse.quote(
            "지원자리스트_" + SupportBusiness.objects.get(id=id).title, safe='')
        return response


def sb_detail_pdf_down(request, id):
    url = "http://gconnect.kr/sb_detail_pdf/" + str(id)
    subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf", shell=True, check=True)
    print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
    with open(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % urllib.parse.quote(
            "공고문_" + SupportBusiness.objects.get(id=id).title, safe='')
        return response


def all_sp_download(request, id):
    id_arr = id.split(",")
    zip_filename = "%s.zip" % (str("체크한 사업 지원서"))
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for sb in id_arr:
        ap_list = Appliance.objects.filter(sb_id=sb)
        for ap in ap_list:
            zip_subdir = "applicance"
            url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(ap.id)
            print(url)
            subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
            print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
            if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
                zip_path = os.path.join(SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/지원서.pdf")
                zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
                print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
                time.sleep(1)
            if ap.business_file != "":
                fdir, fname = os.path.split(ap.business_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/사업자등록증." + fname.split(".")[
                        -1])
                zf.write(ap.business_file.path, zip_path)
            if ap.fund_file != "":
                fdir, fname = os.path.split(ap.fund_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/투자증명서." + fname.split(".")[-1])
                zf.write(ap.fund_file.path, zip_path)
            if ap.etc_file != "":
                fdir, fname = os.path.split(ap.etc_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/기타첨부파일." + fname.split(".")[
                        -1])
                zf.write(ap.etc_file.path, zip_path)
            if ap.ir_file != "":
                fdir, fname = os.path.split(ap.ir_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/사업소개서." + fname.split(".")[-1])
                zf.write(ap.ir_file.path, zip_path)
            if ap.ppt_file != "":
                fdir, fname = os.path.split(ap.ppt_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/ppt파일." + fname.split(".")[-1])
                zf.write(ap.ppt_file.path, zip_path)
            if ap.tax_file != "":
                fdir, fname = os.path.split(ap.tax_file.path)
                zip_path = os.path.join(
                    SupportBusiness.objects.get(id=sb).title + "/" + ap.startup.name + "/납세증명서." + fname.split(".")[-1])
                zf.write(ap.tax_file.path, zip_path)
    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


def all_user_sp_download_index(request):
    ap = Appliance.objects.get(id=request.POST.get("id"))
    ir, business, tax, fund, ppt, etc = 0, 0, 0, 0, 0, 0
    if ap.ir_file:
        ir = 1
    if ap.business_file:
        business = 1
    if ap.tax_file:
        tax = 1
    if ap.fund_file:
        fund = 1
    if ap.ppt_file:
        ppt = 1
    if ap.etc_file:
        etc = ap.sb.etc_file_title
    return JsonResponse({"ir": ir, "business": business, "tax": tax, "fund": fund, "ppt": ppt, "etc": etc})


def all_user_sp_download(request):
    ap_list = []
    ap_list.append(Appliance.objects.get(id=request.GET.get("id")))
    if ap_list[0].startup != request.user.startup:
        return HttpResponse("잘못된 접근입니다.")

    ir = request.GET.get("ir")
    business = request.GET.get("business")
    tax = request.GET.get("tax")
    fund = request.GET.get("fund")
    etc = request.GET.get("etc")
    ppt = request.GET.get("ppt")
    app = request.GET.get("ap")

    zip_filename = "%s.zip" % (
        str(ap_list[0].sb.apply_end).split("-")[
            0] + "_" + ap_list[0].sb.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list:
        if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf" and app == "1":
            url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(ap.id)
            print(url)
            subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
            zip_path = os.path.join(ap.startup.name + "/지원서.pdf")
            zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
            print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
            time.sleep(1)
        if ap.business_file != "" and business == "1":
            fdir, fname = os.path.split(ap.business_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업자등록증." + fname.split(".")[-1])
            zf.write(ap.business_file.path, zip_path)
        if ap.fund_file != "" and fund == "1":
            fdir, fname = os.path.split(ap.fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(ap.fund_file.path, zip_path)
        if ap.etc_file != "" and etc == "1":
            fdir, fname = os.path.split(ap.etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(ap.etc_file.path, zip_path)
        if ap.ir_file != "" and ir == "1":
            fdir, fname = os.path.split(ap.ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(ap.ir_file.path, zip_path)
        if ap.ppt_file != "" and ppt == "1":
            fdir, fname = os.path.split(ap.ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(ap.ppt_file.path, zip_path)
        if ap.tax_file != "" and tax == "1":
            fdir, fname = os.path.split(ap.tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(ap.tax_file.path, zip_path)
    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


def set_stop(request):
    print(request.POST)
    if request.user.additionaluserinfo.auth == "5":
        data = request.POST.get("data")
        for id in data.split(","):
            print(id)
                #공고문 작성중인 경우에는 블라이인드 처리가 되지 않도록 한다.
            if SupportBusiness.objects.all().filter(id=id)[0].open_status == True:
                SupportBusiness.objects.all().filter(id=id).update(is_blind=True, )
                make_alarm.delay(SupportBusiness.objects.all().filter(id=id)[0].id,"2",SupportBusiness.objects.all().filter(id=id)[0].user.id)
            if SupportBusiness.objects.all().filter(id=id)[0].complete == True:
                SupportBusiness.objects.all().filter(id=id).update(is_blind=True, )
                make_alarm.delay(SupportBusiness.objects.all().filter(id=id)[0].id, "2",
                           SupportBusiness.objects.all().filter(id=id)[0].user.id)
    return HttpResponse("")


def set_start(request):
    # if request.user.additionaluserinfo.auth == "5":
    #     data = request.POST.get("data")
    #     for id in data.split(","):
    #         if SupportBusiness.objects.all().filter(id=id)[0].is_blind==True and SupportBusiness.objects.all().filter(id=id)[0].confirm==True and SupportBusiness.objects.all().filter(id=id)[0].complete==True:
    #             SupportBusiness.objects.all().filter(id=id)[0].update(is_blind=False,  confirm=False,)
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count= SupportBusiness.objects.all().filter(id=id)[0].confirm_count+1
    #             make_alarm.delay(id, "1")
    #             # 공고 완료 > 블라인드 > 수정 > 승인 요청
    #
    #         if SupportBusiness.objects.all().filter(id=id)[0].is_blind == False and  SupportBusiness.objects.all().filter(id=id)[0].confirm == True and SupportBusiness.objects.all().filter(id=id)[0].complete == True:
    #             SupportBusiness.objects.all().filter(id=id).update( confirm=False, )
    #
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count = SupportBusiness.objects.all().filter(id=id)[0].confirm_count + 1
    #             make_alarm.delay(id, "1")
    #             # 공고 완료 > 블라인드 > 수정 > 승인 요청
    #
    #         elif SupportBusiness.objects.all().filter(id=id)[0].is_blind==True and SupportBusiness.objects.all().filter(id=id)[0].open_status==False and SupportBusiness.objects.all().filter(id=id)[0].confirm==True and SupportBusiness.objects.all().filter(id=id)[0].complete==False :
    #             SupportBusiness.objects.all().filter(id=id).update(is_blind=False, confirm=False, open_status=True)
    #
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count = \
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count + 1
    #             make_alarm.delay(id, "1")
    #             # 공고중 > 블라인드 > 수정 > 승인 요청
    #
    #         elif SupportBusiness.objects.all().filter(id=id)[0].is_blind==False and SupportBusiness.objects.all().filter(id=id)[0].open_status==False and SupportBusiness.objects.all().filter(id=id)[0].confirm==True and SupportBusiness.objects.all().filter(id=id)[0].complete==False:
    #             SupportBusiness.objects.all().filter(id=id).update(open_status=True, confirm=False)
    #             if SupportBusiness.objects.all().filter(id=id)[0].confirm_count == 0 :
    #                 make_alarm.delay(id, "0")
    #             else:
    #                 make_alarm.delay(id, "1")
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count = \
    #             SupportBusiness.objects.all().filter(id=id)[0].confirm_count + 1
    #
    #             # 최초 공고 작성 > 승인 요청
    #
    data = request.POST.get("data")
    for id in data.split(","):
        if request.user.additionaluserinfo.auth == "5":
            target = SupportBusiness.objects.get(id=id)
            target.confirm_list.add(request.user.additionaluserinfo)
            target.is_blind = False
            target.confirm_count = SupportBusiness.objects.get(id=id).confirm_count + 1
            target.open_status = True
            target.confirm=False
            target.save()
        else:
            SupportBusiness.objects.get(id=id).confirm_list.add(request.user.additionaluserinfo)
    return HttpResponse("")



def delete_sb(request):
    if request.user.additionaluserinfo.auth == "5":
        data = request.POST.get("data")
        for id in data.split(","):
            Appliance.objects.all().filter(sb=SupportBusiness.objects.get(id=id)).delete()
            SupportBusiness.objects.get(id=id).filter.clear()
            SupportBusiness.objects.get(id=id).delete()
    return HttpResponse("")


def manager_account(request):
    if request.user.additionaluserinfo.auth == "5" :
        q = AdditionalUserInfo.objects.all().filter(auth=4)

    elif request.user.additionaluserinfo.auth == "4":
        q = request.user.additionaluserinfo.additionaluserinfo_set.all()
    admin = User.objects.get(username="gca_manager@test.com")
    return render(request, "pc/manager/account.html", {"q": q, "admin":admin})


def add_manager_acc(request):

    if request.method == "POST":
        if len(User.objects.all().filter(username=request.POST.get("id"))) == 0:
            add_user = User.objects.create_user(username=request.POST.get("id"), password=request.POST.get("pw"))
            if add_user is not None:
                print(request.POST)
                AdditionalUserInfo(
                    user=add_user,
                    name=request.POST.get("name"),
                    # department=request.POST.get("department"),
                    belong_to=request.POST.get("department"),
                    position=request.POST.get("position"),
                    tel=request.POST.get("tel"),
                    phone=request.POST.get("phone"),
                    additional_email=request.POST.get("additional_email"),
                    boss = request.user.additionaluserinfo,
                    auth="4"
                ).save()
                return HttpResponse("")
        else:
            return HttpResponse("no")

    return HttpResponse("")


def del_manager_acc(request):
    if (request.user.additionaluserinfo.auth == "5"):
        if request.method == "POST":
            for k in request.POST.get("id").split(","):
                user_id = AdditionalUserInfo.objects.get(id=k).user_id
                print(user_id)
                User.objects.get(id=str(user_id)).delete()
    return HttpResponse("")


def stop_sb(request):
    print(request.POST)
    if request.user.additionaluserinfo.auth == "5":
        data = request.POST.get("data")
        for id in data.split(","):
            print(id)
                #공고문 작성중인 경우에는 블라이인드 처리가 되지 않도록 한다.
            if SupportBusiness.objects.all().filter(id=id)[0].open_status == True:
                SupportBusiness.objects.all().filter(id=id).update(is_blind=True, open_status=False)
            if SupportBusiness.objects.all().filter(id=id)[0].complete == True:
                SupportBusiness.objects.all().filter(id=id).update(is_blind=True, open_status=False )
    return HttpResponse("")


def accept_sb(request):

    if request.user.additionaluserinfo.auth == "5":
        sb = SupportBusiness.objects.get(id=request.POST.get("id"))
        if sb.complete != True:
            sb.complete = False
        sb.is_blind = False
        sb.confirm = False
        sb.open_status = True
        sb.complete = False
        sb.confirm_count=sb.confirm_count+1
        sb.save()
        return HttpResponse("")


from xlrd import open_workbook


def upload_xls_startup(request):
    if os.path.abspath(os.path.dirname(__name__)) + "/test.xlsx":
        print("here")
        wb = open_workbook(os.path.abspath(os.path.dirname(__name__)) + "/test.xlsx")
        ws = wb.sheet_by_index(0)
        num_row = ws.nrows
        for k in range(1, num_row):
            name = ws.cell_value(k, 0)
            print(name)
            # 유저 id 와 pw 생성의 경우
            print(User.objects.get(username="startup_" + str(k - 1) + "@naver.com"))
            Startup.objects.all().filter(user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).update(
                name=ws.cell_value(k, 0),
                established_date=ws.cell_value(k, 1).replace("년", "") + "-" + ws.cell_value(k, 2).replace("월",
                                                                                                          "") + "-" + ws.cell_value(
                    k, 3).replace("일", ""),
                category=ws.cell_value(k, 4),
                address_0=ws.cell_value(k, 5) + " " + ws.cell_value(k, 6),
                address_detail_0=ws.cell_value(k, 7),
                employee_number=ws.cell_value(k, 8),
                service_products=ws.cell_value(k, 16)
            )
            Startup.objects.get(user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).filter.clear()
            Startup.objects.get(user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).filter.add(
                Filter.objects.get(name=ws.cell_value(k, 9)))
            Startup.objects.get(user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).filter.add(
                Filter.objects.get(name="법인사업자"))
            Startup.objects.get(user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).filter.add(
                Filter.objects.all().filter(name__icontains=ws.cell_value(k, 11))[0])
            AdditionalUserInfo.objects.all().filter(
                user=User.objects.get(username="startup_" + str(k - 1) + "@naver.com")).update(
                tel=ws.cell_value(k, 14)
            )


def upload_xls_admin(request):
    if os.path.abspath(os.path.dirname(__name__)) + "/gca_admin_acc.xlsx":
        print("here")
        wb = open_workbook(os.path.abspath(os.path.dirname(__name__)) + "/gca_admin_acc.xlsx")
        ws = wb.sheet_by_index(0)
        num_row = ws.nrows
        for k in range(1, num_row):
            name = ws.cell_value(k, 0)
            print(name)
            # 유저 id 와 pw 생성의 경우
            user = User.objects.create_user(username=ws.cell_value(k, 3) + ws.cell_value(k, 4),
                                            password=ws.cell_value(k, 6))
            AdditionalUserInfo(
                user=user,
                auth="4",
                name=ws.cell_value(k, 2),
                position=ws.cell_value(k, 1),
                department=ws.cell_value(k, 0),
            ).save()


def send_email(request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'neogelon@gmail.com',
        ['cto@tradelink.kr'],
        fail_silently=False,
    )


from django.utils.dateparse import parse_datetime


def get_sp_excel(request):
    id_string = request.GET.get("id").replace("/", "")
    sp_id_list = id_string.split(",")

    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원사업 리스트")
    sheet.write(0, 1, "공고 마감년도")
    sheet.write(0, 2, "공고명")
    sheet.write(0, 3, "게시일")
    sheet.write(0, 4, "기관명")
    sheet.write(0, 5, "사업 담당자")
    sheet.write(0, 6, "참여기업수")
    sheet.write(0, 7, "선정자수")
    sheet.write(0, 8, "상태")

    k = 1
    for a in sp_id_list:
        print("==")
        print(a)
        sp = SupportBusiness.objects.get(id=a)
        sheet.write(k, 0, k)
        sheet.write(k, 1, sp.apply_end.year)
        sheet.write(k, 2, sp.title)
        sheet.write(k, 3, parse_datetime(sp.update_at))
        print(parse_datetime(sp.update_at))
        sheet.write(k, 4, sp.user.department)
        sheet.write(k, 5, sp.user.name)
        sheet.write(k, 6, sp.appliance_set.count())
        sheet.write(k, 7, len(Award.objects.all().filter(sb=sp)))
        sheet.write(k, 8, sp.manage_status())

        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "전체 공고문.xls", safe='')
    book.save(response)

    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")

    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response


def get_stl_excel(request):
    id_string = request.GET.get("id").replace("/", "")
    sp_id_list = id_string.split(",")

    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("기업회원 리스트")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "회원아이디")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "핸드폰 번호")
    sheet.write(0, 5, "추가 이메일")
    sheet.write(0, 6, "소재지")
    sheet.write(0, 7, "구성원수")
    sheet.write(0, 8, "매출액")
    sheet.write(0, 9, "수출액")
    sheet.write(0, 10, "투자유치액")
    sheet.write(0, 11, "지원사업 참가횟수")
    sheet.write(0, 12, "지원사업 선정횟수")

    k = 1
    for a in sp_id_list:
        print("==")
        print(a)
        sp = Startup.objects.get(id=a)
        sheet.write(k, 0, k)
        sheet.write(k, 1, sp.name)
        sheet.write(k, 2, sp.user.username)
        sheet.write(k, 3, sp.user.additionaluserinfo.name)
        sheet.write(k, 4, sp.user.additionaluserinfo.tel)
        sheet.write(k, 5, sp.user.additionaluserinfo.additional_email)
        sheet.write(k, 6, sp.address_0 + " " + sp.address_detail_0)
        sheet.write(k, 7, sp.employee_number)
        sheet.write(k, 8, sp.revenue_before_0)
        sheet.write(k, 9, sp.export_before_0)
        sheet.write(k, 10, sp.fund_before_0)
        sheet.write(k, 11, len(Appliance.objects.all().filter(startup=sp)))
        sheet.write(k, 12, len(Award.objects.all().filter(startup=sp)))

        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "기업회원.xls", safe='')
    book.save(response)
    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")
    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response

def get_stp_excel(request):
    id_string = request.GET.get("id").replace("/", "")
    sp_id_list = id_string.split(",")
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("회원 리스트")
    sheet.write(0, 1, "회원아이디")
    sheet.write(0, 2, "회원명")
    sheet.write(0, 3, "핸드폰 번호")
    sheet.write(0, 4, "추가 이메일")

    k = 1
    for a in sp_id_list:
        print("==")
        print(a)
        sp = AdditionalUserInfo.objects.get(id=a)
        sheet.write(k, 0, k)
        sheet.write(k, 1, sp.user.username)
        sheet.write(k, 2, sp.name)
        sheet.write(k, 3, sp.tel)
        sheet.write(k, 4, sp.additional_email)

        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "개인회원.xls", safe='')
    book.save(response)

    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")

    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response


def get_sbtl_excel(request):
    id_string = request.GET.get("id").replace("/", "")
    sp_id_list = id_string.split(",")

    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원사업 참가기업 리스트")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "공고 마감일")

    sheet.write(0, 3, "지원사업명")
    sheet.write(0, 4, "대표자명")
    sheet.write(0, 5, "소재지")
    sheet.write(0, 6, "선정여부")

    k = 1
    for a in sp_id_list:
        print("==")
        print(a)
        sp = Startup.objects.get(id=a)
        sheet.write(k, 0, k)
        sheet.write(k, 1, sp.name)
        sheet.write(k, 2, Appliance.objects.all().filter(startup=sp).order_by("-id")[0].sb.apply_end.year)
        sheet.write(k, 3, Appliance.objects.all().filter(startup=sp).order_by("-id")[0].sb.title)
        sheet.write(k, 4, sp.user.additionaluserinfo.name)
        sheet.write(k, 5, sp.address_0 + " " + sp.address_detail_0)
        if len(Award.objects.all().filter(startup=sp).filter(
                sb=Appliance.objects.all().filter(startup=sp).order_by("-id")[0].sb)) == 0:
            award = "N"
        else:
            award = "Y"
        sheet.write(k, 6, award)

        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "기업회원.xls", safe='')
    book.save(response)

    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")

    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response


def get_sbtl2_excel(request):
    id_string = request.GET.get("id").replace("/", "")
    sp_id_list = id_string.split(",")

    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원사업 리스트")
    sheet.write(0, 1, "공고 마감년도")
    sheet.write(0, 2, "공고명")

    sheet.write(0, 3, "게시일")
    sheet.write(0, 4, "기관명")
    sheet.write(0, 5, "사업담당자")
    sheet.write(0, 6, "참여기업수")
    sheet.write(0, 7, "선정자수")
    sheet.write(0, 8, "상태")
    k = 1
    for a in sp_id_list:
        print("==")
        print(a)
        sp = SupportBusiness.objects.get(id=a)
        sheet.write(k, 0, k)
        sheet.write(k, 1, sp.apply_end.year)
        sheet.write(k, 2, sp.title)
        sheet.write(k, 3, (sp.update_at).isoformat())
        sheet.write(k, 4, sp.user.department)
        sheet.write(k, 5, sp.user.name)
        sheet.write(k, 6, len(Appliance.objects.all().filter(sb=sp)))
        sheet.write(k, 7, len(Award.objects.all().filter(sb=sp)))
        sheet.write(k, 8, sp.manage_status())

        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "지원사업.xls", safe='')
    book.save(response)

    # response = HttpResponse(out_content, content_type="application/vnd.ms-excel")

    # response['Content-Disposition'] = 'attachment; filename=선정자리스트.xlsx'
    return response


from django.core import serializers


def get_repre(request):
    id = request.POST.get("id")
    data = (AdditionalUserInfo.objects.get(id=id))
    data = serializers.serialize('json', [data, ])
    struct = json.loads(data)
    name = (AdditionalUserInfo.objects.get(id=id)).user.username
    struct[0]["id"] = name
    data = json.dumps(struct[0])
    return HttpResponse(data, content_type='application/json')

def error_404(request):
    if request.user.additionaluserinfo.auth == "4" or request.user.additionaluserinfo.auth =="5":
        data = {"target":"m"}
    else:
        data = {"target": "u"}
    return render(request, 'pc/p404.html', data)



def error_500(request):
    data = {}
    return render(request, 'pc/p500.html', data)

def static(request):
    return render(request, 'pc/static.html')


def change_stage(request):
    id=request.POST.get("id")
    to = request.POST.get("to")
    boss = request.POST.get("boss")
    print(to)
    print(id)
    print(boss)
    if to == "2":
        u = User.objects.get(username=id)
        print(u.additionaluserinfo)
        
        u.additionaluserinfo.boss = User.objects.get(username=boss).additionaluserinfo
        u.additionaluserinfo.save()

    elif to=="0" :
        u = User.objects.get(username=id)
        print(u.additionaluserinfo)
        u.additionaluserinfo.boss = None
        u.additionaluserinfo.save()
    elif to=="1":
        u = User.objects.get(username=id)
        print(u.additionaluserinfo)
        u.additionaluserinfo.boss = User.objects.get(username="gca_manager@test.com").additionaluserinfo
        u.additionaluserinfo.save()
    return HttpResponse("")

@csrf_exempt
def vue_home_grant(request):
    result={}
    result["data"]=[]
    print(request.GET.get('q'))

    for sp in SupportBusiness.objects.all():
        obj = {}
        obj["tag"] = []
        obj["title"] = sp.title
        obj["id"] = sp.id

        obj["due"] = str(sp.apply_end).split(" ")[0]
        obj["title_sub"] = sp.title_sub
        obj["short_desc"] = sp.short_desc
        obj["int"] =  random.randrange(0, 100)
        obj["comp"] = random.randrange(0, 100)

        obj["rec"]=0
        for f in sp.filter.all():
            obj["tag"].append(f.name)
            if f.name in tag_list:
                obj["rec"]= obj["rec"]+1
        obj["title"] = obj["title"] + str(obj["rec"])
        # if random.randrange(0,10)%2==0:
        #     obj["img"] = img_list[random.randrange(0,9)]


        result["data"].append(copy.deepcopy(obj))

    return JsonResponse(result)

def get_grant_detail(request):
    id = request.GET.get("id")
    sp = SupportBusiness.objects.all().get(id=id)
    result = {}
    result["title"] = sp.title
    result["short_desc"] = sp.short_desc
    result["apply_start"] = sp.apply_start
    result["apply_end"] = sp.apply_end
    result["object"] = sp.object
    result["top_support_tag"]=[]
    result["int"] = random.randrange(0, 100)
    result["comp"] = random.randrange(0, 100)
    result["object_tag"]=[]
    for t in sp.filter.all():
        if t.cat_0 == "지원형태":
            result["top_support_tag"].append(t.name)
        else:
            result["object_tag"].append(t.name)
    return JsonResponse(result)

def get_static_info(request):
    total_grant = len(SupportBusiness.objects.all().filter(user_id=request.GET.get("id")))
    current_grant = len(SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1))
    result={}
    result["total_grant"] = total_grant
    result["current_grant"] = current_grant
    result["current_grant_list"] = []

    for sp in SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1):
        result["current_grant_list"].append({"name":sp.title,"id":sp.id})
    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1)
    # 매니져가 올린 모든 지원사업 // 일일 좋아요 수 , 매니져 평균 좋아요 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).order_by("date").values("date").order_by("date").distinct()
    k = 0
    inter_arr=[]
    inter_avg_arr=[]
    for inter in int_date:
        inter_arr.append({"date":(inter["date"]),"number":(len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"])))})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month, day=inter["date"].day))
        if len(mother) != 0:
            inter_avg_arr.append({"date": (inter["date"]),
                          "number": (len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"])))/len(mother)})
    result["total_int_data"] =inter_arr
    result["total_int_avg_data"] = inter_avg_arr

    # 매니져가 올린 모든 지원사업 // 일일 지원 수 , 매니져  일일 평균 지원 수
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []

    for ap in Appliance.objects.all().filter(q_objects).order_by("created_at").dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])

    apply_arr=[]
    apply_avg_arr=[]
    for k in date_arr:
        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        apply_arr.append({"date":k,"number":len(ap)})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        if len(mother) !=0 :
            apply_avg_arr.append({"date": k, "number": len(ap)/len(mother)})
    result["total_app_data"] = apply_arr
    result["total_app_avg_data"] = apply_avg_arr

    # 매니져가 올린 모든 지원사업 // 일일 지원 수 , 매니져  일일 평균 방문 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    hit_arr=[]
    hit_avg_arr=[]
    for h in hit:
        hit_arr.append({"date":h["date"],"number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        if(len(mother)!=0):
            hit_avg_arr.append({"date":h["date"],"number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))/len(mother)})
    result["total_hit_data"]=hit_arr
    result["total_hit_avg_data"] = hit_avg_arr

    result["min_date"] = sorted([hit_arr[0]["date"],
                                 datetime.date(year=int(apply_arr[0]["date"].split("-")[0]), month=int(apply_arr[0]["date"].split("-")[1]),
                                                   day=int(apply_arr[0]["date"].split("-")[2])),
                                 inter_arr[0]["date"]
                                 ])[0]


    # 기관 평균 데이터 시작!!!
    # 기관 평균 좋아요 수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects).filter(complete=1)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).values("date").order_by("date").distinct()
    k = 0
    result["agency_int_avg_data"]=[]
    for inter in int_date:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month, day=inter["date"].day))
        result["agency_int_avg_data"].append({"date":inter["date"],"number":len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"]))/len(mother)})

    # 기관 평균 일일 방문자수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    result["agency_hit_avg_data"] = []
    for h in hit:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=h["date"].year, month=h["date"].month, day=h["date"].day))
        result["agency_hit_avg_data"].append(
            {
             "date":h["date"],
             "number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))/(len(mother))
            }
        )
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []
    result["agency_app_avg_data"]=[]
    for ap in Appliance.objects.all().filter(q_objects).dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])
    for k in date_arr:
        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))

        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))

        result["agency_app_avg_data"].append({
            "date":k,
            "number":len(ap)/len(mother)
        })

    # 태그 추출

    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    ap = Appliance.objects.all().filter(q_objects).values("startup")
    # 지원자의 지역 추출

    ap_local_tag = []
    ap_kind_tag = []
    ap_em_tag = []
    ap_tag_tag = []
    result["ap_startup_list"]=[]
    k=0
    for a in ap:
        filter = Startup.objects.get(id=a["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                ap_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                ap_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                ap_tag_tag.append(f.name)
        if Startup.objects.get(id=a["startup"]).employee_number == "" or Startup.objects.get(
                id=a["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=a["startup"]).employee_number
        ap_em_tag.append(str(number))

    temp_list = []
    for a in ap:
        temp_list.append(a["startup"])
    for a in set(temp_list):
        st = Startup.objects.get(id=a)
        result["ap_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(ap_kind_tag[:2]),
            "local": ",".join(ap_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["ap_local_tag"]=(organize(ap_local_tag))
    result["ap_kind_tag"]=(organize(ap_kind_tag))
    result["ap_em_tag"]=(organize(ap_em_tag))
    result["ap_tag_tag"]= (organize(ap_tag_tag))

    hit_local_tag = []
    hit_kind_tag = []
    hit_em_tag = []
    hit_tag_tag = []
    hit = HitLog.objects.all().filter(q_objects).values("user").distinct()
    k=0
    result["hit_startup_list"]=[]
    for h in hit:
        if Startup.objects.all().filter(user_id=AdditionalUserInfo.objects.get(id=h["user"]).user.id):
            filter = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.filter.all()
            for f in filter:
                if f.cat_1 == "소재지":
                    hit_local_tag.append(f.name)
                if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                    hit_kind_tag.append(f.name)
                if f.cat_0 == "조건" and f.cat_1 != "소재지":
                    hit_tag_tag.append(f.name)

            if AdditionalUserInfo.objects.get(
                    id=h["user"]).user.startup.employee_number == "" or AdditionalUserInfo.objects.get(
                    id=h["user"]).user.startup.employee_number == None:
                number = "무응답"
            else:
                number = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.employee_number
            hit_em_tag.append(str(number))
            st = AdditionalUserInfo.objects.get(id=h["user"]).user.startup
            result["hit_startup_list"].append({
                "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(hit_kind_tag[:2]),
                "local": ",".join(hit_local_tag[:2]),
                "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
            })
            k = k + 1

    result["hit_local_tag"]=(organize(hit_local_tag))
    result["hit_kind_tag"]=(organize(hit_kind_tag))
    result["hit_em_tag"]=(organize(hit_em_tag))
    result["hit_tag_tag"] = (organize(hit_tag_tag))

    aw_local_tag = []
    aw_kind_tag = []
    aw_em_tag = []
    aw_tag_tag = []
    aw_startup_list=[]
    result["aw_startup_list"]=[]
    k=0
    award = Award.objects.all().filter(q_objects).values("startup").distinct()
    for aw in award:
        filter = Startup.objects.get(id=aw["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                aw_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                aw_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                aw_tag_tag.append(f.name)

        if Startup.objects.get(id=aw["startup"]).employee_number == "" or Startup.objects.get(
                id=aw["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=aw["startup"]).employee_number
        aw_em_tag.append(number)
        st=Startup.objects.get(id=aw["startup"])
        result["aw_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(aw_kind_tag[:2]),
            "local": ",".join(aw_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["aw_local_tag"]=(organize(aw_local_tag))
    result["aw_kind_tag"]=(organize(aw_kind_tag))
    result["aw_em_tag"]=(organize(aw_em_tag))
    result["aw_tag_tag"]=(organize(aw_tag_tag))


    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1)
    q_objects = Q()
    startup_list=[]
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    ap = Appliance.objects.all().filter(q_objects).values("startup").distinct()
    for a in ap:
        startup_list.append(a["startup"])
    hit = HitLog.objects.all().filter(q_objects).values("user").distinct()
    for h in hit:
        if len(Startup.objects.all().filter(user = AdditionalUserInfo.objects.get(id=h["user"]).user))!=0:
            startup_list.append(Startup.objects.get(user=AdditionalUserInfo.objects.get(id=h["user"]).user).id)
    award = Award.objects.all().filter(q_objects).values("startup").distinct()

    all_local_tag=[]
    all_kind_tag=[]
    all_tag_tag=[]
    all_em_tag=[]
    for aw in award:
        startup_list.append(aw["startup"])
    result["all_startup_list"]=[]
    k=1
    for id in set(startup_list):
        filter = Startup.objects.get(id=id).filter.all()
        st =  Startup.objects.get(id=id)

        for f in filter:
            if f.cat_1 == "소재지":
                all_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                all_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                all_tag_tag.append(f.name)
        if Startup.objects.get(id=id).employee_number == "" or Startup.objects.get(
                id=id).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=id).employee_number
        all_em_tag.append(number)
        result["all_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(all_kind_tag[:2]), "local":",".join(all_local_tag[:2]),
            "employee_num":st.employee_number , "tel":st.user.additionaluserinfo.tel
        })
        k=k+1
    result["all_local_tag"]= organize(all_local_tag)
    result["all_kind_tag"]=organize(all_kind_tag)
    result["all_tag_tag"]=organize(all_tag_tag)
    result["all_em_tag"]=organize(all_em_tag)
    return JsonResponse(result)


def get_grant_static_detail(request):
    result = {}

    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id"))
    result["title"] = SupportBusiness.objects.all().get(id=request.GET.get("sb_id")).title
    print(result["title"])
    # 매니져가 올린 모든 지원사업 // 매니져 평균 좋아요 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).order_by("date").values("date").order_by("date").distinct()
    k = 0
    inter_arr = []
    inter_avg_arr = []
    for inter in int_date:
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month,
                                               day=inter["date"].day))
        inter_avg_arr.append({"date": (inter["date"]),
                              "number": (len(
                                  InterestLog.objects.all().filter(q_objects).filter(date=inter["date"]))) / len(
                                  mother)})
    result["total_int_avg_data"] = inter_avg_arr

    # 매니져가 올린 모든 지원사업 //  매니져  일일 평균 지원 수
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []

    for ap in Appliance.objects.all().filter(q_objects).order_by("created_at").dates("created_at", "day").values(
            "created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])

    apply_arr = []
    apply_avg_arr = []
    for k in date_arr:

        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        apply_avg_arr.append({"date": k, "number": len(ap) / len(mother)})
    result["total_app_avg_data"] = apply_avg_arr

    # 매니져가 올린 모든 지원사업 //  매니져  일일 평균 방문 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    hit_arr = []
    hit_avg_arr = []
    for h in hit:
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        hit_avg_arr.append({"date": h["date"],
                            "number": len(HitLog.objects.all().filter(q_objects).filter(date=h["date"])) / len(mother)})
    result["total_hit_avg_data"] = hit_avg_arr
    # 기관 평균 데이터 시작!!!
    # 기관 평균 좋아요 수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).values("date").order_by("date").distinct()
    k = 0
    result["agency_int_avg_data"] = []
    for inter in int_date:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month,
                                               day=inter["date"].day))
        result["agency_int_avg_data"].append({"date": inter["date"], "number": len(
            InterestLog.objects.all().filter(q_objects).filter(date=inter["date"])) / len(mother)})

    # 기관 평균 일일 방문자수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    result["agency_hit_avg_data"] = []
    for h in hit:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=h["date"].year, month=h["date"].month, day=h["date"].day))
        result["agency_hit_avg_data"].append(
            {
                "date": h["date"],
                "number": len(HitLog.objects.all().filter(q_objects).filter(date=h["date"])) / (len(mother))
            }
        )
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []
    result["agency_app_avg_data"] = []
    for ap in Appliance.objects.all().filter(q_objects).dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])
    for k in date_arr:
        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        print(k)
        print(len(ap))
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        print(len(mother))
        result["agency_app_avg_data"].append({
            "date": k,
            "number": len(ap) / len(mother)
        })
    # 태그 추출
    ap = Appliance.objects.all().filter(sb_id=request.GET.get("sb_id")).values("startup")
    # 지원자의 지역 추출
    ap_local_tag = []
    ap_kind_tag = []
    ap_em_tag = []
    ap_tag_tag = []
    result["ap_startup_list"] = []
    k = 0
    for a in ap:
        filter = Startup.objects.get(id=a["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                ap_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                ap_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                ap_tag_tag.append(f.name)
        if Startup.objects.get(id=a["startup"]).employee_number == "" or Startup.objects.get(
                id=a["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=a["startup"]).employee_number
        ap_em_tag.append(str(number))
    print(ap)
    temp_list = []
    for a in ap:
        temp_list.append(a["startup"])
    for a in set(temp_list):
        st = Startup.objects.get(id=a)
        result["ap_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(ap_kind_tag[:2]),
            "local": ",".join(ap_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["ap_local_tag"] = (organize(ap_local_tag))
    result["ap_kind_tag"] = (organize(ap_kind_tag))
    result["ap_em_tag"] = (organize(ap_em_tag))
    result["ap_tag_tag"] = (organize(ap_tag_tag))

    hit_local_tag = []
    hit_kind_tag = []
    hit_em_tag = []
    hit_tag_tag = []
    hit = HitLog.objects.all().filter(sb_id=request.GET.get("sb_id")).values("user").distinct()
    k = 0
    result["hit_startup_list"] = []
    for h in hit:
        if Startup.objects.all().filter(user_id=AdditionalUserInfo.objects.get(id=h["user"]).user.id):
            filter = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.filter.all()
            for f in filter:
                if f.cat_1 == "소재지":
                    hit_local_tag.append(f.name)
                if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                    hit_kind_tag.append(f.name)
                if f.cat_0 == "조건" and f.cat_1 != "소재지":
                    hit_tag_tag.append(f.name)

            if AdditionalUserInfo.objects.get(
                    id=h["user"]).user.startup.employee_number == "" or AdditionalUserInfo.objects.get(
                id=h["user"]).user.startup.employee_number == None:
                number = "무응답"
            else:
                number = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.employee_number
            hit_em_tag.append(str(number))
            st = AdditionalUserInfo.objects.get(id=h["user"]).user.startup
            result["hit_startup_list"].append({
                "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(hit_kind_tag[:2]),
                "local": ",".join(hit_local_tag[:2]),
                "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
            })
            k = k + 1

    result["hit_local_tag"] = (organize(hit_local_tag))
    result["hit_kind_tag"] = (organize(hit_kind_tag))
    result["hit_em_tag"] = (organize(hit_em_tag))
    result["hit_tag_tag"] = (organize(hit_tag_tag))

    aw_local_tag = []
    aw_kind_tag = []
    aw_em_tag = []
    aw_tag_tag = []
    aw_startup_list = []
    result["aw_startup_list"] = []
    k = 0
    award = Award.objects.all().filter(sb_id=request.GET.get("sb_id")).values("startup").distinct()
    for aw in award:
        filter = Startup.objects.get(id=aw["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                aw_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                aw_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                aw_tag_tag.append(f.name)

        if Startup.objects.get(id=aw["startup"]).employee_number == "" or Startup.objects.get(
                id=aw["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=aw["startup"]).employee_number
        aw_em_tag.append(number)
        st = Startup.objects.get(id=aw["startup"])
        result["aw_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(aw_kind_tag[:2]),
            "local": ",".join(aw_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["aw_local_tag"] = (organize(aw_local_tag))
    result["aw_kind_tag"] = (organize(aw_kind_tag))
    result["aw_em_tag"] = (organize(aw_em_tag))
    result["aw_tag_tag"] = (organize(aw_tag_tag))

    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id"))
    q_objects = Q()
    startup_list = []
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    ap = Appliance.objects.all().filter(sb_id=request.GET.get("sb_id")).values("startup").distinct()
    for a in ap:
        startup_list.append(a["startup"])
    hit = HitLog.objects.all().filter(sb_id=request.GET.get("sb_id")).values("user").distinct()
    for h in hit:
        if len(Startup.objects.all().filter(user=AdditionalUserInfo.objects.get(id=h["user"]).user)) != 0:
            startup_list.append(Startup.objects.get(user=AdditionalUserInfo.objects.get(id=h["user"]).user).id)

    award = Award.objects.all().filter(sb_id=request.GET.get("sb_id")).values("startup").distinct()

    all_local_tag = []
    all_kind_tag = []
    all_tag_tag = []
    all_em_tag = []
    for aw in award:
        startup_list.append(aw["startup"])
    result["all_startup_list"] = []
    k = 1
    for id in set(startup_list):
        filter = Startup.objects.get(id=id).filter.all()
        st = Startup.objects.get(id=id)

        for f in filter:
            if f.cat_1 == "소재지":
                all_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                all_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                all_tag_tag.append(f.name)
        if Startup.objects.get(id=id).employee_number == "" or Startup.objects.get(
                id=id).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=id).employee_number
        all_em_tag.append(number)
        result["all_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(all_kind_tag[:2]),
            "local": ",".join(all_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1
    result["all_local_tag"] = organize(all_local_tag)
    result["all_kind_tag"] = organize(all_kind_tag)
    result["all_tag_tag"] = organize(all_tag_tag)
    result["all_em_tag"] = organize(all_em_tag)

   ### 개별 사업 정보
    #좋아요 데이터
    int_date = InterestLog.objects.all().filter(sb_id=request.GET.get("sb_id")).order_by("date").values("date").order_by("date").distinct()
    inter_arr = []
    for inter in int_date:
        inter_arr.append({"date": (inter["date"]),
                          "number": (len(InterestLog.objects.all().filter(sb_id=request.GET.get("sb_id")).filter(date=inter["date"])))})
    result["total_int_data"] = inter_arr
    #지원자 데이터
    date_arr=[]
    for ap in Appliance.objects.all().filter(sb_id=request.GET.get("sb_id")).order_by("created_at").dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])
    apply_arr=[]
    for k in date_arr:
        ap = Appliance.objects.all().filter(sb_id=request.GET.get("sb_id")).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        apply_arr.append({"date":k,"number":len(ap)})
    result["total_app_data"] = apply_arr
    #방문자 데이터

    hit = HitLog.objects.all().filter(sb_id=request.GET.get("sb_id")).values("date").distinct()
    hit_arr = []
    hit_avg_arr = []
    for h in hit:
        hit_arr.append(
            {"date": h["date"], "number": len(HitLog.objects.all().filter(sb_id=request.GET.get("sb_id")).filter(date=h["date"]))})
    print("방문 데이터")
    print(hit_arr)
    result["total_hit_data"]=hit_arr
    try:
        if hit_arr[0]["date"]:
            hit_date = (hit_arr[0]["date"])
            hit_date =datetime.datetime(year=hit_date.year, month=hit_date.month, day=hit_date.day)
            print(datetime.datetime(year=hit_date.year, month=hit_date.month, day=hit_date.day))
    except Exception as e:
        print("여기")
        print(e)
        hit_date=datetime.datetime.now()
    try:
        if  datetime.datetime(year=int(apply_arr[0]["date"].split("-")[0]),
                                               month=int(apply_arr[0]["date"].split("-")[1]),
                                               day=int(apply_arr[0]["date"].split("-")[2])):
            apply_date = datetime.datetime(year=int(apply_arr[0]["date"].split("-")[0]),
                                               month=int(apply_arr[0]["date"].split("-")[1]),
                                               day=int(apply_arr[0]["date"].split("-")[2]))
    except Exception as e:
        print("저기")
        print(e)
        apply_date = datetime.datetime.now()
    try:
        if inter_arr[0]["date"]:
            inter_date =  inter_arr[0]["date"]
            print(datetime.datetime(year = inter_date.year, month= inter_arr.month, day=inter_arr.day))
    except Exception as e:
        print("아오")
        print(e)
        inter_date = datetime.datetime.now()
    print(type(inter_date))
    print(type(apply_date))
    print(type(hit_date))

    result["min_date"] = str(sorted([hit_date,apply_date,inter_date])[0]).split(" ")[0]



    return JsonResponse(result)


def organize(arr):
    result_list=[]
    for k, v in itertools.groupby(sorted(arr)):
        obj={}
        result = list(v)
        obj[result[0]] = len(result)
        result_list.append(copy.deepcopy(obj))
    return result_list



def get_all_static_info(request):
    total_grant = len(SupportBusiness.objects.all().filter(user_id=request.GET.get("id")))
    current_grant = len(SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(complete=1))
    result={}
    result["total_grant"] = total_grant
    result["current_grant"] = current_grant
    result["current_grant_list"] = []
    for sp in SupportBusiness.objects.all().filter(user_id=request.GET.get("id")):
        result["current_grant_list"].append({"name":sp.title,"id":sp.id})
    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id"))
    # 매니져가 올린 모든 지원사업 // 일일 좋아요 수 , 매니져 평균 좋아요 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).order_by("date").values("date").order_by("date").distinct()
    k = 0
    inter_arr=[]
    inter_avg_arr=[]
    for inter in int_date:
        inter_arr.append({"date":(inter["date"]),"number":(len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"])))})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month, day=inter["date"].day))
        inter_avg_arr.append({"date": (inter["date"]),
                          "number": (len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"])))/len(mother)})
    result["total_int_data"] =inter_arr
    result["total_int_avg_data"] = inter_avg_arr

    # 매니져가 올린 모든 지원사업 // 일일 지원 수 , 매니져  일일 평균 지원 수
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []

    for ap in Appliance.objects.all().filter(q_objects).order_by("created_at").dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])

    apply_arr=[]
    apply_avg_arr=[]
    for k in date_arr:
        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        apply_arr.append({"date":k,"number":len(ap)})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        apply_avg_arr.append({"date": k, "number": len(ap)/len(mother)})
    result["total_app_data"] = apply_arr
    result["total_app_avg_data"] = apply_avg_arr

    # 매니져가 올린 모든 지원사업 // 일일 지원 수 , 매니져  일일 평균 방문 수
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    hit_arr=[]
    hit_avg_arr=[]
    for h in hit:
        hit_arr.append({"date":h["date"],"number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))})
        mother = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]),
                                               day=int(k.split("-")[2])))
        hit_avg_arr.append({"date":h["date"],"number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))/len(mother)})
    result["total_hit_data"]=hit_arr
    result["total_hit_avg_data"] = hit_avg_arr

    result["min_date"] = sorted([hit_arr[0]["date"],
                                 datetime.date(year=int(apply_arr[0]["date"].split("-")[0]), month=int(apply_arr[0]["date"].split("-")[1]),
                                                   day=int(apply_arr[0]["date"].split("-")[2])),
                                 inter_arr[0]["date"]
                                 ])[0]


    # 기관 평균 데이터 시작!!!
    # 기관 평균 좋아요 수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    int_date = InterestLog.objects.all().filter(q_objects).values("date").order_by("date").distinct()
    k = 0
    result["agency_int_avg_data"]=[]
    for inter in int_date:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=inter["date"].year, month=inter["date"].month, day=inter["date"].day))
        result["agency_int_avg_data"].append({"date":inter["date"],"number":len(InterestLog.objects.all().filter(q_objects).filter(date=inter["date"]))/len(mother)})

    # 기관 평균 일일 방문자수
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    sb = SupportBusiness.objects.all().filter(q_u_objects)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    hit = HitLog.objects.all().filter(q_objects).values("date").distinct()
    result["agency_hit_avg_data"] = []
    for h in hit:
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=h["date"].year, month=h["date"].month, day=h["date"].day))
        result["agency_hit_avg_data"].append(
            {
             "date":h["date"],
             "number":len(HitLog.objects.all().filter(q_objects).filter(date=h["date"]))/(len(mother))
            }
        )
    user = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    q_u_objects = Q()
    for u in user.boss.child_list():
        q_u_objects = q_u_objects | Q(user_id=u.id)
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    date_arr = []
    result["agency_app_avg_data"]=[]
    for ap in Appliance.objects.all().filter(q_objects).dates("created_at", "day").values("created_at").distinct():
        if str(ap["created_at"]).split(" ")[0] not in date_arr:
            date_arr.append(str(ap["created_at"]).split(" ")[0])
    for k in date_arr:
        ap = Appliance.objects.all().filter(q_objects).filter(
            created_at__date=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        print(k)
        print(len(ap))
        mother = SupportBusiness.objects.all().filter(q_u_objects).filter(
            apply_start__lte=datetime.datetime(year=int(k.split("-")[0]), month=int(k.split("-")[1]), day=int(k.split("-")[2])))
        print(len(mother))
        result["agency_app_avg_data"].append({
            "date":k,
            "number":len(ap)/len(mother)
        })

    # 태그 추출

    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id"))
    q_objects = Q()
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    ap = Appliance.objects.all().filter(q_objects).values("startup")
    # 지원자의 지역 추출

    ap_local_tag = []
    ap_kind_tag = []
    ap_em_tag = []
    ap_tag_tag = []
    result["ap_startup_list"]=[]
    k=0
    for a in ap:
        filter = Startup.objects.get(id=a["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                ap_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                ap_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                ap_tag_tag.append(f.name)
        if Startup.objects.get(id=a["startup"]).employee_number == "" or Startup.objects.get(
                id=a["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=a["startup"]).employee_number
        ap_em_tag.append(str(number))
    print(ap)
    temp_list = []
    for a in ap:
        temp_list.append(a["startup"])
    for a in set(temp_list):
        st = Startup.objects.get(id=a)
        result["ap_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(ap_kind_tag[:2]),
            "local": ",".join(ap_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["ap_local_tag"]=(organize(ap_local_tag))
    result["ap_kind_tag"]=(organize(ap_kind_tag))
    result["ap_em_tag"]=(organize(ap_em_tag))
    result["ap_tag_tag"]= (organize(ap_tag_tag))

    hit_local_tag = []
    hit_kind_tag = []
    hit_em_tag = []
    hit_tag_tag = []
    hit = HitLog.objects.all().filter(q_objects).values("user").distinct()
    print(hit)
    k=0
    result["hit_startup_list"]=[]
    for h in hit:

        if Startup.objects.all().filter(user_id=AdditionalUserInfo.objects.get(id=h["user"]).user.id):
            filter = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.filter.all()
            for f in filter:
                if f.cat_1 == "소재지":
                    hit_local_tag.append(f.name)
                if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                    hit_kind_tag.append(f.name)
                if f.cat_0 == "조건" and f.cat_1 != "소재지":
                    hit_tag_tag.append(f.name)

            if AdditionalUserInfo.objects.get(
                    id=h["user"]).user.startup.employee_number == "" or AdditionalUserInfo.objects.get(
                    id=h["user"]).user.startup.employee_number == None:
                number = "무응답"
            else:
                number = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.employee_number
            hit_em_tag.append(str(number))
            st = AdditionalUserInfo.objects.get(id=h["user"]).user.startup
            result["hit_startup_list"].append({
                "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(hit_kind_tag[:2]),
                "local": ",".join(hit_local_tag[:2]),
                "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
            })
            k = k + 1

    result["hit_local_tag"]=(organize(hit_local_tag))
    result["hit_kind_tag"]=(organize(hit_kind_tag))
    result["hit_em_tag"]=(organize(hit_em_tag))
    result["hit_tag_tag"] = (organize(hit_tag_tag))

    aw_local_tag = []
    aw_kind_tag = []
    aw_em_tag = []
    aw_tag_tag = []
    aw_startup_list=[]
    result["aw_startup_list"]=[]
    k=0
    award = Award.objects.all().filter(q_objects).values("startup").distinct()
    for aw in award:
        filter = Startup.objects.get(id=aw["startup"]).filter.all()
        for f in filter:
            if f.cat_1 == "소재지":
                aw_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                aw_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                aw_tag_tag.append(f.name)

        if Startup.objects.get(id=aw["startup"]).employee_number == "" or Startup.objects.get(
                id=aw["startup"]).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=aw["startup"]).employee_number
        aw_em_tag.append(number)
        st=Startup.objects.get(id=aw["startup"])
        result["aw_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(aw_kind_tag[:2]),
            "local": ",".join(aw_local_tag[:2]),
            "employee_num": st.employee_number, "tel": st.user.additionaluserinfo.tel
        })
        k = k + 1

    result["aw_local_tag"]=(organize(aw_local_tag))
    result["aw_kind_tag"]=(organize(aw_kind_tag))
    result["aw_em_tag"]=(organize(aw_em_tag))
    result["aw_tag_tag"]=(organize(aw_tag_tag))


    sb = SupportBusiness.objects.all().filter(user_id=request.GET.get("id"))
    q_objects = Q()
    startup_list=[]
    for s in sb:
        q_objects = q_objects | Q(sb_id=s.id)
    ap = Appliance.objects.all().filter(q_objects).values("startup").distinct()
    for a in ap:
        startup_list.append(a["startup"])
    hit = HitLog.objects.all().filter(q_objects).values("user").distinct()
    for h in hit:
        if len(Startup.objects.all().filter(user = AdditionalUserInfo.objects.get(id=h["user"]).user))!=0:
            startup_list.append(Startup.objects.get(user=AdditionalUserInfo.objects.get(id=h["user"]).user).id)
    award = Award.objects.all().filter(q_objects).values("startup").distinct()

    all_local_tag=[]
    all_kind_tag=[]
    all_tag_tag=[]
    all_em_tag=[]
    for aw in award:
        startup_list.append(aw["startup"])
    result["all_startup_list"]=[]
    k=1
    for id in set(startup_list):
        filter = Startup.objects.get(id=id).filter.all()
        st =  Startup.objects.get(id=id)

        for f in filter:
            if f.cat_1 == "소재지":
                all_local_tag.append(f.name)
            if f.cat_0 == "영역" or f.cat_0 == "기본장르":
                all_kind_tag.append(f.name)
            if f.cat_0 == "조건" and f.cat_1 != "소재지":
                all_tag_tag.append(f.name)
        if Startup.objects.get(id=id).employee_number == "" or Startup.objects.get(
                id=id).employee_number == None:
            number = "무응답"
        else:
            number = Startup.objects.get(id=id).employee_number
        all_em_tag.append(number)
        result["all_startup_list"].append({
            "index": k, "email": st.user.username, "name": st.name, "kind": ",".join(all_kind_tag[:2]), "local":",".join(all_local_tag[:2]),
            "employee_num":st.employee_number , "tel":st.user.additionaluserinfo.tel
        })
        k=k+1
    result["all_local_tag"]= organize(all_local_tag)
    result["all_kind_tag"]=organize(all_kind_tag)
    result["all_tag_tag"]=organize(all_tag_tag)
    result["all_em_tag"]=organize(all_em_tag)
    return JsonResponse(result)


def similar_grant(request):
    result={}
    result["data"]=[]
    print(request.GET.get('q'))

    origin_sp = SupportBusiness.objects.all().get(id=request.GET.get('q'))

    for sp in SupportBusiness.objects.all().exclude(id=request.GET.get('q')):
        obj = {}
        obj["tag"] = []
        obj["title"] = sp.title
        obj["due"] = str(sp.apply_end).split(" ")[0]
        obj["title_sub"] = sp.title_sub
        obj["short_desc"] = sp.short_desc
        obj["int"] =  random.randrange(0, 100)
        obj["comp"] = random.randrange(0, 100)
        obj["id"] = sp.id
        obj["sim"]=0
        for f in sp.filter.all():
            obj["tag"].append(f.name)
            if f in origin_sp.filter.all():
                obj["sim"]= obj["sim"]+1

        # if random.randrange(0,10)%2==0:
        #     obj["img"] = img_list[random.randrange(0,9)]
        result["data"].append(copy.deepcopy(obj))
        sorted(result["data"], key=lambda c:c["sim"])
    return JsonResponse(result)

def vue_get_startup_list(request):
    st = Startup.objects.all()
    result = []
    for s in st:
        temp_obj={}
        temp_obj["name"] = s.name
        temp_obj["short_desc"] = s.short_desc
        temp_obj["tag"]=[]
        temp_obj["id"]=s.id
        for t in s.tag.all():
            if t.name != "" and t.name != None:
                temp_obj["tag"].append(t.name)
        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)

def vue_get_startup_detail(request):
    print(request.GET.get("id"))
    #st= AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    st = Startup.objects.get(id=request.GET.get("id"))
    result={}

    result["back_img"] = st.back_img
    result["logo"] = st.logo

    result["startup_id"] = st.id
    result["name"] = st.name
    # result["logo"] = st.thumbnail
    result["short_desc"] = st.short_desc
    result["intro_text"] = st.intro_text
    result["information"]={}
    result["information"]["id"] = st.id
    result["information"]["tag"]=[]
    for t in st.tag.all():
        if t.name != "" and t.name != None:
            result["information"]["tag"].append(t.name)
    result['information']["homepage"] = st.website
    result['information']["email"] = st.user.username
    result["location"] = st.address_0
    result["business_file"]= st.business_file.split("/")[-1]
    result["business_file_path"] = st.business_file
    if result["business_file"] == "":
        result["business_file"] = "파일을 업로드 하세요."
        result["business_file_path"] =""
    result["service"]=[]
    result["tag"]=[]

    for f in st.filter.all():
        result["tag"].append(f.name)

    for service in st.service_set.all():
        obj={}
        obj["intro"] = service.intro
        obj["file"] = service.file
        obj["file_name"] = service.file.split("/")[-1]
        obj["name"] = service.name
        obj["img"] = service.img
        obj["img_name"] = service.img.split("/")[-1]
        obj["id"] = service.id
        result["service"].append(copy.deepcopy(obj))
    result["history"]=[]
    for history in st.history_set.all():
        obj={}
        obj["year"] = history.year
        obj["month"] = history.month
        obj["content"] = history.content
        obj["id"] = history.id
        result["history"].append(copy.deepcopy(obj))
    result["revenue"]=[]
    for revenue in st.revenue_set.all():
        obj={}
        obj["year"] = revenue.year
        obj["num"] = revenue.size
        obj["id"]= revenue.id
        result["revenue"].append(copy.deepcopy(obj))
    result["trade"] = []
    for trade in st.tradeinfo_set.all():
        obj = {}
        obj["year"] = trade.year
        obj["size"] = trade.size
        obj["id"] = trade.id
        result["trade"].append(copy.deepcopy(obj))
    result["invest"]=[]
    for invest in st.fund_set.all():
        obj={}
        obj["year"] = invest.year
        obj["size"] = invest.size
        obj["agency"] = invest.agency
        obj["step"] = invest.step
        obj["currency"] = invest.currency
        result["invest"].append(copy.deepcopy(obj))
    result["news"]=[]
    result["news"] = []

    for news in st.activity_set.order_by("-created_at").all():
        obj={}
        obj["date"] =  news.created_at
        obj["content"] = news.text
        obj["img"] = news.img

        obj["like_num"] = len(news.activitylike_set.all())
        obj["rep_num"] = len(news.reply_set.all())
        obj["id"] = news.id
        obj["img"] = news.img

        obj["rep"]=[]
        for rep in news.reply_set.all():
            temp = {}
            #temp["logo"] = rep.activity.startup.thumbnail
            temp["content"] = rep.text
            temp["date"] = rep.created_at
            temp["id"] = rep.id
            obj["rep"].append(copy.deepcopy(temp))
        result["news"].append(copy.deepcopy(obj))
    return JsonResponse(result)

@csrf_exempt
def vue_update_startup_detail(request):
    print(request.POST)
    print(request.FILES)
    rjd = json.loads(request.POST.get("json_data"))
    #file_path = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']), rjd["startup_id"]  )
    st = Startup.objects.get(id=rjd["startup_id"])
    st.name = rjd["name"]
    st.short_desc = rjd["short_desc"]
    st.intro_text =  rjd["intro_text"]
    st.website = rjd["information"]["homepage"]
    st.user.username = rjd["information"]["email"]
    st.tag.clear()
    for tag in rjd["information"]["tag"]:

        tag_origin ,created= Tag.objects.get_or_create(name=tag)
        st.tag.add(tag_origin)
    st.address_0 = rjd["location"]
    user = st.user
    user.username = rjd["information"]["email"]
    user.save()
    if request.FILES.get("file"):
        if rjd["business_file"] == request.FILES.get("file").name:
            path = handle_uploaded_file_business_file(request.FILES['file'], str(request.FILES['file']), rjd["startup_id"])
            st.business_file = path
    st.save()


    for act in rjd["news"]:
        if act.get("id"):
            activity = Activity.objects.get(id=act.get("id"))
        else:
            activity = Activity()
        activity.text = act["content"]
        activity.startup = st
        print(rjd)
        try:
            if rjd["file_name"] == request.FILES.get("file_news").name:
                path = handle_uploaded_file_business_file(request.FILES['file_news'], str(request.FILES['file_news']), st.id)
                activity.img = path
        except:
            pass
        activity.save()
        activity_id = activity.id
        try:
            for rep in act["rep"]:

                if rep.get("id"):
                    reply = Reply.objects.get(id=rep.get("id"))
                else:
                    reply = Reply()
                reply.text = rep["content"]
                reply.author_id = "60"
                reply.activity_id = activity_id
                reply.save()
        except Exception as e:
            print(e)
            pass

    for service in rjd["service"]:
        if service.get("id"):
            ser = Service.objects.get(id = service["id"])
            ser.intro = service["intro"]
            ser.name =service["name"]
            if request.FILES.get("file_1"):
                if service["file_name"] and service["file_name"] == request.FILES.get("file_1").name:
                    path = handle_uploaded_file_service_product( request.FILES['file_1'], str(request.FILES['file_1']),  rjd["startup_id"] )
                    ser.file = path
            if request.FILES.get("file_2"):
                if service["img_name"] and service["img_name"] == request.FILES.get("file_2").name:
                    path = handle_uploaded_file_service_product( request.FILES['file_2'], str(request.FILES['file_2']),  rjd["startup_id"] )
                    ser.img = path
            ser.save()
            print("he22re")
        else :
            ser = Service()
            ser.intro = service["intro"]
            ser.name = service["name"]

            if request.FILES.get("file_1"):
                    # 파일 을 변경한 경우
                path = handle_uploaded_file_service_product(request.FILES['file_1'], str(request.FILES['file_1']),
                                                                rjd["startup_id"])
                ser.file = path
            if request.FILES.get("file_2"):
                path = handle_uploaded_file_service_product(request.FILES['file_2'], str(request.FILES['file_2']),
                                                            rjd["startup_id"])
                ser.img = path
            ser.startup = st
            ser.save()
            print("here2")
    for history in rjd["history"]:
        if history.get("id"):
            his = History.objects.get(id=history.get("id"))
        else:
            his = History()
        his.year = history["year"]
        his.month = history["month"]
        his.content = history["content"]
        his.startup = st
        his.save()
    if request.FILES.get("img_back"):
        st.back_img =handle_uploaded_file_business_back(request.FILES['img_back'], str(request.FILES['img_back']),
                                                                rjd["startup_id"])
    if request.FILES.get("img_logo"):
        st.logo = handle_uploaded_file_service_logo(request.FILES['img_logo'], str(request.FILES['img_logo']),
                                                     rjd["startup_id"])
    st.save()
    return JsonResponse(
        {"result":"ok"}
    )


def handle_uploaded_file_service_product(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/service_product/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/service_product/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/service_product')
    with open('media/uploads/user/'+ str(user_id) +'/company/service_product/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/service_product/'+filename
def handle_uploaded_file_business_file(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/business_file/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/business_file/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/business_file')
    with open('media/uploads/user/'+ str(user_id) +'/company/business_file/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/business_file/'+filename

def handle_uploaded_file_service_logo(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/logo/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/service_product/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/service_product')
    with open('media/uploads/user/'+ str(user_id) +'/company/service_product/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/service_product/'+filename
def handle_uploaded_file_business_back(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/back/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/business_file/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/business_file')
    with open('media/uploads/user/'+ str(user_id) +'/company/business_file/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/business_file/'+filename


@csrf_exempt
def vue_update_startup_with_application_1(request):
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    st = Startup.objects.get(id=rjd["st_id"])
    if len(History.objects.all().filter(year=rjd["found_date"].split("-")[0]).filter(month=rjd["found_date"].split("-")[1]).filter(content= "회사 설립").filter(startup_id= rjd["st_id"])) == 0 :
        h = History()
        h.year = rjd["found_date"].split("-")[0]
        h.month = rjd["found_date"].split("-")[1]
        h.content ="회사 설립"
        h.startup = st
        h.save()

    st.established_date = rjd["found_date"]
    st = Startup.objects.get(id=rjd["st_id"])
    st.name = rjd["name"]
    st.address_0 = rjd["location"]
    st.save()


def vue_update_startup_with_application_2(request):
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    st = Startup.objects.get(id = rjd["st_id"])
    for f in st.filter.all():
        if f.cat_0 !="조건" and f.cat_0 !="지원형태":
            st.filter.remove(f)
    for i in app["tag"]:
        st.filter.add(Filter.objects.all().filter( cat_0= i))
    st.save()
    return "ok"


def vue_update_startup_with_application_3(request):
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    st = Startup.objects.get(id = rjd["st_id"])
    st.employee_number = rjd["total_employee"]
    for r in Revenue.objects.all().filter(st=st):
        r.delete()
    for r in rjd["revenue"]:
        rev = Revenue()
        rev.year = r["year"]
        rev.size = r["size"]
        rev.startup = st
        rev.save()

    for r in rjd["trade"]:
        rev = TradeInfo()
        rev.year = r["year"]
        rev.size = r["size"]
        rev.startup = st
        rev.save()

    st.website = rjd["homepage"]
    st.save()





def vue_get_application(request):
    try:
        st = Startup.objects.get(id=request.GET.get("id"))
    except:
        st = AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    sb = SupportBusiness.objects.get(id=request.GET.get("gr"))
    app, created = Appliance.objects.get_or_create(startup=st, sb=sb)
    result={}
    result["id"] = app.id
    result["st_id"]= st.id
    result["sb_id"] = sb.id
    result["location"] = app.address
    result["name"] = st.name
    result["business_number"] = app.business_number
    result["found_date"] = app.found_date
    result["repre_name"] = app.repre_name
    result["repre_tel"] = app.repre_tel
    result["repre_email"] = app.repre_email
    result["mark_name"] = app.repre_name
    result["mark_tel"] = app.repre_tel
    result["mark_email"] = app.repre_email
    result["keyword"] = app.keyword
    result["sns"] = app.sns
    result["total_employee"] = app.total_employee
    result["hold_employee"] = app.hold_employee
    result["assurance_employee"] = app.assurance_employee
    result["tag"]=[]
    for f in app.filter.all():
        result["tag"].append(f.name)
    result["patent_file_name"] = app.patent_file
    result["trade_file_name"] = app.trade_file
    result["sub_patent_file_name"] = app.sub_patent_file
    result["design_file_name"] = app.design_file
    result["exp"] = app.exp
    result["company_intro"] = app.company_intro
    result["business_intro"] = app.business_intro
    result["service_category"] = app.service_category
    result["service_intro"] = app.service_intro
    result["service_name"] = app.service_name
    result["kind"] = app.kind
    result["revenue"]=[]
    for rev in app.revenueinapplication_set.all():
        result["revenue"].append({"year":rev.year,"num":rev.num,"id":rev.id})
    result["trade"]=[]
    for rev in app.tradeinapplication_set.all():
        result["trade"].append({"year":rev.year,"num":rev.num,"id":rev.id})
    result["oversea"]=[]
    for rev in app.overseainapplication_set.all():
        result["oversea"].append({"nation": rev.nation , "content": rev.content, "id": rev.id})
    return JsonResponse(result)



def handle_uploaded_file_right(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/service_product/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/service_product/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/service_product')
    with open('media/uploads/user/'+ str(user_id) +'/company/service_product/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/service_product/'+filename


@csrf_exempt
def vue_update_application(request):
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    st = app.startup
    print(rjd)
    st.name = rjd["name"]
    st.address_0 = rjd["location"]
    st.save()
    app.business_number = rjd["business_number"]
    app.address = rjd["location"]

    app.found_date = rjd["found_date"]
    app.repre_name = rjd["repre_name"]
    app.repre_tel = rjd["repre_tel"]
    app.repre_email = rjd["repre_email"]
    app.mark_name = rjd["mark_name"]
    app.mark_tel = rjd["mark_tel"]
    app.mark_email = rjd["mark_email"]
    app.keyword = rjd["keyword"]
    app.sns = rjd["sns"]
    app.total_employee = rjd["total_employee"]
    app.hold_employee = rjd["hold_employee"]
    app.assurance_employee = rjd["assurance_employee"]
    app.save()
    app.filter.clear()
    for f in rjd["tag"]:
        print(f)
        app.filter.add( Filter.objects.get(name=f))

    if request.FILES["file_1"]:
        app.patent_file =handle_uploaded_file_right(request.FILES["file_1"], str(request.FILES["file_1"]), st.id)
    if request.FILES["file_2"]:
        app.trade_file = handle_uploaded_file_right(request.FILES["file_2"], str(request.FILES["file_2"]), st.id)
    if request.FILES["file_3"]:
        app.sub_patent_file = handle_uploaded_file_right(request.FILES["file_3"], str(request.FILES["file_3"]), st.id)
    if request.FILES["file_4"]:
        app.design_file = handle_uploaded_file_right(request.FILES["file_4"], str(request.FILES["file_4"]), st.id)


    app.exp = rjd["exp"]
    app.company_intro = rjd["company_intro"]
    app.business_intro = rjd["business_intro"]
    app.service_category = rjd["service_category"]
    app.service_intro = rjd["service_intro"]
    app.service_name = rjd["service_name"]
    app.kind = rjd["kind"]
    for o in rjd["oversea"]:
        if o["id"]:
            oversea = OverseaInApplication.objects.get(id=o["id"])
        else:
            oversea = OverseaInApplication()
        oversea.nation = o["nation"]
        oversea.content = o["content"]
        oversea.save()
    for rev in rjd["revenue"]:
        if rev["id"]:
            revenue = RevenueInApplication.objects.get(id=rev["id"])
        else:
            revenue = RevenueInApplication()
        revenue.year = rev["year"]
        revenue.num = rev["num"]
        revenue.save()
    for trade in rjd["trade"]:
        if trade["id"]:
            tr = TradeInApplication.objects.get(id=trade["id"])
        else:
            tr = TradeInApplication()
        tr.year = trade["year"]
        tr.num  = trade["num"]

    app.save()
    return  JsonResponse({"result":"ok"})



def vue_get_dashboard(request):
    print(request)
    result = {}
    #모집 마감된 공고문
    due_sp = SupportBusiness.objects.all().filter(apply_end__lt=datetime.datetime.now()).filter(complete = 0).filter(user_id=86)
    due_set = []
    for sp in due_sp:
        result_due={}
        result_due["id"] = sp.id

        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["apply_num"] =len(Appliance.objects.all().filter(sb_id=sp.id))

        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id))/int(sp.recruit_size),2)
        else:
            result_due["comp"] = "없음"
        due_set.append(copy.deepcopy(result_due))

        blind_sp = SupportBusiness.objects.all().filter(is_blind=1).filter(user_id=86)
        blind_set = []
        for sp in blind_sp:
            result_due = {}
            result_due["id"] = sp.id

            result_due["pick_date"] = sp.pick_date
            result_due['title'] = sp.title
            result_due["start"] = sp.apply_start
            result_due["end"] = sp.apply_end
            result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))

            if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
                result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
            else:
                result_due["comp"] = "없음"
            blind_set.append(copy.deepcopy(result_due))

        writing_sp = SupportBusiness.objects.all().filter(confirm=0).filter(user_id=86)
        writing_set = []
        for sp in writing_sp:
            result_due = {}
            result_due["id"] = sp.id

            result_due["pick_date"] = sp.pick_date
            result_due['title'] = sp.title
            result_due["start"] = sp.apply_start
            result_due["end"] = sp.apply_end
            result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))

            if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
                result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
            else:
                result_due["comp"] = "없음"
            writing_set.append(copy.deepcopy(result_due))

        ing_sp = SupportBusiness.objects.all().filter(confirm=1).filter(apply_end__gte=datetime.datetime.now()).filter(user_id=86)
        ing_set = []
        for sp in ing_sp:
            result_due = {}
            result_due["id"] = sp.id

            result_due["pick_date"] = sp.pick_date
            result_due['title'] = sp.title
            result_due["start"] = sp.apply_start
            result_due["end"] = sp.apply_end
            result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))

            if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
                result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
            else:
                result_due["comp"] = "없음"
                ing_set.append(copy.deepcopy(result_due))

    result["due_set"] = due_set
    result["blind_set"] = blind_set
    result["writing_set"] = writing_set
    result["ing_set"] = ing_set


    return JsonResponse(result)

@csrf_exempt
def vue_set_application(request):
    print(request.body)
    rjd=json.loads(request.body.decode('utf-8'))
    print(rjd)
    print(",".join(rjd["meta"]))
    id= rjd["id"]

    sb = SupportBusiness.objects.get(id=id)
    sb.meta = ",".join(rjd["meta"])
    sb.confirm_count = sb.confirm_count+1;
    sb.save()
    return JsonResponse({"result":"ok"})

def handle_uploaded_file_poster(file, filename):
    print('media/uploads/poster/')
    if not os.path.exists('media/uploads/poster/'):
        os.makedirs('media/uploads/poster')
    with open('media/uploads/poster/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/poster/'+filename


@csrf_exempt
def vue_get_grant_information(request):
    sp = SupportBusiness.objects.get(id=request.GET.get("id"))
    result={}
    result["title"] = sp.title
    result["poster"] = sp.poster
    result["short_desc"] = sp.short_desc
    result["title_tag"]  = sp.title_tag
    result["title_sub"] = sp.title_sub
    result["business_period_start"] = sp.business_period_start
    result["business_period_end"] = sp.business_period_start
    result["place"]=sp.place
    result["subject"]=sp.subject
    result["business_detail"] = sp.business_detail
    result["tag"] = []
    for t in sp.filter.all():
        result["tag"].append(t.name)
    result["supply_content"] = sp.supply_content
    result["apply_start"] = sp.apply_start
    result["apply_end"] = sp.apply_end
    result["object"] = sp.object
    result["condition"]= sp.condition
    result["recruit_size"] = sp.recruit_size
    result["prefer"] = sp.prefer
    result["constraint"] = sp.constraint
    result["pro_0_choose"] = sp.pro_0_choose
    result["pro_0_start"] = sp.pro_0_start
    result["pro_0_end"] = sp.pro_0_end

    result["pro_0_open"] = sp.pro_0_open
    result["pro_0_criterion"] = sp.pro_0_criterion
    result["pro_1_choose"] = sp.pro_1_choose
    result["pro_2_choose"] = sp.pro_2_choose
    result["meta_file_info"] = sp.meta_file_info
    result["ceremony"]= sp.ceremony
    result["faq"] = sp.faq
    result["additional_faq"] = sp.additional_faq
    result["etc"] = sp.etc
    result["open_method"]=sp.open_method
    result["meta"] = sp.meta
    return JsonResponse(result, safe=False)


@csrf_exempt
def vue_set_grant_information(request):
    sp = SupportBusiness.objects.get(id=request.GET.get("id"))
    rjd = json.loads(request.POST.get("json_data"))

    sp.title = rjd["title"]
    sp.poster= rjd["poster"]
    sp.short_desc= rjd["short_desc"]
    sp.title_tag= rjd["title_tag"]
    sp.title_sub= rjd["title_sub"]
    sp.business_period_start= rjd["business_period_start"]
    sp.business_period_end= rjd["business_period_end"]
    sp.place= rjd["place"]
    sp.subject= rjd["subject"]
    sp.business_detail= rjd["business_detail"]
    sp.supply_content= rjd["supply_content"]
    sp.apply_start= rjd["apply_start"]
    sp.apply_end= rjd["apply_end"  ]
    sp.object= rjd["object"]
    sp.condition= rjd["condition"]
    sp.recruit_size= rjd["recruit_size"]
    sp.prefer= rjd["prefer"]
    sp.constraint= rjd["constraint"]
    sp.pro_0_choose= rjd["pro_0_choose"]
    sp.pro_0_start= rjd["pro_0_start"]
    sp.pro_0_end = rjd["pro_0_end"]

    sp.pro_0_open= rjd["pro_0_open"]
    sp.pro_0_criterion= rjd["pro_0_criterion"]
    sp.pro_1_choose= rjd["pro_1_choose"]
    sp.pro_2_choose= rjd["pro_2_choose"]
    sp.meta_file_info= rjd["meta_file_info"]
    sp.ceremony= rjd["ceremony"]
    sp.faq= rjd["faq"]
    sp.additional_faq= rjd["additional_faq"]
    sp.etc= rjd["etc"]
    sp.open_method = rjd["open_method"]
    return JsonResponse({"result":"ok"})


@csrf_exempt
def vue_submit_application(request):
    user_id = request.POST.get("user_id")
    id = request.POST.get("id")
    user_kind = request.POST.get("user_kind")
    SupportBusiness.objects.get(id=id).confirm_count = SupportBusiness.objects.get(id=id).confirm_count+1

    return JsonResponse({"result":"ok"})







@csrf_exempt
def vue_set_grant_1(request):
    rjd = json.loads(request.POST.get("json_data"))
    if rjd["id"] != "new":
        sb = SupportBusiness.objects.get(id=rjd["id"])
    else:
        sb = SupportBusiness()
    print(rjd)
    sb.title = rjd["title"]
    sb.title_tag = rjd["tag"]
    sb.short_desc = rjd["short_desc"]
    if request.FILES.get('file'):
        sb.poster = handle_uploaded_file_poster(request.FILES['file'], str(request.FILES['file']))
    sb.business_period_start = rjd["start"]
    sb.business_period_end = rjd["end"]
    sb.place = rjd["location"]
    sb.subject = rjd["subject"]
    sb.business_detail = rjd["business_detail"]
    sb.writing_step = 1
    sb.save()
    print(sb.id)
    return JsonResponse({"result":sb.id})


@csrf_exempt
def vue_set_grant_2(request):

    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    sb = SupportBusiness.objects.get(id=rjd["id"])
    tag = rjd["supply_tag"]
    sb.filter.clear()
    for t in sb.filter.all():
        if t.cat_0== "지원형태":
            sb.filter.remove(t)
    print(tag)
    for t in tag:
        sb.filter.add(Filter.objects.all().get(name=t))
    sb.supply_content = rjd["supply_content"]
    sb.writing_step = 2
    sb.save()
    return JsonResponse({"result":"ok"})

@csrf_exempt
def vue_set_grant_3(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    sb = SupportBusiness.objects.get(id=rjd["id"])
    tag = rjd["recruit_tag"]
    sb.filter.clear()
    for t in sb.filter.all():
        if t.cat_0 == "기본장르" or t.cat_0 == "영역":
            sb.filter.remove(t)
    for t in tag:
        print(t)
        sb.filter.add(Filter.objects.get(name=t))
    sb.object = rjd["object"]
    sb.apply_start = rjd["apply_start"]
    sb.apply_end = rjd["apply_end"]
    sb.condition = rjd["condition"]
    sb.recruit_size = rjd["recruit_size"]
    sb.prefer = rjd["prefer"]
    sb.constraint = rjd["constraint"]
    sb.writing_step = 3
    sb.save();
    return JsonResponse({"result":"ok"})


@csrf_exempt
def vue_set_grant_4(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    sb = SupportBusiness.objects.get(id=rjd["id"])

    sb.pro_0_choose = rjd["pro_0_choose"]
    sb.pro_0_start = rjd["pro_0_start"].split("T")[0]
    sb.pro_0_end = rjd["pro_0_end"].split("T")[0]
    sb.pro_0_open = rjd["pro_0_open"]
    sb.open_method = rjd["open_method"]

    sb.pro_0_criterion = rjd["pro_0_criterion"]
    sb.pro_1_choose = rjd["pro_1_choose"]
    sb.pro_2_choose  = rjd["pro_2_choose"]
    sb.writing_step = 5
    sb.save();
    return JsonResponse({"result":"ok"})



@csrf_exempt
def vue_set_grant_5(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    sb = SupportBusiness.objects.get(id=rjd["id"])
    sb.meta_file_info = rjd["file_list"]
    sb.writing_step = 5
    sb.save();
    return JsonResponse({"result":"ok"})



@csrf_exempt
def vue_set_grant_6(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    sb = SupportBusiness.objects.get(id=rjd["id"])
    sb.ceremony = rjd["ceremony"]
    sb.faq = rjd["faq"]
    sb.additional_faq = rjd["additional_faq"]
    sb.etc = rjd["etc"]
    sb.writing_step = 6
    sb.save()
    return JsonResponse({"result":"ok"})

@csrf_exempt
def vue_get_grant_info(request):
    result = {}
    # 모집 마감된 공고문
    due_sp = SupportBusiness.objects.all().filter(apply_end__lt=datetime.datetime.now()).filter(complete=0).filter(user_id=86)
    due_set = []
    for sp in due_sp:
        result_due = {}
        result_due["id"] = sp.id
        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["author"] = sp.user.name
        
        result_due["end"] = sp.apply_end
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        result_due["status"] = "모집종료"

        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = str(round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2))+":1"
        else:
            result_due["comp"] = "없음"
        due_set.append(copy.deepcopy(result_due))

    waiting_sp = SupportBusiness.objects.all().filter(confirm=1).filter(confirm_count=0).filter( user_id=86)
    waiting_set = []
    for sp in waiting_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due["id"] = sp.id
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["status"] = "승인대기"
        result_due["author"] = sp.user.name
        result_due["updated"] = sp.update_at
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = str(
                round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)) + ":1"
        else:
            result_due["comp"] = "없음"
        waiting_set.append(copy.deepcopy(result_due))

    #작성중인 공고
    writing_sp = SupportBusiness.objects.all().filter(confirm=0).filter(user_id=86)
    writing_set = []
    for sp in writing_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due["id"] = sp.id
        result_due["author"] = sp.user.name
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["updated"] = sp.update_at

        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        result_due["status"] = "작성중"

        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        writing_set.append(copy.deepcopy(result_due))
    #공고중인 공고
    ing_sp = SupportBusiness.objects.all().filter(confirm=1).filter(apply_end__gte=datetime.datetime.now()).filter(
        user_id=86)
    ing_set = []
    for sp in ing_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due["id"] = sp.id
        result_due['title'] = sp.title
        result_due["author"] = sp.user.name
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["status"] = "공고중"

        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        ing_set.append(copy.deepcopy(result_due))

    #공고 종료된 공고
    comp_sp = SupportBusiness.objects.all().filter(complete=1).filter(user_id=86)
    comp_set = []
    for sp in comp_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due["id"] = sp.id
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["author"] = sp.user.name
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        result_due["status"] = "공고종료"

        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        comp_set.append(copy.deepcopy(result_due))
    #블라인드된 공고문
    blind_sp = SupportBusiness.objects.all().filter(is_blind=1).filter(user_id=86)
    blind_set = []
    for sp in blind_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due["id"] = sp.id
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["author"] = sp.user.name
        result_due["end"] = sp.apply_end
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        result_due["status"] = "블라인드"

        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        blind_set.append(copy.deepcopy(result_due))

    all_sp = SupportBusiness.objects.all().filter( user_id=86)
    all_set = []
    for sp in all_sp:
        result_due = {}
        result_due["id"] = sp.id
        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["author"] = sp.user.name
        result_due["end"] = sp.apply_end
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))

        if sp.apply_end < datetime.datetime.now() and  sp.complete==0 :  #모집 종료 된 공고문
            result["status"] = "모집종료"

        if sp.confirm == 0:  # 작성중인 공고문
            result["status"] = "작성중"

        if sp.confirm == 1 and sp.confirm_count == 0:  # 승인대기중인 공고문
            result["status"] = "승인대기"
        if  sp.confirm == 1 and sp.apply_end > datetime.datetime.now() and sp.confirm_count >= 1:
            result["status"] = "공고중"

        if sp.complete==1 : # 공고 종료 된 공고문
            result_due["status"] = "공고종료"

        if sp.is_blind==1 : #블라인드 공고문
            result_due["status"] = "블라인드"

        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        all_set.append(copy.deepcopy(result_due))


    result["due_set"] = due_set
    result["blind_set"] = blind_set
    result["writing_set"] = writing_set
    result["ing_set"] = ing_set
    result["waiting_set"] = waiting_set
    result["comp_set"] = comp_set
    result["all_set"] = all_set

    return JsonResponse(result)

def vue_static_user(request):
    #총기업수
    total_startup = len(Startup.objects.all())
    #총 개인회원수
    total_user = len(AdditionalUserInfo.objects.all().exclude(auth=5).exclude(auth=4))
    #기업회원 1개당 평균 사업 참가수
    avg_apply = round(len(Appliance.objects.all())/total_startup,2)
    #기업 회원 한개당 평균 사업 선정수
    avg_award = round(len(Award.objects.all())/total_startup,2)


    ## 최종 선정기업
    # 총 기업회원수
    total_startup_award = len(Award.objects.all().values('startup_id').distinct())
    #기업회원 1개당 평균 사업 참가수
    k=0;
    for st in Award.objects.all().values('startup_id').distinct():
        k = k + len(Award.objects.all().filter(startup_id=st["startup_id"]))
    avg_apply_award = round(k/total_startup_award,2)
    avg_pick_number = round(len(Award.objects.all())/total_startup_award,2)

    #경기지역 모아보기
    total_startup_gg = len(Startup.objects.all().filter(filter__name__contains="경기"))
    k=0;
    startup_list = []
    for st in (Startup.objects.all().filter(filter__name__contains="경기")):
        k = k + len(Award.objects.all().filter(startup=st))
        startup_list.append(st.id)
    avg_apply_gg = round(k/total_startup_gg,2)
    avg_pick_gg = round(len(Award.objects.all().filter(startup_id__in=startup_list))/total_startup_gg,2)

    result={}
    result["total_startup"]= total_startup
    result["total_user"]=total_user
    result["avg_apply"]=avg_apply
    result["avg_award"]=avg_award

    result["total_startup_award"] = total_startup_award
    result["avg_apply_award"] = avg_apply_award
    result["avg_pick_number"] = avg_pick_number

    result["total_startup_gg"]= total_startup_gg
    result["avg_apply_gg"]= avg_apply_gg
    result["avg_pick_gg"] =avg_pick_gg

    return JsonResponse(result)

def vue_get_startup_account(request):
    st= Startup.objects.all()
    result = {}
    k=1
    startup_set=[]
    for s in st :
        temp={}
        temp["index"]=k
        k=k+1
        temp["name"] = s.name
        temp["id"] = s.user.username

        temp["repre"] = s.user.additionaluserinfo.name
        temp["tel"] = s.user.additionaluserinfo.phone
        temp["email"] = s.user.username
        tag_list=[]
        for t in s.filter.all():
            tag_list.append(t.name)
        temp["tag"] = tag_list
        if "경기"  in s.address_0 :
            local = "경기"
        elif "서울" in s.address_0:
            local = "서울"
        elif "인천" in s.address_0:
            local = "인천"
        else :
            local = "기타"
        temp["local"] = local
        temp["employ_num"] = s.employee_number
        temp["apply_num"] = len(Appliance.objects.all().filter(startup=s))
        temp["award_num"] = len(Award.objects.all().filter(startup=s))
        temp["join"] = s.user.date_joined
        temp["tag"]=[]
        for t in s.filter.all():
            temp["tag"].append(t.name)
        startup_set.append(copy.deepcopy(temp))
    result["startup"] = startup_set
    user = AdditionalUserInfo.objects.all().exclude(auth=4).exclude(auth=5)
    p=1
    user_set = []
    for u in user:
        user={}
        user["index"]=p
        p=p+1
        user["id"] = u.user.username
        user["name"] = u.name
        user["phone"] = u.phone
        user["joined"] = u.user.date_joined
        user_set.append(copy.deepcopy(user))
    result["user_set"] = user_set

    ## 사업 참여 기업
    aw_startup_set = Appliance.objects.all().values("startup").distinct()
    k=1
    ap_set = []
    for s in aw_startup_set:

        aw_st={}
        print(s)
        st = Startup.objects.get(id=s["startup"])
        aw_st["index"] = k
        k=k+1
        aw_st["name"] = st.name
        aw_st["repre"] = st.user.additionaluserinfo.name
        tag_list = []
        for t in st.filter.all():
            tag_list.append(t.name)
        aw_st["tag"] = tag_list
        if "경기" in st.address_0:
            local = "경기"
        elif "서울" in st.address_0:
            local = "서울"
        elif "인천" in st.address_0:
            local = "인천"
        else:
            local = "기타"
        aw_st["local"] = local


        aw_st["title"] = Appliance.objects.all().filter(startup=st).last().sb.title
        if len(Award.objects.all().filter(sb=Appliance.objects.all().filter(startup=st).last().sb).filter(startup=st)) == 0 :
            aw_st["awarded"] = "탈락"
        else:
            aw_st["awarded"] = "선정"
        aw_st["due_date"] = str(Appliance.objects.all().filter(startup=st).last().sb.apply_end).split(" ")[0]
        ap_set.append(copy.deepcopy(aw_st))
    result["ap_set"] = ap_set
    return JsonResponse(result)



def vue_add_manager_acc(request):

    if request.method == "POST":
        if len(User.objects.all().filter(username=request.POST.get("id"))) == 0:
            add_user = User.objects.create_user(username=request.POST.get("id"), password=request.POST.get("pw"))
            if add_user is not None:
                print(request.POST)
                AdditionalUserInfo(
                    user=add_user,
                    name=request.POST.get("name"),
                    # department=request.POST.get("department"),
                    belong_to=request.POST.get("department"),
                    position=request.POST.get("position"),
                    tel=request.POST.get("tel"),
                    phone=request.POST.get("phone"),
                    additional_email=request.POST.get("additional_email"),
                    boss = request.user.additionaluserinfo,
                    auth="4"
                ).save()
                return HttpResponse("")
        else:
            return HttpResponse("no")

    return HttpResponse("")


def vue_get_grant_list(request):
    sb = SupportBusiness.objects.all()
    k=0
    result_set = []
    for s in sb:
        temp={}
        temp["index"]=k
        k=k+1
        temp["title"] = s.title
        temp["created_at"] = s.created_at
        print(s.user)
        print(s.user.name)
        temp["author"] = s.user.name
        temp["id"] = s.id
        temp["team"] = s.user.department
        temp["belong_to"] = s.user.belong_to
        temp["tel"] = s.user.tel
        temp["apply_num"] = len(Appliance.objects.all().filter(sb=s))
        temp["award_num"] = len(Award.objects.all().filter(sb=s))
        if s.apply_start < datetime.datetime.now() and s.apply_end > datetime.datetime.now():
            status="공고중"
        elif s.is_blind == 1:
            status = "블라인드중"
        elif s.complete == 1:
            status = "공고종료"
        elif s.complete==0 and s.apply_end < datetime.datetime.now():
            status = "모집종료"
        else:
            status = ""
        temp["status"] = status
        result_set.append(copy.deepcopy(temp))

    return JsonResponse(result_set, safe=False)


def vue_get_grant_list_excel(request):
    sb = SupportBusiness.objects.all()
    k=0
    result_set = []
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원사업 리스트")
    sheet.write(0, 1, "순서")
    sheet.write(0, 2, "공고명")
    sheet.write(0, 3, "핸드폰 번호")
    sheet.write(0, 4, "담당자")
    sheet.write(0, 5, "팀")
    sheet.write(0, 6, "기관")
    sheet.write(0, 7, "연락처")
    sheet.write(0, 8, "지원기업수")
    sheet.write(0, 9, "상태")
    k = 1
    for s in sb:
        print(k)
        sheet.write(k, 1, k)
        sheet.write(k, 2, s.title)
        sheet.write(k, 3, s.user.phone)
        sheet.write(k, 4, s.user.name)
        sheet.write(k, 5, s.user.department)
        sheet.write(k, 6, "경기도 콘텐츠진흥원")
        sheet.write(k, 7, s.user.tel)
        sheet.write(k, 8, len(Appliance.objects.all().filter(sb=s)))
        sheet.write(k, 9, len(Award.objects.all().filter(sb=s)))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "지원사업 리스트.xls", safe='')
    book.save(response)
    return response



from django.views.decorators.csrf import ensure_csrf_cookie

def vue_get_child(request):
    manager_set = AdditionalUserInfo.objects.all().filter(boss_id=request.GET.get("id")).values("name","id")
    return JsonResponse(list(manager_set), safe=False)

def vue_get_grant_by_manager(request):
    grant_set = SupportBusiness.objects.all().filter(user_id=request.GET.get("id")).values("title","id")
    return JsonResponse(list(grant_set), safe=False)

from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def vue_sign(request):
    login_form = LoginForm()
    return render(request, 'pc/accounts/login.html', {"form": login_form})

import  requests

@csrf_exempt
def vue_get_Kakao_auth(request):

    headers = {'Authorization': 'Bearer {0}'.format(request.POST.get(request.POST.get("token")))}
    upload_result = requests.post("https://kapi.kakao.com/v2/user/me", headers=headers)
    print(upload_result.text)

@csrf_exempt
def vue_get_agent_dashboard(request):
    print(request.POST)
    print(AdditionalUserInfo.objects.get(id=request.POST.get("id")).additionaluserinfo_set.all())
    manager_list = []
    for a in AdditionalUserInfo.objects.get(id=request.POST.get("id")).additionaluserinfo_set.all():
        manager_list.append(a.id)
    result = {}
    # 모집 마감된 공고
    due_sp = SupportBusiness.objects.all().filter(apply_end__lt=datetime.datetime.now()).filter(complete=0).filter(
        user_id__in=manager_list)
    due_set=[]
    for sp in due_sp:
        result_due = {}
        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["id"]= sp.id
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = str(
                round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)) + ":1"
        else:
            result_due["comp"] = "없음"
        due_set.append(copy.deepcopy(result_due))
    # 승인 요청중인 공고
    waiting_sp = SupportBusiness.objects.all().filter(confirm=1).filter(confirm_count=0).filter( user_id__in=manager_list)
    waiting_set = []
    for sp in waiting_sp:
        result_due = {}
        result_due["id"] = sp.id
        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = str(
                round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)) + ":1"
        else:
            result_due["comp"] = "없음"
        waiting_set.append(copy.deepcopy(result_due))


    # 공고중인 공고
    ing_sp = SupportBusiness.objects.all().filter(confirm=1).filter(apply_end__gte=datetime.datetime.now()).filter(
        user_id__in=manager_list)
    ing_set = []
    for sp in ing_sp:
        result_due = {}
        result_due["id"] = sp.id
        result_due["pick_date"] = sp.pick_date
        result_due['title'] = sp.title
        result_due["start"] = sp.apply_start
        result_due["end"] = sp.apply_end
        result_due["apply_num"] = len(Appliance.objects.all().filter(sb_id=sp.id))
        result_due["int"] = len(AdditionalUserInfo.objects.all().filter(interest=sp))
        result_due["open_date"] = (sp.created_at)
        if sp.recruit_size != "" and sp.recruit_size != 0 and sp.recruit_size != None:
            result_due["comp"] = round(len(Appliance.objects.all().filter(sb_id=sp.id)) / int(sp.recruit_size), 2)
        else:
            result_due["comp"] = "없음"
        ing_set.append(copy.deepcopy(result_due))


    result["due_set"] = due_set
    result["ing_set"] = ing_set
    result["waiting_set"] = waiting_set

    return JsonResponse(result)

@csrf_exempt
def vue_get_agent_account(request):
    account_set = []
    k=1
    all_account_set=[]
    for ac in  AdditionalUserInfo.objects.all().filter(boss_id=request.POST.get("id")):
        temp={}
        temp["index"] = k
        k=k+1
        temp["id"] = ac.user.username
        temp["name"] = ac.name
        temp["position"] = ac.position
        temp["team"] = ac.department
        temp["belong_to"] = ac.belong_to
        temp["tel"] = ac.tel
        temp["phone"] = ac.phone
        temp["email"] = ac.user.username
        temp["joined"] = str(ac.user.date_joined).split(" ")[0]
        account_set.append(copy.deepcopy(temp))
    k=1
    for ac in AdditionalUserInfo.objects.all().filter(auth=4):
        temp = {}
        temp["index"] = k
        k = k + 1
        temp["id"] = ac.user.username
        temp["name"] = ac.name
        temp["position"] = ac.position
        temp["team"] = ac.department
        temp["belong_to"] = ac.belong_to
        temp["tel"] = ac.tel
        temp["phone"] = ac.phone
        temp["email"] = ac.user.username
        temp["joined"] = str(ac.user.date_joined).split(" ")[0]
        all_account_set.append(copy.deepcopy(temp))
    result={}
    result["account_set"] = account_set
    result["all_account_set"] = all_account_set

    return  JsonResponse(result, safe=False)

@csrf_exempt
def cert_email(request):
    if request.POST.get("type") == "confirm":
        target = request.POST.get("val")
        random_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        try:
            send_mail(
                '[G-connect] 인증메일입니다.',
                '인증코드는 [' + random_code + "] 입니다.",
                'neogelon@gmail.com',
                [target],
                fail_silently=False,
            )
            EmailConfirmation(
                email=target,
                confirmation_code=random_code
            ).save()
            return HttpResponse("ok")
        except Exception as e:
            print(e)
            return HttpResponse("none")


    elif request.POST.get("type") == "confirm2":
        if EmailConfirmation.objects.all().filter(email=request.POST.get("target")).order_by("-id")[0].confirmation_code == request.POST.get("confirmation_code"):
            EmailConfirmation.objects.all().filter(email=request.POST.get("target")).update(confirm=True)

            return HttpResponse("ok")
        else:
            return HttpResponse("no")

@csrf_exempt
def vue_add_interest_sb(request):
    user_id = request.POST.get("id")

    if SupportBusiness.objects.get(id=request.POST.get("val")) not in AdditionalUserInfo.objects.get(id=user_id).interest.all():
        AdditionalUserInfo.objects.get(id=user_id).interest.add(SupportBusiness.objects.get(id=request.POST.get("val")))
        return HttpResponse("ok-add")
    else:
        AdditionalUserInfo.objects.get(id=user_id).interest.remove(SupportBusiness.objects.get(id=request.POST.get("val")))
        return HttpResponse("ok-remove")

@csrf_exempt
def vue_add_interest_st(request):
    user_id = request.POST.get("id")
    if Startup.objects.get(id=request.POST.get("val")) not in AdditionalUserInfo.objects.get(id=user_id).interest_startup.all():
        AdditionalUserInfo.objects.get(id=user_id).interest_startup.add(Startup.objects.get(id=request.POST.get("val")))
        return HttpResponse("ok-add")
    else:
        AdditionalUserInfo.objects.get(id=user_id).interest_startup.remove(Startup.objects.get(id=request.POST.get("val")))
        return HttpResponse("ok-remove")
@csrf_exempt
def vue_my_interest_set(request):
    user_id = request.POST.get("id")
    return JsonResponse(list(AdditionalUserInfo.objects.get(id=user_id).interest_startup.all().values("id")), safe=False)

@csrf_exempt
def vue_my_interest_set_detail(request):
    user_id = request.POST.get("id")
    st_list=[]
    for k in  (AdditionalUserInfo.objects.get(id=user_id).interest_startup.all().values("id")):
        st_list.append(k["id"])
    st = Startup.objects.all().filter(id__in=st_list)
    result = []
    for s in st:
        temp_obj = {}
        temp_obj["name"] = s.name
        temp_obj["short_desc"] = s.short_desc
        temp_obj["tag"] = []
        temp_obj["id"] = s.id
        for t in s.tag.all():
            if t.name != "" and t.name != None:
                temp_obj["tag"].append(t.name)
        result.append(copy.deepcopy(temp_obj))
    return JsonResponse(list(result), safe=False)
@csrf_exempt
def vue_signup(request):
    print(request.method)
    print(request.POST)
    print(LoginForm)
    if request.method == "POST":

        form = LoginForm(request.POST)
        if form.is_valid() and \
                        EmailConfirmation.objects.all().filter(email=form.cleaned_data["username"]).order_by("-id")[
                            0].confirmation_code == request.POST.get("confirmation_code"):
            user = User.objects.create_user(username=form.cleaned_data["username"],
                                            password=form.cleaned_data["password"])
            EmailConfirmation.objects.all().filter(email=form.cleaned_data["username"]).order_by("-id")[0].confirm = True
            if user is not None:
                AdditionalUserInfo(user=user).save()
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
                if user is not None:
                    login(request, user)
                return JsonResponse({"result":"ok","id":user.additionaluserinfo.id, "user":"u"})
            else:
                return JsonResponse({"result":"false"})


def handle_uploaded_file_movie(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/movie/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/movie/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/movie')
    with open('media/uploads/user/'+ str(user_id) +'/company/movie/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/user/'+ str(user_id) +'/company/movie/'+filename

@csrf_exempt
def vue_upload_clip(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    clip = Clip()
    clip.user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    clip.save()
    if request.FILES.get("file_1"):
        if rjd["file_name"] == request.FILES.get("file_1").name:
            path = handle_uploaded_file_movie(request.FILES['file_1'], str(request.FILES['file_1']),
                                                      rjd["user_id"])
            clip.mov_address = path
    clip.thumb = "https://img.youtube.com/vi/"+rjd["youtube_id"]+"/0.jpg"
    clip.title =rjd["title"]
    for t in rjd["filter_p"]:
        clip.filter.add(EduFilter.objects.get(name=t.replace("#  ","")))
        print(t)
    clip.play = int(rjd["time"])
    print(rjd["time"])
    clip.youtube = rjd["youtube_id"]
    clip.info =  rjd["info"]
    clip.object = rjd["object"]
    clip.save()
    return JsonResponse({"result":"ok"})

@csrf_exempt
def vue_get_lec_tag(request):
    result={}
    result["tag"]=[]
    for filter in EduFilter.objects.all():
        temp={}
        temp["id"] = filter.id
        temp["name"] = filter.name
        result["tag"].append(copy.deepcopy(temp))
    return JsonResponse(result)

import urllib.request


@csrf_exempt
def vue_get_clip_uploaded(request):
    clip_list = Clip.objects.filter(user_id = request.POST.get("id"))
    print("kre")
    result={}
    result["clip"]=[]
    ip = urllib.request.urlopen('https://api.ipify.org/').read().decode()
    result["ip"] = ip
    for c in clip_list:
        temp={}
        temp["title"] = c.title
        temp["created_at"] = c.created_at
        temp["user"] = c.user.name
        temp["play"] = c.play
        temp["thumb"] = c.thumb
        temp["id"] = c.id
        result["clip"].append(copy.deepcopy(temp))
    return  JsonResponse(result)


@csrf_exempt
def vue_upload_course(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    course = Course()
    course.user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    course.save()
    if request.FILES.get("file1"):
        if rjd["img_name"] == request.FILES.get("file1").name:
            path = handle_uploaded_file_movie(request.FILES['file1'], str(request.FILES['file1']),
                                              rjd["user_id"])
            course.thumb = path
    course.title = rjd["title"]
    for t in rjd["filter_p"]:
        course.filter.add(EduFilter.objects.get(name=t.replace("#  ", "")))

    for t in rjd["clip_list"]:
        course.clips.add(Clip.objects.get(id=t))
    course.info = rjd["info"]
    course.object = rjd["object2"]

    course.rec_dur = rjd["object"]
    course.save()
    return JsonResponse({"result": "ok"})


@csrf_exempt
def vue_get_course_uploaded(request):
    course_list = Course.objects.all().filter(user_id = request.POST.get("id"))
    result={}
    result["course_set"]=[]
    for c in course_list:
        temp={}
        temp["id"] = c.id
        temp["created"] = c.created_at
        temp["title"] = c.title
        temp["filter"] = []
        print(c.clips.all().first())
        try:
            temp["entry_point"]= "/course/view/"+str(c.id)+"/"+str(c.clips.all().first().id)
        except:
            temp["entry_point"] = ""
        for f in c.filter.all():
            print(f.name)
            temp["filter"].append(f.name)
        temp["rec_dur"] = c.rec_dur
        temp["info"] = c.info
        temp["clips"] = []
        for clip in c.clips.all():
            ttem={}
            ttem["title"]= clip.title
            ttem["created"] = clip.created_at
            ttem["play"] = clip.play
            ttem["int"] = len(clip.additionaluserinfo_set.all())
            temp["clips"].append(copy.deepcopy(ttem))
        result["course_set"].append(copy.deepcopy(temp))
    return JsonResponse(result)

@csrf_exempt
def vue_upload_path(request):
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    path = Path()
    path.user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    path.save()
    if request.FILES.get("file1"):
        if rjd["img_name"] == request.FILES.get("file1").name:
            path = handle_uploaded_file_movie(request.FILES['file1'], str(request.FILES['file1']),
                                              rjd["user_id"])
            path.thumb = path
    path.title = rjd["title"]

    for t in rjd["filter_p"]:
        path.filter.add(EduFilter.objects.get(name=t.replace("#  ", "")))

    for t in rjd["course_list"]:
        path.course.add(Course.objects.get(id=t))

    path.info = rjd["info"]
    path.rec_dur = rjd["object"]
    path.object = rjd["object2"]
    path.save()
    return JsonResponse({"result": "ok"})


@csrf_exempt
def vue_get_clip(request):
    result={}
    clip= Clip.objects.get(id=request.POST.get("id"))
    result["ip"]=  urllib.request.urlopen('https://api.ipify.org/').read().decode()
    if request.POST.get("user"):
        if clip in AdditionalUserInfo.objects.get(id= request.POST.get("user")).interest_clip.all() :
            result["int_clip"] = "true"
        else:
            result["int_clip"] = "false"
    result["title"] = clip.title
    result["youtube"] = clip.youtube
    result["mov_address"] = clip.mov_address
    result["object"] = clip.object
    result["info"] = clip.info
    result["play"] = clip.play
    result["user"] = clip.user.name
    result["created"] = clip.created_at
    result["int"] = len(clip.additionaluserinfo_set.all())
    result["tag"]=[]
    for  t in clip.filter.all():
        result["tag"].append(t.name)

    result["another_clip"]=[]
    for c in Clip.objects.all().order_by("?")[:4]:
        temp={}
        temp["id"] = c.id
        temp["play"] = c.play
        temp["title"] = c.title
        result["another_clip"].append(copy.deepcopy(temp))

    result["another_course"] = []
    for c in Course.objects.all().order_by("?")[:2]:
        temp = {}
        temp["id"] = c.id
        temp["title"] = c.title
        result["another_course"].append(copy.deepcopy(temp))


    return JsonResponse(result)


@csrf_exempt
def vue_get_course(request):
    result={}
    clip= Clip.objects.get(id=request.POST.get("clip"))
    result["title"] = clip.title
    result["youtube"] = clip.youtube
    result["mov_address"] = clip.mov_address
    result["object"] = clip.object
    result["info"] = clip.info
    result["play"] = clip.play
    result["user"] = clip.user.name
    result["created"] = clip.created_at
    result["int"] = len(clip.additionaluserinfo_set.all())
    result["clip_id"] = clip.id
    result["tag"] = []
    for t in clip.filter.all():
        result["tag"].append(t.name)
    result["another_clip"]=[]
    k=1
    for c in Course.objects.get(id=request.POST.get("id")).clips.all():
        temp={}
        temp["index"] = k
        k=k+1
        temp["id"] = c.id
        temp["play"] = c.play
        temp["title"] = c.title
        result["another_clip"].append(copy.deepcopy(temp))



    return JsonResponse(result)


@csrf_exempt
def vue_get_path(request):
    result={}
    clip= Clip.objects.get(id=request.POST.get("clip"))
    result["title"] = clip.title
    result["youtube"] = clip.youtube
    result["mov_address"] = clip.mov_address
    result["object"] = clip.object
    result["info"] = clip.info
    result["clip_id"] = clip.id
    result["int"] = len(clip.additionaluserinfo_set.all())
    result["play"] = clip.play
    result["user"] = clip.user.name
    result["created"] = clip.created_at
    result["another_course"]=[]
    k=1
    a=1
    for c in Path.objects.get(id=request.POST.get("id")).course.all():
        temp={}
        temp["index"]=a
        a=a+1
        k = 1
        temp["id"] = c.id
        temp["title"] = c.title
        temp["clips"]=[]
        for clip in c.clips.all():
            ttem={}
            ttem["index"] = k
            k = k + 1
            ttem["id"] = clip.id
            ttem["play"] = clip.play
            ttem["title"] = clip.title
            temp["clips"].append(copy.deepcopy(ttem))
        result["another_course"].append(copy.deepcopy(temp))
    return JsonResponse(result)


@csrf_exempt
def get_startup_application(request):
    ad_user = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    user = ad_user.user
    st = Startup.objects.get(user_id=user.id)
    result={}
    result["interest"] = []
    for inte in AdditionalUserInfo.objects.get(id=request.POST.get("id")).interest.all():
        temp={}
        temp["title"] = inte.title
        temp["int"] = len(inte.additionaluserinfo_set.all())
        if inte.recruit_size == "":
            temp["comp"] = "없음"
        else:
            temp["comp"] = len(Appliance.objects.all().filter(sb=inte)) / int(inte.recruit_size)
            temp["comp"] = round(temp["comp"],2)
        temp["date"] = str(inte.apply_end).split(" ")[0]
        temp["start"] = str(inte.apply_start).split(" ")[0]
        temp["id"] = inte.id

        result["interest"].append(copy.deepcopy(temp))
    #작성중인 지원서
    result["writing"]=[]
    for ap in Appliance.objects.all().filter(startup=st).filter(is_submit=False):
        temp = {}
        temp["title"] = ap.sb.title
        temp["int"] = len(ap.sb.additionaluserinfo_set.all())
        temp["sb_id"] = ap.sb.id
        if ap.sb.recruit_size == "":
            temp["comp"] = "없음"
        else:
            temp["comp"] = len(Appliance.objects.all().filter(sb=ap.sb)) / int(ap.sb.recruit_size)
            temp["comp"] = round(temp["comp"], 2)
        temp["date"] = str(ap.sb.apply_end).split(" ")[0]
        temp["start"] = str(ap.sb.apply_start).split(" ")[0]
        temp["id"] = ap.id
        result["writing"].append(copy.deepcopy(temp))
        # 지원완료 지원서
    result["comp"] = []
    for ap in Appliance.objects.all().filter(startup=st).filter(is_submit=True):
        temp = {}
        temp["title"] = ap.sb.title
        temp["int"] = len(ap.sb.additionaluserinfo_set.all())
        if ap.sb.recruit_size == "":
            temp["comp"] = "없음"
        else:
            temp["comp"] = len(Appliance.objects.all().filter(sb=ap.sb)) / int(ap.sb.recruit_size)
            temp["comp"] = round(temp["comp"], 2)
        temp["date"] = str(ap.sb.apply_end).split(" ")[0]
        temp["start"] = str(ap.sb.apply_start).split(" ")[0]
        temp["id"] = ap.id
        temp["sb_id"]=ap.sb.id
        result["comp"].append(copy.deepcopy(temp))
    return JsonResponse(result)

@csrf_exempt
def vue_remove_service_product(request):
    st = Startup.objects.get(user_id = AdditionalUserInfo.objects.get(id=request.POST.get("id")).user.id)
    Service.objects.all().filter(startup=st).filter(id=request.POST.get("service_id")).delete()
    return  JsonResponse({"result":"ok"})
from django.core.serializers import serialize
from django.forms.models import model_to_dict

@csrf_exempt
def vue_del_startup_news(request):
    rjd = json.loads(request.POST.get("json_data"))
    Activity.objects.get(id=rjd["id"]).delete()
    return JsonResponse({"result":"ok"})



@csrf_exempt
def vue_get_user_info(request):
    ad =  AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    result={}
    result["phone"] = ad.tel
    result["name"] = ad.name
    result["agreement"]= ad.agreement
    result["email"] = ad.user.username
    return JsonResponse({"result":result})


@csrf_exempt
def get_home_info(request):
    gr = SupportBusiness.objects.all().order_by("?")[:6]
    result={}
    result["sb_set"] = []
    for g in gr:
        team={}
        team["title"] = g.title
        team["due"] = g.apply_end
        team["short_desc"] = g.short_desc
        team["tag"]=[]
        for f in g.filter.all():
            team["tag"].append(f.name)
        team["poster"]= g.poster
        team["id"] = g.id
        result["sb_set"].append(copy.deepcopy(team))



    return JsonResponse(result)

@csrf_exempt
def vue_get_startup_list_sample(request):
    st = Startup.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["name"] = s.name
        temp_obj["short_desc"] = s.short_desc
        temp_obj["tag"]=[]
        temp_obj["id"]=s.id
        for t in s.tag.all():
            if t.name != "" and t.name != None:
                temp_obj["tag"].append(t.name)
        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)
@csrf_exempt
def vue_sample_list_sample(request):
    st = Startup.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["name"] = s.name
        temp_obj["short_desc"] = s.short_desc
        temp_obj["tag"]=[]
        temp_obj["id"]=s.id
        for t in s.tag.all():
            if t.name != "" and t.name != None:
                temp_obj["tag"].append(t.name)
        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)


@csrf_exempt
def vue_sample_list_clip(request):
    st = Clip.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["title"] = s.title
        temp_obj["thumb"] = s.thumb
        temp_obj["mov_address"]=s.mov_address
        temp_obj["youtube"]=s.youtube
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info

        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)

@csrf_exempt
def vue_sample_course_path(request):
    st = Course.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["title"] = s.title
        temp_obj["thumb"] = s.thumb
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info

        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)


@csrf_exempt
def vue_sample_path_path(request):
    st = Course.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["title"] = s.title
        temp_obj["thumb"] = s.thumb
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info
        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)

@csrf_exempt
def vue_get_statics_by_channel(request):
    path = Path.objects.all()
    result = {}
    result["path"]=[]
    for p in path:
        temp_path={}
        temp_path["title"] = p.title
        temp_path["id"] = p.id
        temp_path["course"] = []
        for c in p.course.all():
            temp_course = {}
            temp_course["id"] = c.id

            temp_course["title"] = c.title
            temp_course["clip"] = []
            for clip in c.clips.all():
                print("why")
                temp_clip = {}
                temp_clip["title"] = clip.title
                temp_clip["id"] = clip.id

                temp_course["clip"].append(copy.deepcopy(temp_clip))
            temp_path["course"].append(copy.deepcopy(temp_course))
        result["path"].append( copy.deepcopy(temp_path))
    return  JsonResponse(result)

import requests
import urllib.request
@csrf_exempt
def vue_get_sns_auth(request):
    provider = request.POST.get("provider")
    token = request.POST.get("token")
    print(provider)
    print(token)
    if provider == "naver":
        # 접근 토큰 발급 받기
        url = "https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id=MonomZR2k6j8bS3LEFvy&client_secret=J1ll08KKVd&code="+token+"&state=aaa"
        re = requests.get(url)
        print(re.text)
        header = "Bearer " + re.json()["access_token"]  # Bearer 다음에 공백 추가
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": header}
        re = requests.get(url, headers=headers)
        print(re.json()["response"]["nickname"])
        print(re.json()["response"]["name"])
        print(re.json()["response"]["email"])
        print(re.json()["response"]["profile_image"])

        name = (re.json()["response"]["name"])
        email = re.json()["response"]["email"]
    if provider == "kakao":
        url = "https://kapi.kakao.com/v2/user/me"
        re = requests.get(url)
        header = "Bearer " + token  # Bearer 다음에 공백 추가
        headers = {"Authorization": header}
        re = requests.post(url, headers=headers,)
        print(re.text)
        print(re.json()["properties"]["nickname"])
        print(re.json()["kakao_account"]["email"])
        print(re.json()["properties"]["profile_image"])
        name = re.json()["properties"]["nickname"]
        email =re.json()["kakao_account"]["email"]

    if provider =="facebook":
        url = "https://graph.facebook.com/v3.0/oauth/access_token?client_id=162083444444485&redirect_uri=http://gconnect.kr/login&client_secret=1916c66420a16d82b106718eaa8b0ee1&code="+token

        re = requests.get(url)
        print(re.text)
        print(re.json()["access_token"])
        access_token = re.json()["access_token"]
        url = "https://graph.facebook.com/debug_token?input_token="+re.json()["access_token"]+"&access_token=162083444444485|1916c66420a16d82b106718eaa8b0ee1"
        re = requests.get(url)
        print(re.json()["data"]["user_id"])
        url = "https://graph.facebook.com/"+re.json()["data"]["user_id"]+"?fields=id,name,first_name,last_name,age_range,link,gender,locale,picture,timezone,updated_time,verified,email&access_token="+access_token
        re = requests.get(url)
        print(re.json()["name"])
        name = re.json()["name"]
        email = re.json()["email"]
    print(email)

    # user = User.objects.create_user(email, "", "snslogin12")
    # print(user)
    # if user is not None:
    #     login(request, user)
    #
    # user_p  = AdditionalUserInfo()
    # user_p.user = user
    # user_p.save()
    # st = Startup()
    # st.user = user
    # st.save()

    return JsonResponse({"name":name, "user_id":  189 })


@csrf_exempt
def vue_get_startup_detail_manager(request):
    print(request.GET.get("id"))
    # st= AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    st = AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    result = {}

    result["back_img"] = st.back_img
    result["logo"] = st.logo

    result["startup_id"] = st.id
    result["name"] = st.name
    # result["logo"] = st.thumbnail
    result["short_desc"] = st.short_desc
    result["intro_text"] = st.intro_text
    result["information"] = {}
    result["information"]["id"] = st.id
    result["information"]["tag"] = []
    for t in st.tag.all():
        if t.name != "" and t.name != None:
            result["information"]["tag"].append(t.name)
    result['information']["homepage"] = st.website
    result['information']["email"] = st.user.username
    result["location"] = st.address_0
    try:
        result["business_file"] = st.business_file.split("/")[-1]
    except:
        result["business_file"]=""
    result["business_file_path"] = st.business_file
    if result["business_file"] == "":
        result["business_file"] = "파일을 업로드 하세요."
        result["business_file_path"] = ""
    result["service"] = []
    result["tag"] = []

    for f in st.filter.all():
        result["tag"].append(f.name)

    for service in st.service_set.all():
        obj = {}
        obj["intro"] = service.intro
        obj["file"] = service.file
        obj["file_name"] = service.file.split("/")[-1]
        obj["name"] = service.name
        obj["img"] = service.img
        obj["img_name"] = service.img.split("/")[-1]
        obj["id"] = service.id
        result["service"].append(copy.deepcopy(obj))
    result["history"] = []
    for history in st.history_set.all():
        obj = {}
        obj["year"] = history.year
        obj["month"] = history.month
        obj["content"] = history.content
        obj["id"] = history.id
        result["history"].append(copy.deepcopy(obj))
    result["revenue"] = []
    for revenue in st.revenue_set.all():
        obj = {}
        obj["year"] = revenue.year
        obj["num"] = revenue.size
        obj["id"] = revenue.id
        result["revenue"].append(copy.deepcopy(obj))
    result["trade"] = []
    for trade in st.tradeinfo_set.all():
        obj = {}
        obj["year"] = trade.year
        obj["size"] = trade.size
        obj["id"] = trade.id
        result["trade"].append(copy.deepcopy(obj))
    result["invest"] = []
    for invest in st.fund_set.all():
        obj = {}
        obj["year"] = invest.year
        obj["size"] = invest.size
        obj["agency"] = invest.agency
        obj["step"] = invest.step
        obj["currency"] = invest.currency
        result["invest"].append(copy.deepcopy(obj))
    result["news"] = []
    result["news"] = []

    for news in st.activity_set.order_by("-created_at").all():
        obj = {}
        obj["date"] = news.created_at
        obj["content"] = news.text
        obj["img"] = news.img

        obj["like_num"] = len(news.activitylike_set.all())
        obj["rep_num"] = len(news.reply_set.all())
        obj["id"] = news.id
        obj["rep"] = []
        for rep in news.reply_set.all():
            temp = {}
            # temp["logo"] = rep.activity.startup.thumbnail
            temp["content"] = rep.text
            temp["date"] = rep.created_at
            temp["id"] = rep.id
            obj["rep"].append(copy.deepcopy(temp))
        result["news"].append(copy.deepcopy(obj))
    return JsonResponse(result)


@csrf_exempt
def vue_get_grant_detail(request):
    sp = SupportBusiness.objects.get(id=request.GET.get("id"))
    ap = len(Appliance.objects.all().filter(sb=sp))
    if sp.recruit_size == 0 or sp.recruit_size == None or sp.recruit_size =="":
        comp="없음"
    else:
        print(sp.recruit_size)
        comp =  str(round(int(ap)/int(sp.recruit_size),2))+":1"

    view = len(HitLog.objects.all().filter(sb=sp))
    inte = len(sp.additionaluserinfo_set.all())

    return JsonResponse({"result": serialize('json',[sp,]),"comp":comp , "view":view,"int":inte,"ap":ap })


@csrf_exempt
def vue_get_manager_list(request):
    id = request.POST.get("id")
    managers = AdditionalUserInfo.objects.get(id=id).additionaluserinfo_set.all()
    m_list= []
    for m in managers:
        temp={}
        temp["id"] = m.id
        temp["name"] = m.name
        temp["grant"] =[]
        for s in SupportBusiness.objects.all().filter(user=m):
            ttem={}
            ttem["title"] = s.title
            ttem["id"] = s.id
            temp["grant"].append(copy.deepcopy(ttem))

        m_list.append(copy.deepcopy(temp))
    return JsonResponse(m_list, safe = False)

@csrf_exempt
def vue_get_grant_ttl(request):
    sb = SupportBusiness.objects.get(id=request.GET.get("gr"))
    temp={}
    temp["title"] = sb.title
    temp["start"] = sb.apply_start
    temp["end"] = sb.apply_end
    temp["pro_0_open"]= sb.pro_0_end
    if sb.recruit_size =="" or  sb.recruit_size == None or  sb.recruit_size ==0:
        temp["comp"] = "없음"
    else:
        temp["comp"] = str(round(len(Appliance.objects.all().filter(sb=sb))/sb.recruit_size,2) ) +":1"


    return  JsonResponse(temp, safe=False)


@csrf_exempt
def toggle_int_clip(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    if clip in ad.interest_clip.all():
        ad.interest_clip.remove(clip)
    else:
        ad.interest_clip.add(clip)
    return JsonResponse({"result":"ok"})

@csrf_exempt
def vue_hit_clip_log(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    HitClipLog.objects.get_or_create(clip=clip, user=ad)

@csrf_exempt
def vue_watch_clip_history(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    WatchClipHistory.objects.create(clip=clip, user=ad)


@csrf_exempt
def vue_hit_course_log(request):
    print("?")
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    HitCourseLog.objects.get_or_create(clip=clip, user=ad, course= course)
    return  JsonResponse({"result":"ok"})
@csrf_exempt
def vue_watch_course_history(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    WatchCourseHistory.objects.create(clip=clip, user=ad, course=course)
    return JsonResponse({"result": "ok"})

@csrf_exempt
def vue_hit_path_log(request):
    print("--")
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    path = Path.objects.get(id=request.POST.get("path"))
    HitPathLog.objects.get_or_create(clip=clip, user=ad, course= course,path=path)

@csrf_exempt
def vue_watch_path_history(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    path = Path.objects.get(id=request.POST.get("path"))
    WatchPathHistory.objects.create(clip=clip, user=ad, course=course, path=path)



@csrf_exempt
def vue_get_ing_lecture(request):
    result={}
    result["path_list"] = []
    for p in HitPathLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.path.title
        t["id"]=p.path.id
        t["created"] = p.path.created_at
        t["user"] = p.path.user.name
        t["play"] = p.path.total_play
        t["thumb"] = p.path.thumb
        t["entry_point"] = "/path/view/"+str(p.path.id) + "/" + str(p.course.id) + "/" + str(p.clip.id)

        result["path_list"].append(copy.deepcopy(t))
    result["course_list"] =[] # = HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in HitCourseLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.course.title
        t["id"]=p.course.id
        t["created"] = p.course.created_at
        t["user"] = p.course.user.name
        t["play"] = p.course.total_play
        t["thumb"] = p.course.thumb
        t["entry_point"] = "/course/view/"+str(p.course.id) + "/"+str(p.clip.id)
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in HitClipLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.clip.title
        t["id"]=p.clip.id
        t["created"] = p.clip.created_at
        t["user"] = p.clip.user.name
        t["play"] = p.clip.play
        t["thumb"] = p.clip.thumb

        result["clip_list"].append(copy.deepcopy(t))


    return JsonResponse({'results':result })



@csrf_exempt
def vue_get_manager_lecture(request):
    result={}
    result["path_list"] = []
    for p in Path.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.name
        t["play"] = p.total_play
        t["thumb"] = p.thumb
        #t["entry_point"] = "/path/view/"+str(p.id) + "/" + str(p.course.all().first().id) + "/" + str(p.course.all().first().clips.all().first().id)
        t["entry_point"]=""
        for c in p.course.all():
            for clip in c.clips.all():
                if(c.id and clip.id):
                    t["entry_point"] = "/path/view/"+str(p.id) + "/" + str(c.id) + "/" + str(clip.id)
        result["path_list"].append(copy.deepcopy(t))
    result["course_list"] =[] # = HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in Course.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.name
        t["play"] = p.total_play
        t["thumb"] = p.thumb
        try:
            t["entry_point"] = "/course/view/"+str(p.id) + "/"+str(p.clips.first().id)
        except:
            t["entry_point"] = ""
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in Clip.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.name
        t["play"] = p.play
        t["thumb"] = p.thumb

        result["clip_list"].append(copy.deepcopy(t))



    return JsonResponse({'results':result })



@csrf_exempt
def vue_toggle_fav_clip(request):
    ad = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    cl = Clip.objects.get(id=request.GET.get("clip_id"))
    if cl in ad.interest_clip.all():
        ad.interest_clip.remove(cl)
    else:
        ad.interest_clip.add(cl)
        fv = FavClipLog()
        fv.user = ad
        fv.Clip = cl
        fv.save()

@csrf_exempt
def vue_toggle_fav_course(request):
    ad = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    cl = Course.objects.get(id=request.GET.get("course_id"))
    if cl in ad.interest_course.all():
        ad.interest_course.remove(cl)
    else:
        ad.interest_course.add(cl)
        fv = FavCourseLog()
        fv.user = ad
        fv.Course = cl
        fv.save()


@csrf_exempt
def vue_toggle_fav_path(request):
    ad = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    cl = Path.objects.get(id=request.GET.get("course_id"))
    if cl in ad.interest_path.all():
        ad.interest_path.remove(cl)
    else:
        ad.interest_path.add(cl)
        fv = FavPathLog()
        fv.user = ad
        fv.Path = cl
        fv.save()


@csrf_exempt
def vue_get_channel_statics_path(request):
    path = Path.objects.get(id=request.GET.get("path_id"))
    fav_date_list = FavPathLog.objects.all().filter(Path=path).order_by("date").values("date").distinct()
    result={}
    result["fav_static"]=[]
    for fd in fav_date_list:
        temp={}
        temp["date"] = fd["date"]
        temp["number"] = len(FavPathLog.objects.filter(Path=path).filter(date = fd["date"]))
        result["fav_static"].append(copy.deepcopy(temp))

    watch_time = WatchPathHistory.objects.all().filter(Path=path).order_by("date").values("date").distinct()
    result["watch_static"]=[]
    for i in watch_time:
        temp={}
        temp["date"] = i["date"]
        temp["number"]= len(WatchPathHistory.objects.all().filter(Path=path).filter(date=i["date"]))*6
        result["watch_static"].append(copy.deepcopy(temp))

    local_list=[]
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_1=="소재지":
                local_list.append(t.name)
    kind_list=[]
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                kind_list.append(t.name)
    em_list=[]
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                kind_list.append(t.name)
    field_list = []
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.name)
    user_list=[]
    for u in path.additionaluserinfo_set.all():
        if u not in user_list:
            user_list.append(u)
    for u in FavPathLog.objects.all().filter(Path=path):
        if u.user not in user_list:
            user_list.append(u.user)
    for u in HitPathLog.objects.all().filter(path=path):
        if u.user not in user_list:
            user_list.append(u.user)
    for u in WatchPathHistory.objects.all().filter(Path=path):
        if u.user not in user_list:
            user_list.append(u.user)
    result_user=[]
    for u in user_list:
        temp={}
        temp["name"]= u.name
        result_user.append(copy.deepcopy(temp))


    return JsonResponse({"line":result, "path_kind_tag":organize(kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list), "user":result_user })


@csrf_exempt
def vue_get_channel_statics_course(request):
    course = Course.objects.get(id=request.GET.get("course_id"))
    fav_date_list = FavCourseLog.objects.all().filter(Course=course).values("date").distinct()
    result={}
    result["fav_static"]=[]
    for fd in fav_date_list:
        temp={}
        temp["date"] = fd["date"]
        temp["number"] = len(FavCourseLog.objects.filter(Course=course).filter(date = fd["date"]))
        result["fav_static"].append(copy.deepcopy(temp))

    watch_time = WatchCourseHistory.objects.all().filter(course=course).values("date").distinct()
    result["watch_static"]=[]
    for i in watch_time:
        temp={}
        temp["date"] = i["date"]
        temp["number"]= len(WatchCourseHistory.objects.all().filter(Course=course).filter(date=i["date"]))*6
        result["watch_static"].append(copy.deepcopy(temp))

    local_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_1=="소재지":
                local_list.append(t.name)
    kind_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                kind_list.append(t.name)
    em_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                kind_list.append(t.name)
    field_list = []
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.name)

    return JsonResponse({"line":result, "path_kind_tag":organize(kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list),  })


@csrf_exempt
def vue_get_channel_statics_clip(request):
    clip = Clip.objects.get(id=request.GET.get("clip_id"))
    fav_date_list = FavClipLog.objects.all().filter(Clip=clip).values("date").distinct()
    result={}
    result["fav_static"]=[]
    for fd in fav_date_list:
        temp={}
        temp["date"] = fd["date"]
        temp["fav_num"] = len(FavClipLog.objects.filter(Clip=clip).filter(date = fd["date"]))
        result["fav_static"].append(copy.deepcopy(temp))

    watch_time = WatchClipHistory.objects.all().filter(clip=clip).values("date").distinct()
    result["watch_static"]=[]
    for i in watch_time:
        temp={}
        temp["date"] = i["date"]
        temp["watch_num"]= len(WatchClipHistory.objects.all().filter(Clip=clip).filter(date=i["date"]))*6
        result["watch_static"].append(copy.deepcopy(temp))

    local_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_1=="소재지":
                local_list.append(t.name)
    kind_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                kind_list.append(t.name)
    em_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                kind_list.append(t.name)
    field_list = []
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.name)

    return JsonResponse({"line":result, "path_kind_tag":organize(kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list),  })







def appliance_all_download(request, sb):
    ap_list = Appliance.objects.filter(sb_id=sb)
    zip_filename = "%s.zip" % (
        str(ap_list[0].sb.apply_end).split("-")[
            0] + "_" + ap_list[0].sb.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list[4:5]:
        zip_subdir = "applicance"
        url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(ap.id)
        subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
        print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
        if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
            zip_path = os.path.join(ap.startup.name + "/지원서.pdf")
            zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
            time.sleep(1)
        if ap.business_file != "":
            fdir, fname = os.path.split(ap.business_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업자등록증." + fname.split(".")[-1])
            zf.write(ap.business_file.path, zip_path)
        if ap.fund_file != "":
            fdir, fname = os.path.split(ap.fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(ap.fund_file.path, zip_path)
        if ap.etc_file != "":
            fdir, fname = os.path.split(ap.etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(ap.etc_file.path, zip_path)
        if ap.ir_file != "":
            fdir, fname = os.path.split(ap.ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(ap.ir_file.path, zip_path)
        if ap.ppt_file != "":
            fdir, fname = os.path.split(ap.ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(ap.ppt_file.path, zip_path)
        if ap.tax_file != "":
            fdir, fname = os.path.split(ap.tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(ap.tax_file.path, zip_path)
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원자 리스트")
    sheet.write(0, 0, "순서")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "업종")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "사업자 등록번호")
    sheet.write(0, 5, "이메일")
    sheet.write(0, 6, "대표 전화번호")
    sheet.write(0, 7, "필터")
    k = 1
    for a in ap_list:
        sheet.write(k, 0, k)
        sheet.write(k, 1, a.startup.name)
        sheet.write(k, 2, a.startup.category)
        sheet.write(k, 3, a.startup.user.additionaluserinfo.name)
        sheet.write(k, 4, Appliance.objects.all().filter(sb_id=sb).filter(startup_id=a.startup.id)[0].business_number)
        sheet.write(k, 5, a.startup.user.username)
        sheet.write(k, 6, a.startup.user.additionaluserinfo.tel)
        filter_list = a.startup.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.name)
        sheet.write(k, 7, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    zf.writestr("전체 리스트.xls", f.getvalue())

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


import zipfile
def getfiles(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = ["/home/ubuntu/google.pdf"]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "somefiles"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s =  io.BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp

def vue_get_clip_all(request):
    result = []
    for c in Clip.objects.all():
        temp={}
        temp["id"] = c.id
        temp["user"]=c.user.name
        temp["img"]=c.thumb
        temp["title"]=c.title
        temp["dur"]=c.play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)


def vue_get_course_all(request):
    result = []
    for c in Course.objects.all():
        temp={}
        temp["id"] = c.id
        try:
            temp["entry_point"] = "/course/view/"+ str(c.id)+"/" + str(c.clips.all().first().id)
        except:
            temp["entry_point"]=""
        temp["user"]=c.user.name
        temp["img"]=c.thumb
        temp["title"]=c.title
        temp["dur"]=c.total_play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)



def vue_get_path_all(request):
    result = []
    for c in Path.objects.all():
        temp={}
        temp["id"] = c.id
        try:
            temp["entry_point"] = "/path/view/"+ str(c.id)+"/"+ str(c.course.all().first().id) + "/"+ str(c.course.all().first().clips.all().first().id)
        except:
            temp["entry_point"]=""
        temp["user"]=c.user.name
        temp["img"]=c.thumb
        temp["title"]=c.title
        temp["dur"]=c.total_play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)