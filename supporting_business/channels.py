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



@csrf_exempt
def toggle_int_clip(request):
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    if clip in ad.interest_clip.all():
        ad.interest_clip.remove(clip)
    else:
        ad.interest_clip.add(clip)
    return JsonResponse({"result":"ok"})




@csrf_exempt
def toggle_int_path(request):
    clip = Path.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    if clip in ad.interest_path.all():
        ad.interest_path.remove(clip)
    else:
        ad.interest_path.add(clip)
    return JsonResponse({"result":"ok"})




@csrf_exempt
def toggle_int_course(request):
    clip = Course.objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    if clip in ad.interest_course.all():
        ad.interest_course.remove(clip)
    else:
        ad.interest_course.add(clip)
    return JsonResponse({"result":"ok"})



@csrf_exempt
def vue_hit_clip_log(request):
    print(request)
    print(request.body)
    print(request.POST)
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    HitClipLog.objects.get_or_create(clip=clip, user=ad)

@csrf_exempt
def vue_watch_clip_history(request):
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    WatchClipHistory.objects.create(clip=clip, user=ad)


@csrf_exempt
def vue_hit_course_log(request):
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    HitCourseLog.objects.get_or_create(clip=clip, user=ad, course= course)
    WatchCourseHistory.objects.get_or_create(clip=clip, user=ad, course=course)
    return  JsonResponse({"result":"ok"})

@csrf_exempt
def vue_watch_course_history(request):
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    WatchCourseHistory.objects.create(clip=clip, user=ad, course=course)
    WatchClipHistory.objects.create(clip=clip, user=ad, )
    time = clip.clip_play
    num = len(WatchCourseHistory.objects.all().filter(clip=clip))*6
    if 100 * num / time > 98 :
        return JsonResponse({"result": "com"})
    return JsonResponse({"result": "ok"})

@csrf_exempt
def vue_hit_path_log(request):
    print("--")
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    path = Path.objects.get(id=request.POST.get("path"))
    HitPathLog.objects.get_or_create(clip=clip, user=ad, course= course,path=path)


@csrf_exempt
def vue_watch_path_history(request):
    print("hello")
    clip = clip.clip_objects.get(id=request.POST.get("val"))
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    course = Course.objects.get(id=request.POST.get("course"))
    path = Path.objects.get(id=request.POST.get("path"))
    watch = WatchPathHistory.objects.create(clip=clip, user=ad, course=course, Path=path)
    print(watch)
    WatchCourseHistory.objects.create(clip=clip, user=ad, course=course,)
    WatchClipHistory.objects.create(clip=clip, user=ad,)
    print("hello")
    return JsonResponse({"result":"ok"})

@csrf_exempt
def vue_get_ing_lecture(request):
    result={}
    result["path_list"] = []
    for p in HitPathLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["clip_title"]=p.path.title
        t["id"]=p.path.id
        t["created"] = p.path.created_at
        t["user"] = p.path.user.repre_name
        t["play"] = p.path.total_play
        t["clip_thumb"] = p.path.clip_thumb
        t["entry_point"] = "/path/view/"+str(p.path.id) + "/" + str(p.course.id) + "/" + str(p.clip.id)

        result["path_list"].append(copy.deepcopy(t))
    result["course_list"] =[] # = HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in HitCourseLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["clip_title"]=p.course.title
        t["id"]=p.course.id
        t["created"] = p.course.created_at
        t["user"] = p.course.user.repre_name
        t["play"] = p.course.total_play
        t["clip_thumb"] = p.course.clip_thumb
        t["entry_point"] = "/course/view/"+str(p.course.id) + "/"+str(p.clip.id)
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in HitClipLog.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["clip_title"]=p.clip.clip_title
        t["id"]=p.clip.id
        t["created"] = p.clip.clip_created_at
        t["user"] = p.clip.user.repre_name
        t["play"] = p.clip.clip_play
        t["clip_thumb"] = p.clip.clip_clip_thumb

        result["clip_list"].append(copy.deepcopy(t))


    return JsonResponse({'results':result })



@csrf_exempt
def vue_get_manager_lecture(request):
    result={}
    result["path_list"] = []
    for p in Path.objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["clip_title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.repre_name
        t["play"] = p.total_play
        t["clip_thumb"] = p.clip_thumb
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
        t["clip_title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.repre_name
        t["play"] = p.total_play
        t["clip_thumb"] = p.clip_thumb
        try:
            t["entry_point"] = "/course/view/"+str(p.id) + "/"+str(p.clips.first().id)
        except:
            t["entry_point"] = ""
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in clip.clip_objects.all().filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id"):
        t={}
        t["clip_title"]=p.title
        t["id"]=p.id
        t["created"] = p.created_at
        t["user"] = p.user.repre_name
        t["play"] = p.play
        t["clip_thumb"] = p.clip_thumb

        result["clip_list"].append(copy.deepcopy(t))



    return JsonResponse({'results':result })



@csrf_exempt
def vue_toggle_fav_clip(request):
    ad = AdditionalUserInfo.objects.get(id=request.GET.get("id"))
    cl = clip.clip_objects.get(id=request.GET.get("clip_id"))
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
                local_list.append(t.jiwon_filter_name)
    company_kind_list=[]
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                company_kind_list.append(t.jiwon_filter_name)
    em_list=[]
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                company_kind_list.append(t.jiwon_filter_name)
    field_list = []
    for f in path.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.jiwon_filter_name)
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
        temp["repre_name"]= u.repre_name
        result_user.append(copy.deepcopy(temp))


    return JsonResponse({"line":result, "path_company_kind_tag":organize(company_kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list), "user":result_user })

# --------[강의 샘플 듣기]-------

@csrf_exempt
def vue_get_channel_statics_course(request):
    course = Course.objects.get(id=request.GET.get("course_id"))
    fav_date_list = FavCourseLog.objects.all().filter(Course=course).values("date").distinct()
    result={}
    result["fav_static"]=[]
    for fd in fav_date_list:
        temp={}
        temp["date"] = fd["date"]
        print(len(FavCourseLog.objects.filter(Course=course).filter(date = fd["date"])))
        temp["number"] = len(FavCourseLog.objects.filter(Course=course).filter(date = fd["date"]))
        result["fav_static"].append(copy.deepcopy(temp))

    watch_time = WatchCourseHistory.objects.all().filter(course=course).values("date").distinct()
    result["watch_static"]=[]
    for i in watch_time:
        temp={}
        temp["date"] = i["date"]
        temp["number"]= len(WatchCourseHistory.objects.all().filter(course=course).filter(date=i["date"]))*6
        result["watch_static"].append(copy.deepcopy(temp))

    local_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_1=="소재지":
                local_list.append(t.jiwon_filter_name)
    company_kind_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                company_kind_list.append(t.jiwon_filter_name)
    em_list=[]
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                company_kind_list.append(t.jiwon_filter_name)
    field_list = []
    for f in course.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.jiwon_filter_name)

    return JsonResponse({"line":result, "path_company_kind_tag":organize(company_kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list),  })
# --------[양파 샘플 듣기]-------


@csrf_exempt
def vue_get_channel_statics_clip(request):
    clip = clip.clip_objects.get(id=request.GET.get("clip_id"))
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

        temp["number"]= len(WatchClipHistory.objects.all().filter(clip=clip).filter(date=i["date"]))*6
        result["watch_static"].append(copy.deepcopy(temp))

    local_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_1=="소재지":
                local_list.append(t.jiwon_filter_name)
    company_kind_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="기본장르" :
                company_kind_list.append(t.jiwon_filter_name)
    em_list=[]
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0=="구성원"  :
                company_kind_list.append(t.jiwon_filter_name)
    field_list = []
    for f in clip.additionaluserinfo_set.all():
        for t in f.user.startup.filter.all():
            if t.cat_0 == "영역":
                field_list.append(t.jiwon_filter_name)

    return JsonResponse({"line":result, "path_company_kind_tag":organize(company_kind_list), "path_local_tag":organize(local_list),
                         "path_em_tag": organize(em_list), "path_field_tag":organize(field_list),  })



#------------------------ 중복일 가능성 있음
# --------[강의 샘플 듣기]-------

@csrf_exempt
def vue_sample_list_clip(request):
    st = clip.clip_objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["support_business_name"] = s.support_business_name
        temp_obj["clip_thumb"] = s.clip_thumb
        temp_obj["mov_address"]=s.mov_address
        temp_obj["clip_youtube"]=s.clip_youtube
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info

        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)



# --------[코스  샘플 듣기]-------


@csrf_exempt
def vue_sample_course_path(request):
    st = Course.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["clip_title"] = s.title
        temp_obj["clip_thumb"] = s.clip_thumb
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info

        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)

# --------[패스스 샘플 듣기]------

@csrf_exempt
def vue_sample_path_path(request):
    st = Course.objects.all().order_by("?")[:3]
    result = []
    for s in st:
        temp_obj={}
        temp_obj["clip_title"] = s.title
        temp_obj["clip_thumb"] = s.clip_thumb
        temp_obj["created"] = s.created_at
        temp_obj["info"] = s.info
        result.append(copy.deepcopy(temp_obj))
    return  JsonResponse(list(result), safe=False)

@csrf_exempt
def vue_get_statics_by_channel(request):
    path = Path.objects.all()
    result = {}

    result["simple_path"]=[]
    for p in Path.objects.all():
        result["simple_path"].append({
            "name":p.path_title, "id":p.id,
        })
    result["simple_course"] = []
    for p in Course.objects.all():
        result["simple_course"].append({
            "name": p.title, "id": p.id,
        })
    result["simple_clip"] = []
    for p in clip.clip_objects.all():
        result["simple_clip"].append({
            "name": p.title, "id": p.id,
        })




    result["path"]=[]
    for p in path:
        temp_path={}
        temp_path["clip_title"] = p.title
        temp_path["id"] = p.id
        temp_path["course"] = []
        for c in p.course.all():
            temp_course = {}
            temp_course["id"] = c.id

            temp_course["clip_title"] = c.title
            temp_course["clip"] = []
            for clip in c.clips.all():
                print("why")
                temp_clip = {}
                temp_clip["clip_title"] = clip.clip_title
                temp_clip["id"] = clip.id

                temp_course["clip"].append(copy.deepcopy(temp_clip))
            temp_path["course"].append(copy.deepcopy(temp_course))
        result["path"].append( copy.deepcopy(temp_path))
    return  JsonResponse(result)



#-----------------------재 중복일 수 있음
# --------[모든 샘플 듣기]-------

def vue_get_clip_all(request):
    result = []
    for c in clip.clip_objects.all():
        temp={}
        temp["id"] = c.id
        temp["user"]=c.user.repre_name
        temp["img"]=c.clip_thumb
        temp["clip_title"]=c.title
        temp["dur"]=c.play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.jiwon_filter_name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)

# --------[[코스 샘플 듣기]-------

def vue_get_course_all(request):
    result = []
    for c in Course.objects.all():
        temp={}
        temp["id"] = c.id
        try:
            temp["entry_point"] = "/course/view/"+ str(c.id)+"/" + str(c.clips.all().first().id)
        except:
            temp["entry_point"]=""
        temp["user"]=c.user.repre_name
        temp["img"]=c.clip_thumb
        temp["clip_title"]=c.title
        temp["dur"]=c.total_play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.jiwon_filter_name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)


# -------[[모든 패스리스트 가지고 오기]]----------
def vue_get_path_all(request):
    result = []
    for c in Path.objects.all():
        temp={}
        temp["id"] = c.id
        try:
            temp["entry_point"] = "/path/view/"+ str(c.id)+"/"+ str(c.course.all().first().id) + "/"+ str(c.course.all().first().clips.all().first().id)
        except:
            temp["entry_point"]=""
        temp["user"]=c.user.repre_name
        temp["img"]=c.clip_thumb
        temp["clip_title"]=c.title
        temp["dur"]=c.total_play
        temp["date"]=c.created_at
        temp["sub"] = c.info
        temp["tag"] =[]
        for t in c.filter.all():
            temp["tag"].append(t.jiwon_filter_name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)