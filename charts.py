#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
#
""" Charting """

import logging

import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import models
import bblib
import chartlib
import urllib
import time
import datetime
import reqlib

class MainPage(webapp.RequestHandler):
  def get(self):
    
    # determine default values when nothing comes in query string
    # m=0 (meterid)
    # c=2 (chartid)
    # dt=2010-03-07 (datetime to show)
    # s=0 (size, big or small)  
    
    params = reqlib.getParams(self)

    chartlib.renderChartsPage(self, params)


application = webapp.WSGIApplication([
  (r'/charts/(.*)/(.*)/(.*)/(.*)', MainPage),  
  ('/charts', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
