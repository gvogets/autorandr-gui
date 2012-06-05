#!/usr/bin/env python
# coding=utf-8

import wx
import xdg.IconTheme
import subprocess
import logging

class NewProfile(wx.Dialog):
  """ Dialog for Entering a Name and a Comment for a new Profile """

  def __init__(self, parent, *args, **kwargs):
    """ Describe the GUI for saving a new profile. """
    logging.debug(u"Opening a NewProfile dialog")
    self.profile = None
    super(NewProfile, self).__init__(parent=parent, title="Profil speichern")
    panel = wx.Panel(self)
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    sizer = wx.FlexGridSizer(cols=2, rows=3, vgap=15, hgap=15)
    nametxt = wx.StaticText(self, label="Profilname")
    commenttxt = wx.StaticText(self, label="Kommentar")
    name = wx.TextCtrl(self)
    comment = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
    sizer.AddMany([(nametxt), (name, 1, wx.EXPAND),\
        (commenttxt), (comment, 1, wx.EXPAND),\
        (wx.StaticText(panel)), (btns, 1, wx.EXPAND)])
    sizer.AddGrowableRow(1, 1)
    sizer.AddGrowableCol(1, 1)
    hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
    self.SetSizerAndFit(hbox)
    self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
    self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    self.name = name
    self.comment = comment

  def OnOk(self, e):
    """ Save the input and close the dialog. """
    logging.debug(u"Returning information for a new profile")
    self.profile = [self.name.GetValue(), self.comment.GetValue()]
    self.Destroy()

  def OnCancel(self, e):
    """ Just close the dialog. """
    self.Destroy()

class TimeoutDialog(wx.Dialog):
  """ Displays a Dialog with a countdown for hot key mode. """

  def __init__(self, parent, timeout, *args, **kwargs):
    """ Describe the timeout dialog. """
    logging.debug(u"Opening a new timeout dialog box with a duration of {0} secs.".format(timeout))
    TIMER_ID = 100
    self.timeout = timeout
    super(TimeoutDialog, self).__init__(parent=parent, \
        title=u"Die Bildschirmuflösung wurde geändert")
    vbox = wx.BoxSizer(wx.VERTICAL)
    font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    font.SetPointSize(int(1.2 * float(font.GetPointSize()) ))
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    self.title = wx.StaticText(self, label="Ist die Bildschirmanzeige in Ordnung?")
    self.title.SetFont(font)
    self.text = wx.StaticText(self)
    self.__SetLabelText()
    btns = self.CreateButtonSizer(wx.YES|wx.NO|wx.NO_DEFAULT)
    vbox.Add(self.title, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=30)
    vbox.Add(self.text, proportion=1, flag=wx.LEFT|wx.RIGHT, border=30)
    vbox.Add(btns, proportion=1, flag=wx.ALL|wx.ALIGN_CENTER, border=15)
    self.SetSizerAndFit(vbox)
    self.Bind(wx.EVT_BUTTON, self.OnNo, id=wx.ID_NO)
    self.Bind(wx.EVT_BUTTON, self.OnYes, id=wx.ID_YES)
    """ Add a Timer """
    self.tim = wx.Timer(self, TIMER_ID)
    self.tim.Start(1000)
    wx.EVT_TIMER(self, TIMER_ID, self.OnTimer)

  def __SetLabelText(self):
    """ Generate the label to fit with the current timeout. """
    self.text.SetLabel(u"Diese Anzeige wird in " + \
        u"%i Sekunden "  % self.timeout + \
        u"auf die vorherige Einstellung zurückgesetzt.")

  def OnYes(self, e):
    logging.debug(u"Proper display configuration confirmed by user")
    self.EndModal(wx.ID_YES)

  def OnNo(self, e):
    self.EndModal(wx.ID_NO)

  def OnTimer(self, e):
    """ Change the Label or if the time has run out: Close and return ID_NO. """
    if self.timeout > 1:
      self.timeout -= 1
      self.__SetLabelText()
      self.tim.Start(1000)
      logging.debug(u"The timeout is now at {0} secs.".format(self.timeout))
    else:
      self.EndModal(wx.ID_NO)

class ArFrame(wx.Frame):
  """ Main GUI """

  def __init__(self, controller, *args, **kwargs):
    """ Describe the main UI and font settings. """
    logging.debug(u"Initializing main UI")
    title = "Bildschirmprofilverwaltungswerkzeug" #DDSG-Kapitaen
    self.controller = controller
    wx.Frame.__init__(self, *args, title=title, **kwargs)
    self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    self.font.SetPointSize(int(1.2 * float(self.font.GetPointSize()) ))
    self.font.SetWeight(wx.FONTWEIGHT_BOLD)
    self.italfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    self.italfont.SetPointSize(int(0.8 * float(self.italfont.GetPointSize()) ))
    #self.italfont.SetStyle(wx.FONTSTYLE_ITALIC)
    self.__toolbar()
    self.vertbox = self.__vertbox()


  def __toolbar(self):
    """ Build our toolbar """
    logging.debug(u"Building toolbar")
    self.toolbar = self.CreateToolBar(style=wx.TB_HORZ_TEXT)
    openTool = self.toolbar.AddLabelTool(wx.ID_ANY, u'Bildschirm einrichten',\
      self.getbitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR), \
      shortHelp=u"Das Einstellungswerkzeug Ihres Rechners starten.")
    autoTool = self.toolbar.AddLabelTool(wx.ID_ANY, u'Automatik', \
      self.getbitmap(wx.ART_GO_UP, wx.ART_TOOLBAR), \
      shortHelp=u"Automatisches Ausrichten von Bildschirmen")
    self.toolbar.AddSeparator()
    saveTool = self.toolbar.AddLabelTool(wx.ID_SAVE, u'Speichern', \
      self.getbitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR), \
      shortHelp=u"Die derzeitigen Bildschirminstellungen als Profil speichern.")
    deleteTool = self.toolbar.AddLabelTool(wx.ID_DELETE, u'Löschen', \
      self.getbitmap(wx.ART_DELETE, wx.ART_TOOLBAR), \
      shortHelp=u"Ein Profil auswählen und löschen.")
    self.toolbar.AddSeparator()
    standardTool = self.toolbar.AddLabelTool(wx.ID_ANY, u'Standard festlegen', \
      self.getbitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR), \
      shortHelp=u"Ein Profil als Voreinstellung beim Rechnerstart festlegen.")
    self.toolbar.AddSeparator()
    quitTool = self.toolbar.AddLabelTool(wx.ID_EXIT, u'Beenden', \
      self.getbitmap(wx.ART_QUIT, wx.ART_TOOLBAR), \
      shortHelp=u"Das Programm beenden.")
    self.toolbar.Realize()
    self.Bind(wx.EVT_TOOL, self.OnOpen, openTool)
    self.Bind(wx.EVT_TOOL, self.OnQuit, quitTool)
    self.Bind(wx.EVT_TOOL, self.OnDelete, deleteTool)
    self.Bind(wx.EVT_TOOL, self.OnStandard, standardTool)
    self.Bind(wx.EVT_TOOL, self.OnSave, saveTool)
    self.Bind(wx.EVT_TOOL, self.OnAuto, autoTool)
    self.SetToolBar(self.toolbar)

  def __vertbox(self):
    """ Create a box to hold all profile entries. """
    sb = wx.StaticBox(self, label="Gespeicherte Profile")
    vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
    self.SetSizerAndFit(vbox)
    return vbox

  def AddEmptyEntry(self):
    """ Add a empty box to show that no profiles have been saved """
    msg = u'Kein gespeichertes Profil vorhanden'
    text = wx.StaticText(self, label=msg)
    text.SetFont(self.font)
    text.SetForegroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_GRAYTEXT))
    self.vertbox.Add(text, flag=wx.GROW|wx.ALIGN_CENTER|wx.BOTTOM|wx.TOP, \
        border=30)
    self.vertbox.Layout()
    

  def AddEntry(self, name='Unbekannt', comment='Kein Kommentar', \
      dimensions=None, makeline=True, status=None, enable=True):
    """ Draw the Box that contains information from a single profile """
    logging.debug(u"Adding an entry for profile {0}".format(name))
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    """ Define the left Text-Box """
    txtwidth = 350
    stname = wx.StaticText(self, label=name)
    stname.SetFont(self.font)
    stname.Wrap(txtwidth)
    stcomment = wx.StaticText(self, label=comment)
    stcomment.Wrap(txtwidth)
    stdim = wx.FlexGridSizer(cols=3, vgap=1, hgap=5)
    if dimensions == None:
      txt = wx.StaticText(self, label="Bildschirmeinstellung unbekannt")
      txt.SetFont(self.italfont)
      stdim.Add(txt)
    else:
      for i in range(len(dimensions)):
        txt = wx.StaticText(self, label=dimensions[i])
        txt.SetToolTipString(str(i))
        txt.SetFont(self.italfont)
        if i % 3 == 1:
          sty = wx.ALIGN_CENTER
        elif i % 3 == 0:
          sty = wx.ALIGN_RIGHT
        else:
          sty = wx.ALIGN_LEFT
          txt.SetForegroundColour( \
              wx.SystemSettings_GetColour(wx.SYS_COLOUR_GRAYTEXT))
        stdim.Add(txt, flag=sty)
    txtvbox = wx.BoxSizer(wx.VERTICAL)
    txtvbox.Add(stname, flag=wx.TOP|wx.BOTTOM, border=1)
    txtvbox.Add(stcomment, flag=wx.ALL, border=3)
    txtvbox.Add(stdim, flag=wx.TOP|wx.ALL, border=3)
    """ Define the right Button-Box """
    statustxt = ""
    if status != None:
      if "standard" in status:
        statustxt = "Standardprofil"
      if "detected" in status:
        statustxt = "erkanntes Profil"
      if ("detected" in status) and ("standard" in status) :
        statustxt = "Standardprofil\nerkanntes Profil"
    btntxt = wx.StaticText(self, label=statustxt, style=wx.ALIGN_RIGHT)
    if status != None and "active" in status:
      btnapply = wx.Button(self, id=wx.ID_REFRESH, name=name)
      stname.SetLabel(name + " (aktiv)")
    else:
      btnapply = wx.Button(self, id=wx.ID_APPLY, name=name)
    if enable == False:
      btnapply.Disable()
      btntxt.SetLabel('inkompatibles Profil')
    self.Bind(wx.EVT_BUTTON, self.OnApply)
    """ Define the middle Panel """
    midpanel = wx.Panel(self, size=(10,1))
    """ Combine all the things """
    hbox.Add(txtvbox, 0, flag=wx.ALL, border=5)
    hbox.Add(midpanel, 1, flag=wx.EXPAND|wx.ALL)
    hbox.Add(btntxt, 0, \
        flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, \
        border=5)
    hbox.Add(btnapply, 0, \
        flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, \
        border=5)
    self.vertbox.Add(hbox, flag=wx.EXPAND)
    if makeline:
      self.vertbox.Add(wx.StaticLine(self), \
        flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5)
    self.vertbox.Layout()

  def OnQuit(self, e):
    self.Close()

  def OnOpen(self, e):
    """ Load external tool to configure the displays. """
    if self.controller.GetBackend() == 'auto-disper':
      launch = ["/usr/share/autorandr/launcher.sh", "nvidia"]
      logging.debug(u"Launching nvidia-settings")
    else:
      launch = "/usr/share/autorandr/launcher.sh"
      logging.debug(u"Launching arandr")
    exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
    self.controller.UnsetActiveProfile()

  def OnDelete(self, e):
    """ Displays a Dialog for choosing a profile to delete. """
    profiles = self.controller.GetProfiles(False)
    logging.debug(u"Display dialog to delete a profile")
    stdmsg = "Wählen sie das Profil, das gelöscht werden soll"
    stdcap = "Profil löschen"
    stddlg = wx.SingleChoiceDialog(self, stdmsg, stdcap, profiles)
        
    if stddlg.ShowModal() == wx.ID_OK:
      select = profiles[stddlg.GetSelection()]
      self.controller.Delete(select)

  def OnAuto(self, e):
    """ Display a dialog to call disper with a few automatic options. """
    modes = { \
        u"Primärer Bildschirm": ["-s"], \
        u"Sekundärer Bildschirm": ["-S"], \
        "Klonmodus": ["-c"], \
        "Erweiterter Desktop, links": ["-e", "-t", "left"], \
        "Erweiterter Desktop, rechts": ["-e", "-t", "right"], \
        }
    logging.debug(u"Display automatic dialog")
    stdmsg = u"Wählen sie den gewünschten automatischen Modus:"
    stdcap = "Automatik"
    stddlg = wx.SingleChoiceDialog(self, stdmsg, stdcap, sorted(modes.keys()) )

    if stddlg.ShowModal() == wx.ID_OK:
      select = stddlg.GetStringSelection()
      args = modes[select]
      launch = ["/usr/share/autorandr/launcher.sh", "disper"] + args
      exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
      self.controller.UnsetActiveProfile()

  def OnStandard(self, e):
    """ Display a dialog to choose a standard profile or no profile. """
    logging.debug(u"Display dialog to choose a standard profile")
    profiles = ['Keines'] +  self.controller.GetProfiles(False)
    stdmsg = "Wählen sie das Standardprofil, das beim Anmelden geladen wird:"
    stdcap = "Standardprofil wählen"
    stddlg = wx.SingleChoiceDialog(self, stdmsg, stdcap, profiles)
        
    if stddlg.ShowModal() == wx.ID_OK:
      select = profiles[stddlg.GetSelection()]
      if select == "Keines":
        select = None
      self.controller.SetStandard(select)
    
  def OnApply(self, e):
    """ Load this profile """
    name = e.GetEventObject().GetName()
    logging.debug(u"Applying profile {0}".format(name))
    self.controller.SetProfile(name)

  def OnSave(self, e):
    """ Save a profile, display the NewProfile dialog """
    dialog = NewProfile(self)
    dialog.ShowModal()
    if dialog.profile != None:
      self.controller.Add(name=dialog.profile[0], comment=dialog.profile[1])
    dialog.Destroy()


  def getbitmap(self, *args):
    """ A helper function for the toolbar """
    return wx.ArtProvider.GetBitmap(*args)

  def drawme(self):
    """ Draw the application in the appropriate size. """
    logging.debug(u"Drawing the UI")
    self.Fit()
    width = self.toolbar.GetSizeTuple()[0]
    height = self.GetClientSizeTuple()[1]
    self.SetClientSizeWH(width, height)
    self.Show()

def main():
  """ Testing when calling directly """
  app = wx.App(False)
  frame = ArFrame(None, None, wx.ID_ANY)
  frame.AddEntry()
  frame.AddEntry(name="Blah", \
      comment="Das ist ein Kommentar")
  frame.AddEntry(name="Blubb", \
      comment="Das ist ein langer, mehrzeiliger Kommentar." + \
        "wirklich! Lorem ipsum und so.", \
        status=["standard", "detected", "active"])
  frame.Fit()
  frame.Show(True)
  app.MainLoop()

""" Load main() """
if __name__ == "__main__":
    main()
