# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import string
import random
from .forms import *
from django.utils import timezone
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
from zipfile import ZipFile
import ffmpeg
import requests
import urllib.request

### for auth
try:
     # Django versions >= 1.9

    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend




@csrf_exempt
def is_in_favor_list(target,id, additionaluserinfo_id):
    try:
        user = AdditionalUserInfo.objects.get(id=additionaluserinfo_id)

        if target  == "support_business":
            if SupportBusiness.objects.get(id=id) in user.favorite.all():
                return True
            else:
                return False
        if target  == "clip":
            if Clip.objects.get(id=id) in user.favorite_clip.all():
                return True
            else:
                return False
        if target  == "course":
            print("course check")
            if Course.objects.get(id=id) in user.favorite_course.all():
                return True
            else:
                return False
        if target  == "path":
            if Path.objects.get(id=id) in user.favorite_path.all():
                return True
            else:
                return False

        if target  == "startup":
            print("startup check!!!")
            if Startup.objects.get(id=id) in user.favorite_startup.all():
                return True;
            else :
                return False
    except:
        return False



 #세션 인증

def gca_check_session(request):
    my_session_key= request.GET.get("session_key")
    my_id = request.GET.get("gca_id")
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(my_session_key)
    session_user_id = ""
    try:
        session_user_id = session[SESSION_KEY]
        backend_path = session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        user = backend.get_user(session_user_id) or AnonymousUser()
        sk_user_id = str(AdditionalUserInfo.objects.get(id=my_id).user.id)
    except KeyError:
        user = AnonymousUser()

    print("sk check")
    if my_session_key == "gca_test":
        return True
    if user.is_authenticated() and str(session_user_id) == sk_user_id :
        return True
    else:
        return False


#----------------------- 매니저 페이징 라우터 ---------------------

#전체 지원사업 라우터
@csrf_exempt
def other_support_business_support_business(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    support_business = SupportBusiness.objects.all().exclude(support_business_status=1).exclude(support_business_status=None)
    total = len(support_business)
    try:
        support_business_result = support_business[start_index:start_index+size]
    except Exception as e :
        print(e)
        support_business_result = ""
    k = 0
    result = {}
    result["result_set"] = []
    for s in support_business_result:
        temp = {}
        temp["mng_id"] = s.id
        temp["mng_index"] = k
        k = k + 1
        temp["mng_support_business_name"] = s.support_business_name
        temp["mng_support_business_apply_start_ymd"] = s.support_business_apply_start_ymd
        temp["mng_author"] = s.support_business_author.mng_name
        temp["mng_mng_team"] = s.support_business_author.mng_team
        temp["mng_mng_kikwan"] = s.support_business_author.mng_kikwan
        temp["mng_mng_tel"] = s.support_business_author.mng_tel
        temp["mng_apply_num"] = len(Appliance.objects.all().filter(support_business=s).filter(is_submit=True))
        temp["mng_award_num"] = len(Award.objects.all().filter(support_business=s))
        try:
            if s.support_business_status == "1":
                mng_status = "작성중"
            elif s.support_business_status == "2":
                mng_status = "승인대기중"
            elif s.support_business_status == "3":
                mng_status = "공고중"
            elif s.support_business_status == "4":
                mng_status = "모집종료"
            elif s.support_business_status == "5":
                mng_status = "공고종료"
            elif s.support_business_status == "6":
                mng_status = "블라인드중"
        except:
            print("error")
            mng_status = ""
        temp["mng_status"] = mng_status
        result["result_set"].append(copy.deepcopy(temp))
    result["total"] =total
    return JsonResponse(result, safe=False)


@csrf_exempt
def mng_account_kikwan_mng_account(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    acc_set = []
    k = start_index
    result={}
    boss_id = AdditionalUserInfo.objects.get(id = request.POST.get("id")).mng_boss_id
    account_set = AdditionalUserInfo.objects.all().filter(mng_boss_id=boss_id).order_by("-id")
    total = len(account_set)
    try:
        account_set_result = account_set[start_index:start_index+size]
    except:
        account_set_result = ""
    for ac in account_set_result:
        temp = {}
        temp["mng_index"] = k
        k = k + 1
        temp["mng_id"] = ac.user.username
        temp["mng_mng_name"] = ac.mng_name
        temp["mng_mng_position"] = ac.mng_position
        temp["mng_mng_bonbu"] = ac.mng_bonbu
        temp["mng_mng_kikwan"] = ac.mng_kikwan
        temp["mng_mng_team"] = ac.mng_team
        temp["mng_mng_tel"] = ac.mng_tel
        temp["mng_mng_phone"] = ac.mng_phone
        temp["mng_mng_email"] = ac.mng_email
        temp["mng_mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        acc_set.append(copy.deepcopy(temp))

    result["account_set"] = acc_set
    result["total"]= total
    return JsonResponse(result, safe=False)

@csrf_exempt
def user_account_person(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    user_set = []
    p = start_index
    result={}
    result["mng_usr_set"]=[]
    user_ad = AdditionalUserInfo.objects.all().exclude(auth=4).exclude(auth=5)
    total = len(user_ad)
    try:
        user_ad_result = user_ad[start_index:start_index+size]
    except Exception as e:
        print(e)
        user_ad_result=""
    for u in user_ad_result:
        try:
            user = {}
            user["mng_id"] = u.user.username
            user["mng_repre_name"] = Startup.objects.get(user=u.user).repre_name
            user["mng_repre_tel"] = Startup.objects.get(user=u.user).repre_tel
            user["mng_joined"] = u.user.date_joined
            user["mng_index"] = p
            p = p+ 1
            print(u.user)

            user_set.append(copy.deepcopy(user))

        except Exception as e:
            print(e)
            pass
    result["mng_usr_set"] = user_set
    result["total"] = total
    return JsonResponse(result, safe=False)

@csrf_exempt
def support_business_detail_appliance(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business"))
    ap = Appliance.objects.all().filter(support_business=support_business).filter(is_submit=True)
    total = len(ap)
    ap_result = ap[start_index:start_index+size]
    k = start_index
    result = {}
    result["appliance"] = []
    for a in ap_result:
        temp = {}
        temp["index"] = k
        k = k + 1
        temp["company_name"] = a.company_name
        temp["company_kind"] = a.company_kind
        temp["id"] = a.id
        temp["repre_name"] = a.repre_name
        temp["repre_email"] = a.repre_email

        temp["repre_tel"] = a.repre_tel
        temp["appliance_update_at_ymdt"] = a.appliance_update_at_ymdt
        temp["down_path"] = a.id
        result["appliance"].append(copy.deepcopy(temp))
    result["total"] = total
    return JsonResponse(result, safe=False)


@csrf_exempt
def support_business_detail_favorite(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    support_business_id = request.GET.get("support_business_id")
    support_business = SupportBusiness.objects.get(id=support_business_id)
    item = support_business.additionaluserinfo_set.all()
    item_result = item[start_index:start_index+size]
    total = len(item)
    result={}
    result["favorite"]=[]
    index = start_index
    for st in item_result:
        kind = st.user.startup.selected_company_filter_list
        kind_l = ""
        for k in kind.all():
            if( k.cat_1 =="기업형태"):
                kind_l = k.filter_name
        result["favorite"].append({
            "id":st.user.startup.id,
            "index":index,
            "company_name":st.user.startup.company_name,
            "company_kind":kind_l,
            "repre_name":st.user.startup.repre_name,
            "username":st.user.username,
            "repre_tel" : st.user.startup.repre_tel,
        })
        index = index+1
    result["total"] = total

    return JsonResponse(result,safe=False)

@csrf_exempt
def support_business_detail_awarded(request):
    support_business_id = request.GET.get("support_business_id")
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    result={}
    win_list = Award.objects.filter(support_business_id=support_business_id)
    total = len(win_list)
    win_list_result = win_list[start_index:start_index+size]
    winner = []
    k = start_index
    for a_w in win_list_result:
        ap, created = Appliance.objects.get_or_create(support_business_id=support_business_id, startup=a_w.startup)
        print(ap)
        winner.append({
            "index": k, "company_name": a_w.startup.company_name, "repre_name": a_w.startup.repre_name,
            "company_kind": a_w.startup.company_kind, "user_id": a_w.startup.user.username,
            "repre_tel": a_w.startup.repre_tel, "repre_email": a_w.startup.repre_email,
            "appliance_update_at_ymdt": str(ap.appliance_update_at_ymdt).split("T")[0]
        })
        k = k + 1
    result["awarded"] = winner
    result["total"] = total

    return JsonResponse(result, safe=False)

@csrf_exempt
def statics_my_support_business_ing_hit(request):
    support_business_id = request.GET.get("support_business_id")
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    result = {}
    support_business = SupportBusiness.objects.get(id=support_business_id)
    startup_list = []
    for hit_startup in HitLog.objects.all().filter(support_business=support_business).values("user").distinct():
        try:
            startup_list.append(Startup.objects.get(user= AdditionalUserInfo.objects.get(id=hit_startup["user"]).user))
        except:
            pass
    result["total"] = len(startup_list)
    result["startup_list"] = []
    k=start_index
    for startup in startup_list:
        filter_list = startup.selected_company_filter_list.all()
        company_kind=""
        local=""
        for filter in filter_list:
            if filter.cat_1 =="기업형태":
                company_kind = (filter.filter_name)
            if filter.cat_1 =="소재지":
                local = (filter.filter_name)
        result["startup_list"].append({
            "startup_id":startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel })
        k = k + 1
    result["startup_list"] = result["startup_list"][start_index:start_index+size]
    return JsonResponse(result, safe=False)

@csrf_exempt
def statics_my_support_business_ing_fav(request):
    support_business_id = request.GET.get("support_business_id")
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    result = {}
    support_business = SupportBusiness.objects.get(id=support_business_id)
    startup_list = []
    for favored_startup in FavoredSupportBusiness.objects.all().filter(favored_support_business=support_business).values("favored_usr").distinct():
        startup_list.append( Startup.objects.get(user= AdditionalUserInfo.objects.get(id=favored_startup["favored_usr"]).user))
    result["total"] = len(startup_list)
    result["startup_list"] = []
    k = start_index
    for startup in startup_list:
        filter_list = startup.selected_company_filter_list.all()
        company_kind = ""
        local = ""
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                company_kind = (filter.filter_name)
            if filter.cat_1 == "소재지":
                local = (filter.filter_name)
        result["startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel})
        k = k + 1
    result["startup_list"] = result["startup_list"][start_index:start_index + size]
    return JsonResponse(result, safe=False)

@csrf_exempt
def statics_my_support_business_ing_appliance(request):
    support_business_id = request.GET.get("support_business_id")
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    result = {}
    support_business = SupportBusiness.objects.get(id=support_business_id)
    startup_list = []
    for applied_startup in Appliance.objects.all().filter(support_business=support_business).values(
            "startup").distinct():
        startup_list.append(Startup.objects.get(id=applied_startup["startup"]))
    result["total"] = len(startup_list)
    result["startup_list"] = []
    k = start_index
    for startup in startup_list:
        filter_list = startup.selected_company_filter_list.all()
        company_kind = ""
        local = ""
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                company_kind = (filter.filter_name)
            if filter.cat_1 == "소재지":
                local = (filter.filter_name)
        result["startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel})
        k = k + 1
    result["startup_list"] = result["startup_list"][start_index:start_index + size]
    return JsonResponse(result, safe=False)



@csrf_exempt
def statics_my_support_business_ing_appliance(request):
    support_business_id = request.GET.get("support_business_id")
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    result = {}
    support_business = SupportBusiness.objects.get(id=support_business_id)
    startup_list = []
    for applied_startup in Appliance.objects.all().filter(support_business=support_business).values(
            "startup").distinct():
        startup_list.append(Startup.objects.get(id=applied_startup["startup"]))
    result["total"] = len(startup_list)
    result["startup_list"] = []
    k = start_index
    for startup in startup_list:
        filter_list = startup.selected_company_filter_list.all()
        company_kind = ""
        local = ""
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                company_kind = (filter.filter_name)
            if filter.cat_1 == "소재지":
                local = (filter.filter_name)
        result["startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel})
        k = k + 1
    result["startup_list"] = result["startup_list"][start_index:start_index + size]
    return JsonResponse(result, safe=False)




#------------------------------------------ 기관 관리자 페이징-------------------------------------

@csrf_exempt
def opr_account_kikwan_mng_account(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    acc_set = []
    k = start_index
    result = {}
    boss_id = AdditionalUserInfo.objects.get(id=request.POST.get("id")).mng_boss_id
    account_set = AdditionalUserInfo.objects.all().filter(mng_boss_id=boss_id).order_by("-id")
    total = len(account_set)
    try:
        account_set_result = account_set[start_index:start_index + size]
    except:
        account_set_result = ""
    for ac in account_set_result:
        temp = {}
        temp["mng_index"] = k
        k = k + 1
        temp["mng_id"] = ac.user.username
        temp["mng_mng_name"] = ac.mng_name
        temp["mng_mng_position"] = ac.mng_position
        temp["mng_mng_bonbu"] = ac.mng_bonbu
        temp["mng_mng_kikwan"] = ac.mng_kikwan
        temp["mng_mng_team"] = ac.mng_team
        temp["mng_mng_tel"] = ac.mng_tel
        temp["mng_mng_phone"] = ac.mng_phone
        temp["mng_mng_email"] = ac.mng_email
        temp["mng_mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        acc_set.append(copy.deepcopy(temp))

    result["account_set"] = acc_set
    result["total"] = total
    return JsonResponse(result, safe=False)

@csrf_exempt
def opr_account_kikwan_all_account(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    acc_set = []
    k = start_index
    result = {}
    acc =  AdditionalUserInfo.objects.all().filter(Q(auth="MNG")|Q(auth="OPR")|Q(auth="4")).order_by("-id")
    result["total"] = len(acc)
    acc_result = acc[start_index:start_index+size]
    opr_all_account_set=[]
    for ac in acc_result:
        temp = {}
        temp["opr_index"] = k
        k = k + 1
        temp["opr_id"] = ac.user.username
        temp["opr_mng_name"] = ac.mng_name
        temp["opr_mng_position"] = ac.mng_position
        temp["opr_mng_bonbu"] = ac.mng_bonbu
        temp["opr_mng_kikwan"] = ac.mng_kikwan
        temp["opr_mng_team"] = ac.mng_team
        try:
            temp["opr_mng_sangsa"] = ac.mng_boss.mng_name
        except:
            temp["opr_mng_sangsa"] = ""
        temp["opr_mng_tel"] = ac.mng_tel
        temp["opr_mng_phone"] = ac.mng_phone
        temp["opr_mng_email"] = ac.mng_email
        temp["opr_mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        opr_all_account_set.append(copy.deepcopy(temp))
    result["all_account_set"] = opr_all_account_set
    return JsonResponse(result, safe=False)


@csrf_exempt
def startup_list(request):
    filter_list = request.POST.get("filter_list").split(",")
    result = Startup.objects.all().exclude(company_name="").exclude(company_name=None)
    for filter in filter_list:
        if filter != None and filter != "":
            result = copy.deepcopy(result.filter(selected_company_filter_list__filter_name=filter))
            print(result)
            for r in result:
                print(r.company_name)
    print(result)
    result_set = []
    for s in result:
        temp_obj = {}
        temp_obj["company_name"] = s.company_name
        temp_obj["logo"] = s.logo
        temp_obj["company_short_desc"] = s.company_short_desc
        try:
            temp_obj["is_favored"] = is_in_favor_list("startup", s.id, request.GET.get("gca_id"))
        except:
            temp_obj["is_favored"] = False
        temp_obj["filter"] = []
        temp_obj["id"] = s.id
        for t in s.selected_company_filter_list.all():
            if t.filter_name != "" and t.filter_name != None and t.cat_0!="지원형태":
                temp_obj["filter"].append(t.filter_name)

        result_set.append(copy.deepcopy(temp_obj))

    return  JsonResponse(list(result_set), safe=False)


