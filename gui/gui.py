#!/usr/bin/env python
# coding=utf-8

import wx

class ArFrame(wx.Frame):
  """ This is a custom frame """
  def __init__(self, controller, *args, **kwargs):
    title = "Bildschirmprofilverwaltungswerkzeug" #DDSG-Kapitaen
    self.controller = controller
    wx.Frame.__init__(self, *args, title=title, **kwargs)
    self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    self.font.SetPointSize(int(1.2 * float(self.font.GetPointSize()) ))
    self.font.SetWeight(wx.FONTWEIGHT_BOLD)
    self.italfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    self.italfont.SetPointSize(int(0.8 * float(self.italfont.GetPointSize()) ))
    self.italfont.SetStyle(wx.FONTSTYLE_ITALIC)
    self.__toolbar()
    self.vertbox = self.__vertbox()

  def __toolbar(self):
    """ Build our toolbar """
    self.toolbar = self.CreateToolBar(style=wx.TB_HORZ_TEXT)
    saveTool = self.toolbar.AddLabelTool(wx.ID_SAVE, u'Speichern', \
      self.getbitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR))
    deleteTool = self.toolbar.AddLabelTool(wx.ID_DELETE, u'Löschen', \
      self.getbitmap(wx.ART_DELETE, wx.ART_TOOLBAR))
    self.toolbar.AddSeparator()
    standardTool = self.toolbar.AddLabelTool(wx.ID_ANY, u'Standard festlegen', \
      self.getbitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR))
    self.toolbar.AddSeparator()
    quitTool = self.toolbar.AddLabelTool(wx.ID_EXIT, u'Beenden', \
      self.getbitmap(wx.ART_QUIT, wx.ART_TOOLBAR))
    self.toolbar.Realize()
    self.Bind(wx.EVT_TOOL, self.OnQuit, quitTool)
    self.Bind(wx.EVT_TOOL, self.OnDelete, deleteTool)
    self.Bind(wx.EVT_TOOL, self.OnStandard, standardTool)
    self.Bind(wx.EVT_TOOL, self.OnSave, saveTool)

  def __vertbox(self):
    sb = wx.StaticBox(self, label="Gespeicherte Profile")
    vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
    self.SetSizerAndFit(vbox)
    return vbox

  def AddEntry(self, name='Unbekannt', comment='Kein Kommentar', \
      dimensions='Abmessungen nicht bekannt', makeline=True, status=None):
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    """ Define the left Text-Box """
    txtwidth = 300
    stname = wx.StaticText(self, label=name)
    stname.SetFont(self.font)
    stname.Wrap(txtwidth)
    stcomment = wx.StaticText(self, label=comment)
    stcomment.Wrap(txtwidth)
    stdim = wx.StaticText(self, label=dimensions)
    stdim.SetFont(self.italfont)
    stdim.Wrap(txtwidth)
    txtvbox = wx.BoxSizer(wx.VERTICAL)
    txtvbox.Add(stname, flag=wx.TOP|wx.BOTTOM, border=1)
    txtvbox.Add(stcomment, flag=wx.ALL, border=3)
    txtvbox.Add(stdim, flag=wx.TOP|wx.ALL, border=3)
    txtvbox.Add(wx.Panel(self, size=(txtwidth+10,1)))
    """ Define the right Button-Box """
    btnbox = wx.BoxSizer(wx.VERTICAL)
    statustxt = ""
    if status != None:
      if "standard" in status:
        statustxt = "Standardprofil"
      if "detected" in status:
        statustxt = "erkanntes Profil"
      if ("detected" in status) and ("standard" in status) :
        statustxt = "Standardprofil\nerkanntes Profil"
    btntxt = wx.StaticText(self, label=statustxt)
    if status != None and "active" in status:
      btnapply = wx.Button(self, id=wx.ID_REFRESH, name=name)
      stname.SetLabel(name + " (aktiv)")
    else:
      btnapply = wx.Button(self, id=wx.ID_APPLY, name=name)
    self.Bind(wx.EVT_BUTTON, self.OnApply)
    btnbox.Add(btntxt, flag=wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, border=1)
    btnbox.Add(btnapply, flag=wx.ALL, border=1)
    """ Define the middle Panel """
    midpanel = wx.Panel(self, size=(10,1))
    """ Combine all the things """
    hbox.Add(txtvbox, flag=wx.ALL, border=5)
    hbox.Add(midpanel)
    hbox.Add(btnbox, flag=wx.ALL, border=5)
    self.vertbox.Add(hbox)
    if makeline:
      self.vertbox.Add(wx.StaticLine(self), \
        flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5)
    self.vertbox.Layout()

  def OnQuit(self, e):
    self.Close()

  def OnDelete(self, e):
    profiles = self.controller.GetProfiles()
    stdmsg = "Wählen sie das Profil, das gelöscht werden soll"
    stdcap = "Profil löschen"
    stddlg = wx.SingleChoiceDialog(self, stdmsg, stdcap, profiles)
        
    if stddlg.ShowModal() == wx.ID_OK:
      select = profiles[stddlg.GetSelection()]
      self.controller.Delete(select)

  def OnStandard(self, e):
    profiles = ['Keines'] +  self.controller.GetProfiles()
    stdmsg = "Wählen sie das Standardprofil, das beim Anmelden geladen wird:"
    stdcap = "Standardprofil wählen"
    stddlg = wx.SingleChoiceDialog(self, stdmsg, stdcap, profiles)
        
    if stddlg.ShowModal() == wx.ID_OK:
      select = profiles[stddlg.GetSelection()]
      if select == "Keines":
        select = None
      self.controller.SetStandard(select)
    
  def OnApply(self, e):
    self.controller.SetProfile(e.GetEventObject().GetName())

  def OnSave(self, e):
    pass

  def getbitmap(self, *args):
    return wx.ArtProvider.GetBitmap(*args)

  def drawme(self):
    self.Fit()
    self.CenterOnScreen()
    self.Show()

def main():
  app = wx.App(False)
  frame = ArFrame(None, None, wx.ID_ANY)
  frame.AddEntry()
  frame.AddEntry(name="Blah", comment="Das ist ein langer, mehrzeiliger Kommentar. Ja \
wirklich! Lorem ipsum und so.")
  frame.AddEntry(name="Blubb", comment="Das ist ein langer, mehrzeiliger Kommentar. Ja \
wirklich! Lorem ipsum und so.", status=["standard", "detected", "active"])
  frame.Fit()
  frame.CenterOnScreen()
  frame.Show(True)
  app.MainLoop()

""" Load main() """
if __name__ == "__main__":
    main()
