#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# mganley2000@gmail.com
#
""" myenergyuse library of functions """

import logging 
import cgi

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import urllib
import time
import datetime
import models


def TopPage(page, pageName):
    page.response.out.write("<html><head><title>%s</title>" % pageName )
    
def TopInc(page):
    page.response.out.write("""
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="/css/styles.css" type="text/css" media="all" title="Normal" />
    <link rel="stylesheet" href="/css/energy.css" type="text/css" media="all" title="Normal" />
    <script type='text/javascript' src='http://www.google.com/jsapi'></script>
    """)
    
def TopEndHead(page):
    page.response.out.write("</head>")
    
def TopNav(page, params, a, d, e):
    page.response.out.write("""
    <div id="normal" style="position: relative; top:0px; left: 4px; width: 99%;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%">
    <tr><td class=hit-logo nowrap><a href="/"><img src="/images/minilogo.gif" width="16" height="16" border="0"></a><span class="hit-goog">My Energy Use</span>
    </td></tr>""")
    
    if( params == "null"):
        params = models.ChartParameters()
        params.Size = 1
        
    # when size = 2 or size = 3 this is a gadget, so supress top nav to save vertical space
    if(int(params.Size) < 2 ):
        page.response.out.write("""<tr><td class=hit-bar>""")
    
        if a:   
            page.response.out.write('<span class="hit-navhomea">Home</span>')
        else:
            page.response.out.write('<a class="hit-navhome" href="/">Home</a>')
            
        user = users.get_current_user()
        
        if user:
            if d:   
                page.response.out.write('<span class="hit-navsel">Notify</span>')
            else:
                page.response.out.write('<a class="hit-navlink" href="/notify">Notify</a>')
    
            if e:   
                page.response.out.write('<span class="hit-navsel">Settings</span>')
            else:
                page.response.out.write('<a class="hit-navlink" href="/settings">Settings</a>')
                
            page.response.out.write('<a class="hit-sign" href="%s">Sign Out</a>' % (users.create_logout_url("/")) )
        else:
            page.response.out.write('<a class="hit-sign" href="%s">Sign In</a>' % (users.create_login_url("/")) )
            
        page.response.out.write('</td>') 
        page.response.out.write('</tr>')
    
    page.response.out.write("""
    </table>
    <div class=hit-divider></div>
    <div id="stats">
    """)
 

# <span class="nav-chart-link"><a href="charts?m=0&c=2&dt=2010-03-12+01:00:00&s=0">Hour</a></span>
#  <span class="nav-chart-select"><a href="charts?m=0&c=2&dt=2010-03-12&s=0"><<</a></span>
#  <span class="nav-chart-select"><a href="charts?m=0&c=2&dt=2010-03-12&s=0">Day</a></span>
#  <span class="nav-chart-select"><a href="charts?m=0&c=2&dt=2010-03-12&s=0">>></a></span>
# <span class="nav-chart-link"><a href="charts?m=0&c=2&dt=2010-03-12&s=0">Week</a></span>
# <span class="nav-chart-link"><a href="charts?m=0&c=2&dt=2010-03-12&s=0">Month</a></span>
#  % (params.MeterID, params.ChartID, urllib.quote(params.RequestedDate))
def ChartNav(page, params):

    if int(params.ChartID) == 1:
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=1&dt=%s&s=%s"><<</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateBack), params.Size ) )        
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=1&dt=%s&s=%s">Hour</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=1&dt=%s&s=%s">>></a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateNext), params.Size ) )        
    else:
        page.response.out.write('<span class="nav-chart-link"><a href="charts?m=%s&c=1&dt=%s&s=%s">Hour</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )        
 
    if int(params.ChartID) == 2:
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=2&dt=%s&s=%s"><<</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateBack), params.Size ) )        
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=2&dt=%s&s=%s">Day</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=2&dt=%s&s=%s">>></a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateNext), params.Size ) )        
    else:
        page.response.out.write('<span class="nav-chart-link"><a href="charts?m=%s&c=2&dt=%s&s=%s">Day</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )        
 
    if int(params.ChartID) == 3:
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=3&dt=%s&s=%s"><<</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateBack), params.Size ) )        
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=3&dt=%s&s=%s">Week</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=3&dt=%s&s=%s">>></a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateNext), params.Size ) )        
    else:
        page.response.out.write('<span class="nav-chart-link"><a href="charts?m=%s&c=3&dt=%s&s=%s">Week</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )        
 
    if int(params.ChartID) == 4:
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=4&dt=%s&s=%s"><<</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateBack), params.Size ) )        
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=4&dt=%s&s=%s">Month</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )
        page.response.out.write('<span class="nav-chart-select"><a href="charts?m=%s&c=4&dt=%s&s=%s">>></a></span>' % ( params.MeterID, urllib.quote(params.RequestedDateNext), params.Size ) )        
    else:
        page.response.out.write('<span class="nav-chart-link"><a href="charts?m=%s&c=4&dt=%s&s=%s">Month</a></span>' % ( params.MeterID, urllib.quote(params.RequestedDate), params.Size ) )        
  
    if int(params.Size) == 0:
        page.response.out.write('<span class="nav-size"><a href="charts?m=%s&c=%s&dt=%s&s=%s">(wide)</a></span>' % ( params.MeterID, params.ChartID, urllib.quote(params.RequestedDate), 1 ) )        
    elif int(params.Size) == 1:
        page.response.out.write('<span class="nav-size"><a href="charts?m=%s&c=%s&dt=%s&s=%s">(reduce)</a></span>' % ( params.MeterID, params.ChartID, urllib.quote(params.RequestedDate), 0 ) )        

    
def BottomNav(page, params):
    
    if( params == "null"):
        params = models.ChartParameters()
        params.Size = 1
        
    if(int(params.Size) < 2 ):
        page.response.out.write("""
        </div>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" class=hit-footer><tr><td>	
        <span class=hit-arr>All Rights Reserved</span>
        <br><span=hitcr>Copyright &copy;2010 MyEnergyUse on Google</span></td></tr></table>
        </div>
        """)
    else:
        page.response.out.write("""
        </div>
        <span class="foot-jump"><a href="/charts" target="_new">goto site</a></span>
        </div>
        """)        

def BottomPage(page):
    page.response.out.write("""
    </body></html>
    """)
 
 
