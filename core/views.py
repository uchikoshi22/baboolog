# -*- coding: utf-8 -*-
"""
core.views
"""


import sys
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout

from google.appengine.api import users
from kay.utils import render_to_response
from kay.auth.decorators import login_required
from werkzeug import (
  unescape, redirect, Response,
)

from datetime import date
import datetime
import time


from core.models import *
from core.forms import *

GMAIL = "@gmail.com"

# Views here.
###############################################################################

@login_required
def add_guardian(request):
  user = request.user
  account = MyUser.all().filter('email = ', user.email).get()
  family = account.family
  if family == None:
    return redirect('/new_family')
  else:
    if request.method == "POST":
      guardian_email = request.values.get('guardian_email')
      if GMAIL in guardian_email:
        if guardian_email in family.guardian_emails:
          pass
        else:
          family.guardian_emails.append(guardian_email)
          family.put()

        guardian = Guardian.all().filter('email = ', guardian_email).get()
        if guardian:
          guardian.relatives.append(family.key().id())
        else:
          guardian = Guardian()
          guardian.email = guardian_email
          guardian.relatives.append(family.key().id())
        guardian.put()
          
        return redirect('/profile')
      else:
        babies_list = Baby.all().filter('family = ', account.family)
        wrong_email = guardian_email
        return render_to_response('core/profile.html',
                                  {'user': user,
                                   'babies_list': babies_list,
                                   'account': account,
                                   'wrong_email': wrong_email,
                                   })
    

@login_required
def profile(request):
  user = request.user
  account = MyUser.all().filter('email = ', user.email).get()
  babies_list = Baby.all().filter('family = ', account.family)

  return render_to_response('core/profile.html',
                            {'user': user,
                             'babies_list': babies_list,
                             'account': account,
                             })

@login_required
def diary(request):
  user = request.user
  acount = MyUser.all().filter('email = ', user.email).get()
  babies_list = Baby.all().filter('family = ', acount.family)
  
  if request.values.get('key'):
    key = request.values.get('key')
    baby = Baby.get_by_id(int(key))
  else:
    primary_baby = Baby.all().filter('family = ', acount.family).filter('is_primary = ', True).get()
    baby = primary_baby

  activities = Activity.all().filter('baby = ', baby)
  
  return render_to_response('core/diary.html',
                            {'user': user,
                             'babies_list': babies_list,
                             'baby': baby,
                             'activities': activities,
                              })

@login_required
def comment(request):
  user = request.user
  acount = MyUser.all().filter('email = ', user.email).get()
  babies_list = Baby.all().filter('family = ', acount.family)
  form = CommentForm()
  #today = datetime.date.today()
  jst_today = get_jst_today()
  today = jst_today
  query_date = get_datetime_object(today)
  post_message = Comment.all().filter('user = ', user).filter('date = ', query_date).get()
  
  if request.method == "POST" and form.validate(request.form):
    if post_message == None:
      comment = Comment()
    else:
      comment = post_message
    
    key = request.values.get('key')
    baby = Baby.get_by_id(int(key))

    date = form['date']
    message = form['message']
    
    comment.baby = baby
    comment.user = user
    comment.date = date
    comment.message = message

    comment.put()

    return redirect('/baboo')
    
    
  else:
    if is_registered(user):
      if not has_baby(user):
        return redirect('/new_baby')
      else:
        if is_invited_family(user):
          return redirect('/')
        elif not has_family(user):
          return redirect('/new_family')
        elif not has_role(user):
          return redirect('/new_profile')
        else:
          if request.values.get('key'):
            key = request.values.get('key')
            baby = Baby.get_by_id(int(key))
          else:
            primary_baby = Baby.all().filter('family = ', acount.family).filter('is_primary = ', True).get()
            baby = primary_baby
            now = time.strftime('%Y-%m-%d %H:%M')

          #acount = MyUser.all().filter('email = ', user.email).get()
          if is_father(user):
            partner_email = acount.family.mother_email
          else:
            partner_email = acount.family.father_email
          partner = MyUser.all().filter('email = ', partner_email).get()
          partner_post = Comment.all().filter('user = ', partner).filter('date = ', query_date).get()
          if partner_post == None or partner_post == "":
            partner_message = ""
          else:
            partner_message = partner_post.message
            
          
          return render_to_response('core/comment.html',
                                     {'user': user,
                                      'baby': baby,
                                      'babies_list': babies_list,
                                      'form': form.as_widget(),
                                      'today': today,
                                      'post_message': post_message,
                                      'partner_message': partner_message,
                                      })
    
    else:
      return redirect('/login')
    

@login_required
def baboo(request):
  user = request.user
  acount = MyUser.all().filter('email = ', user.email).get()
  babies_list = Baby.all().filter('family = ', acount.family)
  today = date.today()
  form = ActivityForm()
  jst_time = get_jst_time_now()
  jst_today = get_jst_today()
  if request.method == "POST" and form.validate(request.form):
    is_milk = request.values.get('is_milk')
    is_nappy = request.values.get('is_nappy')
    is_food = request.values.get('is_food')
    if is_milk == "True" or is_nappy == "True" or is_food == "True":
      activity = Activity()
      activity_date = form['activity_date']
      activity.activity_date = activity_date
      if is_milk == "True":
        #activity.milk_time = form['milk_time']
        milk_time = form['milk_time']
        activity.milk_time = get_string_datetime(activity_date, milk_time)

        activity.milk_class = int(request.values.get('milk_class'))
        if activity.milk_class == 0:
          activity.milk_cc = float(0)
        else:
          if form['milk_cc'] == "":
            activity.milk_cc = float(0)
          else:
            activity.milk_cc = float(form['milk_cc'])
        
      if is_nappy == "True":
        #activity.nappy_time = form['nappy_time']
        nappy_time = form['nappy_time']
        activity.nappy_time = get_string_datetime(activity_date, nappy_time)
        activity.is_poo_poo = form['is_poo_poo']
      if is_food == "True":
        #activity.baby_food_time = form['baby_food_time']
        baby_food_time = form['baby_food_time']
        activity.baby_food_time = get_string_datetime(activity_date, baby_food_time)
        ingredients = request.values.get('ingredients')
        activity.ingredients = ingredients.split(",")
        
      activity.user = user
      baby_key = request.values.get('baby')
      baby = Baby.get_by_id(int(baby_key))
      activity.baby = baby
      activity.put()
      return redirect('/baboo')
    else:
      return redirect('/')
      
    return redirect('/baboo')
  else:
    if is_registered(user):
      if not has_baby(user):
        return redirect('/new_baby')
      else:
        if is_invited_family(user):
          return redirect('/invited_family')
        elif not has_family(user):
          return redirect('/new_family')
        elif not has_role(user):
          return redirect('/new_profile')
        else:
          if request.values.get('key'):
            key = request.values.get('key')
            baby = Baby.get_by_id(int(key))
          else:
            primary_baby = Baby.all().filter('family = ', acount.family).filter('is_primary = ', True).get()
            baby = primary_baby
          now = time.strftime('%Y-%m-%d %H:%M')
          return render_to_response('core/baboo.html',
                                    {'user': user,
                                     'baby': baby,
                                     'babies_list': babies_list,
                                     'jst_time': jst_time,
                                     'jst_today': jst_today,
                                     'form': form.as_widget(),
                                     })
    else:
      return redirect('/login')
        

@login_required
def new_baby(request):
  user = request.user
  form = BabyForm()
  today = date.today()
  if request.method == "POST" and form.validate(request.form):
    baby = Baby()
    baby.name = form['name']
    baby.nickname = form['nickname']
    baby.gender = int(request.values.get('gender'))
    baby.birthday = form['birthday']
    baby.height = form['height']
    baby.weight = form['weight']
    baby.is_primary = form['is_primary']

    acount = MyUser.all().filter('email = ', user.email).get()

    if baby.is_primary == False:
      if len(acount.family.babies) < 1:
        baby.is_primary = True
    else:
      # If the other babiy are already marked as a primary, then change
      # the status and this baby is marked as a primary.
      change_prev_primary(user)
    
    baby.family = acount.family
    baby.put()

    family = acount.family
    family.babies.append(str(baby.key().id()))
    family.put()

    return redirect('/')
    
  else:
    if is_registered(user):
      babies_list = []
      if not has_role(user) and not is_invited_family(user):
        return redirect('/new_profile')
      elif not has_family(user):
        return redirect('/new_family')
      else:
        babies_list = get_babies_list(user)
        return render_to_response('core/new_baby.html',
                                  {'user': user,
                                   'form': form.as_widget(),
                                   'today': today,
                                   'babies_list': babies_list,
                                   })
    else:
      return redirect('/login')
      

@login_required
def new_family(request):
  user = request.user
  form = FamilyForm()
  acount = MyUser.all().filter('email = ', user.email).get()
  if request.method == "POST" and form.validate(request.form):
    family = Family()
    family.guardian_name = form['guardian_name']
    family.guardian_password = request.values.get('password')

    member = Member()

    if acount.role == 0:
      family.father_email = user.email
      family.mother_email = form['mother_email']
      member.email = form['mother_email']
    else: #acount.role = 1 <= user is a mother
      family.father_email = form['father_email']
      family.mother_email = user.email
      member.email = form['father_email']

    family.put()
    member.put()

    acount.family = family
    acount.put()
    
    return redirect('/')
  
  else:
    if is_registered(user):
      if has_family(user):
        return redirect('/family')
      else:
        if is_invited_family(user):
          return redirect('/invited_family')
        elif not has_role(user):
          return redirect('/new_profile')
        else:
          return render_to_response('core/new_family.html',
                                    {'user': user,
                                     'form': form.as_widget(),
                                     'acount': acount,
                                     })
        
    else:
      return redirect('/login')

@login_required
def new_profile(request):
  user = request.user
  if request.method == "POST":
    role = request.values.get('f_or_m')
    acount = MyUser.all().filter('email = ', user.email).get()
    acount.role = int(role)
    acount.put()
    return redirect('/')
  else:
    if is_registered(user):
      if has_role(user):
        return redirect('/profile')
      else:
        return render_to_response('core/new_profile.html',
                                  {'user': user,
                                    })
    else:
      return redirect('/login')

def index(request):
  user = request.user
  babies_list = []
  if user.is_anonymous():
    return redirect('/login')
  else:
    acount = MyUser.all().filter('email = ', user.email).get()
    if is_registered(user):
      if is_invited_family(user):
        if is_father(user) == True:
          acount.family = Family.all().filter('father_email = ', user.email).get()
          acount.role = 0
        if is_mother(user) == True:
          acount.family = Family.all().filter('mother_email = ', user.email).get()
          acount.role = 1


        baby = Baby.all().filter('family = ', acount.family).get()
        if not baby == None:
          acount.has_baby = True
        acount.put()

      if has_role(user):
        role_warning = False
      else:
        role_warning = True
      if has_family(user):
        family_warning = False
      else:
        family_warning = True
      if has_baby(user) == True:
        baby_warning = False
        babies_list = get_babies_list(user)
      else:
        baby_warning = True
      return render_to_response('core/index.html',
                                {'user': user,
                                 'role_warning': role_warning,
                                 'family_warning': family_warning,
                                 'baby_warning': baby_warning,
                                 'babies_list': babies_list,
                                 })
    else:  # if user is not a registered user.
      return redirect('/login')

@login_required
def register(request):
  user = request.user
  if is_registered(user):
    pass
  else:
    member = Member()
    member.email = user.email
    member.put()
  return redirect('/')

def login(request):
  user = request.user
  return render_to_response('core/login.html',
                            {'user': user,
                             })


# Common Libralies
###############################################################################
def is_registered(user):
  member = Member.all().filter('email = ', user.email).get()
  if member == None:
    return False
  else:
    return True

def has_role(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.role == None:
    return False
  else:
    return True

def has_family(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.family == None:
    return False
  else:
    return True

def is_father(user):
  father = Family.all().filter('father_email = ', user.email).get()
  if father == None:
    return False
  else:
    return True

def is_mother(user):
  mother = Family.all().filter('mother_email = ', user.email).get()
  if mother == None:
    return False
  else:
    return True

def is_guardian(user):
  guardian = Guardian.all().filter('email = ', user.email).get()
  if guardian == None:
    return False
  else:
    return True

def is_invited_family(user):
  member = is_registered(user)
  acount = has_family(user)
  if (member and not acount) and (is_father(user) or is_mother(user) or is_guardian(user)) :
    return True
  else:
    return False

def has_baby(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  if acount.family == None or acount.family.babies == None or len(acount.family.babies) < 1:
    return False
  else:
    return True

def get_babies_list(user):
  babies_list = []
  acount = MyUser.all().filter('email = ', user.email).get()
  baby_keys = acount.family.babies
  for baby_key in baby_keys:
    baby = Baby.get_by_id(int(baby_key))
    babies_list.append(baby)
  return babies_list
                  
def change_prev_primary(user):
  acount = MyUser.all().filter('email = ', user.email).get()
  family = acount.family
  babies = Baby.gql("WHERE family=:1 AND is_primary=True", family)
  prev_primary = babies.get()
  prev_primary.is_primary = False
  prev_primary.put()

def get_jst():
  utc = datetime.datetime.utcnow()
  jst = utc + datetime.timedelta(hours=9)
  return jst

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

def get_jst_today():
  jst = get_jst()
  if jst.month < 10:
    month = "0" + str(jst.month)
  else:
    month = str(month)
  if jst.day < 10:
    day = "0" + str(jst.day)
  else:
    day = str(jst.day)
  jst_today = str(jst.year) + "-" + month + "-" + day
  return jst_today


def get_string_datetime(d,t):
  dt = str(d) + " " + str(t)
  string_datetime = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
  return string_datetime

def get_datetime_object(d):
  datetime_object = datetime.datetime.strptime(d, '%Y-%m-%d')
  return datetime_object

