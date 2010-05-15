#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# http://code.google.com/p/myenergyuse/
# watchmyted - at- gmail.com
#
""" myenergyuse chart library of functions """

import logging 
import cgi

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import urllib
import time
import datetime
import bblib


def renderChartsPage(page, params):
    
    bblib.TopPage(page, "Welcome - My Energy Use")
    bblib.TopInc(page)
    bblib.TopEndHead(page)
    bblib.TopNav(page, params, 1, 0, 0)
    
    page.response.out.write("""
    <table border="0" cellspacing="0" cellpadding="0" width="100%" class="hit-layout">
    <tr>
    </td>
    <td id="hit-a">""")
    
    # when this is a gadget, the size will be 2 or 3; suppress this heading when this is a gadget
    if( int(params.Size < 2)):
        page.response.out.write("""
             <div class="hit-content">
             <h3>Charting Power and Energy Use</h3>
             <div>""")
    
    page.response.out.write("""
         <div class="nav-chart"> """)
    
    bblib.ChartNav(page, params)
        
    page.response.out.write("</div>")
    page.response.out.write("<br>")
    
    name = 'chart' + str(params.ChartID)
    
    page.response.out.write("<div class='charts'><img src='chartsvc/%s/%s/%s/%s/%s'></div>" % ( params.MeterID, params.ChartID, params.RequestedDate, params.Size, name ) )
         
    page.response.out.write("""
     </td>
     </tr>
     </table>
     """)      

    bblib.BottomNav(page, params)
    bblib.BottomPage(page)


def processRequestChart(page, c):
    # incoming parameter is "c" for chartid
    # choices are 1, 2, 3 or 4
    
    if c == '':
      # get a default chart
      chartid = 2
      
    else:
      if( int(c) != 1 and int(c) != 2 and int(c) != 3 and int(c) != 4 ):
        chartid = 2
      else:
        chartid = c
    
    return(chartid)
    

def processRequestDate(page, dt, selectedDate, chartID):
    # incoming parameter is "dt" for datetime, "selectedDate" from database or default
    try:
      dtfixed =  urllib.unquote(dt)
      
      if (int(chartID) != 1):
        struct_time = time.strptime(dtfixed,"%Y-%m-%d")  # causes exception if illegal datetime
        dtfixed = datetime.datetime.strptime(dtfixed,"%Y-%m-%d")
      else:
        struct_time = time.strptime(dtfixed,"%Y-%m-%d %H:00:00")  # causes exception if illegal datetime
        dtfixed = datetime.datetime.strptime(dtfixed,"%Y-%m-%d %H:00:00")
        
      err = 0
      
    except ValueError:
      err = 1
    else:
      pass
      
    if( err == 0 ):
      newDate = dtfixed
      if (int(chartID) != 1):
        retVal = newDate.strftime("%Y-%m-%d")        
      else:
        retVal = newDate.strftime("%Y-%m-%d %H:00:00")
    else:     
      retVal = selectedDate    
     
    return(retVal)
 

    
def getAdjustedTodayDateString(page, withHour):
    # simple get a date and adjust for GMT
    # 5 hours and 18 minutes (localtime issue)
    
    deltaMinutes = datetime.timedelta(minutes=-318)
    setdate = datetime.datetime.utcnow()      
    newDate = setdate + deltaMinutes
    logging.debug("**** AdjustedTodayDateString ****")
    logging.debug(newDate.strftime("%Y-%m-%d %H:%M:00"))
    
    if( int(withHour) == 0 ):
      retVal = newDate.strftime("%Y-%m-%d")
    else:
      retVal = newDate.strftime("%Y-%m-%d %H:00:00")      
      
    return(retVal)
  
 
def getDateStringAddSubMonth(page, dt, addSubStr):
    if( addSubStr == "add"):
      delta = datetime.timedelta(days=30)
    else:
      delta = datetime.timedelta(days=-30)
    
    # must be sure to remove anything that is hour:min:sec from dt string before strptime
    #logging.debug(dt[:10])
    dt = dt[:10]
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
    newDate = dt + delta
    
    retVal = newDate.strftime("%Y-%m-%d")      
      
    return(retVal)
  
  
def getDateStringAddSubWeek(page, dt, addSubStr):
    if( addSubStr == "add"):
      delta = datetime.timedelta(days=7)
    else:
      delta = datetime.timedelta(days=-7)
    
    # must be sure to remove anything that is hour:min:sec from dt string before strptime
    #logging.debug(dt[:10])
    dt = dt[:10]
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
    newDate = dt + delta
    
    retVal = newDate.strftime("%Y-%m-%d")      
      
    return(retVal)
  
  
def getDateStringAddSubDay(page, dt, addSubStr):
    if( addSubStr == "add"):
      delta = datetime.timedelta(days=1)
    else:
      delta = datetime.timedelta(days=-1)
    
    # must be sure to remove anything that is hour:min:sec from dt string before strptime
    #logging.debug(dt[:10])
    dt = dt[:10]
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
    newDate = dt + delta
    
    retVal = newDate.strftime("%Y-%m-%d")      
      
    return(retVal)
  
  
def getDateStringAddSubHour(page, dt, addSubStr):
    if( addSubStr == "add"):
      delta = datetime.timedelta(hours=1)
    else:
      delta = datetime.timedelta(hours=-1)
    
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:00:00")
    newDate = dt + delta
    
    retVal = newDate.strftime("%Y-%m-%d %H:00:00")      
      
    return(retVal)    
   

def processRequestSize(page, s):
    if s == '':
        s = 0
      
    size = int(s)
    
    if( size != 1 and size != 2 and size != 3):
        size = 0
      
    return(size)
  
  
def original_processRequestDate(self, dt):
    # incoming parameter is "dt" for datetime
    # choices are 0,1,2, or 3
    err = 0
    
    deltaMinutes = datetime.timedelta(minutes=-318)   # 5 hours and 18 minutes (localtime issue)
      
    dtfixed =  urllib.unquote(dt)
    
    if dt == '':
      # get today    
      err = 1
    else:
      # adjust
      try:  
        logging.debug(dtfixed)
        struct_time = time.strptime(dtfixed,"%Y-%m-%d %H:%M:00")
        err = 0
        dtfixed = datetime.datetime.strptime(dtfixed,"%Y-%m-%d %H:%M:00")
      except ValueError:
        err = 1
      else:
        pass
      
    if( err == 0 ):
      newDate = dtfixed + deltaMinutes
    else:     
      setdate = datetime.datetime.utcnow()      
      newDate = setdate + deltaMinutes
          
    retVal = newDate.strftime("%Y-%m-%d %H:00:00")
      
    return(retVal)


