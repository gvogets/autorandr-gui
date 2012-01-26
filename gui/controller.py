#!/usr/bin/env python

import autorandr
import gui
import wx
import logging
from optparse import OptionParser # depreciated in python 2.7+

def main():
  """ Initializes the application """
  opts = OptionParser()
  opts.add_option("-k", "--hotkey", dest="hotkey", action="store_true", \
      help="Apply the most fitting profile and ask.")
  opts.add_option("-b", "--boot", dest="boot", action="store_true", \
      help="Apply the default profile or the most fitting.")
  opts.add_option("-d", "--debug", dest="debug", action="store_true", \
      help="Enable debug output.")
  (options, args) = opts.parse_args()
  if options.debug == True:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.INFO)
  app = wx.App(False)
  controller = Controller()
  if options.hotkey == True:
    print "Not supported."
    app.Destroy()
  elif options.boot == True:
    print "Not supported."
    app.Destroy()
  else:
    controller.ListProfilesGUI()
  app.MainLoop()


class Controller:
  """ Provides the glue between autorandr and the gui """

  def __init__(self):
    self.autorandr = autorandr.AutoRandR()
    self.gui = gui.ArFrame(self, None, wx.ID_ANY)
    self.profileinfo = {}

  def SetProfile(self, name):
    self.autorandr.setprofile(name)
    self.__StatusChanged(self.autorandr.getactiveprofile())
    self.autorandr.setactiveprofile(name)
    self.__StatusChanged(name)
    self.ListProfilesGUI()

  def GetProfiles(self):
    return self.autorandr.getprofiles()

  def SetStandard(self, name):
    self.autorandr.setdefaultprofile(name)
    self.__StatusChanged(name)
    self.ListProfilesGUI()

  def Delete(self, name):
    self.autorandr.deleteprofile(name)
    self.__StatusChanged(name)
    self.ListProfilesGUI()
  
  def Add(self, name, comment):
    self.autorandr.saveprofile(name, comment)
    self.__StatusChanged(name)
    self.ListProfilesGUI()

  def GetBackend(self):
    return self.autorandr.autox()

  def __GetProfileInfo(self, name):
    try:
      self.profileinfo[name]
    except KeyError as e:
      self.profileinfo[name] = self.autorandr.getprofileinfo(name)
    return self.profileinfo[name]

  def __GetProfiles(self):
    if not hasattr(self, 'profiles'):
      self.profiles = self.autorandr.getprofiles()
    return self.profiles

  def __StatusChanged(self, name):
    try:
      del self.profileinfo[name]
    except KeyError as e:
      pass
    try:
      del self.profiles
    except AttributeError as e:
      pass

  def ListProfilesGUI(self):
    self.__GetProfiles() 
    for i in self.gui.vertbox.GetChildren():
      i.DeleteWindows()
      del i
    for i in self.profiles:
      info = self.__GetProfileInfo(i)
      status = []
      if info['isdefault']:
        status = ['standard']
      if info['isdetected']:
        status = status + ['detected']
      if info['isactive']:
        status = status + ['active']
      # dimensions 
      try:
        dimensions = []
        for i in info['config']:
          dimensions = dimensions + ["{0}:".format(i)] + \
              info['config'][i]
      except KeyError as e:
        dimensions = None
      try:
        self.gui.AddEntry(name=info['name'], comment=info['comment'], \
            status=status, dimensions=dimensions)
      except KeyError as e:
        self.gui.AddEntry(name=info['name'], status=status, \
            dimensions=dimensions)
    self.gui.drawme()


""" Load main() """
if __name__ == "__main__":
  main()
