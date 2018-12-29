from django import forms
from django.core.exceptions import ValidationError

from blog.models import *

class UserForm(forms.Form):
    username = forms.CharField(min_length=4,
                               max_length=10,
                               error_messages={
                                   "required":"用户名不能为空",
                                   "max_length":"用户名不能超过10位",
                                   "min_length":"用户名不能少于4位",
                               })
    password = forms.CharField(min_length=6,
                               error_messages={
                                   "required":"密码不能为空",
                                   "min_length":"密码不能少于6位"
                               })
    repeat_pwd = forms.CharField(error_messages={
        "required":"确认密码不能为空"
    })
    email = forms.EmailField(error_messages={
        "invalid":"格式错误",
        "required":"邮箱不能为空"
    })

    # 局部钩子
    def clean_username(self):
        value = self.cleaned_data.get('username')
        if  UserInfo.objects.filter(username=value).exists():
            raise ValidationError('用户已存在')
        else:
            return value

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("password")
        repeat_pwd = self.cleaned_data.get("repeat_pwd")
        if pwd == repeat_pwd:
            return self.cleaned_data
        else:
            raise ValidationError("密码不一致")
