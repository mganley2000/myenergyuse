#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# http://code.google.com/p/myenergyuse/
# watchmyted - at- gmail.com
#

import logging

import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import models
import bblib
import urllib
import __builtin__
import calendar


class MainPage(webapp.RequestHandler):
  def get(self, meterid, chartid, dt, size, name):
    self.renderPage(meterid, chartid, dt, size, name)
    
  def renderPage(self, meterid, chartid, dt, size, name):
    # POST data to Google Chart API and pass PNG back to caller
    user = users.get_current_user()

    if user:
      
      data_valid = 0
      meter = int(meterid)
      chart = int(chartid)
      timestamp = dt
      
      logging.debug("****chartsvc****")
      logging.debug(urllib.unquote(timestamp))
    
      if (chart == 1 ):
        # hour chart (chart 60 minutes - not 3600 seconds yet)
        dt = datetime.datetime.strptime(urllib.unquote(timestamp),"%Y-%m-%d %H:00:00")
        todayDate = dt.strftime("%Y-%m-%d %H:00:00")
        
        logging.debug("******Hour Chart*******")
        logging.debug(todayDate)
         
        uom = "W"
        q = db.GqlQuery("SELECT * FROM ReadingForHourByMinute WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp = :4", user, meter, uom, todayDate )
        db_rows = q.fetch(1)
     
        if db_rows:
        
          workProps = self.getDataValues60ForOnlyOneHour(db_rows)
          
          #line chart sample
          # http://chart.apis.google.com/chart?chs=320x280&cht=lc&chd=t:40,60,-1,-1,47,75,0,60,52,45,42,20,7,30,32,33,35,77
          #    &chco=0000FF&chxt=x,x,y,y&chxl=0:|12am|6am|12pm|6pm|12am|1:|+|3:|+|+W&chxr=2,0,80
          #    &chds=0,80&chg=25,12.5&chls=1,4,2&chtt=Power+for+day+by+minute|March+3&chts=111111,12

          maxTop = int(round(workProps.max,-3))  #round up to nearest 100
          step = maxTop / 10
          chxr = "2" + "," + "0" + "," + str(maxTop) + "," + str(step)
          chds = "0" + "," + str(maxTop)
          chg = "25," + str(10) + ",1,4"
          if( int(size) == 0):
            chs = "420x380"
          elif( int(size) == 1):
            chs = "750x380"
          elif( int(size) == 2):
            chs = "280x300"
          elif( int(size) == 3):
            chs = "750x380"
            
          logging.debug(size)
          logging.debug("******Hour Chart*******")
        
          chart_props = {
                    "chs": chs,
                    "cht": "lc",                    
                    "chd": workProps.formattedDatapoints,
                    "chco": "0000FF",
                    "chxt": "x,x,y,y",
                    "chxl": "0:|1|15|30|45|60|1:| |3:| | W",                                    
                    "chxr": chxr,
                    "chds": chds,
                    "chg": chg,                      
                    "chls": "1,4,0",
                    "chtt": "Power for Hour per minute|" + todayDate,
                    "chts": "111111,12"
           }
                   
          data_valid = 1
      
      elif (chart == 2 ):
        # day chart (chart 24 hours of 60 minutes in each our)
        # query database for an existing read based on (owner + meter + uom + timestamp)
        dtShort = timestamp[:10]
        dt = datetime.datetime.strptime(dtShort,"%Y-%m-%d")
        todayDate = dt.strftime("%Y-%m-%d")
        startDate = todayDate + " 00:00:00"
        endDate = todayDate + " 23:00:00"
        
        logging.debug("******Day Chart*******")
        logging.debug(startDate)
        logging.debug(endDate)
         
        uom = "W"
        q = db.GqlQuery("SELECT * FROM ReadingForHourByMinute WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp >= :4 AND timestamp <= :5", user, meter, uom, startDate, endDate )
        db_rows = q.fetch(24)
     
        if db_rows:
        
          workProps = self.getDataValues60(db_rows)
          
          #line chart sample
          # http://chart.apis.google.com/chart?chs=320x280&cht=lc&chd=t:40,60,-1,-1,47,75,0,60,52,45,42,20,7,30,32,33,35,77
          #    &chco=0000FF&chxt=x,x,y,y&chxl=0:|12am|6am|12pm|6pm|12am|1:|+|3:|+|+W&chxr=2,0,80
          #    &chds=0,80&chg=25,12.5&chls=1,4,2&chtt=Power+for+day+by+minute|March+3&chts=111111,12

          maxTop = int(round(workProps.max,-3))  #round up to nearest 100
          step = maxTop / 10
          chxr = "2" + "," + "0" + "," + str(maxTop) + "," + str(step)
          chds = "0" + "," + str(maxTop)
          chg = "25," + str(10) + ",1,4"
          if( int(size) == 0):
            chs = "420x380"
          elif( int(size) == 1):
            chs = "750x380"
          elif( int(size) == 2):
            chs = "280x300"
          elif( int(size) == 3):
            chs = "750x380"            
            
          logging.debug(maxTop)
          logging.debug("******Day Chart*******")
        
          chart_props = {
                    "chs": chs,
                    "cht": "lc",                    
                    "chd": workProps.formattedDatapoints,
                    "chco": "0000FF",
                    "chxt": "x,x,y,y",
                    "chxl": "0:|12am|6am|12pm|6pm|12am|1:| |3:| | W",                                    
                    "chxr": chxr,
                    "chds": chds,
                    "chg": chg,                      
                    "chls": "1,4,0",
                    "chtt": "Power for Day per minute|" + todayDate,
                    "chts": "111111,12"
           }
                   
          data_valid = 1
  
      elif (chart == 3 ):
        # week chart (chart 7 days of 15-minute reads; 7 records x 96 columns per records)
        # query database for an existing read based on (owner + meter + uom + timestamp)
        dt = datetime.datetime.strptime(timestamp,"%Y-%m-%d")
        offset = self.getDayOfWeekOffsets(dt.isoweekday())
        delta1 = datetime.timedelta(days=offset.startDay)
        delta2 = datetime.timedelta(days=offset.endDay)
        
        tempStartDate = dt + delta1
        tempEndDate = dt + delta2
        startDate = tempStartDate.strftime("%Y-%m-%d")     
        endDate = tempEndDate.strftime("%Y-%m-%d")        
        
        logging.debug("******Week Chart*******")
        logging.debug(startDate)
        logging.debug(endDate)
        
        uom = "W"
        q = db.GqlQuery("SELECT * FROM ReadingForDayBy15Minute WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp >= :4 AND timestamp <= :5", user, meter, uom, startDate, endDate )
        db_rows = q.fetch(7)
                 
        if db_rows:
        
          workProps = self.getDataValues96(db_rows)
          
          #line chart sample
          # http://chart.apis.google.com/chart?chs=320x280&cht=lc&chd=t:40,60,-1,-1,47,75,0,60,52,45,42,20,7,30,32,33,35,77
          # &chco=0000FF&chxt=x,x,y,y&chxl=0:|12am|6am|12pm|6pm|12am|1:|+|3:|+|+W&chxr=2,0,80&chds=0,80
          # &chg=25,12.5&chls=1,4,2&chtt=Power+for+day+by+minute|March+3&chts=111111,12

          maxTop = int(round(workProps.max,-3))  #round up to nearest 100
          step = maxTop / 10
          chxr = "2" + "," + "0" + "," + str(maxTop) + "," + str(step)
          chds = "0" + "," + str(maxTop)
          chg = "14.2," + str(10) + ",1,4"
          if( int(size) == 0):
            chs = "420x380"
          elif( int(size) == 1):
            chs = "750x380"
          elif( int(size) == 2):
            chs = "280x300"
          elif( int(size) == 3):
            chs = "750x380"            
            
          logging.debug(maxTop)
          logging.debug("******Week Chart*******")
        
          chart_props = {
                    "chs": chs,
                    "cht": "lc",                    
                    "chd": workProps.formattedDatapoints,
                    "chco": "0000FF",
                    "chxt": "x,x,y,y",
                    "chxl": "0:| |Sun| |Mon| |Tue| |Wed| |Thur| |Fri| |Sat| |1:| |3:| | W",                                    
                    "chxr": chxr,
                    "chds": chds,
                    "chg": chg,                      
                    "chls": "1,4,0",
                    "chtt": "Power for Week per 15-minute|" + startDate + " to " + endDate,
                    "chts": "111111,12"
           }
                   
          data_valid = 1
      
      elif (chart == 4 ):     
        # month chart (chart per hour consumption for all days in the month)
        dt = datetime.datetime.strptime(timestamp,"%Y-%m-%d")
        year = dt.strftime("%Y")
        month = dt.strftime("%m")
        monthDate = dt.strftime("%Y-%m")
        daysInMonth = calendar.monthrange(int(year), int(month))[1]
        
        startDate = year + "-" + month + "-" + "01"
        endDate = year + "-" + month + "-" + str(daysInMonth) 
        
        logging.debug("******Month Chart*******")
        logging.debug(startDate)
        logging.debug(endDate)
        
        uom = "Wh"
        q = db.GqlQuery("SELECT * FROM ReadingForDayByHour WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp >= :4 AND timestamp <= :5", user, meter, uom, startDate, endDate )
        db_rows = q.fetch(int(daysInMonth))

        if db_rows:
 
          workProps = self.getDataValues24(db_rows, int(daysInMonth))

          #bar chart sample
          # http://chart.apis.google.com/chart?chs=320x280&cht=bvs&chbh=a,2
          # &chd=t:5,7,20,22,23,26,30,2,9,22,40,42,55,60,-1,-1,47,75,0,60,52,45,42,20,7,30,32,33,35,77
          # &chco=00CCFF&chxt=x,x,y,y&chxl=0:|1|+|+|+|5|+|+|+|+|10|+|+|+|+|15|+|+|+|+|20|+|+|+|+|25|+|+|+|+|30|1:|+|3:|+|kWh
          # &chxr=2,0,80&chds=0,80&chg=25,12.5&chtt=Consumption+for+month+by+day|April+2010&chts=111111,12
              
          maxTop = workProps.max + 2   #round up to nearest 100
          step = maxTop / 10
          chxr = "2" + "," + "0" + "," + str(maxTop) + "," + str(step)
          chds = "0" + "," + str(maxTop)
          chg = "100," + str(10) + ",1,4"
          chxl = self.createMonthChartXAxisLabels(daysInMonth)
          if( int(size) == 0):
            chs = "420x380"
          elif( int(size) == 1):
            chs = "750x380"
          elif( int(size) == 2):
            chs = "280x300"
          elif( int(size) == 3):
            chs = "750x380"            
            
          logging.debug(maxTop)
          logging.debug("******Month Chart*******")              

          chart_props = {
                    "chs": chs,
                    "cht": "bvs",
                    "chbh": "a,2",
                    "chd": workProps.formattedDatapoints,
                    "chco": "AACC77",
                    "chxt": "x,x,y,y",
                    "chxl": chxl,                                    
                    "chxr": chxr,
                    "chds": chds,
                    "chg": chg,                      
                    "chtt": "Consumption for Month per day|" + monthDate,
                    "chts": "111111,12"
           }
          
          data_valid = 1
          
      
      if (data_valid == 1):
        form_data = urllib.urlencode(chart_props)
    
        url = 'http://chart.apis.google.com/chart'
        
        result = urlfetch.fetch(url=url,
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
 
        if (result and result.content):
          self.response.headers['Content-Type'] = 'image/png'      
          self.response.out.write(result.content)
        else:
          self.redirect('/images/noimage.jpg')
      
      else:
        self.redirect('/images/noimage.jpg')


  def getDayOfWeekOffsets(self, isoDay):
        offset = models.DayOfWeekOffsets()
        
        if isoDay == 7:   # isodayofweek is Sunday when 7
          offset.startDay = 0
          offset.endDay = 6
        elif isoDay == 1: # monday
          offset.startDay = -1
          offset.endDay = 5        
        elif isoDay == 2: # tuesday
          offset.startDay = -2
          offset.endDay = 4
        elif isoDay == 3: # wednesday
          offset.startDay = -3
          offset.endDay = 3
        elif isoDay == 4: # thursday
          offset.startDay = -4
          offset.endDay = 2
        elif isoDay == 5: # friday
          offset.startDay = -5
          offset.endDay = 1
        elif isoDay == 6: # saturday
          offset.startDay = -6
          offset.endDay = 0             
        
        return offset
      
  def getDayOfWeekReIndex(self, isoDay):
        
        if isoDay == 7:   # isodayofweek is Sunday when 7
          ret = 0
        elif isoDay == 1: # monday
          ret = 1       
        elif isoDay == 2: # tuesday
          ret = 2
        elif isoDay == 3: # wednesday
          ret = 3
        elif isoDay == 4: # thursday
          ret = 4
        elif isoDay == 5: # friday
          ret = 5
        elif isoDay == 6: # saturday
          ret = 6            
        
        return ret      
      
  def createMonthChartXAxisLabels(self, daysInMonth):
    
    ret = "0:|1| | | |5| | | | |10| | | | |15| | | | |20| | | | |25| | "
    
    if( daysInMonth == 28 ):
      ret = ret + "|"
    elif (daysInMonth == 29):
      ret = ret + "| |"
    elif (daysInMonth == 30):
      ret = ret + "| | |"
    elif (daysInMonth == 31 ):
      ret = ret + "| | | |"     
    
    ret = ret + str(daysInMonth) + "|1:| |3:| |kWh"
    
    return ret
      
  
  def getDataValues60ForOnlyOneHour(self, db_rows):
    # based on getDataValues60
    x = [-1]*60
    
    for row in db_rows:
      dt = row.timestamp
      dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:00:00")
      
      i = 0
      
      x[i + 0] = row.i0
      x[i + 1] = row.i1
      x[i + 2] = row.i2
      x[i + 3] = row.i3
      x[i + 4] = row.i4
      x[i + 5] = row.i5
      x[i + 6] = row.i6
      x[i + 7] = row.i7
      x[i + 8] = row.i8
      x[i + 9] = row.i9
      x[i + 10] = row.i10
      x[i + 11] = row.i11
      x[i + 12] = row.i12
      x[i + 13] = row.i13
      x[i + 14] = row.i14
      x[i + 15] = row.i15
      x[i + 16] = row.i16
      x[i + 17] = row.i17
      x[i + 18] = row.i18
      x[i + 19] = row.i19
      x[i + 20] = row.i20
      x[i + 21] = row.i21
      x[i + 22] = row.i22
      x[i + 23] = row.i23
      x[i + 24] = row.i24
      x[i + 25] = row.i25
      x[i + 26] = row.i26
      x[i + 27] = row.i27
      x[i + 28] = row.i28
      x[i + 29] = row.i29
      x[i + 30] = row.i30
      x[i + 31] = row.i31
      x[i + 32] = row.i32
      x[i + 33] = row.i33
      x[i + 34] = row.i34
      x[i + 35] = row.i35
      x[i + 36] = row.i36
      x[i + 37] = row.i37
      x[i + 38] = row.i38
      x[i + 39] = row.i39
      x[i + 40] = row.i40
      x[i + 41] = row.i41
      x[i + 42] = row.i42
      x[i + 43] = row.i43
      x[i + 44] = row.i44
      x[i + 45] = row.i45
      x[i + 46] = row.i46
      x[i + 47] = row.i47
      x[i + 48] = row.i48
      x[i + 49] = row.i49
      x[i + 50] = row.i50
      x[i + 51] = row.i51
      x[i + 52] = row.i52
      x[i + 53] = row.i53
      x[i + 54] = row.i54
      x[i + 55] = row.i55
      x[i + 56] = row.i56
      x[i + 57] = row.i57
      x[i + 58] = row.i58
      x[i + 59] = row.i59
 
    maxVal = max(x)
    minVal = min(x)
    
    d = models.DataList()
    d.max = maxVal
    d.min = minVal
    d.data = x
    
    count = 0
    s = "t:"
    for i in d.data:
      s = s + str(i)
      if( count < 59 ):
        s = s + ","
        count = count + 1
      
    d.formattedDatapoints = s
    
    return d

  
  def getDataValues60(self, db_rows):
   
    x = [-1]*1440
    
    for row in db_rows:
      dt = row.timestamp
      dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:00:00")
      h = dt.strftime("%H")
      
      i = int(h)*60
      
      x[i + 0] = row.i0
      x[i + 1] = row.i1
      x[i + 2] = row.i2
      x[i + 3] = row.i3
      x[i + 4] = row.i4
      x[i + 5] = row.i5
      x[i + 6] = row.i6
      x[i + 7] = row.i7
      x[i + 8] = row.i8
      x[i + 9] = row.i9
      x[i + 10] = row.i10
      x[i + 11] = row.i11
      x[i + 12] = row.i12
      x[i + 13] = row.i13
      x[i + 14] = row.i14
      x[i + 15] = row.i15
      x[i + 16] = row.i16
      x[i + 17] = row.i17
      x[i + 18] = row.i18
      x[i + 19] = row.i19
      x[i + 20] = row.i20
      x[i + 21] = row.i21
      x[i + 22] = row.i22
      x[i + 23] = row.i23
      x[i + 24] = row.i24
      x[i + 25] = row.i25
      x[i + 26] = row.i26
      x[i + 27] = row.i27
      x[i + 28] = row.i28
      x[i + 29] = row.i29
      x[i + 30] = row.i30
      x[i + 31] = row.i31
      x[i + 32] = row.i32
      x[i + 33] = row.i33
      x[i + 34] = row.i34
      x[i + 35] = row.i35
      x[i + 36] = row.i36
      x[i + 37] = row.i37
      x[i + 38] = row.i38
      x[i + 39] = row.i39
      x[i + 40] = row.i40
      x[i + 41] = row.i41
      x[i + 42] = row.i42
      x[i + 43] = row.i43
      x[i + 44] = row.i44
      x[i + 45] = row.i45
      x[i + 46] = row.i46
      x[i + 47] = row.i47
      x[i + 48] = row.i48
      x[i + 49] = row.i49
      x[i + 50] = row.i50
      x[i + 51] = row.i51
      x[i + 52] = row.i52
      x[i + 53] = row.i53
      x[i + 54] = row.i54
      x[i + 55] = row.i55
      x[i + 56] = row.i56
      x[i + 57] = row.i57
      x[i + 58] = row.i58
      x[i + 59] = row.i59
 
    maxVal = max(x)
    minVal = min(x)
    
    d = models.DataList()
    d.max = maxVal
    d.min = minVal
    d.data = x
    
    count = 0
    s = "t:"
    for i in d.data:
      s = s + str(i)
      if( count < 1439 ):
        s = s + ","
        count = count + 1
      
    d.formattedDatapoints = s
    
    return d
  
  
  def getDataValues96(self, db_rows):
     
    x = [-1]*672    # 96 * 7days
    
    for row in db_rows:
      dt = row.timestamp
      dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
      day = self.getDayOfWeekReIndex(dt.isoweekday())
      
      i = int(day)*96
      
      x[i + 0] = row.i0
      x[i + 1] = row.i1
      x[i + 2] = row.i2
      x[i + 2] = row.i3
      x[i + 4] = row.i4
      x[i + 5] = row.i5
      x[i + 6] = row.i6
      x[i + 7] = row.i7
      x[i + 8] = row.i8
      x[i + 9] = row.i9
      x[i + 10] = row.i10
      x[i + 11] = row.i11
      x[i + 12] = row.i12
      x[i + 13] = row.i13
      x[i + 14] = row.i14
      x[i + 15] = row.i15
      x[i + 16] = row.i16
      x[i + 17] = row.i17
      x[i + 18] = row.i18
      x[i + 19] = row.i19
      x[i + 20] = row.i20
      x[i + 21] = row.i21
      x[i + 22] = row.i22
      x[i + 23] = row.i23
      x[i + 24] = row.i24
      x[i + 25] = row.i25
      x[i + 26] = row.i26
      x[i + 27] = row.i27
      x[i + 28] = row.i28
      x[i + 29] = row.i29
      x[i + 30] = row.i30
      x[i + 31] = row.i31
      x[i + 32] = row.i32
      x[i + 33] = row.i33
      x[i + 34] = row.i34
      x[i + 35] = row.i35
      x[i + 36] = row.i36
      x[i + 37] = row.i37
      x[i + 38] = row.i38
      x[i + 39] = row.i39
      x[i + 40] = row.i40
      x[i + 41] = row.i41
      x[i + 42] = row.i42
      x[i + 43] = row.i43
      x[i + 44] = row.i44
      x[i + 45] = row.i45
      x[i + 46] = row.i46
      x[i + 47] = row.i47
      x[i + 48] = row.i48
      x[i + 49] = row.i49
      x[i + 50] = row.i50
      x[i + 51] = row.i51
      x[i + 52] = row.i52
      x[i + 53] = row.i53
      x[i + 54] = row.i54
      x[i + 55] = row.i55
      x[i + 56] = row.i56
      x[i + 57] = row.i57
      x[i + 58] = row.i58
      x[i + 59] = row.i59
      x[i + 60] = row.i60
      x[i + 61] = row.i61
      x[i + 62] = row.i62
      x[i + 63] = row.i63
      x[i + 64] = row.i64
      x[i + 65] = row.i65
      x[i + 66] = row.i66
      x[i + 67] = row.i67
      x[i + 68] = row.i68
      x[i + 69] = row.i69
      x[i + 70] = row.i70
      x[i + 71] = row.i71
      x[i + 72] = row.i72
      x[i + 73] = row.i73
      x[i + 74] = row.i74
      x[i + 75] = row.i75
      x[i + 76] = row.i76
      x[i + 77] = row.i77
      x[i + 78] = row.i78
      x[i + 79] = row.i79
      x[i + 80] = row.i80
      x[i + 81] = row.i81
      x[i + 82] = row.i82
      x[i + 83] = row.i83
      x[i + 84] = row.i84
      x[i + 85] = row.i85
      x[i + 86] = row.i86
      x[i + 87] = row.i87
      x[i + 88] = row.i88
      x[i + 89] = row.i89
      x[i + 90] = row.i90
      x[i + 91] = row.i91
      x[i + 92] = row.i92
      x[i + 93] = row.i93
      x[i + 94] = row.i94
      x[i + 95] = row.i95
      
    maxVal = max(x)
    minVal = min(x)
    
    d = models.DataList()
    d.max = maxVal
    d.min = minVal
    d.data = x
    
    count = 0
    s = "t:"
    for i in d.data:
      s = s + str(i)
      if( count < 671 ):
        s = s + ","
        count = count + 1
      
    d.formattedDatapoints = s
    
    return d
    

  def getDataValues24(self, db_rows, daysInMonth):
            
    x = [-1]*daysInMonth
    
    for row in db_rows:
      dt = row.timestamp
      dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
      day = dt.strftime("%d")

      i = (int(day) - 1)
      
      sum = 0
      if( row.i0 != -1 ):
        sum = sum + row.i0
      if( row.i1 != -1 ):        
        sum = sum + row.i1
      if( row.i2 != -1 ):        
        sum = sum + row.i2
      if( row.i3 != -1 ):         
        sum = sum + row.i3
      if( row.i4 != -1 ):       
        sum = sum + row.i4
      if( row.i5 != -1 ):       
        sum = sum + row.i5
      if( row.i6 != -1 ):       
        sum = sum + row.i6
      if( row.i7 != -1 ):       
        sum = sum + row.i7
      if( row.i8 != -1 ):       
        sum = sum + row.i8
      if( row.i9 != -1 ):       
        sum = sum + row.i9
      if( row.i10 != -1 ):       
        sum = sum + row.i10
      if( row.i11 != -1 ):       
        sum = sum + row.i11
      if( row.i12 != -1 ):       
        sum = sum + row.i12
      if( row.i13 != -1 ):       
        sum = sum + row.i13
      if( row.i14 != -1 ):       
        sum = sum + row.i14
      if( row.i15 != -1 ):       
        sum = sum + row.i15
      if( row.i16 != -1 ):       
        sum = sum + row.i16
      if( row.i17 != -1 ):       
        sum = sum + row.i17
      if( row.i18 != -1 ):
        sum = sum + row.i18
      if( row.i19 != -1 ):       
        sum = sum + row.i19
      if( row.i20 != -1 ):       
        sum = sum + row.i20
      if( row.i21 != -1 ):     
        sum = sum + row.i21
      if( row.i22 != -1 ):       
        sum = sum + row.i22
      if( row.i23 != -1 ):       
        sum = sum + row.i23        
 
      x[i] = float(sum / 1000)
      
    maxVal = max(x)
    minVal = min(x)
    
    d = models.DataList()
    d.max = maxVal
    d.min = minVal
    d.data = x
    
    totalCount = daysInMonth
    count = 0
    s = "t:"
    for i in d.data:
      s = s + str(i)
      if( count < (totalCount - 1) ):
        s = s + ","
        count = count + 1
      
    d.formattedDatapoints = s
    
    return d



application = webapp.WSGIApplication([
  (r'/chartsvc/(.*)/(.*)/(.*)/(.*)/(.*)', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()