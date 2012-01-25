#!/usr/bin/env python

import subprocess, logging, os, sys
import re, fileinput, shutil, codecs

def findscript(exename):
  """ Return true when the executable named exename is in the path. """
  if subprocess.call(["which", exename]):
    logging.error("{0} can not be found".format(exename))
    return False
  return True
    
def main():
  """ Testing """
  logging.basicConfig(level=logging.DEBUG)
  ar = AutoRandR()
  ar.saveprofile( name="Test Blubb", comment="Das ist das Testprofil", force=True )
  profiles = ar.getprofiles()
  print(profiles)
  for i in profiles:
    print(repr(ar.getprofileinfo(i)))
  ar.setprofile("Nur Extern", force=True)
  ar.setdefaultprofile("Standard")
  ar.deleteprofile("Test Blubb")


class AutoRandR:
  """ Wraps around autorandr/autodisper and provides a interface for display
  profiles """

  def __init__(self):
    """ Look up if everything we need is there """
    for i in ["disper", "autodisper", "autorandr"]:
      if not findscript(i):
        sys.exit("{0} was not found in PATH".format(i))
    self.ardir = os.path.expanduser("~/.autorandr")
    self.arconf = self.ardir + ".conf" 
    self.autox()
    self.setupdir()

  def autox(self):
    """ Returns the name of the script which should be used """
    if hasattr(self,"autox_value"):
      return self.autox_value
    else:
      """ When the GPU supports the NV-CONTROL extension we use autodispser """
      findscript("xdpyinfo")
      exe = subprocess.Popen("xdpyinfo", stdout=subprocess.PIPE)
      xdpyinfo = exe.communicate()[0]
      regex = re.compile(r'NV-CONTROL$')
      for line in xdpyinfo.splitlines():
        if regex.search(line):
          logging.info("NV-CONTROL extension found. Using autodisper.")
          self.autox_value="autodisper"
          return self.autox_value
      logging.info("Using autorandr.")
      self.autox_value="autorandr"
      return self.autox_value

  def setupdir(self):
    """ Creates $HOME/.autorandr and deploys a postswitch file, if it does not exist """
    if not os.path.exists(self.ardir):
      os.mkdir(self.ardir)
      logging.info("Creating configuration directory {0}".format(self.ardir))
    else:
      logging.info("Configuration directory {0} exists".format(self.ardir))
    pswitchfile = self.ardir + os.sep + "postswitch"
    if not os.path.isfile(pswitchfile):
      logging.info("Creating postswitch script {0}".format(pswitchfile))
      pswitch = open(pswitchfile, 'w')
      pswitch.write("#!/bin/sh\ndcop kicker kicker restart\n")
      pswitch.close()
      os.chmod(pswitchfile, int(0700))
    else:
      logging.info("Found postswitch script {0}. Keeping".format(pswitchfile))

  def getprofiles(self):
    """ Gets a list of profilenames """
    plist= []
    for entry in os.listdir(self.ardir):
      profiledir = self.ardir + os.sep + entry
      if os.path.isdir(profiledir):
        logging.debug(\
            u"Looking for a profile. Testing {0}".format(repr(profiledir)))
        content = os.listdir(profiledir)
        logging.debug(\
            u"Found {0} in candidate profile {1}".format(repr(content), \
              repr(entry)))
        if "config" in content:
          plist.append(entry)
          logging.info(u"Found a profile named {0}".format(repr(entry)))
    return plist

  def getprofileinfo(self, name):
    """ Returns a dict with the details to a profile """
    info = {}
    try:
      comment = open( self.ardir + os.sep + name + os.sep + "comment" )
      info['comment'] = comment.read().strip()
    except:
      logging.info(u"Profile {0} has no comment file".format(repr(name)))
    try:
      config = open( self.ardir + os.sep + name + os.sep + "config" )
    except IOError as e:
      logging.error(\
          u"Profile {0} does not exist or is damaged".format(repr(name)))
      return None
    info['name'] = name
    if name in self.getdetectedprofile():
      info['isdetected']=True
    else:
      info['isdetected']=False
    if self.getdefaultprofile() == name:
      info['isdefault']=True
    else:
      info['isdefault']=False
    if self.getactiveprofile() == name:
      info['isactive']=True
    else:
      info['isactive']=False
    outputs = []
    modes = []
    positions = []
    # TODO This does not work with autodisper
    for line in config.readlines():
      line = line.split()
      if line[0] == "output":
        outputs.append(line[1:])
      elif line[0] == "off":
        outputs.pop()
      elif line[0] == "mode":
        modes.append(line[1:])
      elif line[0] == "pos":
        if line[1:] == ["0x0"]:
          pos = ""
        else:
          pos = line[1:]
        positions.append(pos)
    info['config'] = {}
    for i in range(len(outputs)):
      # TODO Warum zum Geier brauch ich hier die .joins
      info['config']["".join(outputs[i])] = [ "".join(modes[i]), "".join(positions[i]) ]
    return info
 
  def getdetectedprofile(self):
    """ Returns the name of the first detected profile or None """
    name = []
    exe = subprocess.Popen(self.autox(), stdout=subprocess.PIPE)
    clist = exe.communicate()[0]
    regex = re.compile(r'\(detected\)$')
    for line in clist.splitlines():
      logging.debug(u"Searching (detected) in {0}".format(repr(line.strip())))
      if regex.search(line):
        name.append(" ".join(line.split()[0:-1]))
          # Any profile which has a whitespace other than <SPACE> will fail here
        logging.info(u"Found detected profile(s) {0}".format(repr(name)))
    return name

  def getactiveprofile(self):
    """ Returns the last set profile """
    return self.getconf("active_profile")

  def getdefaultprofile(self):
    """ Returns the name of the default profile """
    return self.getconf("default_profile")

  def getconf(self, name):
    """ Returns a variable from the configuration file """
    try:
      arconf = open( self.arconf )
    except IOError as e:
      logging.info("Configuration file not found.")
      return None
    regex = re.compile(r'^{0}='.format(name.upper()))
    for line in arconf.readlines():
      search = regex.search(line)
      if search:
        default = line[search.end():].strip().strip('"')
        logging.info("Found Configuration {0} - set to {1}".format(name, default))
        return default
    logging.info("Configuration {0} not found.".format(name))
    return None

  def setprofile(self, name, force=False):
    """ Asks autorandr to set this profile """
    logging.info(u"Trying to set profile {0}".format(repr(name)))
    if name not in unicode(self.getprofiles()):
      logging.error(u"The profile {0} can not be found".format(repr(name)))
      return False
    launch = [ self.autox(), "-l", name ]
    if force == True:
      launch.append("--force")
    logging.debug(u"Trying to set profile with {0}".format(repr(launch)))
    exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
    out = exe.communicate()[0]
    ret = exe.returncode
    if ret != 0:
      for line in out.splitlines():
        logging.error(self.autox() + ": " + line)
        logging.error(\
            u"Loading profile {0} was unsucessful".format(repr(name)))
      return False
    for line in out.splitlines():
      logging.info(self.autox() + ": " + line)
      logging.info(u"Loading profile {0} was sucessful".format(repr(name)))
    return True

  def setconf(self, name, value):
    """ Sets a configuration entry """
    if value == None:
      value = ""
    if os.path.isfile(self.arconf):
      regex = re.compile(r'^{0}='.format(name.upper()))
      found = False
      for line in fileinput.input(self.arconf,inplace=True):
        search = regex.search(line)
        if search:
          found = True
          line = '{0}="{1}"\n'.format(name.upper(),value)
        sys.stdout.write(line)
      if found:
        logging.info(u"Set {0} to {1}".format(repr(name), repr(value)))
        return True
    try:
      arconf = codecs.open(self.arconf, 'a', 'utf-8-sig')
      # Old Style Format here, due to a bug in python 2.x (#7300)
      arconf.write('%(0)s="%(1)s"\n' % { '0': name.upper(), '1': value} )
      arconf.close()
    except IOError as e:
      logging.error(u"Failed to set {0} to {1}".format(repr(name), repr(value)))
      return False
    logging.info(u"Set {0} to {1}".format(repr(name), repr(value)))
    return True

  def setdefaultprofile(self, name):
    """ Sets default profile """
    if name not in self.getprofiles() and name !=None:
      logging.error(u"Profile {0} can not be found.".format(repr(name)))
      return False
    return self.setconf("default_profile", name)

  def setactiveprofile(self, name):
    """ Sets the active profile """
    return self.setconf("active_profile", name)

  def saveprofile(self, name, comment=None, force=False):
    """ Saves a profile according to the comment and the current settings """
    if name in self.getprofiles():
      logging.error(u"A profile with the name {0} already exists.".format(repr(name)))
      if not force:
        return False
    launch = [ self.autox(), "-s", name ]
    logging.debug(u"Trying to save profile with {0}".format(repr(launch)))
    exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
    out = exe.communicate()[0]
    ret = exe.returncode
    if ret != 0:
      for line in out.splitlines():
        logging.error(self.autox() + ": " + line)
        logging.error(u"Saving profile {0} was unsucessful".format(repr(name)))
      return False
    for line in out.splitlines():
      logging.info(self.autox() + ": " + line)
      logging.info(u"Saving profile {0} was sucessful".format(repr(name)))
    if comment:
      try:
        cmt = codecs.open( self.ardir + os.sep + name + os.sep + "comment",\
            'w', "utf-8-sig")
        cmt.write( comment )
        cmt.close()
      except IOError as e:
        print e
        logging.error(u"Could not write comment for profile {0}".format(repr(name)))
    return True

  def deleteprofile(self, name):
    """ Deletes a profile """
    if name not in self.getprofiles():
      logging.error(u"The profile {0} cannot be found.".format(repr(name)))
      return False
    try:
      shutil.rmtree(self.ardir + os.sep + name)
    except OSError as e:
      logging.error(u"Deleting profile {0} failed.".format(repr(name)))
      return False
    if name == self.getdefaultprofile():
      self.setdefaultprofile(None)
    logging.info(u"Profile {0} was deleted".format(repr(name)))
    return True

""" Load main() """
if __name__ == "__main__":
  main()
