#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# mganley2000@gmail.com
#
""" myenergyuse request library of functions """

import logging 
import cgi

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import models
import urllib
import time
import datetime
import bblib
import chartlib


def getParams(page):
    # determine default values when nothing comes in query string
    # m=0 (meterid)
    # c=2 (chartid)
    # dt=2010-03-07 (datetime to show)
    # s=0 (size, big or small)  
    
    params = models.ChartParameters()
    
    params.ChartID = chartlib.processRequestChart(page, page.request.get('c'))
    
    user = users.get_current_user()
    
    m = page.request.get('m')
    if m == '':
      # get a default meter, lookup from Meter table 
      q = db.GqlQuery("SELECT * FROM Meter WHERE owner = :1", user)
      meters = q.fetch(50)
 
      if meters:
        params.MeterID = meters[0].meterID
        if (int(params.ChartID) == 4):
          params.SelectedDate = meters[0].ReadingForDayByHour_timestamp
        elif (int(params.ChartID) == 3):
          params.SelectedDate = meters[0].ReadingForDayBy15Minute_timestamp
        elif (int(params.ChartID) == 2):
          params.SelectedDate = meters[0].ReadingForHourByMinute_timestamp
        elif (int(params.ChartID) == 1):
          params.SelectedDate = meters[0].Reading15MinuteBySecond_timestamp
      else:
        params.MeterID = 0
        # Set Selected Date to most recent time period
        if (int(params.ChartID) != 1):
          params.SelectedDate = chartlib.getAdjustedTodayDateString(page,0)
        else:
          params.SelectedDate = chartlib.getAdjustedTodayDateString(page,1)          
        
    else:
      # try to query meter, get default if not valid
      q = db.GqlQuery("SELECT * FROM Meter WHERE owner = :1 and meterID = :2", user, m)
      meter = q.get()
      
      if( meter ):
        params.MeterID = meter.meterID
        if (int(params.ChartID) == 4):
          params.SelectedDate = meters.ReadingForDayByHour_timestamp
        elif (int(params.ChartID) == 3):
          params.SelectedDate = meters.ReadingForDayBy15Minute_timestamp
        elif (int(params.ChartID) == 2):
          params.SelectedDate = meters.ReadingForHourByMinute_timestamp
        elif (int(params.ChartID) == 1):
          params.SelectedDate = meters.Reading15MinuteBySecond_timestamp        
      else:
        params.MeterID = 0
        # Set Selected Date to most recent time period
        if (int(params.ChartID) != 1):
          params.SelectedDate = chartlib.getAdjustedTodayDateString(page,0)
        else:
          params.SelectedDate = chartlib.getAdjustedTodayDateString(page,1)         
          
    params.RequestedDate = chartlib.processRequestDate(page, page.request.get('dt'), params.SelectedDate, params.ChartID)
    
    # set prev/next dates
    if (int(params.ChartID) == 1):
      params.RequestedDateNext = chartlib.getDateStringAddSubHour(page, params.RequestedDate, "add")      
      params.RequestedDateBack = chartlib.getDateStringAddSubHour(page, params.RequestedDate, "sub")      
    elif (int(params.ChartID) == 2):
      params.RequestedDateNext = chartlib.getDateStringAddSubDay(page, params.RequestedDate, "add")      
      params.RequestedDateBack = chartlib.getDateStringAddSubDay(page, params.RequestedDate, "sub")
    elif (int(params.ChartID) == 3):
      params.RequestedDateNext = chartlib.getDateStringAddSubWeek(page, params.RequestedDate, "add")      
      params.RequestedDateBack = chartlib.getDateStringAddSubWeek(page, params.RequestedDate, "sub")      
    elif (int(params.ChartID) == 4):
      params.RequestedDateNext = chartlib.getDateStringAddSubMonth(page, params.RequestedDate, "add")      
      params.RequestedDateBack = chartlib.getDateStringAddSubMonth(page, params.RequestedDate, "sub")
      
    params.Size = chartlib.processRequestSize(page, page.request.get('s'))
    
    logging.debug(params.MeterID)
    logging.debug(params.ChartID)
    logging.debug(params.SelectedDate)
    logging.debug(params.RequestedDate)
    logging.debug(params.RequestedDateBack)
    logging.debug(params.RequestedDateNext)     
    logging.debug(params.Size)

    return(params)
    
