# -*- coding: utf-8 -*-
# core.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('core/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'core/index': 'core.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='core.views.index'),
    Rule('/login', endpoint='login', view='core.views.login'),
    Rule('/register', endpoint='register', view='core.views.register'),
    Rule('/new_profile', endpoint='new_profile', view='core.views.new_profile'),
    Rule('/new_family', endpoint='new_family', view='core.views.new_family'),
    Rule('/new_baby', endpoint='new_baby', view='core.views.new_baby'),
    Rule('/baboo', endpoint='baboo', view='core.views.baboo'),
    Rule('/comment', endpoint='comment', view='core.views.comment'),
    Rule('/diary', endpoint='diary', view='core.views.diary'),
    Rule('/profile', endpoint='profile', view='core.views.profile'),
    Rule('/add_guardian', endpoint='add_guardian', view='core.views.add_guardian'),
  )
]

