#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Landeshauptstadt München
# All rights reserved.
#
# Licensed under the EUPL, Version 1.0 only (the "Licence"); 
# You may not use this work except in compliance with the Licence. 
# You may obtain a copy of the Licence at: 
#
# http://joinup.ec.europa.eu/software/page/eupl
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the Licence for the specific language governing permissions and
# limitations under the Licence. 

from DistUtilsExtra.auto import setup

setup (name = 'autorandr-gui',
  description = "GUI for autorandr",
  version = '1.0',
  author = 'Georg Vogetseder',
  author_email = 'externer.dl.vogetseder@muenchen.de',
  url = 'http://www.muenchen.de/limux',
  packages = ['autorandrgui'],
  scripts = ['autorandr-gui'],
  data_files = [('/etc/xdg/autostart',['data/autorandr-gui.desktop'])],
)
