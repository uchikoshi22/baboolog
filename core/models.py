# -*- coding: utf-8 -*-
# core.models

from google.appengine.ext import db
#from google.appengine.api import users
from kay.auth.models import GoogleUser
import kay.db

class Member(db.Model):
  email = db.EmailProperty()

class Family(db.Model):
  family_name = db.StringProperty()
  father_name = db.StringProperty()
  father_email = db.EmailProperty()
  mother_name = db.StringProperty()
  mother_email = db.EmailProperty()
  guardian_emails = db.ListProperty(str)
  babies = db.StringListProperty()
  

class MobileUser(db.Model):
  mobile_id = db.StringListProperty()
  
class MyUser(GoogleUser):
  # myuser's alias is member
  g_user = GoogleUser
  family = db.ReferenceProperty(Family)
  role = db.IntegerProperty()  #0 = father, 1 = mother
  m_user = db.StringProperty()
  m_password = db.StringProperty()

class Guardian(db.Model):
  email = db.StringProperty()
  relatives = db.ListProperty(int) # save the key of Family Class
  

class Baby(db.Model):
  name = db.StringProperty()
  nickname = db.StringProperty()
  birthday = db.DateProperty()
  gender = db.IntegerProperty() # 0 = boy, 1 = girl
  height = db.FloatProperty()
  weight = db.FloatProperty()
  is_primary = db.BooleanProperty()
  family = db.ReferenceProperty(Family)

class Activity(db.Model):
  baby = db.ReferenceProperty(Baby)
  user = kay.db.OwnerProperty()
  milk_time = db.DateTimeProperty()
  milk_cc = db.FloatProperty()
  milk_class = db.IntegerProperty() # 0 = breast milk,  1 = milk
  nappy_time = db.DateTimeProperty()
  is_poo_poo = db.BooleanProperty()
  baby_food_time = db.DateTimeProperty()
  ingredients = db.StringListProperty()
  activity_date = db.DateProperty()
  
  
class Comment(db.Model):
  baby = db.ReferenceProperty(Baby)
  user = kay.db.OwnerProperty()
  message = db.TextProperty()
  date = db.DateProperty()
  created = db.DateTimeProperty(auto_now_add=True)
