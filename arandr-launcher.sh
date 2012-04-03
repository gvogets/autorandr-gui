#!/bin/bash

[ -x /usr/bin/arandr ] && \
 /usr/bin/arandr 
[ -x /etc/autorandr/postswitch ] && \
  /etc/autorandr/postswitch
