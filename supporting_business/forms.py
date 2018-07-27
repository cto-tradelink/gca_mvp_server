from django import forms
from django.forms import ModelForm, TextInput, Textarea
from .models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput

import os
# missing imports
from django.utils.safestring import mark_safe
from os import path
from django import forms


class FormatString(str):
    def format(self, *args, **kwargs):
        arguments = list(args)
        arguments[1] = path.basename(arguments[1])
        return super(FormatString, self).format(*arguments, **kwargs)


class ClearableFileInput(forms.ClearableFileInput):
    url_markup_template = FormatString('<a href="{0}">{1}</a>')


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    username = forms.EmailField(label="아이디", label_suffix="",
                                widget=forms.TextInput(attrs={'placeholder': 'example@gconnect.co.kr'}),
                                error_messages={'invalid': _(
                                    "이메일 형식과 맞지 않습니다.")}
                                )

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '비밀번호를 입력하세요'}), label="비밀번호",
                               label_suffix="",
                               )

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("같은 아이디의 유저가 존재합니다. 다른 이메일을 사용하여주세요."))
        else:
            return self.cleaned_data['username']


class ManagerForm(forms.ModelForm):
    class Meta:
        model = AdditionalUserInfo
        fields = ["name", "position", "tel", "web"]
        labels = {
            "name": _("이름"),
            "position": _("담당(직급,소속)"),
            "tel": _("전화번호"),
            "web": _("추가정보 안내 홈페이지 URL")
        }
        widgets = {
            "name": TextInput(),
            "position": TextInput(),
            "tel": TextInput(),
            "web": TextInput(),
        }


class NewStartupUp(forms.Form):
    uid = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label="기업명", label_suffix="")
    established_date = forms.DateField(label="설립일", label_suffix="", widget=forms.TextInput(
        attrs={'class': 'addy_title', "placeholder": "YYYY-MM-DD 형태로 입력"}))
    category = forms.CharField(label="사업분야", label_suffix="", required=False)
    address_0_title = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={'class': 'addy_title', "placeholder": "소재지명 ex)본사", }))
    address_0 = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'class': 'addy',
                                                                                        "placeholder": "주소를 입력하세요", }))
    address_0_detail = forms.CharField(label="", required=False,
                                       widget=forms.TextInput(
                                           attrs={'placeholder': '세부 주소를 입력하세요.', 'class': 'addy_detail'}))

    address_1_title = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={'class': 'addy_title', "placeholder": "소재지명 ex)본사", }))
    address_1 = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'class': 'addy',
                                                                                        "placeholder": "주소를 입력하세요", }))
    address_1_detail = forms.CharField(label="", required=False,
                                       widget=forms.TextInput(
                                           attrs={'placeholder': '세부 주소를 입력하세요.', 'class': 'addy_detail'}))
    address_2_title = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={'class': 'addy_title', "placeholder": "소재지명 ex)본사", }))
    address_2 = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'class': 'addy',
                                                                                        "placeholder": "주소를 입력하세요", }))
    address_2_detail = forms.CharField(label="", required=False,
                                       widget=forms.TextInput(
                                           attrs={'placeholder': '세부 주소를 입력하세요.', 'class': 'addy_detail'}))

    address = forms.CharField(label="소재지", widget=forms.TextInput(attrs={'placeholder': '주소를 입력하세요.'}),
                              label_suffix="", required=False)

    email = forms.CharField(label="대표 메일", widget=forms.TextInput(attrs={'placeholder': 'company@mail.com'}),
                            label_suffix="", required=False)
    website = forms.CharField(label="홈페이지", widget=forms.TextInput(attrs={'placeholder': 'www.companywebsite.com'}),
                              label_suffix="", required=False)
    employee_number = forms.CharField(label="구성원수", label_suffix="", required=False)


class NewStartupBot(forms.Form):
    keyword = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': '#키워드로 입력하세요.'}))
    desc = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': ''}))
    service_products = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': ''}))
    short_desc = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': ''}))

    revenue_before_year_0 = forms.CharField(required=False, )
    revenue_before_year_1 = forms.CharField(required=False, )
    revenue_before_year_2 = forms.CharField(required=False, )
    revenue_before_0 = forms.CharField(required=False, )
    revenue_before_1 = forms.CharField(required=False, )
    revenue_before_2 = forms.CharField(required=False, )

    export_before_year_0 = forms.CharField(required=False, )
    export_before_year_1 = forms.CharField(required=False, )
    export_before_year_2 = forms.CharField(required=False, )
    export_before_0 = forms.CharField(required=False, )
    export_before_1 = forms.CharField(required=False, )
    export_before_2 = forms.CharField(required=False, )

    fund_before_0 = forms.CharField(required=False, )
    fund_before_1 = forms.CharField(required=False, )
    fund_before_2 = forms.CharField(required=False, )
    fund_before_3 = forms.CharField(required=False, )
    fund_before_4 = forms.CharField(required=False, )
    fund_before_5 = forms.CharField(required=False, )
    fund_before_6 = forms.CharField(required=False, )
    fund_before_7 = forms.CharField(required=False, )
    fund_before_8 = forms.CharField(required=False, )
    fund_before_9 = forms.CharField(required=False, )

    fund_before_year_0 = forms.CharField(required=False, )
    fund_before_year_1 = forms.CharField(required=False, )
    fund_before_year_2 = forms.CharField(required=False, )
    fund_before_year_3 = forms.CharField(required=False, )
    fund_before_year_4 = forms.CharField(required=False, )
    fund_before_year_5 = forms.CharField(required=False, )
    fund_before_year_6 = forms.CharField(required=False, )
    fund_before_year_7 = forms.CharField(required=False, )
    fund_before_year_8 = forms.CharField(required=False, )
    fund_before_year_9 = forms.CharField(required=False, )

    fund_before_agent_0 = forms.CharField(required=False, )
    fund_before_agent_1 = forms.CharField(required=False, )
    fund_before_agent_2 = forms.CharField(required=False, )
    fund_before_agent_3 = forms.CharField(required=False, )
    fund_before_agent_4 = forms.CharField(required=False, )
    fund_before_agent_5 = forms.CharField(required=False, )
    fund_before_agent_6 = forms.CharField(required=False, )
    fund_before_agent_7 = forms.CharField(required=False, )
    fund_before_agent_8 = forms.CharField(required=False, )
    fund_before_agent_9 = forms.CharField(required=False, )




class MyPageUp(forms.Form):
    # pw =forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': ''}), label="PW",
    #                            label_suffix="",
    #                            )
    uid = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label="이름", label_suffix="" ,  required=False)


class MyPageBot(forms.Form):
    tel = forms.CharField(label="핸드폰 번호", label_suffix="", help_text="핸드폰 번호로 유용한 알람이 갑니다.", required=False)
    additional_email = forms.CharField(label="추가 email", label_suffix="",
                                       required=False)
    agreement = forms.BooleanField(label="수신 동의", label_suffix="", required=False)
    # position = forms.CharField(label="내 직책", label_suffix="",  required=False, widget=forms.TextInput(attrs={'placeholder': 'CEO'}))


class SupportBusinessForm(forms.Form):
    title = forms.CharField(label="지원 사업명", widget=forms.TextInput(attrs={'placeholder': '지원 사업명을 입력하세요'}))
    from_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': '공고 시작 날짜'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': '공고 마감 날짜'}))
    abstract = forms.CharField(widget=forms.Textarea)
    target = forms.CharField(widget=forms.Textarea)
    detail = forms.CharField(widget=forms.Textarea)
    apply_method = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "예) 온라인 폼, 사업자 등록증 첨부"}))
    etc = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "※ 자세한 사항은 소상공인시장진흥공단(www.semas.or.kr) → 알림마당 → 공지사항 참조(☞바로가기)"}))


class SupportForm(forms.ModelForm):
    class Meta:
        model = SupportBusiness
        fields = '__all__'

        labels = {
            "title": _("지원사업명")
        }
        widgets = {
            "title": TextInput(attrs={'placeholder': '지원 사업명을 입력하세요'}),
            "from_date": TextInput(attrs={'placeholder': '공고 시작 날짜'}),
            "end_date": TextInput(attrs={'placeholder': '공고 마감 날짜'}),
            "abstract": Textarea,
            "target": Textarea,
            "detail": Textarea,
            "apply_method": Textarea(attrs={"placeholder": "예) 온라인 폼, 사업자 등록증 첨부"}),
            "etc": Textarea(attrs={"placeholder": "※ 자세한 사항은 소상공인시장진흥공단(www.semas.or.kr) → 알림마당 → 공지사항 참조(☞바로가기)"})
        }


class ManagerAccountForm(forms.ModelForm):
    class Meta:
        model = AdditionalUserInfo
        fields = ["name", "position", "tel", "web", "department", "belong_to"]
        labels = {}
        widgets = {
            "name": TextInput(),
            "position": TextInput(),
            "tel": TextInput(),
            "web": TextInput(),
            "department": TextInput(),
            "belong_to": TextInput()
        }


class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            "oversea":TextInput(attrs={'placeholder': '해외 진출 국가'}),
            "found_date":TextInput(attrs={"readonly":"true"}),
            "business_number":TextInput(attrs={'placeholder': '000-00-0000'}),
            'ir_file': ClearableFileInput,
            'business_file': ClearableFileInput,
            'tax_file': ClearableFileInput,
            'fund_file': ClearableFileInput,
            'ppt_file': ClearableFileInput,
            'etc_file': ClearableFileInput,
        }


class SupportBusinessForm(forms.ModelForm):
    class Meta:
        model = SupportBusiness
        fields = '__all__'
        exclude = ['filter', 'finance_amount', 'hit', 'created_at', 'user']
        widgets = {
            "title": Textarea(attrs={'placeholder': 'ex)넥스트 스타트업 어워드 '}),
            "employee_num": TextInput(attrs={"type": "hidden"}),
            "title_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "title_sub": Textarea(attrs={'placeholder': 'ex)PlayX4(사업명1) / B2B상담회(사업명2) '}),
            "title_sub_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "short_desc": Textarea(attrs={"placeholder": "띄어쓰기포함 14 글자 ", "maxlength": "28"}),
            "business_period_start": TextInput(attrs={"class": "due_input"}),
            "business_period_end": TextInput(attrs={"class": "due_input"}),
            "pro_0_open": TextInput(attrs={"class": "due_input"}),
            "pro_1_open": TextInput(attrs={"class": "due_input"}),
            "pro_2_open": TextInput(attrs={"class": "due_input"}),
            "place": Textarea(attrs={"placeholder": "ex. 판교 경기문화창조허브 9층 스마트 오피스"}),
            "place_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "subject": Textarea(attrs={"placeholder": "ex. 신진 메이커스 스타트업과 바이어 매칭 장 제공, 콘텐츠 스타트업의 해외 진출을 위한 벤치마킹 기회 제공"}),
            "subject_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "icon_set": TextInput(attrs={"type": "hidden"}),
            "business_detail": Textarea(
                attrs={"placeholder": "ex. 한국관 구성 및 해외 게임 퍼블리셔 및 투자사와의 1:1 비즈니스 상담, 1박2일 콘텐츠 아트토이 해커톤"}),
            "business_detail_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "object": Textarea(attrs={"placeholder": "ex. 경기도내 IT 스타트업, 온라인 모바일 게임 기업"}),
            "object_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "condition": Textarea,
            "condition_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "condition_etc": Textarea,
            "condition_etc_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "object_span": Textarea(attrs={"placeholder": ""}),
            "object_span_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "recruit_size": TextInput(attrs={"class": "due_input", "placeholder": "ex)10 - 숫자만 입력"}),
            "prefer": Textarea(attrs={"placeholder": "ex. 직전년도 PlaX4 참가기업, G-Start A 참가기업, 북부경기문화창조허브 지원사업 참가자"}),
            "prefer_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "constraint": Textarea(attrs={"placeholder": "ex. 금융기관 등으로부터 채무불이행으로 규제중인자 또는 기업"}),
            "constraint_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "choose_method": Textarea,
            "pro_0_choose": Textarea(attrs={"placeholder": "ex. 서류평가, 1.5~2배수 선정"}),
            "pro_0_choose_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "pro_0_start": TextInput(attrs={"class": "due_input"}),
            "pro_0_end": TextInput(attrs={"class": "due_input"}),
            "pro_0_criterion": Textarea(attrs={"placeholder": "ex. 역량(20), 기획력(30), 시장전망(20)"}),
            "pro_0_criterion_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),

            "pro_1_choose": Textarea(attrs={"placeholder": "ex. 서류평가, 1.5~2배수 선정"}),
            "pro_1_choose_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "pro_1_start": TextInput(attrs={"class": "due_input"}),
            "pro_1_end": TextInput(attrs={"class": "due_input"}),
            "pro_1_criterion": Textarea(attrs={"placeholder": "ex. 역량(20), 기획력(30), 시장전망(20)"}),
            "pro_1_criterion_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),

            "pro_2_choose": Textarea(attrs={"placeholder": "ex. 서류평가, 1.5~2배수 선정"}),
            "pro_2_choose_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "pro_2_start": TextInput(attrs={"class": "due_input"}),
            "pro_2_end": TextInput(attrs={"class": "due_input"}),
            "pro_2_criterion": Textarea(attrs={"placeholder": "ex. 역량(20), 기획력(30), 시장전망(20)"}),
            "pro_2_criterion_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "supply_content": Textarea(attrs={"placeholder": "ex. 상금 1등 2000만원, 입주 6개월(연장평가를 통해 최대 2년), 공동 홍보물 제작"}),
            "supply_content_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "supply_condition": Textarea(attrs={"placeholder": "ex. 선정 후 경기도 본사 이전 필수, 해외 일정 전일 100% 참여"}),
            "supply_condition_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "ceremony_start": TextInput(attrs={"class": "due_input"}),
            "ceremony_end": TextInput(attrs={"class": "due_input"}),
            "faq": Textarea,
            "faq_tag": TextInput(attrs={'placeholder': '해시태그를 입력하세요.', "class": "hash"}),
            "additional_faq": Textarea,
            "etc": Textarea,
            "meta": TextInput,
            "etc_file_title": Textarea(attrs={"placeholder": "기타 필요한 파일 이름. - 100글자 이내"}),
            "apply_start": forms.HiddenInput(),
            "apply_end": forms.HiddenInput(),

            "from_date": TextInput(attrs={'placeholder': '공고 시작 날짜'}),
            "end_date": TextInput(attrs={'placeholder': '공고 마감 날짜'}),
            "abstract": Textarea,
            "target": Textarea,
            "detail": Textarea,
            "apply_method": Textarea(attrs={"placeholder": "예) 온라인 폼, 사업자 등록증 첨부"}),
            "etc": Textarea(attrs={"placeholder": ""})
        }
