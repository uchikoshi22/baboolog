# -*- coding: utf-8 -*-
# mobile.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('mobile/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'mobile/index': 'mobile.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='mobile.views.index'),
    Rule('/to_pc', endpoint='to_pc', view='mobile.views.to_pc'),
    Rule('/logout', endpoint='logout', view='mobile.views.logout'),
    Rule('/login', endpoint='login', view='mobile.views.login'),
    Rule('/baboo', endpoint='baboo', view='mobile.views.baboo'),
    Rule('/comment', endpoint='comment', view='mobile.views.comment'),
    Rule('/diary', endpoint='diary', view='mobile.views.diary'),
    Rule('/update_baboo', endpoint='update_babo', view='mobile.views.update_baboo'),
  )
]

