#!/usr/bin/env python

import subprocess, logging, os, sys
import re, fileinput

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
  ar.saveprofile( name="Test Blah", comment="Das ist das Testprofil", force=True )
  profiles = ar.getprofiles()
  print(profiles)
  for i in profiles:
    print(repr(ar.getprofileinfo(i)))
  ar.setprofile("Nur Extern", force=True)
  ar.setdefaultprofile("Standard")


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
        logging.debug("Looking for a profile. Testing {0}".format(profiledir))
        content = os.listdir(profiledir)
        logging.debug("Found {0} in candidate profile {1}".format(repr(content), entry))
        if "config" in content:
          plist.append(entry)
          logging.info("Found a profile named {0}".format(entry))
    return plist

  def getprofileinfo(self, name):
    """ Returns a dict with the details to a profile """
    info = {}
    try:
      comment = open( self.ardir + os.sep + name + os.sep + "comment" )
      info['comment'] = comment.readline().strip()
    except:
      logging.info("Profile {0} has no comment file".format(name))
    try:
      config = open( self.ardir + os.sep + name + os.sep + "config" )
    except IOError as e:
      logging.error("Profile {0} does not exist or is damaged".format(name))
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
        positions.append(line[1:])
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
      logging.debug("Searching (detected) in {0}".format(line.strip()))
      if regex.search(line):
        name.append(" ".join(line.split()[0:-1]))
          # Any profile which has a whitespace other than <SPACE> will fail here
        logging.info("Found detected profile(s) {0}".format(name))
    return name

  def getdefaultprofile(self):
    """ Returns the name of the default profile """
    try:
      arconf = open( self.arconf )
    except IOError as e:
      logging.info("No default profile set.")
      return None
    regex = re.compile(r'^DEFAULT_PROFILE=')
    for line in arconf.readlines():
      search = regex.search(line)
      if search:
        default = line[search.end():].strip().strip('"')
        logging.info("Found default profile {0}".format(default))
        return default
    return None

  def setprofile(self, name, force=False):
    """ Asks autorandr to set this profile """
    logging.info("Trying to set profile {0}".format(name))
    if name not in self.getprofiles():
      logging.error("The profile {0} can not be found".format(name)) 
      return False
    launch = [ self.autox(), "-l", name ]
    if force == True:
      launch.append("--force")
    logging.debug("Trying to set profile with {0}".format(repr(launch)))
    exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
    out = exe.communicate()[0]
    ret = exe.returncode
    if ret != 0:
      for line in out.splitlines():
        logging.error(self.autox() + ": " + line)
        logging.error("Loading profile {0} was unsucessful".format(name))
      return False
    for line in out.splitlines():
      logging.info(self.autox() + ": " + line)
      logging.info("Loading profile {0} was sucessful".format(name))
    return True

  def setdefaultprofile(self, name):
    """ Sets default profile """
    if name not in self.getprofiles():
      logging.error("Profile {0} can not be found.".format(name))
      return False
    if os.path.isfile(self.arconf):
      regex = re.compile(r'^DEFAULT_PROFILE=')
      for line in fileinput.input(self.arconf,inplace=True):
        found = False
        search = regex.search(line)
        if search:
          found = True
          line = 'DEFAULT_PROFILE="{0}"\n'.format(name)
        sys.stdout.write(line)
      if found:
        logging.info("Replaced {0} as the default profile".format(name))
        return True
    try:
      arconf = open(self.arconf, 'w')
      arconf.write('DEFAULT_PROFILE="{0}"\n'.format(name))
      arconf.close()
    except IOError as e:
      logging.error("Failed to set {0} as the default profile".format(name))
      return False
    logging.info("Set {0} as the default profile".format(name))
    return True

  def saveprofile(self, name, comment=None, force=False):
    """ Saves a profile according to the comment and the current settings """
    if name in self.getprofiles():
      logging.error("A profile with the name {0} already exists.".format(name))
      if not force:
        return False
    launch = [ self.autox(), "-s", name ]
    logging.debug("Trying to save profile with {0}".format(repr(launch)))
    exe = subprocess.Popen(launch, stdout=subprocess.PIPE)
    out = exe.communicate()[0]
    ret = exe.returncode
    if ret != 0:
      for line in out.splitlines():
        logging.error(self.autox() + ": " + line)
        logging.error("Saving profile {0} was unsucessful".format(name))
      return False
    for line in out.splitlines():
      logging.info(self.autox() + ": " + line)
      logging.info("Saving profile {0} was sucessful".format(name))
    if comment:
      try:
        cmt = open( self.ardir + os.sep + name + os.sep + "comment", 'w' )
        cmt.write( comment + os.linesep )
        cmt.close()
      except IOError as e:
        print e
        logging.error("Could not write comment for profile {0}".format(name))
    return True

""" Load main() """
if __name__ == "__main__":
    main()
