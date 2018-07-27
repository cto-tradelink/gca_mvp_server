from django import template
import re
from django.utils.safestring import mark_safe
import calendar
import  inspect
import os
import datetime

register = template.Library()

@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value

@register.simple_tag
def user_name(value):
    #print(value)
    #print(inspect.getmembers(value))
    #print(inspect.getmembers(value.socialaccount_set.first()))
    #print(value.socialaccount_set.first().extra_data["email"])
    name = value.additionaluserinfo.name

    if name == "":
        name = "유저"
    return name

@register.simple_tag
def user_avatar(value):
    try:
        if value.additionaluserinfo.avatar:
            img = value.additionaluserinfo.avatar.url
            return mark_safe('<img src="' + img + '">')
        elif value.socialaccount_set.first() :
            img = (value.socialaccount_set.first().get_avatar_url())
            if img is None:
                return ""
            else:
                return mark_safe('<img src="' + img + '">')
        else:
            return ""
    except:
        return ""

@register.simple_tag
def user_social(value):
    try:
        social = value.socialaccount_set.first().provider
    except:
        social = ""

    if social=="naver":
        social = "네이버"
    if social=="facebook":
        social = "페이스북"
    if social=="kakao":
        social = "카카오"
    if social == "":
        social = "없음"

    return social




@register.simple_tag
def geo_code(value):
    return value.replace(" ","+")

@register.simple_tag
def date_format(value):

    string = str(value).replace("-",".")
    return string




@register.filter
def filename(value):
    try:
        return os.path.basename(value.file.name)
    except:
        return ""


@register.filter
def calc_day(value):

    day_string = ["월","화","수","목","금","토","일"]
    try:
        return  value.split(" ")[1]+"월 "+value.split(" ")[2]+"일"+"("+day_string[datetime.date( int(value.split(" ")[0]),int(value.split(" ")[1]), int(value.split(" ")[2])).weekday()]+") 까지"
    except:
        return  ""

@register.filter
def calc_d_day(value):
    today = datetime.date.today()
    someday = datetime.date(int(value.split(" ")[0]), int(value.split(" ")[1]), int(value.split(" ")[2]))
    print(someday-today)
    diff = (someday-today).days
    if diff < 30:
        return "D-" + str(diff)
    else:
        return ""



@register.simple_tag
def calc_year(value):
    try:

        start_time = datetime.datetime(value.year, value.month, value.day)
        how_long = datetime.datetime.now() - start_time

        return int(how_long.days/365)
    except:
        return ""



@register.filter
def local_first(value):
    try:

        return value.split(" ")[0]
    except:
        return ""





@register.filter
def remove_spaces(value):
    return value.replace(' ', '+')


@register.filter
def avg_calc(list):
    arr = []
    for l in list:
        (arr.append(int(l.count)))
    return sum(arr)/len(list)