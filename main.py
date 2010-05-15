#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# http://code.google.com/p/myenergyuse/
# watchmyted - at- gmail.com
#
""" Home Page """

import logging

import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import models
import bblib
import uuid

class MainPage(webapp.RequestHandler):
  def get(self):
    self.renderPage()
  
  def renderPage(self):
    user = users.get_current_user()
    
    if user:
      self.redirect('/charts')
    
    else:
      bblib.TopPage(self, "Welcome - My Energy Use")
      bblib.TopInc(self)
      bblib.TopEndHead(self)
      bblib.TopNav(self, "null", 1, 0, 0)
      
      self.response.out.write("""
      <table border="0" cellspacing="0" cellpadding="0" width="100%" class="hit-layout">
      <tr>
       <td id="hit-a">
           <div class="hit-content">
           <h3>Charting Power and Energy Use</h3>
           <p>
           
           Sign-In to view Charts
           
           </div>
       </td>
       </tr>
       </table>
           
       """)
        
      bblib.BottomNav(self,"null")
      bblib.BottomPage(self)
    
            
application = webapp.WSGIApplication([
  ('/', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
