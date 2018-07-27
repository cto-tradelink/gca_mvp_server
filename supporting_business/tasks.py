from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from .models import *
from supporting_business.models import *
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
@task(name="sum_two_numbers")
def add(x, y):
    return x + y


@task(name="multiply_two_numbers")
def mul(a,b):
    total = a* (b * random.randint(3, 100))
    print(total)
    return total


@task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)


@task(name="make_alarm")
def make_alarm(sb_id, category, to=None):

    origin_sb = SupportBusiness.objects.get(id=sb_id)
    user=[]

    if to ==None:
        for s in Appliance.objects.all().filter(sb=origin_sb):
            user.append(s.startup.user.additionaluserinfo)
        for s in AdditionalUserInfo.objects.all().filter(interest=origin_sb):
            user.append(s)
        for f in origin_sb.filter.all():
            st = Startup.objects.all().filter(filter=f)
            for s in st:
                user.append(s.user.additionaluserinfo)
        for s in list(set(user)):
            Alarm( user=s, origin_sb=origin_sb, category=category,  content="", ).save()
            title = "[" + origin_sb.title + "] 지원 사업이 공고되었습니다.. "
            content = "[" + origin_sb.title + "]이 지원 사업이 공고되었습니다. 로그인 후 확인해주세요. "
            # to = origin_sb.user.user.username
            to = "cto@tradelink.kr"
            send_mail(
                title,
                content,
                'neogelon@gmail.com',
                [to],
                fail_silently=False,
            )
            print("send_mail")
    else:
        to = AdditionalUserInfo.objects.get(id=to)
        Alarm(user=to, origin_sb=origin_sb, category=category, content="", ).save()
        if category==2:
            # 블라인드 처리
            title = "["+origin_sb.title+"] 이 블라인드 처리되었습니다. "
            content = "["+origin_sb.title+"]이 블라인드 처리되었습니다. 로그인 후 확인해주세요. "
            #to = origin_sb.user.user.username
            to = "cto@tradelink.kr"
        else:
            title = "[" + origin_sb.title + "] 이 승인 요청중입니다. "
            content = "[" + origin_sb.title + "]이 승인 요청중입니다. 로그인 후 확인해주세요. "
            #to = AdditionalUserInfo.objects.get(id=1).user.username
            to = "cto@tradelink.kr"
        send_mail(
        title,
        content,
        'neogelon@gmail.com',
        [to],
        fail_silently=False,
    )
    return sb_id


@task(name="alarm_to_startup_due")
def alarm_to_startup_due():
    today_min = datetime.datetime.now()
    origin_sb = SupportBusiness.objects.all().filter(complete=False)
    # 마감 알람 3시간 전
    for sb in origin_sb:
        print((today_min - sb.apply_end).total_seconds()/3600) #시간
        user_set =[]
        if((today_min - sb.apply_end).total_seconds()/60 < 5 and (today_min - sb.apply_end).total_seconds()/60 > 0 ):
            for user in AdditionalUserInfo.objects.all().filter(interest=sb):   # 관심 설정한 유저
                try:
                    user_set.append(user.user.startup)
                except:
                    pass
            print(user_set)
            for s in Startup.objects.all().filter(appliance__sb=sb):
                try:
                    user_set.append(s.user.startup)
                except:
                    pass
            print(user_set)
            print(set(user_set))
            for s in set(user_set):
                Alarm(
                    user=s,
                    origin_sb=sb,
                    category=1,
                    content="",
                ).save()

    return True


