#!/usr/bin/env python

import subprocess, logging, os, sys
import re

def findscript(exename):
  """ Return true when the executable named exename is in the path. """
  if subprocess.call(["which", exename]):
    logging.error("{0} can not be found".format(exename))
    return False
  return True
    
def main():
  logging.basicConfig(level=logging.DEBUG)
  ar = AutoRandR()
  profiles = ar.getprofiles()
  print(profiles)
  for i in profiles:
    print(repr(ar.getprofileinfo(i)))


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
    if self.getdetectedprofile() == name:
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
    exe = subprocess.Popen(self.autox(), stdout=subprocess.PIPE)
    clist = exe.communicate()[0]
    regex = re.compile(r'\(detected\)$')
    for line in clist.splitlines():
      logging.debug("Searching (detected) in {0}".format(line.strip()))
      if regex.search(line):
        name = " ".join(line.split()[0:-1])
          # Any profile which has a whitespace other than <SPACE> will fail here
        logging.info("Found detected profile {0}".format(name))
        return name
    return None

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
        # TODO Here we should check if the profile exists.
        return default
    return None


  def setprofile(self, name="Standard", force=False):
    """ Asks autorandr to set this profile """
    pass 

  def setdefaultprofile(self, name):
    """ Sets default profile """
    pass

  def saveprofile(self, info):
    """ Saves a profile according to the dict info and the current settings """
    pass

""" Load main() """
if __name__ == "__main__":
    main()
