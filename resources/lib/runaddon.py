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

import xbmcaddon

from log import log
from handle import handle

from discovergui import DiscoverGui

def run_addon():
	log("start bluetooth manager")
	try:
		cwd = xbmcaddon.Addon().getAddonInfo('path')

		try:
			rem = False
			cmd = sys.argv[1]
			if cmd == "remove":
				rem = True
		except Exception:
			rem = False

		ui = DiscoverGui("discover.xml", cwd, "Default", "1080i" , remove = rem)
		ui.doModal()

	except Exception as e:
		handle(e)
