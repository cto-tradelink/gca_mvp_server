# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import string
import random
from .forms import *
from django.utils import timezone
from django.contrib.auth.views import login as auth_login
from allauth.socialaccount.models import SocialApp
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

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
 #세션 인증

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



def handle_uploaded_file_poster(file, filename):
    print('media/uploads/poster/')
    if not os.path.exists('media/uploads/poster/'):
        os.makedirs('media/uploads/poster')
    with open('media/uploads/poster/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            return 'media/uploads/poster/'+filename


#---------------------------<< 로그인 >>-------------------------
# --------[1.모든 페이지 공통, 로그인 기능]-----------------------------------------------------------------------------


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업, 매니저, 기관관리자, 비로그인 유저
# 기능 : 인증 메일 보내는 기능
# 함수 완성 여부 : 함수 완성
# 사용된 변수/함수명 등 : cert_email/random_code/target/send_mail/
# 변수 체크 여부 : py(O), VS(0), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def cert_email(request):
    if request.POST.get("type") == "confirm":
        target = request.POST.get("val")
        #target = "kshradio@naver.com"
        random_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        try:
            send_mail(
                '[G-connect] 인증메일입니다.',
                '인증코드는 [' + str(random_code) + "] 입니다.", # random_code
                'neogelon@gmail.com',
                ["kshradio@naver.com"],
                fail_silently=False,
            )
            EmailConfirmation(
                email=target,
                confirmation_code=random_code #random_code
            ).save()
            return HttpResponse("ok")
        except Exception as e:
            print(e)
            return HttpResponse("none")


    elif request.POST.get("type") == "confirm2":
        if EmailConfirmation.objects.filter(email=request.POST.get("target")).order_by("-id")[0].confirmation_code == request.POST.get("confirmation_code"):
            EmailConfirmation.objects.filter(email=request.POST.get("target")).update(confirm=True)

            return HttpResponse("ok")
        else:
            return HttpResponse("no")



#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업, 매니저, 기관관리자, 비로그인 유저
# 기능 : 인증 메일 보내는 기능
# 함수 완성 여부 : 함수 완성
# 사용된 변수/함수명 등 : cert_email/random_code/target/send_mail/
# 변수 체크 여부 : py(O), VS(0), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@my_timer
def vue_login_user(request):
    print(request.body)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            try:
                if str(user.additionaluserinfo.auth) == "MNG" or (user.additionaluserinfo.auth) == "OPR":

                    if  (user.additionaluserinfo.auth) == "OPR":
                        return JsonResponse({"result":"success", "code":"OPR","id":user.additionaluserinfo.id, "session_key": request.session.session_key  })
                    else:
                        return JsonResponse({"result":"success","code": "MNG","id":user.additionaluserinfo.id, "session_key":  request.session.session_key })
                else:
                    return JsonResponse({"result":"success","code":"USR","id":user.additionaluserinfo.id, "session_key":  request.session.session_key  })
            except:
                return JsonResponse({"result":"false"})
        else:
            if (User.objects.filter(username=username)).count()  > 0:
                return JsonResponse({"result":"pw_check"})
            else:
                return JsonResponse({"result":'0'})

# ------------------------------------SNS로그인 기능


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업
# 기능 : SNS 버튼으로 로그인 인증
# 함수 완성 여부 : ㅇ
# provider,token,url,re,header,email,provider,access_token
# 변수 체크 여부 : py(0), VS(-), mysql(0)
#-----------------------------------------------------------------------------------------------------------------------
from django.contrib.auth.models import User
@csrf_exempt
@my_timer
def vue_get_sns_auth(request):
    provider = request.POST.get("provider")
    token = request.POST.get("token")
    email = ""
    name=""
    print(provider)
    print(token)
    if provider == "naver":
        # 접근 토큰 발급 받기
        url = "https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id=MonomZR2k6j8bS3LEFvy&client_secret=J1ll08KKVd&code=" + token + "&state=aaa"
        re = requests.get(url)
        print(re.text)
        # return JsonResponse({})
        header = "Bearer " + re.json()["access_token"]  # Bearer 다음에 공백 추가
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": header}
        re = requests.get(url, headers=headers)
        print(re.json()["response"]["nickname"])
        print(re.json()["response"]["name"])
        try:
            print(re.json()["response"]["email"])
        except:
            print("이메일 없음")
        print(re.json()["response"]["profile_image"])

        name = (re.json()["response"]["name"])
        email = re.json()["response"]["email"]
    if provider == "kakao":
        url = "https://kapi.kakao.com/v2/user/me"
        re = requests.get(url)
        header = "Bearer " + token  # Bearer 다음에 공백 추가
        headers = {"Authorization": header}
        re = requests.post(url, headers=headers, )
        print(re.text)
        print(re.json()["properties"]["nickname"])
        print(re.json()["kakao_account"]["email"])
        print(re.json()["properties"]["profile_image"])
        name = re.json()["properties"]["nickname"]
        email = re.json()["kakao_account"]["email"]

    if provider == "facebook":
        url = "https://graph.facebook.com/v3.0/oauth/access_token?client_id=162083444444485&redirect_uri=http://gconnect.kr/login&client_secret=1916c66420a16d82b106718eaa8b0ee1&code=" + token

        re = requests.get(url)
        print(re.text)

        access_token = re.json()["access_token"]

        url = "https://graph.facebook.com/debug_token?input_token=" + re.json()[
            "access_token"] + "&access_token=162083444444485|1916c66420a16d82b106718eaa8b0ee1"
        re = requests.get(url)
        print(re.json()["data"]["user_id"])
        url = "https://graph.facebook.com/" + re.json()["data"][
            "user_id"] + "?fields=id,name,first_name,last_name,age_range,link,gender,locale,picture,timezone,updated_time,verified,email&access_token=" + access_token
        re = requests.get(url)
        print(re.json()["name"])
        name = re.json()["name"]
        try:
            email = re.json()["email"]
            print(email)
        except:
            pass

    #user = User.objects.get(email=email)
    user, created = User.objects.get_or_create(username=email)

    if created == True:
        add = AdditionalUserInfo()
        add.user = user
        add.auth="USR"
        add.save()
        st = Startup()
        st.repre_name = name
        st.repre_email = email
        st.user= user
        st.save()
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(None)

    session.clear()
    session.create()

    session[SESSION_KEY] = user.id
    print("========")
    print(user.id)
    session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
    #session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()
    return JsonResponse({"name": name, "code":"USR" , "user_id": user.additionaluserinfo.id, "session_key":session.session_key}, safe=False)






#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업유저
# 기능 : (모든페이지) 좋아요 리스트 가져오는 함수
# u, result
# 함수 완성 여부 : O
# 변수 체크 여부 : py(O), VS(O), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------
# -------------- (모든페이지) 좋아요 리스트 가져오는 함수
@csrf_exempt
@my_timer
def vue_get_all_favorite(request):


    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result


    u = AdditionalUserInfo.objects.get(id=user_id)
    result = {}
    result["startup"] = []
    for i in u.favorite_startup_set.all():
        result["startup"].append(i.id)

    result["support_business"] = []
    for i in u.favorite_support_business_set.all():
        result["support_business"].append(i.id)

    result["clip"] = []
    for i in u.favorite_clip_set.all():
        result["clip"].append(i.id)

    result["course"] = []
    for i in u.favorite_course_set.all():
        result["course"].append(i.id)

    result["path"] = []
    for i in u.favorite_path_set.all():
        result["path"].append(i.id)

    return JsonResponse(result, safe=False)




#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업, 비 로그인 유저
# 기능 : 지원사업 방문 기록 남기는 기능
# target, h, id
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(O), VS(O), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------
# --------------- (모든페이지) (통계) 공고문 상세에 들어가면 방문수 카운팅  (고치기 : 변수/ 오류 수정)
# postman작동함
@csrf_exempt
@my_timer
def hit_support_business(request):
    target = request.POST.get("target")
    try:
        id = request.POST.get("id")
        h = HitLog()
        h.user = AdditionalUserInfo.objects.get(id=id)
        h.support_business_id = target
        h.save()
    except:
        h = HitLog()
        h.support_business_id = target
        h.save()
    return JsonResponse({"result": "success"})

# ------- (공통)


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 로그인한 스타트업 유저
# 기능 : 스타트업유저가 지원사업 홈, 스타트업 리스트에서 검색시 필터 저장 기능
# id
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def save_filter(request):

    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result

    print(request.POST.get("filter").split(","))
    id=user_auth_id

    startup = Startup.objects.get(user=AdditionalUserInfo.objects.get(id=id).user)
    #startup.selected_company_filter_list.clear()
    # 스타트업일 경우
    if request.POST.get("kind") == "startup":
        for filter in startup.selected_company_filter_list.all():
            if filter.cat_0 != "지원형태":
                startup.selected_company_filter_list.remove(filter)
           
            
    # 지원사업 필터 일경우
    elif request.POST.get("kind") == "support_business":
        startup.selected_company_filter_list.clear()
        for filter in startup.selected_company_filter_list.all():
             startup.selected_company_filter_list.remove(filter)

    employee_set =False
    for filter in request.POST.get("filter").split(","):
        if filter != "":
            if  '명 이하' in filter or "명 이상" in filter:
                num = int(re.findall('\d+', filter)[0])
                startup.company_total_employee = num
                startup.save()
                employee_set = employee_set | True
            else:
                startup.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=filter))



    if employee_set == False:
        startup.company_total_employee = ""
        startup.save()
    filter_list = []
    for filter in startup.selected_company_filter_list.all():
        filter_list.append(filter.filter_name)
    return JsonResponse({"result":"success","data":filter_list})
#----------------------------------------------------------------------------------------------------------------------
# <<가. 회원별 권한 설정>>
# <목표> 회원별 권한 설정 및 보이는 페이지 정리
#  1. 회원별 권한 설정
#       - 기관관리자 : 매니저생성/하위 귀속 매니저의 통합통계 보기, 매니저 공고문 승인 및 블라인드, 열람(기관관리자 뷰)
#       - 매니저 : 지원서 작성, 기관관리자에 승인요청, 지원자 선발, 통계 열람(본인이 관리하는 사업이 드롭다운드로 보인다.)
#       - 스타트업 : 회사에 기업정보 저장_회사페이지(서비스/프로덕트, 회사소개, 비공개 정보), 지원서 화면에서 동기화되어서 보여야함.
#                   관심담기, 지원서 제출(제출한 시점을 기준으로 json 등의 데이터 분리해서 관리할 것
#  2. 보이는 페이지 url
#        - index.js : 회원 권한별로 열람할 수 있는 페이지가 지정되어있다

#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# 가. 회원별 권한 설정
#
#     <목표>
#     index.js 에서 네이게이션 가드를 통해서 열람 페이지 제한
#     그외 : 각 페이지 기능에서 유저의 code 를 검사
#
# 기관회원 관리 페이지. 기관 관리자 : 매니저 계정 생성
#----------------------------------------------------------------------------------------------------------------------

#-----------------<<<<<유저별 권한>>>>>---------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
# [기관관리자]
#       1. 매니저 계정 생성
#       2. 공고문에 대한 블라인드 처리 권한, 승인 요청한 공고문에 대한 블라인드/승인
#       3. 전체 지원사업/ 회원 열람
#       4. 통계 데이터 : 전체 지원사업, 매니저별 지원사업, 회원 통계, 사이트 통계
#-----------------------------------------------------------------------------------------------------------------------

# ------------(기관관리자) 매니저 계정 생성-----------------------------------------------------------------------------
# --------[기관 회원관리, 매니저 계정 추가 ]----------------------------------------------------------------------------


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관 관리자
# 기능 : 기관 회원관리, 매니저 계정 추가
# add_user, mng_boss_id, mng_boss, new_user,
# 함수 완성 여부 : 완성
# 변수 체크 여부 : py(O), VS(O), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@my_timer
def vue_add_mng_acc(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result

    if request.method == "POST":
        if (User.objects.filter(username=request.POST.get("id"))).count() == 0:
            print(request.POST)
            add_user = User.objects.create_user(username=request.POST.get("id"), password=request.POST.get("pw"))
            if add_user is not None:

                print(request.POST)
                mng_boss_id=request.POST.get("mng_boss")
                mng_boss = AdditionalUserInfo.objects.get(id=mng_boss_id)
                new_user = AdditionalUserInfo()
                print(User.objects.get(username=request.POST.get("id")))
                print(type(User.objects.get(username=request.POST.get("id"))))
                new_user.user=User.objects.get(username=request.POST.get("id"))

                new_user.mng_name=request.POST.get("mng_name")

                new_user.mng_kikwan=request.POST.get("mng_kikwan")
                new_user.mng_bonbu=request.POST.get("mng_bonbu")
                new_user.mng_team=request.POST.get("mng_team")
                new_user.mng_position=request.POST.get("mng_position")
                new_user.mng_tel=request.POST.get("mng_tel")
                new_user.mng_phone=request.POST.get("mng_phone")
                new_user.mng_email=request.POST.get("mng_email")
                new_user.mng_boss = mng_boss
                new_user.auth="MNG"
                new_user.save()
                return HttpResponse("ok")
        else:
            return HttpResponse("no")

    return HttpResponse("")


# --------(대시보드) '승인요청, 공고중 모집종료' 기관관리자 홈화면------------------------------------------------------
# --------[기관관리자. 대시보드 데이터 계산하기]------------------------------------------------------------------------

#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자
# 기능 : 대시보드 데이터 계산
# mng_list, result, end_support_business, result_end, end_set, waiting_support_business, waiting_set, result_end,
# ing_support_business, ing_set ,
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(), VS(), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt

# ------------(기관관리자) 전체 지원사업 공고문의 상태와 정보를 불러온다.---------------------(고치기 : 변수/ 오류 수정)
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자
# 기능 : 전체 지원사업 공고문의 상태와 정보를 불러온다
#  result, user_list, end_support_business , end_set,result_end,waiting_support_business,waiting_set,writing_support_business
#  waiting_set, ing_support_business, ing_set, comp_support_business,comp_set, blind_support_business,blind_set,
#  all_support_business , all_set
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(), VS(), mysql(O)
#-----------------------------------------------------------------------------------------------------------------------



#---------------------(통계) (기관관리자) 기관 관리자가 기관회원 리스트 화면에서 하위 매니저 호출
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자
# 기능 : 기관 관리자가 기관회원 리스트 화면에서 하위 매니저 호출
# id, mngs, temp, m_list
# 함수 완성 여부 :
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------




#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자
# 기능 : 기관 관리자가 기관회원 리스트 화면에서 하위 매니저 호출
# id, mng_acc, temp
# 함수 완성 여부 :
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_mng_acc(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    id = user_auth_id
    mng_acc = AdditionalUserInfo.objects.get(id=id)
    temp={}
    temp["id"] = mng_acc.user.username
    temp["mng_name"] = mng_acc.mng_name
    temp["mng_kikwan"] = mng_acc.mng_kikwan
    temp["mng_bonbu"] = mng_acc.mng_bonbu
    temp["mng_team"] = mng_acc.mng_team
    temp["mng_position"] = mng_acc.mng_position
    temp["mng_tel"] = mng_acc.mng_tel
    temp["mng_phone"] = mng_acc.mng_phone
    temp["mng_email"] = mng_acc.mng_email
    temp["mng_website"] = mng_acc.mng_website
    return JsonResponse((temp), safe = False)


@csrf_exempt
@my_timer
def vue_get_support_business_by_author(request):
    support_business = SupportBusiness.objects.filter(
        support_business_author=AdditionalUserInfo.objects.get(id=request.GET.get("author_id")))
    if request.GET.get("support_business_status")=="ing":
        support_business = support_business.filter(support_business_status=3).filter(support_business_apply_end_ymdt__gte=timezone.now())
    else:
        support_business = support_business.filter(support_business_status__in=[3,4,5,]).filter(Q(support_business_apply_end_ymdt__lte=timezone.now()))
    result=[]
    for s in support_business:
        result.append({
            "value":s.id, "label":s.support_business_name
        })
    return JsonResponse(result , safe=False)






#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_opr_acc(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    id = user_auth_id
    mng_acc = AdditionalUserInfo.objects.get(id=id)
    temp={}
    temp["opr_additional_user_id"] = mng_acc.id
    temp["opr_id"] = mng_acc.user.username
    temp["opr_name"] = mng_acc.mng_name
    temp["opr_kikwan"] = mng_acc.mng_kikwan
    temp["opr_bonbu"] = mng_acc.mng_bonbu
    temp["opr_team"] = mng_acc.mng_team
    temp["opr_position"] = mng_acc.mng_position
    temp["opr_tel"] = mng_acc.mng_tel
    temp["opr_phone"] = mng_acc.mng_phone
    temp["opr_email"] = mng_acc.mng_email
    temp["opr_website"] = mng_acc.mng_website

    return JsonResponse((temp), safe = False)



#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자, 매니저
# 기능 : 기관관리자, 매니저가 바뀐 계정정보를 저장후 업데이트할수있다.
# id, mng_acc
# 함수 완성 여부 :
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_set_opr_acc(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    try:
        username = request.POST.get("opr_id")
        additional_user_info_id = request.POST.get("opr_additional_user_id")
        mng_acc = AdditionalUserInfo.objects.get(id=additional_user_info_id)
        print( request.POST.get("opr_pw1") )
        if request.POST.get("opr_pw0") ==  request.POST.get("opr_pw1"):
            if request.POST.get("opr_pw0") != "":
                user = User.objects.get(id = AdditionalUserInfo.objects.get(id=additional_user_info_id).user.id)
                user.set_password(request.POST.get("opr_pw1"))
                user.save()

        mng_acc.mng_name = request.POST.get("opr_name")
        # mng_acc.mng_kikwan = request.POST.get("opr_kikwan")
        # mng_acc.mng_bonbu= request.POST.get("opr_bonbu")
        # mng_acc.mng_team= request.POST.get("opr_team")
        # mng_acc.mng_position= request.POST.get("opr_position")
        mng_acc.mng_tel= request.POST.get("opr_tel")
        mng_acc.mng_phone = request.POST.get("opr_phone")
        # mng_acc.mng_email = request.POST.get("opr_email")
        # mng_acc.mng_website = request.POST.get("opr_website")
        mng_acc.save()
        return JsonResponse({"result":"true"}, safe = False)
    except:
        return JsonResponse({"result": "false"}, safe=False)

@csrf_exempt
@my_timer
def vue_set_mng_acc(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    try:
        print(request.POST)
        additional_user_info_id = user_auth_id
        mng_acc = AdditionalUserInfo.objects.get(id=additional_user_info_id)
        print(request.POST.get("mng_pw1"))

        #비밀번호를 입력한경우
        if request.POST.get("mng_pw0") == request.POST.get("mng_pw1") and request.POST.get("mng_pw1"):
            if request.POST.get("mng_pw0") != "":
                user = User.objects.get(id=AdditionalUserInfo.objects.get(id=additional_user_info_id).user.id)
                user.set_password(request.POST.get("mng_pw1"))
                user.save()
        #비밀번호를 입력하지 않은 경우 
        mng_acc.mng_name = request.POST.get("mng_name")
        # mng_acc.mng_kikwan = request.POST.get("mng_kikwan")
        # mng_acc.mng_bonbu= request.POST.get("mng_bonbu")
        # mng_acc.mng_team= request.POST.get("mng_team")
        # mng_acc.mng_position= request.POST.get("mng_position")
        mng_acc.mng_tel = request.POST.get("mng_tel")
        mng_acc.mng_phone = request.POST.get("mng_phone")
        # mng_acc.mng_email = request.POST.get("mng_email")
        # mng_acc.mng_website = request.POST.get("mng_website")
        mng_acc.save()
        return JsonResponse({"result": "true"}, safe=False)
    except:
        return JsonResponse({"result": "false"}, safe=False)
#-----------------------------------------------------------------------------------------------------------------------
# [매니저]
#-----------------------------------------------------------------------------------------------------------------------

# ----[[매니저 홈화면 : 대시보드]]
# --------[매니저가 로그인하고, 매니저 홈화면인, 대시보드로 이동 > 서버에서 대시보드에 데이터 나타내는 기능]----(매니저)


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 매니저,
# 기능 : 매니저가 로그인하고, 매니저 홈화면인, 대시보드로 이동 > 서버에서 대시보드에 데이터 나타내는 기능
# result, user_id, end_support_business, end_set, writing_support_business, ing_support_business,
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@my_timer
#postman 작동함
def vue_get_dashboard(request):
    print("서버 연산 시작")
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    result = {}
    support_business_author_id = user_auth_id
    #모집 마감된 공고문
    end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(Q(support_business_status="4")|Q(support_business_status="3")).filter(support_business_author_id=support_business_author_id)
    end_set = []
    for support_business in end_support_business:
        result_end={}
        result_end["id"] = support_business.id
        result_end["author_id"] = support_business.support_business_author.id
        result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
        result_end['support_business_name'] = support_business.support_business_name
        result_end['support_business_poster'] = support_business.support_business_poster

        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] =(Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        try:
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                number = str(round((Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()/int(support_business.support_business_recruit_size),1))
                if( number == "0.0" ):
                    number= "0"
                result_end["comp"] = number +" : 1"
            else:
                result_end["comp"] = ""
        except:
            result_end["comp"] = ""
        end_set.append(copy.deepcopy(result_end))
    blind_support_business = SupportBusiness.objects.filter(support_business_status="6").filter(support_business_author_id=support_business_author_id)
    blind_set = []
    for support_business in blind_support_business:
        result_end = {}
        result_end["id"] = support_business.id
        result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end['support_business_poster'] = support_business.support_business_poster
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        try:
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
                pass
            else:
                result_end["comp"] = ""
        except:
            result_end["comp"] = ""
        blind_set.append(copy.deepcopy(result_end))

    writing_support_business = SupportBusiness.objects.filter(support_business_status="1").filter(support_business_author_id=support_business_author_id)
    writing_set = []
    for support_business in writing_support_business:
        result_end = {}
        result_end["id"] = support_business.id
        result_end["support_business_award_date_ymd"] = str(support_business.support_business_update_at_ymdt).split(" ")[0]
        result_end['support_business_name'] = support_business.support_business_name
        result_end['support_business_poster'] = support_business.support_business_poster
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["comp"]=""
        try:
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
                pass
            else:
                result_end["comp"] = ""
        except:
            result_end["comp"] = ""
        writing_set.append(copy.deepcopy(result_end))

    ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(support_business_author_id=support_business_author_id).filter(support_business_apply_end_ymdt__gt=timezone.now())
    ing_set = []
    for support_business in ing_support_business:

        result_end = {}
        result_end["id"] = support_business.id
        result_end["support_business_award_date_ymd"] = support_business.support_business_pro_0_open_ymd
        result_end["author_id"] = support_business.support_business_author.id
        result_end['support_business_name'] = support_business.support_business_name
        result_end['support_business_poster'] = support_business.support_business_poster
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["comp"]=""
        try:
            if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"

            else:
                result_end["comp"] = ""
        except:
            result_end["comp"] = ""
        ing_set.append(copy.deepcopy(result_end))

    result["end_set"] = end_set
    result["blind_set"] = blind_set
    result["writing_set"] = writing_set
    result["ing_set"] = ing_set
    print("서버 연산 끝")
    print(result)
    return JsonResponse(result, safe=False)


# ------------ (매니저) 본인이 올린 전체 지원사업에 대해서 정보와 상태를 불러오는 함수--------(고치기 : 변수/ 오류 수정)
# --------[지원 사업 관리 페이지, 지원사업 리스트 받아오기  ]-------

#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 매니저,
# 기능 : 지원 사업 관리 페이지, 지원사업 리스트 받아오기
# result,user_id, end_support_business, end_set, waiting_support_business, waiting_set, writing_support_business, writing_set
# ing_support_business , ing_set, comp_support_business, comp_set, all_support_business , all_set
# 함수 완성 여부 : 미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
#----- post정상작동
def vue_get_support_business_info(request):
    result = {}
    # 모집 마감된 공고문
    support_business_author_id = request.POST.get("id")
    #end_support_business = SupportBusiness.objects.filter(apply_end__lt=datetime.now()).filter(status="4").filter(user_id=user_id)
    end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lt=datetime.now()).filter(Q(support_business_status="4")|Q(support_business_status="3")).filter(
        support_business_author_id=support_business_author_id)

    end_set = []
    for support_business in end_support_business:
        result_end = {}
        result_end["id"] = support_business.id
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["author"] = support_business.support_business_author.mng_name
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["status"] = "모집종료"
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["comp"]=""
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        end_set.append(copy.deepcopy(result_end))

    waiting_support_business = SupportBusiness.objects.filter(support_business_status="2").filter( support_business_author_id=support_business_author_id)
    waiting_set = []
    for support_business in waiting_support_business:
        result_end = {}
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["id"] = support_business.id
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["status"] = "승인대기"
        result_end["author"] = support_business.support_business_author.mng_name
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["comp"]=""
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        waiting_set.append(copy.deepcopy(result_end))

    # #작성중인 공고
    writing_support_business = SupportBusiness.objects.filter(Q(support_business_status="1")|Q(support_business_status=None)).filter(support_business_author_id=support_business_author_id)
    writing_set = []
    for support_business in writing_support_business:
        result_end = {}
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["id"] = support_business.id
        result_end["author"] = support_business.support_business_author.mng_name
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["status"] = "작성중"
        if support_business.support_business_recruit_size:
            result_end["comp"] =  " 0 : 1"
        else:
            result_end["comp"] = ""

        writing_set.append(copy.deepcopy(result_end))
    #공고중인 공고
    ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(support_business_apply_end_ymdt__gte=datetime.now()).filter(
        support_business_author_id=support_business_author_id)
    ing_set = []
    for support_business in ing_support_business:
        result_end = {}
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["id"] = support_business.id
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["author"] = support_business.support_business_author.mng_name
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["status"] = "공고중"
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["comp"]=""
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        ing_set.append(copy.deepcopy(result_end))

    #공고 종료된 공고
    comp_support_business = SupportBusiness.objects.filter(support_business_status="5").filter(support_business_apply_end_ymdt__lte=datetime.now()).filter(support_business_author_id=support_business_author_id)
    comp_set = []
    for support_business in comp_support_business:
        result_end = {}
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["id"] = support_business.id
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["author"] = support_business.support_business_author.mng_name
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["status"] = "공고종료"

        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        comp_set.append(copy.deepcopy(result_end))
    #블라인드된 공고문
    blind_support_business = SupportBusiness.objects.filter(support_business_status="6").filter(support_business_author_id= support_business_author_id)
    blind_set = []
    for support_business in blind_support_business:
        result_end = {}
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["id"] = support_business.id
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["author"] = support_business.support_business_author.mng_name
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["status"] = "블라인드"
        result_end["comp"]=""
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        blind_set.append(copy.deepcopy(result_end))

    all_support_business = SupportBusiness.objects.filter(support_business_author_id=support_business_author_id)

    all_set = []
    for support_business in all_support_business:
        result_end = {}
        result_end["id"] = support_business.id
        result_end["support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end['support_business_name'] = support_business.support_business_name
        result_end["support_business_poster"] = support_business.support_business_poster
        result_end["updated"] = support_business.support_business_update_at_ymdt
        result_end["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        try:
            result_end["author"] = support_business.support_business_author.mng_name
        except Exception as e:
            print(e)
        result_end["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count()
        result_end["favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        try:
            if support_business.support_business_status == "4":  # 작성중인 공고문
                result_end["status"] = "모집종료"
            if support_business.support_business_status == "1":  # 작성중인 공고문
                result_end["status"] = "작성중"
            if support_business.support_business_status == "2":  # 승인대기중인 공고문
                result_end["status"] = "승인대기"
            if support_business.support_business_status == "3":
                result_end["status"] = "공고중"
            if support_business.support_business_apply_end_ymdt < timezone.now() and support_business.support_business_status == "3":  # 모집 종료 된 공고문
                result_end["status"] = "모집종료"
            if support_business.support_business_status == "5":  # 공고 종료 된 공고문
                result_end["status"] = "공고종료"
            if support_business.support_business_status == "6":  # 블라인드 공고문
                result_end["status"] = "블라인드"
        except Exception as e:
            print(e)
            print("durl")
            result_end["status"]="작성중"
        result_end["open_date"] = (support_business.support_business_apply_start_ymd)
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size is not None:
            try:
                number =  str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number ="0"
                result_end["comp"] = number + " : 1"
            except:
                result_end["comp"] = ""
        else:
            result_end["comp"] = ""
        all_set.append(copy.deepcopy(result_end))


    result["end_set"] = end_set
    result["blind_set"] = blind_set
    result["writing_set"] = writing_set
    result["ing_set"] = ing_set
    result["waiting_set"] = waiting_set
    result["comp_set"] = comp_set
    result["all_set"] = all_set

    return JsonResponse(result)

# --------(매니저) (기관관리자) 전체지원사업 관리 > 지원사업 모두 불러올 때 + 타매니저 작성 공고 포함 - (고치기 : 변수/ 오류 수정)
# --------[공고문 리스트 가져오기,  ]-------




#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : (매니저) (기관관리자)
# 기능 : 공고문 리스트 가져오기,
# support_business, result_set, temp, status
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_support_business_list(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    support_business = SupportBusiness.objects.exclude(support_business_author_id=user_auth_id)
    k=0
    result_set = []
    for s in support_business:
        temp={}
        temp["id"] = s.id
        temp["index"]=k
        k=k+1
        temp["support_business_name"] = s.support_business_name
        temp["support_business_created_at_ymdt"] = s.support_business_created_at_ymdt
        temp["author"] = s.support_business_author.mng_name
        temp["mng_team"] = s.support_business_author.mng_team
        temp["mng_kikwan"] = s.support_business_author.mng_kikwan
        temp["mng_tel"] = s.support_business_author.mng_tel
        temp["apply_num"] = (Appliance.objects.filter(support_business=s).filter(is_submit=True)).count()
        temp["award_num"] = (Award.objects.filter(support_business=s)).count()
        status=""
        try:
            if  s.support_business_status=="1":
                status="작성중"
            elif s.support_business_status=="2":
                status="승인대기중"
            elif s.support_business_status=="3":
                status="공고중"
            elif s.support_business_status == "4":
                status = "모집종료"
            elif s.support_business_status == "5":
                status = "공고종료"
            elif s.support_business_status == "6":
                status = "블라인드중"

        except:
            print("error")
            status = ""
        temp["status"] = status
        print(status)
        result_set.append(copy.deepcopy(temp))

    return JsonResponse(result_set, safe=False)




#-----------------------------------------------------------------------------------------------------------------------
# [스타트업]
#-----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@my_timer
def opr_vue_get_support_business_list(request):
    support_business = SupportBusiness.objects.exclude(support_business_status=None).exclude(support_business_status=1)
    k=0
    result_set = []
    for s in support_business:
        try:
            temp={}
            temp["opr_id"] = s.id
            temp["opr_index"]=k
            k=k+1
            temp["opr_support_business_name"] = s.support_business_name
            temp["opr_support_business_apply_start_ymd"] = s.support_business_apply_start_ymd
            temp["opr_author"] = s.support_business_author.mng_name
            temp["opr_mng_team"] = s.support_business_author.mng_team
            temp["opr_mng_kikwan"] = s.support_business_author.mng_kikwan
            temp["opr_mng_tel"] = s.support_business_author.mng_tel
            temp["opr_apply_num"] = (Appliance.objects.filter(support_business=s).filter(is_submit=True)).count()
            temp["opr_award_num"] = (Award.objects.filter(support_business=s)).count()
            opr_status=""
            try:
                if  s.support_business_status=="1":
                    opr_status="작성중"
                elif s.support_business_status=="2":
                    opr_status="승인대기중"
                elif s.support_business_status=="3":
                    opr_status="공고중"
                elif s.support_business_status == "4":
                    opr_status = "모집종료"
                elif s.support_business_status == "5":
                    opr_status = "공고종료"
                elif s.support_business_status == "6":
                    opr_status = "블라인드중"

            except:
                print("error")
                opr_status = ""
            temp["opr_status"] = opr_status
            result_set.append(copy.deepcopy(temp))
        except Exception as e:
            print(e)
            pass


    return JsonResponse(result_set, safe=False)


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 모든 유저
# 기능 :  '서비스/프로덕트, 기업소개, 소식' 열람하는 함수
# result, startup, selected_company_filter_list, obj
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
#------------ (모든유저) 타 스타트업 '서비스/프로덕트, 기업소개, 소식' 열람하는 함수
@csrf_exempt
#--------postman정상작동
@my_timer
def vue_get_startup_detail(request):

    if (request.POST.get("area") == "pub"):
        startup = Startup.objects.get(id=request.POST.get("id"))
    else:
        startup = Startup.objects.get(user =AdditionalUserInfo.objects.get(id=request.POST.get("id")).user)
    result = {}
    result["information"] = {}
    result["information"]["id"] = startup.id
    result["information"]["tag"] = []
    result["back_img"] = startup.back_img
    result["logo"] = startup.logo
    result["company_website"] = startup.company_website
    result["company_youtube"] = startup.company_youtube
    result["company_instagram"] = startup.company_instagram
    result["company_facebook"] = startup.company_facebook
    result["company_keyword"] = startup.company_keyword
    result["established_date"]= startup.established_date
    result["company_short_desc"] = startup.company_short_desc
    result["company_intro"] = startup.company_intro
    result["select_tag"]= []
    for f in startup.selected_company_filter_list.all():
        result["select_tag"].append(f.filter_name)
        result["information"]["tag"].append(f.filter_name)
    result["startup_id"] = startup.id
    result["mark_tel"]=startup.mark_tel
    result["company_name"] = startup.company_name
    result["company_kind"] = startup.company_kind
    result["mark_name"] = startup.mark_name
    result["mark_email"] = startup.mark_email
    result["intro_tag"] = []
    result["select_tag"] = []
    for f in startup.selected_company_filter_list.exclude(cat_0 = "지원형태",cat_1="기업형태"):
        result["intro_tag"].append(f.filter_name)
        result["select_tag"].append(f.filter_name)
    if startup.company_total_employee != "":
        result["intro_tag"].append(startup.company_total_employee + "명 이하")
    result["support_business_tag"]=[]
    for f in startup.selected_company_filter_list.filter(cat_0="지원형태"):
        result["support_business_tag"].append(f.filter_name)
    result["select_tag"]= []

    for t in startup.selected_company_filter_list.exclude(filter_name__in=["",None]):
        result["information"]["tag"].append(t.filter_name)
    result['information']["company_website"] = startup.company_website
    result["information"]["repre_email"] =  startup.user.username
    result["address_0"] = startup.address_0
    result["address_1"] = startup.address_1
    result["ip_chk"] = startup.ip_chk
    result["revenue_chk"] = startup.revenue_chk
    result["export_chk"] = startup.export_chk
    result["company_invest_chk"] = startup.company_invest_chk
    result["service"] = []
    result["tag"] = []
    result["pub_tag"]=[]
    for f in startup.selected_company_filter_list.all():
        result["tag"].append(f.filter_name)
    if startup.company_total_employee != "" :
        result["pub_tag"].append( startup.company_total_employee +"명 이하")
        result["tag"].append( startup.company_total_employee +"명 이하")
    for f in startup.selected_company_filter_list.exclude(cat_0='조건',cat_1 = '기업형태' ):
        result["pub_tag"].append(f.filter_name)
    for service  in startup.service_set.all():
        obj = {}
        obj["service_intro"] = service.service_intro
        obj["service_file"] = service.service_file
        obj["file_name"] = service.service_file.split("/")[-1]
        obj["service_name"] = service.service_name
        obj["service_img"] = service.service_img
        obj["img_name"] = service.service_img.split("/")[-1]
        obj["id"] = service.id
        result["service"].append(copy.deepcopy(obj))
    result["company_history"] = []
    for history in startup.history_set.all():
        obj = {}
        obj["company_history_year"] = history.company_history_year
        obj["company_history_month"] = history.company_history_month
        obj["company_history_content"] = history.company_history_content
        obj["id"] = history.id
        result["company_history"].append(copy.deepcopy(obj))
    result["revenue_before_year_0"] = startup.revenue_before_year_0
    result["revenue_before_year_1"] = startup.revenue_before_year_1
    result["revenue_before_year_2"] = startup.revenue_before_year_2
    result["revenue_before_0"] = startup.revenue_before_0
    result["revenue_before_1"] = startup.revenue_before_1
    result["revenue_before_2"] = startup.revenue_before_2
    result["export_before_year_0"] = startup.export_before_year_0
    result["export_before_year_1"] = startup.export_before_year_1
    result["export_before_year_2"] = startup.export_before_year_2
    result["export_before_0"] = startup.export_before_0
    result["export_before_1"] = startup.export_before_1
    result["export_before_2"] = startup.export_before_2
    result["export_before_nation_0"] = startup.export_before_nation_0
    result["export_before_nation_1"] = startup.export_before_nation_1
    result["export_before_nation_2"] = startup.export_before_nation_2
    result["attached_cert_file"]= startup.attached_cert_file
    result["attached_ip_file"] = startup.attached_ip_file
    result["invest"] = []
    for invest in startup.companyinvest_set.all():
        obj = {}
        obj["company_invest_year"] = invest.company_invest_year
        obj["company_invest_size"] = invest.company_invest_size
        obj["company_invest_agency"] = invest.company_invest_agency
        result["invest"].append(copy.deepcopy(obj))
    result["news"] = []
    for news in startup.activity_set.order_by("-company_activity_created_at").all():
        obj = {}
        obj["company_activity_created_at"] = news.company_activity_created_at
        obj["company_activity_text"] = news.company_activity_text
        obj["company_activity_img"] = news.company_activity_img
        obj["company_activity_youtube"] = news.company_activity_youtube
        obj["like_num"] = (news.activitylike_set).count()
        obj["rep_num"] = (news.reply_set).count()
        obj["id"] = news.id
        obj["rep"] = []
        for rep in news.reply_set.select_related("company_activity_author"):
            temp = {}
            # temp["logo"] = rep.activity.startup.clip_thumbnail
            temp["company_activity_text"] = rep.company_activity_text
            temp["company_activity_created_at"] = rep.company_activity_created_at
            temp["rep_author"] = rep.company_activity_author.user.username
            temp["id"] = rep.id
            obj["rep"].append(copy.deepcopy(temp))
        result["news"].append(copy.deepcopy(obj))
    print("end")
    return JsonResponse(result)
# 수정전
# 쿼리수 : 81
# vue_get_startup_detail 함수가 실행된 총 시간: 1.6355056762695312 초
# db 쿼리 시간 :  1.5760000000000007 초
# 쿼리 제외한 연산 시간 :  0.059505676269530516 초
# 수정후
# 53
# vue_get_startup_detail 함수가 실행된 총 시간: 0.8177502155303955 초
# db 쿼리 시간 :  0.7750000000000006 초
# 쿼리 제외한 연산 시간 :  0.04275021553039493 초


#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : (스타트업 유저)
# 기능 : 스타트업정보 -회사 소개 가져오기,
# startup,result - result["back_img"],result["logo"],result["company_website"],result["company_youtube"],result["company_instagram"]
# result["company_facebook"], result["established_date"], result["select_tag"], result["repre_tel"], result["repre_email"]
# .result["startup_id"], result["company_name"], result["repre_name"], result["company_keyword"], result["address_0"]
# result["address_1"], result["company_intro"], result["information"], result["information"], result["information"]["id"]
# ,result["information"]["tag"],   result['information']["company_website"], result['information']["repre_email"] , result["location"]
# result["service"], result["tag"] , result["company_history"],  obj["company_history_year"], obj["company_history_month"],obj["company_history_content"]
# result["service"], result["tag"] , result["company_history"],  obj["company_history_year"], obj["company_history_month"],obj["company_history_content"]

# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(o), VS(o), mysql(o)
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_startup_detail_base(request):
    print("hello")

    startup = AdditionalUserInfo.objects.get(id=request.POST.get("id")).user.startup
    result = {}
    result["back_img"] = startup.back_img
    result["logo"] = startup.logo
    result["company_website"] = startup.company_website
    result["company_youtube"] = startup.company_youtube
    result["company_instagram"] = startup.company_instagram
    result["company_facebook"] = startup.company_facebook
    result["established_date"]= str(startup.established_date).split("T")[0]
    result["select_tag"]= ""
    result["repre_tel"] =startup.repre_tel
    result["repre_email"] = startup.user.username
    result["mark_tel"] = startup.mark_tel
    result["mark_email"] = startup.mark_email
    result["mark_name"] = startup.mark_name
    result["startup_id"] = startup.id
    result["company_name"] = startup.company_name

    result["company_keyword"] = startup.company_keyword
    result["company_kind"] = startup.company_kind

    result["address_0"] = startup.address_0
    result["address_1"] = startup.address_1
    result["company_intro"] = startup.company_intro
    result["information"] = {}
    result["information"]["id"] = startup.id
    result["information"]["tag"] = []
    result['information']["company_website"] = startup.company_website
    result['information']["mark_email"] = startup.mark_email
    try:
        result["location"] = startup.address_0 + startup.address_1
    except:
        pass
    result["service"] = []
    result["tag"] = []
    result["intro_tag"] = []
    result["select_tag"] = []
    for f in startup.selected_company_filter_list.all():
        result['information']["tag"].append(f.filter_name)
        if f.cat_0 == "기본장르" or f.cat_0 == "영역" or f.cat_0 == "조건":
            print("필터를 넣습니다.")
            result["intro_tag"].append(f.filter_name)
            result["select_tag"].append(f.filter_name)
    result["company_history"] = []
    print(startup.company_total_employee)
    if startup.company_total_employee != "":
        print("hrer")
        print(  result["intro_tag"])

        result["intro_tag"].append(startup.company_total_employee+" 명 이하")
    for history in startup.history_set.all():
        obj={}
        obj["company_history_year"] = history.company_history_year

        obj["company_history_month"] = history.company_history_month
        obj["company_history_content"] = history.company_history_content
        obj["id"] = history.id
        result["company_history"].append(copy.deepcopy(obj))


    return JsonResponse(result)




# -------- (스타트업) 회원가입]-----------------------------------------------------------------------------------------
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : (스타트업 유저 )
# 기능 : 스타트업회원가입
# startup,result ,form, EmailConfirmation, user,
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@my_timer
def vue_signup(request):

    if request.method == "POST":
        form = LoginForm(request.POST)
        print(form)
        print(request.POST)
        print(form.is_valid())
        print( EmailConfirmation.objects.filter(email=form.cleaned_data["username"]).order_by("-id")[
                            0].confirmation_code == request.POST.get("confirmation_code"))
        if form.is_valid() and \
                        EmailConfirmation.objects.filter(email=form.cleaned_data["username"]).order_by("-id")[
                            0].confirmation_code == request.POST.get("confirmation_code"):
            user = User.objects.create_user(username=form.cleaned_data["username"],
                                            password=form.cleaned_data["password"])
            EmailConfirmation.objects.filter(email=form.cleaned_data["username"]).order_by("-id")[0].confirm = True
            if user is not None:
                AdditionalUserInfo(user=user,  auth="USR").save()
                Startup(user=user, mark_email=form.cleaned_data["username"], company_name="", company_short_desc="" ).save()
                user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
                print(user)
                print(user.pk)
                if user is not None:
                    login(request, user)
                    print("before_session_create")

                    engine = import_module(settings.SESSION_ENGINE)
                    session = engine.SessionStore(None)

                    session.clear()
                    session.create()

                    session[SESSION_KEY] = user.pk
                    print("========")

                    session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
                    # session[HASH_SESSION_KEY] = user.get_session_auth_hash()
                    session.save()

                    print(user.id)
                    print(session.session_key)

                return JsonResponse({"result":"ok","id":user.additionaluserinfo.id, "user":"USR", "code":"USR", "session_key":session.session_key})
            else:
                return JsonResponse({"result":"false","message":"이미가입"})
        else:
            return JsonResponse({"result": "false","message":"인증번호"})

@csrf_exempt
@my_timer
def token_check(request):
    form = LoginForm(request.POST)
    num = len(EmailConfirmation.objects.filter(email=form.cleaned_data["username"]).order_by("-id")[
        0].confirmation_code == request.POST.get("confirmation_code"))


# ---- (스타트업) 계정정보 ---------------------------------------------------------------------------------------------
# --------[유저 인포메이션 정보저장]-------
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업,
# 기능 : 유저 인포메이션 정보저장
# ad
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------

#TODO: 소셜 로그인시 네이버, 페이스북, 카카오톡  인증 여부 테이블-프로바이더 테이블 만들고 계정페이지에서 나타낼것 - 기관관,매니저 - 개인회원 페이지 연동.
@csrf_exempt
@my_timer
def vue_set_usr_info(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    print(request)
    ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    ad.user.startup.mark_tel = request.POST.get("mark_tel")
    ad.user.startup.mark_name = request.POST.get("mark_name")
    ad.user.startup.save()
    if request.POST.get("agreement") == True:
        ad.agreement = True
    else:
        ad.agreement = False
    ad.sns = request.POST.get("facebook")
    ad.save()
    print(ad.sns)
    return JsonResponse({"result": "ok"})

# ---- (스타트업) db에 입력된 계정정보를 뷰단에 뿌려주는 함수

# ---- (스타트업) 계정정보 ---------------------------------------------------------------------------------------------
# --------[유저 인포메이션 정보저장]-------
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업,
# 기능 : 유저 인포메이션 정보저장
# result
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_usr_info(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    ad = AdditionalUserInfo.objects.get(id=user_auth_id)

    result = {}
    result["mark_tel"] =  ad.user.startup.mark_tel
    result["mark_name"] =  ad.user.startup.mark_name
    result["agreement"] = ad.agreement
    result["mark_email"] = ad.user.username
    result["facebook"] = ad.sns
    return JsonResponse({"result": result})




#---------------------(기관관리자) 스타트업 리스트를 가져와서 스타트업들에게 알람은 추가하는 DB : 기관 관리자가 승인하게되면, 해당 지원사업에 비슷한 필터를 등록한 스타트업에게 알람간다.

#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 기관관리자,
# 기능 : 스타트업 리스트를 가져와서 스타트업들에게 알람은 추가하는 DB
# filter_list, a
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------

def vue_get_alarm_startup(arr,msg, support_business_id):

    startup_list=[]
    filter_list = arr
    #동일한 필터를 가진 스타트업
    filter_startup_list = Startup.objects.filter(selected_company_filter_list__in=filter_list)
    #좋아요를 누른 스타트업
    favorite_additionaluser_list = AdditionalUserInfo.objects.filter(favorite=SupportBusiness.objects.get(id=support_business_id))
    print(favorite_additionaluser_list)
    #지원사업에 지원한 스타트업
    apply_startup = Startup.objects.filter(appliance__support_business=SupportBusiness.objects.get(id=support_business_id))
    print(apply_startup)
    # for s in filter_startup_list:
    #     if s.support_business_author.additionaluserinfo.id not in startup_list:
    #         startup_list.append(s.support_business_author.additionaluserinfo.id)
    for s in favorite_additionaluser_list:
        if s.id not in startup_list:
            startup_list.append(s.id)
    for s in apply_startup:
        if s.user.additionaluserinfo.id not in startup_list:
            startup_list.append(s.user.additionaluserinfo.id)

    for s in startup_list:
        a = Alarm()
        a.support_business_author_id = s
        a.alarm_content = msg
        a.user = AdditionalUserInfo.objects.get(id=s)
        a.alarm_origin_support_business_id =  support_business_id
        a.save()

# ----------(스타트업) 스타트업의 정보가 변경되었을 때, 해당 스타트업에 좋아요 누른 '스타트업 유저'에게 알람을 준다.
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업,
# 기능 :  스타트업의 정보가 변경되었을 때, 해당 스타트업에 좋아요 누른 '스타트업 유저'에게 알람을 준다
# follow_users, startup_name, a
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------

def vue_get_follow_startup(st_id):

    follow_users = Startup.objects.get(id=st_id).additionaluserinfo_set
    startup_name = Startup.objects.get(id=st_id).company_name
    print("add alarm")
    for a_follow_user in follow_users.all():
        print("add alarm2")
        a = Alarm()
        a.user = a_follow_user
        a.alarm_content = startup_name + "의 정보가 변경되었습니다"
        a.alarm_origin_st = Startup.objects.get(id=st_id)
        a.save()



# -----(중복) : 뷰단에서 찾아서 수정/통합 후 삭제=> 함수 변경 2018-08-18T11:53:00Z
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업,
# 기능 :  스타트업 유저의 관심 지원사업 리스트를 보여준다
# id, ad, f, list
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------






# ----------(스타트업) 모든 읽지 않은 알람 리스트 불러오기
#-----[체크리스트]------------------------------------------------------------------------------------------------------
# 대상 : 스타트업,
# 기능 :  모든 읽지 않은 알람 리스트 불러오기
# user_id, user, alarm_set,
# 함수 완성 여부 :  미완성
# 변수 체크 여부 : py(), VS(), mysql()
#-----------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def get_unread_alarm(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    try:
        user_id = user_auth_id
        user = AdditionalUserInfo.objects.get(id=user_id)
        alarm_set = []
        print(user)
        for a in Alarm.objects.filter(user=user).filter(alarm_read=False).order_by("-alarm_created_at"):
            kind=""
            if a.alarm_origin_support_business_id == None:
                kind = "startup"
                alarm_set.append({
                    "id": a.id,
                    "alarm_kind": kind,
                    "alarm_content": a.alarm_content,
                    "alarm_origin_support_business": "",
                    "alarm_origin_support_business_id": "",
                    "alarm_origin_st": a.alarm_origin_st.company_name,
                    "alarm_origin_st_id": a.alarm_origin_st_id,
                    "alarm_created_at": a.alarm_created_at,
                })
            else:
                kind ="support_business"
                alarm_set.append({
                    "id":a.id,
                    "alarm_kind":kind,
                    "alarm_content":a.alarm_content,
                    "alarm_origin_support_business":a.alarm_origin_support_business.support_business_name,
                    "alarm_origin_support_business_id": a.alarm_origin_support_business_id,
                    "alarm_origin_st":"",
                    "alarm_origin_st_id": "",
                    "alarm_created_at":a.alarm_created_at,
                })
    except Exception as e :
        print(e)
        pass

    return JsonResponse((alarm_set), safe=False)



# ----------------------------------------------------------------------------------------------------------------------
# 나. 기관 관리자가 매니저 회원 생성
#       <목표>
#       공고문을 등록할수 있는 매니저를 생성한다
#       매니저가 쓴 공고문의 통계를 취합해서 볼수 있다.
#----------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------
# 다. 매니저 : 공고문 생성 + 지원서 양식지정
#       <목표>
#       매니저는 유저가 지원할수있는 공고문과 지원서 양식을 생성할수있다.
#----------------------------------------------------------------------------------------------------------------------





# --------[공고문 정보 업데이트 기능 : 공통]------------------------------------------------------------------ (매니저)
@csrf_exempt
@my_timer
def vue_set_support_business_information(request):
    support_business = SupportBusiness.objects.get(id=request.GET.get("id"))
    rjd = json.loads(request.POST.get("json_data"))
    support_business.support_business_name = rjd["support_business_name"]
    support_business.support_business_name_tag = rjd["support_business_name_tag"]
    support_business.support_business_name_sub = rjd["support_business_name_sub"]
    support_business.support_business_poster = rjd["support_business_poster"]
    support_business.support_business_short_desc = rjd["support_business_short_desc"]
    support_business.support_business_subject = rjd["support_business_subject"]
    support_business.support_business_detail = rjd["support_business_detail"]
    support_business.support_business_apply_start_ymd = rjd["support_business_apply_start_ymd"]
    support_business.support_business_apply_end_ymdt = rjd["support_business_apply_end_ymdt"]
    support_business.support_business_object = rjd["support_business_object"]
    support_business.support_business_prefer = rjd["support_business_prefer"]
    support_business.support_business_constraint = rjd["support_business_constraint"]
    support_business.support_business_recruit_size = rjd["support_business_recruit_size"]
    support_business.support_business_pro_0_choose = rjd["support_business_pro_0_choose"]
    support_business.support_business_pro_0_start_ymd = rjd["support_business_pro_0_start_ymd"]
    support_business.support_business_pro_0_end_ymd = rjd["support_business_pro_0_end_ymd"]
    support_business.support_business_pro_0_open_ymd = rjd["support_business_pro_0_open_ymd"]
    support_business.support_business_pro_0_criterion = rjd["support_business_pro_0_criterion"]
    support_business.support_business_pro_1_choose = rjd["support_business_pro_1_choose"]
    support_business.support_business_pro_1_start_ymd = rjd["support_business_pro_1_start_ymd"]
    support_business.support_business_pro_1_end_ymd = rjd["support_business_pro_1_end_ymd"]
    support_business.support_business_pro_1_open_ymd = rjd["support_business_pro_1_open_ymd"]
    support_business.support_business_pro_1_criterion = rjd["support_business_pro_1_criterion"]
    support_business.support_business_pro_2_choose = rjd["support_business_pro_2_choose"]
    support_business.support_business_pro_2_start_ymd = rjd["support_business_pro_2_start_ymd"]
    support_business.support_business_pro_2_end_ymd = rjd["support_business_pro_2_end_ymd"]
    support_business.support_business_pro_2_open_ymd = rjd["support_business_pro_2_open_ymd"]
    support_business.support_business_pro_2_criterion = rjd["support_business_pro_2_criterion"]
    support_business.support_business_supply_content = rjd["support_business_supply_content"]
    support_business.mng_support_business_step_6_etc_input = rjd["mng_support_business_step_6_etc_input"]
    support_business.support_business_ceremony_start_ymd = rjd["support_business_ceremony_start_ymd"]
    support_business.support_business_ceremony_end_ymd = rjd["support_business_ceremony_end_ymd"]
    support_business.support_business_faq = rjd["support_business_faq"]
    support_business.support_business_additional_faq = rjd["support_business_additional_faq"]
    support_business.support_business_meta = rjd["support_business_meta"]
    support_business.support_business_meta_0 = rjd["support_business_meta_0"]


    return JsonResponse({"result":"ok"})



import base64
import os.path
#-----------------------------------------------------------------------------------------------------------------------
# --------[공고문 생성 프로세스 시작! //공고문 생성시 필터 사용: SBF 사용]----------------------------------------------
# --------[공고문 작성 기능 (지원서 작성 첫번째 페이지, 1 페이지) : 공고문 수정하기]------- (매니저)
# 첫번째 작성시 'new'의 동작 시점을 한단계 앞당기기 [현재 시점 : 공고문 작성 1p->2p => 변경시점 : 공고문 작성 버튼 눌렀을 때]
# 단, 조심할 것! 매주기마다 url만 생성되고 내용이 없는 공고문은 삭제하기

@csrf_exempt
@my_timer
def vue_make_application(request):

    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    new_support_business = SupportBusiness()
    new_support_business.support_business_author_id = user_auth_id
    new_support_business.save()
    print(new_support_business.id)
    return JsonResponse({"id":new_support_business.id})

# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_1(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    if rjd["id"] != "new":
        support_business = SupportBusiness.objects.get(id=rjd.get("id"))
    else:
        support_business = SupportBusiness()
    print(rjd)
    support_business.support_business_name = rjd.get("support_business_name")

    try:
        support_business.support_business_name_tag = rjd.get("support_business_name_tag")
    except:
        pass
    try:
        support_business.support_business_short_desc = rjd.get("support_business_short_desc")
    except:
        pass
    if  rjd.get("user") == "mng":
        support_business.support_business_status = "1"


    support_business.save()
    if request.FILES.get('file'):
        support_business.support_business_poster = handle_uploaded_file_poster(request.FILES['file'], str(request.FILES['file']))
        print(os.path.exists( support_business.support_business_poster) )
        print("exist check")
        with open( support_business.support_business_poster, "rb") as image_file:
            print(image_file)
            encoded_string = base64.b64encode(image_file.read())
        print(encoded_string)
        print("========")
        print(encoded_string.decode('utf-8'))
        # support_business.support_business_poster_data_url \
        #     ="data:image/"+support_business.support_business_poster.split(".")[-1]+";base64,"+ encoded_string.decode('utf-8')
    try:
        support_business.support_business_meta_0= rjd.get("support_business_meta_0")
    except:
        pass
    try:
        support_business.support_business_subject = rjd.get("support_business_subject")
    except:
        pass
    try:
        support_business.support_business_detail = rjd.get("support_business_detail")
    except:
        pass
    print(support_business.support_business_detail)
    try:
        support_business.support_business_name_sub = rjd.get("support_business_name_sub")
    except:
        pass
    support_business.save()
    print(support_business.id)

    return JsonResponse({"result":support_business.id})


# --------[공고문 내용 업데이트 기능 (지원서 작성 두번째 페이지, 2 페이지) : 공고문 수정하기]------- (매니저)
# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_2(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    support_business = SupportBusiness.objects.get(id=rjd.get("id"))
    tag = rjd.get("supply_tag")

    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_0 == "지원형태":
            support_business.selected_support_business_filter_list.remove(t)
    for t in tag:
        support_business.selected_support_business_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))
    try:
        support_business.support_business_supply_content = rjd.get("support_business_supply_content")
    except:
        pass
    support_business.save()
    return JsonResponse({"result":"ok"})




import re
# --------[공고문 내용 업데이트 기능 (지원서 작성 세번째 페이지) 3 페이지 : 공고문 수정하기]------- (매니저)
# ------ postman정상작동
from django.utils import timezone
@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_3(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    support_business = SupportBusiness.objects.get(id=rjd.get("id"))
    tag = rjd.get("recruit_tag")


    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_0 == "기본장르" or t.cat_0 == "영역":
            support_business.selected_support_business_filter_list.remove(t)

    # 모집 조건 필터
    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_0 == "조건":
            support_business.selected_support_business_filter_list.remove(t)

    for t in tag:
        print(t)
        if "명 이" not in t:
            support_business.selected_support_business_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))

    for t in tag:
        if "명 이" in t :
            num = int(re.findall('\d+', t)[0])
            if num != 0:
                support_business.support_business_employee_condition = num
            else:
                pass
        else:
            support_business.selected_support_business_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))

    if rjd["support_business_apply_start_ymd"] !="":
        if rjd["support_business_apply_start_ymd"].split("T")[0] != "":
            support_business.support_business_apply_start_ymd = rjd.get("support_business_apply_start_ymd").split("T")[0]
            support_business.save()
    if rjd["support_business_apply_end_ymdt"] !="":
        support_business.support_business_apply_end_ymdt = rjd.get("support_business_apply_end_ymdt").split(".")[0]
    support_business.save()

    support_business.support_business_recruit_size = rjd.get("support_business_recruit_size")
    support_business.support_business_prefer = rjd.get("support_business_prefer")
    support_business.support_business_constraint = rjd.get("support_business_constraint")
    support_business.mng_support_business_step_3_etc_input_mojipjogun = rjd.get("mng_support_business_step_3_etc_input_mojipjogun")
    support_business.mng_support_business_step_3_etc_input_mojipgenre = rjd.get("mng_support_business_step_3_etc_input_mojipgenre")
    support_business.mng_support_business_step_3_etc_input_mojipjogun_chk = rjd.get("mng_support_business_step_3_etc_input_mojipjogun_chk")
    support_business.mng_support_business_step_3_etc_input_mojipgenre_chk = rjd.get("mng_support_business_step_3_etc_input_mojipgenre_chk")

    try:
        if rjd.get("support_business_prefer_chk") == True:
            support_business.support_business_prefer_chk = True
        else :
            support_business.support_business_prefer_chk = False
    except:
        support_business.support_business_prefer_chk = False
    try:
        if rjd.get("support_business_constraint_chk") == True:
            support_business.support_business_constraint_chk = True
        else :
            support_business.support_business_constraint_chk = False
    except:
        support_business.support_business_constraint_chk = False
    try:
        support_business.support_business_update_at_ymdt = timezone.now()
    except:
        pass
    support_business.save()
    return JsonResponse({"result":"ok"})


# --------[공고문 내용 업데이트 기능 (지원서 작성 네번째 페이지) 4 페이지 : 공고문 수정하기]------- (매니저)
# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_4(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    support_business = SupportBusiness.objects.get(id=rjd.get("id"))

    print(rjd)
    support_business.support_business_pro_0_choose = rjd.get("support_business_pro_0_choose")
    support_business.support_business_pro_1_check = rjd.get("support_business_pro_1_check")
    support_business.support_business_pro_2_check = rjd.get("support_business_pro_2_check")


    try:
        if rjd.get("support_business_pro_0_start_ymd") !="":
            support_business.support_business_pro_0_start_ymd = rjd.get("support_business_pro_0_start_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_0_end_ymd").split("T")[0] !="":
            support_business.support_business_pro_0_end_ymd = rjd.get("support_business_pro_0_end_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_0_open_ymd") != "":
            support_business.support_business_pro_0_open_ymd = rjd.get("support_business_pro_0_open_ymd").split("T")[0]
    except:
        pass
    try:
        support_business.support_business_pro_0_criterion = rjd.get("support_business_pro_0_criterion")
    except:
        pass
    try:
        support_business.support_business_pro_1_choose = rjd.get("support_business_pro_1_choose")
    except:
        pass
    try:
        if rjd.get("support_business_pro_1_start_ymd") != "":
            support_business.support_business_pro_1_start_ymd = rjd.get("support_business_pro_1_start_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_1_end_ymd").split("T")[0] != "":
            support_business.support_business_pro_1_end_ymd = rjd.get("support_business_pro_1_end_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_1_open_ymd") != "":
            support_business.support_business_pro_1_open_ymd = rjd.get("support_business_pro_1_open_ymd").split("T")[0]
    except:
        pass
    try:
        support_business.support_business_pro_1_criterion = rjd.get("support_business_pro_1_criterion")
    except:
        pass
    try:
        support_business.support_business_pro_2_choose = rjd.get("support_business_pro_2_choose")
    except:
        pass
    try:
        if rjd.get("support_business_pro_2_start_ymd") != "":
            support_business.support_business_pro_2_start_ymd = rjd.get("support_business_pro_2_start_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_2_end_ymd").split("T")[0] != "":
            support_business.support_business_pro_2_end_ymd = rjd.get("support_business_pro_2_end_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_pro_2_open_ymd") != "":
            support_business.support_business_pro_2_open_ymd = rjd.get("support_business_pro_2_open_ymd").split("T")[0]
    except:
        pass
    try:
        support_business.support_business_pro_2_criterion = rjd.get("support_business_pro_2_criterion")
    except:
        pass

    support_business.save()
    return JsonResponse({"result":"ok"})

    # --------[공고문 내용 업데이트 기능 (지원서 작성 다섯번째 페이지) 5 페이지 : 공고문 수정하기]------- (매니저)

@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_5(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))

    print(request.POST)
    print(request.FILES)



    print(rjd)
    support_business = SupportBusiness.objects.get(id=rjd["id"])


    if request.FILES:
        print("첫번째 if 문 통과")
        for key in request.FILES:
            name = request.FILES[key].name
            if not os.path.exists('media/uploads/sb/' + str(support_business.id) + '/business_file/'):
                os.makedirs('media/uploads/sb/' + str(support_business.id) + '/business_file')
            with open('media/uploads/sb/' + str(support_business.id) + '/business_file/' +  (name),
                      'wb+') as destination:
                for chunk in request.FILES[key].chunks():
                    destination.write(chunk)
            sb_file = SupportBusinessAttachedFiles()
            sb_file.support_business = support_business
            sb_file.file_path = 'media/uploads/sb/' + str(support_business.id) + '/business_file/' + name
            sb_file.save()
    try:
        support_business.support_business_meta = rjd.get("support_business_meta")
    except:
        pass
    try:
        support_business.support_business_etc_file_title_mng = rjd.get("support_business_etc_file_title_mng")
    except:
        pass
    support_business.save();
    return JsonResponse({"result":"ok"})

    # --------[공고문 내용 업데이트 기능 (지원서 작성 여섯번째 페이지) 6 페이지 : 공고문 수정하기]------- (매니저)

@csrf_exempt
@my_timer
def vue_set_mng_support_business_step_6(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))

    support_business = SupportBusiness.objects.get(id=rjd["id"])

    try:
        if rjd.get("support_business_ceremony_start_ymd") != '':
            support_business.support_business_ceremony_start_ymd = rjd.get("support_business_ceremony_start_ymd").split("T")[0]
    except:
        pass
    try:
        if rjd.get("support_business_ceremony_end_ymd") != '':
            support_business.support_business_ceremony_end_ymd = rjd.get("support_business_ceremony_end_ymd").split("T")[0]
    except:
        pass
    try:
        support_business.support_business_faq = rjd.get("support_business_faq")
    except Exception as e:
        print(e)
    try:
        support_business.support_business_additional_faq = rjd.get("support_business_additional_faq")
    except Exception as e:
        print(e)
    try:
        support_business.mng_support_business_step_6_etc_input = rjd.get("mng_support_business_step_6_etc_input")
    except Exception as e:
        print(e)
    try:
        if rjd.get("mng_support_business_step_6_etc_input_chk")== True:
            support_business.mng_support_business_step_6_etc_input_chk = True
        else:
            support_business.mng_support_business_step_6_etc_input_chk = False
    except Exception as e:
        print(e)
    try:
        if rjd.get("support_business_ceremony_chk") == True:
            support_business.support_business_ceremony_chk = True
        else:
            support_business.support_business_ceremony_chk = False
    except Exception as e:
        print(e)
    try:
        if  rjd.get("support_business_faq_chk") == True:
            support_business.support_business_faq_chk = True
        else:
            support_business.support_business_faq_chk = False
    except Exception as e:
        print(e)
    try:
        if rjd.get("support_business_additional_faq_chk")== True:
            support_business.support_business_additional_faq_chk = True
        else:
            support_business.support_business_additional_faq_chk = False
    except Exception as e:
        print(e)
    support_business.save()
    return JsonResponse({"result":"ok"})




# --------[공고문 제출하기 기능 (지원서 작성 마무리) 6 페이지 : 공고문 제출하기]------- (매니저)
# ------ postman정상작동
@csrf_exempt
@my_timer
def mng_support_business_step_7(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    id = json.loads(request.POST.get("json_data"))["id"]
    support_business = SupportBusiness.objects.get(id=id)


    support_business.support_business_status = "2"
    support_business.save();
    return JsonResponse({"result":"success"})

#----------------공고문 작성/제출하기 완료!!----------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------------------
# 라. 기관 관리자 : 승인
#       <목표>
#       기관 관리자는 매니저가 작성하고 승인 요청한 공고문을 승인할 수 있다.
#       <승인 단계>
#           - 공고문 작성중 : 1
#           - 승인 요청 : 2
#           - 공고중
#           - 모집종료 : 4
#           - 공고종료 : 5
#           - 블라인드 : 6
#----------------------------------------------------------------------------------------------------------------------



#------------ (기관관리자) 승인 요청된 공고문, 승인 완료된 공고문 블라인드 하기
@csrf_exempt
@my_timer
def support_business_blind(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    id =request.GET.get("id")
    support_business = SupportBusiness.objects.get(id=id)
    support_business.support_business_status = "6"
    support_business.save()
    vue_get_alarm_startup(support_business.selected_support_business_filter_list.all(),"해당 지원사업이 블라인드 처리되었습니다.",id)

    return JsonResponse({"result":"success"})


#------------ (기관관리자) 매니저가 승인요청한 공고문을 승인하기 : 승인요청(2) > 공고중(3)
@csrf_exempt
@my_timer
def support_business_open(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    id = request.GET.get("id")
    support_business = SupportBusiness.objects.get(id=id)
    support_business.support_business_status = "3"
    support_business.save();
    vue_get_alarm_startup(support_business.selected_support_business_filter_list.all(),"공고문이 등록/수정되었습니다.",id)
    return JsonResponse({"result":"success"})


#----------------------------------------------------------------------------------------------------------------------
# 마. 매니저 : 지원사업 관리, 승인/ 블라인드/ 날짜별로 구분되어 모집마감, 공고종료
#       <목표>
#       지원사업의 단계에 따라 '지원사업 공고문'이 분류되어 리스트로 나타난다.
#----------------------------------------------------------------------------------------------------------------------

import threading
def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def set_support_business_status():
    print("set")
    for support_business in SupportBusiness.objects.all():
        try:
            if support_business.support_business_status == "3" and support_business.support_business_apply_end_ymdt < timezone.now():
                support_business.support_business_status = "4"
                support_business.save()
        except:
            print(support_business)
@csrf_exempt
def set_support_business_status_trigger(request):
    setInterval(set_support_business_status, 10)
    return HttpResponse("")






#----------------------------------------------------------------------------------------------------------------------
# 바. 기업 정보 제대로 저장될것, 동기화 될것, -> 프로필_마이페이지(계정 관련), 스타트업 상세 페이지_서비스/프로덕트
#       <목표>
#        프로필_마이페이지(계정 관련), 스타트업 상세 페이지_서비스/프로덕트간 정보가 동기화 되어 화면에 나타날것
#----------------------------------------------------------------------------------------------------------------------

# ------[ 중복 그룹 2 ]----def 2개 중복-----------------------------------------------------------------------------------
# --------[1.스타트업 정보 저장 기능, 로그인 기능]------------------------------------------------------------------
#------------ (스타트업) 내 회사 정보 저장 : 내 기업페이지 관리
# >> 기업 소개 페이지에서 많은 데이터 들이 접속을 하면서 사이트가 응답없음이 되어서 페이지에서 필요한 데이터만 남겨서
# 함수를 만들었습니다.
#-----[1/2]----
@csrf_exempt
#----------postman 정상작동
@my_timer
def vue_update_startup_detail_base(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    #file_path = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']), rjd["startup_id"]  )
    startup = Startup.objects.get(id=rjd["startup_id"])

    startup.company_website = rjd["information"]["company_website"]
    startup.mark_email =  rjd["mark_email"]
    startup.mark_name = rjd["mark_name"]
    startup.mark_tel = rjd["mark_tel"]
    startup.company_intro = rjd["company_intro"]
    try:
        startup.company_kind = rjd["company_kind"]

    except:
        pass
    startup.company_youtube = rjd["company_youtube"]
    startup.company_instagram = rjd["company_instagram"]
    startup.company_keyword = rjd["company_keyword"]
    startup.established_date = rjd["established_date"].split("T")[0]
    startup.company_facebook = rjd["company_facebook"]
    startup.address_0= rjd["address_0"]
    startup.address_1 = rjd["address_1"]
    for f in startup.selected_company_filter_list.all():
        if f.cat_0 =="영역" or f.cat_0 =="기본장르" or f.cat_0 =="조건":
            startup.selected_company_filter_list.remove(f)
    for k in rjd["intro_tag"]:

        print(k)

        if "명 이하" in k or "명 이상" in k:

            num = int(re.findall('\d+', k)[0])

            startup.company_total_employee = num

        elif k != "구성원 제한없음":
            startup.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=k))
    try:
        startup.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=rjd["company_kind"]))
    except:
        print("")
    startup.user.additionaluserinfo.save()
    startup.save()
    try:

        for history in rjd["company_history"]:
            if history.get("id"):
                his = History.objects.get(id=history.get("id"))
            else:
                his = History()

            print(history["company_history_year"])
            print(history["company_history_content"])
            if history["company_history_year"] !="" and  history["company_history_content"] !="":
                his.company_history_year = history["company_history_year"]
                his.company_history_content = history["company_history_content"]
                his.startup = startup

                his.save()
    except Exception as e:
        print(e)
        pass

    startup.save()
    vue_get_follow_startup(rjd["startup_id"])
    return JsonResponse(
        {"result":"ok"}
    )

@csrf_exempt
@my_timer
def vue_update_startup_head_detail(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    startup = Startup.objects.get(id=rjd["startup_id"])
    startup.company_name = rjd["company_name"]
    startup.company_short_desc = rjd["company_short_desc"]

    if request.FILES.get("back_img"):
        startup.back_img =handle_uploaded_file_business_back(request.FILES['back_img'], str(request.FILES['back_img']),
                                                                rjd["startup_id"])
    if request.FILES.get("logo"):
        startup.logo = handle_uploaded_file_service_logo(request.FILES['logo'], str(request.FILES['logo']),
                                                     rjd["startup_id"])
    startup.save()
    return JsonResponse(
        {"result":"ok"}
    )

#-----[2/2]----
#--- (중복) 스타트업 정보 저장 >> 기업 소개 페이지를 제외한 모든 페이지의 정보 저장
#
@csrf_exempt
@my_timer
def vue_update_startup_news_detail(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    print(request.POST)
    rjd = json.loads(request.POST.get("json_data"))
    #file_path = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']), rjd["startup_id"]  )
    startup = Startup.objects.get(id=rjd["startup_id"])


    for act in rjd["news"]:
        print(act)
        if act.get("id"):
            activity = Activity.objects.get(id=act.get("id"))
        else:
            activity = Activity()
        activity.company_activity_text = act["company_activity_text"]
        activity.company_activity_youtube = act["company_activity_youtube"]
        activity.startup = startup
        try:
            if act["company_activity_img"] == request.FILES.get("file_news").name:
                path_news_img = handle_uploaded_file_business_file(request.FILES['file_news'], str(request.FILES['file_news']), startup.id)
                activity.company_activity_img = path_news_img
        except:
            pass
        activity.save()
        activity_id = activity.id
        try:
            for rep in act["rep"]:
                print(rep)
                if rep.get("id"):
                    reply = Reply.objects.get(id=rep.get("id"))
                else:
                    reply = Reply()
                    reply.company_activity_author = Startup.objects.get(user=AdditionalUserInfo.objects.get(id=user_auth_id).user)

                reply.company_activity_text = rep["company_activity_text"]
                reply.activity_id = activity_id
                reply.save()
        except Exception as e:
            print(e)
            pass
    vue_get_follow_startup(rjd["startup_id"])
    return JsonResponse({"result":"ok","email":AdditionalUserInfo.objects.get(id=user_auth_id).user.username})

@csrf_exempt
@my_timer
def vue_update_startup_detail(request):

    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    print(request.POST)
    rjd = json.loads(request.POST.get("json_data"))
    #file_path = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']), rjd["startup_id"]  )
    startup = Startup.objects.get(id=rjd["startup_id"])

    startup.company_intro =  rjd["company_intro"]
    startup.company_website = rjd["information"]["company_website"]
    startup.company_kind = rjd["company_kind"]
    startup.ip_chk = rjd["ip_chk"]
    print(rjd["ip_chk"])
    print(startup.ip_chk)
    startup.revenue_chk = rjd["revenue_chk"]
    startup.export_chk = rjd["export_chk"]
    startup.company_invest_chk = rjd["company_invest_chk"]

    startup.revenue_before_0 = rjd["revenue_before_0"]
    startup.revenue_before_1 = rjd["revenue_before_1"]
    startup.revenue_before_2 = rjd["revenue_before_2"]
    startup.revenue_before_year_0 = rjd["revenue_before_year_0"]
    startup.revenue_before_year_1 = rjd["revenue_before_year_1"]
    startup.revenue_before_year_2 = rjd["revenue_before_year_2"]

    startup.export_before_0 = rjd["export_before_0"]
    startup.export_before_1 = rjd["export_before_1"]
    startup.export_before_2 = rjd["export_before_2"]

    startup.export_before_nation_0 = rjd["export_before_nation_0"]
    startup.export_before_nation_1 = rjd["export_before_nation_1"]
    startup.export_before_nation_2 = rjd["export_before_nation_2"]

    startup.export_before_year_0 =  rjd["export_before_year_0"]
    startup.export_before_year_1 =  rjd["export_before_year_1"]
    startup.export_before_year_2 =  rjd["export_before_year_2"]

    try:
        startup.attached_cert_file = handle_uploaded_file_business_file(request.FILES['attached_cert_file'], str(request.FILES['attached_cert_file']),rjd["startup_id"])
        print(startup.attached_cert_file)
    except Exception as e:
        print(e)
        pass
    try:
        print("ipfile")

        startup.attached_ip_file =  handle_uploaded_file_business_file(request.FILES['attached_ip_file'], str(request.FILES['attached_ip_file']),rjd["startup_id"])
        print(startup.attached_ip_file)
    except Exception as e:
        print(e)
        pass

    try:
        for t in startup.selected_company_filter_list.all():
            if t.cat_0 == "지원형태":
                startup.selected_company_filter_list.remove(t)
        for t in rjd["support_business_tag"]:
            startup.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))
    except Exception as e:
        print(e)
        pass
    try:
        startup.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=rjd["company_kind"]))
    except:
        print("")
    startup.address_0 = rjd["address_0"]
    startup.repre_email = rjd["information"]["repre_email"]

    try:
        if request.FILES.get("ip__0"):
            path = handle_uploaded_file_business_file(request.FILES['ip__0'], str(request.FILES['ip__0']), rjd["startup_id"])
            startup.attached_ir_file = path
        startup.save()
    except:
        print("예외 발생")
        pass

    CompanyInvest.objects.filter(startup=startup).delete()

    for invest in rjd["invest"]:
        try:
            date = invest["company_invest_year"].split("T")[0]
            CompanyInvest(
                startup=startup,
                company_invest_year = date,
                company_invest_size=invest["company_invest_size"],
                company_invest_agency=invest["company_invest_agency"],
            ).save()
        except:
            pass

    for service in rjd["service"]:
        print(service)

        if service.get("id"):
            ser = Service.objects.get(id = service["id"])
            ser.service_intro = service["service_intro"]
            ser.service_name = service["service_name"]
            try:
                print(service["service_img"].strip())
                print(request.FILES)
                for key in request.FILES.keys():
                    print("업로드 파일 이름:",end="")
                    print(request.FILES[key].name)

                    if service["service_img"].strip()  == request.FILES[key].name :
                        path = handle_uploaded_file_service_product(request.FILES[key], str(request.FILES[key]),
                                                                    rjd["startup_id"])
                        ser.service_img = path
            except Exception as e:
                print(e)
            try:
                for key in request.FILES.keys():
                    if service["file_name"].strip()  == request.FILES[key].name :
                        path = handle_uploaded_file_service_product(request.FILES[key], str(request.FILES[key]),
                                                                    rjd["startup_id"])
                        ser.service_file = path
            except Exception as e:
                print(e)
            ser.save()

        else :
            ser = Service()
            try:
                ser.service_intro = service["service_intro"]
            except:
                pass
            try:
                ser.service_name = service["service_name"]
            except:
                pass
            try:
                for key in request.FILES.keys():
                    if service["file_name"].strip() == request.FILES[key].name:
                        path = handle_uploaded_file_service_product(request.FILES[key], str(request.FILES[key]),
                                                                    rjd["startup_id"])
                        ser.service_file = path
            except Exception as e:
                print(e)
            try:
                for key in request.FILES.keys():
                    if service["service_img"].strip() == request.FILES[key].name:
                        path = handle_uploaded_file_service_product(request.FILES[key], str(request.FILES[key]),
                                                                    rjd["startup_id"])
                        ser.service_img = path
            except Exception as e:
                print(e)

            ser.startup = startup
            ser.save()


    startup.save()

    vue_get_follow_startup(rjd["startup_id"])


    return JsonResponse({
        "attached_cert_file":startup.attached_cert_file,
        "attached_ip_file": startup.attached_ip_file
    },safe=False)






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



# --------------------------------------------- 중복 정리 시작 ----------------------------------------------------------

# --------------------------------------------- 중복 정리 완료 ----------------------------------------------------------





#------ (스타트업 정보 저장 완료!)--------------------------------------------------------------------------------------












import urllib.parse
#------------- (스타트업) (전체) 지원사업의 카드뷰----------------------------------------------------------------------
#-------------(스타트업) 열람할 지원사업/공고문 카드뷰를 볼 때 : 지원사업 홈
@csrf_exempt
@my_timer
def vue_home_support_business(request):
    check_result = gca_check_session(request)
    if check_result != False:
        user_auth_id =  check_result
    tag_list = urllib.parse.unquote(request.POST.get('q')).split(",")
    result={}
    print(tag_list)
    result["data"]=[]
    data=[]
    support_business_set = SupportBusiness.objects.filter(support_business_status=3)#.filter(support_business_apply_end_ymdt__gte=timezone.now())#.exclude(support_business_status=None).exclude(Q(support_business_status=1)|(Q(support_business_status=2)|(Q(support_business_status=6))))
    for filter in tag_list:
        if filter != "" and filter != None:
            if "명 이하" in filter or "명 이상" in filter:
                num = int(re.findall('\d+', filter)[0])
                if num != 0:
                    support_business_set = support_business_set.filter(support_business_employee_condition__lte=num)
                else:
                    pass
            elif filter!="구성원 제한없음":
                support_business_set = support_business_set.filter(selected_support_business_filter_list__filter_name = filter)
    for support_business in support_business_set:
        obj = {}
        obj["tag"] = []
        obj["support_business_name"] = support_business.support_business_name
        obj["id"] = support_business.id
        obj["support_business_poster"] = support_business.support_business_poster
        try:
            obj["is_favored"] = is_in_favor_list("support_business", support_business.id , user_auth_id)
        except:
            obj["is_favored"] = False
        obj["support_business_apply_end_ymdt"] = (support_business.support_business_apply_end_ymdt)
        obj["support_business_short_desc"] = support_business.support_business_short_desc
        obj["favorite"] =  (support_business.additionaluserinfo_set.all()).count()
        obj["comp"]=""


        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            number =  str(round((
                Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                support_business.support_business_recruit_size), 1))
            if number == "0.0":
                number ="0"
            obj["comp"] = number + " : 1"

        else:
            obj["comp"] = ""

        obj["selected_support_business_filter_list"]=[]
        print(obj["selected_support_business_filter_list"])
        for s in support_business.selected_support_business_filter_list.all():
            obj["selected_support_business_filter_list"].append(s.filter_name)
        obj["rec"]=0

        for f in support_business.selected_support_business_filter_list.all():
            obj["tag"].append(f.filter_name)
            if f.filter_name in tag_list:
                obj["rec"]= obj["rec"]+1


        # if random.randrange(0,10)%2==0:
        #     obj["img"] = img_list[random.randrange(0,9)]

        result["data"].append(copy.deepcopy(obj))
    try:
        if gca_check_session(request) != False:
            user_id = gca_check_session(request)
            user_startup = Startup.objects.get(user = AdditionalUserInfo.objects.get(id=user_id).user)
            result["usr_filter"] = []
            for f in user_startup.selected_company_filter_list.all():
                result["usr_filter"].append(f.filter_name)
            print(result['usr_filter'])
    except:
        pass
    return JsonResponse(result)


@csrf_exempt
@my_timer
def vue_home_support_business_new(request):
    check_result = gca_check_session(request)
    if check_result != False:
        user_auth_id =  check_result
    tag_list = urllib.parse.unquote(request.POST.get('q')).split(",")
    result={}
    result["data"]=[]
    data=[]
    support_business_set = SupportBusiness.objects.filter(support_business_status=3)#.filter(support_business_apply_end_ymdt__gte=timezone.now())#.exclude(support_business_status=None).exclude(Q(support_business_status=1)|(Q(support_business_status=2)|(Q(support_business_status=6))))
    for filter in tag_list:
        if filter != "" and filter != None:
            if "명 이하" in filter or "명 이상" in filter:
                num = int(re.findall('\d+', filter)[0])
                if num != 0:
                    support_business_set = support_business_set.filter(support_business_employee_condition__lte=num)
                else:
                    pass
            elif filter!="구성원 제한없음":
                support_business_set = support_business_set.filter(support_business_raw_filter_text__contains=filter)
    for support_business in support_business_set:
        obj = {}
        obj["tag"] = []
        obj["support_business_name"] = support_business.support_business_name
        obj["id"] = support_business.id
        obj["support_business_poster"] = support_business.support_business_poster
        try:
            obj["is_favored"] = is_in_favor_list("support_business", support_business.id , user_auth_id)
        except:
            obj["is_favored"] = False
        obj["support_business_apply_end_ymdt"] = (support_business.support_business_apply_end_ymdt)
        obj["support_business_short_desc"] = support_business.support_business_short_desc
        obj["favorite"] =  (support_business.additionaluserinfo_set.all()).count()
        obj["comp"]=""


        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            number =  str(round((
                Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                support_business.support_business_recruit_size), 1))
            if number == "0.0":
                number ="0"
            obj["comp"] = number + " : 1"

        else:
            obj["comp"] = ""

        obj["selected_support_business_filter_list"]=[]
        print(obj["selected_support_business_filter_list"])
        for s in support_business.selected_support_business_filter_list.all():
            obj["selected_support_business_filter_list"].append(s.filter_name)
        obj["rec"]=0

        for f in support_business.selected_support_business_filter_list.all():
            obj["tag"].append(f.filter_name)
            if f.filter_name in tag_list:
                obj["rec"]= obj["rec"]+1


        # if random.randrange(0,10)%2==0:
        #     obj["img"] = img_list[random.randrange(0,9)]

        result["data"].append(copy.deepcopy(obj))
    try:
        if gca_check_session(request) != False:
            user_id = gca_check_session(request)
            user_startup = Startup.objects.get(user = AdditionalUserInfo.objects.get(id=user_id).user)
            result["usr_filter"] = []
            for f in user_startup.selected_company_filter_list.all():
                result["usr_filter"].append(f.filter_name)
            print(result['usr_filter'])
    except:
        pass
    return JsonResponse(result)




@csrf_exempt
@my_timer
def similar_filter_support_business(request):

    check_result = gca_check_session(request)
    user_auth_id=""
    if check_result != False:
        user_auth_id =  check_result

    filter_string_list = request.GET.get("q").split(",")
    filter_list = []
    result={}
    result["data"]=[]
    for f in filter_string_list:
        try:
            filter_list.append(SupportBusinessFilter.objects.get(filter_name=f))
        except:
            pass
    support_business_list = SupportBusiness.objects.filter(selected_support_business_filter_list__in=filter_list)\
        .exclude(support_business_status__in=[1,2,4,5,6,"1","2","4","5","6"]).filter(support_business_apply_end_ymdt__gte= timezone.now()).values("id").order_by("support_business_apply_end_ymdt")
    sb_list=[]

    for su in support_business_list:
        supportbusiness = SupportBusiness.objects.get(id=su["id"])
        if supportbusiness not in sb_list:
            sb_list.append(supportbusiness)

    for support_business in sb_list:
        obj = {}
        obj["tag"] = []
        obj["support_business_name"] = support_business.support_business_name
        obj["support_business_apply_end_ymdt"] = (support_business.support_business_apply_end_ymdt)
        obj["support_business_apply_start_ymd"] = (support_business.support_business_apply_start_ymd)
        obj["support_business_short_desc"] = support_business.support_business_short_desc
        obj["support_business_poster"] = support_business.support_business_poster
        obj["is_favored"] = is_in_favor_list("support_business", support_business.id, user_auth_id)
        obj["id"] = support_business.id
        obj["sim"] = 0
        obj["selected_support_business_filter_list"] = []
        for f in support_business.selected_support_business_filter_list.all():
            obj["selected_support_business_filter_list"].append(f.filter_name)
            if f in filter_list:
                obj["sim"] = obj["sim"] + 1
        result["data"].append(copy.deepcopy(obj))
    return JsonResponse({"result":(result)},safe=False)





#-------------(스타트업) '이런 지원사업은 어떠세요?' 항목에 열람할 카드뷰를 볼 때 : 지원사업 상세페이지 하단
@csrf_exempt
@my_timer
def similar_support_business(request):
    result={}
    result["data"]=[]
    print(request.GET.get('q'))

    origin_support_business = SupportBusiness.objects.get(id=request.GET.get('q'))

    for support_business in SupportBusiness.objects.filter(support_business_status=3).filter(support_business_apply_end_ymdt__gte=datetime.now()).exclude(id=request.GET.get('q')):
        obj = {}
        obj["tag"] = []
        obj["support_business_name"] = support_business.support_business_name
        obj["support_business_apply_end_ymdt"] = (support_business.support_business_apply_end_ymdt)
        obj["support_business_apply_start_ymd"] = (support_business.support_business_apply_start_ymd)
        obj["support_business_short_desc"] = support_business.support_business_short_desc
        obj["support_business_poster"] = support_business.support_business_poster
        obj["comp"]=""
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            number =  str(round((
                Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                support_business.support_business_recruit_size), 1))
            if number =="0.0":
                number ="0"
            obj["comp"] = number + " : 1"

        else:
            obj["comp"] = ""

        obj["favorite"] = str((AdditionalUserInfo.objects.filter(favorite=support_business)).count())
        obj["is_favored"] = is_in_favor_list("support_business", support_business.id, request.GET.get("gca_id"))
        obj["id"] = support_business.id
        obj["sim"]=0
        obj["selected_support_business_filter_list"]=[]
        for f in support_business.selected_support_business_filter_list.all():
            obj["selected_support_business_filter_list"].append(f.filter_name)
            if f in origin_support_business.selected_support_business_filter_list.all():
                obj["sim"]= obj["sim"]+1

        # if random.randrange(0,10)%2==0:
        #     obj["img"] = img_list[random.randrange(0,9)]
        result["data"].append(copy.deepcopy(obj))
        sorted(result["data"], key=lambda c:c["sim"])
    return JsonResponse(result)


# --------[공고문 상세 정보 페이지]-----------------------------------------------------------------------------

@csrf_exempt
@my_timer
def get_support_business_detail(request):
    user_auth_id=""
    check_result = gca_check_session(request)
    if check_result != False:
        user_auth_id =  check_result
    id = request.GET.get("id")
    support_business = SupportBusiness.objects.get(id=id)
    result = {}
    result["support_business_name"] = support_business.support_business_name
    result["mng_name"] = support_business.support_business_author.mng_name
    result["mng_email"] = support_business.support_business_author.user.username
    result["mng_tel"] = support_business.support_business_author.mng_tel
    result["mng_id"] = support_business.support_business_author.id
    result["support_business_id"] = support_business.id
    result["is_favored"] = is_in_favor_list("support_business", support_business.id , user_auth_id)

    result["kikwan"] = support_business.support_business_author.mng_kikwan

    result["support_business_name_sub"] = support_business.support_business_name_sub

    result["support_business_subject"] = support_business.support_business_subject
    result["support_business_detail"] = support_business.support_business_detail
    result["support_business_poster"] = support_business.support_business_poster
    try:
        with open(support_business.support_business_poster, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        result["support_business_poster_data_url"] = str(encoded_string)
    except Exception as e:
        print(e)
    result["support_business_status"] = support_business.support_business_status


    result["support_business_short_desc"] = support_business.support_business_short_desc
    result["support_business_name_tag"] = support_business.support_business_name_tag
    result["base_tag"] = []
    result["special_tag"] = []
    result["tag"] = []
    for t in support_business.selected_support_business_filter_list.all():
        result["tag"].append(t.filter_name)
        if t.cat_0 == "기본장르":
            result["base_tag"].append(t.filter_name)
        if t.cat_0 == "영역":
            result["special_tag"].append(t.filter_name)
    if support_business.support_business_employee_condition != None:
        result["tag"].append( str(support_business.support_business_employee_condition) +"명 이하")

    result["support_business_supply_content"] = support_business.support_business_supply_content
    result["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
    result["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
    result["support_business_object"] = support_business.support_business_object
    result["support_business_recruit_size"] = support_business.support_business_recruit_size
    result["support_business_prefer"] = support_business.support_business_prefer
    result["support_business_constraint"] = support_business.support_business_constraint
    result["support_business_prefer_chk"] = support_business.support_business_prefer_chk
    result["support_business_constraint_chk"] = support_business.support_business_constraint_chk
    result["support_business_pro_0_choose"] = support_business.support_business_pro_0_choose
    result["support_business_pro_0_start_ymd"] = support_business.support_business_pro_0_start_ymd
    result["support_business_pro_0_end_ymd"] = support_business.support_business_pro_0_end_ymd
    result["support_business_pro_0_open_ymd"] = support_business.support_business_pro_0_open_ymd
    result["support_business_pro_0_criterion"] = support_business.support_business_pro_0_criterion




    result["favorite"] = (support_business.additionaluserinfo_set.all()).count()
    result["comp"]=""
    if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
        try:
            number =  str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
            if(number =="0.0" ):
                number = "0"
            result["comp"] =  number + " : 1"
        except:
            result["comp"] = ""
    else:
        result["comp"] = ""

    result["support_business_etc_file_title_mng"] = support_business.support_business_etc_file_title_mng
    result["support_business_pro_1_choose"] = support_business.support_business_pro_1_choose
    result["support_business_pro_1_start_ymd"] = support_business.support_business_pro_1_start_ymd
    result["support_business_pro_1_end_ymd"] = support_business.support_business_pro_1_end_ymd
    result["support_business_pro_1_open_ymd"] = support_business.support_business_pro_1_open_ymd
    result["support_business_pro_1_criterion"] = support_business.support_business_pro_1_criterion
    result["support_business_pro_1_check"] = support_business.support_business_pro_1_check

    result["support_business_pro_2_choose"] = support_business.support_business_pro_2_choose
    result["support_business_pro_2_start_ymd"] = support_business.support_business_pro_2_start_ymd
    result["support_business_pro_2_end_ymd"] = support_business.support_business_pro_2_end_ymd
    result["support_business_pro_2_open_ymd"] = support_business.support_business_pro_2_open_ymd
    result["support_business_pro_2_criterion"] = support_business.support_business_pro_2_criterion
    result["support_business_pro_2_check"] = support_business.support_business_pro_2_check

    result["support_business_ceremony_start_ymd"] = support_business.support_business_ceremony_start_ymd
    result["support_business_ceremony_end_ymd"] = support_business.support_business_ceremony_end_ymd

    result["support_business_meta"] = support_business.support_business_meta
    result["support_business_faq"] = support_business.support_business_faq
    result["support_business_additional_faq"] = support_business.support_business_additional_faq
    result["support_business_meta"] = support_business.support_business_meta
    result["support_business_meta_0"] = support_business.support_business_meta_0
    result["mng_support_business_step_6_etc_input_chk"]  = support_business.mng_support_business_step_6_etc_input_chk
    result["support_business_ceremony_chk" ] = support_business.support_business_ceremony_chk
    result["support_business_faq_chk" ] = support_business.support_business_faq_chk
    result["support_business_additional_faq_chk" ] = support_business.support_business_additional_faq_chk
    result["support_business_meta"] = support_business.support_business_meta

    result["mng_support_business_step_3_etc_input_mojipjogun"] = support_business.mng_support_business_step_3_etc_input_mojipjogun
    result["mng_support_business_step_3_etc_input_mojipgenre"] = support_business.mng_support_business_step_3_etc_input_mojipgenre
    result["mng_support_business_step_3_etc_input_mojipjogun_chk"] = support_business.mng_support_business_step_3_etc_input_mojipjogun_chk
    result["mng_support_business_step_3_etc_input_mojipgenre_chk"] = support_business.mng_support_business_step_3_etc_input_mojipgenre_chk

    result["mng_support_business_step_6_etc_input"] = support_business.mng_support_business_step_6_etc_input
    result["support_business_etc_file_title_mng"] = support_business.support_business_etc_file_title_mng
    result["support_business_appliance_form"] = support_business.support_business_appliance_form

    result["object_tag"]=[]
    result["top_support_tag"]=[]
    result["files"]=[]
    for file in support_business.supportbusinessattachedfiles_set.all():
        result["files"].append({"name":file.file_path.split("/")[-1], "path": file.file_path, "id":file.id})

    try:

        if support_business.support_business_status == "4":  # 작성중인 공고문
            result["status"] = "모집종료"
        if support_business.support_business_status == "1":  # 작성중인 공고문
            result["status"] = "작성중"
        if support_business.support_business_status == "2":  # 승인대기중인 공고문
            result["status"] = "승인대기"
        if support_business.support_business_status == "3":
            result["status"] = "공고중"
        if support_business.support_business_apply_end_ymdt < timezone.now() and support_business.support_business_status == "3":  # 모집 종료 된 공고문
            result["status"] = "모집종료"
        if support_business.support_business_status == "5":  # 공고 종료 된 공고문
            result["status"] = "공고종료"
        if support_business.support_business_status == "6":  # 블라인드 공고문
            result["status"] = "블라인드"


    except:
        result["status"] = "작성중"


    result["selected_support_business_filter_list"] = []
    for t in support_business.selected_support_business_filter_list.all():
        result["selected_support_business_filter_list"].append(t.filter_name)

    result["local_tag"] = []
    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_1 == "소재지":
            result["local_tag"].append(t.filter_name)

    result["kind_tag"] = []
    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_1 == "기업형태":
            result["kind_tag"].append(t.filter_name)

    result["year_tag"] = []
    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_1 == "업력":
            result["year_tag"].append(t.filter_name)

    result["step_tag"] = []
    for t in support_business.selected_support_business_filter_list.all():
        if t.cat_1 == "기업단계":
            result["step_tag"].append(t.filter_name)


    for t in  support_business.selected_support_business_filter_list.all():
        if t.cat_0 == "지원형태":
            result["top_support_tag"].append(t.filter_name)
        else:
            result["object_tag"].append(t.filter_name)

    result["genre_filter"]=[]
    for t in  SupportBusinessFilter.objects.all():
        if t.cat_0 == "기본장르":
            result["genre_filter"].append(t.filter_name)

    result["conditions_location_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "소재지":
            result["conditions_location_filter"].append(t.filter_name)

    result["area_creation_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "창작":
            result["area_creation_filter"].append(t.filter_name)

    result["area_it_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "IT 관련":
            result["area_it_filter"].append(t.filter_name)
    result["area_manufacture_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "제조/융합 관련":
            result["area_manufacture_filter"].append(t.filter_name)
    result["area_founded_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "창업":
            result["area_founded_filter"].append(t.filter_name)

    
    result["area_newbusiness_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "신규사업":
            result["area_newbusiness_filter"].append(t.filter_name)

    result["area_etc_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기타" and t.cat_0=="영역":
            result["area_etc_filter"].append(t.filter_name)


    result["conditions_comtype_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기업형태":
            result["conditions_comtype_filter"].append(t.filter_name)
    result["conditions_record_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "업력":
            result["conditions_record_filter"].append(t.filter_name)
    result["conditions_stage_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기업단계":
            result["conditions_stage_filter"].append(t.filter_name)
    result["type_cash_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "자금지원":
            result["type_cash_filter"].append(t.filter_name)
    result["type_invest_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "엑셀러레이팅 투자연계":
            result["type_invest_filter"].append(t.filter_name)
    result["type_edu_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "교육":
            result["type_edu_filter"].append(t.filter_name)
    result["type_market_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "판로":
            result["type_market_filter"].append(t.filter_name)
    result["type_network_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "네트워킹":
            result["type_network_filter"].append(t.filter_name)
    result["type_etc_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기타지원":
            result["type_etc_filter"].append(t.filter_name)
    result["type_space_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "공간지원":
            result["type_space_filter"].append(t.filter_name)
    result["type_pitching_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "피칭":
            result["type_pitching_filter"].append(t.filter_name)

    return JsonResponse(result, safe=False)


@csrf_exempt
@my_timer
def vue_get_filter(request):
    result={}

    result["genre_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_0 == "기본장르":
            result["genre_filter"].append(t.filter_name)

    result["conditions_location_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "소재지":
            result["conditions_location_filter"].append(t.filter_name)

    result["area_creation_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "창작":
            result["area_creation_filter"].append(t.filter_name)

    result["area_it_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "IT 관련":
            result["area_it_filter"].append(t.filter_name)
    result["area_manufacture_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "제조/융합 관련":
            result["area_manufacture_filter"].append(t.filter_name)
    result["area_founded_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "창업":
            result["area_founded_filter"].append(t.filter_name)

    result["area_newbusiness_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "신규사업":
            result["area_newbusiness_filter"].append(t.filter_name)

    result["area_etc_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기타" and t.cat_0 == "영역":
            result["area_etc_filter"].append(t.filter_name)

    result["conditions_comtype_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기업형태":
            result["conditions_comtype_filter"].append(t.filter_name)
    result["conditions_record_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "업력":
            result["conditions_record_filter"].append(t.filter_name)
    result["conditions_stage_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기업단계":
            result["conditions_stage_filter"].append(t.filter_name)
    result["type_cash_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "자금지원":
            result["type_cash_filter"].append(t.filter_name)
    result["type_invest_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "엑셀러레이팅 투자연계":
            result["type_invest_filter"].append(t.filter_name)
    result["type_edu_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "교육":
            result["type_edu_filter"].append(t.filter_name)
    result["type_market_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "판로":
            result["type_market_filter"].append(t.filter_name)
    result["type_network_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "네트워킹":
            result["type_network_filter"].append(t.filter_name)
    result["type_etc_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "기타지원":
            result["type_etc_filter"].append(t.filter_name)
    result["type_space_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "공간지원":
            result["type_space_filter"].append(t.filter_name)
    result["type_pitching_filter"] = []
    for t in SupportBusinessFilter.objects.all():
        if t.cat_1 == "피칭":
            result["type_pitching_filter"].append(t.filter_name)
    return JsonResponse(result, safe=False)


#------ (스타트업) 내기업관리 페이지
# --------[서비스/프로덕트 삭제,  ]-------
@csrf_exempt
@my_timer
def vue_remove_service_product(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    startup = Startup.objects.get(user_id = AdditionalUserInfo.objects.get(id=request.POST.get("id")).user.id)
    Service.objects.filter(startup=startup).filter(id=request.POST.get("service_id")).delete()
    return  JsonResponse({"result":"ok"})
from django.core.serializers import serialize
from django.forms.models import model_to_dict


# ------[ 중복 그룹 4]----def 2개 중복-----------------------------------------------------------------------------------
#-----[1/2]----
# --------[뉴스 삭제 하기]-------
@csrf_exempt
@my_timer
def vue_del_startup_news(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    Activity.objects.get(id=rjd["id"]).delete()
    return JsonResponse({"result":"ok"})




# ------------ (스타트업) 지원서 작성 페이지에 들어갔을 때 '지원사업 제목'만 가져오는 함수 : 스타트업 지원하기
@csrf_exempt
@my_timer
def vue_get_support_business_name(request):
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business"))
    temp = {}
    temp["support_business_name"] = support_business.support_business_name
    temp["support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
    temp["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
    temp["support_business_pro_0_open_ymd"] = support_business.support_business_pro_0_open_ymd

    try:
        if support_business.support_business_status == "4":  # 작성중인 공고문
            temp["status"] = "모집종료"
        if support_business.support_business_status == "1":  # 작성중인 공고문
            temp["status"] = "작성중"
        if support_business.support_business_status == "2":  # 승인대기중인 공고문
            temp["status"] = "승인대기"
        if support_business.support_business_status == "3":
            temp["status"] = "공고중"
        if support_business.support_business_apply_end_ymdt < timezone.now() and support_business.support_business_status == "3":  # 모집 종료 된 공고문
            temp["status"] = "모집종료"
        if support_business.support_business_status == "5":  # 공고 종료 된 공고문
            temp["status"] = "공고종료"
        if support_business.support_business_status == "6":  # 블라인드 공고문
            temp["status"] = "블라인드"
    except Exception as e:
        temp["status"] = "작성중"
    temp["comp"]=""

    if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
        number = str(round((
                Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                support_business.support_business_recruit_size), 1))
        if number == "0.0":
            number ="0"
        temp["comp"] = number + " : 1"

    else:
        temp["comp"] = ""
    return JsonResponse(temp, safe=False)





#---- 지원사업 지원시 정보 불러오기는 다음 프로세스에 있음

# --------- 좋아요---------------------------------------------------------------------------------------------------
#------------(스타트업) 유저가 '지원사업' 하트를 눌렀을 때, 관심지원사업 리스트에 토글 : 관심지원사업 리스트

# --------[관심사업  토글 ]-------



# ------------(스타트업) 유저가 '지원사업' 하트를 눌렀을 때, 관심 지원 사업 리스트에 토글 : 관심 기업 리스트
# --------[관심 기업 토글 ]-------




@csrf_exempt
@my_timer
def toggle_from_favorite_log(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    user_id = user_auth_id
    user  = AdditionalUserInfo.objects.get(id=user_id)
    result=""
    if request.GET.get("target")=="support_business":
        support_business = SupportBusiness.objects.get(id=request.GET.get(id))
        if (FavoriteLog.objects.filter(support_business=support_business).filter(user=user)).count()>0:
            FavoriteLog.objects.filter(support_business=support_business).filter(user=user).delete()
            result="remove"
        else:
            fav_log = FavoriteLog()
            fav_log.support_business = support_business
            fav_log.user = user
            fav_log.save()
            result="save"
    if request.GET.get("target") == "startup":
        startup = Startup.objects.get(id=request.GET.get(id))
        if (FavoriteLog.objects.filter(startup=startup).filter(user=user)).count() > 0:
            FavoriteLog.objects.filter(startup=startup).filter(user=user).delete()
            result="remove"
        else:
            fav_log = FavoriteLog()
            fav_log.startup = startup
            fav_log.user = user
            fav_log.save()
            result ="save"
    if request.GET.get("target") == "clip":
        clip = Clip.objects.get(id=request.GET.get(id))
        if (FavoriteLog.objects.filter(clip=clip).filter(user=user)).count() > 0:
            FavoriteLog.objects.filter(clip=clip).filter(user=user).delete()
            result="remove"
        else:
            fav_log = FavoriteLog()
            fav_log.clip = clip
            fav_log.user = user
            fav_log.save()
            result="save"
    if request.GET.get("target") == "course":
        course = Course.objects.get(id=request.GET.get(id))
        if (FavoriteLog.objects.filter(course=course).filter(user=user)).count() > 0:
            FavoriteLog.objects.filter(course=course).filter(user=user).delete()
            result="remove"
        else:
            fav_log = FavoriteLog()
            fav_log.course = course
            fav_log.user = user
            fav_log.save()
            result="save"
    if request.GET.get("target") == "path":
        path = Path.objects.get(id=request.GET.get(id))
        if (FavoriteLog.objects.filter(path=path).filter(user=user)).count() > 0:
            FavoriteLog.objects.filter(path=path).filter(user=user).delete()
            result="delete"
        else:
            fav_log = FavoriteLog()
            fav_log.path = path
            fav_log.user = user
            fav_log.save()
            result="remove"
    return  JsonResponse({"result":result})

@csrf_exempt
@my_timer
def get_usr_favored_data(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    ad = AdditionalUserInfo.objects.get(id=user_auth_id)
    # 해당 유저의 관심 지원사업
    fav_support_business = FavoriteLog.objects.filter(user=ad).exclude(support_business=None)
    favorite_support_business=[]
    for fav in fav_support_business:
        favorite_support_business.append(fav.support_business_id)
    # 해당 유저의 관심 스타트업
    fav_startup = FavoriteLog.objects.filter(user=ad).exclude(startup=None)
    favorite_startup = []
    for fav in fav_startup:
        favorite_startup.append(fav.startup_id)
    #해당 유저의 관심 강좌
    fav_clip = FavoriteLog.objects.filter(user=ad).exclude(clip=None)
    favorite_clip = []
    for fav in fav_clip:
        favorite_clip.append(fav.clip_id)
    #해당 유저의 관심 코스
    fav_course = FavoriteLog.objects.filter(user=ad).exclude(course=None)
    favorite_course = []
    for fav in fav_course:
        favorite_course.append(fav.course_id)
    #해당 유저의 관심 패스
    fav_path = FavoriteLog.objects.filter(user=ad).exclude(path=None)
    favorite_path = []
    for fav in fav_path:
        favorite_path.append(fav.path_id)
    result={}
    result["favorite_support_business"] = copy.deepcopy(favorite_support_business)
    result["favorite_startup"] = copy.deepcopy(favorite_startup)
    result["favorite_clip"] = copy.deepcopy(favorite_clip)
    result["favorite_course"] = copy.deepcopy(favorite_course)
    result["favorite_path"] = copy.deepcopy(favorite_path)
    return JsonResponse(result)




# ------------(스타트업) 유저가 본인이 하트 누른'관심 기업'을 관심 기업 리스트에 데이터 가져오기 : 관심 기업 리스트
# --------[관심 기업 리스트 가져오기]-------
@csrf_exempt
@my_timer
def vue_my_favorite_set(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = request.POST.get("id")
    return JsonResponse(list(AdditionalUserInfo.objects.get(id= user_auth_id).favorite_startup.all().values("id")), safe=False)





#-------------- (스타트업) '스타트업 소식'에 좋아요 눌렀을 때 동작

@csrf_exempt
@my_timer
def vue_set_activity_like(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    id = request.POST.get("id")
    target = request.POST.get("k")
    ta = ActivityLike.objects.get_or_create(company_activity_user=AdditionalUserInfo.objects.get(id=id), activity=Activity.objects.get(id=target))
    return JsonResponse({"result":"ok"})








#----------------------------------------------------------------------------------------------------------------------
# 아. 스타트업 유저가 공고중인 지원사업에 지원시 원소스 파일에서 (프로필_마이페이지+스타트업 상세페이지 + 비공개 정보) 따와진 정보가 채워지기
#    // 지원서 db 와는 별개임
#       <목표>
#       기본적으로 '기업페이지 관리'에 있는 내용중 해당되는 내용이 있으면 불러와진다.
#       "마이페이지>기업소개텝>기업정보 테이블 > 관련태그" 에서 불러와진다.
#       기업페이지의 필터에서 불러와진다.
#       변경시, 기업페이지 필터도 변경된다.
#       매출액, 수출액, 투자 유치내역 - 기업페이지의 매출액 인풋 창에서 불러와짐
#       첨부서류 : 지적 재산권의 경우, 추가하기 버튼을 통해 입력창을 추가하거나, 우측x 표시로 삭제가능
#----------------------------------------------------------------------------------------------------------------------









#//------------ (스타트업) 유저가 지원서 작성 시, 기업정보 불러오기 : 채워넣을 공간에 정보를 채워넣기_스타트업이 기업페이지관리에 등록한 정보
# --------[0 . 지원서 정보 등록 최초 지원서 db에 생성 기능 : 지원하기 클릭시 ]------------------------------------------
# # --------[맨처음 지원하기 눌렀을때, 최초 지원서 생성 기능]-----------------------------------------------------------
### !!!! todo 지원서 db에 생성하는 시점은 '지원하기' 버튼 클릭시 (현재는 첫번째 프로세스에서 두번째 프로세스 넘어갈때로 추정 > 아직 코드 못찾음
# @csrf_exempt
# def vue_set_application(request):
#     print(request.body)
#     rjd=json.loads(request.body.decode('utf-8'))
#     print(rjd)
#     print(",".join(rjd["meta"]))
#     id= rjd["id"]
#
#     support_business = SupportBusiness.objects.get(id=id)
#     support_business.meta = ",".join(rjd["meta"])
#     print(support_business.meta)
#     support_business.status=2
#     support_business.confirm_count = support_business.confirm_count+1;
#     support_business.save()
#     return JsonResponse({"result":"ok"})
#
# def handle_uploaded_file_poster(file, filename):
#     print('media/uploads/poster/')
#     if not os.path.exists('media/uploads/poster/'):
#         os.makedirs('media/uploads/poster')
#     with open('media/uploads/poster/' + filename, 'wb+') as destination:
#         for chunk in file.chunks():
#             destination.write(chunk)
#             return 'media/uploads/poster/'+filename




# --------[1 . 지원서 정보 등록 > 스타트업 정보 업데이트 ]--------------------------------------------------------------
# ------------(스타트업) 지원서에 첫번째 페이지 작성한 것을 기준으로 스타트업 정보를 업데이트
@csrf_exempt
@my_timer
def vue_update_startup_with_application_1(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)

    app = Appliance.objects.get(id=rjd["id"])
    app.company_name = rjd["company_name"]

    for k in app.selected_company_filter_list.all():
        if k.cat_1 =="기업형태":
            app.selected_company_filter_list.remove(k)
    for kind in SupportBusinessFilter.objects.all():
        if kind.cat_1 == "기업 형태" and rjd["company_kind"] == kind.filter_name :
            app.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=rjd["company_kind"]))
    app.company_kind = rjd["company_kind"]


    try:
        app.established_date = rjd["established_date"].split("T")[0]
        # startup.established_date =  rjd["established_date"].split("T")[0]
    except Exception as e:
        print(e)
        print("================================")
        pass
    # startup.address_0 = rjd["address_0"]
    # startup.address_1 = rjd["address_1"]
    # startup.repre_name = rjd["repre_name"]
    # startup.repre_tel = rjd["repre_tel"]
    # startup.repre_name = rjd["repre_name"]
    # startup.repre_tel = rjd["repre_tel"]
    # startup.repre_email = rjd["repre_email"]
    # startup.save()

    app.address_0 = rjd["address_0"]
    app.address_1 = rjd["address_1"]
    app.repre_name = rjd["repre_name"]
    app.repre_tel = rjd["repre_tel"]
    app.repre_email = rjd["repre_email"]
    app.mark_name = rjd["mark_name"]
    app.mark_tel = rjd["mark_tel"]
    app.mark_email = rjd["mark_email"]
    app.save()


    return JsonResponse({"result":"ok"})


# --------[2. 지원서 정보 등록 > 스타트업 정보 업데이트 ]-----------------------------------------------------------------------------
# ------------(스타트업) 지원서에 두번째 페이지 작성한 것을 기준으로 스타트업 정보를 업데이트
@csrf_exempt
@my_timer
def vue_update_startup_with_application_2(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    print(rjd)
    for r in app.selected_company_filter_list.all():
        if r.cat_0 == "기본장르" or r.cat_0 =="영역":
            app.selected_company_filter_list.remove(r)

    for t in rjd["base_filter"]:
        try:
            app.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))
        except Exception as e:
            print(e)
            pass
    for t in rjd["special_filter"]:
        try:
            app.selected_company_filter_list.add(SupportBusinessFilter.objects.get(filter_name=t))
        except Exception as e:
            print(e)
            pass

    app.company_keyword = rjd["company_keyword"]
    app.save()

    # for ap_service in app.applianceservice_set.all():
    #     ap_service.delete()
    for s in app.applianceservice_set.all():
        s.delete()

    for service in rjd["service"]:
        tr = ApplianceService()
        tr.service_name = service["service_name"]
        tr.service_intro = service["service_intro"]
        tr.startup = app.startup
        tr.appliance = app
        tr.save()
    print(app.applianceservice_set.all())

    return JsonResponse({"result":"ok"})




#(지금업무중)
# --------[3. 지원서 정보 등록 > 스타트업 정보 업데이트 ]-----------------------------------------------------------------------------
# ------------(스타트업) 지원서에 세번째 페이지 작성한 것을 기준으로 스타트업 정보를 업데이트
@csrf_exempt
@my_timer
def vue_update_startup_with_application_3(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    app.company_youtube = rjd["company_youtube"]
    app.company_instagram = rjd["company_instagram"]
    app.company_facebook = rjd["company_facebook"]
    app.company_website = rjd["company_website"]
    app.company_total_employee = rjd["company_total_employee"]
    app.company_hold_employee = rjd["company_hold_employee"]
    app.company_assurance_employee = rjd["company_assurance_employee"]
    app.revenue_before_0 = rjd["revenue_before_0"]
    app.revenue_before_1 = rjd["revenue_before_1"]
    app.revenue_before_2 = rjd["revenue_before_2"]

    app.export_before_0 = rjd["export_before_0"]
    app.export_before_1 = rjd["export_before_1"]
    app.export_before_2 = rjd["export_before_2"]
    app.export_before_nation_0 = rjd["export_before_nation_0"]
    app.export_before_nation_1 = rjd["export_before_nation_1"]
    app.export_before_nation_2 = rjd["export_before_nation_2"]

    ApplianceInvest.objects.filter(applicance=app).delete()
    for inv in rjd["invest"]:
        iv = ApplianceInvest()
        iv.applicance = app
        iv.company_invest_agency = inv["company_invest_agency"]
        iv.company_invest_size = inv["company_invest_size"]
        iv.company_invest_year = inv["company_invest_year"]
        iv.save()
    app.save()


    return JsonResponse({"result":"success"})



# --------[4. 지원서 정보 등록 > 스타트업 정보 업데이트 ]-----------------------------------------------------------------------------
# ------------(스타트업) 지원서에 네번째 페이지 작성한 것을 기준으로 스타트업 정보를 업데이트
@csrf_exempt
@my_timer
def vue_update_startup_with_application_4(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    print("=====")
    print(rjd["company_history"])
    print("=======")
    print(rjd["company_intro"])
    app = Appliance.objects.get(id=rjd["id"])
    app.company_intro = rjd["company_intro"]
    app.save()
    ApplianceHistory.objects.filter(appliance=app).delete()
    print("***************")
    print(rjd["company_history"])
    for h in rjd["company_history"]:
        print("루프 몇번 도니")
        print(h)
        history = ApplianceHistory()
        history.appliance = app
        history.company_history_year = h["company_history_year"]
        history.company_history_content = h["company_history_content"]
        history.save()


    return JsonResponse({"result":"ok"})




def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'='* (4 - missing_padding)
    return base64.decodebytes(data)

@csrf_exempt
@my_timer
def vue_update_startup_with_application_6(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    app = Appliance.objects.get(id=rjd["id"])
    startup = Startup.objects.get(id=rjd["st_id"])

    try:
        if request.FILES["attached_ir_file"]:
            # startup.attached_ir_file = handle_uploaded_file_right(request.FILES["attached_ir_file"], str(request.FILES["attached_ir_file"]), startup.id)
            # startup.save()
            app.attached_ir_file = handle_uploaded_file_right(request.FILES["attached_ir_file"], str(request.FILES["attached_ir_file"]), startup.id)
            app.save()
    except Exception as e:
         print(e)
    try:
        if request.FILES["attached_cert_file"]:
            # startup.attached_cert_file = handle_uploaded_file_right(request.FILES["attached_cert_file"], str(request.FILES["attached_cert_file"]), startup.id)
            # startup.save()
            app.attached_cert_file = handle_uploaded_file_right(request.FILES["attached_cert_file"], str(request.FILES["attached_cert_file"]), startup.id)
            app.save()
    except Exception as e:
         print(e)

    try:
        if request.FILES["attached_tax_file"]:
            # startup.attached_tax_file = handle_uploaded_file_right(request.FILES["attached_tax_file"],
            #                                                         str(request.FILES["attached_tax_file"]),
            #                                                         startup.id)
            # startup.save()
            app.attached_tax_file = handle_uploaded_file_right(request.FILES["attached_tax_file"],
                                                                str(request.FILES["attached_tax_file"]), startup.id)
            app.save()
    except Exception as e:
        print(e)

    try:
        if request.FILES["attached_fund_file"]:
            # startup.attached_fund_file = handle_uploaded_file_right(request.FILES["attached_fund_file"],
            #                                                         str(request.FILES["attached_fund_file"]),
            #                                                         startup.id)
            # startup.save()
            app.attached_fund_file = handle_uploaded_file_right(request.FILES["attached_fund_file"],
                                                                str(request.FILES["attached_fund_file"]), startup.id)
            app.save()
    except Exception as e:
        print(e)

    try:
        if request.FILES["attached_ppt_file"]:
            # startup.attached_ppt_file = handle_uploaded_file_right(request.FILES["attached_ppt_file"],
            #                                                         str(request.FILES["attached_ppt_file"]),
            #                                                         startup.id)
            # startup.save()
            app.attached_ppt_file = handle_uploaded_file_right(request.FILES["attached_ppt_file"],
                                                                str(request.FILES["attached_ppt_file"]), startup.id)
            app.save()
    except Exception as e:
        print(e)

    try:
        if request.FILES["attached_etc_file"]:
            # startup.attached_etc_file = handle_uploaded_file_right(request.FILES["attached_etc_file"],
            #                                                         str(request.FILES["attached_etc_file"]),
            #                                                         startup.id)
            # startup.save()
            app.attached_etc_file = handle_uploaded_file_right(request.FILES["attached_etc_file"],
                                                                str(request.FILES["attached_etc_file"]), startup.id)
            app.save()
    except Exception as e:
        print(e)

    try:
        if request.FILES["attached_ip_file"]:
            # startup.attached_ip_file = handle_uploaded_file_right(request.FILES["attached_ip_file"],
            #                                                         str(request.FILES["attached_ip_file"]),
            #                                                         startup.id)
            # startup.save()
            app.attached_ip_file = handle_uploaded_file_right(request.FILES["attached_ip_file"],
                                                                str(request.FILES["attached_ip_file"]), startup.id)
            app.save()
    except Exception as e:
        print(e)

    return JsonResponse({"result":"ok"})



#--- 여러 파일 업로드 창 만들기, 지재권 여러파일 등록하기
def handle_uploaded_file_right(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/service_product/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/service_product/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/service_product')
    with open('media/uploads/user/'+ str(user_id) +'/company/service_product/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
        return 'media/uploads/user/'+ str(user_id) +'/company/service_product/'+filename


# --------(스타트업) 지원서 불러오기 : 지원서 작성완료 후/제출하기 누르기 전, 미리보기----------------------------------
# --------[스타트업 지원서 불러오기 기능]-----------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_application(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    startup = AdditionalUserInfo.objects.get(id=user_auth_id).user.startup
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business"))
    app, created = Appliance.objects.get_or_create(startup=startup, support_business=support_business)
    result = {}

    if created == True:
        print("생성되었습니다.")
        result["id"] = app.id
        result["st_id"]= startup.id
        app.st_id = startup.id
        result["support_business_id"] = support_business.id
        app.support_business_id = support_business.id
        result["support_business_appliance_form"] = support_business.support_business_appliance_form
        result["support_business_meta"] = support_business.support_business_meta
        result["address_0"] = startup.address_0
        app.address_0 = startup.address_0
        result["address_1"] = startup.address_1
        app.address_1 = startup.address_1
        result["company_name"] = startup.company_name
        app.company_name = startup.company_name
        result["established_date"] = startup.established_date
        app.established_date = startup.established_date

        result["repre_name"] = startup.repre_name
        app.repre_name = startup.repre_name
        result["repre_tel"] = startup.repre_tel
        app.repre_tel = startup.repre_tel
        result["repre_email"] = startup.repre_email
        app.repre_email = startup.repre_email

        result["mark_name"] = startup.mark_name
        app.mark_name = startup.mark_name
        result["mark_email"] = startup.mark_email
        app.mark_email = startup.mark_email
        result["mark_tel"] = startup.mark_tel
        app.mark_tel = startup.mark_tel

        result["company_website"] = startup.company_website
        app.company_website = startup.company_website
        result["company_youtube"] = startup.company_youtube
        app.company_youtube = startup.company_youtube
        result["company_instagram"] = startup.company_instagram
        app.company_instagram = startup.company_instagram
        result["company_facebook"] = startup.company_facebook
        app.company_facebook=startup.company_facebook
        result["company_kind"] = startup.company_kind
        app.company_kind= startup.company_kind


        result["company_keyword"] = startup.company_keyword
        app.company_keyword = startup.company_keyword
        result["attached_ir_file"] = startup.attached_ir_file
        app.attached_ir_file=startup.attached_ir_file
        result["attached_cert_file"] = startup.attached_cert_file
        app.attached_cert_file = startup.attached_cert_file
        result["attached_tax_file"] = startup.attached_tax_file
        app.attached_tax_file = startup.attached_tax_file
        result["attached_fund_file"] = startup.attached_fund_file
        app.attached_fund_file=startup.attached_fund_file
        result["attached_ppt_file"] = startup.attached_ppt_file
        app.attached_ppt_file = startup.attached_ppt_file
        result["attached_etc_file"] = ""
        result["attached_ip_file"] = startup.attached_ip_file
        app.attached_ip_file = startup.attached_ip_file
        result["company_total_employee"] = 0
        app.company_total_employee = 0
        result["company_hold_employee"] = 0
        app.company_hold_employee =0
        result["company_assurance_employee"] = 0
        app.company_assurance_employee = 0
        result["revenue_before_0"] = startup.revenue_before_0
        app.revenue_before_0=startup.revenue_before_0
        result["revenue_before_1"] = startup.revenue_before_1
        app.revenue_before_1=startup.revenue_before_1
        result["revenue_before_2"] = startup.revenue_before_2
        app.revenue_before_2 = startup.revenue_before_2
        result[ "revenue_before_year_0"] = 2017
        app.revenue_before_year_0 = 2017
        result["revenue_before_year_1"] = 2016
        app.revenue_before_year_1 =2016
        result[ "revenue_before_year_2"] = 2015
        app.revenue_before_year_2 = 2015
        result["export_before_0"] = startup.export_before_0 if app.export_before_0 == "None" or app.export_before_0 == "" else app.export_before_0
        app.export_before_0 = startup.export_before_0
        result["export_before_1"] = startup.export_before_1 if app.export_before_1 == "None" or app.export_before_1 == "" else app.export_before_1
        app.export_before_1 = startup.export_before_1
        result["export_before_2"] = startup.export_before_2 if app.export_before_2 == "None" or app.export_before_2 == "" else app.export_before_2
        app.export_before_2 = startup.export_before_2
        result[ "export_before_year_0"] = 2017
        app.export_before_year_0 = 2017
        result["export_before_year_1"] = 2016
        app.export_before_year_1 = 2016
        result[ "export_before_year_2"] = 2015
        app.export_before_year_2 = 2015
        result["export_before_nation_0"] = startup.export_before_nation_0 if app.export_before_nation_0 == "None" or app.export_before_nation_0 == "" else app.export_before_nation_0
        app.export_before_nation_0 = startup.export_before_nation_0
        result["export_before_nation_1"] = startup.export_before_nation_1 if app.export_before_nation_1 == "None" or app.export_before_nation_1 == "" else app.export_before_nation_1
        app.export_before_nation_1=startup.export_before_nation_1
        result[ "export_before_nation_2"] = startup.export_before_nation_2 if app.export_before_nation_2 == "None" or app.export_before_nation_2 == "" else app.export_before_nation_2
        app.export_before_nation_2 = startup.export_before_nation_2
        result["company_intro"] = startup.company_intro if app.company_intro==None or app.company_intro=="" else app.company_intro
        app.company_intro = startup.company_intro
        result["company_history"] = []
        app.save()
        for t in startup.history_set.all():
            his = ApplianceHistory()
            his.appliance = app
            his.company_history_year=t.company_history_year
            his.company_history_content=t.company_history_content
            his.save()
            result["company_history"].append({
                "company_history_year": t.company_history_year,
                "company_history_content": t.company_history_content,
                "id": his.id,
            })

        result["invest"] = []
        print(app.applianceinvest_set)
        for inv in startup.companyinvest_set.all():
            appinv =  ApplianceInvest()
            appinv.applicance = app
            appinv.company_invest_year= inv.company_invest_year
            appinv.company_invest_size= inv.company_invest_size
            appinv.company_invest_agency= inv.company_invest_agency
            appinv.save()
            result["invest"].append({
                "id":appinv.id,
                "company_invest_year":inv.company_invest_year,
                "company_invest_size": inv.company_invest_size,
                "company_invest_agency": inv.company_invest_agency,
            })
        result["tag"]=[]
        result["base_filter"] = []
        result["special_filter"] = []
        area_filter=[]
        for t in startup.selected_company_filter_list.all():
            app.selected_company_filter_list.add(t)

        for t in startup.selected_company_filter_list.all():
            if t.cat_0 == "기본장르" or t.cat_0=="영역":
                area_filter.append(t.filter_name)
        for t in startup.selected_company_filter_list.all():
            if t.cat_0 =="기본장르":
                result["base_filter"].append(t.filter_name)
            elif t.cat_0 =="영역":
                result["special_filter"].append(t.filter_name)
        print()
        result["is_submit"] = False
        result["service"] = []
        for s in startup.service_set.all():
            app_ser = ApplianceService()
            app_ser.appliance = app
            app_ser.service_name=s.service_name
            app_ser.service_intro=s.service_intro
            app_ser.startup = startup
            app_ser.save()
            result["service"].append({"service_name":s.service_name,"":s.service_intro ,"id":app_ser.id})
        result["created"] = True
    else:
        result["id"] = app.id
        result["st_id"] = startup.id
        result["created"] = False
        result["support_business_id"] = support_business.id
        result["support_business_appliance_form"] = support_business.support_business_appliance_form
        result["support_business_meta"] = support_business.support_business_meta
        result["address_0"] =  app.address_0
        result["address_1"] =  app.address_1

        result["company_name"] = startup.company_name
        result["established_date"] = startup.established_date
        result["company_kind"] = startup.company_kind

        result["repre_name"] =  app.repre_name
        result["repre_tel"] =  app.repre_tel
        result["repre_email"] = app.repre_email
        result["mark_name"] =  app.mark_name
        result["mark_email"] =  app.mark_email
        result["mark_tel"] = app.mark_tel
        result[ "company_website"] = app.company_website
        result["company_youtube"] =  app.company_youtube
        result["company_instagram"] =  app.company_instagram
        result["company_facebook"] = app.company_facebook

        result["company_keyword"] =  app.company_keyword
        result["attached_ir_file"] =  app.attached_ir_file
        result["attached_cert_file"] =  app.attached_cert_file
        result["attached_tax_file"] =   app.attached_tax_file
        result["attached_fund_file"] =  app.attached_fund_file
        result["attached_ppt_file"] =  app.attached_ppt_file
        result["attached_etc_file"] =  app.attached_etc_file
        result["attached_ip_file"] = app.attached_ip_file
        result["company_total_employee"] = app.company_total_employee
        result["company_hold_employee"] = app.company_hold_employee
        result["company_assurance_employee"] =  app.company_assurance_employee
        result["revenue_before_0"] = app.revenue_before_0
        result["revenue_before_1"] = app.revenue_before_1
        result["revenue_before_2"] = app.revenue_before_2
        result["revenue_before_year_0"] = 2017
        result["revenue_before_year_1"] = 2016
        result["revenue_before_year_2"] = 2015
        result["export_before_0"] = app.export_before_0
        result["export_before_1"] = app.export_before_1
        result["export_before_2"] =  app.export_before_2
        result["export_before_year_0"] = 2017
        result["export_before_year_1"] = 2016
        result["export_before_year_2"] = 2015
        result["export_before_nation_0"] =  app.export_before_nation_0
        result["export_before_nation_1"] =  app.export_before_nation_1
        result["export_before_nation_2"] = app.export_before_nation_2
        result["company_intro"] =  app.company_intro
        result["company_history"] = []
        for t in app.appliancehistory_set.all():
            result["company_history"].append({
                "company_history_year": t.company_history_year,
                "company_history_content": t.company_history_content,
                "id": t.id,
            })
        result["invest"] = []
        for inv in app.applianceinvest_set.all():
            result["invest"].append({
                "id":inv.id,
                "company_invest_year": inv.company_invest_year,
                "company_invest_size": inv.company_invest_size,
                "company_invest_agency": inv.company_invest_agency,
            })
        result["tag"] = []
        result["base_filter"] = []
        result["special_filter"] = []
        area_filter = []
        for t in app.selected_company_filter_list.all():
            if t.cat_0 == "기본장르" or t.cat_0 == "영역":
                area_filter.append(t.filter_name)
        for t in app.selected_company_filter_list.all():
            if t.cat_0 == "기본장르":
                result["base_filter"].append(t.filter_name)
            elif t.cat_0 == "영역":
                result["special_filter"].append(t.filter_name)
        result["service"] = []
        for s in app.applianceservice_set.all():
            result["service"].append({"service_name": s.service_name, "service_intro": s.service_intro, "id": s.id})
        result["is_submit"]=app.is_submit
        result["is_applied_to_company_info"] = app.is_applied_to_company_info


    return JsonResponse(result, )


# --------(스타트업) 작성완료한 지원서 제출하기-------------------------------------------------------------------------
# --------[스타트업 지원서 제출하기]-----------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_submit_application(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    gr = request.GET.get("support_business")
    support_business = SupportBusiness.objects.get(id=gr)
    startup = AdditionalUserInfo.objects.get(id=user_auth_id).user.startup
    app = Appliance.objects.get(support_business=support_business, startup=startup)
    filter_list = []
    for a_filter in app.selected_company_filter_list.all():
        filter_list.append( SupportBusinessFilter.objects.get(id=a_filter.id).filter_name )
    app.raw_filter_list = ",".join(filter_list)
    app.is_submit = True
    app.appliance_update_at_ymdt = timezone.now()
    app.save()
    support_business_application = SupportBusinessApplicant()
    support_business_application.applicant_support_business = support_business
    support_business_application.applicant_usr = AdditionalUserInfo.objects.get(id=user_auth_id)
    support_business_application.save()
    for filter in AdditionalUserInfo.objects.get(id=user_auth_id).user.startup.selected_company_filter_list.all():
        try:
            support_business_application.applicant_usr_filter( FilterForStatics.objects.get(filter_name=filter.filter_name) )
        except:
            pass



    return JsonResponse({"result":"success"})
@csrf_exempt
@my_timer
def vue_submit_support_business(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business = SupportBusiness.objects.get(id=request.POST.get("id"))
    support_business.support_business_appliance_form = request.POST.get("meta")
    support_business.support_business_update_at_ymdt = timezone.now()

    if request.POST.get("user") == "mng":
        support_business.support_business_status=2


    support_business.save();
    return JsonResponse({"result":"ok"})

# --------(스타트업) "작성중인 지원서/ 지원완료/공고종료" : 지원사업 관리 페이지
# --------[스타트업 지원서 불러오기 ]-------
@csrf_exempt
@my_timer
def get_startup_application(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    # user_auth_id = request.GET.get("user_auth_id")
    ad_user = AdditionalUserInfo.objects.get(id=user_auth_id)
    user = ad_user.user
    startup = Startup.objects.get(user_id=user.id)
    result={}
    #작성중인 지원서
    result["writing"]=[]

    for ap in Appliance.objects.filter(startup=startup).filter(is_submit=False):
        try:
            temp = {}
            temp["support_business_name"] = ap.support_business.support_business_name
            temp["favorite"] = (ap.support_business.additionaluserinfo_set.all()).count()
            temp["support_business_id"] = ap.support_business.id
            temp["support_business_kikwan"] = ap.support_business.support_business_author.mng_kikwan
            temp["support_business_poster"] = ap.support_business.support_business_poster
            temp["support_business_apply_start_ymd"] = ap.support_business.support_business_apply_start_ymd
            temp["support_business_apply_end_ymdt"] = ap.support_business.support_business_apply_end_ymdt
            temp["updated"] = ap.appliance_update_at_ymdt

            if ap.support_business.support_business_recruit_size == "" or ap.support_business.support_business_recruit_size == None or  ap.support_business.support_business_recruit_size== "0" :
                temp["comp"] =  str((Appliance.objects.filter(support_business=ap.support_business).filter(is_submit=True)).count()) +" : 1"
            else:
                #temp["comp"] = len(Appliance.objects.filter(support_business=ap.support_business)) / int(ap.support_business.recruit_size)
                number = str(round( ((Appliance.objects.filter(support_business=ap.support_business).filter(is_submit=True).count()))/int(ap.support_business.support_business_recruit_size ),1 ) )
                if number == "0.0":
                    number ="0"
                temp["comp"] = ""
            try:
                if ap.support_business.support_business_status == "4":  # 작성중인 공고문
                    temp["status"] = "모집종료"
                if ap.support_business.support_business_status == "1":  # 작성중인 공고문
                    temp["status"] = "작성중"
                if ap.support_business.support_business_status == "2":  # 승인대기중인 공고문
                    temp["status"]= "승인대기"
                if ap.support_business.support_business_status == "3":
                    temp["status"] = "공고중"
                if ap.support_business.support_business_apply_end_ymdt < timezone.now() and ap.support_business.support_business_status == "3":  # 모집 종료 된 공고문
                    temp["status"] = "모집종료"
                if ap.support_business.support_business_status == "5":  # 공고 종료 된 공고문
                    temp["status"] = "공고종료"
                if ap.support_business.support_business_status == "6":  # 블라인드 공고문
                    temp["status"]= "블라인드"
            except Exception as e:
                print(e)
                temp["status"] = "작성중"

            temp["date"] = str(ap.support_business.support_business_pro_0_end_ymd).split(" ")[0]
            temp["start"] = str(ap.support_business.support_business_apply_start_ymd).split(" ")[0]
            temp["id"] = ap.id
            result["writing"].append(copy.deepcopy(temp))
                # 지원완료 지원서
        except Exception as e:
            print(e)
    result["comp"] = []
    for ap in Appliance.objects.filter(startup=startup).filter(is_submit=True):
        temp = {}
        temp["support_business_name"] = ap.support_business.support_business_name
        temp["favorite"] = (ap.support_business.additionaluserinfo_set.all()).count()
        temp["updated"] = ap.appliance_update_at_ymdt
        if ap.support_business.support_business_recruit_size == "" or  ap.support_business.support_business_recruit_size == None  or ap.support_business.support_business_recruit_size == "0":
            temp["comp"] = ""
        else:


            # temp["comp"] = len(Appliance.objects.filter(support_business=ap.support_business)) / int(ap.support_business.recruit_size)
            number = str( round(((Appliance.objects.filter(support_business=ap.support_business).filter(
                is_submit=True).count())) / int(ap.support_business.support_business_recruit_size ), 1) )
            if number == "0.0":
                number ="0"
            temp["comp"] = str(number) +" : 1"
        temp["date"] = str(ap.support_business.support_business_pro_0_end_ymd).split(" ")[0]
        temp["start"] = str(ap.support_business.support_business_pro_0_start_ymd).split(" ")[0]
        temp["support_business_kikwan"] = ap.support_business.support_business_author.mng_kikwan
        temp["support_business_apply_start_ymd"] = ap.support_business.support_business_apply_start_ymd
        temp["support_business_poster"] = ap.support_business.support_business_poster
        temp["support_business_apply_end_ymdt"] = ap.support_business.support_business_apply_end_ymdt
        temp["id"] = ap.id
        temp["support_business_id"]=ap.support_business.id
        award_num = (Award.objects.filter(support_business=ap.support_business).filter(startup=startup)).count()
        is_award=False
        if award_num !=0 :
            is_award = True
        temp["is_awarded"]= is_award


        try:
            if ap.support_business.support_business_status == "4":  # 작성중인 공고문
                temp["status"] = "모집종료"
            if ap.support_business.support_business_status == "1":  # 작성중인 공고문
                temp["status"] = "작성중"
            if ap.support_business.support_business_status == "2":  # 승인대기중인 공고문
                temp["status"] = "승인대기"
            if ap.support_business.support_business_status == "3":
                temp["status"] = "공고중"
            if ap.support_business.support_business_apply_end_ymdt < timezone.now() and ap.support_business.support_business_status == "3":  # 모집 종료 된 공고문
                temp["status"] = "모집종료"
            if ap.support_business.support_business_status == "5":  # 공고 종료 된 공고문
                temp["status"] = "공고종료"
            if ap.support_business.support_business_status == "6":  # 블라인드 공고문
                temp["status"] = "블라인드"
        except Exception as e:
            print(e)
            temp["status"] = "작성중"
        result["comp"].append(copy.deepcopy(temp))

    result["end"] = []
    for ap in Appliance.objects.filter(startup=startup).filter(is_submit=True).filter(Q(support_business__support_business_status="5")):

        temp = {}
        temp["support_business_name"] = ap.support_business.support_business_name
        temp["favorite"] = (ap.support_business.additionaluserinfo_set.all()).count()
        if ap.support_business.support_business_recruit_size == ""or  ap.support_business.support_business_recruit_size == None  or ap.support_business.support_business_recruit_size == "0":
            temp["comp"] = ""
        else:
            # temp["comp"] = len(Appliance.objects.filter(support_business=ap.support_business)) / int(ap.support_business.recruit_size)
            number = str( round(((Appliance.objects.filter(support_business=ap.support_business).filter(
                is_submit=True).count())) / int(ap.support_business.support_business_recruit_size ), 1) )
            if number == "0.0":
                number ="0"
            temp["comp"] = number + " : 1"
        temp["date"] = str(ap.support_business.support_business_pro_0_end_ymd).split(" ")[0]
        temp["start"] = str(ap.support_business.support_business_pro_0_start_ymd).split(" ")[0]
        temp["support_business_apply_start_ymd"] = ap.support_business.support_business_apply_start_ymd
        temp["support_business_poster"] = ap.support_business.support_business_poster
        temp["support_business_apply_end_ymdt"] = ap.support_business.support_business_apply_end_ymdt
        temp["id"] = ap.id
        temp["support_business_id"]=ap.support_business.id
        temp["updated"] = ap.appliance_update_at_ymdt
        award_num = (Award.objects.filter(support_business=ap.support_business).filter(startup=startup)).count()
        is_award=False
        if award_num !=0 :
            is_award = True
        temp["is_awarded"]= is_award


        try:
            if ap.support_business.support_business_status == "4":  # 작성중인 공고문
                temp["status"] = "모집종료"
            if ap.support_business.support_business_status == "1":  # 작성중인 공고문
                temp["status"] = "작성중"
            if ap.support_business.support_business_status == "2":  # 승인대기중인 공고문
                temp["status"] = "승인대기"
            if ap.support_business.support_business_status == "3":
                temp["status"] = "공고중"
            if ap.support_business.support_business_apply_end_ymdt < timezone.now() and ap.support_business.support_business_status == "3":  # 모집 종료 된 공고문
                temp["status"] = "모집종료"
            if ap.support_business.support_business_status == "5":  # 공고 종료 된 공고문
                temp["status"] = "공고종료"
            if ap.support_business.support_business_status == "6":  # 블라인드 공고문
                temp["status"] = "블라인드"
        except Exception as e:
            print(e)
            temp["status"] = "작성중"
        result["end"].append(copy.deepcopy(temp))


    return JsonResponse(result)


# # 해당 지원사업에 좋아요를 누른모든 스타트업 유저 목록을 반환한다.
# def vue_get_favorite_to_support_business(request):
#     support_business = SupportBusiness.objects.get(id=request.POST.get("id"))
#     user = AdditionalUserInfo.objects.filter(favorite)
#TODO: 스타트업 정보 입력 업무 후에 진행할것.



#----------------------------------------------------------------------------------------------------------------------
# 자. 매니저가 모집기간이  종료되면 공고 상태 변경 '공고중 > 모집마감'
#       <목표>
#       1. 공고문의 상태가 변경(공고중>모집마감)
#       2. 대시보드에서 알람이 뜬다
#----------------------------------------------------------------------------------------------------------------------





#----------------------------------------------------------------------------------------------------------------------
# 차. 매니저: 선정자 선택시 공고 상태 변경 '모집마감 > 공고종료'
#       <목표>
#       1. 선정자 선택이 가능하다.
#       2. '선정자를 선택'하면 공고 상태가 변경된다. '모집마감 > 공고 종료'
#----------------------------------------------------------------------------------------------------------------------






#------ (매니저) 지원사업 관리페이지 : 스타트업 리스트가 나타나게 해주는 함수 / 선정 대상자 리스트업
@csrf_exempt
@my_timer
def vue_get_support_business_appliance(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business"))
    ap = Appliance.objects.filter(support_business=support_business, is_submit=True).select_related("startup")
    k = 1
    result = []
    for a in ap:
        temp = {}
        temp["index"] = k
        k = k + 1
        temp["company_name"] = a.startup.company_name
        temp["company_kind"] = a.startup.company_kind
        temp["company_id"] = a.startup.id
        temp["id"] = a.id
        temp["mark_name"] = a.startup.mark_name
        temp["mark_email"] = a.startup.mark_email
        temp["mark_tel"] = a.startup.mark_tel
        temp["appliance_update_at_ymdt"] = a.appliance_update_at_ymdt
        temp["down_path"] = a.id
        result.append(copy.deepcopy(temp))
        print(temp)
    print(result)
    return JsonResponse(result,safe=False)
# 수정전
# 쿼리수:11
# vue_get_support_business_appliance 함수가 실행된 총 시간: 0.21616053581237793 초
# db 쿼리 시간 :  0.187 초
# 쿼리 제외한 연산 시간 :  0.02916053581237793 초
# 수정후
# 쿼리수:2
# vue_get_support_business_appliance 함수가 실행된 총 시간: 0.053377389907836914 초
# db 쿼리 시간 :  0.053 초
# 쿼리 제외한 연산 시간 :  0.00037738990783691556 초

# --------(매니저) 선정자 선택 함수
# --------postman 확인 완료 - 정상작동

@csrf_exempt
@my_timer
def vue_set_awarded(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business_id = request.GET.get("support_business_id")
    ap_id_list = request.GET.get("ap_id").split(",")
    for ap in ap_id_list:
        r_ap = Appliance.objects.get(id=ap)
        win,save = Award.objects.get_or_create(support_business_id=support_business_id, startup=r_ap.startup)
        win.save()
        support_business_award = SupportBusinessAwarded()
        support_business_award.awarded_support_business_id = support_business_id
        support_business_award.awarded_usr = r_ap.startup.user.additionaluserinfo
        for filter in r_ap.startup.user.startup.selected_company_filter_list.all():
            try:
                support_business_award.awarded_usr_filter.add(FilterForStatics.objects.get(filter_name=filter.filter_name))
            except:
                pass
    support_business = SupportBusiness.objects.get(id= support_business_id)
    support_business.support_business_status="5"
    support_business.save()
    vue_get_alarm_startup(support_business.selected_support_business_filter_list.all(), "지원사업 선정자가 선정되었습니다.", support_business.id)


    return JsonResponse({"result":"success"})





# --------(매니저) 선정자 선택후 공고 상태 변경 '모집마감(4) > 공고 종료(5)'
@csrf_exempt
@my_timer
def support_business_end(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    id = json.loads(request.POST.get("json_data"))["id"]
    support_business = SupportBusiness.objects.get(id=id)
    support_business.status = 5
    support_business.save();


# ------[ 중복 그룹 5 ]----def 3개 중복-----------------------------------------------------------------------------------
#------------<분류다시할것> (매니저) 유저가 제출한 지원서+파일 -> zipfile로 만들어주고 다운해줌, 현재 지원서는 작동안함: 매니저/기관관리자 지원사업관리 페이지
#-------- (선생님) 파일 다운로드, 엑셀 다운로드 이런 양식으로 해라------------------------------------------------------
@csrf_exempt

def downloadit(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    response = HttpResponse(request.POST.get("data"), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(request.POST.get("filename"))
    return response
#-------------------------------------------------
#-----[1/3]----
@csrf_exempt
@my_timer
def appliance_all_download(request, support_business):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    ap_list = Appliance.objects.filter(support_business_id=support_business)
    zip_file_name = "%s.zip" % (
        str(ap_list[0].support_business.apply_end).split("-")[
            0] + "_" + ap_list[0].support_business.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list[4:5]:
        zip_subdir = "applicance"
        url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].support_business_id) + "/" + str(ap.id)
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
        if ap.attached_fund_file != "":
            fdir, fname = os.path.split(ap.attached_fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(ap.attached_fund_file.path, zip_path)
        if ap.attached_etc_file != "":
            fdir, fname = os.path.split(ap.attached_etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(ap.attached_etc_file.path, zip_path)
        if ap.ir_file != "":
            fdir, fname = os.path.split(ap.ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(ap.ir_file.path, zip_path)
        if ap.attached_ppt_file != "":
            fdir, fname = os.path.split(ap.attached_ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(ap.attached_ppt_file.path, zip_path)
        if ap.attached_tax_file != "":
            fdir, fname = os.path.split(ap.attached_tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(ap.attached_tax_file.path, zip_path)
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
        sheet.write(k, 1, a.startup.company_name)
        sheet.write(k, 2, a.startup.company_kind)
        sheet.write(k, 3, a.startup.repre_name)
        sheet.write(k, 4, Appliance.objects.filter(support_business_id=support_business).filter(startup_id=a.startup.id))
        sheet.write(k, 5, a.startup.repre_email)
        sheet.write(k, 6, a.startup.repre_tel)
        filter_list = a.startup.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.filter_name)
        sheet.write(k, 7, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    zf.writestr("전체 리스트.xls", f.getvalue())

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_file_name, safe='')
    return resp


#----------------------------------------------------------------------------------------------------------------------
# 카. 통계 그래프 만들기!
# 하기(1, 2번 정보) 정보들중
#       A 섹션 통계 그래프 만들기,
#           1. 클릭수, 관심담기, 지원자수, 카운팅해서,
#
#       B 섹션 그래프 만들기(파이그래프)
#           2. 기업의 정보를 태그 기준으로 추출/ 정리후 카운팅해서
#----------------------------------------------------------------------------------------------------------------------

# --------(통계) (기관관리자) 기관회원 조회 > 소속회원 보기
# --------[기관관리자 - 매니저에 따른 지원사업 가져오기 ]-------

@csrf_exempt
@my_timer
def vue_get_mng_list(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    id = request.POST.get("id")
    mngs = AdditionalUserInfo.objects.get(id=id).additionaluserinfo_set.all()
    m_list= []
    for m in mngs:
        temp={}
        temp["id"] = m.id
        temp["mng_name"] = m.mng_name
        temp["support_business"] =[]
        for s in SupportBusiness.objects.filter(support_business_author=m):
            ttem={}
            ttem["support_business_name"] = s.support_business_name
            ttem["id"] = s.id
            temp["support_business"].append(copy.deepcopy(ttem))
        m_list.append(copy.deepcopy(temp))
    return JsonResponse(m_list, safe = False)




# ------[ 중복 그룹 6 ]----def 3개 중복-----------------------------------------------------------------------------------
# --------(통계) 전체 지원사업 통계
# 통계 홈화면에서 맨처음에 드롭다운으로 원하는 '지원사업' 통계를 선택해서 보여주는 함수
#-----중복 [1/3]----
# --------[전체 통계, 매니저, 기관관리자.]-----------------------------------------------------------------------------


#---- (중복 2/3) 약간 (중복)
# --------(리스트) (매니저) 해당 매니저의 전체 지원사업 통계를 계산해주는 함수
# 전체 지원사업 통계에서 아무것도 선택하지 않았을 때, 전체라고 가정하고 통계를 보여주는 화면 // 현재 홈화면임
# --------[매니저 통계 페이지, 상세 지원사업 통계 데이터 추출 기관 관리자, 매니저 지원사업 통계 페이지에서 호출  ]------
# def view_last_cron_stat_txt():
#     file_content2="/tmp/cron_stat.txt"
#     return file_content2
#
# def cron_stat():
#     result=""
#     #for all id
#
#            url1="localhost:890/get_static_info/id="+id
#            #url2=
#            #url3=
#
#     return HttpResponse(result)
@csrf_exempt
@my_timer
def get_static_info_from_stattable(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result

    my_id = request.GET.get("stat_user_id")
    my_stat_page= request.GET.get("stat_page")

    st = StatTable.objects.filter(stat_user_id=my_id).filter(stat_page=my_stat_page).order_by("-stat_timestamp")[0]

    result = st.stat_json
    return HttpResponse(result)

def date_range(start_date, end_date):
    for ordinal in range(start_date.toordinal(), end_date.toordinal()):
        yield datetime.date.fromordinal(ordinal)




import requests
def cron_stat(request):

    for add in  AdditionalUserInfo.objects.filter(auth="MNG"):
        url="http://13.209.21.165:890/get_static_info/?id="+add.id
    return JsonResponse({"result":"true"})

def filter_categorizing(filter_list):
    comtype_filter=[]
    location_filter=[]
    genre_filter=[]
    area_filter=[]
    local
    for filter in filter_list:
        if filter.cat_1 == "기업형태":
            comtype_filter.append(filter.filter_name)
            kind = filter.filter_name
        if filter.cat_1 == "소재지":
            location_filter.append(filter.filter_name)
        if filter.cat_0 == "기본장르":
            genre_filter.append(filter.filter_name)
        if filter.cat_0 == "영역":
            area_filter.append(filter.filter_name)

#-- =-- pin
# ------ postman 정상음답
@my_timer
@csrf_exempt
def get_support_business_static(request):
    # 프론트에 보낼 객체 선언
    result={}
    # 지원 사업 아이디를 get 파라메터로 받아옴
    support_business_id = request.GET.get("support_business_id")
    # 지원 사업 객체를 만듦
    support_business = SupportBusiness.objects.get(id=support_business_id)
    # 지원 사업의 작성자를 get 파라메터로 받아옴
    support_business_author_id = request.GET.get("support_business_author")
    # 지원사업의 최종 업데이트일 = 기관관리자의 승인일 = 홈페이지에 노출된 날 이 지원사업 통계에서 최초 날짜가 됨
    result["support_business_min_date"] =  str(SupportBusiness.objects.get(id=support_business_id).support_business_update_at_ymdt).split(" ")[0]

    #  (특정)매니저가 올린 (특정)지원사업의 해당 지원사업의 방문 데이터
    # 방문 날짜 데이터 - distict 로 날짜만 추출
    support_business_detail_hit_date_ymd=[]
    # 날짜로 해당 날짜에 몇번 방문했는지 객체 배열로 만든다
    support_business_detail_hit=[]
    # 방문 로그에서 날짜 역순으로, 중복없이 배열을 만듬
    for date_dict in  HitLog.objects.filter(support_business_id=support_business_id).values("date").order_by("-date").distinct():
        # 중복없게 하기 위한 조건문 - 없으면 배열에 추가한다
        if date_dict["date"] not in support_business_detail_hit_date_ymd :
            support_business_detail_hit_date_ymd.append(date_dict["date"])
    # 중복없이 만들어진 날짜 배열로 방문 리스트를 추가한다.  date: 방문 날짜, hit : 방문수
    for date in  support_business_detail_hit_date_ymd:
        support_business_detail_hit.append(
            {
                "date":date, "number":(HitLog.objects.filter(support_business_id= support_business_id).filter(date=date)).count()
            }
        )
    # 프론트에 보낼 객체에 저장한다.
    result["support_business_detail_hit"] = support_business_detail_hit


    # 방문자 리스트에서 스타트업 리스트를 만듬
    startup_list = []
    # 방문자 리스트에서 user 의 아이디를 중복 없이 추출함
    for hit_startup in HitLog.objects.filter(support_business=support_business).values("user").distinct():
        try:
            # 스타트업 리스트 배열에 유저 아이디로 스타트업 객채를 검색해서 추가한다.
            startup_list.append( Startup.objects.get(user= AdditionalUserInfo.objects.get(id=hit_startup["user"]).user))
        except:
            # 방문자 중에 스타트업이 없는 경우 - 매니저, 기관관리자, 비로그인 유저 등
            pass
    # 기업 형태 필터
    hit_comtype_filter = []
    # 기업 소재지 필터
    hit_location_filter = []
    # 기업 장르 필터
    hit_genre_filter =[]
    # 기업 영역 필터
    hit_area_filter = []
    # 스타트업 리스트
    result["hit_startup_list"]=[]
    # 인덱스를 보내주기위한 k ( 사용자에게 보내지는 테이블에 나타나는 인덱스 )
    k=1

    for startup in startup_list:
        # 스타트업 배열에 있는 한 스타트업의
        # 필터를 모두 가져온다
        filter_list = startup.selected_company_filter_list.all()

        company_kind = ""
        local = []
        for filter in filter_list:
            # 필터가 속한 카테고리 1 이 기업형태 이면
            if filter.cat_1 =="기업형태":
                #기업 형태 필터에  추가
                hit_comtype_filter.append(filter.filter_name)
                company_kind = filter.filter_name
            if filter.cat_1 =="소재지":
                #소재지 필터에 추가
                local.append(filter.filter_name)
                hit_location_filter.append(filter.filter_name)
            if filter.cat_0 =="기본장르":
                #기업장르 필터에 추가
                hit_genre_filter.append(filter.filter_name)
            if filter.cat_0 =="영역":
                #기업 영역 필터에 추가
                hit_area_filter.append(filter.filter_name)
        # 필터가 정리되면  스타트업 리스트를 추가한다.
        result["hit_startup_list"].append({
            # 스타트업 아이디 (첨부서류 다운 받을때 사용)
            "startup_id":startup.id,
            # 인덱스, 대표 이메일, 회사 이름
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            # 기업 형태
            "company_kind": company_kind,
            # 기업 소재지
            "company_local": ",".join(local),
            # 기업 직원수, 대표 전화
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        # 인덱스를 +1 해줌
        k = k + 1
    # 방문 통계에 모든 리스트안에 저장된 모든 필터들의 갯수를 세서 객체 배열로 저장한다
    result["hit_comtype_filter"] = (organize(hit_comtype_filter))
    result["hit_location_filter"] = (organize(hit_location_filter))
    result["hit_genre_filter"] = (organize(hit_genre_filter))
    result["hit_area_filter"] = (organize(hit_area_filter))

    # 매니저의 해당 지원사업의 좋아요 데이터 : [공고문 id /날짜 / 숫자 ] list1
    support_business_detail_favorite_date_ymd = []

    # 좋아요 통계
    favored_support_business=[]
    # 좋아요 누른 로그 테이블에서 중복없이 날짜 추출
    for date_dict in FavoriteLog.objects.filter(support_business=support_business).values("date").order_by("-date").distinct():
        # 날짜 리스트에 해당 날짜가 없으면 추가한다.
        if date_dict["date"] not in support_business_detail_favorite_date_ymd:
            support_business_detail_favorite_date_ymd.append(date_dict["date"])
    # 만들어진 날짜 리스트에서 각 날짜별로
    for date in support_business_detail_favorite_date_ymd:
        # 좋아요 지원사업 리스트에 추가된다. - 앞의 데이터와 동일한 포맷
        favored_support_business.append(
            {
                "date": date,
                # 해당 날짜로 검색된 테이블의 행 수 = 좋아요 수
                "number": (FavoriteLog.objects.filter(support_business=support_business).filter(date=date)).count()
            }
        )
    # favored_support_business 에 저장한다.
    result["favored_support_business"] = favored_support_business


# =======[매니저 my 지원사업 좋아요 누른 스타트업의 id, 필터 추출]====== : 완료
    startup_list = []
    # favoritelog 테이블에서 user 를 중복없이 추출
    for favored_startup in FavoriteLog.objects.filter(support_business=support_business).values("user").distinct():
        print(favored_startup)
        # 좋아요를 누른 유저의 스타트업을 추출한다.
        # 앞에서의 예외처리를 하지 않는 이유는 이미 좋아요를 누르며너 예외 처리가 프론트단에서 되기 때문
        startup_list.append( Startup.objects.get(user= AdditionalUserInfo.objects.get(id=favored_startup["user"]).user))
    # 좋아요를 누른 회사의 기업 형태 필터
    favored_comtype_filter = []
    # 좋아요를 누른 회사의 소재지 필터
    favored_location_filter = []
    # 좋아요를 누른 회사의 장르 필터
    favored_genre_filter =[]
    # 좋아요를 누른 회사의 영역 필터
    favored_area_filter = []
    # 좋아요를 누른 회사의 리스트
    result["favored_startup_list"]=[]
    k=1

    for startup in startup_list:

        # 좋아요를 누른 회사가 선택한 필터를 모두 가져온다
        filter_list = startup.selected_company_filter_list.all()

        company_kind = ""
        local = []
        for filter in filter_list:
            # 필터의 카테고리가 기업 형태라면
            if filter.cat_1 =="기업형태":
                # cat_1 = 기업 형태라면. 회사 기업 형태 리스트에 넣는다
                favored_comtype_filter.append(filter.filter_name)
                company_kind = filter.filter_name
            if filter.cat_1 =="소재지":
                # cat_1  = 소재지 라면 소재지 리스트에 넣는다
                favored_location_filter.append(filter.filter_name)
                local.append(filter.filter_name)
            if filter.cat_0 =="기본장르":
                # 필터의 카레고리가 기본장르라면, 기본장르 리스트에 넣는다
                favored_genre_filter.append(filter.filter_name)
            if filter.cat_0 =="영역":
                # 필터의 카테고리가 영역이면 영역 리스트에 넣는다
                favored_area_filter.append(filter.filter_name)

        # 좋아요를 누른 회사 리스트에 추가한다.
        result["favored_startup_list"].append({
            # 인덱스, 스타트업 대표메일, 회사 이름
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            # 기업 형태
            "company_kind": company_kind,
            # 소재지
            "company_local": ",".join(local),
            # 기업 구성원, 대표 전화
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    #좋아요를 누른 회사들의 기업 형태 , 위치, 장르, 영역 필터를 객베 배열로 만든다
    result["favored_comtype_filter"] = (organize(favored_comtype_filter))
    result["favored_location_filter"] = (organize(favored_location_filter))
    result["favored_genre_filter"] = (organize(favored_genre_filter))
    result["favored_area_filter"] = (organize(favored_area_filter))



    # 지원자  데이터
    support_business_appliance_date_ymd = []
    support_business_appliance = []
    # 지원서 테이블에서 지원사업이 현재 지원사업이고, 지원서의 제출 날짜가 지원서의 작성일 이후, 제출한날을 기준으로 역순으로 날짜 배열을 만든다
    for date_dict in Appliance.objects.filter(support_business=support_business).filter(
            appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]) \
            .dates("appliance_update_at_ymdt","day").values("appliance_update_at_ymdt").order_by("-appliance_update_at_ymdt").distinct():
        # 지원사업 지원 날짜 배열에 해당 날짜가 없는 경우에만 추가한다.
        if date_dict["appliance_update_at_ymdt"] not in support_business_appliance_date_ymd:
            support_business_appliance_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    # 날짜 데이터에 저장된 날짜로
    for date in support_business_appliance_date_ymd:
        #지원자 명단을 수정한다.
        #지원자 리스트에 하나씩 추가한다.
        support_business_appliance.append(
            {
                "date": date,
                "number": (Appliance.objects.filter(support_business=support_business).filter(appliance_update_at_ymdt__date=str(date))).count()
            }
        )
    result["support_business_appliance"] = support_business_appliance
    # 스타트업 리스트를 선언하고
    startup_list = []
    # 지원서를 작성한 스타트업 하다
    for applied_startup in Appliance.objects.filter(support_business=support_business).values("startup").distinct():
        print(applied_startup)
        # 스타트업 리스트 배열에 추가한다.
        startup_list.append(Startup.objects.get(id=applied_startup["startup"]))
    # 각 필터 배열을 선언한다
    applied_comtype_filter = []
    applied_location_filter = []
    applied_genre_filter = []
    applied_area_filter = []
    result["applied_startup_list"] = []
    # 인덱스가 되는 k 값 초기화
    k = 1
    for startup in startup_list:
        # 해당 스타트업이 선택한 필터 리스트를 모두 가져온다
        filter_list = startup.selected_company_filter_list.all()
        company_kind =""
        local=[]
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                # 기업 형태에 필터를 추가하고,
                applied_comtype_filter.append(filter.filter_name)
                # 회사 종류에 기업 필터를 저장한다.
                company_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                # 소재지 필터에 추가
                applied_location_filter.append(filter.filter_name)
                local.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                # 장르 필터에 추가
                applied_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                # 영역 필터에 추가 한다
                applied_area_filter.append(filter.filter_name)

        ap=Appliance.objects.get(startup=startup, support_business=support_business)
        result["applied_startup_list"].append({
            # 지원서 아이디 - 첨부서류 다운시 필요, 스타트업 아이디, 인덱스 , 대표 메일, 회사 이름, 기업 형태, 소재지, 구성원수, 대표 전화
            "app_id":Appliance.objects.get(support_business=support_business, startup=startup).id,
                "startup_id": startup.id, "update_date":str(ap.appliance_update_at_ymdt),
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "company_local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    # 각 배열을 객체 배열 형태로 카운팅 해서 저장한다.
    result["applied_comtype_filter"] = (organize(applied_comtype_filter))
    result["applied_location_filter"] = (organize(applied_location_filter))
    result["applied_genre_filter"] = (organize(applied_genre_filter))
    result["applied_area_filter"] = (organize(applied_area_filter))



    #  매니저가 작성한 모든 지원사업의 방문 데이터
    #  매니저가 작성한 모든 지원사업
    support_business_mng_arr = SupportBusiness.objects.filter(support_business_author_id=support_business_author_id)
    #  매니저가 작성한 모든 지원사업의 평균 데이터 - 날짜
    support_business_detail_hit_avg_date_ymd = []
    support_business_detail_mng_sum_hit = []
    support_business_detail_mng_avg_hit = []
    # 방문자 로그에서 해당 매니저가 작성한 모든 지원사업과 연결된 방문 로그를 추출
    for date_dict in HitLog.objects.filter(support_business__in=support_business_mng_arr).filter( date__gte= str(support_business.support_business_update_at_ymdt).split(" ")[0] ).values("date").order_by(
            "-date").distinct():
        # 날짜 배열에 해당 날짜가 안들어가 있다면 날짜를 추가한다.
        if date_dict["date"] not in support_business_detail_hit_avg_date_ymd:
            support_business_detail_hit_avg_date_ymd.append(date_dict["date"])
    for date in support_business_detail_hit_avg_date_ymd:
        # 각 날짜 별로 객체 배열을 만들어서 추가한다.
        support_business_detail_mng_sum_hit.append(
            {
                "date": date,
                "number": (HitLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date)).count()
            }
        )
        support_business_detail_mng_avg_hit.append(
            {
                "date": date,
                "number": round((HitLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date).count()) /
                                (SupportBusiness.objects.filter(support_business_author_id=support_business_author_id).exclude(Q(support_business_status="1") | Q(support_business_status="2")).filter(support_business_update_at_ymdt__lte=date).count())
                                ,1)
            }
        )
    # 평균 방문수, 전체 방문수에 추가한다.
    result["support_business_detail_mng_sum_hit"] = support_business_detail_mng_sum_hit
    result["support_business_detail_mng_avg_hit"] = support_business_detail_mng_avg_hit



    # 매니저가 작성한 모든 지원사업에 좋아요를 누른 데이터
    support_business_favorite_date_ymd = []
    support_business_mng_sum_favorite = []
    support_business_mng_avg_favorite = []
    # 좋아요 로그 테이블에서 매니저가 작성항 모든 지원사업과 관련된 로그를 가져온다.
    for date_dict in FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(
            date__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("date").order_by(
            "-date").distinct():
        # 중복되지 않게 날짜 배열 생성
        if date_dict["date"] not in support_business_favorite_date_ymd:
            support_business_favorite_date_ymd.append(date_dict["date"])
    for date in support_business_favorite_date_ymd:
        # 날짜, 좋아요를 누른수 객체를 만들어서 추가한다.
        support_business_mng_sum_favorite.append(
            {
                "date": date,
                "number": (
                    FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date).count())
            }
        )
        support_business_mng_avg_favorite.append(
            {
                "date": date,
                "number": round(
                    (FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date).count()) /
                    (SupportBusiness.objects.filter(
                        support_business_author_id=support_business_author_id).exclude(
                        Q(support_business_status="1") | Q(support_business_status="2")).filter(
                        support_business_update_at_ymdt__lte=date).count())
                    , 1)
            }
        )
    result["support_business_mng_sum_favorite"] = support_business_mng_sum_favorite
    result["support_business_mng_avg_favorite"] = support_business_mng_avg_favorite




    # 매니저가 작성한 모든 지원사업의 지원자 데이터
    support_business_favorite_date_ymd = []
    support_business_mng_sum_appliance = []
    support_business_mng_avg_appliance = []
    for date_dict in Appliance.objects.filter(support_business__in=support_business_mng_arr).dates("appliance_update_at_ymdt","day").filter(
            appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("appliance_update_at_ymdt").order_by(
            "-appliance_update_at_ymdt").distinct():

        if date_dict["appliance_update_at_ymdt"] not in support_business_favorite_date_ymd:
            support_business_favorite_date_ymd.append(date_dict["appliance_update_at_ymdt"])

    for date in support_business_favorite_date_ymd:
        print(  Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date))
        support_business_mng_sum_appliance.append(
            {
                # 중복되지 않은 날짜자 별로 지원서 제출수 객체 를 만든다
                "date": date,
                "number": (
                    Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date)).count()
            }
        )
        print()
        support_business_mng_avg_appliance.append(
            {
                "date": date,
                "number": round(
                    (Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date).count()) /
                    (SupportBusiness.objects.filter(
                        support_business_author_id=support_business_author_id).exclude(
                        Q(support_business_status="1") | Q(support_business_status="2"))).count()
                    , 1)
            }
        )
    result["support_business_mng_sum_appliance"] = support_business_mng_sum_appliance
    result["support_business_mng_avg_appliance"] = support_business_mng_avg_appliance



    #  기관에서  작성한 모든 지원사업의 방문 데이터
    #  매니저가 작성한 모든 지원사업
    ad = AdditionalUserInfo.objects.get(id=support_business_author_id).mng_boss.additionaluserinfo_set.all()
    author_list=[]
    for a in ad:
        author_list.append(a.id)
    support_business_kikwan_arr = SupportBusiness.objects.filter(support_business_author_id__in=author_list)

    support_business_detail_hit_date_ymd = []
    support_business_detail_kikwan_sum_hit = []
    support_business_detail_kikwan_avg_hit = []
    for date_dict in HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter( date__gte= str(support_business.support_business_update_at_ymdt).split(" ")[0] ).values("date").order_by(
            "-date").distinct():
        if date_dict["date"] not in support_business_detail_hit_date_ymd:
            support_business_detail_hit_date_ymd.append(date_dict["date"])
    for date in support_business_detail_hit_date_ymd:
        support_business_detail_kikwan_sum_hit.append(
            {
                "date": date,
                "number": (HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date)).count()
            }
        )
        support_business_detail_kikwan_avg_hit.append(
            {
                "date": date,
                "number": round((HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date).count()) /
                                (SupportBusiness.objects.filter(support_business_author_id__in=author_list).exclude(Q(support_business_status="1") | Q(support_business_status="2"))).count()
                                ,1)
            }
        )
    result["support_business_detail_kikwan_sum_hit"] = support_business_detail_kikwan_sum_hit
    result["support_business_detail_kikwan_avg_hit"] = support_business_detail_kikwan_avg_hit



    # 기관에서 작성한 모든 지원사업에 좋아요를 누른 데이터
    support_business_favorite_date_ymd = []
    support_business_kikwan_sum_favorite = []
    support_business_kikwan_avg_favorite = []
    for date_dict in FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(
            date__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("date").order_by(
            "-date").distinct():
        if date_dict["date"] not in support_business_favorite_date_ymd:
            support_business_favorite_date_ymd.append(date_dict["date"])
    for date in support_business_favorite_date_ymd:
        support_business_kikwan_sum_favorite.append(
            {
                "date": date,
                "number": (
                    FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date)).count()
            }
        )
        support_business_kikwan_avg_favorite.append(
            {
                "date": date,
                "number": round(
                    (FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date)).count() /
                    (SupportBusiness.objects.filter(
                        support_business_author_id__in=author_list).exclude(
                        Q(support_business_status="1") | Q(support_business_status="2")).filter(
                        support_business_update_at_ymdt__lte=date).count())
                    , 1)
            }
        )
    result["support_business_kikwan_sum_favorite"] = support_business_kikwan_sum_favorite
    result["support_business_kikwan_avg_favorite"] = support_business_kikwan_avg_favorite



    # 기관에서 작성한 모든 지원사업의 지원자 데이터
    support_business_favorite_date_ymd = []
    support_business_kikwan_sum_appliance = []
    support_business_kikwan_avg_appliance = []
    for date_dict in Appliance.objects.filter(support_business__in=support_business_kikwan_arr).dates("appliance_update_at_ymdt","day").filter(
            appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("appliance_update_at_ymdt").order_by(
            "-appliance_update_at_ymdt").distinct():

        if date_dict["appliance_update_at_ymdt"] not in support_business_favorite_date_ymd:
            support_business_favorite_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    for date in support_business_favorite_date_ymd:
        print(  Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date))
        support_business_kikwan_sum_appliance.append(
            {
                "date": date,
                "number": (
                    Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date)).count()
            }
        )
        support_business_kikwan_avg_appliance.append(
            {
                "date": date,
                "number": round(
                    (Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date)).count() /
                    (SupportBusiness.objects.filter(
                        support_business_author_id__in=author_list).exclude(
                        Q(support_business_status="1") | Q(support_business_status="2")).count())
                    , 1)
            }
        )
    result["support_business_kikwan_sum_appliance"] = support_business_mng_sum_appliance
    result["support_business_kikwan_avg_appliance"] = support_business_mng_avg_appliance



    # 선정자 추출
    aw_comtype_filter = []
    aw_location_filter = []
    aw_genre_filter = []
    aw_area_filter = []
    aw_startup_list = []
    result["aw_startup_list"] = []
    k = 0
    # 지원사업의 선정자 테이블에서 스타트업아이디를 중복없이 추출
    award = Award.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()
    for aw in award:
        # 선정 스타트업이 선택한 필터를 추출
        filter = Startup.objects.get(id=aw["startup"]).selected_company_filter_list.all()
        company_kind=""
        local=[]
        for f in filter:
            if f.cat_1 == "기업형태":
                aw_comtype_filter.append(f.filter_name)
                company_kind = f.filter_name
            if f.cat_1 == "소재지":
                aw_location_filter.append(f.filter_name)
                local.append(f.filter_name)
            if f.cat_0 == "기본장르":
                aw_genre_filter.append(f.filter_name)
            if f.cat_0 == "영역":
                aw_area_filter.append(f.filter_name)

        startup = Startup.objects.get(id=aw["startup"])
        result["aw_startup_list"].append({
            # 각 데이터로 스타트업 리스트를 만듬
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "company_local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    result["aw_comtype_filter"] = (organize(aw_comtype_filter))
    result["aw_location_filter"] = (organize(aw_location_filter))
    result["aw_genre_filter"] = (organize(aw_genre_filter))
    result["aw_area_filter"] = (organize(aw_area_filter))

    support_business = SupportBusiness.objects.filter(support_business_author_id=request.GET.get("id"))
    q_objects = Q()
    startup_list = []
    for s in support_business:
        q_objects = q_objects | Q(support_business_id=s.id)
    ap = Appliance.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()
    for a in ap:
        startup_list.append(a["startup"])
    support_business_detail_hit = HitLog.objects.filter(
        support_business_id=request.GET.get("support_business_id")).values("user").distinct()
    for h in support_business_detail_hit:
        print(h)
        try:
            if (Startup.objects.filter(user=AdditionalUserInfo.objects.get(id=h["user"]).user)).count() != 0:
                startup_list.append(Startup.objects.get(user=AdditionalUserInfo.objects.get(id=h["user"]).user).id)
        except:
            pass
    award = Award.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()
    for aw in award:
        startup_list.append(aw["startup"])

    # 모든 스타트업 리스트 - 통계에서 전체에 해당하는 부분
    result["all_startup_list"] = []

    all_comtype_filter = []
    all_location_filter = []
    all_genre_filter = []
    all_area_filter = []
    k = 1
    #set 는 리스트에서 중복과 순서를 없애줌
    for id in set(startup_list):
        filter_list = Startup.objects.get(id=id).selected_company_filter_list.all()
        startup = Startup.objects.get(id=id)
        company_kind = ""
        local = []
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                all_comtype_filter.append(filter.filter_name)
                company_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                all_location_filter.append(filter.filter_name)
                local.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                all_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                all_area_filter.append(filter.filter_name)

        result["all_startup_list"].append({
            # 각 데이터로 모든 스타트업의 리스트 생성
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "company_local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    result["all_comtype_filter"] = organize(all_comtype_filter)
    result["all_location_filter"] = organize(all_location_filter)
    result["all_genre_filter"] = organize(all_genre_filter)
    result["all_area_filter"] = organize(all_area_filter)



    # 위의 결과를 테이블에 만들어서 스트링 형태로 저장해 놓고 사용자한테 매번 연산을 거치지 않게 해서 보여주려고 하였었음.
    # 과거 프로토 버전 구현하고 나서 현재 수정되면서 수정된 부분 반영안되어있음
    # st = StatTable()
    # st.stat_user_id = request.GET.get("stat_user_id")
    # support_business = SupportBusiness.objects.get(id=request.GET.get("support_business_id"))
    # if support_business.support_business_status != 5 and support_business.support_business_author_id  == request.GET.get("id"):
    #     st.stat_name = "my_support_business_ing"
    # elif support_business.support_business_status == 5 and support_business.support_business_author_id  == request.GET.get("id"):
    #     st.stat_name = "my_support_business_end"
    # elif support_business.support_business_status != 5 and support_business.support_business_author_id != request.GET.get("id"):
    #     st.stat_name = "other_support_business_ing"
    # elif support_business.support_business_status == 5 and support_business.support_business_author_id  != request.GET.get("id"):
    #     st.stat_name = "other_support_business_end"



    # result_json = JsonResponse(result)
    # st.stat_json  =result_json.content
    # st.save()

    return JsonResponse(result)





@csrf_exempt
@my_timer
def show_from_stattable(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    my_stat_id = request.GET.get("id")
    my_stat_page =request.GET.get("page")

    st = StatTable.objects.filter(stat_user_id=my_stat_id).filter(stat_name=my_stat_page).order_by("-stat_timestamp")[0]
    
    
    
    # if  my_stat_page=="2":
    #     st = StatTable.objects.filter(stat_user_id=my_id).filter(stat_name="my_support_business_end").order_by("-stat_timestamp")[0]
    # if  my_stat_page=="3":
    #     st = StatTable.objects.all().exclude(stat_user_id=my_id).filter(stat_name="other_support_business_ing").order_by("-stat_timestamp")[0]
    # if  my_stat_page=="4":
    #     st = StatTable.objects.all().exclude(stat_user_id=my_id).filter(stat_name="other_support_business_end").order_by("-stat_timestamp")[0]
    #TODO: STAT 페이지 참고

    result = st.stat_json
    return HttpResponse(result)


# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_by_kikwan_1(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business_list = []
    support_business_list = []
    for sp in SupportBusiness.objects.filter(support_business_status="3",
                                             support_business_apply_end_ymdt__gte=timezone.now()).select_related(
                                                "support_business_author"):
        support_business_list.append({
            "author": sp.support_business_author.mng_name,
            "author_id": sp.support_business_author.id,
            "name": sp.support_business_name,
            "support_business_id": sp.id,
            "support_business_status": sp.support_business_status
        })
    return JsonResponse(support_business_list, safe=False)
# 수정전
# 쿼리수 : 6
# vue_get_support_business_select_name_by_kikwan_1 함수가 실행된 총 시간: 0.16927003860473633 초
# db 쿼리 시간 :  0.17 초
# 쿼리 제외한 연산 시간 :  0.0007299613952636841 초
# 수정후
# 쿼리수: 1
# vue_get_support_business_select_name_by_kikwan_1 함수가 실행된 총 시간: 0.015623331069946289 초
# db 쿼리 시간 :  0.016 초
# 쿼리 제외한 연산 시간 :  0.00037666893005371127 초


# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_by_kikwan_2(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business_list=[]
    for sp in SupportBusiness.objects.filter(support_business_apply_end_ymdt__lte=timezone.now() ).filter( Q(support_business_status="3") |  Q(support_business_status="5") | Q(support_business_status="4") ):
        support_business_list.append({
            "author":sp.support_business_author.mng_name,
            "author_id": sp.support_business_author.id,
            "name":sp.support_business_name,
            "support_business_id":sp.id,
            "support_business_status":sp.support_business_status
            })

    return JsonResponse(support_business_list, safe=False)


#--- (중복 3/3)
# --------(통계) (매니저) 통계 홈화면에서 드롭다운으로 지원사업을 선택하면, 해당 지원사업 통계를 계산해주는 함수
# --------[8.통계 페이지,지원사업 통계 데이터 추출  기능 // 기관관리자, 매니저: 통계 페이지에서 호출됨]-----------------
# // todo 통계 정보를 매번 계산하는 현재 방법 > 미리 계산해두고 정보를 json 파일로 가지고 있어서 보여주는 것으로 짜기(at least 매 2시간마다 실행/5분단위여도 좋음)

#--- 통계 정리 : 사업별통계 > 진행중 사업: auth = "mng"/ / my "gca_id = support_business_author.id"// ing = satatus = "3"
# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_1(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result

    mng = AdditionalUserInfo.objects.get(id=user_auth_id)
    support_business_list = []
    for sp in SupportBusiness.objects.filter(support_business_author=mng).filter(support_business_status__in=["3"]).filter(support_business_apply_end_ymdt__gte=timezone.now()):#.filter(support_business_apply_end_ymdt__gte=timezone.now()):
        support_business_list.append({
            "author": sp.support_business_author.mng_name,
            "name":sp.support_business_name,
            "support_business_id":sp.id,
            "support_business_status": sp.support_business_status
        })
    return JsonResponse(support_business_list, safe=False)


#--- 통계 정리 : 사업별통계 > 진행중 사업: auth = "mng"/ / my "gca_id = support_business_author.id"// end = satatus = "4"|"5"
# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_2(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    mng = AdditionalUserInfo.objects.get(id=user_auth_id)
    support_business_list = []

    for sp in SupportBusiness.objects.filter(support_business_author=mng).filter(Q(support_business_status="4")|Q(support_business_status="5")|Q(support_business_status="3")).filter(support_business_apply_end_ymdt__lte=timezone.now()):
        print(sp.support_business_name)
        support_business_list.append({
            "author": sp.support_business_author.mng_name,
            "name":sp.support_business_name,
            "support_business_id":sp.id,
            "support_business_status": sp.support_business_status
            })

    return JsonResponse(support_business_list, safe=False)

#--- 통계 정리 : 사업별통계 > 진행중 사업: auth = "mng"/ / my "gca_id  != support_business_author.id"// ing = satatus = "3"
# ------ postman정상작동
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_3(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    mng = AdditionalUserInfo.objects.get(id=user_auth_id)
    support_business_list = []
    for sp in SupportBusiness.objects.exclude(support_business_author=mng).filter( Q(support_business_status="3")).filter(support_business_apply_end_ymdt__gte=timezone.now()):
        support_business_list.append({
            "name":sp.support_business_name,
            "author": sp.support_business_author.mng_name,
            "support_business_id":sp.id,
            "support_business_status": sp.support_business_status
        })
    return JsonResponse(support_business_list, safe=False)


#--- 통계 정리 : 사업별통계 > 진행중 사업: auth = "mng"/ / my "gca_id  != support_business_author.id"// end = satatus = "4"|"5"
@csrf_exempt
@my_timer
def vue_get_support_business_select_name_4(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    support_business_list = []
    mng = AdditionalUserInfo.objects.get(id=user_auth_id)
    for sp in SupportBusiness.objects.exclude(support_business_author = mng).filter(Q(support_business_status="4")|Q(support_business_status="5")|Q(support_business_status="3")).filter(support_business_apply_end_ymdt__lte=timezone.now()):
        support_business_list.append({
            "name":sp.support_business_name,
            "author": sp.support_business_author.mng_name,
            "support_business_id":sp.id,
            "support_business_status": sp.support_business_status
        })

    return JsonResponse(support_business_list, safe=False)

@csrf_exempt
@my_timer
def excel_down_statics(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=statics_list.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')
    list = request.GET.get("startup_list").split(",")
    startup_list=[]
    for list_item in list:
        startup_list.append(Startup.objects.get(id=list_item))
    index=0;
    for  startup  in startup_list:
        ws.write(index, 0 ,index+1)
        ws.write(index, 1, startup.mark_email)
        ws.write(index, 2, startup.company_name)
        company_kind=""
        local=[]
        for filter in startup.selected_company_filter_list.all():
            if filter.cat_1=="기업형태":
                company_kind = filter.filter_name
            if filter.cat_1=="소재지":
                local.append(filter.filter_name)
        ap=Appliance.objects.filter(startup=startup, support_business_id = request.GET.get("support_business_id")).order_by("-id").first()

        ws.write(index, 3, company_kind)
        ws.write(index, 4  , ",".join(local) )
        ws.write(index, 5, startup.company_total_employee)
        ws.write(index, 6, startup.mark_tel)
        try:
            ws.write(index, 7, str(ap.appliance_update_at_ymdt))
        except:
            ws.write(index, 7, '')
        index=index+1
    wb.save(response)
    return response


#--------------------------------------------- 중복 정리 시작 ----------------------------------------------------------

#--------------------------------------------- 중복 정리 완료 ----------------------------------------------------------





# --------(통계) (매니저) (백단) 태그리스트를 숫자로 반환 > 태그가 몇개씩 있는지 세고, 파이그래프 생성
def organize(arr):
    result_list=[]
    for k, v in itertools.groupby(sorted(arr)):
        obj={}
        result = list(v)
        obj[result[0]] = len(result)
        result_list.append(copy.deepcopy(obj))
    return result_list



# --------(통계) 유저 통계 페이지, 경기지역모아보기 등
# --------[유저 통계 페이지, 유저 값 계산 ]-------
@csrf_exempt
@my_timer
def vue_static_usr(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    #총기업수
    total_startup = (Startup.objects.all()).count()
    #총 개인회원수
    total_usr = (AdditionalUserInfo.objects.exclude(auth=5).exclude(auth=4)).count()
    #기업회원 1개당 평균 사업 참가수
    avg_apply_num_per_startup = round((Appliance.objects.all()).count()/total_startup,2)
    #기업 회원 한개당 평균 사업 선정수
    avg_award_num_per_startup = round((Award.objects.all().count())/total_startup,2)


    ## 최종 선정기업
    # 총 기업회원수
    total_awarded_startup = (Award.objects.all().values('startup_id').distinct()).count()
    #기업회원 1개당 평균 사업 참가수
    k=0;
    apply_num_arr =[]
    for startup in Award.objects.all().values('startup_id').distinct():
        #k = k + len(Award.objects.filter(startup_id=startup["startup_id"]))
        apply_num_arr.append((Award.objects.filter(startup_id=startup["startup_id"])).count())
    if len(apply_num_arr) > 0:
        avg_apply_num_per_awarded= sum(apply_num_arr)/len(apply_num_arr)
    else:
        avg_apply_num_per_awarded=0
    if(total_awarded_startup !=0):
        avg_award_num_per_awarded = len( Award.objects.all()) / total_awarded_startup
    else:
        avg_award_num_per_awarded = 0
    #경기지역 모아보기
    total_startup_gg = (Startup.objects.filter(  selected_company_filter_list__filter_name__contains="경기"))
    k=0;
    startup_list = []
    for startup in (Startup.objects.filter( selected_company_filter_list__filter_name__contains="경기")):
        k = k + (Award.objects.filter(startup=startup).count())
        startup_list.append(startup.id)
        startup_list.append(startup.id)
    apply_num_startup_gg_arr=[]

    #경기 지역 회사가 모든 사업에 참가한 횟수
    total_appliance_gg = Appliance.objects.filter(startup__in=total_startup_gg)

     # 모든 사업의 선정자수
    total_award_num = Award.objects.all()

    if len(total_appliance_gg) > 0 :
        # 경기 기업회원 1개당 평균 사업 참가수
        avg_apply_num_per_startup_gg = round(len(total_appliance_gg)/len(total_startup_gg),2)

        # 경기 기업 회원 1개당 평균 사업 선정수
        avg_award_num_per_awarded_gg = round(len(total_award_num)/len(total_startup_gg),2)
    else:
        avg_apply_num_per_startup_gg = 0
        avg_award_num_per_awarded_gg = 0




    result={}
    result["total_startup"]= total_startup
    result["total_usr"]=total_usr
    result["avg_apply_num_per_startup"]= round(avg_apply_num_per_startup,2)
    result["avg_award_num_per_startup"]=round(avg_award_num_per_startup,2)

    result["total_awarded_startup"] = (total_awarded_startup)
    result["avg_apply_num_per_awarded"] = round(avg_apply_num_per_awarded,2)
    result["avg_award_num_per_awarded"] = round(avg_award_num_per_awarded,2)

    result["total_startup_gg"]= len(total_startup_gg)
    result["avg_apply_num_per_startup_gg"]= round(avg_apply_num_per_startup_gg,2)
    result["avg_award_num_per_awarded_gg"] =round(avg_award_num_per_awarded_gg,2)

    return JsonResponse(result)



#------- (통계)
@csrf_exempt
@my_timer
def vue_get_short_title(request):
    support_business_name = SupportBusiness.objects.get(id=request.GET.get("id")).support_business_name
    return JsonResponse({"support_business_name":support_business_name})









#----------------------------------------------------------------------------------------------------------------------
# 파. 참여기업 리스트 만들기
# 종료된 공고 그래프 하단, 참여한 기업이 리스트 형태로 나타나야 함
#----------------------------------------------------------------------------------------------------------------------

# --------(리스트) (매니저) (기관관리자) 유저관리> 사업참여기업 탭
# --------[선정자 리스트 조회 ]-----------------------------------------------------------------------------
# todo :  선정여부 Y/N 분기문 만들어서 한번에 관리하는 함수로 거듭나자!

@csrf_exempt
@my_timer
def vue_get_awarded(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business_id=request.GET.get("support_business_id")
    win_list = Award.objects.filter(support_business_id=support_business_id)
    winner=[]
    k=1

    for a_w in win_list:
        ap , created = Appliance.objects.get_or_create(support_business_id=support_business_id, startup =a_w.startup )
        print(ap)
        winner.append({
           "index":k,
            "company_id":a_w.startup.id,
            "company_name":a_w.startup.company_name,
            "mark_name" : a_w.startup.mark_name,
            "company_kind":a_w.startup.company_kind,
            "user_id":a_w.startup.mark_email,
            "mark_tel": a_w.startup.mark_tel,
            "mark_email": a_w.startup.mark_email,
            "appliance_update_at_ymdt": str(ap.appliance_update_at_ymdt)
        })
        k=k+1
    support_business = SupportBusiness.objects.get(id=support_business_id)
    # support_business.support_business_status = 5
    # support_business.save()

    return JsonResponse(winner,safe=False)



@csrf_exempt
@my_timer
def opr_vue_get_awarded(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    support_business_id=request.GET.get("support_business_id")
    win_list = Award.objects.filter(support_business_id=support_business_id)
    winner=[]
    k=1

    for a_w in win_list:
        ap , created = Appliance.objects.get_or_create(support_business_id=support_business_id, startup =a_w.startup )
        print(ap)
        winner.append({
            "id":a_w.startup.id,
           "opr_index":k, "opr_company_name":a_w.startup.company_name, "opr_mark_name" : a_w.startup.mark_name,"opr_company_kind":a_w.startup.company_kind, "opr_user_id":a_w.startup.user.username,
            "opr_mark_tel": a_w.startup.mark_tel,  "opr_mark_email": a_w.startup.mark_email, "opr_appliance_update_at_ymdt": str(ap.appliance_update_at_ymdt).split("T")[0]
        })
        k=k+1
    support_business = SupportBusiness.objects.get(id=support_business_id)
    # support_business.support_business_status = 5
    # support_business.save()

    return JsonResponse(winner,safe=False)











# --------(홈화면) / (스타트업) (매니저) (기관관리자) : 스타트업 홈화면
# --------[스타트업 홈화면]---------------------------------------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_startup_list(request):
    print("here")
    startup = Startup.objects.exclude(company_name=None).exclude(company_name="")
    result = []
    for s in startup:
        temp_obj={}
        temp_obj["company_name"] = s.company_name
        temp_obj["logo"] = s.logo
        temp_obj["company_short_desc"] = s.company_short_desc
        temp_obj["is_favored"] = is_in_favor_list( "startup",s.id, user_auth_id)
        temp_obj["filter"] = []

        temp_obj["id"]=s.id
        for t in s.selected_company_filter_list.all():
            if t.filter_name != "" and t.filter_name != None:
                print(t.filter_name)
                if t.cat_1 == "기업형태":
                    print(t.filter_name)
                if t.cat_0 != "지원형태" and t.cat_1!="기업형태":
                    temp_obj["filter"].append(t.filter_name)

        result.append(copy.deepcopy(temp_obj))

    return  JsonResponse(list(result), safe=False)


# --------(스타트업) (매니저) (기관관리자) : 스타트업 상세 정보페이지
# --------[스타트업 상세 정보페이지 ]-----------------------------------------------------------------------------------





# --------(리스트) (매니저) (기관관리자) : 유저 회원 관리 페이지--------------------------------------------------------
# --------[유저 회원 관리,  스타트업 계정 정보 가져오기  ]--------------------------------------------------------------
@csrf_exempt
@my_timer
def vue_get_startup_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    startup= Startup.objects.all()
    result = {}
    k=1
    startup_set=[]
    for s in startup :
        temp={}
        temp["index"]=k
        k=k+1
        temp["company_name"] = s.company_name
        temp["id"] = s.user.username

        temp["repre_name"] = s.user.startup.repre_name
        temp["repre_tel"] = s.user.additionaluserinfo.repre_tel

        temp["repre_email"] = s.repre_email if s.user.additionaluserinfo.repre_email !="" else  s.user.username
        tag_list=[]
        for t in s.selected_company_filter_list.all():
            tag_list.append(t.filter_name)
        temp["tag"] = tag_list
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
        temp["local"] = local
        temp["employ_num"] = s.company_total_employee
        temp["apply_num"] = (Appliance.objects.filter(startup=s)).count()
        temp["award_num"] = (Award.objects.filter(startup=s)).count()
        temp["join"] = s.user.date_joined
        temp["tag"]=[]
        for t in s.selected_company_filter_list.all():
            temp["tag"].append(t.filter_name)
        startup_set.append(copy.deepcopy(temp))
    result["startup"] = startup_set
    user_ad = AdditionalUserInfo.objects.exclude(auth=4).exclude(auth=5)
    p=1
    user_set = []
    p=1
    for u in user_ad:
        try:
            user={}
            #user["index"]=p
            p=p+1
            print(u.user)
            user["id"] = u.user.username
            user["repre_name"] = Startup.objects.get(user=u.user).repre_name
            user["repre_tel"] =  Startup.objects.get(user=u.user).repre_tel
            user["joined"] = u.user.date_joined
            user_set.append(copy.deepcopy(user))

        except:
            pass
        result["usr_set"] = user_set

    ## 사업 참여 기업
    aw_startup_set = Appliance.objects.all().values("startup").distinct()
    k=1
    ap_set = []
    for s in aw_startup_set:

        aw_st={}
        print(s)
        startup = Startup.objects.get(id=s["startup"])
        aw_st["index"] = k
        k=k+1
        aw_st["company_name"] = startup.company_name
        aw_st["repre_name"] = startup.repre_name
        aw_st["repre_tel"] = startup.repre_tel
        tag_list = []
        for t in startup.selected_company_filter_list.all():
            tag_list.append(t.filter_name)
        aw_st["tag"] = tag_list
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
        aw_st["local"] = local


        aw_st["support_business_name"] = Appliance.objects.filter(startup=startup).last().support_business.support_business_name
        if (Award.objects.filter(support_business=Appliance.objects.filter(startup=startup).last().support_business).filter(startup=startup)).count() == 0 :
            aw_st["awarded"] = "탈락"
        else:
            aw_st["awarded"] = "선정"
        aw_st["end_date"] = str(Appliance.objects.filter(startup=startup).last().support_business.support_business_apply_end_ymdt).split(" ")[0]
        ap_set.append(copy.deepcopy(aw_st))
    result["ap_set"] = ap_set
    return JsonResponse(result)

@csrf_exempt
@my_timer
def opr_vue_get_startup_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    startup= Startup.objects.all()
    result = {}
    k=1
    startup_set=[]
    for s in startup :
        temp={}
        temp["opr_index"]=k
        k=k+1
        temp["opr_company_name"] = s.company_name
        temp["opr_id"] = s.user.username
        temp["opr_startup_id"] = s.id

        temp["opr_repre_name"] = s.user.startup.repre_name
        temp["opr_repre_tel"] = s.user.additionaluserinfo.repre_tel

        temp["opr_repre_email"] = s.repre_email if s.user.additionaluserinfo.repre_email !="" else  s.user.username
        tag_list=[]
        for t in s.selected_company_filter_list.all():
            tag_list.append(t.filter_name)
        temp["opr_tag"] = tag_list
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
        temp["opr_local"] = local
        temp["opr_employ_num"] = s.company_total_employee
        temp["opr_apply_num"] = (Appliance.objects.filter(startup=s)).count()
        temp["opr_award_num"] = (Award.objects.filter(startup=s)).count()
        temp["opr_join"] = s.user.date_joined
        temp["opr_tag"]=[]
        for t in s.selected_company_filter_list.all():
            temp["opr_tag"].append(t.filter_name)
        startup_set.append(copy.deepcopy(temp))
    result["opr_startup"] = startup_set
    user_ad = AdditionalUserInfo.objects.exclude(auth=4).exclude(auth=5)

    user_set = []
    p=1
    for u in user_ad:
        try:
            user = {}
            user["opr_id"] = u.user.username
            user["opr_repre_name"] = Startup.objects.get(user=u.user).repre_name
            user["opr_repre_tel"] = Startup.objects.get(user=u.user).repre_tel
            user["opr_joined"] = u.user.date_joined

            user["opr_index"]=p
            p=p+1
            print(u.user)


            user_set.append(copy.deepcopy(user))

        except Exception as e:
            print(e)
            pass
        result["opr_usr_set"] = user_set

    ## 사업 참여 기업
    aw_startup_set = Appliance.objects.all().values("startup").distinct()
    k=1
    ap_set = []
    for s in aw_startup_set:

        aw_st={}
        print(s)
        startup = Startup.objects.get(id=s["startup"])
        aw_st["opr_index"] = k
        k=k+1
        aw_st["opr_company_name"] = startup.company_name
        aw_st["opr_repre_name"] = startup.repre_name
        aw_st["opr_startup_id"] = startup.id
        aw_st["opr_repre_tel"] = startup.repre_tel
        tag_list = []
        for t in startup.selected_company_filter_list.all():
            tag_list.append(t.filter_name)
        aw_st["opr_tag"] = tag_list
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
        aw_st["opr_local"] = local


        aw_st["opr_support_business_name"] = Appliance.objects.filter(startup=startup).last().support_business.support_business_name
        if (Award.objects.filter(support_business=Appliance.objects.filter(startup=startup).last().support_business).filter(startup=startup)).count() == 0 :
            aw_st["opr_awarded"] = "N"
        else:
            aw_st["opr_awarded"] = "Y"
        aw_st["opr_end_date"] = str(Appliance.objects.filter(startup=startup).last().support_business.support_business_apply_end_ymdt).split(" ")[0]
        ap_set.append(copy.deepcopy(aw_st))
    result["opr_ap_set"] = ap_set
    return JsonResponse(result)


# ------ postman정상작동
@csrf_exempt
@my_timer
def get_favorite_support_business_list(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    ad = AdditionalUserInfo.objects.get(id=user_auth_id)
    result={}
    result["support_business_set"] = []
    for support_business in ad.favorite.exclude(support_business_status=None).order_by("-support_business_apply_end_ymdt"):
        team={}
        team["support_business_name"] = support_business.support_business_name
        team["is_favored"] = True
        team["support_business_name"] = support_business.support_business_name
        team["support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        team["support_business_short_desc"] = support_business.support_business_short_desc
        team["selected_support_business_filter_list"]=[]
        for f in support_business.selected_support_business_filter_list.all():
            team["selected_support_business_filter_list"].append(f.filter_name)
        team["support_business_poster"]= support_business.support_business_poster
        team["id"] = support_business.id
        result["support_business_set"].append(copy.deepcopy(team))
    return JsonResponse(result)





#------[ 중복 그룹 7 ]----def 2개 중복------------------------------------------------------------------------------------
# # 메인 홈화면, 지원서 3개씩 랜덤하게 보여주는 경우 사용
# # --------[]-------
@csrf_exempt
@my_timer
def get_home_info(request):

    check_result = gca_check_session(request)
    user_auth_id=""
    if check_result != False:
        user_auth_id =  check_result
    gr = SupportBusiness.objects.filter(support_business_status=3).filter(support_business_apply_end_ymdt__gte=timezone.now()).order_by("-support_business_update_at_ymdt")[:6] #.filter(  Q(support_business_status=3)|Q(support_business_status=4)|Q(support_business_status=5)).filter(support_business_apply_start_ymd__lte=datetime.now()).order_by("?")[:6]
    result={}
    result["support_business_set"] = []
    for g in gr:
        team={}
        team["support_business_name"] = g.support_business_name
        team["support_business_apply_end_ymdt"] = g.support_business_apply_end_ymdt
        team["support_business_short_desc"] = g.support_business_short_desc
        team["selected_support_business_filter_list"]=[]
        for f in g.selected_support_business_filter_list.all():
            team["selected_support_business_filter_list"].append(f.filter_name)
        team["support_business_poster"]= g.support_business_poster
        try:
            team["is_favored"] = is_in_favor_list("support_business",g.id, user_auth_id)
        except Exception as e :
            print(e)
            team["is_favored"] = ""
        team["id"] = g.id
        result["support_business_set"].append(copy.deepcopy(team))
    result["startup_set"] = []

    startup = Startup.objects.exclude(company_name="").exclude(company_name=None).order_by("?")[:3]

    for s in startup:
        temp_obj = {}
        temp_obj["company_name"] = s.company_name
        temp_obj["company_short_desc"] = s.company_short_desc
        temp_obj["logo"] = s.logo

        temp_obj["is_favored"] = is_in_favor_list("startup", s.id, user_auth_id)

        temp_obj["tag"] = []
        temp_obj["id"] = s.id
        temp_obj["filter"] = []
        temp_obj["filter"] = []

        for t in s.selected_company_filter_list.all():
            if t.cat_0 != "지원형태" and t.cat_1 != "기업형태":
                temp_obj["filter"].append(t.filter_name)

        result["startup_set"].append(copy.deepcopy(temp_obj))

    result["clip"] = []
    for c in Clip.objects.all().order_by("-id")[:3]:
        temp={}
        temp["clip_id"] = c.id
        try:
            temp["clip_user"]=c.clip_user.user.startup.mark_name
        except:
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_thumb"]=c.clip_thumb
        temp["clip_title"]=c.clip_title
        temp["clip_play"]=c.clip_play
        temp["clip_created_at"]=c.clip_created_at
        temp["clip_info"] = c.clip_info
        temp["clip_tag"] =[]
        temp["is_favored"] = is_in_favor_list( "clip", c.id  , user_auth_id )
        temp["clip_entry_point"] ="/channel/clip/view/"+str(c.id)
        # 채널 통계에서 사용되는 레이블과 value
        temp["label"] = c.clip_title
        temp["value"] = c.id

        temp["tag"]=[]
        for t in c.clip_filter.all()  :
            temp["tag"].append(t.name)
        result["clip"].append(copy.deepcopy(temp))

    result["course"]=[]
    for c in Course.objects.all().order_by("-id")[:3]:
        temp = {}
        temp["id"] = c.id
        try:
            print(0)
            temp["course_entry_point"] = "/channel/course/view/" + str(c.id) + "/" + str(
                c.course_clips.all().first().id)
        except Exception as e:
            print(e)
            print(c.course_clips.all())
            print(c.course_clips.all().first())
            temp["course_entry_point"] = ""
        try:
            temp["course_user"] = c.course_user.user.startup.mark_name
        except:
            temp["course_user"] = c.course_user.mng_name
        temp["course_thumb"] = c.course_thumb
        temp["course_id"] = c.id
        temp["label"] = c.course_title
        temp["value"] = c.id
        temp["is_favored"] = is_in_favor_list("course", c.id, user_auth_id)

        temp["course_title"] = c.course_title
        temp["course_rec_dur"] = c.course_rec_dur
        temp["course_created_at"] = c.course_created_at
        temp["course_info"] = c.course_info
        temp["course_tag"] = []
        temp["course_total_play"] = c.course_total_play
        for t in c.course_filter.all():
            temp["course_tag"].append(t.name)
        result["course"].append(copy.deepcopy(temp))

    result["path"] = []
    for c in Path.objects.all().order_by("-id"):
        temp = {}
        temp["id"] = c.id
        try:
            temp["path_entry_point"] = "/channel/path/view/" + str(c.id) + "/" + str(
                c.path_course.all().first().id) + "/" + str(c.path_course.first().course_clips.all().first().id)
        except Exception as e:
            print(e)
            temp["path_entry_point"] = ""
        try:
            temp["path_user"] = c.path_user.user.startup.mark_name
        except:
            temp["path_user"] = c.path_user.mng_name
        temp["path_thumb"] = c.path_thumb
        temp["path_title"] = c.path_title
        temp["path_rec_dur"] = c.path_rec_dur
        temp["label"] = c.path_title
        temp["value"] = c.id

        temp["is_favored"] = is_in_favor_list("path", c.id, user_auth_id)

        temp["path_total_play"] = c.path_total_play
        temp["path_id"] = c.id
        temp["path_created_at"] = c.path_created_at
        temp["path_info"] = c.path_info
        temp["path_tag"] = []
        for t in c.path_filter.all():
            temp["path_tag"].append(t.name)
        result["path"].append(copy.deepcopy(temp))



    return JsonResponse(result)

#---- (중복)
# --------[스타트업 리스트 샘플 페이지]-------


#------[ 중복 그룹 ]----------------------------------------------------------------------------------------------------





def handle_uploaded_file_movie(file, filename, user_id):
    print('media/uploads/user/'+ str(user_id) +'/company/movie/')
    if not os.path.exists('media/uploads/user/'+ str(user_id) +'/company/movie/'):
        os.makedirs('media/uploads/user/' + str(user_id) + '/company/movie')
    with open('media/uploads/user/'+ str(user_id) +'/company/movie/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return 'media/uploads/user/'+ str(user_id) +'/company/movie/'+filename



@csrf_exempt
@my_timer
def add_favorite_support_business(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business_id"))
    result = ""
    if support_business not in usr.favorite.all() :
        usr.favorite.add(support_business)
        FavoriteLog(user_id=user_id, support_business_id=support_business.id , date= timezone.now()).save()
        result="add"

    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def remove_favorite_support_business(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business_id"))
    print(support_business.id)
    result = ""
    if support_business in usr.favorite.all() :
        usr.favorite.remove(support_business)
        FavoriteLog.objects.filter(user_id=user_id).filter(support_business_id=support_business.id).delete()
        result="remove"


    return JsonResponse({"result":result})



@csrf_exempt
@my_timer
def add_favorite_path(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    path = Path.objects.get(id=request.GET.get("path_id"))
    result = ""
    if path not in usr.favorite_path.all() :

        usr.favorite_path.add(path)
        FavoriteLog(user_id=user_id, path_id=path.id , date= timezone.now()).save()
        result="add"
    return JsonResponse({"result":result})


@csrf_exempt
@my_timer
def remove_favorite_path(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    path = Path.objects.get(id=request.GET.get("path_id"))
    result = ""
    if path in usr.favorite_path.all() :
        usr.favorite_path.remove(path)
        FavoriteLog.objects.filter(user_id=user_id).filter( path_id=path.id).delete()
        result="remove"
    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def add_favorite_course(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    course = Course.objects.get(id=request.GET.get("course_id"))
    result = ""
    if course not in usr.favorite_course.all() :
        usr.favorite_course.add(course)
        FavoriteLog(user_id=user_id, course_id=course.id , date= timezone.now()).save()
        result="add"

    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def remove_favorite_course(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    course = Course.objects.get(id=request.GET.get("course_id"))
    result = ""
    if course in usr.favorite_course.all() :
        usr.favorite_course.remove(course)
        FavoriteLog.objects.filter(user_id=user_id).filter( course_id=course.id).delete()
        result="remove"
    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def add_favorite_clip(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    clip = Clip.objects.get(id=request.GET.get("clip_id"))
    result = ""
    if clip not in usr.favorite_clip.all() :

        usr.favorite_clip.add(clip)
        FavoriteLog(user_id=user_id, clip_id=clip.id , date= timezone.now()).save()
        result="add"

    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def remove_favorite_clip(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
        user_auth_id =  check_result
    user_id = user_auth_id
    usr = AdditionalUserInfo.objects.get(id=user_id)
    clip = Clip.objects.get(id=request.GET.get("clip_id"))
    result = ""
    if clip in usr.favorite_clip.all() :
        usr.favorite_clip.remove(clip)
        FavoriteLog.objects.filter(user_id=user_id).filter( clip_id=clip.id).delete()
        result="remove"
    else:
        usr.favorite_clip.add(clip)
        FavoriteLog(user_id=user_id, clip_id=clip.id , date= timezone.now()).save()
        result="add"

    return JsonResponse({"result":result})


@csrf_exempt
@my_timer
def vue_hit_clip_log(request):

    clip = Clip.objects.get(id=request.POST.get("val"))
    try:
        ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    except:
        ad=None
    HitClipLog.objects.get_or_create(hit_clip=clip, hit_clip_user=ad)
    return JsonResponse({"result": "ok"})

@csrf_exempt
@my_timer
def vue_watch_history(request):
    WatchHistory(
        watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id")), watch_course_id=request.POST.get("course_id"),
        watch_path_id=request.POST.get("path_id"), watch_clip_id=request.POST.get("clip_id")
    ).save()
    return JsonResponse({"result":"ok"})
@csrf_exempt
@my_timer
def vue_channel_process_check(request):
    print(request.POST)
    if request.POST.get("path_id"):
        WatchHistory(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id")),watch_path_id=request.POST.get("path_id")).save()
        origin_length = int(Path.objects.get(id=request.POST.get("path_id")).path_total_play)
        view_num = (WatchHistory.objects.filter(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id")))\
            .filter(watch_path_id=request.POST.get("path_id"))).count()*6
        per = view_num*100 / origin_length
        return  JsonResponse({"result":per})
    if request.POST.get("course_id"):
        WatchHistory(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id")), watch_course_id=request.POST.get("course_id")).save()
        origin_length = int(Course.objects.get(id=request.POST.get("course_id")).course_total_play)
        view_num = (
            WatchHistory.objects.filter(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id"))) \
            .filter(watch_course_id=request.POST.get("course_id"))).count() * 6
        per = view_num * 100 / origin_length
        return JsonResponse({"result": per})
    if request.POST.get("clip_id"):
        WatchHistory(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id")), watch_clip_id=request.POST.get("clip_id")).save()
        origin_length = int(Clip.objects.get(id=request.POST.get("clip_id")).clip_play)
        view_num = (
            WatchHistory.objects.filter(watch_user=AdditionalUserInfo.objects.get(id=request.POST.get("id"))) \
            .filter(watch_clip_id=request.POST.get("clip_id"))).count() * 6
        per = view_num * 100 / origin_length
        return JsonResponse({"result": per})

@csrf_exempt
@my_timer
def vue_hit_course_log(request):
    clip = Clip.objects.get(id=request.POST.get("val"))
    try:
        ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    except:
        ad=""
    course = Course.objects.get(id=request.POST.get("course_id"))
    HitCourseLog.objects.get_or_create(hit_course_clip=clip, hit_course_user=ad, hit_course= course)
    return  JsonResponse({"result":"ok"})


@csrf_exempt
@my_timer
def vue_hit_path_log(request):

    clip = Clip.objects.get(id=request.POST.get("val"))
    try:
        ad = AdditionalUserInfo.objects.get(id=request.POST.get("id"))
    except:
        ad=""
    course = Course.objects.get(id=request.POST.get("course"))
    path = Path.objects.get(id=request.POST.get("path"))
    HitPathLog.objects.get_or_create(hit_path_clip=clip, hit_path_user=ad, hit_path_course= course,hit_path=path)
    return JsonResponse({"result":"ok"})



@csrf_exempt
@my_timer
def vue_get_ing_lecture(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    result={}
    result["path_list"] = []
    for p in HitPathLog.objects.filter(user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
        t={}
        t["clip_title"]=p.path.title
        t["id"]=p.path.id
        t["created"] = p.path.created_at
        t["user"] = p.path.user.repre_name
        t["play"] = p.path.total_play
        t["clip_thumb"] = p.path.clip_thumb
        t["entry_point"] = "/path/view/"+str(p.path.id) + "/" + str(p.course.id) + "/" + str(p.clip.id)

        result["path_list"].append(copy.deepcopy(t))
    result["course_list"] =[] # = HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id").values()[:3]
    for p in HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
        t={}
        t["clip_title"]=p.course.title
        t["id"]=p.course.id
        t["created"] = p.course.created_at
        t["user"] = p.course.user.repre_name
        t["play"] = p.course.total_play
        t["clip_thumb"] = p.course.clip_thumb
        t["entry_point"] = "/course/view/"+str(p.course.id) + "/"+str(p.clip.id)
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id").values()[:3]
    for p in HitClipLog.objects.filter(user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
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
@my_timer
def vue_get_favorite_channel(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    result={}
    result["clip_list"] = []
    result["course_list"]=[]
    result["path_list"] = []

    for p in AdditionalUserInfo.objects.get(id=user_auth_id).favorite_path.all():
        t={}
        t["path_title"]=p.path_title
        t["id"]=p.id
        t["is_favored"] = is_in_favor_list("path",p.id,user_auth_id)
        t["path_created_at"] = p.path_created_at

        try:
            t["path_user"] = p.path_user.user.startup.mark_name
        except:
            t["path_user"] = p.path_user.mng_name
        t["path_total_play"] = p.path_total_play
        t["path_thumb"] = p.path_thumb
        result["path_list"].append(copy.deepcopy(t))

    for p in AdditionalUserInfo.objects.get(id=user_auth_id).favorite_course.all():
        t={}
        t["course_title"]=p.course_title
        t["id"]=p.id
        t["is_favored"] = is_in_favor_list("course", p.id, user_auth_id)
        t["course_created_at"] = p.course_created_at
        try:
            t["course_user"] = p.course_user.user.startup.mark_name
        except:
            t["course_user"] = p.course_user.mng_name

        t["course_total_play"] = p.course_total_play
        t["course_thumb"] = p.course_thumb
        result["course_list"].append(copy.deepcopy(t))

    for p in AdditionalUserInfo.objects.get(id=user_auth_id).favorite_clip.all():
        t={}
        t["clip_title"]=p.clip_title
        t["id"]=p.id
        t["is_favored"] = is_in_favor_list("clip", p.id, user_auth_id)
        t["clip_created_at"] = p.clip_created_at
        try:
            t["clip_user"] = p.clip_user.user.startup.mark_name
        except:
            t["clip_user"] = p.clip_user.mng_name
        t["clip_play"] = p.clip_play
        t["clip_thumb"] = p.clip_thumb
        try:
            t["clip_entry_point"] = "/channel/clip/view/"+str(p.id)
        except:
            pass
        result["clip_list"].append(copy.deepcopy(t))
    print(result)
    return JsonResponse(result, safe=False)

@csrf_exempt
@my_timer
def vue_get_author_lecture(request):


    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    result={}
    result["path_list"] = []
    for p in Path.objects.filter(path_user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
        t={}
        t["path_title"]=p.path_title
        t["id"]=p.id
        t["path_created_at"] = p.path_created_at
        try:
            t["path_user"] = p.path_user.user.startup.mark_name
        except:
            t["path_user"] = p.path_user.mng_name
        t["path_total_play"] = p.path_total_play
        t["path_thumb"] = p.path_thumb
        #t["entry_point"] = "/path/view/"+str(p.id) + "/" + str(p.course.all().first().id) + "/" + str(p.course.all().first().clips.all().first().id)
        t["entry_point"]=""
        for c in p.path_course.all():
            for clip in c.course_clips.all():
                if(c.id and clip.id):
                    t["entry_point"] = "/path/view/"+str(p.id) + "/" + str(c.id) + "/" + str(clip.id)
        result["path_list"].append(copy.deepcopy(t))
    result["course_list"] =[] # = HitCourseLog.objects.filter(user= AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in Course.objects.filter(course_user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
        t={}
        t["course_title"]=p.course_title
        t["id"]=p.id
        t["course_created_at"] = p.course_created_at
        try:
            t["course_user"] = p.course_user.user.startup.mark_name
        except:
            t["course_user"] = p.course_user.mng_name


        t["course_total_play"] = p.course_total_play
        t["course_thumb"] = p.course_thumb
        try:
            t["entry_point"] = "/course/view/"+str(p.id) + "/"+str(p.course_clips.first().id)
        except:
            t["entry_point"] = ""
        result["course_list"].append(copy.deepcopy(t))

    result["clip_list"] =[] # = HitClipLog.objects.filter(user=AdditionalUserInfo.objects.get(id=request.GET.get("id"))).order_by("-id").values()[:3]
    for p in Clip.objects.filter(clip_user= AdditionalUserInfo.objects.get(id=user_auth_id)).order_by("-id"):
        t={}
        t["clip_title"]=p.clip_title
        t["id"]=p.id
        t["clip_created_at"] = p.clip_created_at
        try:
            t["clip_user"] = p.clip_user.user.startup.mark_name
        except:
            t["clip_user"] = p.clip_user.user.additionaluserinfo.mng_name
        t["clip_play"] = p.clip_play
        t["clip_thumb"] = p.clip_thumb

        result["clip_list"].append(copy.deepcopy(t))

    return JsonResponse({'results':result })


@csrf_exempt

def generate_thumbnail(in_filename, out_filename, time, width):
    try:
        (
            ffmpeg
            .input(in_filename, ss=time)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)
import subprocess
@csrf_exempt
def getLength(filename):

    result = subprocess.Popen(["ffprobe", filename],stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    #print(result.stdout.readlines())
    for x in result.stdout.readlines():
        xs= x.decode('utf-8')
        xi= xs.find("Duration")
        if xi>0:
             xl= xs[xi+10:xi+10+11].split(":")
             sec= int(xl[0])*3600 + int(xl[1])*60 + int(xl[2].split(".")[0])
             return sec
    return 0



@csrf_exempt
@my_timer
def vue_upload_clip(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    clip = Clip()
    clip.clip_user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    clip.save()
    print ("step 00")
    if request.FILES.get("clip_file"):
        if  request.FILES.get("clip_file").name:
            print("step 1")
            path = handle_uploaded_file_movie(request.FILES['clip_file'], str(request.FILES['clip_file']),
                                                      rjd["user_id"])
            print("step 2")
            clip.clip_mov_url = path
            print("path")
            #generate_thumbnail(path, "thumnail.png", 0,"128")
            print(getLength(path))
    clip.clip_thumb = "https://img.youtube.com/vi/"+rjd["youtube_id"]+"/0.jpg"
    clip.clip_title =rjd["clip_title"]
    for t in rjd["filter_p"]:
        print(t)
        clip.clip_filter.add(EduFilter.objects.get(name=t.replace("#  ","")))

    clip.clip_play = int(rjd["time"])
    print(rjd["time"])
    clip.clip_youtube = rjd["youtube_id"]
    clip.clip_info =  rjd["clip_info"]
    clip.clip_object = rjd["clip_object"]
    clip.save()
    return JsonResponse({"result":"ok"})
@csrf_exempt
@my_timer
def vue_get_channel_statics_clip(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    clip = Clip.objects.get(id=request.GET.get("clip_id"))
    cct = json.loads(json.dumps(ast.literal_eval(ClipCountingTable.objects.get(clip=clip).string_data)))
    return  JsonResponse(cct)



def vue_get_channel_statics_clip_update():

    for clip in Clip.objects.all():
        hit_date_list = HitClipLog.objects.filter(hit_clip=clip).values("hit_clip_date").distinct()
        result = {}
        result["hit_static"] = {}
        result["all_static"]= {}
        result["hit_static"]["line_data"] = []
        for hd in hit_date_list:
            temp={}
            temp["date"] = str(hd["hit_clip_date"])
            temp["number"] = (HitClipLog.objects.filter(hit_clip=clip).filter(hit_clip_date = hd["hit_clip_date"])).count()
            result["hit_static"]["line_data"].append(copy.deepcopy(temp))
        favorite_date_list = FavoriteLog.objects.filter(clip=clip).values("date").distinct()
        result["favorite_static"]={}
        result["favorite_static"]["line_data"]=[]
        for fd in favorite_date_list:
            temp={}
            temp["date"] = str(fd["date"])
            temp["number"] = (FavoriteLog.objects.filter(clip=clip).filter(date = fd["date"])).count()
            result["favorite_static"]["line_data"].append(copy.deepcopy(temp))
        registered_date_list = RegisteredChannel.objects.filter(clip=clip).values("date").distinct()
        result["reg_static"] = {}
        result["reg_static"]["line_data"] = []
        for fd in registered_date_list:
            temp = {}
            temp["date"] = str(fd["date"])
            temp["number"] = (RegisteredChannel.objects.filter(clip=clip).filter(date=fd["date"])).count()
            result["reg_static"]["line_data"].append(copy.deepcopy(temp))
        all_user_list=[]
        hit_user_list = []
        favorite_usr_list=[]
        registered_usr_list=[]
        result["all_static"]["all_usr_num"]=""
        for hit_row in HitClipLog.objects.filter(hit_clip=clip ):
            try:
                hit_user_list.append( hit_row.hit_clip_user.user.startup)
            except:
                pass
        for fav_row in FavoriteLog.objects.filter(clip=clip):
            try:
                favorite_usr_list.append(fav_row.user.user.startup)
            except:
                pass
        for reg_row  in RegisteredChannel.objects.filter(clip=clip):
            try:
                registered_usr_list.append(reg_row.channel_user.user.startup )
            except:
                pass
        all_user_list =  list(set( hit_user_list + favorite_usr_list + registered_usr_list ) )
        hit_user_list = list(set(hit_user_list))
        favorite_usr_list = list(set(favorite_usr_list))
        registered_usr_list = list(set(registered_usr_list))

        result["all_static"]["all_usr_num"] = len(all_user_list)
        result["hit_static"]["hit_usr_num"] = len(hit_user_list)
        result["favorite_static"]["favorite_usr_num"] = len(favorite_usr_list)
        result["reg_static"]["reg_usr_num"] = len(registered_usr_list)
        # 전체
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []
        k = 1
        com_kind=""
        local=""
        result["all_static"]["all_startup_list"] = []
        result["all_static"]["all_comtype_filter"]=[]
        for startup in all_user_list:
            com_kind = ""
            local = []
            filter_list = startup.selected_company_filter_list.all()
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
            result["all_static"]["all_startup_list"].append({
                    "startup_id": startup.id,
                    "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                    "company_kind": com_kind,
                    "local": ",".join(local),
                    "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
                })
            k = k + 1
        result["all_static"]["all_comtype_filter"] = organize(all_comtype_filter)
        result["all_static"]["all_location_filter"] =  organize(all_location_filter)
        result["all_static"]["all_genre_filter"] =  organize(all_genre_filter)
        result["all_static"]["all_area_filter"] = organize( all_area_filter)
        # 방문자
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        result["hit_static"]["hit_startup_list"] = []
        k = 1
        result["hit_static"]["hit_startup_list"]=[]
        for startup in hit_user_list:
            filter_list = startup.selected_company_filter_list.all()
            com_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
            result["hit_static"]["hit_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["hit_static"]["hit_comtype_filter"] =  organize(hit_comtype_filter)
        result["hit_static"]["hit_location_filter"] = organize(hit_location_filter)
        result["hit_static"]["hit_genre_filter"] =  organize(hit_genre_filter)
        result["hit_static"]["hit_area_filter"] =  organize(hit_area_filter)
    # 등록자
        reg_comtype_filter = []
        reg_location_filter = []
        reg_genre_filter = []
        reg_area_filter = []
        result["reg_static"]["reg_startup_list"] = []
        k = 1

        for startup in registered_usr_list:
            filter_list = startup.selected_company_filter_list.all()
            com_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    reg_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    reg_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    reg_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    reg_area_filter.append(filter.filter_name)
            result["reg_static"]["reg_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["reg_static"]["reg_comtype_filter"] =  organize(reg_comtype_filter)
        result["reg_static"]["reg_location_filter"] =  organize(reg_location_filter)
        result["reg_static"]["reg_genre_filter"] =  organize(reg_genre_filter)
        result["reg_static"]["reg_area_filter"] =  organize(reg_area_filter)
    # 좋아요
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        result["favorite_static"]["fav_startup_list"] = []
        k = 1

        for startup in favorite_usr_list:
            filter_list = startup.selected_company_filter_list.all()
            com_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
            result["favorite_static"]["fav_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["favorite_static"]["fav_comtype_filter"] =  organize(fav_comtype_filter)
        result["favorite_static"]["fav_location_filter"] =  organize(fav_location_filter)
        result["favorite_static"]["fav_genre_filter"] =  organize(fav_genre_filter)
        result["favorite_static"]["fav_area_filter"] =  organize(fav_area_filter)
        result["min_date"] = clip.clip_created_at.isoformat()
        cct,created = ClipCountingTable.objects.get_or_create(clip=clip)
        cct.clip=clip
        cct.string_data=result
        cct.save()
    return JsonResponse({"data":result})
@csrf_exempt
@my_timer
def vue_get_channel_statics_path(request):
    path = Path.objects.get(id=request.GET.get("path_id"))
    cct = json.loads(json.dumps(ast.literal_eval(PathCountingTable.objects.get(path=path).string_data)))
    return  JsonResponse(cct)


def vue_get_channel_statics_path_update():
    # path = Path.objects.get(id=request.GET.get("path_id"))
    for path in Path.objects.all():
        hit_date_list = HitPathLog.objects.filter(hit_path=path).values("hit_path_date").distinct()
        result = {}
        result["hit_static"] = {}
        result["all_static"] = {}
        result["hit_static"]["line_data"] = []
        for hd in hit_date_list:
            temp = {}
            temp["date"] = str(hd["hit_path_date"])
            temp["number"] = (HitPathLog.objects.filter(hit_path=path).filter(hit_path_date=hd["hit_path_date"])).count()
            result["hit_static"]["line_data"].append(copy.deepcopy(temp))
        favorite_date_list = FavoriteLog.objects.filter(path=path).values("date").distinct()
        result["favorite_static"] = {}
        result["favorite_static"]["line_data"] = []
        for fd in favorite_date_list:
            temp = {}
            temp["date"] = str(fd["date"])
            temp["number"] = (FavoriteLog.objects.filter(path=path).filter(date=fd["date"])).count()
            result["favorite_static"]["line_data"].append(copy.deepcopy(temp))
        registered_date_list = RegisteredChannel.objects.filter(path=path).values("date").distinct()
        result["reg_static"] = {}
        result["reg_static"]["line_data"] = []
        for fd in registered_date_list:
            temp = {}
            temp["date"] = str(fd["date"])
            temp["number"] = (RegisteredChannel.objects.filter(path=path).filter(date=fd["date"])).count()
            result["reg_static"]["line_data"].append(copy.deepcopy(temp))
            # 전체
        # 먼저 각각의 스타트업 리스트 추출 하고 전체 리스트 만들어서 push

        all_user_list = []
        hit_user_list = []
        favorite_usr_list = []
        registered_usr_list = []
        result["all_static"]["all_usr_num"] = ""
        for hit_row in HitPathLog.objects.filter(hit_path=path):
            try:
                hit_user_list.append(hit_row.hit_path_user.user.startup)
            except:
                pass
        for fav_row in FavoriteLog.objects.filter(path=path):
            try:
                favorite_usr_list.append(fav_row.user.user.startup)
            except:
                pass
        for reg_row in RegisteredChannel.objects.filter(path=path):
            try:
                registered_usr_list.append(reg_row.channel_user.user.startup)
            except:
                pass
        all_user_list = list(set(hit_user_list + favorite_usr_list + registered_usr_list))

        hit_user_list = list(set(hit_user_list))
        favorite_usr_list = list(set(favorite_usr_list))
        registered_usr_list = list(set(registered_usr_list))

        result["all_static"]["all_usr_num"] = len(all_user_list)
        result["hit_static"]["hit_usr_num"] = len(hit_user_list)
        result["favorite_static"]["favorite_usr_num"] = len(favorite_usr_list)
        result["reg_static"]["reg_usr_num"] = len(registered_usr_list)
        # 전체
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []

        k = 1


        result["all_static"]["all_startup_list"] = []

        result["all_static"]["all_comtype_filter"] = []
        for startup in all_user_list:
            com_kind = ""
            local = []
            filter_list = startup.selected_company_filter_list.all()
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
            result["all_static"]["all_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": local,
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["all_static"]["all_comtype_filter"] = organize(all_comtype_filter)
        result["all_static"]["all_location_filter"] = organize(all_location_filter)
        result["all_static"]["all_genre_filter"] = organize(all_genre_filter)
        result["all_static"]["all_area_filter"] = organize(all_area_filter)

        # 방문자
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        result["hit_static"]["hit_startup_list"] = []
        k = 1

        result["hit_static"]["hit_startup_list"] = []
        for startup in hit_user_list:
            com_kind = ""
            local = []
            filter_list = startup.selected_company_filter_list.all()
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)

                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
            result["hit_static"]["hit_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["hit_static"]["hit_comtype_filter"] = organize(hit_comtype_filter)
        result["hit_static"]["hit_location_filter"] = organize(hit_location_filter)
        result["hit_static"]["hit_genre_filter"] = organize(hit_genre_filter)
        result["hit_static"]["hit_area_filter"] = organize(hit_area_filter)

        # 등록자
        reg_comtype_filter = []
        reg_location_filter = []
        reg_genre_filter = []
        reg_area_filter = []
        result["reg_static"]["reg_startup_list"] = []
        k = 1

        for startup in registered_usr_list:
            com_kind = ""
            local = []
            filter_list = startup.selected_company_filter_list.all()
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    reg_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    reg_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    reg_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    reg_area_filter.append(filter.filter_name)

            result["reg_static"]["reg_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        result["reg_static"]["reg_comtype_filter"] = organize(reg_comtype_filter)
        result["reg_static"]["reg_location_filter"] = organize(reg_location_filter)
        result["reg_static"]["reg_genre_filter"] = organize(reg_genre_filter)
        result["reg_static"]["reg_area_filter"] = organize(reg_area_filter)

        # 좋아요
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        result["favorite_static"]["fav_startup_list"] = []
        k = 1

        for startup in favorite_usr_list:
            com_kind = ""
            local = []
            filter_list = startup.selected_company_filter_list.all()
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                    local = filter.filter_name
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)

                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
            result["favorite_static"]["fav_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["favorite_static"]["fav_comtype_filter"] = organize(fav_comtype_filter)
        result["favorite_static"]["fav_location_filter"] = organize(fav_location_filter)
        result["favorite_static"]["fav_genre_filter"] = organize(fav_genre_filter)
        result["favorite_static"]["fav_area_filter"] = organize(fav_area_filter)
        result["min_date"] = path.path_created_at.isoformat()
        cct,created = PathCountingTable.objects.get_or_create(path=path)
        cct.path=path
        cct.string_data=result
        cct.save()
    return JsonResponse({"data": result, })

@csrf_exempt
@my_timer
def vue_get_channel_statics_course(request):
    course = Course.objects.get(id=request.GET.get("course_id"))
    cct = json.loads(json.dumps(ast.literal_eval(CourseCountingTable.objects.get(course=course).string_data)))
    return  JsonResponse(cct)


def vue_get_channel_statics_course_update():


    for course in Course.objects.all():
        hit_date_list = HitCourseLog.objects.filter(hit_course=course).values("hit_course_date").distinct()
        result = {}
        result["hit_static"] = {}
        result["all_static"] = {}
        result["hit_static"]["line_data"] = []
        for hd in hit_date_list:
            temp = {}
            temp["date"] = str(hd["hit_course_date"])
            temp["number"] = (HitCourseLog.objects.filter(hit_course=course).filter(hit_course_date=hd["hit_course_date"])).count()
            result["hit_static"]["line_data"].append(copy.deepcopy(temp))
        favorite_date_list = FavoriteLog.objects.filter(course=course).values("date").distinct()
        result["favorite_static"] = {}
        result["favorite_static"]["line_data"] = []
        for fd in favorite_date_list:
            temp = {}
            temp["date"] = str(fd["date"])
            temp["number"] = (FavoriteLog.objects.filter(course=course).filter(date=fd["date"])).count()
            result["favorite_static"]["line_data"].append(copy.deepcopy(temp))
        registered_date_list = RegisteredChannel.objects.filter(course=course).values("date").distinct()
        result["reg_static"] = {}
        result["reg_static"]["line_data"] = []
        for fd in registered_date_list:
            temp = {}
            temp["date"] = str(fd["date"])
            temp["number"] = (RegisteredChannel.objects.filter(course=course).filter(date=fd["date"])).count()
            result["reg_static"]["line_data"].append(copy.deepcopy(temp))
            # 전체
        # 먼저 각각의 스타트업 리스트 추출 하고 전체 리스트 만들어서 push

        all_user_list = []
        hit_user_list = []
        favorite_usr_list = []
        registered_usr_list = []
        result["all_static"]["all_usr_num"] = ""
        for hit_row in HitCourseLog.objects.filter(hit_course=course):
            try:
                hit_user_list.append(hit_row.hit_course_user.user.startup)
            except:
                pass
        for fav_row in FavoriteLog.objects.filter(course=course):
            try:
                favorite_usr_list.append(fav_row.user.user.startup)
            except:
                pass
        for reg_row in RegisteredChannel.objects.filter(course=course):
            try:
                registered_usr_list.append(reg_row.channel_user.user.startup)
            except:
                pass
        all_user_list = list(set(hit_user_list + favorite_usr_list + registered_usr_list))

        hit_user_list = list(set(hit_user_list))
        favorite_usr_list = list(set(favorite_usr_list))
        registered_usr_list = list(set(registered_usr_list))

        result["all_static"]["all_usr_num"] = len(list(set(all_user_list)))
        result["hit_static"]["hit_usr_num"] = len(hit_user_list)
        result["favorite_static"]["favorite_usr_num"] = len(favorite_usr_list)
        result["reg_static"]["reg_usr_num"] = len(registered_usr_list)

        # 전체
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []



        result["all_static"]["all_startup_list"] = []
        result["all_static"]["all_comtype_filter"] = []
        for startup in all_user_list:
            filter_list = startup.selected_company_filter_list.all()
            k = 1
            com_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
            result["all_static"]["all_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["all_static"]["all_comtype_filter"] = organize(all_comtype_filter)
        result["all_static"]["all_location_filter"] = organize(all_location_filter)
        result["all_static"]["all_genre_filter"] = organize(all_genre_filter)
        result["all_static"]["all_area_filter"] = organize(all_area_filter)

        # 방문자
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        result["hit_static"]["hit_startup_list"] = []
        k = 1
        com_kind = ""
        local = ""
        result["hit_static"]["hit_startup_list"] = []
        local = []
        for startup in hit_user_list:
            filter_list = startup.selected_company_filter_list.all()
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
            result["hit_static"]["hit_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["hit_static"]["hit_comtype_filter"] = organize(hit_comtype_filter)
        result["hit_static"]["hit_location_filter"] = organize(hit_location_filter)
        result["hit_static"]["hit_genre_filter"] = organize(hit_genre_filter)
        result["hit_static"]["hit_area_filter"] = organize(hit_area_filter)

        # 등록자
        reg_comtype_filter = []
        reg_location_filter = []
        reg_genre_filter = []
        reg_area_filter = []
        result["reg_static"]["reg_startup_list"] = []
        k = 1
        com_kind = ""
        local = ""
        for startup in registered_usr_list:
            filter_list = startup.selected_company_filter_list.all()
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    reg_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    reg_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    reg_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    reg_area_filter.append(filter.filter_name)

            result["reg_static"]["reg_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        result["reg_static"]["reg_comtype_filter"] = organize(reg_comtype_filter)
        result["reg_static"]["reg_location_filter"] = organize(reg_location_filter)
        result["reg_static"]["reg_genre_filter"] = organize(reg_genre_filter)
        result["reg_static"]["reg_area_filter"] = organize(reg_area_filter)

        # 좋아요
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        result["favorite_static"]["fav_startup_list"] = []
        k = 1
        com_kind = ""
        local = ""
        for startup in favorite_usr_list:
            filter_list = startup.selected_company_filter_list.all()
            local=[]
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                    com_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)

                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
            result["favorite_static"]["fav_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": com_kind,
                "local": ','.join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["favorite_static"]["fav_comtype_filter"] = organize(fav_comtype_filter)
        result["favorite_static"]["fav_location_filter"] = organize(fav_location_filter)
        result["favorite_static"]["fav_genre_filter"] = organize(fav_genre_filter)
        result["favorite_static"]["fav_area_filter"] = organize(fav_area_filter)
        result["min_date"] = course.course_created_at.isoformat()
        cct,created = CourseCountingTable.objects.get_or_create(course=course)
        cct.course=course
        cct.string_data=result
        cct.save()

    return JsonResponse({"data": result, })





@csrf_exempt
@my_timer
def vue_get_statics_by_channel(request):
    path = Path.objects.all()
    result = {}
    result["simple_path"]=[]
    for p in Path.objects.all():
        if len(p.path_title) > 30:
            p.path_title = p.path_title [:30] + "..."
        result["simple_path"].append({
            "label":p.path_title, "id":p.id,
        })
    result["simple_course"] = []
    for p in Course.objects.all():
        if len(p.course_title) > 30:
            p.course_title = p.course_title[:30] + "..."
        result["simple_course"].append({
            "label": p.course_title, "id": p.id,
        })
    result["simple_clip"] = []
    for p in Clip.objects.all():
        if len(p.clip_title) > 30:
            p.clip_title = p.clip_title[:30] + "..."
        result["simple_clip"].append({
            "label": p.clip_title, "id": p.id,
        })

    result["path"]=[]
    for p in path:
        temp_path={}
        temp_path["clip_title"] = p.path_title
        temp_path["id"] = p.id
        temp_path["course"] = []
        for c in p.path_course.all():
            temp_course = {}
            temp_course["id"] = c.id
            temp_course["clip_title"] = c.course_title
            temp_course["clip"] = []
            for clip in c.course_clips.all():
                print("why")
                temp_clip = {}
                temp_clip["clip_title"] = clip.clip_title
                temp_clip["id"] = clip.id
                temp_course["clip"].append(copy.deepcopy(temp_clip))
            temp_path["course"].append(copy.deepcopy(temp_course))
        result["path"].append( copy.deepcopy(temp_path))
    return  JsonResponse(result)

@csrf_exempt
@my_timer
def vue_get_lec_tag(request):
    result={}
    result["tag"]=[]
    for filter in EduFilter.objects.all():
        temp={}
        temp["id"] = filter.id
        temp["name"] = filter.name
        result["tag"].append(copy.deepcopy(temp))
    return JsonResponse(result)

@csrf_exempt
@my_timer
def vue_get_clip_uploaded(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result

    clip_list = Clip.objects.filter(clip_user_id = user_auth_id)
    print(clip_list)
    result={}
    result["clip"]=[]
    for c in clip_list:
        temp={}
        temp["clip_title"] = c.clip_title
        temp["clip_created_at"] = c.clip_created_at
        try:
            temp["clip_user"] = c.clip_user.user.startup.mark_name
        except:
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_play"] = c.clip_play
        temp["clip_author"] = c.clip_user.id
        temp["clip_thumb"] = c.clip_thumb
        temp["id"] = c.id
        result["clip"].append(copy.deepcopy(temp))

    return JsonResponse(result)


@csrf_exempt
@my_timer
def vue_modify_clip(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    clip = Clip.objects.get(id=rjd["clip_id"])

    print("step 00")
    if request.FILES.get("clip_file"):
        if request.FILES.get("clip_file").name:
            print("step 1")
            path = handle_uploaded_file_movie(request.FILES['clip_file'], str(request.FILES['clip_file']),
                                              rjd["user_id"])
            print("step 2")
            clip.clip_mov_url = path
            print("path")
            # generate_thumbnail(path, "thumnail.png", 0,"128")
            print(getLength(path))
    clip.clip_thumb = "https://img.youtube.com/vi/" + rjd["youtube_id"] + "/0.jpg"
    clip.clip_title = rjd["clip_title"]
    for t in rjd["filter_p"]:
        clip.clip_filter.add(EduFilter.objects.get(name=t.replace("#  ", "")))
        print(t)
    clip.clip_play = int(rjd["time"])
    print(rjd["time"])
    clip.clip_youtube = rjd["youtube_id"]
    clip.clip_info = rjd["clip_info"]
    clip.clip_object = rjd["clip_object"]
    clip.save()
    return JsonResponse({"result": "ok"})






@csrf_exempt
@my_timer
def vue_upload_course(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    course = Course()
    course.course_user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    course.save()
    if request.FILES.get("file_1"):
        if  request.FILES.get("file_1").name:
            path = handle_uploaded_file_movie(request.FILES['file_1'], str(request.FILES['file_1']),
                                              rjd["user_id"])
            course.course_thumb = path
    course.course_title = rjd["course_title"]
    for t in rjd["course_tag"]:
        course.course_filter.add(EduFilter.objects.get(name=t.replace("#  ", "")))
    time=0
    for t in rjd["course_clips"]:
        course.course_clips.add(Clip.objects.get(id=t["id"]))
        time= time + t["clip_play"]
    course.course_info = rjd["course_info"]
    course.course_object = rjd["course_object"]
    course.course_total_play = time
    course.course_rec_dur = rjd["course_rec_dur"]
    course.save()
    return JsonResponse({"result": "ok"})

@csrf_exempt
@my_timer
def vue_modify_course(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    course = Course.objects.get(id=rjd["course_id"])
    course.course_user = AdditionalUserInfo.objects.get(id=rjd["user_id"])
    course.save()
    if request.FILES.get("file_1"):
        if  request.FILES.get("file_1").name:
            path = handle_uploaded_file_movie(request.FILES['file_1'], str(request.FILES['file_1']),
                                              rjd["user_id"])
            course.course_thumb = path
    course.course_title = rjd["course_title"]
    course.course_filter.clear()
    for t in rjd["course_tag"]:
        course.course_filter.add(EduFilter.objects.get(name=t.replace("#  ", "")))
    time=0
    course.course_clips.clear()
    for t in rjd["course_clips"]:
        course.course_clips.add(Clip.objects.get(id=t["clip_id"]))
        time= time + t["clip_play"]
    course.course_info = rjd["course_info"]
    course.course_object = rjd["course_object"]
    course.course_total_play = time
    course.course_rec_dur = rjd["course_rec_dur"]
    course.save()
    return JsonResponse({"result": "ok"})



@csrf_exempt
@my_timer
def vue_get_course_uploaded(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    course_list = Course.objects.filter(course_user_id = user_auth_id)
    result={}
    result["course_set"]=[]
    for c in course_list:
        temp={}
        temp["id"] = c.id
        temp["course_created_at"] = c.course_created_at
        temp["course_title"] = c.course_title
        temp["filter"] = []
        print(c.course_clips.all().first())
        try:
            temp["entry_point"]= "/course/view/"+str(c.id)+"/"+str(c.course_clips.all().first().id)
        except:
            temp["entry_point"] = ""
        for f in c.course_filter.all():
            print(f.name)
            temp["filter"].append(f.name)
        temp["course_rec_dur"] = c.course_rec_dur
        temp["course_info"] = c.course_info
        try:
            temp["user"] =  c.course_user.user.startup.mark_name
        except:
            temp["user"] = c.course_user.mng_name
        temp["course_total_play"] = c.course_total_play
        temp["course_clips"] = []
        for clip in c.course_clips.all():
            ttem={}
            ttem["clip_title"]= clip.clip_title
            ttem["clip_created_at"] = clip.clip_created_at
            ttem["clip_play"] = clip.clip_play
            ttem["int"] = (clip.additionaluserinfo_set.all()).count()
            temp["course_clips"].append(copy.deepcopy(ttem))
        result["course_set"].append(copy.deepcopy(temp))
    return JsonResponse(result)



@csrf_exempt
@my_timer
def vue_upload_path(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    path = Path()
    path.path_user = AdditionalUserInfo.objects.get(id=user_auth_id)
    path.save()
    if request.FILES.get("file_1"):
        print(request.FILES)
        if request.FILES.get("file_1").name:
            img_path = handle_uploaded_file_movie(request.FILES['file_1'], str(request.FILES['file_1']),
                                              rjd["user_id"])
            path.path_thumb = img_path
    path.path_title = rjd["path_title"]
    for t in rjd["path_filter"]:
        print(t)
        path.path_filter.add(EduFilter.objects.get(name=t.replace("#", "").strip()))
    try:
        time=0
        for t in rjd["path_course"]:
            path.path_course.add(Course.objects.get(id=t["id"]))
            time = time + t["course_total_play"]
    except Exception as e:
        print(e)
        pass
    path.path_total_play = time
    path.path_info = rjd["path_info"]
    path.path_rec_dur = rjd["path_rec_dur"]
    path.path_object = rjd["path_object"]
    path.save()
    return JsonResponse({"result": "ok"})
@csrf_exempt
@my_timer
def vue_modify_path(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    rjd = json.loads(request.POST.get("json_data"))
    print(rjd)
    path = Path.objects.get(id= rjd["path_id"])
    path.path_user = AdditionalUserInfo.objects.get(id=user_auth_id)
    path.save()
    if request.FILES.get("file_1"):
        print(request.FILES)
        if request.FILES.get("file_1").name:
            img_path = handle_uploaded_file_movie(request.FILES['file_1'], str(request.FILES['file_1']),
                                              rjd["user_id"])
            path.path_thumb = img_path
    path.path_title = rjd["path_title"]
    for t in rjd["path_filter"]:
        print(t)
        path.path_filter.add(EduFilter.objects.get(name=t.replace("#", "").strip()))

    try:
        time=0
        for t in rjd["path_course"]:
            print(t)
            try:
                path.path_course.add(Course.objects.get(id=t["course_id"]))
            except:
                path.path_course.add(Course.objects.get(id=t["id"]))
            time = time + t["course_total_play"]
    except Exception as e:
        print(e)
        pass
    path.path_total_play = time
    path.path_info = rjd["path_info"]
    path.path_rec_dur = rjd["path_rec_dur"]
    path.path_object = rjd["path_object"]
    path.save()
    return JsonResponse({"result": "ok"})


@csrf_exempt
@my_timer
def vue_get_clip(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result={}
    print(request.POST)
    clip= Clip.objects.get(id=request.POST.get("id"))
    result["ip"]=  urllib.request.urlopen('https://api.ipify.org/').read().decode()
    if request.POST.get("user"):
        print(AdditionalUserInfo.objects.get(id= request.POST.get("user")).favorite_clip.all())
        if clip in AdditionalUserInfo.objects.get(id= request.POST.get("user")).favorite_clip.all() :
            result["is_favored"] = "true"
        else:
            result["is_favored"] = "false"
    result["clip_title"] = clip.clip_title
    result["clip_youtube"] = clip.clip_youtube
    result["clip_user_id"]= clip.clip_user.id
    result["clip_mov_url"] = clip.clip_mov_url
    result["is_favored"] = is_in_favor_list( "clip" , clip.id , user_auth_id)
    result["clip_id"] = clip
    result["clip_object"] = clip.clip_object
    result["clip_info"] = clip.clip_info
    result["clip_play"] = clip.clip_play
    try:
        result["clip_user"] = clip.clip_user.user.startup.mark_name
    except:
        result["clip_user"] = clip.clip_user.mng_name
    result["clip_created_at"] = clip.clip_created_at
    result["clip_thumb"] = clip.clip_thumb
    result["clip_id"] = clip.id
    result["int"] = (clip.additionaluserinfo_set.all()).count()
    result["tag"]=[]
    for  t in clip.clip_filter.all():
        result["tag"].append(t.name)
    result["another_clip"]=[]
    for c in Clip.objects.all().order_by("?")[:4]:
        temp={}
        temp["id"] = c.id
        temp["clip_play"] = c.clip_play
        temp["clip_title"] = c.clip_title
        temp["clip_thumb"] = c.clip_thumb
        print(clip.clip_user)
        try:
            temp["clip_user"] = c.clip_user.user.startup.mark_name
            print(temp["clip_user"])
        except Exception as e:
            print(e)
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_created_at"] = c.clip_created_at
        temp["clip_youtube"] = c.clip_youtube
        result["another_clip"].append(copy.deepcopy(temp))
    result["another_course"] = []
    for c in Course.objects.all().order_by("?"):
        temp = {}
        temp["id"] = c.id
        temp["course_title"] = c.course_title
        temp["course_total_play"] = c.course_total_play
        temp["course_thumb"] = c.course_thumb
        try:
            temp["course_user"] = c.course_user.user.startup.mark_name
        except:
            temp["course_user"] = c.course_user.mng_name
        temp["course_created_at"] = c.course_created_at
        try:
            temp["entry_point"] = "course/view/"+str(c.id) + "/"+ str(c.course_clips.all().first().id)
        except Exception as e:
            pass
        temp["clip_youtube"] = clip.clip_youtube
        result["another_course"].append(copy.deepcopy(temp))
    return JsonResponse(result)

@csrf_exempt
@my_timer
def vue_get_course(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result={}
    clip= Clip.objects.get(id=request.POST.get("clip"))
    course = Course.objects.get(id=request.POST.get("id") )
    if user_auth_id:
        print(AdditionalUserInfo.objects.get(id= user_auth_id).favorite_course.all())
        if course in AdditionalUserInfo.objects.get(id= user_auth_id).favorite_course.all() :
            result["is_favored"] = "true"
        else:
            result["is_favored"] = "false"
    result["course_title"] = Course.objects.get(id=request.POST.get("id")).course_title
    result["clip_title"] = clip.clip_title
    result["course_play"] = course.course_total_play
    result["course_youtube"] = clip.clip_youtube
    result["course_mov_url"] = clip.clip_mov_url
    result["course_object"] = clip.clip_object
    result["course_info"] = clip.clip_info
    result["course_info"] = clip.clip_info
    result["is_favored"] = is_in_favor_list( "course", course.id , user_auth_id)
    try:
        result["course_user"] = clip.clip_user.user.startup.mark_name
    except:
        result["course_user"] = clip.clip_user.mng_name
    result["course_created_at"] = clip.clip_created_at
    result["int"] = (clip.additionaluserinfo_set.all()).count()
    result["course_id"] = course.id
    result["tag"] = []
    for t in clip.clip_filter.all():
        result["tag"].append(t.name)
    result["another_clip"]=[]
    k=1
    url_list = []
    prefix = "/channel/course/view/"
    for c in Course.objects.get(id=request.POST.get("id")).course_clips.all():
        temp={}
        url_list.append(prefix + str(course.id)+"/"+ str(c.id) )
        temp["index"] = k
        k=k+1
        temp["id"] = c.id
        temp["clip_play"] = c.clip_play
        temp["clip_created_at"] = c.clip_created_at
        try:
            temp["clip_user"] = c.clip_user.user.startup.mark_name
        except:
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_title"] = c.clip_title
        result["another_clip"].append(copy.deepcopy(temp))

    result["another_course"] = []
    for c in Course.objects.all().order_by("?")[:2]:
        temp = {}
        temp["id"] = c.id
        temp["course_title"] = c.course_title
        temp["course_total_play"] = c.course_total_play
        temp["course_thumb"] = c.course_thumb
        try:
            temp["course_user"] = c.course_user.user.startup.mark_name
        except:
            temp["course_user"] = c.course_user.mng_name

        temp["course_created_at"] = c.course_created_at
        try:
            temp["course_entry_point"] = "/channel/course/view/"+str(c.id)+"/"+str(c.course_clips.first().id)+"/"
        except:
            pass
        result["another_course"].append(copy.deepcopy(temp))
    present = url_list.index("/channel/course/view/"+ str(course.id) +"/"+str(clip.id) )
    if present == 0:
        prev=""
    else:
        prev = url_list[present - 1]
    if present == len(url_list)-1:
        next= ""
    else:
        next = url_list[present+1]
    result["prev_url"]= prev
    result["next_url"] = next
    return JsonResponse(result)


@csrf_exempt
@my_timer
def vue_get_path(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result={}
    path_url_list = []
    try:
        clip= Clip.objects.get(id=request.POST.get("clip"))
        result["clip_title"] = clip.clip_title
        result["clip_youtube"] = clip.clip_youtube
        result["clip_mov_url"] = clip.clip_mov_url
        result["object"] = clip.clip_object
        result["course_info"] = clip.course_info
        result["tag"] = []
        for t in clip.clip_filter.all():
            result["tag"].append(t.name)
        result["clip_id"] = clip.id
        result["int"] = (clip.additionaluserinfo_set.all()).count()
        result["clip_play"] = clip.clip_play
        result["user"] = clip.user.name
        result["created"] = clip.created_at

    except Exception as e:
        print(e)

    p = Path.objects.get(id=request.POST.get("id"))
    result["path_filter"] = []
    try:
        result["user"] = p.path_user.user.startup.mark_name
    except:
        result["user"] = p.path_user.mng_name
    for t in p.path_filter.all():
        result["path_filter"].append(t.name)
    result["path_title"] = p.path_title
    result["path_rec_dur"] = p.path_rec_dur
    result["path_id"] = p.id
    result["path_info"] = p.path_info
    result["path_object"] = p.path_object
    result["path_created_at"] = p.path_created_at
    result["is_favored"]=""
    try:
        if p in AdditionalUserInfo.objects.get(id=user_auth_id).favorite_path.all():
            result["is_favored"] = "true"
        else:
            result["is_favored"] = "false"
    except:
        result["is_favored"] = "false"
    result["total_play"] = p.path_total_play
    result["course"]=[]
    result["another_course"] = []

    k = 1
    a = 1
    # 패스 => 코스 항목
    for c in Path.objects.get(id=request.POST.get("id")).path_course.all():
            temp = {}
            temp["index"] = a
            a = a + 1
            k = 1
            temp["id"] = c.id
            temp["course_title"] = c.course_title
            try:
                temp["author"] = c.course_user.user.startup.mark_name
            except:
                temp["author"] = c.course_user.mng_name
            temp["course_created_at"] = c.course_created_at
            temp["course_info"] = c.course_info
            temp["course_object"] = c.course_object
            temp["course_rec_dur"] = c.course_rec_dur
            temp["course_total_play"] = c.course_total_play

            temp["course_filter"] = []
            for f in c.course_filter.all():
                temp["course_filter"].append(f.name)

            temp["clips"] = []
            # 코스 항목 => 강좌 항목 //
            for clip in c.course_clips.all():
                ttem = {}
                ttem["index"] = k
                k = k + 1
                ttem["id"] = clip.id
                try:
                    ttem["clip_user"] = clip.clip_user.user.startup.mark_name
                except:
                    ttem["clip_user"] = clip.clip_user.mng_name
                ttem["clip_play"] = clip.clip_play
                ttem["clip_title"] = clip.clip_title
                ttem["clip_created_at"] = clip.clip_created_at
                ttem["clip_info"] = clip.clip_info
                ttem["clip_object"] = clip.clip_object
                temp["clips"].append(copy.deepcopy(ttem))
                path_url_list.append(str(p.id)+"/"+str(c.id)+"/"+str(clip.id))

            result["course"].append(copy.deepcopy(temp))
            result["another_course"].append(copy.deepcopy(temp))

    path_index = path_url_list.index(str(p.id)+"/"+request.POST.get('course') + "/" +request.POST.get("clip"))
    if path_index-1 >= 0:
        prev_url = path_url_list[path_index-1]
    else:
        prev_url = ""
    if path_index < len(path_url_list)-1:
        next_url = path_url_list[path_index+1]
    else :
        next_url = ""
    result["prev_url"] = prev_url
    result["next_url"] = next_url

    temp= JsonResponse(result)
#    temp_content= temp.content // json string
#    //  update stat_table set json_data= temp_content where  stat_id=1;
    return temp
    #return JsonResponse(result)


@csrf_exempt
@my_timer
def vue_del_history(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    id= request.GET.get("id")
    try:
        History.objects.get(id=id).delete()
    except:
        pass
    try:
        ApplianceHistory.objects.get(id=id).delete()
    except:
        pass
    return JsonResponse({"result":"ok"})

@csrf_exempt
@my_timer
def set_alarm_read(request):
    arl=Alarm.objects.get(id= request.GET.get("val") )
    arl.alarm_read = True;
    arl.save()
    return JsonResponse({"result","success"})

@csrf_exempt
@my_timer
def delete_alarm(request):
    del_qs = Alarm.objects.filter(read=False).filter(alarm_created_at__lte = datetime.now()-timedelta(days=-7))
    for qs in del_qs:
        qs.delete()


@csrf_exempt
@my_timer
def  get_support_business_favorite_startup(request):
    support_business_id = request.GET.get("support_business_id")
    support_business = SupportBusiness.objects.get(id=support_business_id)
    item = support_business.additionaluserinfo_set.all()
    result=[]
    index = 1
    for st in item:
        kind = st.user.startup.selected_company_filter_list
        print(kind)
        kind_l = ""
        print(st.user.username)
        for k in kind.all():
            print(k.filter_name)
            if( k.cat_1 =="기업형태"):
                kind_l = k.filter_name
        result.append({
            "id":st.user.startup.id,
            "index":index,
            "company_name":st.user.startup.company_name,
            "company_kind":kind_l,
            "mark_name":st.user.startup.mark_name,
            "username":st.user.startup.mark_email,
            "mark_tel" : st.user.startup.mark_tel,
        })
        index = index+1
    return JsonResponse(result,safe=False)



# --------[기관 회원관리 - 매니저 계정 정보 조회 ]------- (기관관리자)
@csrf_exempt
@my_timer
def opr_vue_get_kikwan_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    opr_account_set = []
    k=1
    opr_all_account_set=[]
    for ac in  AdditionalUserInfo.objects.filter(mng_boss_id=request.POST.get("id")).order_by("-id"):
        temp={}
        temp["opr_index"] = k
        k=k+1
        temp["opr_id"] = ac.user.username
        temp["opr_mng_name"] = ac.mng_name
        temp["opr_mng_position"] = ac.mng_position
        temp["opr_mng_bonbu"] = ac.mng_bonbu
        temp["opr_mng_kikwan"] = ac.mng_kikwan
        temp["opr_mng_team"] = ac.mng_team
        temp["opr_mng_tel"] = ac.mng_tel
        temp["opr_mng_phone"] = ac.mng_phone
        temp["opr_mng_email"] = ac.mng_email
        temp["opr_mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        opr_account_set.append(copy.deepcopy(temp))
    k=1
    for ac in AdditionalUserInfo.objects.filter(Q(auth="MNG")|Q(auth="OPR")|Q(auth="4")).order_by("-id"):
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
    result={}
    result["opr_account_set"] = opr_account_set
    result["opr_all_account_set"] = opr_all_account_set

    return  JsonResponse(result, safe=False)





# --------[기관 회원관리 - 매니저 계정 정보 조회 ]------- (기관관리자)
@csrf_exempt
@my_timer
def opr_vue_get_kikwan_account_excel(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    opr_account_set = []
    k=1
    opr_all_account_set=[]

    ws.write(k, 0, str(k + 1))
    wb = xlwt.Workbook()
    ws = wb.add_sheet('소속회원')
    for ac in  AdditionalUserInfo.objects.filter(mng_boss_id=request.POST.get("id")).order_by("-id"):
        temp={}
        temp["opr_index"] = k
        k=k+1
        temp["opr_id"] = ac.user.username
        temp["opr_mng_name"] = ac.mng_name
        temp["opr_mng_position"] = ac.mng_position
        temp["opr_mng_bonbu"] = ac.mng_bonbu
        temp["opr_mng_kikwan"] = ac.mng_kikwan
        temp["opr_mng_team"] = ac.mng_team
        temp["opr_mng_tel"] = ac.mng_tel
        temp["opr_mng_phone"] = ac.mng_phone
        temp["opr_mng_email"] = ac.mng_email
        temp["opr_mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        opr_account_set.append(copy.deepcopy(temp))
    k=1
    for ac in AdditionalUserInfo.objects.filter(Q(auth="MNG")|Q(auth="OPR")|Q(auth="4")).order_by("-id"):
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
    result={}
    result["opr_account_set"] = opr_account_set
    result["opr_all_account_set"] = opr_all_account_set

    return  JsonResponse(result, safe=False)






@csrf_exempt
@my_timer
def opr_get_support_business_static(request):
    result={}
    support_business_id = request.GET.get("support_business_id")
    support_business = SupportBusiness.objects.get(id=support_business_id)
    support_business_author_id = request.GET.get("support_business_author")
    result["opr_support_business_min_date"] =  str(SupportBusiness.objects.get(id=support_business_id).support_business_update_at_ymdt).split(" ")[0]
    # 지원사업의 승인된 날짜부터 기산한다.

    #  매니저의 해당 지원사업의 방문 데이터
    support_business_detail_hit_date_ymd=[]
    support_business_detail_hit=[]
    for date_dict in  HitLog.objects.filter(support_business=support_business).values("date").order_by("-date").distinct():
        if date_dict["date"] not in support_business_detail_hit_date_ymd :
            support_business_detail_hit_date_ymd.append(date_dict["date"])
    for date in  support_business_detail_hit_date_ymd:
        support_business_detail_hit.append(
            {
                "date":date, "number":(HitLog.objects.filter(support_business= support_business).filter(date=date)).count()
            }

        )
    result["opr_support_business_detail_hit"] = support_business_detail_hit


    # 매니저의 해당 지원사업의 좋아요 데이터
    support_business_detail_favorite_date_ymd = []
    support_business_favorite=[]
    for date_dict in FavoriteLog.objects.filter(support_business=support_business).filter(date__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0])\
            .values("date").order_by("-date").distinct():
        if date_dict["date"] not in support_business_detail_favorite_date_ymd:
            support_business_detail_favorite_date_ymd.append(date_dict["date"])
    for date in support_business_detail_favorite_date_ymd:
        support_business_favorite.append(
            {
                "date": date,
                "number": (FavoriteLog.objects.filter(support_business=support_business).filter(date=date)).count()
            }
        )
    result["opr_support_business_detail_hit"] = support_business_detail_hit
    result["opr_support_business_favorite"] = support_business_favorite

    # =======[매니저 my 지원사업 좋아요 누른 스타트업의 id, 필터 추출]====== : 완료  list2
    startup_list = []
    for favored_startup in FavoredSupportBusiness.objects.filter(
            favored_support_business=support_business).values("favored_usr").distinct():
        print(favored_startup)
        startup_list.append(
            Startup.objects.get(user=AdditionalUserInfo.objects.get(id=favored_startup["favored_usr"]).user))
    favored_comtype_filter = []
    favored_location_filter = []
    favored_genre_filter = []
    favored_area_filter = []
    result["favored_startup_list"] = []
    k = 1

    for startup in startup_list:
        filter_list = startup.selected_company_filter_list.all()
        company_kind = ""
        local = []
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                favored_comtype_filter.append(filter.filter_name)
                company_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                favored_location_filter.append(filter.filter_name)
                local.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                favored_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                favored_area_filter.append(filter.filter_name)
        result["favored_startup_list"].append({
            "startup_id":startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    result["favored_comtype_filter"] = (organize(favored_comtype_filter))
    result["favored_location_filter"] = (organize(favored_location_filter))
    result["favored_genre_filter"] = (organize(favored_genre_filter))
    result["favored_area_filter"] = (organize(favored_area_filter))





    # 매니저의 해당 지원사업의 지원  데이터
    support_business_appliance_date_ymd = []
    support_business_appliance = []
    for date_dict in Appliance.objects.filter(support_business=support_business).filter(
            appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]) \
            .dates("appliance_update_at_ymdt","day").values("appliance_update_at_ymdt").order_by("-appliance_update_at_ymdt").distinct():
        if date_dict["appliance_update_at_ymdt"] not in support_business_appliance_date_ymd:
            support_business_appliance_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    for date in support_business_appliance_date_ymd:
        support_business_appliance.append(
            {
                "date": date,
                "number": (Appliance.objects.filter(support_business=support_business).filter(appliance_update_at_ymdt__date=str(date))).count()
            }
        )

    result["opr_support_business_appliance"] = support_business_appliance


    #
    # # 과거 통계 코드 - 기관 정테의 통계를 계산 해줌
    # #  매니저가 작성한 모든 지원사업의 방문 데이터
    # #  매니저가 작성한 모든 지원사업
    # support_business_mng_arr = SupportBusiness.objects.filter(support_business_author_id=support_business_author_id)
    #
    # support_business_detail_hit_avg_date_ymd = []
    # support_business_detail_mng_sum_hit = []
    # support_business_detail_mng_avg_hit = []
    # for date_dict in HitLog.objects.filter(support_business__in=support_business_mng_arr).filter( date__gte= str(support_business.support_business_update_at_ymdt).split(" ")[0] ).values("date").order_by(
    #         "-date").distinct():
    #     if date_dict["date"] not in support_business_detail_hit_avg_date_ymd:
    #         support_business_detail_hit_avg_date_ymd.append(date_dict["date"])
    # for date in support_business_detail_hit_avg_date_ymd:
    #     support_business_detail_mng_sum_hit.append(
    #         {
    #             "date": date,
    #             "number": len(HitLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date))
    #         }
    #     )
    #     support_business_detail_mng_avg_hit.append(
    #         {
    #             "date": date,
    #             "number": round(len(HitLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date)) /
    #                             len(SupportBusiness.objects.filter(support_business_author_id=support_business_author_id).exclude(Q(support_business_status="1") | Q(support_business_status="2")))
    #                             ,1)
    #         }
    #     )
    # result["opr_support_business_detail_mng_sum_hit"] = support_business_detail_mng_sum_hit
    # result["opr_support_business_detail_mng_avg_hit"] = support_business_detail_mng_avg_hit
    #
    #
    #
    # # 매니저가 작성한 모든 지원사업에 좋아요를 누른 데이터
    # support_business_favorite_date_ymd = []
    # support_business_mng_sum_favorite = []
    # support_business_mng_avg_favorite = []
    # for date_dict in FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(
    #         date__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("date").order_by(
    #         "-date").distinct():
    #     if date_dict["date"] not in support_business_favorite_date_ymd:
    #         support_business_favorite_date_ymd.append(date_dict["date"])
    # for date in support_business_favorite_date_ymd:
    #     support_business_mng_sum_favorite.append(
    #         {
    #             "date": date,
    #             "number": len(
    #                 FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date))
    #         }
    #     )
    #     support_business_mng_avg_favorite.append(
    #         {
    #             "date": date,
    #             "number": round(
    #                 len(FavoriteLog.objects.filter(support_business__in=support_business_mng_arr).filter(date=date)) /
    #                 len(SupportBusiness.objects.filter(
    #                     support_business_author_id=support_business_author_id).exclude(
    #                     Q(support_business_status="1") | Q(support_business_status="2")))
    #                 , 1)
    #         }
    #     )
    # result["opr_support_business_mng_sum_favorite"] = support_business_mng_sum_favorite
    # result["opr_support_business_mng_avg_favorite"] = support_business_mng_avg_favorite
    #
    #
    # # 매니저가 작성한 모든 지원사업의 지원자 데이터
    # support_business_favorite_date_ymd = []
    # support_business_mng_sum_appliance = []
    # support_business_mng_avg_appliance = []
    # for date_dict in Appliance.objects.filter(support_business__in=support_business_mng_arr).dates("appliance_update_at_ymdt","day").filter(
    #         appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("appliance_update_at_ymdt").order_by(
    #         "-appliance_update_at_ymdt").distinct():
    #
    #     if date_dict["appliance_update_at_ymdt"] not in support_business_favorite_date_ymd:
    #         support_business_favorite_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    #
    # for date in support_business_favorite_date_ymd:
    #     print(  Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date))
    #     support_business_mng_sum_appliance.append(
    #         {
    #             "date": date,
    #             "number": len(
    #                 Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date))
    #         }
    #     )
    #
    #     if len(SupportBusiness.objects.filter(
    #                     support_business_author_id=support_business_author_id).exclude(
    #                     Q(support_business_status="1") | Q(support_business_status="2")).filter(
    #                     support_business_update_at_ymdt__lte=date)) != 0:
    #         support_business_mng_avg_appliance.append(
    #         {
    #             "date": date,
    #             "number": round(
    #                 len(Appliance.objects.filter(support_business__in=support_business_mng_arr).filter(appliance_update_at_ymdt__date=date)) /
    #                 len(SupportBusiness.objects.filter(
    #                     support_business_author_id=support_business_author_id).exclude(
    #                     Q(support_business_status="1") | Q(support_business_status="2")))
    #                 , 1)
    #         }
    #         )
    #     else:
    #         support_business_mng_avg_appliance.append(
    #             {
    #                 "date": date,
    #                 "number": 0,
    #             }
    #         )
    # result["opr_support_business_mng_sum_appliance"] = support_business_mng_sum_appliance
    # result["opr_support_business_mng_avg_appliance"] = support_business_mng_avg_appliance
    #
    #
    # #  기관에서  작성한 모든 지원사업의 방문 데이터
    # #  매니저가 작성한 모든 지원사업
    # ad = AdditionalUserInfo.objects.get(id=support_business_author_id).additionaluserinfo_set.all()
    # author_list=[]
    # for a in ad:
    #     author_list.append(a.id)
    # support_business_kikwan_arr = SupportBusiness.objects.filter(support_business_author_id__in=author_list)
    #
    #
    # support_business_detail_hit_date_ymd = []
    # support_business_detail_kikwan_sum_hit = []
    # support_business_detail_kikwan_avg_hit = []
    # for date_dict in HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter( date__gte= str(support_business.support_business_update_at_ymdt).split(" ")[0] ).values("date").order_by(
    #         "-date").distinct():
    #     if date_dict["date"] not in support_business_detail_hit_date_ymd:
    #         support_business_detail_hit_date_ymd.append(date_dict["date"])
    # for date in support_business_detail_hit_date_ymd:
    #     support_business_detail_kikwan_sum_hit.append(
    #         {
    #             "date": date,
    #             "number": len(HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date))
    #         }
    #     )
    #     support_business_detail_kikwan_avg_hit.append(
    #         {
    #             "date": date,
    #             "number": round(len(HitLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date)) /
    #                             len(SupportBusiness.objects.filter(support_business_author_id__in=author_list).exclude(Q(support_business_status="1") | Q(support_business_status="2")))
    #                             ,1)
    #         }
    #     )
    # result["opr_support_business_detail_kikwan_sum_hit"] = support_business_detail_kikwan_sum_hit
    # result["opr_support_business_detail_kikwan_avg_hit"] = support_business_detail_kikwan_avg_hit
    #
    #
    #
    # # 기관에서 작성한 모든 지원사업에 좋아요를 누른 데이터
    # support_business_favorite_date_ymd = []
    # support_business_kikwan_sum_favorite = []
    # support_business_kikwan_avg_favorite = []
    # for date_dict in FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(
    #         date__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("date").order_by(
    #         "-date").distinct():
    #     if date_dict["date"] not in support_business_favorite_date_ymd:
    #         support_business_favorite_date_ymd.append(date_dict["date"])
    # for date in support_business_favorite_date_ymd:
    #     support_business_kikwan_sum_favorite.append(
    #         {
    #             "date": date,
    #             "number": len(
    #                 FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date))
    #         }
    #     )
    #     support_business_kikwan_avg_favorite.append(
    #         {
    #             "date": date,
    #             "number": round(
    #                 len(FavoriteLog.objects.filter(support_business__in=support_business_kikwan_arr).filter(date=date)) /
    #                 len(SupportBusiness.objects.filter(
    #                     support_business_author_id__in=author_list).exclude(
    #                     Q(support_business_status="1") | Q(support_business_status="2")))
    #                 , 1)
    #         }
    #     )
    # result["opr_support_business_kikwan_sum_favorite"] = support_business_kikwan_sum_favorite
    # result["opr_support_business_kikwan_avg_favorite"] = support_business_kikwan_avg_favorite
    #
    #
    #
    #
    # # 기관에서 작성한 모든 지원사업의 지원자 데이터
    # support_business_favorite_date_ymd = []
    # support_business_kikwan_sum_appliance = []
    # support_business_kikwan_avg_appliance = []
    # for date_dict in Appliance.objects.filter(support_business__in=support_business_kikwan_arr).dates("appliance_update_at_ymdt","day").filter(
    #         appliance_update_at_ymdt__gte=str(support_business.support_business_update_at_ymdt).split(" ")[0]).values("appliance_update_at_ymdt").order_by(
    #         "-appliance_update_at_ymdt").distinct():
    #
    #     if date_dict["appliance_update_at_ymdt"] not in support_business_favorite_date_ymd:
    #         support_business_favorite_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    # for date in support_business_favorite_date_ymd:
    #     print("넣기전")
    #     print(  Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date))
    #     support_business_kikwan_sum_appliance.append(
    #         {
    #             "date": date,
    #             "number": len(
    #                 Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date))
    #         }
    #     )
    #     print()
    #     support_business_kikwan_avg_appliance.append(
    #         {
    #             "date": date,
    #             "number": round(
    #                 len(Appliance.objects.filter(support_business__in=support_business_kikwan_arr).filter(appliance_update_at_ymdt__date=date)) /
    #                 len(SupportBusiness.objects.filter(
    #                     support_business_author_id__in=author_list).exclude(
    #                     Q(support_business_status="1") | Q(support_business_status="2")))
    #                 , 1)
    #         }
    #     )
    # result["opr_support_business_kikwan_sum_appliance"] = support_business_mng_sum_appliance
    # result["opr_support_business_kikwan_avg_appliance"] = support_business_mng_avg_appliance



    # 태그 추출
    ap = Appliance.objects.filter(support_business_id=request.GET.get("support_business_id")).values("startup")
    # 지원자의 지역 추출
    opr_ap_comtype_filter = []
    opr_ap_location_filter = []
    opr_ap_genre_filter = []
    opr_ap_area_filter = []
    result["opr_ap_area_filter"] = []
    k = 0
    for a in ap:
        filter = Startup.objects.get(id=a["startup"]).selected_company_filter_list.all()
        local_ap_company_kind_tag = []
        local_ap_local_tag = []
        company_kind=""
        local=[]
        for f in filter:
            if f.cat_1 == "기업형태":
                opr_ap_comtype_filter.append(f.filter_name)
                company_kind = f.filter_name
            if f.cat_1 == "소재지":
                opr_ap_location_filter.append(f.filter_name)
                local.append(f.filter_name)
            if f.cat_0 == "기본장르":
                opr_ap_genre_filter.append(f.filter_name)
            if f.cat_0 == "영역":
                opr_ap_area_filter.append(f.filter_name)

    result["opr_ap_startup_list"]=[]
    print(ap)
    temp_list = []
    for a in ap:
        temp_list.append(a["startup"])
    for a in set(temp_list):
        startup = Startup.objects.get(id=a)
        result["opr_ap_startup_list"].append({
            "startup_id":startup.id,
            "app_id":Appliance.objects.get(startup = startup, support_business= support_business).id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    result["opr_ap_comtype_filter"] = (organize(opr_ap_comtype_filter))
    result["opr_ap_location_filter"] = (organize(opr_ap_location_filter))
    result["opr_ap_genre_filter"] = (organize(opr_ap_genre_filter))
    result["opr_ap_area_filter"] = (organize(opr_ap_area_filter))



    opr_hit_comtype_filter = []
    opr_hit_location_filter = []
    opr_hit_genre_filter = []
    opr_hit_area_filter = []
    support_business_detail_hit = HitLog.objects.filter(
        support_business_id=request.GET.get("support_business_id")).values("user").distinct()
    k = 0
    result["opr_hit_startup_list"] = []

    for h in support_business_detail_hit:
        try:
            if Startup.objects.filter(user_id=AdditionalUserInfo.objects.get(id=h["user"]).user.id):
                filter = AdditionalUserInfo.objects.get(id=h["user"]).user.startup.selected_company_filter_list.all()
                local_hit_company_kind_tag = []
                local_hit_local_tag = []
                company_kind=""
                local=[]
                for f in filter:
                    if f.cat_1 == "기업형태":
                        opr_hit_comtype_filter.append(f.filter_name)
                        company_kind = f.filter_name
                    if f.cat_1 == "소재지":
                        opr_hit_location_filter.append(f.filter_name)
                        local.append(f.filter_name)
                    if f.cat_0 == "영역":
                        opr_hit_area_filter.append(f.filter_name)
                    if f.cat_0 == "기본장르":
                        opr_hit_genre_filter.append(f.filter_name)


                startup = AdditionalUserInfo.objects.get(id=h["user"]).user.startup
                result["opr_hit_startup_list"].append({
                    "startup_id":startup.id,
                    "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                    "company_kind": company_kind,
                    "local": ",".join(local),
                    "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
                })
                k = k + 1
        except:
            pass

    result["opr_hit_comtype_filter"] = (organize(opr_hit_comtype_filter))
    result["opr_hit_location_filter"] = (organize(opr_hit_location_filter))
    result["opr_hit_genre_filter"] = (organize(opr_hit_genre_filter))
    result["opr_hit_area_filter"] = (organize(opr_hit_area_filter))

    opr_aw_comtype_filter = []
    opr_aw_location_filter = []
    opr_aw_genre_filter = []
    opr_aw_area_filter = []
    aw_startup_list = []
    result["opr_aw_startup_list"] = []
    k = 0
    award = Award.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()
    for aw in award:
        filter = Startup.objects.get(id=aw["startup"]).selected_company_filter_list.all()
        local_aw_company_kind_tag = []
        local_aw_local_tag = []
        company_kind=""
        local=[]
        for f in filter:
            if f.cat_1 == "기업형태":
                opr_aw_comtype_filter.append(f.filter_name)
                company_kind=f.filter_name
            if f.cat_1 == "소재지":
                opr_aw_location_filter.append(f.filter_name)
                local.append(f.filter_name)
            if f.cat_0 == "기본장르":
                opr_aw_genre_filter.append(f.filter_name)
            if f.cat_0 == "영역":
                opr_aw_area_filter.append(f.filter_name)

        startup = Startup.objects.get(id=aw["startup"])
        result["opr_aw_startup_list"].append({
            "startup_id":startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    result["opr_aw_comtype_filter"] = (organize(opr_aw_comtype_filter))
    result["opr_aw_location_filter"] = (organize(opr_aw_location_filter))
    result["opr_aw_genre_filter"] = (organize(opr_aw_genre_filter))
    result["opr_aw_area_filter"] = (organize(opr_aw_area_filter))

    support_business = SupportBusiness.objects.filter(support_business_author_id=request.GET.get("id"))
    q_objects = Q()
    startup_list = []
    for s in support_business:
        q_objects = q_objects | Q(support_business_id=s.id)
    ap = Appliance.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()
    for a in ap:
        startup_list.append(a["startup"])
    support_business_detail_hit = HitLog.objects.filter(
        support_business_id=request.GET.get("support_business_id")).values("user").distinct()
    for h in support_business_detail_hit:
        try:
            if (Startup.objects.filter(user=AdditionalUserInfo.objects.get(id=h["user"]).user)).count() != 0:
                startup_list.append(Startup.objects.get(user=AdditionalUserInfo.objects.get(id=h["user"]).user).id)
        except:
            pass
    award = Award.objects.filter(support_business_id=request.GET.get("support_business_id")).values(
        "startup").distinct()

    opr_all_comtype_filter = []
    opr_all_location_filter = []
    opr_all_genre_filter = []
    opr_all_area_filter = []
    for aw in award:
        startup_list.append(aw["startup"])
    result["opr_all_startup_list"] = []
    k = 1
    for id in set(startup_list):
        filter = Startup.objects.get(id=id).selected_company_filter_list.all()
        startup = Startup.objects.get(id=id)
        try:
            submit_day=Appliance.objects.get(support_business_id=request.GET.get("support_business_id"),startup_id=id).appliance_update_at_ymdt
        except Exception as e:
            print(e)
            submit_day=""

        company_kind=""
        local=[]
        for f in filter:
            if f.cat_1 == "기업형태":
                opr_all_comtype_filter.append(f.filter_name)
                company_kind= f.filter_name
            if f.cat_1 == "소재지":
                opr_all_location_filter.append(f.filter_name)
                local.append(f.filter_name)
            if f.cat_0 == "기본장르":
                opr_all_genre_filter.append(f.filter_name)
            if f.cat_0 == "영역":
                opr_all_area_filter.append(f.filter_name)

        result["opr_all_startup_list"].append({
            "startup_id":startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": company_kind,
            "local": ",".join(local),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,"submit_day" : submit_day,
        })
        k = k + 1
    result["opr_all_comtype_filter"] = organize(opr_all_comtype_filter)
    result["opr_all_location_filter"] = organize(opr_all_location_filter)
    result["opr_all_genre_filter"] = organize(opr_all_genre_filter)
    result["opr_all_area_filter"] = organize(opr_all_area_filter)

    #
    # st = StatTable()
    # st.stat_user_id = request.GET.get("stat_user_id")
    # support_business = SupportBusiness.objects.get(id=request.GET.get("support_business_id"))
    # if support_business.support_business_status != 5 and support_business.support_business_author_id  == request.GET.get("id"):
    #     st.stat_name = "my_support_business_ing"
    # elif support_business.support_business_status == 5 and support_business.support_business_author_id  == request.GET.get("id"):
    #     st.stat_name = "my_support_business_end"
    # elif support_business.support_business_status != 5 and support_business.support_business_author_id != request.GET.get("id"):
    #     st.stat_name = "other_support_business_ing"
    # elif support_business.support_business_status == 5 and support_business.support_business_author_id  != request.GET.get("id"):
    #     st.stat_name = "other_support_business_end"

    #
    #
    # result_json = JsonResponse(result)
    # st.stat_json  =result_json.content
    # st.save()

    # return result_json
    return JsonResponse(result)

@csrf_exempt
@my_timer
def opr_vue_get_support_business_info(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    result = {}
    support_business_author_list  = []
    print(AdditionalUserInfo.objects.get(id= user_auth_id).child_list())
    print(datetime.now())
    for r in AdditionalUserInfo.objects.get(id= user_auth_id).child_list():
        support_business_author_list.append(r.id)
    #user_id = request.POST.get("id")
    end_support_business = SupportBusiness.objects.filter(support_business_apply_end_ymdt__lte=datetime.now()).filter(Q(support_business_status="4")|Q(support_business_status="3")).filter(
        support_business_author_id__in=support_business_author_list)

    end_set = []
    for support_business in end_support_business:

        result_end = {}
        result_end["opr_id"] = support_business.id
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["opr_status"] = "모집종료"
        result_end["opr_status_num"] = support_business.support_business_status

        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] = ""

        else:
            result_end["opr_comp"] = ""
        end_set.append(copy.deepcopy(result_end))

    waiting_support_business = SupportBusiness.objects.filter(support_business_status="2").filter( support_business_author_id__in=support_business_author_list)
    waiting_set = []
    for support_business in waiting_support_business:
        result_end = {}
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["opr_id"] = support_business.id
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt

        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end["opr_status"] = "승인대기"
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["opr_status_num"] = support_business.support_business_status
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] = str(
                    (Appliance.objects.filter(support_business_id=support_business.id).filter(
                        is_submit=True)).count()) + " : 1"
        else:
            result_end["opr_comp"] = str(
                (Appliance.objects.filter(support_business_id=support_business.id).filter(
                    is_submit=True)).count()) + " : 1"
        waiting_set.append(copy.deepcopy(result_end))


    # 공고중인 공고
    ing_support_business = SupportBusiness.objects.filter(support_business_status="3").filter(support_business_apply_end_ymdt__gte=datetime.now()).filter(
        support_business_author_id__in=support_business_author_list)
    ing_set = []
    for support_business in ing_support_business:
        result_end = {}
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["opr_id"] = support_business.id
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_status"] = "공고중"
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["opr_status_num"] = support_business.support_business_status
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] = ""
        else:
            result_end["opr_comp"] = ""
        ing_set.append(copy.deepcopy(result_end))

    # 공고 종료된 공고
    comp_support_business= SupportBusiness.objects.filter(support_business_status="5").filter(support_business_author_id__in=support_business_author_list)
    comp_set = []
    for support_business in comp_support_business:
        result_end = {}
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["opr_id"] = support_business.id
        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["opr_status"] = "공고종료"

        result_end["opr_status_num"] = support_business.support_business_status
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] = ""
        else:
            result_end["opr_comp"] = ""
        comp_set.append(copy.deepcopy(result_end))
    # 블라인드된 공고문
    blind_support_business = SupportBusiness.objects.filter(support_business_status="6").filter( support_business_author_id__in=support_business_author_list)
    blind_set = []
    for support_business in blind_support_business:
        result_end = {}
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end["opr_id"] = support_business.id
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        result_end["opr_status"] = "블라인드"
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_status_num"] = support_business.support_business_status
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] = str(
                    (Appliance.objects.filter(support_business_id=support_business.id).filter(
                        is_submit=True)).count()) + " : 1"
        else:
            result_end["opr_comp"] = str(
                (Appliance.objects.filter(support_business_id=support_business.id).filter(
                    is_submit=True)).count()) + " : 1"
        blind_set.append(copy.deepcopy(result_end))

    all_support_business = SupportBusiness.objects.filter( support_business_author_id__in=support_business_author_list).exclude(Q(support_business_status=None)|Q(support_business_status=1)|Q(support_business_status=6))

    all_set = []
    for support_business in all_support_business:
        result_end = {}
        result_end["opr_id"] = support_business.id
        result_end["opr_support_business_award_date_ymd"] = support_business.support_business_award_date_ymd
        result_end['opr_support_business_poster'] = support_business.support_business_poster
        result_end['opr_support_business_name'] = support_business.support_business_name
        result_end["opr_support_business_apply_start_ymd"] = support_business.support_business_apply_start_ymd
        result_end["opr_support_business_update_at_ymdt"] = support_business.support_business_update_at_ymdt
        result_end["opr_author"] = support_business.support_business_author.mng_name
        result_end["opr_status_num"] = support_business.support_business_status
        try:
            result_end["author"] = support_business.support_business_author.mng_name
        except Exception as e:
            print(e)
        result_end["opr_support_business_apply_end_ymdt"] = support_business.support_business_apply_end_ymdt
        result_end["opr_apply_num"] = (Appliance.objects.filter(support_business_id=support_business.id)).count()
        result_end["opr_favorite"] = (AdditionalUserInfo.objects.filter(favorite=support_business)).count()
        try:
            if support_business.support_business_status == "4":  # 작성중인 공고문
                result_end["opr_status"] = "모집종료"
            if support_business.support_business_status == "1":  # 작성중인 공고문
                result_end["opr_status"] = "작성중"
            if support_business.support_business_status == "2":  # 승인대기중인 공고문
                result_end["opr_status"] = "승인대기"
            if support_business.support_business_status == "3":
                result_end["opr_status"] = "공고중"
            if support_business.support_business_apply_end_ymdt < timezone.now() and support_business.support_business_status == "3":  # 모집 종료 된 공고문
                result_end["opr_status"] = "모집종료"
            if support_business.support_business_status == "5":  # 공고 종료 된 공고문
                result_end["opr_status"] = "공고종료"
            if support_business.support_business_status == "6":  # 블라인드 공고문
                result_end["opr_status"] = "블라인드"
        except:
            result_end["opr_status"] = "작성중"
        result_end["opr_open_date"] = (support_business.support_business_apply_start_ymd)
        if support_business.support_business_recruit_size != "" and support_business.support_business_recruit_size != 0 and support_business.support_business_recruit_size != None:
            try:
                number = str(round((
                    Appliance.objects.filter(support_business_id=support_business.id).filter(is_submit=True)).count() / int(
                    support_business.support_business_recruit_size), 1))
                if number == "0.0":
                    number = "0"
                result_end["opr_comp"] = number + " : 1"
                pass
            except:
                result_end["opr_comp"] =""
        else:
            result_end["opr_comp"] = ""
        all_set.append(copy.deepcopy(result_end))

    result["opr_end_set"] = end_set
    result["opr_blind_set"] = blind_set
    result["opr_writing_set"] = []
    result["opr_ing_set"] = ing_set
    result["opr_waiting_set"] = waiting_set
    result["opr_comp_set"] = comp_set
    result["opr_all_set"] = all_set

    return JsonResponse(result)

#------ (매니저) 지원사업 관리페이지 : 스타트업 리스트가 나타나게 해주는 함수 / 선정 대상자 리스트업
@csrf_exempt
@my_timer
def opr_vue_get_support_business_appliance(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    print("지원사업 아이디")
    print(request.GET.get("support_business"))
    support_business = SupportBusiness.objects.get(id=request.GET.get("support_business"))
    ap = Appliance.objects.filter(support_business=support_business).filter(is_submit=True)
    k=1
    result = []
    print("지원서 목록")
    print(ap)
    for a in ap :
        temp={}
        temp["opr_index"] = k
        k=k+1
        temp["opr_company_name"] = a.startup.company_name
        temp["opr_company_kind"] = a.startup.company_kind
        temp["opr_id"] = a.id
        temp["id"] = a.startup.id

        temp["opr_mark_name"] = a.startup.mark_name
        temp["opr_mark_email"] = a.startup.mark_email

        temp["opr_mark_tel"] = a.startup.mark_tel
        temp["opr_appliance_update_at_ymdt"] = a.appliance_update_at_ymdt
        temp["opr_down_path"] = a.id
        result.append(copy.deepcopy(temp))
        print(temp)
    print(result)
    return JsonResponse(result,safe=False)


@csrf_exempt
def index(request):
    print("blah")


@csrf_exempt
@my_timer
def vue_get_startup_public_detail(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    # startup= AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    startup = Startup.objects.get(id=request.GET.get("id"))
    result = {}
    result["back_img"] = startup.back_img
    result["logo"] = startup.logo
    result["company_website"] = startup.company_website
    result["company_id"] = startup.id

    result["is_favored"]= is_in_favor_list("startup", startup.id, user_auth_id)

    result["company_youtube"] = startup.company_youtube
    result["company_instagram"] = startup.company_instagram
    result["company_facebook"] = startup.company_facebook
    result["company_keyword"] = startup.company_keyword
    result["established_date"] = startup.established_date
    result["company_short_desc"] = startup.company_short_desc
    result["company_intro"] = startup.company_intro
    result["select_tag"] = []
    for f in startup.selected_company_filter_list.all():
        result["select_tag"].append(f.filter_name)
    result["startup_id"] = startup.id
    result["mark_tel"] = startup.mark_tel
    result["company_name"] = startup.company_name
    result["company_kind"] = startup.company_kind


    result["mark_name"] = startup.mark_name
    result["mark_email"] = startup.mark_email if startup.mark_email != "" else startup.user.username

    # result["logo"] = startup.clip_thumbnail_selected_company_filter_list

    result["information"] = {}
    result["information"]["id"] = startup.id
    result["information"]["tag"] = []
    result["support_business_tag"] = []
    for f in startup.selected_company_filter_list.all():
        if f.cat_0 == "지원형태":
            result["support_business_tag"].append(f.filter_name)
    result["select_tag"] = []

    for f in startup.selected_company_filter_list.all():
        result["information"]["tag"].append(f.filter_name)

    for t in startup.selected_company_filter_list.all():
        if t.filter_name != "" and t.filter_name != None:
            result["information"]["tag"].append(t.filter_name)
    result['information']["company_website"] = startup.company_website
    result["information"]["mark_email"] = startup.mark_email if startup.mark_email != "" else startup.user.username
    result["address_0"] = startup.address_0
    result["address_1"] = startup.address_1
    result["ip_chk"] = startup.ip_chk
    result["revenue_chk"] = startup.revenue_chk
    result["export_chk"] = startup.export_chk
    result["company_invest_chk"] = startup.company_invest_chk
    result["service"] = []

    result["tag"] = []
    result["pub_tag"] = []
    for f in startup.selected_company_filter_list.all():
        result["tag"].append(f.filter_name)
    for f in startup.selected_company_filter_list.all():
        if f.cat_0!="지원조건" and f.cat_1!="기업형태":
            result["pub_tag"].append(f.filter_name)

    for service in startup.service_set.all():
        obj = {}
        obj["service_intro"] = service.service_intro
        obj["service_file"] = service.service_file
        obj["file_name"] = service.service_file.split("/")[-1]
        obj["service_name"] = service.service_name
        obj["service_img"] = service.service_img
        obj["img_name"] = service.service_img.split("/")[-1]
        obj["id"] = service.id
        result["service"].append(copy.deepcopy(obj))
    result["company_history"] = []
    for history in startup.history_set.all():
        obj = {}
        obj["company_history_year"] = history.company_history_year
        obj["company_history_month"] = history.company_history_month
        obj["company_history_content"] = history.company_history_content
        obj["id"] = history.id
        result["company_history"].append(copy.deepcopy(obj))

    result["revenue_before_year_0"] = startup.revenue_before_year_0
    result["revenue_before_year_1"] = startup.revenue_before_year_1
    result["revenue_before_year_2"] = startup.revenue_before_year_2
    result["revenue_before_0"] = startup.revenue_before_0
    result["revenue_before_1"] = startup.revenue_before_1
    result["revenue_before_2"] = startup.revenue_before_2

    result["export_before_year_0"] = startup.export_before_year_0
    result["export_before_year_1"] = startup.export_before_year_1
    result["export_before_year_2"] = startup.export_before_year_2
    result["export_before_0"] = startup.export_before_0
    result["export_before_1"] = startup.export_before_1
    result["export_before_2"] = startup.export_before_2
    result["export_before_nation_0"] = startup.export_before_nation_0
    result["export_before_nation_1"] = startup.export_before_nation_1
    result["export_before_nation_2"] = startup.export_before_nation_2
    result["attached_cert_file"] = startup.attached_cert_file
    result["attached_ip_file"] = startup.attached_ip_file

    result["invest"] = []

    for invest in startup.companyinvest_set.all():
        obj = {}
        obj["company_invest_year"] = invest.company_invest_year
        obj["company_invest_size"] = invest.company_invest_size
        obj["company_invest_agency"] = invest.company_invest_agency
        result["invest"].append(copy.deepcopy(obj))

    result["news"] = []
    for news in startup.activity_set.order_by("-company_activity_created_at").all():
        obj = {}
        obj["company_activity_created_at"] = news.company_activity_created_at
        obj["company_activity_text"] = news.company_activity_text
        obj["company_activity_img"] = news.company_activity_img
        obj["company_activity_youtube"] = news.company_activity_youtube
        obj["like_num"] = (news.activitylike_set.all()).count()
        obj["rep_num"] = (news.reply_set.all()).count()
        obj["id"] = news.id

        obj["rep"] = []
        for rep in news.reply_set.all():
            temp = {}
            # temp["logo"] = rep.activity.startup.clip_thumbnail
            temp["company_activity_text"] = rep.company_activity_text
            temp["company_activity_created_at"] = rep.company_activity_created_at
            temp["id"] = rep.id
            obj["rep"].append(copy.deepcopy(temp))
        result["news"].append(copy.deepcopy(obj))
    print("end")
    return JsonResponse(result)


@csrf_exempt
@my_timer
def save_user_appliance_data_url(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    print(request.POST)
    data = request.POST.get("data")
    app = Appliance.objects.get(startup=AdditionalUserInfo.objects.get(id=user_auth_id).user.startup , support_business_id=request.POST.get("support_business_id"))
    # app.img_data_url = data
    imgdata = (data)
    print(data)
    binary_data = a2b_base64(imgdata.split(",")[1])
    filename = 'media/appliance/'+str(AdditionalUserInfo.objects.get(id=user_auth_id).user.startup.id)+'/'+str(app.id)+'/스타트업_지원서.png'
    if not os.path.exists( 'media/appliance/'+str(AdditionalUserInfo.objects.get(id=user_auth_id).user.startup.id)+'/'+str(app.id)):
        os.makedirs( 'media/appliance/'+str(AdditionalUserInfo.objects.get(id=user_auth_id).user.startup.id)+'/'+str(app.id))
    with open(filename, 'wb') as f:
        f.write(binary_data)
    app.img_data_url = filename
    app.save()
    return JsonResponse({"RESULT":"ok"})
import os
import zipfile



@csrf_exempt
@my_timer
def vue_get_startup_public_detail_news(request):
    print(request.GET.get("id"))
    # startup= AdditionalUserInfo.objects.get(id=request.GET.get("id")).user.startup
    startup = Startup.objects.get(id=request.GET.get("id"))
    result = {}

    result["news"] = []
    for news in startup.activity_set.order_by("-company_activity_created_at").all():
        obj = {}
        obj["company_activity_created_at"] = news.company_activity_created_at
        obj["company_activity_text"] = news.company_activity_text
        obj["company_activity_img"] = news.company_activity_img
        obj["company_activity_youtube"] = news.company_activity_youtube
        obj["like_num"] = (news.activitylike_set.all()).count()
        obj["rep_num"] = (news.reply_set.all()).count()
        obj["id"] = news.id

        obj["rep"] = []
        for rep in news.reply_set.all():
            temp = {}
            # temp["logo"] = rep.activity.startup.clip_thumbnail
            temp["company_activity_text"] = rep.company_activity_text
            temp["company_activity_created_at"] = rep.company_activity_created_at
            temp["id"] = rep.id
            obj["rep"].append(copy.deepcopy(temp))
        result["news"].append(copy.deepcopy(obj))
    print("end")
    return JsonResponse(result)

@csrf_exempt
@my_timer
def vue_get_kikwan_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    opr_account_set = []
    k = 1
    boss_id = AdditionalUserInfo.objects.get(id=user_auth_id).mng_boss_id
    opr_all_account_set = []
    for ac in AdditionalUserInfo.objects.filter(mng_boss_id=boss_id).order_by("-id"):
        temp = {}
        temp["mng_index"] = k
        k = k + 1
        temp["id"] = ac.user.username
        temp["mng_name"] = ac.mng_name
        temp["mng_position"] = ac.mng_position
        temp["mng_bonbu"] = ac.mng_bonbu
        temp["mng_kikwan"] = ac.mng_kikwan
        temp["mng_team"] = ac.mng_team
        temp["mng_tel"] = ac.mng_tel
        temp["mng_phone"] = ac.mng_phone
        temp["mng_email"] = ac.mng_email
        temp["mng_date_joined_ymd"] = ac.mng_date_joined_ymd
        opr_account_set.append(copy.deepcopy(temp))


    result = {}
    result["account_set"] = opr_account_set


    return JsonResponse(result, safe=False)


@csrf_exempt
@my_timer
def delete_channel(request):
    print(request.POST.get("del_num"))
    print(request.POST.get("del_target"))
    if request.POST.get("del_target") == "clip":
        Clip.objects.get(id=request.POST.get("del_num")).delete()
        print("clip delete!!!!!")

    if request.POST.get("del_target") == "course":
        Course.objects.get(id=request.POST.get("del_num")).delete()
        print("course delete!!!!!")

    if request.POST.get("del_target") == "path":
        Path.objects.get(id=request.POST.get("del_num")).delete()
        print("pathdelete!!!!!")



    return  JsonResponse({"result":"ok"})


@csrf_exempt
@my_timer
def vue_get_register_channel(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    if request.POST.get("target") == "path":
        RegisteredChannel.objects.get_or_create(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id), path=Path.objects.get(id=request.POST.get("id"))
        )
        return JsonResponse({"result":"ok"})
    if request.POST.get("target") == "course":
        RegisteredChannel.objects.get_or_create(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id),
                                                        course=Course.objects.get(id=request.POST.get("id"))
        )
        return JsonResponse({"result": "ok"})
    if request.POST.get("target") == "clip":
        RegisteredChannel.objects.get_or_create(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id),
                                                        clip=Clip.objects.get(id=request.POST.get("id"))
        )
        return JsonResponse({"result": "ok"})

@csrf_exempt
@my_timer
def vue_channel_register_check(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    if request.POST.get("target") == "path":
        result = RegisteredChannel.objects.filter(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id), path=Path.objects.get(id=request.POST.get("id"))
        )
        if (result).count() >0 :
            return JsonResponse({"result":"reg"})
        else :
            return  JsonResponse({"result":"no"})
    if request.POST.get("target") == "course":
        result = RegisteredChannel.objects.filter(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id)).filter(course=Course.objects.get(id=request.POST.get("id")) )
        if (result).count() > 0:
            return JsonResponse({"result": "reg"})
        else:
            return JsonResponse({"result": "no"})

    if request.POST.get("target") == "clip":
        result = RegisteredChannel.objects.filter(
            channel_user=AdditionalUserInfo.objects.get(id=user_auth_id),
                                                        clip=Clip.objects.get(id=request.POST.get("id"))
        )

        if (result).count() >0 :
            return JsonResponse({"result":"reg"})
        else :
            return  JsonResponse({"result":"no"})

@csrf_exempt
@my_timer
def vue_get_registerd_channel(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    result={}
    result["path_list"]=[]
    result["course_list"] =[]
    result["clip_list"]=[]
    for ch in RegisteredChannel.objects.filter(channel_user=AdditionalUserInfo.objects.get(id=user_auth_id)):
        if ch.path != None:
            p = ch.path
            t = {}
            t["path_title"] = p.path_title
            t["id"] = p.id
            t["path_created_at"] = p.path_created_at

            try:
                t["path_user"] = p.path_user.user.startup.mark_name
            except:
                t["path_user"] = p.path_user.mng_name
            t["path_total_play"] = p.path_total_play
            t["path_thumb"] = p.path_thumb
            t["path_percent"] = 0
            origin_length = int(p.path_total_play)
            view_num = (WatchHistory.objects.filter(
                watch_user=AdditionalUserInfo.objects.get(id=user_auth_id)) \
                           .filter(watch_path=p)).count() * 6
            try:
                per = round(view_num * 100 / origin_length,2)
                if(per > 100):
                    per = 100
            except:
                per=0
            t["path_percent"] = per
            t["path_entry_point"] = ""
            result["path_list"].append(copy.deepcopy(t))
        if ch.course != None:
            p=ch.course
            t = {}
            t["course_title"] = p.course_title
            t["id"] = p.id
            t["course_created_at"] = p.course_created_at
            try:
                t["course_user"] = p.course_user.user.startup.mark_name
            except:
                t["course_user"] = p.course_user.mng_name
            t["course_total_play"] = p.course_total_play
            t["course_thumb"] = p.course_thumb

            origin_length = int(p.course_total_play)
            view_num = (WatchHistory.objects.filter(
                watch_user=AdditionalUserInfo.objects.get(id=user_auth_id)) \
                           .filter(watch_course=p)).count() * 6
            try:
                per = round(view_num * 100 / origin_length,2)
                if (per > 100):
                    per = 100
                t["course_percent"] = per
            except:
                t["course_percent"]=""
            try:
                t["course_entry_point"] = ""
            except:
                pass
            result["course_list"].append(copy.deepcopy(t))
        if ch.clip != None:
            p = ch.clip
            t = {}
            t["clip_title"] = p.clip_title
            t["id"] = p.id
            t["clip_created_at"] = p.clip_created_at

            try:
                t["clip_user"] = p.clip_user.user.startup.mark_name
            except:
                t["clip_user"] = p.clip_user.mng_name

            t["clip_play"] = p.clip_play
            t["clip_thumb"] = p.clip_thumb

            origin_length = int(p.clip_play)
            view_num = (WatchHistory.objects.filter(
                watch_user=AdditionalUserInfo.objects.get(id=user_auth_id)) \
                           .filter(watch_clip=p)).count() * 6
            per = round(view_num * 100 / origin_length,2)
            if (per > 100):
                per = 100
            t["clip_percent"] = per
            try:
                t["clip_entry_point"] =""
            except:
                pass
            result["clip_list"].append(copy.deepcopy(t))

    return  JsonResponse(result, safe = False)

from django.http import HttpResponse
@csrf_exempt
@my_timer
def make_excel_kikwan(request):
    print(request.GET.get("id_list"))
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=support_business_list.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')


    support_business = SupportBusiness.objects.filter(id__in=request.GET.get("id_list").split(","))
    k = 0
    result_set = []
    for s in support_business:
        temp = {}
        temp["id"] = s.id
        ws.write( k , 0, str(k+1) )

        ws.write( k, 1, s.support_business_name )
        ws.write(k, 2, s.support_business_created_at_ymdt)
        ws.write(k, 3, s.support_business_author.mng_name)
        ws.write(k, 4, s.support_business_author.mng_team)
        ws.write(k, 5, s.support_business_author.mng_kikwan)
        ws.write(k, 6, s.support_business_author.mng_tel)
        ws.write(k,  7 ,(Appliance.objects.filter(support_business=s)).count())
        ws.write(k, 8, (Award.objects.filter(support_business=s)).count())

        try:

            if s.support_business_status == "1":
                ws.write(k, 9, "작성중")
            elif s.support_business_status == "2":
                ws.write(k, 9, "승인대기중")
            elif s.support_business_status == "3":
                ws.write(k, 9, "공고중")
            elif s.support_business_status == "4":
                ws.write(k, 9, "모집종료")
            elif s.support_business_status == "5":
                ws.write(k, 9, "공고종료")
            elif s.support_business_status == "6":
                ws.write(k, 9, "블라인드중")


            k = k + 1
        except Exception as e:
            print(e)
            print("error")
            status = ""

    wb.save(response)
    return response

@csrf_exempt
@my_timer
def excel_down_all_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=kikwan_account_list.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')
    k=0
    for ac in  AdditionalUserInfo.objects.filter(mng_boss=AdditionalUserInfo.objects.get(id=user_auth_id).mng_boss).order_by("-id"):
        temp={}
        ws.write(k, 0, k)
        ws.write(k, 1, ac.user.username)
        ws.write(k, 2, ac.mng_name)
        ws.write(k, 3, ac.mng_position)
        ws.write(k, 4, ac.mng_bonbu)
        ws.write(k, 5, ac.mng_kikwan)
        ws.write(k, 6, ac.mng_team)
        ws.write(k, 7, ac.mng_tel)
        ws.write(k, 8, ac.mng_phone)
        ws.write(k, 9, ac.mng_email)
        ws.write(k, 10, ac.mng_date_joined_ymd)
        k = k + 1
    wb.save(response)
    return response







@csrf_exempt
@my_timer
def vue_get_course_information(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result={}
    course = Course.objects.get(id=request.GET.get("course_id"))
    result["course_object"] = course.course_object
    result["course_info"] = course.course_info
    result["is_favored"] = ""
    result["course_author_id"] = course.course_user.id
    try :
        if course in AdditionalUserInfo.objects.get(id=user_auth_id).favorite_course.all():
            result["is_favored"] = True
        else:
            result["is_favored"] = False
    except:
        result["is_favored"] = False

    result["course_title"] = course.course_title
    result["course_rec_dur"] = course.course_rec_dur
    result["course_total_play"] = course.course_total_play
    result["course_created_at"] = course.course_created_at
    result["course_thumb"] = course.course_thumb
    result["course_id"] = course.id

    try:
        result["course_author"] = course.course_user.user.startup.mark_name

    except:
        result["course_author"] = course.course_user.mng_name
    result["course_filter"]=[]
    for filter in course.course_filter.all():
        print(filter)
        result["course_filter"].append(filter.name)

    result["course_clip"]=[]
    for clip in course.course_clips.all():
        obj = {}
        obj["clip_title"] = clip.clip_title
        obj["clip_created_at"] = clip.clip_created_at
        try:
            obj["clip_author"] = clip.clip_user.user.startup.mark_name
        except:
            obj["clip_author"] = clip.clip_user.mng_name
        obj["clip_thumb"] = clip.clip_thumb
        obj["clip_play"] = clip.clip_play
        obj["clip_id"] = clip.id
        result["course_clip"].append(copy.deepcopy(obj))


    return JsonResponse(result, safe=False)





@csrf_exempt
@my_timer
def vue_get_path_information(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result = {}
    path = Path.objects.get(id=request.GET.get("path_id"))
    result["path_object"] = path.path_object
    result["path_info"] = path.path_info
    result["path_title"] = path.path_title
    result["path_rec_dur"] = path.path_rec_dur
    result["path_total_play"] = path.path_total_play
    result["path_created_at"] = path.path_created_at
    result["is_favored"] = is_in_favor_list("path", path.id ,user_auth_id)
    result["path_author_id"] = path.path_user.id
    result["path_thumb"] = path.path_thumb
    result["path_id"] = path.id
    try:
        result["path_author"] = path.path_user.user.startup.mark_name
    except:
        result["path_author"] = path.path_user.mng_name
    result["path_filter"] = []

    for filter in path.path_filter.all():
        print(filter)
        result["path_filter"].append(filter.name)

    result["path_course"]=[]
    for course in path.path_course.all():
        obj_c={}
        obj_c["course_id"] = course.id
        obj_c["course_object"] = course.course_object
        obj_c["course_info"] = course.course_info
        obj_c["course_title"] = course.course_title
        obj_c["course_rec_dur"] = course.course_rec_dur
        obj_c["course_total_play"] = course.course_total_play
        obj_c["course_created_at"] = course.course_created_at
        obj_c["course_thumb"] = course.course_thumb
        try:
            obj_c["course_author"] = course.course_user.user.startup.mark_name
        except:
            obj_c["course_author"] = course.course_user.mng_name
        obj_c["course_entry_point"] = ""
        obj_c["course_filter"]=[]
        for filter in course.course_filter.all():
            print(filter)
            obj_c["course_filter"].append(filter.name)

        obj_c["course_clip"]=[]
        for clip in course.course_clips.all():
            obj = {}
            obj["clip_title"] = clip.clip_title
            obj["clip_created_at"] = clip.clip_created_at
            try:
                obj["clip_author"] = clip.clip_user.user.startup.mark_name
            except:
                obj["clip_author"] = clip.clip_user.mng_name
            obj["clip_thumb"] = clip.clip_thumb
            obj["clip_play"] = clip.clip_play
            obj["clip_id"] = clip.id
            obj_c["course_clip"].append(copy.deepcopy(obj))
        result["path_course"].append(copy.deepcopy(obj_c))

    print(result)
    return JsonResponse(result, safe=False)

@csrf_exempt
@my_timer
def vue_get_name(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    name = AdditionalUserInfo.objects.get(id=user_auth_id).user.startup.mark_name
    return JsonResponse({"name":name},safe=False)






@csrf_exempt
@my_timer
def excel_down_support_business_gwanri_ap(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=support_business.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')
    k=0
    startup_list = []
    for id in request.GET.get("id_list").split(","):
        startup_list.append(Startup.objects.get(id=id))
    for startup in startup_list :
        com_type_list = startup.selected_company_filter_list.all()
        com_type=""
        for filter in com_type_list:
            if(filter.cat_1=="기업형태"):
                com_type = filter.filter_name
        app = Appliance.objects.get(startup=startup, support_business_id=request.GET.get("support_business"))
        ws.write(k, 0, k+1)
        ws.write(k, 1, startup.company_name)
        ws.write(k, 2, com_type)
        ws.write(k, 3, startup.mark_name)
        ws.write(k, 4, startup.mark_tel)
        ws.write(k, 5, str(app.appliance_update_at_ymdt))
        k = k + 1
    wb.save(response)
    return response





@csrf_exempt
@my_timer
def excel_down_support_business_gwanri_fav(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=support_business_gwanri.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')
    k=0
    startup_list = []
    for id in request.GET.get("id_list").split(","):
        startup_list.append(Startup.objects.get(id=id))
    for startup in startup_list :
        com_type_list = startup.selected_company_filter_list.all()
        com_type=""
        for filter in com_type_list:
            if(filter.cat_1=="기업형태"):
                com_type = filter.filter_name

        ws.write(k, 0, k+1)
        ws.write(k, 1, startup.company_name)
        ws.write(k, 2, com_type)
        ws.write(k, 3, startup.mark_name)
        ws.write(k, 4, startup.mark_email)
        ws.write(k, 5, startup.mark_tel)
        ws.write(k, 6, startup.mark_email)
        k = k + 1
    wb.save(response)
    return response



@csrf_exempt
@my_timer
def excel_down_support_business_gwanri_aw(request):
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=support_business_gwanri.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet_1')
    k=0
    startup_list = []
    for id in request.GET.get("id_list").split(","):
        startup_list.append(Startup.objects.get(id=id))
    for startup in startup_list :
        ap = Appliance.objects.get(support_business_id=request.GET.get("support_business"), startup=startup)
        com_type_list = startup.selected_company_filter_list.all()
        com_type=""
        for filter in com_type_list:
            if(filter.cat_1=="기업형태"):
                com_type = filter.filter_name

        ws.write(k, 0, k+1)
        ws.write(k, 1, startup.company_name)
        ws.write(k, 2, com_type)
        ws.write(k, 3, startup.mark_name)
        ws.write(k, 4, startup.mark_email)
        ws.write(k, 5, startup.mark_tel)
        ws.write(k, 6, str(ap.appliance_update_at_ymdt))
        k = k + 1
    wb.save(response)
    return response

@my_timer
def vue_get_support_business_list_excel(request):
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
    sheet.write(0, 9, "선정기업수")
    sheet.write(0, 10, "상태")
    k = 1
    for s in sb:
        print(k)
        sheet.write(k, 1, k)
        sheet.write(k, 2, s.support_business_name)
        sheet.write(k, 3, s.support_business_author.mng_phone)
        sheet.write(k, 4, s.support_business_author.mng_tel)
        sheet.write(k, 5, s.support_business_author.mng_team)
        sheet.write(k, 6, "경기도 콘텐츠진흥원")
        sheet.write(k, 7, s.support_business_author.mng_phone)
        sheet.write(k, 8, (Appliance.objects.filter(support_business =s).filter(is_submit=True).count()))
        sheet.write(k, 9, (Award.objects.filter(support_business=s).count()))
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
        sheet.write(k, 10, mng_status)
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "지원사업 리스트.xls", safe='')
    book.save(response)
    return response


@my_timer
def vue_get_support_business_selected_list_excel(request):

    sb = SupportBusiness.objects.filter(id__in=request.GET.get("id_list").split(","))
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
    sheet.write(0, 9, "선정기업수")
    sheet.write(0, 10, "상태")

    k = 1
    for s in sb:
        print(k)
        sheet.write(k, 1, k)
        sheet.write(k, 2, s.support_business_name)
        sheet.write(k, 3, s.support_business_author.mng_phone)
        sheet.write(k, 4, s.support_business_author.mng_name)
        sheet.write(k, 5, s.support_business_author.mng_team)
        sheet.write(k, 6, "경기도 콘텐츠진흥원")
        sheet.write(k, 7, s.support_business_author.mng_phone)
        sheet.write(k, 8, (Appliance.objects.filter(support_business =s)).count())
        sheet.write(k, 9, (Award.objects.filter(support_business=s)).count())
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
        sheet.write(k, 10, mng_status)


        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "지원사업 리스트.xls", safe='')
    book.save(response)
    return response
#
# @csrf_exempt
# def download_file(request):

@csrf_exempt
@my_timer
def vue_get_download_usr_account(request):

    if request.GET.get("tbl")=="1":
        startup = Startup.objects.all()

        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "기업명")
        sheet.write(0, 3, "계정아이디")
        sheet.write(0, 4, "담당자")
        sheet.write(0, 5, "핸드폰번호")
        sheet.write(0, 6, "메일주소")
        sheet.write(0, 7, "소재지")
        sheet.write(0, 8, "구성원수")
        sheet.write(0, 9, "사업참가횟수")
        sheet.write(0, 10, "사업선정횟수")
        sheet.write(0, 11, "가입일")
        k = 1
        for s in startup:
            temp = {}
            temp["opr_index"] = k
            sheet.write(k, 1, k)

            sheet.write(k, 2, s.company_name)
            sheet.write(k, 3, s.user.username)
            sheet.write(k, 4, s.user.startup.mark_name)
            sheet.write(k, 5, s.user.startup.mark_tel)
            sheet.write(k, 6,s.user.startup.mark_email)
            tag_list = []
            for t in s.selected_company_filter_list.all():
                tag_list.append(t.filter_name)
            temp["opr_tag"] = tag_list
            try:
                if "경기" in s.address_0:
                    local = "경기"
                elif "서울" in s.address_0:
                    local = "서울"
                elif "인천" in s.address_0:
                    local = "인천"
                else:
                    local = "기타"
            except:
                local = "기타"

            sheet.write(k, 7, (local))
            sheet.write(k, 8, s.company_total_employee)
            sheet.write(k, 9, (Appliance.objects.filter(startup=s)).count())
            sheet.write(k, 10,(Award.objects.filter(startup=s)).count())
            sheet.write(k, 11,str(s.user.date_joined).split(" ")[0])
            k = k + 1

        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response
    if request.GET.get("tbl")=="2":
        aw_startup_set = Appliance.objects.all().values("startup").distinct()
        k = 1
        ap_set = []
        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "기업명")
        sheet.write(0, 3, "공고마감일")
        sheet.write(0, 4, "공고명")
        sheet.write(0, 5, "담당자")
        sheet.write(0, 6, "소재지")
        sheet.write(0, 7, "선정여부")

        for s in aw_startup_set:
            aw_st = {}
            startup = Startup.objects.get(id=s["startup"])
            sheet.write(k, 1, k)
            sheet.write(k, 2, startup.company_name)
            sheet.write(k, 3,   str(Appliance.objects.filter(
                startup=startup).last().support_business.support_business_apply_end_ymdt).split(" ")[0] )
            sheet.write(k, 4,   Appliance.objects.filter(
                startup=startup).last().support_business.support_business_name )
            sheet.write(k, 5,  startup.mark_name)


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
                local = "기타"
            sheet.write(k, 6,(local))
            aw_st["opr_support_business_name"] = Appliance.objects.filter(
                startup=startup).last().support_business.support_business_name
            if (Award.objects.filter(
                    support_business=Appliance.objects.filter(startup=startup).last().support_business).filter(
                    startup=startup)).count() == 0:
                aw_st["opr_awarded"] = "탈락"
            else:
                aw_st["opr_awarded"] = "선정"
            sheet.write(k, 7, aw_st["opr_awarded"] )
            k=k+1

        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response

    if request.GET.get("tbl") == "3":
        user_ad = AdditionalUserInfo.objects.exclude(auth="MNG").exclude(auth="OPR")

        user_set = []
        p = 1
        k=1
        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "회원 아이디")
        sheet.write(0, 3, "이름")
        sheet.write(0, 4, "핸드폰번호")
        sheet.write(0, 5, "SNS")
        sheet.write(0, 6, "가입일")

        for u in user_ad:
            try:
                user = {}
                user["opr_id"] = u.user.username
                repre_name = Startup.objects.get(user=u.user).mark_name
                username = u.user.username
                tel = Startup.objects.get(user=u.user).mark_tel
                date_joined =  u.user.date_joined

                sheet.write(k, 1, k)
                sheet.write(k, 2, username)
                sheet.write(k, 3, repre_name)
                sheet.write(k, 4, tel)
                sheet.write(k, 5, "")
                sheet.write(k, 6, str(date_joined).split(" ")[0])
                k=k+1


            except Exception as e:
                print(e)

                pass
        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response

@csrf_exempt
@my_timer
def vue_get_download_usr_account_selected(request):

    if request.GET.get("tbl")=="1":
        startup = Startup.objects.filter(id__in=request.GET.get("id_list").split(","))

        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "기업명")
        sheet.write(0, 3, "계정아이디")
        sheet.write(0, 4, "담당자")
        sheet.write(0, 5, "핸드폰번호")
        sheet.write(0, 6, "메일주소")
        sheet.write(0, 7, "소재지")
        sheet.write(0, 8, "구성원수")
        sheet.write(0, 9, "사업참가횟수")
        sheet.write(0, 10, "사업선정횟수")
        sheet.write(0, 11, "가입일")
        k = 1
        for s in startup:
            temp = {}
            temp["opr_index"] = k
            sheet.write(k, 1, k)

            sheet.write(k, 2, s.company_name)
            sheet.write(k, 3, s.user.username)
            sheet.write(k, 4, s.user.startup.mark_name)
            sheet.write(k, 5, s.user.startup.mark_tel)
            sheet.write(k, 6,s.user.startup.mark_email)
            tag_list = []
            for t in s.selected_company_filter_list.all():
                tag_list.append(t.filter_name)
            temp["opr_tag"] = tag_list
            try:
                if "경기" in s.address_0:
                    local = "경기"
                elif "서울" in s.address_0:
                    local = "서울"
                elif "인천" in s.address_0:
                    local = "인천"
                else:
                    local = "기타"
            except:
                local = "기타"

            sheet.write(k, 7, (local))
            sheet.write(k, 8, s.company_total_employee)
            sheet.write(k, 9, (Appliance.objects.filter(startup=s)).count())
            sheet.write(k, 10,(Award.objects.filter(startup=s)).count())
            sheet.write(k, 11, str(s.user.date_joined).split(" ")[0])
            k = k + 1

        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response
    if request.GET.get("tbl")=="2":
        aw_startup_set = Appliance.objects.all().values("startup").distinct()
        k = 1
        ap_set = []
        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "기업명")
        sheet.write(0, 3, "공고마감일")
        sheet.write(0, 4, "공고명")
        sheet.write(0, 5, "담당자")
        sheet.write(0, 6, "소재지")
        sheet.write(0, 7, "선정여부")

        for s in aw_startup_set:
            aw_st = {}
            startup = Startup.objects.get(id=s["startup"])
            print(s["startup"])
            if str(startup.id) in request.GET.get("id_list").split(","):
                sheet.write(k, 1, k)
                sheet.write(k, 2, startup.company_name)
                sheet.write(k, 3,   str(Appliance.objects.filter(
                    startup=startup).last().support_business.support_business_apply_end_ymdt).split(" ")[0] )
                sheet.write(k, 4,   Appliance.objects.filter(
                    startup=startup).last().support_business.support_business_name )
                sheet.write(k, 5,  startup.mark_name)


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
                    local = "기타"
                sheet.write(k, 6,(local))
                aw_st["opr_support_business_name"] = Appliance.objects.filter(
                    startup=startup).last().support_business.support_business_name
                if (Award.objects.filter(
                        support_business=Appliance.objects.filter(startup=startup).last().support_business).filter(
                        startup=startup)).count() == 0:
                    aw_st["opr_awarded"] = "탈락"
                else:
                    aw_st["opr_awarded"] = "선정"
                sheet.write(k, 7, aw_st["opr_awarded"] )
                k=k+1

        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response

    if request.GET.get("tbl") == "3":
        user_ad = AdditionalUserInfo.objects.exclude(auth="OPR").exclude(auth="MNG")

        user_set = []
        p = 1
        k=1
        f = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "회원 아이디")
        sheet.write(0, 3, "이름")
        sheet.write(0, 4, "핸드폰번호")
        sheet.write(0, 5, "SNS")
        sheet.write(0, 6, "가입일")

        for u in user_ad:
            try:
                if str(u.user.startup.id) in request.GET.get("id_list").split(","):
                    user = {}
                    user["opr_id"] = u.user.username
                    repre_name = Startup.objects.get(user=u.user).mark_name
                    username = u.user.username
                    tel = Startup.objects.get(user=u.user).mark_tel
                    date_joined = u.user.date_joined
                    sheet.write(k, 1, k)
                    sheet.write(k, 2, username)
                    sheet.write(k, 3, repre_name)
                    sheet.write(k, 4, tel)
                    sheet.write(k, 5, "")
                    sheet.write(k, 6, str(date_joined).split(" ")[0])
                    k = k + 1
            except Exception as e:
                print(e)
                pass
        book.save(f)
        out_content = f.getvalue()
        response = HttpResponse(content_type='application/force-download')
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
            "회원 리스트.xls", safe='')
        book.save(response)
        return response

from binascii import a2b_base64
@csrf_exempt
@my_timer
def download_appliance(request):

    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = []

    appliance_id = request.GET.get("appliance_id")
    app = Appliance.objects.get(id=appliance_id)
    sb = app.support_business
    filelist = sb.support_business_meta
    if "file_0" in filelist:
        filenames.append(app.attached_ir_file)
    if "file_1" in filelist:
        filenames.append(app.attached_cert_file)
    if "file_2" in filelist:
        filenames.append(app.attached_tax_file)
    if "file_3" in filelist:
        filenames.append(app.attached_fund_file)
    if "file_4" in filelist:
        filenames.append(app.attached_ppt_file)
    if "file_5" in filelist:
        filenames.append(app.attached_ip_file)
    if "file_6" in filelist:
        filenames.append(app.attached_etc_file)

    try:
        imgdata =(app.img_data_url)
        filenames.append(imgdata)
    except:
        pass

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    zip_subdir = "지원서 "
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        try:
            print(filenames)
            print("경로"+fpath)
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            print(fname)
            print(zip_path)
            # Add file, at correct path
            zf.write(fpath, zip_path)
        except:
            pass
    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp


@csrf_exempt
@my_timer
def get_realtime_support_business_appliance(request):
    support_business_id = request.GET.get("support_business_id")
    print("==========================")
    print(support_business_id)
    support_business = SupportBusiness.objects.get(id=support_business_id)
    support_business_appliance_date_ymd = []
    support_business_appliance = []
    result={}
    result["support_business_min_date"] =  str(SupportBusiness.objects.get(id=support_business_id).support_business_apply_start_ymd).split(" ")[0]
    for date_dict in Appliance.objects.filter(support_business=support_business).filter(is_submit=True).\
            dates("appliance_update_at_ymdt","day").values("appliance_update_at_ymdt").order_by("-appliance_update_at_ymdt").distinct():
        if date_dict["appliance_update_at_ymdt"] not in support_business_appliance_date_ymd:
            support_business_appliance_date_ymd.append(date_dict["appliance_update_at_ymdt"])
    for date in support_business_appliance_date_ymd:
        support_business_appliance.append(
            {
                "date": date,
                "number": (Appliance.objects.filter(support_business=support_business).filter(appliance_update_at_ymdt__date=str(date))).count()
            }
        )
    result["support_business_appliance"] = support_business_appliance
    return JsonResponse(result)

@csrf_exempt
@my_timer
def mng_vue_get_support_business_list(request):
    support_business = SupportBusiness.objects.exclude(support_business_status="1")
    k = 0
    result_set = []
    for s in support_business:
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
        temp["mng_apply_num"] = (Appliance.objects.filter(support_business=s).filter(is_submit=True)).count()
        temp["mng_award_num"] = (Award.objects.filter(support_business=s)).count()
        opr_status = ""
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
        result_set.append(copy.deepcopy(temp))

    return JsonResponse(result_set, safe=False)

@csrf_exempt
@my_timer
def mng_vue_get_kikwan_account(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    opr_account_set = []
    k = 1
    opr_all_account_set = []
    result={}
    boss_id = AdditionalUserInfo.objects.get(id = request.POST.get("id")).mng_boss_id

    for ac in AdditionalUserInfo.objects.filter(mng_boss_id=boss_id).order_by("-id"):
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
        opr_account_set.append(copy.deepcopy(temp))
    k = 1

    result["opr_account_set"] = opr_account_set

    return JsonResponse(result, safe=False)


@csrf_exempt
@my_timer
def opr_vue_get_kikwan_account_excel(request):
    opr_account_set = []
    k = 1
    opr_all_account_set = []
    result = {}

    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("회원 리스트")
    sheet.write(0, 1, "순서")
    sheet.write(0, 2, "계정 아이디")
    sheet.write(0, 3, "이름")
    sheet.write(0, 4, "직급")
    sheet.write(0, 5, "본부")
    sheet.write(0, 6, "기관")
    sheet.write(0, 7, "연락처")
    sheet.write(0, 8, "메일주소")
    sheet.write(0, 9, "가입일")
    for ac in boss.additionaluserinfo_set.all().order_by("-id"):
        temp = {}
        temp["mng_index"] = k


        sheet.write(k, 1,k)
        sheet.write(k, 2,  ac.user.username)
        sheet.write(k, 3 , ac.mng_name)
        sheet.write(k, 4, ac.mng_position)
        sheet.write(k, 5,  ac.mng_bonbu)
        sheet.write(k, 6, ac.mng_kikwan)
        sheet.write(k, 7, ac.mng_team)
        sheet.write(k, 8, ac.mng_tel)
        sheet.write(k, 9, ac.mng_phone)
        sheet.write(k, 10, ac.mng_email)
        sheet.write(k, 11, ac.mng_date_joined_ymd)
        k = k + 1

    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "기관내회원 리스트.xls", safe='')
    book.save(response)
    return response


# 포스트맨 정상작동
@csrf_exempt
@my_timer
def mng_vue_get_kikwan_account_excel(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id = check_result

    opr_account_set = []
    k = 1
    opr_all_account_set = []
    result = {}
    if( AdditionalUserInfo.objects.get(id=user_auth_id).mng_boss_id):
        boss_id = AdditionalUserInfo.objects.get(id=user_auth_id).mng_boss_id
    else:
        boss_id = AdditionalUserInfo.objects.get(id=user_auth_id).id
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("회원 리스트")
    sheet.write(0, 1, "순서")
    sheet.write(0, 2, "계정 아이디")
    sheet.write(0, 3, "이름")
    sheet.write(0, 4, "직급")
    sheet.write(0, 5, "본부")
    sheet.write(0, 6, "기관")
    sheet.write(0, 7, "팀")
    sheet.write(0, 8, "연락처")
    sheet.write(0, 9, "핸드폰번호")
    sheet.write(0, 10, "메일주소")
    sheet.write(0, 11, "가입일")
    for ac in AdditionalUserInfo.objects.filter(mng_boss_id=boss_id).order_by("-id"):
        print(ac.user.username)
        temp = {}
        temp["mng_index"] = k
        sheet.write(k, 1,k)
        sheet.write(k, 2,   ac.user.username)
        sheet.write(k, 3 , ac.mng_name)
        sheet.write(k, 4, ac.mng_position)
        sheet.write(k, 5,  ac.mng_bonbu)
        sheet.write(k, 6, ac.mng_kikwan)
        sheet.write(k, 7, ac.mng_team)
        sheet.write(k, 8, ac.mng_tel)
        sheet.write(k, 9, ac.mng_phone)
        sheet.write(k, 10, ac.mng_email)
        sheet.write(k, 11, str(ac.mng_date_joined_ymd).split(" ")[0])
        k = k + 1
    if  not (AdditionalUserInfo.objects.get(id=user_auth_id).mng_boss_id):
        sheet = book.add_sheet("전체 회원 리스트")
        sheet.write(0, 1, "순서")
        sheet.write(0, 2, "계정 아이디")
        sheet.write(0, 3, "이름")
        sheet.write(0, 4, "직급")
        sheet.write(0, 5, "본부")
        sheet.write(0, 6, "기관")
        sheet.write(0, 7, "팀")
        sheet.write(0, 8, "연락처")
        sheet.write(0, 9, "핸드폰번호")
        sheet.write(0, 10, "메일주소")
        sheet.write(0, 11, "가입일")
        k=1
        for ac in AdditionalUserInfo.objects.exclude(auth="USR").order_by("-id"):
            print(ac.user.username)
            temp = {}
            temp["mng_index"] = k
            sheet.write(k, 1, k)
            sheet.write(k, 2, ac.user.username)
            sheet.write(k, 3, ac.mng_name)
            sheet.write(k, 4, ac.mng_position)
            sheet.write(k, 5, ac.mng_bonbu)
            sheet.write(k, 6, ac.mng_kikwan)
            sheet.write(k, 7, ac.mng_team)
            sheet.write(k, 8, ac.mng_tel)
            sheet.write(k, 9, ac.mng_phone)
            sheet.write(k, 10, ac.mng_email)
            sheet.write(k, 11, str(ac.mng_date_joined_ymd).split(" ")[0])
            k = k + 1
    book.save(f)
    out_content = f.getvalue()
    response = HttpResponse(content_type='application/force-download')
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
        "기관 회원 리스트.xls", safe='')
    book.save(response)
    return response





@csrf_exempt
@my_timer
def vue_get_channel_static(request):
    id= request.GET.get("id")
    result={}
    if request.GET.get("channel")=="1":  # 강좌 인 경우..

        date_arr = []
        favorite_by_date = []
        for date_dict in Favoritelog.objects.filter(favorite_clip_id=id).values("favorite_date").order_by(
                "-favorite_date").distinct():
            if date_dict["favorite_date"] not in date_arr:
                date_arr.append(date_dict["favorite_date"])
        print(date_arr)
        for date in date_arr:
            favorite_by_date.append(
                {
                    "date": date, "number": (
                    Favoritelog.objects.filter(favorite_clip_id=id).filter(favorite_date=date)).count()
                }
            )
        result["favorite_by_date"] = favorite_by_date
        print(result)
        startup_list = []
        for favored_startup in FavoriteLog.objects.filter(
                favorite_clip_id=id).values("favorite_user_id").distinct():
            print(favored_startup)
            startup_list.append(
                Startup.objects.get(user=AdditionalUserInfo.objects.get(id=favored_startup["favorite_user_id"]).user))
        favored_comtype_filter = []
        favored_location_filter = []
        favored_genre_filter = []
        favored_area_filter = []
        result["favored_startup_list"] = []
        k = 1
        # 작업중
        for startup in startup_list:
            filter_list = startup.selected_company_filter_list.all()
            company_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    favored_comtype_filter.append(filter.filter_name)
                    company_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    favored_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    favored_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    favored_area_filter.append(filter.filter_name)
            result["favored_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "repre_tel": startup.mark_tel
            })
            k = k + 1
        result["favored_comtype_filter"] = (organize(favored_comtype_filter))
        result["favored_location_filter"] = (organize(favored_location_filter))
        result["favored_genre_filter"] = (organize(favored_genre_filter))
        result["favored_area_filter"] = (organize(favored_area_filter))




        date_arr = []
        hit_by_date = []
        for date_dict in HitClipLog.objects.filter(hit_clip_id=id).values("hit_clip_date").order_by(
                "-hit_clip_date").distinct():
            if date_dict["hit_clip_date"] not in date_arr:
                date_arr.append(date_dict["hit_clip_date"])
        print(date_arr)
        for date in date_arr:
            hit_by_date.append(
                {
                    "date": date, "number": (
                    HitClipLog.objects.filter(hit_clip_id=id).filter(hit_clip_date=date)).count()
                }
            )
        result["hit_by_date"] = hit_by_date
        print(result)
        startup_list = []
        for target_startup in HitClipLog.objects.filter(
                hit_clip_id=id).values("hit_clip_user_id").distinct():
            print(target_startup)
            startup_list.append(
                Startup.objects.get(user=AdditionalUserInfo.objects.get(id=target_startup["hit_clip_user_id"]).user))
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        result["hit_startip_list"] = []
        k = 1

        for startup in startup_list:
            filter_list = startup.selected_company_filter_list.all()
            company_kind = ""
            local = []
            for filter in filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                    company_kind = filter.filter_name
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                    local.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
            result["favored_startup_list"].append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        result["hit_comtype_filter"] = (organize(hit_comtype_filter))
        result["hit_location_filter"] = (organize(hit_location_filter))
        result["hit_genre_filter"] = (organize(hit_genre_filter))
        result["hit_area_filter"] = (organize(hit_area_filter))

        print(result)

@csrf_exempt
@my_timer
def vue_get_course_all(request):
    result = []
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""

    for c in Course.objects.all().order_by("-id"):
        temp={}
        temp["id"] = c.id
        try:

            temp["course_entry_point"] = "/channel/course/view/"+ str(c.id)+"/" + str(c.course_clips.all().first().id)
        except Exception as e:
            print(e)
            print(c.course_clips.all())
            print(c.course_clips.all().first())
            temp["course_entry_point"]=""
        try:
            temp["course_user"]=c.course_user.user.startup.mark_name
        except:
            temp["course_user"] = c.course_user.mng_name
        temp["course_thumb"]=c.course_thumb
        temp["course_id"] = c.id
        temp["label"] = c.course_title
        temp["value"] = c.id
        temp["is_favored"] = is_in_favor_list("course", c.id, user_auth_id)

        temp["course_title"]=c.course_title
        temp["course_rec_dur"]=c.course_rec_dur
        temp["course_created_at"]=c.course_created_at
        temp["course_info"] = c.course_info
        temp["course_tag"] =[]
        temp["course_total_play"] = c.course_total_play
        for t in c.course_filter.all():
            temp["course_tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)


# -------[[모든 패스리스트 가지고 오기]]----------
@csrf_exempt
@my_timer
def vue_get_path_all(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""

    result = []
    for c in Path.objects.all().order_by("-id"):
        temp={}
        temp["id"] = c.id
        try:
            temp["path_entry_point"] = "/channel/path/view/"+ str(c.id)+"/"+ str(c.path_course.all().first().id) + "/"+ str(c.path_course.first().course_clips.all().first().id)
        except Exception as e:
            print(e)
            temp["path_entry_point"]=""
        try:
            temp["path_user"]=c.path_user.user.startup.mark_name
        except:
            temp["path_user"] = c.path_user.mng_name
        temp["path_thumb"]=c.path_thumb
        temp["path_title"]=c.path_title
        temp["path_rec_dur"]=c.path_rec_dur
        temp["label"] = c.path_title
        temp["value"] = c.id

        temp["is_favored"] = is_in_favor_list("path", c.id, user_auth_id)

        temp["path_total_play"] = c.path_total_play
        temp["path_id"] = c.id
        temp["path_created_at"]=c.path_created_at
        temp["path_info"] = c.path_info
        temp["path_tag"] =[]
        for t in c.path_filter.all():
            temp["path_tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)

# ------ postman정상작동
@csrf_exempt
@my_timer
def get_favorite_startup(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    usr_id= user_auth_id
    add  = AdditionalUserInfo.objects.get(id=usr_id)
    result=[]
    for a in add.favorite_startup.all():

        filter=[]
        for t in a.selected_company_filter_list.all():
            if t.cat_0 !="조건" and t.cat_0 != "지원형태":
                filter.append(t.filter_name)
        is_favored=""
        try:
            is_favored =  is_in_favor_list("startup",a.id, usr_id)
        except  Exception as e:
            print(e)
            is_favored =  False

        result.append({
            "company_name": a.company_name,
            "company_short_desc": a.company_short_desc,
            "filter":filter, "logo": a.logo, "is_favored" : is_favored,
            "id":a.id
        })
    return JsonResponse(result, safe=False, )



@csrf_exempt
@my_timer
def vue_get_startup_list_sample(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""

    startup = Startup.objects.exclude(company_name="").exclude(company_name=None).order_by("?")[:3]
    result = []
    for s in startup:
        temp_obj = {}
        temp_obj["company_name"] = s.company_name
        temp_obj["company_short_desc"] = s.company_short_desc
        temp_obj["logo"] = s.logo

        temp_obj["is_favored"] = is_in_favor_list("startup", s.id, user_auth_id)

        temp_obj["tag"] = []
        temp_obj["id"] = s.id
        temp_obj["filter"] = []
        temp_obj["filter"] = []

        for t in s.selected_company_filter_list.all():
            if t.cat_0 != "지원형태" and t.cat_1 !="기업형태":
                temp_obj["filter"].append(t.filter_name)

        result.append(copy.deepcopy(temp_obj))



    return JsonResponse(list(result), safe=False)


@csrf_exempt
@my_timer
def vue_get_clip_all(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""

    result = []
    for c in Clip.objects.all().order_by("-id"):
        temp={}
        temp["clip_id"] = c.id
        try:
            temp["clip_user"]=c.clip_user.user.startup.mark_name
        except:
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_thumb"]=c.clip_thumb
        temp["clip_title"]=c.clip_title
        temp["clip_play"]=c.clip_play
        temp["clip_created_at"]=c.clip_created_at
        temp["clip_info"] = c.clip_info
        temp["clip_tag"] =[]
        temp["is_favored"] = is_in_favor_list( "clip", c.id  , user_auth_id )
        temp["clip_entry_point"] ="/channel/clip/view/"+str(c.id)
        # 채널 통계에서 사용되는 레이블과 value
        temp["label"] = c.clip_title
        temp["value"] = c.id

        temp["tag"]=[]
        for t in c.clip_filter.all()  :
            temp["tag"].append(t.name)
        result.append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)


@csrf_exempt
@my_timer
def get_channel_content(request):
    check_result = gca_check_session(request)
    if check_result:
        user_auth_id = check_result
    else:
        user_auth_id = ""
    result={}
    result["clip"]=[]
    result["course"]=[]
    result["path"]=[]
    for c in Clip.objects.all().order_by("-id"):
        temp = {}
        temp["clip_id"] = c.id
        try:
            temp["clip_user"] = c.clip_user.user.startup.mark_name
        except:
            temp["clip_user"] = c.clip_user.mng_name
        temp["clip_thumb"] = c.clip_thumb
        temp["clip_title"] = c.clip_title
        temp["clip_play"] = c.clip_play
        temp["clip_created_at"] = c.clip_created_at
        temp["clip_info"] = c.clip_info
        temp["clip_tag"] = []
        temp["is_favored"] = is_in_favor_list("clip", c.id, user_auth_id)
        temp["clip_entry_point"] = "/channel/clip/view/" + str(c.id)
        # 채널 통계에서 사용되는 레이블과 value
        temp["label"] = c.clip_title
        temp["value"] = c.id
        temp["tag"] = []
        for t in c.clip_filter.all():
            temp["tag"].append(t.name)
        result["clip"].append(copy.deepcopy(temp))
    for c in Course.objects.all().order_by("-id"):
        temp = {}
        temp["id"] = c.id
        try:
            temp["course_entry_point"] = "/channel/course/view/" + str(c.id) + "/" + str(
                c.course_clips.all().first().id)
        except Exception as e:
            temp["course_entry_point"] = ""
        try:
            temp["course_user"] = c.course_user.user.startup.mark_name
        except:
            temp["course_user"] = c.course_user.mng_name
        temp["course_thumb"] = c.course_thumb
        temp["course_id"] = c.id
        temp["label"] = c.course_title
        temp["value"] = c.id
        temp["is_favored"] = is_in_favor_list("course", c.id, user_auth_id)
        temp["course_title"] = c.course_title
        temp["course_rec_dur"] = c.course_rec_dur
        temp["course_created_at"] = c.course_created_at
        temp["course_info"] = c.course_info
        temp["course_tag"] = []
        temp["course_total_play"] = c.course_total_play
        for t in c.course_filter.all():
            temp["course_tag"].append(t.name)
        result["course"].append(copy.deepcopy(temp))

    for c in Path.objects.all().order_by("-id"):
        temp = {}
        temp["id"] = c.id
        try:
            temp["path_entry_point"] = "/channel/path/view/" + str(c.id) + "/" + str(
                c.path_course.all().first().id) + "/" + str(c.path_course.first().course_clips.all().first().id)
        except Exception as e:
            temp["path_entry_point"] = ""
        try:
            temp["path_user"] = c.path_user.user.startup.mark_name
        except:
            temp["path_user"] = c.path_user.mng_name
        temp["path_thumb"] = c.path_thumb
        temp["path_title"] = c.path_title
        temp["path_rec_dur"] = c.path_rec_dur
        temp["label"] = c.path_title
        temp["value"] = c.id
        temp["is_favored"] = is_in_favor_list("path", c.id, user_auth_id)
        temp["path_total_play"] = c.path_total_play
        temp["path_id"] = c.id
        temp["path_created_at"] = c.path_created_at
        temp["path_info"] = c.path_info
        temp["path_tag"] = []
        for t in c.path_filter.all():
            temp["path_tag"].append(t.name)
        result["path"].append(copy.deepcopy(temp))
    return JsonResponse(result, safe=False)




@csrf_exempt
@my_timer
def add_favorite_startup(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    ad = AdditionalUserInfo.objects.get(id=user_id)
    startup_id = request.GET.get("startup_id")
    startup = Startup.objects.get(id=startup_id)
    result = ""
    if startup not in ad.favorite_startup.all():
        ad.favorite_startup.add(startup)
        FavoriteLog.objects.filter(startup=startup).filter(user=ad).delete()
        result = "add"

    return JsonResponse({"result":result})

@csrf_exempt
@my_timer
def remove_favorite_startup(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    user_id = user_auth_id
    ad = AdditionalUserInfo.objects.get(id=user_id)
    startup_id = request.GET.get("startup_id")
    startup = Startup.objects.get(id=startup_id)
    result = ""
    if startup in ad.favorite_startup.all():
        ad.favorite_startup.remove(startup)
        FavoriteLog.objects.filter(startup=startup).filter(user=ad).delete()
        result = "remove"

    return JsonResponse({"result":result})





from PIL import Image

# -*- coding: utf-8 -*-
from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from decimal import Decimal
@csrf_exempt
def make_pdf(request):
    imgdata =request.POST.get("data")
    binary_data = a2b_base64(imgdata.split(",")[1])
    filename = 'media/test.png'  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(binary_data)
    im = Image.open(filename)
    imgwidth, imgheight = im.size

    k=0
    print(request.POST.get("height_array"))
    height_arr = request.POST.get("height_array").split(",")
    output_height_arr = []
    for i in range(0,len(height_arr)-1):
        print(height_arr[i])
        print(str(height_arr[i+1]) + "///")
        box = ( 130, int(height_arr[i]), imgwidth, int(height_arr[i+1]))
        percent=0.5
        a = im.crop(box)
        try:

            a = a.resize((int(imgwidth * percent), int( (int(height_arr[(i +1)]) - int(height_arr[(i)]) ) * percent)), Image.ANTIALIAS)
            output_height_arr.append(int( (int(height_arr[(i +1)]) - int(height_arr[(i)]) ) * percent))
            a.save(os.path.join("TESTIMG-%s.png" % k))
            k=k+1
        except:
            box = (0, i, imgwidth, imgheight)
            a = im.crop(box)
            a = a.resize((int(imgwidth * percent), int(int(height_arr[(8)]) * percent)))
            a.save(os.path.join("TESTIMG-%s.png" % k))

    path = os.path.join('TESTIMG-{0}.png')   # path.format(num)
    pdf = PdfFileWriter()
    for num in range(0, 8):
        per=1
        imgTemp = BytesIO()
        imgDoc = canvas.Canvas(imgTemp, pagesize=A4)
        # Draw image on Canvas and save PDF in buffer
        imgDoc.drawImage(path.format(num), 0, 0, width=imgwidth*0.5, height=output_height_arr[num]*per)
        # x, y - start position
        # in my case -25, -45 needed
        imgDoc.save()
        # Use PyPDF to merge the image-PDF into the template
        pdf.addPage(PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0))

    pdf.write(open("output.pdf", "wb"))


@csrf_exempt
@my_timer
def appliance_delete_service(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_id =  check_result
    try:
        print(request.POST)
        print(ApplianceService.objects.get(id= request.POST.get("id")))
        ApplianceService.objects.get(id=request.POST.get("id")).delete()
    except Exception as e :
        print(e)
    return JsonResponse({"result":"ok"})


@csrf_exempt
@my_timer
def email_check(request):
    num = (User.objects.filter(username=request.POST.get("email"))).count()
    if num == 0:
        return JsonResponse({"result":"ok"})
    else:
        return JsonResponse({"result": "exist"})


@csrf_exempt
@my_timer
def get_usr_filter(request):
    print("hahaha")
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    usr_acc = AdditionalUserInfo.objects.get(id=user_auth_id)
    usr_startup,created = Startup.objects.get_or_create(user = usr_acc.user)
    filter = usr_startup.selected_company_filter_list.all()
    filter_list = []
    if request.POST.get("kind") == "support_business":
        for f in filter:
            filter_list.append(f.filter_name)
    elif request.POST.get("kind") == "startup":
        for f in filter:
            if f.cat_0 != "지원형태":
                filter_list.append(f.filter_name)
    if usr_startup.company_total_employee != None and  usr_startup.company_total_employee  !="" and  usr_startup.company_total_employee != "0":
        filter_list.append( str(usr_startup.company_total_employee) +"명 이하")
                
    return JsonResponse({"result":filter_list})

@csrf_exempt
@my_timer
def get_usr_appliance_check(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    add = AdditionalUserInfo.objects.get(id=user_auth_id)
    startup = Startup.objects.get(user=add.user)
    result = {}
    if (Appliance.objects.filter(support_business_id=request.POST.get("support_business_id"))).count() > 0:
        result["is_applied"] = True
        ap = Appliance.objects.get(support_business_id=request.POST.get("support_business_id"),startup=startup )
        result["is_appliance_submitted"] = ap.is_submit
        result["appliance_id"] = ap.id
    else:
        result["is_applied"] = False
        result["is_appliance_submitted"] = False
        result["appliance_id"] = ""

    return JsonResponse(result, safe=False)

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
                accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                    accountId=account,
                    webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def get_results(service, profile_id):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.

    result = {}
    result["info"]={}
    result["info"]["week_user"] = service.data().ga().get(
            ids='ga:181394897' ,
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:users').execute()

    result["info"]["new_user"] = service.data().ga().get(
            ids='ga:181394897',
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:newUsers').execute()

    result["info"]["session_per_user"] = service.data().ga().get(
            ids='ga:181394897' ,
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:sessionsPerUser').execute()

    result["info"]["page_per_user"] = service.data().ga().get(
            ids='ga:181394897' ,
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:pageviewsPerSession').execute()

    result["info"]["page_view"] = service.data().ga().get(
            ids='ga:181394897' ,
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:pageviews').execute()

    result["info"]["user_in_30"]= service.data().ga().get(
            ids='ga:181394897' ,
            start_date='30daysAgo',
            end_date='today',
            metrics='ga:users',
            dimensions="ga:date",).execute()

    result["info"]["new_user_in_30"] = service.data().ga().get(
        ids='ga:181394897' ,
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:newUsers',
        dimensions="ga:date", ).execute()

    result["info"]["session_in_30"] = service.data().ga().get(
        ids='ga:181394897',
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:sessions',
        dimensions="ga:date", ).execute()

    result["info"]["session_per_user_in_30"] = service.data().ga().get(
        ids='ga:181394897',
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:sessionsPerUser',
        dimensions="ga:date", ).execute()

    result["info"]["page_per_session_in_30"] = service.data().ga().get(
        ids='ga:181394897' ,
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:pageviewsPerSession',
        dimensions="ga:date", ).execute()

    result["info"]["pageviews_in_30"] = service.data().ga().get(
        ids='ga:181394897' ,
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:pageviews',
        dimensions="ga:date", ).execute()


    return result

def print_results(results):
    # Print data nicely for the user.
    if results:
        print ( results.get('profileInfo').get('profileName'))
        print (results.get('rows')[0][0] )

    else:
        print ('No results found')
@csrf_exempt
@my_timer
def get_site_statics_update(request):
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = '/workspace/supporting_business/gcaprj-af2bb7d7431a.json'
    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    profile_id = get_first_profile_id(service)
    GATable.objects.all().delete()
    ga = GATable()
    ga.string_data = get_results(service, profile_id)
    ga.save()
    return JsonResponse(get_results(service, profile_id))
@csrf_exempt
@my_timer
def get_site_statics(request):
    data = json.loads(json.dumps(ast.literal_eval(GATable.objects.all().last().string_data)))
    return JsonResponse(data)

@csrf_exempt
@my_timer
def sync_with_appliance(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    else:
        user_auth_id =  check_result
    support_business_id = request.POST.get("support_business_id")
    startup = Startup.objects.get(user = AdditionalUserInfo.objects.get(id=user_auth_id).user)
    app = Appliance.objects.get(support_business_id = support_business_id, startup=startup)
    # app ====> startup 으로
    startup.address_0 = app.address_0
    startup.address_1 = app.address_1
    startup.company_name = app.company_name
    startup.established_date = app.established_date
    startup.repre_name = app.repre_name
    startup.repre_tel = app.repre_tel
    startup.repre_email = app.repre_email
    startup.mark_name = app.mark_name
    startup.mark_email = app.mark_email
    startup.mark_tel = app.mark_tel
    startup.company_website = app.company_website
    startup.company_youtube = app.company_youtube
    startup.company_instagram = app.company_instagram
    startup.company_facebook = app.company_facebook
    startup.company_kind = app.company_kind
    startup.company_keyword = app.company_keyword
    startup.attached_ir_file = app.attached_ir_file
    startup.attached_cert_file = app.attached_cert_file
    startup.attached_tax_file = app.attached_tax_file
    startup.attached_fund_file = app.attached_fund_file
    startup.attached_ppt_file = app.attached_ppt_file
    startup.attached_etc_file = app.attached_etc_file
    startup.attached_ip_file = app.attached_ip_file
    startup.company_total_employee = app.company_total_employee
    startup.company_hold_employee = app.company_hold_employee
    startup.company_assurance_employee = app.company_assurance_employee
    startup.revenue_before_0 = app.revenue_before_0
    startup.revenue_before_1 = app.revenue_before_1
    startup.revenue_before_2 = app.revenue_before_2
    startup.revenue_before_year_0 = 2017
    startup.revenue_before_year_1 = 2016
    startup.revenue_before_year_2 = 2015
    startup.export_before_0 = app.export_before_0
    startup.export_before_1 = app.export_before_1
    startup.export_before_2 = app.export_before_2
    startup.export_before_year_0 = 2017
    startup.export_before_year_1 = 2016
    startup.export_before_year_2 = 2015
    startup.export_before_nation_0 = app.export_before_nation_0
    startup.export_before_nation_1 = app.export_before_nation_1
    startup.export_before_nation_2 = app.export_before_nation_2
    startup.company_intro = app.company_intro
    startup.save()
    for info in startup.service_set.all():
        info.delete()
    for info in startup.history_set.all():
        info.delete()
    for info in startup.companyinvest_set.all():
        info.delete()
    for t in ApplianceHistory.objects.filter(appliance=app):
        his = History()
        his.company_history_year = t.company_history_year
        his.company_history_content = t.company_history_content
        his.startup=startup
        his.save()
    for inv in ApplianceInvest.objects.filter(applicance=app):
        com_inv = CompanyInvest()
        com_inv.startup = startup
        com_inv.company_invest_year = inv.company_invest_year
        com_inv.company_invest_size = inv.company_invest_size
        com_inv.company_invest_agency = inv.company_invest_agency
        com_inv.save()
    for t in startup.selected_company_filter_list.all():
        if t.cat_0 == "기본장르" or t.cat_0 == "영역":
            startup.selected_company_filter_list.remove(t)

    for t in app.selected_company_filter_list.all():
        if t.cat_0 == "기본장르" or t.cat_0 == "영역":
            startup.selected_company_filter_list.add(t)
    for s in app.applianceservice_set.all():
        app_ser = Service()
        app_ser.startup = startup
        app_ser.service_name = s.service_name
        app_ser.service_intro = s.service_intro
        app_ser.save()
    app.is_applied_to_company_info = True
    app.save()
    return  JsonResponse({"result":True})
import os
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404
import urllib.parse
def download(request):
    path=  urllib.parse.unquote(request.GET.get("media"))
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(file_path)
    print(os.path.basename(file_path))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(
                os.path.basename(file_path), safe='')
            return response
    raise Http404


@csrf_exempt

def del_file(request):
    if request.POST.get("cat") == "my_service":
        print("herer")
        ser = Service.objects.get(id = request.POST.get("value"))
        ser.service_file = ""
        ser.save()
        return JsonResponse({"result":"true"} , safe=False)

    if request.POST.get("cat") == "attached_file":
        print("herer")
        ser = Service.objects.get(id=request.POST.get("value"))
        ser.service_file = ""
        ser.save()
        return JsonResponse({"result": "true"})

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
@csrf_exempt
def logout(request):
    session_key = request.GET.get("session_key")
    try:
        Session.objects.get(session_key=session_key).delete()
        return JsonResponse({"result":"true"})
    except:
        return JsonResponse({"result":"false"})
@csrf_exempt
@my_timer
def delete_application(request):
    print(request.POST.get("application_id"))
    app_num = request.POST.get("application_id")
    app =Appliance.objects.get(id=app_num)
    try:
        aw=Award.objects.get(startup=app.startup, support_business=app.support_business)
        aw.delete()
    except Exception as e:
        print(e)
    app.delete()
    return JsonResponse({"result":"true"})
@csrf_exempt
@my_timer
def delete_support_business(request):
    print(request.POST.get("support_business_id"))
    support_business_num = request.POST.get("support_business_id")
    SupportBusiness.objects.get(id=support_business_num).delete()
    return JsonResponse({"result":"true"})



from django.db.models import F
import ast
@csrf_exempt
@my_timer
def updated_support_statics(request):
    support_business_id = request.GET.get("support_business_id")
    result = {}
    print(request.GET.get("opr_id"))
    if request.GET.get("opr_id") == None:
        qs = CountingTable.objects.filter(support_business_id= support_business_id)
        qs_startup = CountingStartupListTable.objects.get(support_business_id=support_business_id)
        qs_filter = CountingFilterListTable.objects.get(support_business_id=support_business_id)
    else:
        if request.GET.get("period") =="ing":
            qs = OPRINGCountingTable.objects.filter(opr_id=request.GET.get("opr_id"))
            qs_startup = OPRINGCountingStartupListTable.objects.get(opr_id=request.GET.get("opr_id"))
            qs_filter = OPRINGCountingFilterListTable.objects.get(opr_id=request.GET.get("opr_id"))
        else:
            qs = OPRENDCountingTable.objects.filter(opr_id=request.GET.get("opr_id"))
            qs_startup = OPRENDCountingStartupListTable.objects.get(opr_id=request.GET.get("opr_id"))
            qs_filter = OPRENDCountingFilterListTable.objects.get(opr_id=request.GET.get("opr_id"))
    if int(support_business_id) > 0:
        result["support_business_min_date"]  = str(SupportBusiness.objects.get(id=support_business_id).support_business_update_at_ymdt).split(" ")[0]
    else:
        result["support_business_min_date"] = str(qs[0].date).split(" ")[0]

    result["support_business_detail_hit"] = list(qs.order_by("-date").annotate(number=F("hit_num")).values("date","number"))
    result["favored_support_business"] = list(qs.order_by("-date").annotate(number=F("fav_num")).values("date","number"))
    result["support_business_appliance"] =  list(qs.order_by("-date").annotate(number=F("apply_num")).values("date","number"))

    result["all_startup_list"] = json.loads(json.dumps(ast.literal_eval(qs_startup.all_startup_list)))
    result["hit_startup_list"] =   json.loads(json.dumps(ast.literal_eval(qs_startup.hit_startup_list)))
    result["favored_startup_list"] = json.loads(json.dumps(ast.literal_eval(qs_startup.fav_startup_list)))
    print(qs_startup.applied_startup_list)
    result["applied_startup_list"] =  json.loads(json.dumps(ast.literal_eval(qs_startup.applied_startup_list)))
    result["aw_startup_list"] =  json.loads(json.dumps(ast.literal_eval(qs_startup.awarded_startup_list)))

    result["all_comtype_filter"] =  json.loads(json.dumps(ast.literal_eval(qs_filter.all_filter)))["all_comtype_filter"]
    result["all_location_filter"]= json.loads(json.dumps(ast.literal_eval(qs_filter.all_filter)))["all_location_filter"]
    result["all_genre_filter"]= json.loads(json.dumps(ast.literal_eval(qs_filter.all_filter)))["all_genre_filter"]
    result["all_area_filter"]= json.loads(json.dumps(ast.literal_eval(qs_filter.all_filter)))["all_area_filter"]
    result["hit_comtype_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.hit_filter)))["organized_hit_comtype_filter"]
    result["hit_location_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.hit_filter)))["organized_hit_location_filter"]
    result["hit_genre_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.hit_filter)))["organized_hit_genre_filter"]
    result["hit_area_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.hit_filter)))["organized_hit_area_filter"]
    result["favored_comtype_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.fav_filter)))["organized_fav_comtype_filter"]
    result["favored_location_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.fav_filter)))["organized_fav_location_filter"]
    result["favored_genre_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.fav_filter)))["organized_fav_genre_filter"]
    result["favored_area_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.fav_filter)))["organized_fav_area_filter"]
    result["applied_comtype_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.applied_filter)))["organized_app_comtype_filter"]
    result["applied_location_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.applied_filter)))["organized_app_location_filter"]
    result["applied_genre_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.applied_filter)))["organized_app_genre_filter"]
    result["applied_area_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.applied_filter)))["organized_app_area_filter"]
    result["aw_comtype_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.awarded_filter)))["organized_aw_comtype_filter"]
    result["aw_location_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.awarded_filter)))["organized_aw_location_filter"]
    result["aw_genre_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.awarded_filter)))["organized_aw_genre_filter"]
    result["aw_area_filter"] = json.loads(json.dumps(ast.literal_eval(qs_filter.awarded_filter)))["organized_aw_area_filter"]
    return JsonResponse(result)

@csrf_exempt
@my_timer
def check_company_name(request):
    check_result = gca_check_session(request)
    if check_result != False:
        user_auth_id =  check_result
    name = request.POST.get("company_name")
    add = AdditionalUserInfo.objects.get(id=user_auth_id)
    num = (Startup.objects.exclude(user=add.user).filter(company_name=name)).count()
    return JsonResponse({"result":num})

@csrf_exempt
@my_timer
def delete_support_business_file(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return HttpResponse(status=401)
    SupportBusinessAttachedFiles.objects.get(id=request.POST.get("id")).delete()
    return JsonResponse({"result":"ok"})


@csrf_exempt
@my_timer
def superuser_grant_check(request):
    check_result = gca_check_session(request)
    if check_result == False:
        return  HttpResponse(status=401)
    else:
        user_auth_id = check_result
        is_superuser = AdditionalUserInfo.objects.get(id=user_auth_id).is_superuser
        return JsonResponse({"result":is_superuser})


from background_task import background


@background(schedule=60)
def update_static_count_0():
    sb_set = SupportBusiness.objects.all()
    CountingStartupListTable.objects.all().delete()
    CountingFilterListTable.objects.all().delete()
    for sb in sb_set:
        # 방문자 스타트업 리스트 추출
        go = HitLog.objects.filter(support_business=sb).values("user_id").distinct()
        hit_startup = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    hit_startup.append(st.id)

        hit_startup_list = []
        k = 1;
        for startup_id in hit_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)

            hit_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        go = FavoriteLog.objects.filter(support_business=sb).values("user_id").distinct()
        fav_startup = []
        fav_startup_list = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    fav_startup.append(st.id)
        k = 1;
        for startup_id in fav_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            fav_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        app = Appliance.objects.filter(support_business=sb).filter(is_submit=True).values("startup_id").distinct()
        app_startup = []
        app_startup_list = []
        for startup_in_app in app:
            app_startup.append(startup_in_app["startup_id"])
        k = 1;

        for startup_id in app_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.get(support_business=sb, startup=startup)

            app_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "app_id": pre_app.id,
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        aw = Award.objects.filter(support_business=sb)
        aw_startup = []
        aw_startup_list = []

        for awin in aw:
            aw_startup.append(awin.startup_id)
        k = 1;
        for startup_id in aw_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.get(support_business=sb, startup=startup)
            aw_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "app_id": pre_app.id,
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1

        hit_filter_list = []
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []

        for st in hit_startup:
            startup = Startup.objects.get(id=st)
            hit_filter_list = list(startup.selected_company_filter_list.all())
            for filter in hit_filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_hit_comtype_filter = organize(hit_comtype_filter)
        organized_hit_location_filter = organize(hit_location_filter)
        organized_hit_genre_filter = organize(hit_genre_filter)
        organized_hit_area_filter = organize(hit_area_filter)
        fav_filter_list = []
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        for st in fav_startup:
            startup = Startup.objects.get(id=st)
            fav_filter_list = list(startup.selected_company_filter_list.all())
            for filter in fav_filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_fav_comtype_filter = organize(fav_comtype_filter)
        organized_fav_location_filter = organize(fav_location_filter)
        organized_fav_genre_filter = organize(fav_genre_filter)
        organized_fav_area_filter = organize(fav_area_filter)
        app_filter_list = []
        app_comtype_filter = []
        app_location_filter = []
        app_genre_filter = []
        app_area_filter = []
        for st in app_startup:
            startup = Startup.objects.get(id=st)
            app_filter_list = list(startup.selected_company_filter_list.all())
            for filter in app_filter_list:
                if filter.cat_1 == "기업형태":
                    app_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    app_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    app_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    app_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_app_comtype_filter = organize(app_comtype_filter)
        organized_app_location_filter = organize(app_location_filter)
        organized_app_genre_filter = organize(app_genre_filter)
        organized_app_area_filter = organize(app_area_filter)
        aw_filter_list = []
        aw_comtype_filter = []
        aw_location_filter = []
        aw_genre_filter = []
        aw_area_filter = []
        for st in aw_startup:
            startup = Startup.objects.get(id=st)
            aw_filter_list = list(startup.selected_company_filter_list.all())
            for filter in aw_filter_list:
                if filter.cat_1 == "기업형태":
                    aw_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    aw_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    aw_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    aw_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_aw_comtype_filter = organize(aw_comtype_filter)
        organized_aw_location_filter = organize(aw_location_filter)
        organized_aw_genre_filter = organize(aw_genre_filter)
        organized_aw_area_filter = organize(aw_area_filter)
        all_startup = []
        for startup in aw_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in app_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in fav_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in hit_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        all_startup_list = []
        for startup_id in all_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            all_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        all_filter_list = []
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []
        for st in all_startup:
            startup = Startup.objects.get(id=st)
            all_filter_list = list(startup.selected_company_filter_list.all())
            for filter in all_filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_all_comtype_filter = organize(all_comtype_filter)
        organized_all_location_filter = organize(all_location_filter)
        organized_all_genre_filter = organize(all_genre_filter)
        organized_all_area_filter = organize(all_area_filter)
        cst = CountingStartupListTable()
        cst.support_business = sb
        cst.all_startup_list = all_startup_list
        cst.hit_startup_list = hit_startup_list
        cst.fav_startup_list = fav_startup_list
        cst.applied_startup_list = app_startup_list
        cst.awarded_startup_list = aw_startup_list
        cst.save()
        cft = CountingFilterListTable()
        cft.support_business = sb
        filter_str = {}
        filter_str["all_comtype_filter"] = organized_all_comtype_filter
        filter_str["all_location_filter"] = organized_all_location_filter
        filter_str["all_genre_filter"] = organized_all_genre_filter
        filter_str["all_area_filter"] = organized_all_area_filter
        cft.all_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
        filter_str["organized_hit_location_filter"] = organized_hit_location_filter
        filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
        filter_str["organized_hit_area_filter"] = organized_hit_area_filter
        cft.hit_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
        filter_str["organized_fav_location_filter"] = organized_fav_location_filter
        filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
        filter_str["organized_fav_area_filter"] = organized_fav_area_filter
        cft.fav_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
        filter_str["organized_app_location_filter"] = organized_app_location_filter
        filter_str["organized_app_genre_filter"] = organized_app_genre_filter
        filter_str["organized_app_area_filter"] = organized_app_area_filter
        cft.applied_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
        filter_str["organized_aw_location_filter"] = organized_aw_location_filter
        filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
        filter_str["organized_aw_area_filter"] = organized_aw_area_filter
        cft.awarded_filter = str(filter_str)
        cft.save()
@background(schedule=60)
def update_static_count_1():
    opr_list_qs = AdditionalUserInfo.objects.filter(auth="OPR").values_list("id", flat=True)
    OPRENDCountingStartupListTable.objects.all().delete()
    OPRENDCountingFilterListTable.objects.all().delete()
    for opr_id in opr_list_qs:
        opr = AdditionalUserInfo.objects.get(id=opr_id)
        opr_mng = opr.additionaluserinfo_set.all()
        support_business_set = []
        for mng in opr_mng:
            support_business_set = support_business_set + list(
                SupportBusiness.objects.filter(support_business_author=mng)
                .filter(support_business_apply_end_ymdt__lte=datetime.now())
                .filter(support_business_status__in=[3, 4, 5, "4", "5"]))
        # 기관관리자 하위의 매니저의 전체 지원사업
        go = HitLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
        hit_startup = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    hit_startup.append(st.id)
        hit_startup_list = []
        k = 1;
        for startup_id in hit_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            hit_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        go = FavoriteLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
        fav_startup = []
        fav_startup_list = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    fav_startup.append(st.id)
        k = 1;
        for startup_id in fav_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            fav_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values(
            "startup_id").distinct()
        app_startup = []
        app_startup_list = []
        for startup_in_app in app:
            app_startup.append(startup_in_app["startup_id"])
        k = 1;
        for startup_id in app_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.filter(startup=startup).last()
            app_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
                "app_id": pre_app.id
            })
            k = k + 1
        aw = Award.objects.filter(support_business__in=support_business_set)
        aw_startup = []
        aw_startup_list = []
        for awin in aw:
            aw_startup.append(awin.startup_id)
        k = 1;
        for startup_id in aw_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.filter(startup=startup).last()
            aw_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
                "app_id": pre_app.id
            })
            k = k + 1
        hit_filter_list = []
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        for st in hit_startup:
            startup = Startup.objects.get(id=st)
            hit_filter_list = list(startup.selected_company_filter_list.all())
            for filter in hit_filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                    print(hit_comtype_filter)
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_hit_comtype_filter = organize(hit_comtype_filter)
        organized_hit_location_filter = organize(hit_location_filter)
        organized_hit_genre_filter = organize(hit_genre_filter)
        organized_hit_area_filter = organize(hit_area_filter)
        fav_filter_list = []
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        for st in fav_startup:
            startup = Startup.objects.get(id=st)
            fav_filter_list = list(startup.selected_company_filter_list.all())
            for filter in fav_filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_fav_comtype_filter = organize(fav_comtype_filter)
        organized_fav_location_filter = organize(fav_location_filter)
        organized_fav_genre_filter = organize(fav_genre_filter)
        organized_fav_area_filter = organize(fav_area_filter)
        app_filter_list = []
        app_comtype_filter = []
        app_location_filter = []
        app_genre_filter = []
        app_area_filter = []
        for st in app_startup:
            startup = Startup.objects.get(id=st)
            app_filter_list = list(startup.selected_company_filter_list.all())
            for filter in app_filter_list:
                if filter.cat_1 == "기업형태":
                    app_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    app_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    app_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    app_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_app_comtype_filter = organize(app_comtype_filter)
        organized_app_location_filter = organize(app_location_filter)
        organized_app_genre_filter = organize(app_genre_filter)
        organized_app_area_filter = organize(app_area_filter)
        aw_filter_list = []
        aw_comtype_filter = []
        aw_location_filter = []
        aw_genre_filter = []
        aw_area_filter = []
        for st in aw_startup:
            startup = Startup.objects.get(id=st)
            aw_filter_list = list(startup.selected_company_filter_list.all())
            for filter in aw_filter_list:
                if filter.cat_1 == "기업형태":
                    aw_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    aw_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    aw_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    aw_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_aw_comtype_filter = organize(aw_comtype_filter)
        organized_aw_location_filter = organize(aw_location_filter)
        organized_aw_genre_filter = organize(aw_genre_filter)
        organized_aw_area_filter = organize(aw_area_filter)
        all_startup = []
        for startup in aw_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in app_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in fav_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in hit_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        all_startup_list = []
        k = 1
        for startup_id in all_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            all_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        all_filter_list = []
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []
        for st in all_startup:
            startup = Startup.objects.get(id=st)
            all_filter_list = list(startup.selected_company_filter_list.all())
            for filter in all_filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_all_comtype_filter = organize(all_comtype_filter)
        organized_all_location_filter = organize(all_location_filter)
        organized_all_genre_filter = organize(all_genre_filter)
        organized_all_area_filter = organize(all_area_filter)
        cst = OPRENDCountingStartupListTable()
        cst.opr = opr
        cst.all_startup_list = all_startup_list
        cst.hit_startup_list = hit_startup_list
        cst.fav_startup_list = fav_startup_list
        cst.applied_startup_list = app_startup_list
        cst.awarded_startup_list = aw_startup_list
        cst.save()
        cft = OPRENDCountingFilterListTable()
        cft.opr = opr
        filter_str = {}
        filter_str["all_comtype_filter"] = organized_all_comtype_filter
        filter_str["all_location_filter"] = organized_all_location_filter
        filter_str["all_genre_filter"] = organized_all_genre_filter
        filter_str["all_area_filter"] = organized_all_area_filter
        cft.all_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
        filter_str["organized_hit_location_filter"] = organized_hit_location_filter
        filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
        filter_str["organized_hit_area_filter"] = organized_hit_area_filter
        cft.hit_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
        filter_str["organized_fav_location_filter"] = organized_fav_location_filter
        filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
        filter_str["organized_fav_area_filter"] = organized_fav_area_filter
        cft.fav_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
        filter_str["organized_app_location_filter"] = organized_app_location_filter
        filter_str["organized_app_genre_filter"] = organized_app_genre_filter
        filter_str["organized_app_area_filter"] = organized_app_area_filter
        cft.applied_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
        filter_str["organized_aw_location_filter"] = organized_aw_location_filter
        filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
        filter_str["organized_aw_area_filter"] = organized_aw_area_filter
        cft.awarded_filter = str(filter_str)
        cft.save()
from datetime import datetime
from datetime import timedelta
@background(schedule=60)
def update_static_count_2():
    OPRENDCountingTable.objects.all().delete()
    opr_list_qs = AdditionalUserInfo.objects.filter(auth="OPR").values_list("id", flat=True)
    for opr_id in opr_list_qs:
        opr = AdditionalUserInfo.objects.get(id=opr_id)
        opr_mng = opr.additionaluserinfo_set.all()
        support_business_set = []
        for mng in opr_mng:
            support_business_set = support_business_set + list(
                SupportBusiness.objects.filter(support_business_author=mng)
                .filter(support_business_apply_end_ymdt__lte=datetime.now())
                .filter(support_business_status__in=[3, 4, 5, "3", "4", "5"]))
        for sb in support_business_set:
            init_date = sb.support_business_created_at_ymdt.date()
            while init_date <= datetime.now().date():
                print(init_date)
                print("date")
                res = OPRENDCountingTable()
                hit_num = (
                    HitLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
                fav_num = (
                    FavoriteLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
                app_num = (Appliance.objects.filter(support_business__in=support_business_set).filter(
                    appliance_update_at_ymdt=init_date).filter(is_submit=True)).count()
                res.date = init_date
                res.opr_id = opr_id
                res.hit_num = hit_num
                res.fav_num = fav_num
                res.apply_num = app_num
                init_date = init_date + timedelta(days=1)
                res.save()

@background(schedule=60)
def update_static_count_3():
    opr_list_qs = AdditionalUserInfo.objects.filter(auth="OPR").values_list("id", flat=True)
    OPRINGCountingFilterListTable.objects.all().delete()
    OPRINGCountingStartupListTable.objects.all().delete()
    for opr_id in opr_list_qs:
        opr = AdditionalUserInfo.objects.get(id=opr_id)
        opr_mng = opr.additionaluserinfo_set.all()
        support_business_set = []
        for mng in opr_mng:
            support_business_set = support_business_set + list(
                SupportBusiness.objects.filter(support_business_author=mng)
                .filter(support_business_apply_end_ymdt__gte=datetime.now())
                .filter(support_business_status__in=[3, "3"]))
        # 기관관리자 하위의 매니저의 전체 지원사업
        go = HitLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
        hit_startup = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    hit_startup.append(st.id)
        hit_startup_list = []
        k = 1;
        for startup_id in hit_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            hit_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        go = FavoriteLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
        fav_startup = []
        fav_startup_list = []
        for user in go:
            if user["user_id"] != None:
                add = AdditionalUserInfo.objects.get(id=user["user_id"])
                if add.auth == "USR":
                    st = Startup.objects.get(user=add.user)
                    fav_startup.append(st.id)
        k = 1;
        for startup_id in fav_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            fav_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values(
            "startup_id").distinct()
        app_startup = []
        app_startup_list = []
        for startup_in_app in app:
            app_startup.append(startup_in_app["startup_id"])
        k = 1;
        for startup_id in app_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.filter(startup=startup).last()
            app_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
                "app_id": pre_app.id
            })
            k = k + 1
        aw = Award.objects.filter(support_business__in=support_business_set)
        aw_startup = []
        aw_startup_list = []
        for awin in aw:
            aw_startup.append(awin.startup_id)
        k = 1;
        for startup_id in aw_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            pre_app = Appliance.objects.filter(startup=startup).last()
            aw_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "udated_date": str(pre_app.appliance_update_at_ymdt),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
                "app_id": pre_app.id
            })
            k = k + 1
        hit_filter_list = []
        hit_comtype_filter = []
        hit_location_filter = []
        hit_genre_filter = []
        hit_area_filter = []
        for st in hit_startup:
            startup = Startup.objects.get(id=st)
            hit_filter_list = list(startup.selected_company_filter_list.all())
            for filter in hit_filter_list:
                if filter.cat_1 == "기업형태":
                    hit_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    hit_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    hit_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    hit_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_hit_comtype_filter = organize(hit_comtype_filter)
        organized_hit_location_filter = organize(hit_location_filter)
        organized_hit_genre_filter = organize(hit_genre_filter)
        organized_hit_area_filter = organize(hit_area_filter)
        fav_filter_list = []
        fav_comtype_filter = []
        fav_location_filter = []
        fav_genre_filter = []
        fav_area_filter = []
        for st in fav_startup:
            startup = Startup.objects.get(id=st)
            fav_filter_list = list(startup.selected_company_filter_list.all())
            for filter in fav_filter_list:
                if filter.cat_1 == "기업형태":
                    fav_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    fav_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    fav_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    fav_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_fav_comtype_filter = organize(fav_comtype_filter)
        organized_fav_location_filter = organize(fav_location_filter)
        organized_fav_genre_filter = organize(fav_genre_filter)
        organized_fav_area_filter = organize(fav_area_filter)
        app_filter_list = []
        app_comtype_filter = []
        app_location_filter = []
        app_genre_filter = []
        app_area_filter = []
        for st in app_startup:
            startup = Startup.objects.get(id=st)
            app_filter_list = list(startup.selected_company_filter_list.all())
            for filter in app_filter_list:
                if filter.cat_1 == "기업형태":
                    app_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    app_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    app_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    app_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_app_comtype_filter = organize(app_comtype_filter)
        organized_app_location_filter = organize(app_location_filter)
        organized_app_genre_filter = organize(app_genre_filter)
        organized_app_area_filter = organize(app_area_filter)
        aw_filter_list = []
        aw_comtype_filter = []
        aw_location_filter = []
        aw_genre_filter = []
        aw_area_filter = []
        for st in aw_startup:
            startup = Startup.objects.get(id=st)
            aw_filter_list = list(startup.selected_company_filter_list.all())
            for filter in aw_filter_list:
                if filter.cat_1 == "기업형태":
                    aw_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    aw_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    aw_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    aw_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_aw_comtype_filter = organize(aw_comtype_filter)
        organized_aw_location_filter = organize(aw_location_filter)
        organized_aw_genre_filter = organize(aw_genre_filter)
        organized_aw_area_filter = organize(aw_area_filter)
        all_startup = []
        for startup in aw_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in app_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in fav_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        for startup in hit_startup:
            if startup not in all_startup:
                all_startup.append(startup)
        all_startup_list = []
        for startup_id in all_startup:
            startup = Startup.objects.get(id=startup_id)
            local = []
            for filter in startup.selected_company_filter_list.all():
                if (filter.cat_1) == "소재지":
                    local.append(filter.filter_name)
            all_startup_list.append({
                "startup_id": startup.id,
                "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
                "company_kind": startup.company_kind,
                "local": ",".join(local),
                "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
            })
            k = k + 1
        all_filter_list = []
        all_comtype_filter = []
        all_location_filter = []
        all_genre_filter = []
        all_area_filter = []
        for st in all_startup:
            startup = Startup.objects.get(id=st)
            all_filter_list = list(startup.selected_company_filter_list.all())
            for filter in all_filter_list:
                if filter.cat_1 == "기업형태":
                    all_comtype_filter.append(filter.filter_name)
                if filter.cat_1 == "소재지":
                    all_location_filter.append(filter.filter_name)
                if filter.cat_0 == "기본장르":
                    all_genre_filter.append(filter.filter_name)
                if filter.cat_0 == "영역":
                    all_area_filter.append(filter.filter_name)
                    # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
        organized_all_comtype_filter = organize(all_comtype_filter)
        organized_all_location_filter = organize(all_location_filter)
        organized_all_genre_filter = organize(all_genre_filter)
        organized_all_area_filter = organize(all_area_filter)
        cst = OPRINGCountingStartupListTable()
        cst.opr = opr
        cst.all_startup_list = all_startup_list
        cst.hit_startup_list = hit_startup_list
        cst.fav_startup_list = fav_startup_list
        cst.applied_startup_list = app_startup_list
        cst.awarded_startup_list = aw_startup_list
        cst.save()
        cft = OPRINGCountingFilterListTable()
        cft.opr = opr
        filter_str = {}
        filter_str["all_comtype_filter"] = organized_all_comtype_filter
        filter_str["all_location_filter"] = organized_all_location_filter
        filter_str["all_genre_filter"] = organized_all_genre_filter
        filter_str["all_area_filter"] = organized_all_area_filter
        cft.all_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
        filter_str["organized_hit_location_filter"] = organized_hit_location_filter
        filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
        filter_str["organized_hit_area_filter"] = organized_hit_area_filter
        cft.hit_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
        filter_str["organized_fav_location_filter"] = organized_fav_location_filter
        filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
        filter_str["organized_fav_area_filter"] = organized_fav_area_filter
        cft.fav_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
        filter_str["organized_app_location_filter"] = organized_app_location_filter
        filter_str["organized_app_genre_filter"] = organized_app_genre_filter
        filter_str["organized_app_area_filter"] = organized_app_area_filter
        cft.applied_filter = str(filter_str)
        filter_str = {}
        filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
        filter_str["organized_aw_location_filter"] = organized_aw_location_filter
        filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
        filter_str["organized_aw_area_filter"] = organized_aw_area_filter
        cft.awarded_filter = str(filter_str)
        cft.save()

@background(schedule=60)
def update_static_count_4():
    OPRINGCountingTable.objects.all().delete()
    opr_list_qs = AdditionalUserInfo.objects.filter(auth="OPR").values_list("id", flat=True)
    for opr_id in opr_list_qs:
        opr = AdditionalUserInfo.objects.get(id=opr_id)
        opr_mng = opr.additionaluserinfo_set.all()
        support_business_set = []
        for mng in opr_mng:
            support_business_set = support_business_set + list(
                SupportBusiness.objects.filter(support_business_author=mng)
                .filter(support_business_apply_end_ymdt__gte=datetime.now())
                .filter(support_business_status__in=[3, "3"]))
        for sb in support_business_set:
            init_date = sb.support_business_created_at_ymdt.date()
            while init_date <= datetime.now().date():
                res = OPRINGCountingTable()
                hit_num = (
                    HitLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
                fav_num = (
                    FavoriteLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
                app_num = (Appliance.objects.filter(support_business__in=support_business_set).filter(
                    appliance_update_at_ymdt=init_date).filter(is_submit=True)).count()
                res.date = init_date
                res.opr_id = opr_id
                res.hit_num = hit_num
                res.fav_num = fav_num
                res.apply_num = app_num
                init_date = init_date + timedelta(days=1)
                res.save()

@background(schedule=60)
def update_static_count_5():
    CountingTable.objects.all().delete()
    sb_set = SupportBusiness.objects.all()
    for sb in sb_set:
        try:
            print(sb.support_business_name + "*" * 10)
        except:
            print()
        init_date = sb.support_business_created_at_ymdt.date()

        while init_date <= datetime.now().date():
            res = CountingTable()
            hit_num = (HitLog.objects.filter(support_business=sb).filter(date=init_date)).count()
            fav_num = (FavoriteLog.objects.filter(support_business=sb).filter(date=init_date)).count()
            app_num = (
                Appliance.objects.filter(support_business=sb).filter(appliance_update_at_ymdt=init_date).filter(
                    is_submit=True)).count()
            res.date = init_date
            res.hit_num = hit_num
            res.fav_num = fav_num
            res.apply_num = app_num
            res.support_business = sb
            init_date = init_date + timedelta(days=1)
            res.save()

# update_static_count_0(repeat=600,repeat_until=datetime(2019,12,31))
# update_static_count_1(repeat=600,repeat_until=datetime(2019,12,31))
# update_static_count_2(repeat=600,repeat_until=datetime(2019,12,31))
# update_static_count_3(repeat=600,repeat_until=datetime(2019,12,31))
# update_static_count_4(repeat=600,repeat_until=datetime(2019,12,31))
# update_static_count_5(repeat=600,repeat_until=datetime(2019,12,31))

#####  통계 갱신 코드 수정

@background(schedule=60)
def get_opr_support_business_statics_number():

    for opr in AdditionalUserInfo.objects.filter(auth="OPR") :
        get_opr_end_count(opr.id)
        get_opr_end_startup_list(opr.id)
        get_opr_ing_count(opr.id)
        get_opr_ing_startup_list(opr.id)
    for sb in SupportBusiness.objects.all():
        get_support_business_statics_number(sb.id)
        get_support_business_statics_filter_list(sb.id)
    vue_get_channel_statics_clip_update()
    vue_get_channel_statics_course_update()
    vue_get_channel_statics_path_update()

get_opr_support_business_statics_number(repeat=600, repeat_until=datetime(2019, 12, 31))
def get_opr_end_count(opr_id):
    opr = AdditionalUserInfo.objects.get(id=opr_id)
    opr_mng = opr.additionaluserinfo_set.all()

    support_business_set = []

    support_business_set =  (SupportBusiness.objects.filter(support_business_author__in=opr_mng)
                                                           .filter(support_business_apply_end_ymdt__lte=datetime.now())
                                                           .filter(
            support_business_status__in=[3, 4, 5, "3", "4", "5"]))
    try:
        init_date = support_business_set.order_by("support_business_created_at_ymdt")[0].support_business_created_at_ymdt.date()
        print(init_date)
        while init_date <= datetime.now().date():
            res,created = OPRENDCountingTable.objects.get_or_create(opr_id=opr_id, date=init_date)
            hit_num = (HitLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
            fav_num = (
                FavoriteLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
            app_num = (Appliance.objects.filter(support_business__in=support_business_set).filter(
                appliance_update_at_ymdt=init_date).filter(is_submit=True)).count()
            res.date = init_date
            res.opr_id = opr_id
            res.hit_num = hit_num
            res.fav_num = fav_num
            res.apply_num = app_num
            init_date = init_date + timedelta(days=1)
            res.save()
    except:
        res = OPRENDCountingTable()
        res.opr_id = opr_id
        res.save()
def get_opr_ing_count(opr_id):
    opr = AdditionalUserInfo.objects.get(id=opr_id)
    opr_mng = opr.additionaluserinfo_set.all()
    support_business_set =  (SupportBusiness.objects.filter(support_business_author__in=opr_mng)
                                                       .filter(support_business_apply_end_ymdt__gte=datetime.now())
                                                       .filter(support_business_status__in=[3, "3"]))
    try:
        init_date = support_business_set.order_by("support_business_created_at_ymdt")[0].support_business_created_at_ymdt.date()
        while init_date <= datetime.now().date():
            res, created = OPRINGCountingTable.objects.get_or_create(opr_id=opr_id, date=init_date)
            hit_num = (HitLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
            fav_num = (
                FavoriteLog.objects.filter(support_business__in=support_business_set).filter(date=init_date)).count()
            app_num = (Appliance.objects.filter(support_business__in=support_business_set).filter(
                appliance_update_at_ymdt=init_date).filter(is_submit=True)).count()
            res.date = init_date
            res.opr_id = opr_id
            res.hit_num = hit_num
            res.fav_num = fav_num
            res.apply_num = app_num
            init_date = init_date + timedelta(days=1)
            res.save()

    except:
        res = OPRINGCountingTable()
        res.opr_id = opr_id
        res.save()
def get_opr_end_startup_list(opr_id):
    opr = AdditionalUserInfo.objects.get(id=opr_id)
    opr_mng = opr.additionaluserinfo_set.all()
    support_business_set = []
    for mng in opr_mng:
        support_business_set = support_business_set + list(SupportBusiness.objects.filter(support_business_author=mng)
                                                           .filter(
            support_business_apply_end_ymdt__lte=datetime.now())
                                                           .filter(support_business_status__in=[3, 4, 5, "4", "5"]))
    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values_list(
        "startup_id",
        flat=True).distinct()
    go = HitLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
    hit_startup = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                hit_startup.append(st.id)
    hit_startup_list = []
    k = 1;
    for startup_id in hit_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():
            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if( filter.cat_1) =="기업형태":
                if startup.company_kind != filter.filter_name:
                    print(startup)
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(
                startup=startup).filter(is_submit=True).last()
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id
        else:
            udated_date = ""
            app_id = ""
        hit_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date" :udated_date, "app_id" :app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    go = FavoriteLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
    fav_startup = []
    fav_startup_list = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                fav_startup.append(st.id)
    k = 1
    for startup_id in fav_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                if startup.company_kind != filter.filter_name:
                    print(startup)
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(
                startup=startup).filter(is_submit=True).last()
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id
        else:
            udated_date = ""
            app_id = ""
        fav_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date, "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values(
        "startup_id").distinct()
    app_startup = []
    app_startup_list = []
    for startup_in_app in app:
        app_startup.append(startup_in_app["startup_id"])
    k = 1;
    for startup_id in app_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                if startup.company_kind != filter.filter_name:
                    print(startup)
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.filter(startup=startup).filter(is_submit=True).last()
        app_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
            "app_id": pre_app.id
        })
        k = k + 1

    aw = Award.objects.filter(support_business__in=support_business_set)
    aw_startup = []
    aw_startup_list = []
    for awin in aw:
        aw_startup.append(awin.startup_id)
    k = 1;
    for startup_id in aw_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                if startup.company_kind != filter.filter_name:
                    print(startup)
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.filter(startup=startup).filter(is_submit=True).last()
        aw_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
            "app_id": pre_app.id
        })
        k = k + 1
    hit_filter_list = []
    hit_comtype_filter = []
    hit_location_filter = []
    hit_genre_filter = []
    hit_area_filter = []

    for st in hit_startup:
        startup = Startup.objects.get(id=st)
        hit_filter_list = list(startup.selected_company_filter_list.all())
        for filter in hit_filter_list:

            if filter.cat_1 == "기업형태":
                hit_comtype_filter.append(filter.filter_name)
                print(hit_comtype_filter)
            if filter.cat_1 == "소재지":
                hit_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                hit_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                hit_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_hit_comtype_filter = organize(hit_comtype_filter)
    organized_hit_location_filter = organize(hit_location_filter)
    organized_hit_genre_filter = organize(hit_genre_filter)
    organized_hit_area_filter = organize(hit_area_filter)

    fav_filter_list = []
    fav_comtype_filter = []
    fav_location_filter = []
    fav_genre_filter = []
    fav_area_filter = []
    for st in fav_startup:
        startup = Startup.objects.get(id=st)
        fav_filter_list = list(startup.selected_company_filter_list.all())
        for filter in fav_filter_list:

            if filter.cat_1 == "기업형태":
                fav_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                fav_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                fav_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                fav_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_fav_comtype_filter = organize(fav_comtype_filter)
    organized_fav_location_filter = organize(fav_location_filter)
    organized_fav_genre_filter = organize(fav_genre_filter)
    organized_fav_area_filter = organize(fav_area_filter)

    app_filter_list = []
    app_comtype_filter = []
    app_location_filter = []
    app_genre_filter = []
    app_area_filter = []
    for st in app_startup:
        startup = Startup.objects.get(id=st)
        app_filter_list = list(startup.selected_company_filter_list.all())
        for filter in app_filter_list:

            if filter.cat_1 == "기업형태":
                app_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                app_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                app_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                app_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_app_comtype_filter = organize(app_comtype_filter)
    organized_app_location_filter = organize(app_location_filter)
    organized_app_genre_filter = organize(app_genre_filter)
    organized_app_area_filter = organize(app_area_filter)

    aw_filter_list = []
    aw_comtype_filter = []
    aw_location_filter = []
    aw_genre_filter = []
    aw_area_filter = []
    for st in aw_startup:
        startup = Startup.objects.get(id=st)
        aw_filter_list = list(startup.selected_company_filter_list.all())

        for filter in aw_filter_list:
            if filter.cat_1 == "기업형태":
                aw_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                aw_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                aw_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                aw_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_aw_comtype_filter = organize(aw_comtype_filter)
    organized_aw_location_filter = organize(aw_location_filter)
    organized_aw_genre_filter = organize(aw_genre_filter)
    organized_aw_area_filter = organize(aw_area_filter)

    all_startup = []

    for startup in aw_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in app_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in fav_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in hit_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    all_startup_list = []
    k = 1

    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values_list(
        "startup_id",
        flat=True).distinct()
    for startup_id in all_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():
            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(
                startup=startup).filter(is_submit=True).last()
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id
        else:
            udated_date = ""
            app_id = ""
        all_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    all_filter_list = []
    all_comtype_filter = []
    all_location_filter = []
    all_genre_filter = []
    all_area_filter = []
    for st in all_startup:
        startup = Startup.objects.get(id=st)
        all_filter_list = list(startup.selected_company_filter_list.all())
        for filter in all_filter_list:
            if filter.cat_1 == "기업형태":
                all_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                all_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                all_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                all_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_all_comtype_filter = organize(all_comtype_filter)
    organized_all_location_filter = organize(all_location_filter)
    organized_all_genre_filter = organize(all_genre_filter)
    organized_all_area_filter = organize(all_area_filter)

    cst,created = OPRENDCountingStartupListTable.objects.get_or_create(opr=opr)
    cst.opr = opr
    cst.all_startup_list = all_startup_list
    cst.hit_startup_list = hit_startup_list
    cst.fav_startup_list = fav_startup_list
    cst.applied_startup_list = app_startup_list
    cst.awarded_startup_list = aw_startup_list
    cst.save()

    cft,created = OPRENDCountingFilterListTable.objects.get_or_create(opr=opr)
    cft.opr.id = opr.id
    filter_str = {}
    filter_str["all_comtype_filter"] = organized_all_comtype_filter
    filter_str["all_location_filter"] = organized_all_location_filter
    filter_str["all_genre_filter"] = organized_all_genre_filter
    filter_str["all_area_filter"] = organized_all_area_filter
    cft.all_filter = str(filter_str)

    filter_str = {}
    filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
    filter_str["organized_hit_location_filter"] = organized_hit_location_filter
    filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
    filter_str["organized_hit_area_filter"] = organized_hit_area_filter
    cft.hit_filter = str(filter_str)

    filter_str = {}
    filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
    filter_str["organized_fav_location_filter"] = organized_fav_location_filter
    filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
    filter_str["organized_fav_area_filter"] = organized_fav_area_filter
    cft.fav_filter = str(filter_str)

    filter_str = {}
    filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
    filter_str["organized_app_location_filter"] = organized_app_location_filter
    filter_str["organized_app_genre_filter"] = organized_app_genre_filter
    filter_str["organized_app_area_filter"] = organized_app_area_filter
    cft.applied_filter = str(filter_str)

    filter_str = {}
    filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
    filter_str["organized_aw_location_filter"] = organized_aw_location_filter
    filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
    filter_str["organized_aw_area_filter"] = organized_aw_area_filter
    cft.awarded_filter = str(filter_str)
    cft.save()

def get_opr_ing_startup_list(opr_id):
    opr = AdditionalUserInfo.objects.get(id=opr_id)
    opr_mng = opr.additionaluserinfo_set.all()
    support_business_set = []

    for mng in opr_mng:
        support_business_set = support_business_set + list(SupportBusiness.objects.filter(support_business_author=mng)
                                                           .filter(
            support_business_apply_end_ymdt__gte=datetime.now())
                                                           .filter(support_business_status__in=[3, "3"]))
    # 기관관리자 하위의 매니저의 전체 지원사업
    go = HitLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values_list("startup_id",
                                                                                             flat=True).distinct()
    hit_startup = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                hit_startup.append(st.id)
    hit_startup_list = []
    k = 1;
    for startup_id in hit_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(startup=startup).filter(is_submit=True).last()
            udated_date= str(pre_app.appliance_update_at_ymdt)
            app_id= pre_app.id
        else:
            udated_date = ""
            app_id = ""

        hit_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    go = FavoriteLog.objects.filter(support_business__in=support_business_set).values("user_id").distinct()
    fav_startup = []
    fav_startup_list = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                fav_startup.append(st.id)
    k = 1;
    for startup_id in fav_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(
                startup=startup).filter(is_submit=True).last()
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id
        else:
            udated_date = ""
            app_id = ""
        fav_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values(
        "startup_id").distinct()
    app_startup = []
    app_startup_list = []
    for startup_in_app in app:
        app_startup.append(startup_in_app["startup_id"])
    k = 1;
    for startup_id in app_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.filter(startup=startup).filter(is_submit=True).last()
        app_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
            "app_id": pre_app.id
        })
        k = k + 1
    aw = Award.objects.filter(support_business__in=support_business_set)
    aw_startup = []
    aw_startup_list = []

    for awin in aw:
        aw_startup.append(awin.startup_id)
    k = 1;
    for startup_id in aw_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.filter(startup=startup).filter(is_submit=True).last()
        aw_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel,
            "app_id": pre_app.id
        })
        k = k + 1
    hit_filter_list = []
    hit_comtype_filter = []
    hit_location_filter = []
    hit_genre_filter = []
    hit_area_filter = []

    for st in hit_startup:
        startup = Startup.objects.get(id=st)
        hit_filter_list = list(startup.selected_company_filter_list.all())
        for filter in hit_filter_list:
            if filter.cat_1 == "기업형태":
                hit_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                hit_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                hit_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                hit_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_hit_comtype_filter = organize(hit_comtype_filter)
    organized_hit_location_filter = organize(hit_location_filter)
    organized_hit_genre_filter = organize(hit_genre_filter)
    organized_hit_area_filter = organize(hit_area_filter)
    fav_filter_list = []
    fav_comtype_filter = []
    fav_location_filter = []
    fav_genre_filter = []
    fav_area_filter = []
    for st in fav_startup:
        startup = Startup.objects.get(id=st)
        fav_filter_list = list(startup.selected_company_filter_list.all())
        for filter in fav_filter_list:
            if filter.cat_1 == "기업형태":
                fav_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                fav_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                fav_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                fav_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_fav_comtype_filter = organize(fav_comtype_filter)
    organized_fav_location_filter = organize(fav_location_filter)
    organized_fav_genre_filter = organize(fav_genre_filter)
    organized_fav_area_filter = organize(fav_area_filter)
    app_filter_list = []
    app_comtype_filter = []
    app_location_filter = []
    app_genre_filter = []
    app_area_filter = []
    for st in app_startup:
        startup = Startup.objects.get(id=st)
        app_filter_list = list(startup.selected_company_filter_list.all())
        for filter in app_filter_list:
            if filter.cat_1 == "기업형태":
                app_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                app_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                app_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                app_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_app_comtype_filter = organize(app_comtype_filter)
    organized_app_location_filter = organize(app_location_filter)
    organized_app_genre_filter = organize(app_genre_filter)
    organized_app_area_filter = organize(app_area_filter)
    aw_filter_list = []
    aw_comtype_filter = []
    aw_location_filter = []
    aw_genre_filter = []
    aw_area_filter = []
    for st in aw_startup:
        startup = Startup.objects.get(id=st)
        aw_filter_list = list(startup.selected_company_filter_list.all())
        for filter in aw_filter_list:
            if filter.cat_1 == "기업형태":
                aw_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                aw_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                aw_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                aw_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_aw_comtype_filter = organize(aw_comtype_filter)
    organized_aw_location_filter = organize(aw_location_filter)
    organized_aw_genre_filter = organize(aw_genre_filter)
    organized_aw_area_filter = organize(aw_area_filter)
    all_startup = []
    for startup in aw_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in app_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in fav_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in hit_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    all_startup_list = []
    app = Appliance.objects.filter(support_business__in=support_business_set).filter(is_submit=True).values_list(
        "startup_id",
        flat=True).distinct()
    for startup_id in all_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1) == "기업형태":
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.filter(support_business__in=support_business_set).filter(
                startup=startup).filter(is_submit=True).last()
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id
        else:
            udated_date = ""
            app_id = ""
        all_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1

    all_filter_list = []
    all_comtype_filter = []
    all_location_filter = []
    all_genre_filter = []
    all_area_filter = []
    for st in all_startup:
        startup = Startup.objects.get(id=st)
        all_filter_list = list(startup.selected_company_filter_list.all())

        for filter in all_filter_list:
            if filter.cat_1 == "기업형태":
                all_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                all_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                all_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                all_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_all_comtype_filter = organize(all_comtype_filter)
    organized_all_location_filter = organize(all_location_filter)
    organized_all_genre_filter = organize(all_genre_filter)
    organized_all_area_filter = organize(all_area_filter)

    cst,created = OPRINGCountingStartupListTable.objects.get_or_create(opr=opr)
    cst.opr = opr
    cst.all_startup_list = all_startup_list
    cst.hit_startup_list = hit_startup_list
    cst.fav_startup_list = fav_startup_list
    cst.applied_startup_list = app_startup_list
    cst.awarded_startup_list = aw_startup_list
    cst.save()
    cft,created = OPRINGCountingFilterListTable.objects.get_or_create(opr=opr)
    cft.opr = opr
    filter_str = {}
    filter_str["all_comtype_filter"] = organized_all_comtype_filter
    filter_str["all_location_filter"] = organized_all_location_filter
    filter_str["all_genre_filter"] = organized_all_genre_filter
    filter_str["all_area_filter"] = organized_all_area_filter
    cft.all_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
    filter_str["organized_hit_location_filter"] = organized_hit_location_filter
    filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
    filter_str["organized_hit_area_filter"] = organized_hit_area_filter
    cft.hit_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
    filter_str["organized_fav_location_filter"] = organized_fav_location_filter
    filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
    filter_str["organized_fav_area_filter"] = organized_fav_area_filter
    cft.fav_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
    filter_str["organized_app_location_filter"] = organized_app_location_filter
    filter_str["organized_app_genre_filter"] = organized_app_genre_filter
    filter_str["organized_app_area_filter"] = organized_app_area_filter
    cft.applied_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
    filter_str["organized_aw_location_filter"] = organized_aw_location_filter
    filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
    filter_str["organized_aw_area_filter"] = organized_aw_area_filter
    cft.awarded_filter = str(filter_str)
    cft.save()


def get_support_business_statics_number(id):
    sb = SupportBusiness.objects.get(id=id)
    init_date = sb.support_business_created_at_ymdt.date()
    while  init_date <= datetime.now().date():
        res,created = CountingTable.objects.get_or_create(support_business=sb,date = init_date)
        hit_num = (HitLog.objects.filter(support_business = sb).filter(date = init_date)).count()
        fav_num = (FavoriteLog.objects.filter(support_business = sb).filter(date=init_date)).count()
        app_num = (Appliance.objects.filter(support_business= sb).filter(appliance_update_at_ymdt=init_date).filter(is_submit=True)).count()
        res.date = init_date
        res.hit_num = hit_num
        res.fav_num = fav_num
        res.apply_num = app_num
        res.updated_at = datetime.now()
        res.support_business = sb
        res.save()
        init_date= init_date+timedelta(days=1)

def get_support_business_statics_filter_list(id):
    # 방문자 스타트업 리스트 추출
    sb = SupportBusiness.objects.get(id=id)
    go = HitLog.objects.filter(support_business=sb).values("user_id").distinct()
    app = Appliance.objects.filter(support_business=sb).filter(is_submit=True).values_list("startup_id",
                                                                                             flat=True).distinct()
    hit_startup = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                hit_startup.append(st.id)
    hit_startup_list = []
    k = 1;
    for startup_id in hit_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1 == "기업형태"):
                startup.company_kind = filter.filter_name

        startup.save()
        if startup.id in app:
            print(app)
            print(sb.id)
            print(startup.id)
            pre_app = Appliance.objects.get(support_business=sb, startup=startup)
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id= pre_app.id,
        else:
            udated_date =""
            app_id = ""

        hit_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    go = FavoriteLog.objects.filter(support_business=sb).values("user_id").distinct()
    fav_startup = []
    fav_startup_list = []
    for user in go:
        if user["user_id"] != None:
            add = AdditionalUserInfo.objects.get(id=user["user_id"])
            if add.auth == "USR":
                st = Startup.objects.get(user=add.user)
                fav_startup.append(st.id)
    k = 1;
    for startup_id in fav_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1 == "기업형태"):
                startup.company_kind = filter.filter_name
        startup.save()
        if startup.id in app:
            pre_app = Appliance.objects.get(support_business=sb, startup=startup)
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id,
        else:
            udated_date = ""
            app_id = ""
        fav_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": udated_date,
            "app_id": app_id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    app = Appliance.objects.filter(support_business=sb).filter(is_submit=True).values("startup_id").distinct()
    app_startup = []
    app_startup_list = []
    for startup_in_app in app:
        app_startup.append(startup_in_app["startup_id"])
    k = 1;
    for startup_id in app_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1 == "기업형태"):
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.get(support_business=sb, startup=startup)
        app_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "app_id": pre_app.id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    aw = Award.objects.filter(support_business=sb)
    aw_startup = []
    aw_startup_list = []
    for awin in aw:
        aw_startup.append(awin.startup_id)
    k = 1;
    for startup_id in aw_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1 == "기업형태"):
                startup.company_kind = filter.filter_name
        startup.save()
        pre_app = Appliance.objects.get(support_business=sb, startup=startup)
        aw_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),
            "udated_date": str(pre_app.appliance_update_at_ymdt),
            "app_id": pre_app.id,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    hit_filter_list = []
    hit_comtype_filter = []
    hit_location_filter = []
    hit_genre_filter = []
    hit_area_filter = []
    for st in hit_startup:
        startup = Startup.objects.get(id=st)
        hit_filter_list = list(startup.selected_company_filter_list.all())
        for filter in hit_filter_list:
            if filter.cat_1 == "기업형태":
                hit_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                hit_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                hit_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                hit_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.

    organized_hit_comtype_filter = organize(hit_comtype_filter)
    organized_hit_location_filter = organize(hit_location_filter)
    organized_hit_genre_filter = organize(hit_genre_filter)
    organized_hit_area_filter = organize(hit_area_filter)
    fav_filter_list = []
    fav_comtype_filter = []
    fav_location_filter = []
    fav_genre_filter = []
    fav_area_filter = []
    for st in fav_startup:
        startup = Startup.objects.get(id=st)
        fav_filter_list = list(startup.selected_company_filter_list.all())
        for filter in fav_filter_list:
            if filter.cat_1 == "기업형태":
                fav_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                fav_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                fav_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                fav_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_fav_comtype_filter = organize(fav_comtype_filter)
    organized_fav_location_filter = organize(fav_location_filter)
    organized_fav_genre_filter = organize(fav_genre_filter)
    organized_fav_area_filter = organize(fav_area_filter)
    app_filter_list = []
    app_comtype_filter = []
    app_location_filter = []
    app_genre_filter = []
    app_area_filter = []
    for st in app_startup:
        startup = Startup.objects.get(id=st)
        app_filter_list = list(startup.selected_company_filter_list.all())
        for filter in app_filter_list:
            if filter.cat_1 == "기업형태":
                app_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                app_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                app_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                app_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_app_comtype_filter = organize(app_comtype_filter)
    organized_app_location_filter = organize(app_location_filter)
    organized_app_genre_filter = organize(app_genre_filter)
    organized_app_area_filter = organize(app_area_filter)
    aw_filter_list = []
    aw_comtype_filter = []
    aw_location_filter = []
    aw_genre_filter = []
    aw_area_filter = []
    for st in aw_startup:
        startup = Startup.objects.get(id=st)
        aw_filter_list = list(startup.selected_company_filter_list.all())
        for filter in aw_filter_list:
            if filter.cat_1 == "기업형태":
                aw_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                aw_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                aw_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                aw_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_aw_comtype_filter = organize(aw_comtype_filter)
    organized_aw_location_filter = organize(aw_location_filter)
    organized_aw_genre_filter = organize(aw_genre_filter)
    organized_aw_area_filter = organize(aw_area_filter)
    all_startup = []
    for startup in aw_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in app_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in fav_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    for startup in hit_startup:
        if startup not in all_startup:
            all_startup.append(startup)
    all_startup_list = []
    k = 1;
    app = Appliance.objects.filter(support_business=sb).filter(is_submit=True).values_list("startup_id",
                                                                                           flat=True).distinct()
    for startup_id in all_startup:
        startup = Startup.objects.get(id=startup_id)
        local = []
        startup.company_kind = ""
        for filter in startup.selected_company_filter_list.all():

            if (filter.cat_1) == "소재지":
                local.append(filter.filter_name)
            if (filter.cat_1 == "기업형태"):
                startup.company_kind = filter.filter_name
        startup.save()

        if startup.id in app:
            pre_app = Appliance.objects.get(support_business=sb, startup=startup)
            udated_date = str(pre_app.appliance_update_at_ymdt)
            app_id = pre_app.id,
        else:
            udated_date = ""
            app_id = ""


        all_startup_list.append({
            "startup_id": startup.id,
            "index": k, "mark_email": startup.mark_email, "company_name": startup.company_name,
            "company_kind": startup.company_kind,
            "local": ",".join(local),"app_id":app_id, "udated_date":udated_date,
            "company_total_employee": startup.company_total_employee, "mark_tel": startup.mark_tel
        })
        k = k + 1
    all_filter_list = []
    all_comtype_filter = []
    all_location_filter = []
    all_genre_filter = []
    all_area_filter = []
    for st in all_startup:
        startup = Startup.objects.get(id=st)
        all_filter_list = list(startup.selected_company_filter_list.all())
        for filter in all_filter_list:
            if filter.cat_1 == "기업형태":
                all_comtype_filter.append(filter.filter_name)
            if filter.cat_1 == "소재지":
                all_location_filter.append(filter.filter_name)
            if filter.cat_0 == "기본장르":
                all_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                all_area_filter.append(filter.filter_name)
                # -> organize 로 각  필터 갯수 센것들이 들어가야 함.
    organized_all_comtype_filter = organize(all_comtype_filter)
    organized_all_location_filter = organize(all_location_filter)
    organized_all_genre_filter = organize(all_genre_filter)
    organized_all_area_filter = organize(all_area_filter)
    cst,created = CountingStartupListTable.objects.get_or_create(support_business=sb)
    cst.support_business = sb
    cst.all_startup_list = all_startup_list
    cst.hit_startup_list = hit_startup_list
    cst.fav_startup_list = fav_startup_list
    cst.applied_startup_list = app_startup_list
    cst.awarded_startup_list = aw_startup_list
    cst.updated_at = datetime.now()
    cst.save()
    cft,created = CountingFilterListTable.objects.get_or_create(support_business=sb)
    cft.support_business = sb
    filter_str = {}
    filter_str["all_comtype_filter"] = organized_all_comtype_filter
    filter_str["all_location_filter"] = organized_all_location_filter
    filter_str["all_genre_filter"] = organized_all_genre_filter
    filter_str["all_area_filter"] = organized_all_area_filter
    cft.all_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_hit_comtype_filter"] = organized_hit_comtype_filter
    filter_str["organized_hit_location_filter"] = organized_hit_location_filter
    filter_str["organized_hit_genre_filter"] = organized_hit_genre_filter
    filter_str["organized_hit_area_filter"] = organized_hit_area_filter
    cft.hit_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_fav_comtype_filter"] = organized_fav_comtype_filter
    filter_str["organized_fav_location_filter"] = organized_fav_location_filter
    filter_str["organized_fav_genre_filter"] = organized_fav_genre_filter
    filter_str["organized_fav_area_filter"] = organized_fav_area_filter
    cft.fav_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_app_comtype_filter"] = organized_app_comtype_filter
    filter_str["organized_app_location_filter"] = organized_app_location_filter
    filter_str["organized_app_genre_filter"] = organized_app_genre_filter
    filter_str["organized_app_area_filter"] = organized_app_area_filter
    cft.applied_filter = str(filter_str)
    filter_str = {}
    filter_str["organized_aw_comtype_filter"] = organized_aw_comtype_filter
    filter_str["organized_aw_location_filter"] = organized_aw_location_filter
    filter_str["organized_aw_genre_filter"] = organized_aw_genre_filter
    filter_str["organized_aw_area_filter"] = organized_aw_area_filter
    cft.awarded_filter = str(filter_str)
    cft.updated_at=datetime.now()
    cft.save()


