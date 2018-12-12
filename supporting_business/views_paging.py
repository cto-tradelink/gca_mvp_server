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
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from datetime import datetime
from django.db import reset_queries
import time
from django.db import connection

def my_timer(original_function):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        reset_queries()
        result = original_function(*args, **kwargs)
        t2 = time.time() - t1
        time_sql=0.0
        for q in connection.queries:
            time_sql = float(q["time"]) + time_sql
        print( '{} 함수가 실행된 총 시간: {} 초'.format(original_function.__name__, t2))
        print('db 쿼리 시간 :  {} 초'.format(time_sql))
        print('쿼리 제외한 연산 시간 :  {} 초'.format(t2 - time_sql))

        return result

    return wrapper

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

def gca_check_session(request):

    session_key = request.GET.get("session_key")
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        user = User.objects.get(id=uid)
    except:
        return False
    if user.additionaluserinfo and user.is_authenticated():
        return user.additionaluserinfo.id
    else:
        return False



#----------------------- 매니저 페이징 라우터 ---------------------

#전체 지원사업 라우터
@my_timer
@csrf_exempt
def other_support_business_support_business(request):
    start_index = int(request.POST.get("start_index"))
    size = int(request.POST.get("size"))
    support_business = SupportBusiness.objects.exclude(support_business_status__in=[1,None]).select_related("support_business_author")
    total = (support_business).count()
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
        temp["mng_apply_num"] = (Appliance.objects.filter(support_business=s,is_submit=True)).count()
        temp["mng_award_num"] = (Award.objects.filter(support_business=s)).count()
        mng_status=""
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

# 수정전
# 쿼리수 : 31
# test 함수가 실행된 총 시간: 0.8711519241333008 초
# db 쿼리 시간 :  0.8280000000000004 초
# 쿼리 제외한 연산 시간 :  0.04315192413330038 초
# 수정후
# 쿼리수 :13
# test_2 함수가 실행된 총 시간: 0.15365195274353027 초
# db 쿼리 시간 :  0.15700000000000003 초
# 쿼리 제외한 연산 시간 :  -0.003348047256469755 초




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


import re
@csrf_exempt
def startup_list(request):
    check_result = gca_check_session(request)
    if check_result != False:
        user_auth_id = check_result
    filter_list = request.POST.get("filter_list").split(",")
    result = Startup.objects.all().exclude(company_name="").exclude(company_name=None)
    for filter in filter_list:
        if filter == "구성원 제한없음":
            pass
        elif "명 이하" in filter or "명 이상" in filter:
            # x 명이 있는 경우에는 구성원을 입력하지 않은 스타트업을 추가해주어야함
            num = int(re.findall('\d+', filter)[0])
            if (num != 0):
                result = copy.deepcopy(result.filter(company_total_employee__lte=num).exclude(company_name="").exclude(
                    company_name=None)) | Startup.objects.all().filter(company_total_employee=None)
        elif filter != None and filter != "":
            result = copy.deepcopy(result.filter(selected_company_filter_list__filter_name=filter))

    result_set = []
    for s in result:
        temp_obj = {}
        temp_obj["company_name"] = s.company_name
        temp_obj["logo"] = s.logo
        temp_obj["company_short_desc"] = s.company_short_desc
        try:
            temp_obj["is_favored"] = is_in_favor_list("startup", s.id, user_auth_id)
        except:
            temp_obj["is_favored"] = False
        temp_obj["filter"] = []
        temp_obj["id"] = s.id
        for t in s.selected_company_filter_list.all():
            if t.filter_name != "" and t.filter_name != None and t.cat_0!="지원형태" and t.cat_1!="기업형태":
                temp_obj["filter"].append(t.filter_name)
        result_set.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result_set), safe=False)

@csrf_exempt
def startup_list_by_or(request):
    filter_list = request.POST.get("filter_list").split(",")
    result = Startup.objects.exclude(company_name__in=["",None])
    startup_set =[]
    startup_list = []
    for filter in filter_list:
        if filter == "구성원 제한없음":
            pass
        elif "명 이하" in filter or "명 이상" in filter:
            # x 명이 있는 경우에는 구성원을 입력하지 않은 스타트업을 추가해주어야함
            num = int(re.findall('\d+', filter)[0])
            if (num != 0):
                result = copy.deepcopy(result.filter(company_total_employee__lte=num)) | \
                Startup.objects.filter(company_total_employee=None)
        elif filter != None and filter != "":
            for s in result.filter(selected_company_filter_list__filter_name__in=filter_list):
                if s not in startup_list:
                    startup_list.append(s)

    for s in startup_list:
        temp_obj = {}
        temp_obj["company_name"] = s.company_name
        temp_obj["logo"] = s.logo
        temp_obj["company_short_desc"] = s.company_short_desc
        try:
            temp_obj["is_favored"] = is_in_favor_list("startup", s.id, request.POST.get("id"))
        except:
            temp_obj["is_favored"] = False
        temp_obj["filter"] = []
        temp_obj["id"] = s.id
        temp_obj["sim"]=0
        for t in s.selected_company_filter_list.exclude(cat_0="지원형태",cat_1 = "기업형태" ):
            temp_obj["filter"].append(t.filter_name)
        temp_obj["sim"] = s.selected_company_filter_list.filter(filter_name__in=filter_list).count()
        startup_set.append(copy.deepcopy(temp_obj))


    return JsonResponse(startup_set, safe=False)
# 수정전
# 쿼리수 131
# startup_list_by_or 함수가 실행된 총 시간: 2.089946746826172 초
# db 쿼리 시간 :  1.9490000000000007 초
# 쿼리 제외한 연산 시간 :  0.14094674682617114 초
# 수정후
# 쿼리수 9
# startup_list_by_or 함수가 실행된 총 시간: 0.13151216506958008 초
# db 쿼리 시간 :  0.10200000000000001 초
# 쿼리 제외한 연산 시간 :  0.02951216506958007 초

@csrf_exempt
def get_vue_mng_dashboard(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    result = {}
    support_business_author_id = user_auth_id
    end=""
    end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(
        Q(support_business_status="4") | Q(support_business_status="3")).filter(
        support_business_author_id=support_business_author_id)
    result = []
    end = end_support_business.count()

    if(request.POST.get("kind")=="end"):
    # 모집 마감된 공고문
        end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(
            Q(support_business_status="4") | Q(support_business_status="3")).filter(
            support_business_author_id=support_business_author_id)
        result = []
        end = end_support_business.count()
        for support_business in end_support_business:
            result_end = {}
            result_end["id"] = support_business.id
            result_end["author_id"] = support_business.support_business_author.id
            result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
            result_end['support_business_name'] = support_business.support_business_name
            result_end['support_business_poster'] = support_business.support_business_poster

            result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            try:
                if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                    number = str(round((Appliance.objects.filter(support_business_id=support_business.id).filter(
                        is_submit=True)).count() / int(support_business.support_business_recruit_size), 1))
                    if (number == "0.0"):
                        number = "0"
                    result_end["comp"] = number + " : 1"
                else:
                    result_end["comp"] = ""
            except:
                result_end["comp"] = ""
            result.append(copy.deepcopy(result_end))
    blind=""
    blind_support_business = SupportBusiness.objects.filter(support_business_status="6").filter(
        support_business_author_id=support_business_author_id)
    blind = blind_support_business.count()
    if request.POST.get("kind")=="blind":
        blind_support_business = SupportBusiness.objects.filter(support_business_status="6").filter(
            support_business_author_id=support_business_author_id)
        blind= blind_support_business.count()
        blind_set = []
        result=[]
        for support_business in blind_support_business:
            result_end = {}
            result_end["id"] = support_business.id
            result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
            result_end['support_business_name'] = support_business.support_business_name
            result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end['support_business_poster'] = support_business.support_business_poster
            result_end["apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            try:
                if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                    number = str(round((
                                           Appliance.objects.filter(support_business_id=support_business.id).filter(
                                               is_submit=True)).count() / int(
                        support_business.support_business_recruit_size), 1))
                    if number == "0.0":
                        number = "0"
                    result_end["comp"] = number + " : 1"
                    pass
                else:
                    result_end["comp"] = ""
            except:
                result_end["comp"] = ""
            result.append(copy.deepcopy(result_end))
    writing=""
    writing_support_business = SupportBusiness.objects.filter(support_business_status="1").filter(
        support_business_author_id=support_business_author_id)
    writing = writing_support_business.count()
    if request.POST.get("kind")=="writing":

        writing_support_business = SupportBusiness.objects.filter(support_business_status="1").filter(
            support_business_author_id=support_business_author_id)
        writing = writing_support_business.count()
        writing_set = []
        result=[]
        for support_business in writing_support_business:
            result_end = {}
            result_end["id"] = support_business.id
            result_end["support_business_award_date_ymd"] = \
            str(support_business.support_business_update_at_ymdt).split(" ")[0]
            result_end['support_business_name'] = support_business.support_business_name
            result_end['support_business_poster'] = support_business.support_business_poster
            result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            result_end["comp"] = ""
            try:
                if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                    number = str(round((
                                           Appliance.objects.filter(support_business_id=support_business.id).filter(
                                               is_submit=True)).count() / int(
                        support_business.support_business_recruit_size), 1))
                    if number == "0.0":
                        number = "0"
                    result_end["comp"] = number + " : 1"
                    pass
                else:
                    result_end["comp"] = ""
            except:
                result_end["comp"] = ""
            result.append(copy.deepcopy(result_end))
    ing=""
    ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(
        support_business_author_id=support_business_author_id).filter(
        support_business_apply_end_ymdt__gt=timezone.now())
    ing_set = []
    ing = ing_support_business.count()
    if request.POST.get("kind")=="ing":
        ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(
            support_business_author_id=support_business_author_id).filter(
            support_business_apply_end_ymdt__gt=timezone.now())
        ing_set = []
        ing=ing_support_business.count()
        for support_business in ing_support_business:

            result_end = {}
            result_end["id"] = support_business.id
            result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
            result_end["author_id"] = support_business.support_business_author.id
            result_end['support_business_name'] = support_business.support_business_name
            result_end['support_business_poster'] = support_business.support_business_poster
            result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            result_end["comp"] = ""
            try:
                if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                    number = str(round((
                                           Appliance.objects.filter(support_business_id=support_business.id).filter(
                                               is_submit=True)).count() / int(
                        support_business.support_business_recruit_size), 1))
                    if number == "0.0":
                        number = "0"
                    result_end["comp"] = number + " : 1"

                else:
                    result_end["comp"] = ""
            except:
                result_end["comp"] = ""
            result.append(copy.deepcopy(result_end))
    return JsonResponse({"result_set":result,"set_num":{"ing": ing, "blind":blind ,"writing":writing, "end":end }}, safe=False)

@csrf_exempt
def vue_get_opr_dashboard(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    mng_list = []

    for a in AdditionalUserInfo.objects.get(id=user_auth_id).additionaluserinfo_set.all():
        mng_list.append(a.id)
    result = []
    # 모집 마감된 공고

    end = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(
            Q(support_business_status="4") | Q(support_business_status="3")).filter(
            support_business_author_id__in=mng_list).count()

    if(request.POST.get("kind") == "end"):
        end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(
            Q(support_business_status="4") | Q(support_business_status="3")).filter(
            support_business_author_id__in=mng_list)
        end_set = []
        for support_business in end_support_business:
            result_end = {}
            result_end["opr_support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
            result_end['opr_support_business_name'] = support_business.support_business_name
            result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["opr_id"] = support_business.id
            result_end["opr_support_business_author_id"] = support_business.support_business_author.id
            result_end["opr_support_business_poster"] = support_business.support_business_poster
            result_end["opr_apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                try:
                    number = str(round((
                                           Appliance.objects.filter(support_business_id=support_business.id).filter(
                                               is_submit=True)).count() / int(
                        support_business.support_business_recruit_size), 1))
                    if number == "0.0":
                        number = "0"
                    result_end["opr_comp"] = number + " : 1"
                except:
                    result_end["opr_comp"] = str((
                                                     Appliance.objects.filter(
                                                         support_business_id=support_business.id).filter(
                                                         is_submit=True)).count()) + " : 1"
            else:
                result_end["opr_comp"] = str((Appliance.objects.filter(support_business_id=support_business.id).filter(
                    is_submit=True)).count()) + " : 1"
            result.append(copy.deepcopy(result_end))


    wating =  waiting_support_business = SupportBusiness.objects.filter(support_business_status="2").filter(
            support_business_author_id__in=mng_list).count()
    if(request.POST.get("kind") == "waiting") :
        # 승인 요청중인 공고
        waiting_support_business = SupportBusiness.objects.filter(support_business_status="2").filter(
            support_business_author_id__in=mng_list)
        waiting_set = []
        for support_business in waiting_support_business:
            result_end = {}
            result_end["opr_id"] = support_business.id
            result_end["opr_support_business_award_date_ymd"] = \
            str(support_business.support_business_update_at_ymdt).split(" ")[0]
            result_end['opr_support_business_name'] = support_business.support_business_name
            result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
            result_end["opr_support_business_poster"] = support_business.support_business_poster
            result_end["opr_apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
            result_end["opr_comp"] = "0 : 1"
            result.append(copy.deepcopy(result_end))
    ing =  SupportBusiness.objects.filter(support_business_status="3").filter(
            support_business_apply_end_ymdt__gte=timezone.now()).filter(support_business_author_id__in=mng_list).count()
    if(request.POST.get("kind") == "ing"):
        # 공고중인 공고
        ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(
            support_business_apply_end_ymdt__gte=timezone.now()).filter(support_business_author_id__in=mng_list)
        ing_set = []
        for support_business in ing_support_business:
            result_end = {}
            result_end["opr_id"] = support_business.id
            result_end["opr_support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
            result_end['opr_support_business_name'] = support_business.support_business_name
            result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
            result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
            result_end["opr_support_business_poster"] = support_business.support_business_poster
            result_end["opr_apply_num"] = (
            Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
            result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
            result_end["opr_support_business_author_id"] = support_business.support_business_author.id
            result_end["opr_open_date"] = (support_business.support_business_created_at_ymdt)
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                try:
                    number = str(round((
                                           Appliance.objects.filter(support_business_id=support_business.id).filter(
                                               is_submit=True)).count() / int(
                        support_business.support_business_recruit_size), 1))
                    if number == "0.0":
                        number = "0"
                    result_end["opr_comp"] = number + " : 1"
                except:
                    result_end["opr_comp"] = str((
                                                     Appliance.objects.filter(
                                                         support_business_id=support_business.id).filter(
                                                         is_submit=True)).count()) + " : 1"
            else:
                result_end["opr_comp"] = ""
            result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
            result.append(copy.deepcopy(result_end))
    return JsonResponse({ "result_set" : result, "set_num":{"end":end, "ing":ing, "waiting" : wating,} }, safe=False)




@csrf_exempt
def mng_vue_get_startup_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    startup= Startup.objects.all()
    result = []
    if request.POST.get("kind") == "startup":
        k=1
        startup_set=[]
        for s in startup :
            temp={}
            temp["mng_index"]=k
            k=k+1
            temp["mng_company_name"] = s.company_name
            temp["mng_id"] = s.user.username
            temp["mng_startup_id"] = s.id
            temp["mng_mark_name"] = s.mark_name
            temp["mng_mark_tel"] = s.mark_tel
            temp["mng_mark_email"] = s.mark_email
            tag_list=[]
            for t in s.selected_company_filter_list.all():
                tag_list.append(t.filter_name)
            temp["mng_tag"] = tag_list
            try:
                if "경기" in s.address_0:
                    local = "경기"
                elif "서울" in s.address_0:
                    local = "서울"
                elif "인천" in s.address_0:
                    local = "인천"
                else :
                    local = "기타"
            except:
                local="기타"
            temp["mng_local"] = local
            temp["mng_employ_num"] = int(s.company_total_employee) if s.company_total_employee else 0
            temp["mng_apply_num"] = (Appliance.objects.filter(startup=s)).count()
            temp["mng_award_num"] = (Award.objects.filter(startup=s)).count()
            temp["mng_join"] = s.user.date_joined
            temp["mng_tag"]=[]
            for t in s.selected_company_filter_list.all():
                temp["mng_tag"].append(t.filter_name)
            startup_set.append(copy.deepcopy(temp))
        result = startup_set
    if request.POST.get("kind") == "user":
        user_ad = AdditionalUserInfo.objects.exclude(auth=4).exclude(auth=5)
        user_set = []
        p=1
        for u in user_ad:
            try:
                user = {}
                user["mng_id"] = u.user.username
                user["mng_startup_id"] = Startup.objects.get(user=u.user).id
                user["mng_mark_name"] = Startup.objects.get(user=u.user).mark_name
                user["mng_mark_tel"] = Startup.objects.get(user=u.user).mark_tel
                user["mng_facebook"] = Startup.objects.get(user=u.user).company_facebook
                user["mng_joined"] = u.user.date_joined
                user["mng_index"]=p
                p=p+1
                user_set.append(copy.deepcopy(user))
            except Exception as e:
                pass
        result = user_set
    if request.POST.get("kind")=="aw":
        ## 사업 참여 기업
        aw_startup_set = Appliance.objects.all().values("startup").distinct()
        k=1
        ap_set = []
        for s in aw_startup_set:
            aw_st={}
            startup = Startup.objects.get(id=s["startup"])
            aw_st["mng_index"] = k
            k=k+1
            aw_st["mng_company_name"] = startup.company_name
            aw_st["mng_mark_name"] = startup.mark_name
            aw_st["mng_startup_id"] = startup.id
            aw_st["mng_mark_tel"] = startup.mark_tel
            tag_list = []
            for t in startup.selected_company_filter_list.all():
                tag_list.append(t.filter_name)
            aw_st["mng_tag"] = tag_list
            try:
                if "경기" in startup.address_0:
                    local = "경기"
                elif "서울" in startup.address_0:
                    local = "서울"
                elif "인천" in startup.address_0:
                    local = "인천"
                else:
                    local = "기타"
            except:
                local="기타"
            aw_st["mng_local"] = local
            aw_st["mng_support_business_name"] = Appliance.objects.filter(startup=startup).last().support_business.support_business_name
            if (Award.objects.filter(support_business=Appliance.objects.filter(startup=startup).last().support_business).filter(startup=startup)).count() == 0 :
                aw_st["mng_awarded"] = "N"
            else:
                aw_st["mng_awarded"] = "Y"
            aw_st["mng_end_date"] = str(Appliance.objects.filter(startup=startup).last().support_business.support_business_apply_end_ymdt).split(" ")[0]
            ap_set.append(copy.deepcopy(aw_st))
        result = ap_set
    print(result)
    return JsonResponse({"result":result})
















