#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# http://code.google.com/p/myenergyuse/
# watchmyted - at- gmail.com
#
""" Frequently asked questions """

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
    bblib.TopPage(self, "Not Found or Error - MyEnergyUse on Google")
    bblib.TopInc(self)
    bblib.TopEndHead(self)
    bblib.TopNav(self, "null", 1, 0, 0)
    
    self.response.out.write("""
    <table border="0" cellspacing="0" cellpadding="0" width="100%" class="hit-layout">
    <tr>
    <td id="hit-a">
        <div class="hit-content">
        <h3>Page Not Found or Error on Page</h3>
        <p> 
         The page was not found or there was an error.  Try again one of the links at the top of the page.
        </p>
        </div>
    </td>
    </tr>
    </table>
        
    """)
        
    bblib.BottomNav(self, "null")
    bblib.BottomPage(self)
    


application = webapp.WSGIApplication([
  ('/.*', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()