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
    """ Loads the gui and the backend """
    self.autorandr = autorandr.AutoRandR()
    self.gui = gui.ArFrame(self, None, wx.ID_ANY)
    self.profileinfo = {}
    self.gpuhash = self.autorandr.getgpuhash()

  def SetProfile(self, name):
    """ Load a named profile """
    self.autorandr.setprofile(name)
    self.__StatusChanged(self.autorandr.getactiveprofile())
    self.autorandr.setactiveprofile(name)
    self.__StatusChanged(name)
    logging.debug(u"Loading profile {0}".format(name))
    self.ListProfilesGUI()

  def UnsetActiveProfile(self):
    """ Unmark a profile as active (currently loaded) """
    oldone = self.autorandr.getactiveprofile()
    self.autorandr.setactiveprofile('')
    logging.debug(u"Profile {0} is no longer active.".format(oldone))
    self.__StatusChanged(oldone)
    self.ListProfilesGUI()

  def SetStandard(self, name):
    """ Make a profile standard at boottime """
    oldstandard = self.autorandr.getdefaultprofile()
    self.autorandr.setdefaultprofile(name)
    logging.debug(u"Setting standard profile to {0}".format(name))
    self.__StatusChanged(name)
    self.__StatusChanged(oldstandard)
    self.ListProfilesGUI()

  def Delete(self, name):
    """ Delete a profile """
    self.autorandr.deleteprofile(name)
    logging.debug(u"Profile {0} has been deleted.".format(name))
    self.__StatusChanged(name)
    self.ListProfilesGUI()
  
  def Add(self, name, comment=None, force=False):
    """ Save a profile """
    self.autorandr.saveprofile(name, comment, force)
    logging.debug(u"Profile {0} has been saved".format(name))
    self.__StatusChanged(name)
    self.ListProfilesGUI()

  def GetBackend(self):
    """ Find out whether we use disper or xrandr. """
    return self.autorandr.autox()

  def __GetProfileInfo(self, name, detectedprofiles=None):
    """ Gather information for a named profile """
    try:
      self.profileinfo[name]
      logging.debug(u"Gathering profile information on {0}".format(name))
    except KeyError as e:
      self.profileinfo[name] = \
          self.autorandr.getprofileinfo(name, detectedprofiles)
      logging.debug(u"Information from profile {0} was not cached.".format(name))
    return self.profileinfo[name]

  def GetProfiles(self, showhidden=True):
    """ Get all profile names. """
    return self.__GetProfiles(showhidden)

  def __GetProfiles(self, showhidden=True):
    """ Return the names of all profiles, cached or get them. """
    logging.debug(u"Gathering list of profiles")
    if not hasattr(self, 'profiles'):
      self.profiles = self.autorandr.getprofiles(showhidden)
      logging.debug(u"List of profiles was not cached.")
    return self.profiles

  def __GetDetectedProfiles(self):
    """ Return the detected profiles, cached or get them. """
    logging.debug(u"Retrieving detected profiles")
    if not hasattr(self,'detectedprofiles'):
      logging.debug(u"Detected profiles were not in the cache.")
      self.detectedprofiles = self.autorandr.getdetectedprofile()
    return self.detectedprofiles

  def __StatusChanged(self, name):
    """ Remove cached profile information. """
    logging.debug(u"Clean cached attributes")
    try:
      del self.profileinfo[name]
    except KeyError as e:
      pass
    try:
      del self.profiles
    except AttributeError as e:
      pass
    try:
      del self.detectedprofiles
    except AttributeError as e:
      pass

  def HandleHotkey(self):
    """ Handles the invocation via hotkey. """
    logging.debug(u"Handle invocation via hotkey")
    # Save current settings
    self.autorandr.saveprofile(".hotkey", None, True)
    candidate = self.autorandr.getdefaultprofile()
    if candidate in self.__GetDetectedProfiles():
      # Load default profile, if it is detected
      self.autorandr.setprofile(candidate)
      self.autorandr.setactiveprofile(candidate)
    elif self.__GetDetectedProfiles():
      # Load the first detected profile
      self.autorandr.setprofile( \
          self.__GetDetectedProfiles()[0])
      self.autorandr.setactiveprofile( \
          self.__GetDetectedProfiles()[0])
    else:
      # Fallback
      self.autorandr.fallback()
      self.autorandr.setactiveprofile(None)
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
    logging.debug(u"Handle invocation during boot")
    self.autorandr.saveprofile(".boot", None, True)
    candidate = self.autorandr.getdefaultprofile()
    if candidate in self.__GetDetectedProfiles():
      # Load default profile, if it is detected
      self.autorandr.setprofile(candidate)
      self.autorandr.setactiveprofile(candidate)
    elif self.__GetDetectedProfiles():
      # Load the first detected profile
      self.autorandr.setprofile( \
          self.__GetDetectedProfiles()[0])
      self.autorandr.setactiveprofile( \
          self.__GetDetectedProfiles()[0])


  def ListProfilesGUI(self):
    """ Redraw the list of profiles """
    logging.debug(u"Redraw the list of profiles in the GUI")
    # FIXME This code should probably be in gui.py
    self.__GetProfiles(False) 
    for i in self.gui.vertbox.GetChildren():
      i.DeleteWindows()
      del i
    if len(self.profiles) == 0:
      self.gui.AddEmptyEntry()
    for i in self.profiles:
      info = self.__GetProfileInfo(i, self.__GetDetectedProfiles())
      status = []
      if info['isdefault']:
        status = ['standard']
      if info['gpuhash'] == self.gpuhash or info['gpuhash'] == None:
        if info['isdetected']:
          status = status + ['detected']
        if info['isactive']:
          status = status + ['active']
        enable = True
      else:
        enable = False
      if info['comment'] == None:
        comment = 'Kein Kommentar'
      else:
        comment = info['comment']
      # dimensions 
      try:
        dimensions = []
        for i in info['config']:
          dimensions = dimensions + ["{0}:".format(i)] + \
              info['config'][i]
      except KeyError as e:
        dimensions = None
      self.gui.AddEntry(name=info['name'], comment=comment, \
          status=status, dimensions=dimensions, enable=enable)
    self.gui.drawme()


""" Load main() """
if __name__ == "__main__":
  main()
