#!/bin/bash

if [  "$1" = "nvidia" ]; then
  [ -x /usr/bin/nvidia-settings ] && \
    /usr/bin/nvidia-settings -p "X Server Display Configuration"
else
  [ -x /usr/bin/arandr ] && \
    /usr/bin/arandr
fi
[ -x /etc/autorandr/postswitch ] && \
  /etc/autorandr/postswitch
