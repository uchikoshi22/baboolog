# -*- coding: utf-8 -*-
"""
mobile.views
"""

import logging
from google.appengine.api import users
from google.appengine.api import memcache
from werkzeug import (
  unescape, redirect, Response,
)
from werkzeug.exceptions import (
  NotFound, MethodNotAllowed, BadRequest
)

from kay.utils import (
  render_to_response, reverse,
  get_by_key_name_or_404, get_by_id_or_404,
  to_utc, to_local_timezone, url_for, raise_on_dev
)
from kay.i18n import gettext as _
from kay.auth.decorators import login_required

import sys
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout

from core.models import *
from core.forms import *

import datetime
import time

# Create your views here.

def update_baboo(request):
  encoding_class = get_mobile_encoding(request)
  m_user = request.values.get('m_user')
  m_password = request.values.get('m_password')
  account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()

  key = request.values.get('key')
  baby = Baby.get_by_id(int(key))

  bid = request.values.get('bid')
  activity = Activity.get_by_id(int(bid))

  form = ActivityForm()

  if request.method == "POST" and form.validate(request.form):
    bid = request.values.get('bid')
    activity = Activity.get_by_id(int(bid))
    activity.baby = baby
    activity.user = account
    activity.activity_date = form['activity_date']
    is_milk = request.values.get('is_milk')
    if is_milk == "True":
      activity.milk_time = get_string_datetime(activity.activity_date, form['milk_time'])
      activity.milk_class = int(request.values.get('milk_class'))
      if activity.milk_class:
        activity.milk_cc = form['milk_cc']
      else:
        activity.milk_cc = float(0)
      activity.milk_class = int(request.values.get('milk_class'))
    else:
      activity.milk_time = ""
      activity.milk_cc = float(0)
      activity.milk_class = None
    is_nappy = request.values.get('is_nappy')
    if is_nappy == "True":
      activity.nappy_time = get_string_datetime(activity.activity_date, form['nappy_time'])
      is_poo_poo = request.values.get('is_poo_poo')
      if is_poo_poo == "True":
        activity.is_poo_poo = True
      else:
        activity.is_poo_poo = False
    else:
      activity.nappy_time = None
      activity.is_poo_poo = None
      
    is_food = request.values.get('is_food')
    if is_food == "True":
      activity.baby_food_time = get_string_datetime(activity.activity_date, form['baby_food_time'])
      ingredients = request.values.get('ingredients')
      activity.ingredients = ingredients.split(",")
    else:
      activity.baby_food_time = None
      activity.ingredients = []

    activity.put()

    redirect_path = "/m/diary?key=" + str(baby.key().id()) + "&m_user=" + m_user + "&m_password=" + m_password

    return redirect(redirect_path)
      
  else:
    if activity.milk_time:
      milk_time = str(activity.milk_time)[-8:-3]
    else:
      milk_time = ""

    if activity.nappy_time:
      nappy_time = str(activity.nappy_time)[-8:-3]
    else:
      nappy_time = ""

    if activity.baby_food_time:
      baby_food_time = str(activity.baby_food_time)[-8:-3]
    else:
      baby_food_time = ""
      
    ingredients = ""
    if len(activity.ingredients):
      for ingredient in activity.ingredients:
        ingredients += ingredient + ","
      
    
    babies_list = Baby.all().filter('family = ', account.family)
    return render_to_response('mobile/update_baboo.html',
                              {'m_user': m_user,
                               'm_password': m_password,
                               'account': account,
                               'baby': baby,
                               'babies_list': babies_list,
                               'activity': activity,
                               'form': form.as_widget(),
                               'milk_time': milk_time,
                               'nappy_time': nappy_time,
                               'baby_food_time': baby_food_time,
                               'ingredients': ingredients,
                               })

def diary(request):
  encoding_class = get_mobile_encoding(request)
  m_user = request.values.get('m_user')
  m_password = request.values.get('m_password')
  account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()

  if account == None:
    return redirect('/m/logount')
  else:
    if request.values.get('key'):
      key = request.values.get('key')
      baby = Baby.get_by_id(int(key))
    else:
      primary_baby = Baby.all().filter('family = ', account.family).filter('is_primary = ', True).get()
      baby = primary_baby
    babies_list = Baby.all().filter('family = ', account.family)

    if request.values.get('view_day'):
      today = request.values.get('view_day')
    else:
      today = get_jst_today()
    today_object = datetime.datetime.strptime(today, '%Y-%m-%d')
    query_date = datetime.datetime.date(today_object)
    activities = Activity.all().filter('baby = ', baby).filter('activity_date = ', query_date)
    if activities == None:
      activities == None
    else:
      activities = get_activity_flat_list(activities)

    # Get messages from parents
    family = account.family
    comment = Comment.all().filter('baby = ', baby).filter('date = ', query_date).filter('user = ', account).get()
    if account.role == 0:
      if not comment == None:
        father_message = comment.message
      else:
        father_message = ""
      partner_email = family.mother_email
      partner = MyUser.all().filter('email = ', partner_email).get()
      comment = Comment.all().filter('baby = ', baby).filter('date = ', query_date).filter('user = ', partner).get()
      if not comment == None:
        mother_message = comment.message
      else:
        mother_message = ""
    else:
      if not comment == None:
        mother_message = comment.message
      else:
        mother_message = None
      partner_email = family.father_email
      partner = MyUser.all().filter('email = ', partner_email).get()
      comment = Comment.all().filter('baby = ', baby).filter('date = ', query_date).filter('user = ', partner).get()
      if not comment == None:
        father_message = comment.message
      else:
        father_message = ""


    return render_to_response('mobile/diary.html',
                              {'baby': baby,
                               'babies_list': babies_list,
                               'today': today,
                               'm_user': m_user,
                               'm_password': m_password,
                               'account': account,
                               'activities': activities,
                               'father_message': father_message,
                               'mother_message': mother_message,
                               })
    
    
    


def comment(request):
  encoding_class = get_mobile_encoding(request)
  m_user = request.values.get('m_user')
  m_password = request.values.get('m_password')
  account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()
  if account == None:
    return redirect('/m/logout')
  else:
    form = CommentForm()
    today = get_jst_today()
    today_object = datetime.datetime.strptime(today, '%Y-%m-%d')
    #query_date = datetime.datetime.date(today_object)
    post_comment = Comment.all().filter('user = ', account).filter('date = ', today_object).get()
    if request.method == "POST" and form.validate(request.form):
      key = request.values.get('key')
      baby = Baby.get_by_id(int(key))
      m_user = request.values.get('m_user')
      m_password = request.values.get('m_password')
      account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()
      if account == None:
        return redirect('/m/logout')
      else:
        query_date = form['date']
        post_comment = Comment.all().filter('user = ', account).filter('date = ', query_date).get()
        if not post_comment == None:
          comment = post_comment
        else:
          comment = Comment()
        comment.baby = baby
        comment.user = account
        comment.message = form['message']
        comment.date = form['date']
        comment.put()
        redirect_path = "/m/?key=" + str(baby.key().id()) + "&m_user=" + m_user + "&m_password=" + m_password
        return redirect(redirect_path)
      
      
      pass
    else:
      if request.values.get('key'):
        key = request.values.get('key')
        baby = Baby.get_by_id(int(key))
      else:
        primary_baby = Baby.all().filter('family = ', account.family).filter('is_primary = ', True).get()
        baby = primary_baby
      babies_list = Baby.all().filter('family = ', account.family)
      return render_to_response('mobile/comment.html',
                                {'baby': baby,
                                 'babies_list': babies_list,
                                 'form': form.as_widget(),
                                 'today': today,
                                 'm_user': m_user,
                                 'm_password': m_password,
                                 'account': account,
                                 'post_comment': post_comment,
                                 })


def baboo(request):
  m_user = request.values.get('m_user')
  m_password = request.values.get('m_password')
  account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()
  encoding_class = get_mobile_encoding(request)
  form = ActivityForm()
  if m_user == None or account == None:
    return redirect('/m/logout')
  else:
    if request.method == "POST" and form.validate(request.form):
      is_milk = request.values.get('is_milk')
      is_nappy = request.values.get('is_nappy')
      is_food = request.values.get('is_food')
      if is_milk == "True" or is_nappy == "True" or is_food == "True":
        activity = Activity()
        activity_date = form['activity_date']
        activity.activity_date = activity_date
        if is_milk == "True":
          milk_time = form['milk_time']
          activity.milk_time = get_string_datetime(activity_date, milk_time)
          activity.milk_class = int(request.values.get('milk_class'))
          if activity.milk_class == 0:
            activity.milk_cc = float(0)
          else:
            if form['milk_cc'] == "":
              activity.milk_cc = float(0)
            else:
              if form['milk_cc'] == "":
                activity.milk_cc = float(0)
              else:
                activity.milk_cc = float(form['milk_cc'])
        if is_nappy == "True":
          nappy_time = form['nappy_time']
          activity.nappy_time = get_string_datetime(activity_date, nappy_time)
          activity.is_poo_poo = form['is_poo_poo']
        if is_food == "True":
          baby_food_time = form['baby_food_time']
          activity.baby_food_time = get_string_datetime(activity_date, baby_food_time)
          ingredients = request.values.get('ingredients')
          activity.ingredients = ingredients.split(",")
          
          
        activity.user = account
        baby_key = request.values.get('baby')
        baby = Baby.get_by_id(int(baby_key))
        activity.baby = baby
        activity.put()
        redirect_path = "/m/baboo?key=" + str(baby.key().id()) + "&m_user=" + m_user + "&m_password=" + m_password
        return redirect(redirect_path)
      else:
        redirect_path = "/m/baboo?key=" + str(baby.key().id()) + "&m_user=" + m_user + "&m_password=" + m_password
        return redirect(redirect_path)
    else:
      if request.values.get('key'):
        key = request.values.get('key')
        baby = Baby.get_by_id(int(key))
      else:
        primary_baby = Baby.all().filter('family = ', account.family).filter('is_primary = ', True).get()
        baby = primary_baby
      babies_list = Baby.all().filter('family = ', account.family)
      today = get_jst_today()
      time_now = get_jst_time_now()
      return render_to_response('mobile/baboo.html',
                                {'baby': baby,
                                 'babies_list': babies_list,
                                 'form': form.as_widget(),
                                 'today': today,
                                 'time_now': time_now,
                                 'm_user': m_user,
                                 'm_password': m_password,
                                 })



def index(request):
  #machine = str(request.user_agent)
  encoding_class = get_mobile_encoding(request)
  m_user = request.values.get('m_user')
  m_password = request.values.get('m_password')
  account = MyUser.all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()

  if account == None:
    return redirect('/m/logout')
  else:
    if request.values.get('key'):
      key = request.values.get('key')
      baby = Baby.get_by_id(int(key))
    else:
      primary_baby = Baby.all().filter('family = ', account.family).filter('is_primary = ', True).get()
      if primary_baby == None:
        baby = None
      else:
        baby = primary_baby
    babies_list = Baby.all().filter('family = ', account.family)
    if babies_list.count() < 1:
      babies_list = None
    return render_to_response('mobile/index.html',
                              {'baby': baby,
                               'babies_list': babies_list,
                               'encoding_class': encoding_class,
                               'm_user': m_user,
                               'm_password': m_password,
                               })


def login(request):
  encoding_class = get_mobile_encoding(request)
  if request.method == "POST":
    m_user = request.values.get('m_user')
    m_password = request.values.get('m_password')
    account = MyUser().all().filter('m_user = ', m_user).filter('m_password = ', m_password).get()
    if account == None:
      auth_error = True
      return render_to_response('mobile/login.html',
                                {'encoding_class': encoding_class,
                                 'auth_error': auth_error,
                                 'm_user': m_user,
                                 })
    else:
      redirect_path = "/m/?m_user=" + m_user + "&m_password=" + m_password
      return redirect(redirect_path)
      """
      account = MyUser.all().filter('m_user = ', m_user).get()
      baby = Baby.all().filter('family = ', account.family).filter('is_primary = ', True).get()
      babies_list = Baby.all().filter('family = ', account.family)
      return redirect('/m/')
      return render_to_response('mobile/index.html',
                                {'encoding_class' : encoding_class,
                                 'm_user': m_user,
                                 'm_password': m_password,
                                 'baby': baby,
                                 'babies_list': babies_list,
                                })
      """
                                
    
  else:
    return render_to_response('mobile/login.html',
                              {'encoding_class': encoding_class,
                               })


def logout(request):
  user = request.user
  encoding_class = get_mobile_encoding(request)
  return render_to_response('mobile/logout.html',
                            {'user': user,
                             'encoding_class': encoding_class,
                             })

def to_pc(user):
  return render_to_response('mobile/to_pc.html', {})



###############################################################################
def get_mobile_encoding(request):
  machine = str(request.user_agent)
  if "KDDI" in machine:
    encoding_class = "au"
  else:
    encoding_class = "other"
  return encoding_class

def get_jst():
  utc = datetime.datetime.utcnow()
  jst = utc + datetime.timedelta(hours=9)
  return jst

def get_jst_today():
  jst = get_jst()
  if jst.month < 10:
    month = "0" + str(jst.month)
  else:
    month = str(jst.month)
  if jst.day < 10:
    day = "0" + str(jst.day)
  else:
    day = str(jst.day)
  jst_today = str(jst.year) + "-" + month + "-" + day
  return jst_today
    
def get_jst_time_now():
  jst = get_jst()
  if jst.hour < 10:
    hour = "0" + str(jst.hour)
  else:
    hour = str(jst.hour)
  if jst.minute < 10:
    minute = "0" + str(jst.minute)
  else:
    minute = str(jst.minute)
  jst_time = hour + ":" + minute
  return jst_time


def is_invited_family(user):
  member = is_registered(user)
  acount = has_family(user)
  if (member and not acount) and (is_father(user) or is_mother(user)):
    return True
  else:
    return False


def has_family(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.family == None:
    return False
  else:
    return True


def has_role(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.role == None:
    return False
  else:
    return True


def is_registered(user):
  member = Member.all().filter('email = ', user.email).get()
  if member == None:
    return False
  else:
    return True


def has_baby(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.family == None or acount.family.babies == None or len(acount.family.
babies) < 1:
    return False
  else:
    return True

def get_string_datetime(d,t):
  dt = str(d) + " " + str(t)
  string_datetime = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
  return string_datetime

def get_datetime_object(d):
  datetime_object = datetime.datetime.strptime(d, '%Y-%m-%d')
  return datetime_object
          

def get_activity_flat_list(activities):
  activity_flat_list = []
  for activity in activities:
    if activity.milk_time:
      activity_flat_list.append(["milk", activity.key().id(), str(activity.milk_time)[-8:-3], activity.milk_cc, activity.milk_class])
    if activity.nappy_time:
      activity_flat_list.append(["nappy", activity.key().id(), str(activity.nappy_time)[-8:-3], activity.is_poo_poo])
    if activity.baby_food_time:
      activity_flat_list.append(["food", activity.key().id(), str(activity.baby_food_time)[-8:-3], activity.ingredients])


  if len(activity_flat_list) < 2:
    pass
  else:
    activity_flat_list.sort(lambda x, y: cmp(x[2],y[2]))
  return activity_flat_list
