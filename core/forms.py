# -*- coding: utf-8 -*-

from kay.utils import forms
from kay.utils.validators import ValidationError
from core.models import *
from google.appengine.ext import db

class CommentForm(forms.Form):
  message = forms.TextField(label="メッセージ")
  date = forms.DateField(label="日にち", required=True)
  

class ActivityForm(forms.Form):
  milk_time = forms.TimeField(label="ミルクの時間")
  milk_cc = forms.FloatField(label="cc")
  nappy_time = forms.TimeField(label="おむつの時間")
  is_poo_poo = forms.BooleanField(label="うんちしてた？")
  baby_food_time = forms.TimeField(label="離乳食")
  activity_date = forms.DateField(label="日にち", required=True)
  

class BabyForm(forms.Form):
  name = forms.TextField(label="赤ちゃんの名前", required=True)
  nickname = forms.TextField(label="赤ちゃんのニックネーム", required=True)
  birthday = forms.DateField(label="赤ちゃんの誕生日", required=True)
  height = forms.FloatField(label="生まれたときの身長")
  weight = forms.FloatField(label="生まれたときの体重")
  is_primary = forms.BooleanField(label="最初に表示する")


class FamilyForm(forms.Form):
  father_email = forms.EmailField(label="パパのGmailアドレス")
  mother_email = forms.EmailField(label="ママのGmailアドレス")
  guardian_name = forms.TextField(label="おじいちゃん・おばあちゃん用のログイン名")

  def validate_father_email(self, value):
    users = Member.all().filter('email = ', value).get()
    if not users == None:
      raise ValidationError(u"このメールアドレスは既に登録されています")

  def validate_mother_email(self, value):
    users = Member.all().filter('email = ', value).get()
    if not users == None:
      raise ValidationError(u"このメールアドレスは既に登録されています")


class MobileAccountForm(forms.Form):
  mobile_id = forms.TextField(label="ログイン名")

  def validate_mobile_id(self, value):
    mobile_user = MobileUser.all().filter('mobile_id = ', value).get()
    if not mobile_user == None:
      raise ValidationError(u"この携帯電話アクセス用ログイン名は既に使われています")
