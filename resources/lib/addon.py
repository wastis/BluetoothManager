#	This file is part of Bluetooth Manager for Kodi.
#
#	Copyright (C) 2022 wastis    https://github.com/wastis/BluetoothManager
#
#	Bluetooth Manager is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import os
import sys
import xbmcaddon

cwd	= xbmcaddon.Addon().getAddonInfo('path')
sys.path.append ( os.path.join( cwd, 'resources', 'lib' ))
sys.path.append ( os.path.join( cwd, 'resources', 'language' ))

from runaddon import run_addon

if ( __name__ == "__main__" ):
	run_addon()
