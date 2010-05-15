#!/usr/bin/env python
#
# Copyright 2010 myenergyuse
# http://code.google.com/p/myenergyuse/
# watchmyted - at- gmail.com
#
#{
#  "ReadData": {
#    "Blob": "0=1105",
#    "Fuel": "Electric",
#    "MeterID": 0,
#    "Name": "some name test",
#    "Stamp": "2010-02-24",
#    "Store": "ReadingForDayByHour",
#    "Uom": "Wh"
#  }
#}
#
#{
#  "ReadData": {
#    "Blob": "81=770",
#    "Fuel": "Electric",
#    "MeterID": 0,
#    "Name": "some name test",
#    "Stamp": "2010-02-24",
#    "Store": "ReadingForDayBy15Minute",
#    "Uom": "W"
#  }
#}
#
#{
#  "ReadData": {
#    "Blob": "81=770,82=787,[...]",
#    "Fuel": "Electric",
#    "MeterID": 0,
#    "Name": "some name test",
#    "Stamp": "2010-02-24 15:00:00",
#    "Store": "ReadingForHourByMinute",
#    "Uom": "W"
#  }
#}
#
""" Readings Service """

import logging 

import cgi
import datetime
import wsgiref.handlers

from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import models
import bblib

class MainPage(webapp.RequestHandler):
  def get(self):
    self.renderPage(0)
  
  def post(self):
    self.renderPage(0)
    
  def renderPage(self, arg0):
    logging.debug('Handling incoming json data in readingssvc') 

    request_data = simplejson.loads(self.request.body)
    
    try:
      # grab items from json
      req_meterid = request_data['ReadData']['MeterID']
      req_name = request_data['ReadData']['Name']
      req_stamp = request_data['ReadData']['Stamp']
      req_store = request_data['ReadData']['Store']
      req_uom = request_data['ReadData']['Uom']
      req_fuel = request_data['ReadData']['Fuel']      
      req_blob = request_data['ReadData']['Blob']
      
      logging.debug(req_meterid)
      logging.debug(req_name)
      logging.debug(req_stamp)
      logging.debug(req_store)
      logging.debug(req_uom)
      logging.debug(req_fuel)     # not used yet, but fuel will be useful in future when gas and water data also sent
      logging.debug(req_blob)
      
      user = users.get_current_user()
      logging.debug('user retrieved')
      
      if user:
        # first store meterid if not already stored; update name if already stored
        q = db.GqlQuery("SELECT * FROM Meter WHERE owner = :1 AND meterID = :2", user, req_meterid)
        db_meter_read = q.get()
        
        if db_meter_read:
          db_meter_read.name = req_name
          
          if (req_store == 'ReadingForDayByHour'):
            db_meter_read.ReadingForDayByHour_timestamp = req_stamp
          elif (req_store == 'ReadingForDayBy15Minute'):
            db_meter_read.ReadingForDayBy15Minute_timestamp = req_stamp
          elif (req_store == 'ReadingForHourByMinute'):
            db_meter_read.ReadingForHourByMinute_timestamp = req_stamp
          elif (req_store == 'ReadingFor15MinuteBySecond'):
            db_meter_read.Reading15MinuteBySecond_timestamp = req_stamp
          
          db.put(db_meter_read)
          logging.debug('update meter')
          
        else:
          newMeter = models.Meter()
          newMeter.owner = user
          newMeter.meterID = req_meterid
          newMeter.name = req_name
          
          if (req_store == 'ReadingForDayByHour'):
            newMeter.ReadingForDayByHour_timestamp = req_stamp
          elif (req_store == 'ReadingForDayBy15Minute'):
            newMeter.ReadingForDayBy15Minute_timestamp = req_stamp
          elif (req_store == 'ReadingForHourByMinute'):
            newMeter.ReadingForHourByMinute_timestamp = req_stamp
          elif (req_store == 'ReadingFor15MinuteBySecond'):
            newMeter.Reading15MinuteBySecond_timestamp = req_stamp
            
          db.put(newMeter)
          logging.debug('insert meter')              
          
      # handle incoming data based upon the "store" value
      if (req_store == 'ReadingForDayByHour'):
        logging.debug('** Processing ReadingForDayByHour **')
        
        if user:
          # query database for an existing read based on (owner + meter + uom + timestamp)
          # timestamp is for the day
          q = db.GqlQuery("SELECT * FROM ReadingForDayByHour WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp = :4", user, req_meterid, req_uom, req_stamp)
          db_read = q.get()
          
          if db_read:
            # the read already exists
            logging.debug('found existing read - update')
            
            mod_read = self.assignIntervalForStorage24(req_blob, db_read)
            
            db.put(mod_read)
            logging.debug('read updated')
            
          else:
            # the read is new to insert
            logging.debug('read not found - insert')
            
            newRead = models.ReadingForDayByHour()
            newRead.owner = user
            newRead.meterID = req_meterid
            newRead.uom = req_uom
            newRead.timestamp = req_stamp
            
            mod_read = self.assignIntervalForStorage24(req_blob, newRead)
            
            db.put(mod_read)
            logging.debug('read inserted')            
            
        
      elif (req_store == 'ReadingForDayBy15Minute'):
        logging.debug('** ReadingForDayBy15Minute')

        if user:
          # query database for an existing read based on (owner + meter + uom + timestamp)
          # timestamp is for the day 
          q = db.GqlQuery("SELECT * FROM ReadingForDayBy15Minute WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp = :4", user, req_meterid, req_uom, req_stamp)
          db_read = q.get()
          
          if db_read:
            # the read already exists
            logging.debug('found existing read - update')
            
            mod_read = self.assignIntervalForStorage96(req_blob, db_read)
            
            db.put(mod_read)
            logging.debug('read updated')
            
          else:
            # the read is new to insert
            logging.debug('read not found - insert')
            
            newRead = models.ReadingForDayBy15Minute()
            newRead.owner = user
            newRead.meterID = req_meterid
            newRead.uom = req_uom
            newRead.timestamp = req_stamp
            
            mod_read = self.assignIntervalForStorage96(req_blob, newRead)
            
            db.put(mod_read)
            logging.debug('read inserted')            
             

      elif (req_store == 'ReadingForHourByMinute'):
        logging.debug('** ReadingForHourByMinute')
        
        if user:
          # query database for an existing read based on (owner + meter + uom + timestamp)
          # timestamp is for the hour 
          q = db.GqlQuery("SELECT * FROM ReadingForHourByMinute WHERE owner = :1 AND meterID = :2 AND uom = :3 AND timestamp = :4", user, req_meterid, req_uom, req_stamp)
          db_read = q.get()
          
          if db_read:
            # the read already exists
            logging.debug('found existing read - update')
            
            mod_read = self.assignIntervalForStorage60(req_blob, db_read)
            
            db.put(mod_read)
            logging.debug('read updated')
            
          else:
            # the read is new to insert
            logging.debug('read not found - insert')
            
            newRead = models.ReadingForHourByMinute()
            newRead.owner = user
            newRead.meterID = req_meterid
            newRead.uom = req_uom
            newRead.timestamp = req_stamp
            
            mod_read = self.assignIntervalForStorage60(req_blob, newRead)
            
            db.put(mod_read)
            logging.debug('read inserted')            
          
          
      elif (req_store == 'ReadingFor15MinuteBySecond'):
        logging.debug('** ReadingFor15MinuteBySecond')
        pass
      
      else:
        pass
      
      self.response.out.write("success")
      
    except:
      logging.error('Error parsing posted json reading data')
      
      self.response.out.write("error")
  
 
  def assignIntervalForStorage24(self, blob, read):
    # split the blob field at commas to create an iterable list
    logging.debug("assignIntervalForStorage24")
    
    intervals = blob.split(',')
    
    for item in intervals:
      pair = item.split('=')
      interval = pair[0]
      quantity = pair[1]
      
      if (int(interval)==0):
        read.i0 = int(quantity)
      elif (int(interval)==1):
        read.i1 = int(quantity)
      elif (int(interval)==2):
        read.i2 = int(quantity)
      elif (int(interval)==3):
        read.i3 = int(quantity)
      elif (int(interval)==4):
        read.i4 = int(quantity)
      elif (int(interval)==5):
        read.i5 = int(quantity)
      elif (int(interval)==6):
        read.i6 = int(quantity)
      elif (int(interval)==7):
        read.i7 = int(quantity)
      elif (int(interval)==8):
        read.i8 = int(quantity)
      elif (int(interval)==9):
        read.i9 = int(quantity)
      elif (int(interval)==10):
        read.i10 = int(quantity)
      elif (int(interval)==11):
        read.i11 = int(quantity)
      elif (int(interval)==12):
        read.i12 = int(quantity)
      elif (int(interval)==13):
        read.i13 = int(quantity)
      elif (int(interval)==14):
        read.i14 = int(quantity)
      elif (int(interval)==15):
        read.i15 = int(quantity)
      elif (int(interval)==16):
        read.i16 = int(quantity)
      elif (int(interval)==17):
        read.i17 = int(quantity)
      elif (int(interval)==18):
        read.i18 = int(quantity)
      elif (int(interval)==19):
        read.i19 = int(quantity)
      elif (int(interval)==20):
        read.i20 = int(quantity)
      elif (int(interval)==21):
        read.i21 = int(quantity)
      elif (int(interval)==22):
        read.i22 = int(quantity)
      elif (int(interval)==23):
        read.i23 = int(quantity)
    
    return read

  def assignIntervalForStorage60(self, blob, read):
    # split the blob field at commas to create an iterable list
    logging.debug("assignIntervalForStorage60")
    
    intervals = blob.split(',')
    
    for item in intervals:
      pair = item.split('=')
      interval = pair[0]
      quantity = pair[1]
      
      if (int(interval)==0):
        read.i0 = int(quantity)
      elif (int(interval)==1):
        read.i1 = int(quantity)
      elif (int(interval)==2):
        read.i2 = int(quantity)
      elif (int(interval)==3):
        read.i3 = int(quantity)
      elif (int(interval)==4):
        read.i4 = int(quantity)
      elif (int(interval)==5):
        read.i5 = int(quantity)
      elif (int(interval)==6):
        read.i6 = int(quantity)
      elif (int(interval)==7):
        read.i7 = int(quantity)
      elif (int(interval)==8):
        read.i8 = int(quantity)
      elif (int(interval)==9):
        read.i9 = int(quantity)
      elif (int(interval)==10):
        read.i10 = int(quantity)
      elif (int(interval)==11):
        read.i11 = int(quantity)
      elif (int(interval)==12):
        read.i12 = int(quantity)
      elif (int(interval)==13):
        read.i13 = int(quantity)
      elif (int(interval)==14):
        read.i14 = int(quantity)
      elif (int(interval)==15):
        read.i15 = int(quantity)
      elif (int(interval)==16):
        read.i16 = int(quantity)
      elif (int(interval)==17):
        read.i17 = int(quantity)
      elif (int(interval)==18):
        read.i18 = int(quantity)
      elif (int(interval)==19):
        read.i19 = int(quantity)
      elif (int(interval)==20):
        read.i20 = int(quantity)
      elif (int(interval)==21):
        read.i21 = int(quantity)
      elif (int(interval)==22):
        read.i22 = int(quantity)
      elif (int(interval)==23):
        read.i23 = int(quantity)    
      elif (int(interval)==24):
        read.i24 = int(quantity)
      elif (int(interval)==25):
        read.i25 = int(quantity)
      elif (int(interval)==26):
        read.i26 = int(quantity)
      elif (int(interval)==27):
        read.i27 = int(quantity)
      elif (int(interval)==28):
        read.i28 = int(quantity)
      elif (int(interval)==29):
        read.i29 = int(quantity)
      elif (int(interval)==30):
        read.i30 = int(quantity)
      elif (int(interval)==31):
        read.i31 = int(quantity)
      elif (int(interval)==32):
        read.i32 = int(quantity)
      elif (int(interval)==33):
        read.i33 = int(quantity)
      elif (int(interval)==34):
        read.i34 = int(quantity)
      elif (int(interval)==35):
        read.i35 = int(quantity)
      elif (int(interval)==36):
        read.i36 = int(quantity)
      elif (int(interval)==37):
        read.i37 = int(quantity)
      elif (int(interval)==38):
        read.i38 = int(quantity)
      elif (int(interval)==39):
        read.i39 = int(quantity)
      elif (int(interval)==40):
        read.i40 = int(quantity)
      elif (int(interval)==41):
        read.i41 = int(quantity)
      elif (int(interval)==42):
        read.i42 = int(quantity)
      elif (int(interval)==43):
        read.i43 = int(quantity)
      elif (int(interval)==44):
        read.i44 = int(quantity)
      elif (int(interval)==45):
        read.i45 = int(quantity)
      elif (int(interval)==46):
        read.i46 = int(quantity)
      elif (int(interval)==47):
        read.i47 = int(quantity)
      elif (int(interval)==48):
        read.i48 = int(quantity)
      elif (int(interval)==49):
        read.i49 = int(quantity)
      elif (int(interval)==50):
        read.i50 = int(quantity)
      elif (int(interval)==51):
        read.i51 = int(quantity)
      elif (int(interval)==52):
        read.i52 = int(quantity)
      elif (int(interval)==53):
        read.i53 = int(quantity)
      elif (int(interval)==54):
        read.i54 = int(quantity)
      elif (int(interval)==55):
        read.i55 = int(quantity)
      elif (int(interval)==56):
        read.i56 = int(quantity)
      elif (int(interval)==57):
        read.i57 = int(quantity)
      elif (int(interval)==58):
        read.i58 = int(quantity)
      elif (int(interval)==59):
        read.i59 = int(quantity)
      
    return read


  def assignIntervalForStorage96(self, blob, read):
    # split the blob field at commas to create an iterable list
    logging.debug("assignIntervalForStorage96")
    
    intervals = blob.split(',')
    
    for item in intervals:
      pair = item.split('=')
      interval = pair[0]
      quantity = pair[1]
     
      if (int(interval)==0):
        read.i0 = int(quantity)
      elif (int(interval)==1):
        read.i1 = int(quantity)
      elif (int(interval)==2):
        read.i2 = int(quantity)
      elif (int(interval)==3):
        read.i3 = int(quantity)
      elif (int(interval)==4):
        read.i4 = int(quantity)
      elif (int(interval)==5):
        read.i5 = int(quantity)
      elif (int(interval)==6):
        read.i6 = int(quantity)
      elif (int(interval)==7):
        read.i7 = int(quantity)
      elif (int(interval)==8):
        read.i8 = int(quantity)
      elif (int(interval)==9):
        read.i9 = int(quantity)
      elif (int(interval)==10):
        read.i10 = int(quantity)
      elif (int(interval)==11):
        read.i11 = int(quantity)
      elif (int(interval)==12):
        read.i12 = int(quantity)
      elif (int(interval)==13):
        read.i13 = int(quantity)
      elif (int(interval)==14):
        read.i14 = int(quantity)
      elif (int(interval)==15):
        read.i15 = int(quantity)
      elif (int(interval)==16):
        read.i16 = int(quantity)
      elif (int(interval)==17):
        read.i17 = int(quantity)
      elif (int(interval)==18):
        read.i18 = int(quantity)
      elif (int(interval)==19):
        read.i19 = int(quantity)
      elif (int(interval)==20):
        read.i20 = int(quantity)
      elif (int(interval)==21):
        read.i21 = int(quantity)
      elif (int(interval)==22):
        read.i22 = int(quantity)
      elif (int(interval)==23):
        read.i23 = int(quantity)
      elif (int(interval)==24):
        read.i24 = int(quantity)
      elif (int(interval)==25):
        read.i25 = int(quantity)
      elif (int(interval)==26):
        read.i26 = int(quantity)
      elif (int(interval)==27):
        read.i27 = int(quantity)
      elif (int(interval)==28):
        read.i28 = int(quantity)
      elif (int(interval)==29):
        read.i29 = int(quantity)
      elif (int(interval)==30):
        read.i30 = int(quantity)
      elif (int(interval)==31):
        read.i31 = int(quantity)
      elif (int(interval)==32):
        read.i32 = int(quantity)
      elif (int(interval)==33):
        read.i33 = int(quantity)
      elif (int(interval)==34):
        read.i34 = int(quantity)
      elif (int(interval)==35):
        read.i35 = int(quantity)
      elif (int(interval)==36):
        read.i36 = int(quantity)
      elif (int(interval)==37):
        read.i37 = int(quantity)
      elif (int(interval)==38):
        read.i38 = int(quantity)
      elif (int(interval)==39):
        read.i39 = int(quantity)
      elif (int(interval)==40):
        read.i40 = int(quantity)
      elif (int(interval)==41):
        read.i41 = int(quantity)
      elif (int(interval)==42):
        read.i42 = int(quantity)
      elif (int(interval)==43):
        read.i43 = int(quantity)
      elif (int(interval)==44):
        read.i44 = int(quantity)
      elif (int(interval)==45):
        read.i45 = int(quantity)
      elif (int(interval)==46):
        read.i46 = int(quantity)
      elif (int(interval)==47):
        read.i47 = int(quantity)
      elif (int(interval)==48):
        read.i48 = int(quantity)
      elif (int(interval)==49):
        read.i49 = int(quantity)
      elif (int(interval)==50):
        read.i50 = int(quantity)
      elif (int(interval)==51):
        read.i51 = int(quantity)
      elif (int(interval)==52):
        read.i52 = int(quantity)
      elif (int(interval)==53):
        read.i53 = int(quantity)
      elif (int(interval)==54):
        read.i54 = int(quantity)
      elif (int(interval)==55):
        read.i55 = int(quantity)
      elif (int(interval)==56):
        read.i56 = int(quantity)
      elif (int(interval)==57):
        read.i57 = int(quantity)
      elif (int(interval)==58):
        read.i58 = int(quantity)
      elif (int(interval)==59):
        read.i59 = int(quantity)
      elif (int(interval)==60):
        read.i60 = int(quantity)
      elif (int(interval)==61):
        read.i61 = int(quantity)
      elif (int(interval)==62):
        read.i62 = int(quantity)
      elif (int(interval)==63):
        read.i63 = int(quantity)
      elif (int(interval)==64):
        read.i64 = int(quantity)
      elif (int(interval)==65):
        read.i65 = int(quantity)
      elif (int(interval)==66):
        read.i66 = int(quantity)
      elif (int(interval)==67):
        read.i67 = int(quantity)
      elif (int(interval)==68):
        read.i68 = int(quantity)
      elif (int(interval)==69):
        read.i69 = int(quantity)
      elif (int(interval)==70):
        read.i70 = int(quantity)
      elif (int(interval)==71):
        read.i71 = int(quantity)
      elif (int(interval)==72):
        read.i72 = int(quantity)
      elif (int(interval)==73):
        read.i73 = int(quantity)
      elif (int(interval)==74):
        read.i74 = int(quantity)
      elif (int(interval)==75):
        read.i75 = int(quantity)
      elif (int(interval)==76):
        read.i76 = int(quantity)
      elif (int(interval)==77):
        read.i77 = int(quantity)
      elif (int(interval)==78):
        read.i78 = int(quantity)
      elif (int(interval)==79):
        read.i79 = int(quantity)
      elif (int(interval)==80):
        read.i80 = int(quantity)
      elif (int(interval)==81):
        read.i81 = int(quantity)
      elif (int(interval)==82):
        read.i82 = int(quantity)
      elif (int(interval)==83):
        read.i83 = int(quantity)
      elif (int(interval)==84):
        read.i84 = int(quantity)
      elif (int(interval)==85):
        read.i85 = int(quantity)
      elif (int(interval)==86):
        read.i86 = int(quantity)
      elif (int(interval)==87):
        read.i87 = int(quantity)
      elif (int(interval)==88):
        read.i88 = int(quantity)
      elif (int(interval)==89):
        read.i89 = int(quantity)
      elif (int(interval)==90):
        read.i90 = int(quantity)
      elif (int(interval)==91):
        read.i91 = int(quantity)
      elif (int(interval)==92):
        read.i92 = int(quantity)
      elif (int(interval)==93):
        read.i93 = int(quantity)
      elif (int(interval)==94):
        read.i94 = int(quantity)
      elif (int(interval)==95):
        read.i95 = int(quantity)
      
    return read
  


application = webapp.WSGIApplication([
  ('/readingssvc', MainPage)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
