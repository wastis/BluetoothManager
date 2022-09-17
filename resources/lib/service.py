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
import xbmcaddon
import xbmcvfs
import os
from handle import handle

cwd	= xbmcaddon.Addon().getAddonInfo('path')

if ( __name__ == "__main__" ):
	try:
		lock = os.path.join(xbmcvfs.translatePath('special://temp'),'btlock')
		if xbmcvfs.exists(lock):
			xbmcvfs.delete(lock)
	except Exception as e:
		handle(e)
