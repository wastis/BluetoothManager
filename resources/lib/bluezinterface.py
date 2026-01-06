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

from bluezdbus import BlueZDBus
from bluezsignal import BlueZSignal

from bluezobject import BlueZAdapter
from bluezobject import BlueZDevice
from handle import handle
from log import log
from bluezagent import BlueZAgent, BlueZAgentHandler

class BlueZInterface:
	def __init__(self, callback):
		self.callback = callback
		self.blueZ = BlueZDBus()
		self.blueZ.connect()
		self.blueZsignal = BlueZSignal(self,self.on_change)

		self.adapters = {}
		self.devices = {}

		self.Agent = BlueZAgent(self.blueZ)
		self.AgentHandler = BlueZAgentHandler(self.blueZ)

		Thread(target = self.init_bt).start()

	def on_change(self, func, args):
		try:
			method = getattr(self.callback, func)
		except Exception:
			return
		method(*args)

	def init_bt(self):
		try:
			self.scan_objects(False)
			self.blueZsignal.start()
			self.Agent.Start()
			self.on_change("on_start_done",[self.get_adapter_list()])
		except Exception as e:
			handle(e)

	def stop(self):
		self.Agent.Stop()
		self.blueZsignal.stop()

	def scan_objects(self, send_mesg = True):
		self.adapters = {}
		self.devices = {}

		value = self.blueZ.call_func("org.freedesktop.DBus.ObjectManager", "/","GetManagedObjects")
		for key,val in value.items():
			if "org.bluez.Adapter1" in val.keys():
				self.adapters[str(key)] = BlueZAdapter(val["org.bluez.Adapter1"],str(key))

			if "org.bluez.Device1" in val.keys():
				self.devices[str(key)] = BlueZDevice(val["org.bluez.Device1"],str(key))

		if send_mesg:
			self.on_change("on_adapter_scan",[self.get_adapter_list()])
			self.on_change("on_device_scan",[self.get_device_list()])

	def get_adapter_list(self):
		result = []
		for key in sorted(self.adapters.keys()):
			adapter = self.adapters[key]
			result.append(adapter)

		return result

	def get_device_list(self):
		paired = []
		non_paired = []
		unknown = []

		for key in sorted(self.devices.keys()):
			device = self.devices[key]

			if not device.Name:
				unknown.append(device)
			elif device.Paired:
				paired.append(device)
			else:
				non_paired.append(device)

		return paired + non_paired + unknown

	def adapter_scan_on(self, adapter):
		if not self.adapters[adapter].Powered:
			return

		while True:
			try:
				if not self.adapters[adapter].Discovering:
					self.blueZ.call_func("org.bluez.Adapter1", adapter,'StartDiscovery')
				self.blueZ.set("org.bluez.Adapter1",adapter,"Pairable","b",1)
				break
			except Exception as e:
				if e.args[0] == 'org.bluez.Error.NotReady -- Resource Not Ready':
					print("next")
					continue
				else:
					raise(e)

	def adapter_scan_off(self, adapter):
		if self.adapters[adapter].Discovering:
			self.blueZ.call_func("org.bluez.Adapter1", adapter,'StopDiscovery')
		self.blueZ.set("org.bluez.Adapter1",adapter,"Pairable","b",0)

	def adapter_power_on(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Powered","b",1)
		discoverable_on(adapter)

	def adapter_power_off(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Powered","b",0)

	def trust(self,device):
		self.blueZ.set("org.bluez.Device1",device,"Trusted","b",1)

	def cancel_trusted(self,device):
		self.blueZ.set("org.bluez.Device1",device,"Trusted","b",0)
		
	def trustIfPaired(self, device):
		if device.Paired and not device.Trusted:
			self.trust(device.id)

	def pair(self,device):
		# Removed pre-trust to avoid bluez rejection, trust will be set after pairing via autotrust
		self.blueZ.call_func("org.bluez.Device1", device,'Pair')

	def remove(self,device):
		self.cancel_trusted(device)
		adapter = self.devices[device].Adapter
		self.blueZ.call_func("org.bluez.Adapter1", adapter,'RemoveDevice',"o",device)

	def connect(self,device):
		self.blueZ.call_func("org.bluez.Device1", device,'Connect')

	def disconnect(self,device):
		self.blueZ.call_func("org.bluez.Device1", device,'Disconnect')

	def connect_profile(self,device,profile):
		self.blueZ.call_func("org.bluez.Device1", device,'ConnectProfile',"s",profile)

	def disconnect_profile(self,device,profile):
		self.blueZ.call_func("org.bluez.Device1", device,'DisconnectProfile',"s",profile)

	def discoverable_on(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Discoverable","b",1)

	def discoverable_off(self, adapter):
		self.blueZ.set("org.bluez.Adapter1",adapter,"Discoverable","b",0)

	def discoverable(self, adapter):
		log("discoverable adapter %s" % str(adapter))
		return self.blueZ.get(adapter, "org.bluez.Adapter1", "Discoverable")

	def RequestPinCode(self, message, device):
		log("Pairing request from %s" % device)
		self.AgentHandler.RequestPinCode(message, device)

	def RequestPasskey(self, message, device):
		log("Passkey request from %s" % device)
		self.AgentHandler.RequestPasskey(message, device)

	def DisplayPasskey(self, message, device, passkey, entered):
		log("Display passkey for %s" % device)
		self.AgentHandler.DisplayPasskey(message, device, passkey, entered)

	def DisplayPinCode(self, message, device, pincode):
		log("Display PIN for %s" % device)
		self.AgentHandler.DisplayPinCode(message, device, pincode)

	def RequestConfirmation(self, message, device, passkey):
		log("Confirmation request from %s" % device)
		self.AgentHandler.RequestConfirmation(message, device, passkey)

	def RequestAuthorization(self, message, device):
		log("Authorization request from %s" % device)
		self.AgentHandler.RequestAuthorization(message, device)

	def Release(self, message):
		self.AgentHandler.Release(message)

	def AuthorizeService(self, message, device, uuid):
		self.AgentHandler.AuthorizeService(message, device, uuid)

	def Cancel(self, message):
		self.AgentHandler.Cancel(message)
