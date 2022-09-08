#	This file is part of PulseEqualizerGui for Kodi.
#
#	Copyright (C) 2021 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import sys
import os

import xbmcaddon
import xbmcvfs
import xbmc

from log import log
from handle import handle

from discovergui import DiscoverGui

def run_addon():
	log("start bluetooth manager")

	try:
		#avoid multiple starts of the addon to avoid conflict
		lock = os.path.join(xbmcvfs.translatePath('special://temp'),'btlock')
		if xbmcvfs.exists(lock):
			log("addon is locked: " + lock)
			return

		open(lock,'w')

		cwd = xbmcaddon.Addon().getAddonInfo('path')

		try:
			rem = sys.argv[1] == "remove"
		except IndexError:
			rem = False

		skin = xbmc.getSkinDir()
		log("skin: " + skin)

		if not os.path.exists(os.path.join(cwd,"resources","skins",skin)):
			skin = "Default"

		ui = DiscoverGui("discover.xml", cwd, skin, "1080i" , remove = rem)
		ui.doModal()

	except Exception as e:
		handle(e)

	xbmcvfs.delete(lock)
