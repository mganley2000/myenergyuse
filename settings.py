#!/usr/bin/env python
#
# Copyright 2009 myenergyuse
#
""" Preferences """

import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import models
import bblib

class MainPage(webapp.RequestHandler):
  def get(self):
    bblib.TopPage(self, "Settings - My Energy Use")
    bblib.TopInc(self)
    bblib.TopEndHead(self)
    bblib.TopNav(self, "null", 0, 0, 1)
    
    self.response.out.write("""
    <table border="0" cellspacing="0" cellpadding="0" width="100%" class="hit-layout">
    <tr>
       <td id="hit-a">
        <div class="hit-content">
        <h3>Charting Power and Energy Use</h3>
        <p>   
        <br>
        You will be able to specify your current rate.  <br><br>Basic, tiered, or time-of-use.
        </div>
    </td>
    </tr>
    </table>
        
    """)
        
    bblib.BottomNav(self,"null")
    bblib.BottomPage(self)
    


application = webapp.WSGIApplication([
  ('/settings', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
