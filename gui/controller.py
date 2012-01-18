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

  def Apply(self, name):
    self.autorandr.setprofile(name)

  def ListProfilesGUI(self):
    profiles = self.autorandr.getprofiles()
    for i in profiles:
      info = self.autorandr.getprofileinfo(i)
      try:
        self.gui.AddEntry(name=info['name'], comment=info['comment'])
      except KeyError as e:
        self.gui.AddEntry(name=info['name'])
    self.gui.drawme()


""" Load main() """
if __name__ == "__main__":
  main()
