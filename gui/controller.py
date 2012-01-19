#!/usr/bin/env python

import autorandr
import gui
import wx

def main():
  """ Initializes the application """
  app = wx.App(False)
  controller = Controller()
  controller.ListProfilesGUI()
  app.MainLoop()

class Controller:
  """ Provides the glue between autorandr and the gui """

  def __init__(self):
    self.autorandr = autorandr.AutoRandR()
    self.gui = gui.ArFrame(self, None, wx.ID_ANY)

  def SetProfile(self, name):
    self.autorandr.setprofile(name)

  def GetProfiles(self):
    return self.autorandr.getprofiles()

  def SetStandard(self, name):
    self.autorandr.setdefaultprofile(name)
    self.ListProfilesGUI()

  def Delete(self, name):
    print "I would delete {0}".format(name)

  def ListProfilesGUI(self):
    profiles = self.autorandr.getprofiles()
    for i in self.gui.vertbox.GetChildren():
      i.DeleteWindows()
      del i
    for i in profiles:
      info = self.autorandr.getprofileinfo(i)
      status = []
      if info['name'] == self.autorandr.getdefaultprofile():
        status = ['standard']
      if info['name'] in self.autorandr.getdetectedprofile():
        status = status + ['detected']
      try:
        self.gui.AddEntry(name=info['name'], comment=info['comment'], \
            status=status)
      except KeyError as e:
        self.gui.AddEntry(name=info['name'], status=status)
    self.gui.drawme()


""" Load main() """
if __name__ == "__main__":
  main()
