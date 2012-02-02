#!/usr/bin/env python

import autorandr
import gui
import wx
import logging
from optparse import OptionParser # depreciated in python 2.7+

def main():
  """ Parses options and starts the application appropriately """
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
    controller.HandleHotkey()
    app.MainLoop()
    exit()
  elif options.boot == True:
    controller.HandleBoot()
    exit()
  else: # Start GUI
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

  def GetProfiles(self, showhidden=True):
    return self.autorandr.getprofiles(showhidden)

  def SetStandard(self, name):
    self.autorandr.setdefaultprofile(name)
    self.__StatusChanged(name)
    self.ListProfilesGUI()

  def Delete(self, name):
    self.autorandr.deleteprofile(name)
    self.__StatusChanged(name)
    self.ListProfilesGUI()
  
  def Add(self, name, comment=None, force=False):
    self.autorandr.saveprofile(name, comment, force)
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

  def __GetProfiles(self, showhidden=True):
    if not hasattr(self, 'profiles'):
      self.profiles = self.autorandr.getprofiles(showhidden)
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

  def HandleHotkey(self):
    """ Handles the invocation via hotkey. """
    # Save current settings
    self.autorandr.saveprofile(".hotkey", None, True)
    candidate = self.autorandr.getdefaultprofile()
    if candidate in self.autorandr.getdetectedprofile():
      # Load default profile, if it is detected
      self.autorandr.setprofile(candidate)
    elif self.autorandr.getdetectedprofile():
      # Load the first detected profile
      self.autorandr.setprofile( \
          self.autorandr.getdetectedprofile()[0])
    else:
      # Fallback
      self.autorandr.fallback()
    # TimeoutDialog
    dlg = gui.TimeoutDialog(None, 20)
    ret = dlg.ShowModal()
    if ret == wx.ID_NO:
      self.autorandr.setprofile(".hotkey")
    dlg.Destroy()
    # Display GUI
    self.ListProfilesGUI()

  def HandleBoot(self):
    """ Handles the invocation during boot """
    self.autorandr.saveprofile(".boot", None, True)
    candidate = self.autorandr.getdefaultprofile()
    if candidate in self.autorandr.getdetectedprofile():
      # Load default profile, if it is detected
      self.autorandr.setprofile(candidate)
    elif self.autorandr.getdetectedprofile():
      # Load the first detected profile
      self.autorandr.setprofile( \
          self.autorandr.getdetectedprofile()[0])


  def ListProfilesGUI(self):
    self.__GetProfiles(False) 
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
