#!/usr/bin/python
# encoding=utf8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

#import pygtk
import datetime
import time
import itertools
from time import strftime, sleep, localtime
from string import lower
import os
import json
import signal

from urllib2 import Request, urlopen, URLError


from gi.repository import Gtk as gtk
from gi.repository import GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject as gobject
from gi.repository import Wnck as wnck

# How often to check for application change in ms
LOGGING_INTERVAL = 500

# The directory where sentried was cloned -- please add the training /
BASE_PATH = "/home/regac/code/"





project_setup = {}
start_time = end_time = last_logged = None

APPINDICATOR_ID = 'sentried'


def get_active_window():
 default = wnck.Screen.get_default()
 while gtk.events_pending():
  gtk.main_iteration()

 window_list = default.get_windows()
 # Docs: https://developer.gnome.org/libwnck/stable/WnckWindow.html
 for win in window_list:
  if win.is_active():
   window_name = win.get_name()
   app_name = win.get_application().get_name()
   # There's some funkiness with Chrome's application name being
   # frozen to as it is when the script is started.
   if " - Google Chrome" in app_name:
    app_name = "Google Chrome"

   # Remove the unsaved file indicator from VSCode
   app_name = app_name.replace("● ", "")

   project = ""
   for project_string in project_setup:
    if lower(project_string) in lower(window_name):
     project = project_setup[project_string]
     break


   t = [app_name, window_name, project]

   return t

 return ["", ""]

def log_file_name():
 return BASE_PATH + "sentried/data/sentried-" + strftime("%Y-%m-%d", localtime()) + ".csv"

def log():
  global last_logged
  global start_time
  global end_time

  active_window = get_active_window()
  if last_logged == None or last_logged != active_window:
    end_time = localtime()
    if last_logged != None:
      with open(log_file_name(), 'a+') as outfile:
        entry = [time.strftime('%Y-%m-%dT%H:%M:%SZ', start_time), time.strftime('%Y-%m-%dT%H:%M:%SZ', end_time)] + last_logged
        joined_entry = ','.join(list(map(lambda x: "\"" + str(x) + "\"", entry))) + "\n\r"
        outfile.write(joined_entry)
        outfile.close()

    last_logged = active_window
    start_time = end_time

  GLib.timeout_add(LOGGING_INTERVAL, log)


def main():
  indicator = appindicator.Indicator.new(APPINDICATOR_ID, BASE_PATH + "sentried/icon.svg", appindicator.IndicatorCategory.SYSTEM_SERVICES)
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  indicator.set_menu(build_menu())
  notify.init(APPINDICATOR_ID)
  log()
  gtk.main()
  #time.sleep(0.5)

def build_menu():
  menu = gtk.Menu()
  item_quit = gtk.MenuItem('Exit')
  item_quit.connect('activate', quit)
  menu.append(item_quit)
  menu.show_all()
  return menu

def quit(_):
  notify.uninit()
  gtk.main_quit()

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal.SIG_DFL)
  try:
    path = os.path.join(BASE_PATH + "sentried/project_setup.json")
    with open(path) as json_data_file:
      project_setup = json.load(json_data_file)
  except:
    print("No project_setup.json found")
  main()