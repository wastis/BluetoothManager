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

from threading import Thread
import time

import dbussy as dbus
from dbussy import DBUS
from handle import handle
from handle import opthandle
from bluezobject import BlueZAdapter
from bluezobject import BlueZDevice
from log import log

class BlueZSignal:
	def __init__(self, objects = None, on_change = None):
		self.bus_name = 'org.bluez'
		self.loop = None
		self.objects = objects
		self.on_change = on_change
		self.running = False

	def message_filter(self, connection, message, _) :
		try:
			if message.path is not None and \
				(message.path == "/" or message.path.startswith("/org/bluez")):
				if message.member == "PropertiesChanged":
					objlist = [arg for arg in message.objects]

					if objlist[0] == "org.bluez.Device1":
						obj = self.objects.devices[str(message.path)]
						msg = "on_device_change"
					elif objlist[0] == "org.bluez.Adapter1":
						obj = self.objects.adapters[str(message.path)]
						msg = "on_adapter_change"
					else:
						return DBUS.HANDLER_RESULT_NOT_YET_HANDLED

					sig = obj.set_attributes(objlist[1])
					if sig:
						self.on_change(msg, [str(message.path), sig])

					return DBUS.HANDLER_RESULT_HANDLED

				if message.member == "InterfacesRemoved":
					objlist = [arg for arg in message.objects]

					if "org.bluez.Device1" in objlist[1]:
						self.objects.devices.pop(str(objlist[0]))
						self.on_change("on_device_remove", [str(objlist[0])])

					if "org.bluez.Adapter1" in objlist[1]:
						self.objects.adapters.pop(str(objlist[0]))
						self.on_change("on_adapter_remove", [str(objlist[0])])

					return DBUS.HANDLER_RESULT_HANDLED

				if message.member == "InterfacesAdded":
					objlist = [arg for arg in message.objects]

					if "org.bluez.Device1" in objlist[1]:
						self.objects.devices[str(objlist[0])] = \
							BlueZDevice(objlist[1]["org.bluez.Device1"],str(objlist[0]))
						self.on_change("on_device_new",[str(objlist[0])])

					elif "org.bluez.Adapter1" in objlist[1]:
						self.objects.adapters[str(objlist[0])] = \
							BlueZAdapter(objlist[1]["org.bluez.Adapter1"],str(objlist[0]))
						self.on_change("on_adapter_new",[str(objlist[0])])

					return DBUS.HANDLER_RESULT_HANDLED
			return DBUS.HANDLER_RESULT_HANDLED

		except Exception as e:
			opthandle(e)
			return DBUS.HANDLER_RESULT_HANDLED

	def run(self):
		try:
			self.running = True
			conn = dbus.Connection.bus_get \
			  (
				DBUS.BUS_SYSTEM, private = False
			  )
			conn.add_filter(self.message_filter, None)
			conn.bus_add_match("type=signal")

			while conn.read_write_dispatch(timeout = 0.25) :
				if not self.running:
					break
		except Exception as e:
			handle(e)

	def stop(self):
		try:
			if self.running:
				log("stop thread")
				self.running = False
				self.th.join()
		except Exception as e:
			handle(e)

	def start(self):
		self.th = Thread(target = self.run)
		self.th.start()
		time.sleep(0.1)
		return self.th.is_alive()
