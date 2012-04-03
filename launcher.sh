#!/bin/bash

if [  "$1" = "nvidia" ]; then
  [ -x /usr/bin/nvidia-settings ] && \
    /usr/bin/nvidia-settings -p "X Server Display Configuration"
elif [ "$1" = "disper" ]; then
  if [ -x /usr/bin/disper ]; then
    shift
    /usr/bin/disper $@
  fi
else
  [ -x /usr/bin/arandr ] && \
    /usr/bin/arandr
fi
[ -x /etc/autorandr/postswitch ] && \
  /etc/autorandr/postswitch
