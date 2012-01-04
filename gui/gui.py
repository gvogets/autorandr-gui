#!/usr/bin/env python

import wx
import autorandr

class ArFrame(wx.Frame):
  """ This is a custom frame """
  def __init__(self, *args, **kwargs):
    title = "Bildschirmprofilverwaltungswerkzeug" #DDSG-Kapitaen
    wx.Frame.__init__(self, *args, title=title, **kwargs)
    self.__toolbar()
    self.Show(True)

  def __toolbar(self):
    """ Build our toolbar """
    self.toolbar = self.CreateToolBar(style=wx.TB_HORZ_TEXT)
    saveTool = self.toolbar.AddLabelTool(wx.ID_SAVE, 'Speichern', \
      self.getbitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR))
    standardTool = self.toolbar.AddLabelTool(wx.ID_ANY, 'Standard festlegen', \
      self.getbitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR))
    quitTool = self.toolbar.AddLabelTool(wx.ID_EXIT, 'Beenden', \
      self.getbitmap(wx.ART_QUIT, wx.ART_TOOLBAR))
    self.toolbar.Realize()

    self.Bind(wx.EVT_TOOL, self.OnQuit, quitTool)
    self.Bind(wx.EVT_TOOL, self.OnStandard, standardTool)
    self.Bind(wx.EVT_TOOL, self.OnSave, saveTool)

  def OnQuit(self, e):
    self.Close()

  def OnStandard(self, e):
    pass

  def OnSave(self, e):
    pass

  def getbitmap(self, *args):
    return wx.ArtProvider.GetBitmap(*args)

def main():
  app = wx.App(False)
  frame = ArFrame(None, wx.ID_ANY)
  app.MainLoop()

""" Load main() """
if __name__ == "__main__":
    main()
