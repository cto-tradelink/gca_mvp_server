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

