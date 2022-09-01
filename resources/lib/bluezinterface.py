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

from bluezdbus import BlueZDBus
from bluezobject import BlueZAdapter
from bluezobject import BlueZDevice

class BlueZInterface:
	def __init__(self):
		self.blueZ = BlueZDBus()
		self.blueZ.connect()

		self.adapters = {}
		self.devices = {}

		#self.scan_objects()

	def scan_objects(self):
		self.adapters = {}
		self.devices = {}

		value = self.blueZ.call_func("org.freedesktop.DBus.ObjectManager", "/","GetManagedObjects")
		for key,val in value.items():
			if "org.bluez.Adapter1" in val.keys():
				self.adapters[str(key)] = BlueZAdapter(val["org.bluez.Adapter1"])

			if "org.bluez.Device1" in val.keys():
				self.devices[str(key)] = BlueZDevice(val["org.bluez.Device1"])

	def get_adapter_list(self):
		result = []
		for key in sorted(self.adapters.keys()):
			adapter = self.adapters[key]
			result.append({"Name":adapter.Name, "Powered":adapter.Powered, "Discovering":adapter.Discovering, "Pairable":adapter.Pairable, "id":key, "address":adapter.Address })

		return result

	def get_device_list(self):
		paired = []
		non_paired = []
		unknown = []

		for key in sorted(self.devices.keys()):
			device = self.devices[key]

			if not device.Name:
				unknown.append({"Name":"Unknown", "id":key, "address":device.Address })
				continue

			entry = {"Name":device.Name, "Paired":device.Paired, "Trusted":device.Trusted, "Connected":device.Connected, "Icon":device.Icon, "id":key, "address":device.Address }
			if device.Paired:
				paired.append(entry)
			else:
				non_paired.append(entry)

		return paired + non_paired + unknown

	def adapter_scan_on(self, adapter):
		self.blueZ.call_func("org.bluez.Adapter1", adapter,'StartDiscovery')
		self.blueZ.set("org.bluez.Adapter1",adapter,"Pairable","b",1)

	def adapter_scan_off(self, adapter):
		self.blueZ.call_func("org.bluez.Adapter1", adapter,'StopDiscovery')
		self.blueZ.set("org.bluez.Adapter1",adapter,"Pairable","b",0)

	def adapter_power_on(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Powered","b",1)

	def adapter_power_off(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Powered","b",0)

	def trust(self,device):
		self.blueZ.set("org.bluez.Device1",device,"Trusted","b",1)

	def cancel_trusted(self,device):
		self.blueZ.set("org.bluez.Device1",device,"Trusted","b",0)

	def pair(self,device):
		self.trust(device)
		self.blueZ.call_func("org.bluez.Device1", device,'Pair')

	def remove(self,device):
		self.cancel_trusted(device)
		adapter = self.devices[device].Adapter
		self.blueZ.call_func("org.bluez.Adapter1", adapter,'RemoveDevice',"o",device)

	def connect(self,device):
		self.blueZ.call_func("org.bluez.Device1", device,'Connect')

	def disconnect(self,device):
		self.blueZ.call_func("org.bluez.Device1", device,'Disconnect')
