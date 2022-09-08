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

import xbmcgui
import xbmcaddon
from xbmcgui import ListItem

from log import log
from handle import handle
from handle import opthandle
from threading import Thread
from time import sleep
from dbussy import DBusError

from bluezinterface import BlueZInterface

addon = xbmcaddon.Addon()
def tr(lid):
	return addon.getLocalizedString(lid)

class DiscoverGui(  xbmcgui.WindowXMLDialog  ):
	def __init__( self, *_args, **kwargs ):
		self.cwd = _args[1]
		self.remove = kwargs["remove"]

		self.icon_path = self.cwd + "resources/skins/Default/media/"

		self.action_in_progress = False
		self.adapter = None

		self.items = []
		self.items_by_id = {}

	def onInit( self ):
		self.list = self.getControl(2000)
		self.radio = self.getControl(2010)
		self.label = self.getControl(2021)

		#rotating images
		self.discover = self.getControl(1000)
		self.blueset = self.getControl(1001)

		self.label.setLabel(tr(32004))

		self.list.reset()
		self.rot = 0

		Thread(target = self.animate).start()
		self.bluez = BlueZInterface(self)

	def animate(self):
		# the rotating images
		self.running = True
		while(self.running):
			self.rot += 1
			if self.rot == 6:
				self.rot = 0

			self.discover.setImage(self.icon_path + "rotation/rot%d.png" % self.rot)
			self.blueset.setImage(self.icon_path + "rotation/rot%d.png" % self.rot)
			sleep(0.02)

	#
	# dialog config
	#

	def config_no_adapter(self):
		log("config_no_adapter")
		self.label.setLabel(tr(32008))
		self.blueset.setVisible(False)
		self.discover.setVisible(False)
		self.radio.setEnabled(False)
		self.radio.setLabel("")
		self.adapter = None

	def config_adapter(self, adapter):
		log("config_adapter")
		self.adapter = adapter
		self.radio.setLabel(self.adapter.Name)
		self.radio.setEnabled(True)
		log("powered %s" % adapter.Powered)
		if adapter.Powered:
			self.config_power_on()
		else:
			self.config_power_off()

	def config_power_off(self):
		log("config_power_off")
		try:
			self.bluez.adapter_scan_off(self.adapter.id)
		except Exception as e:
			opthandle(e)
		self.radio.setSelected(False)
		self.discover.setVisible(False)
		self.label.setLabel(tr(32004))

	def config_power_on(self):
		log("config_power_on")
		self.radio.setSelected(True)
		if self.remove:
			self.discover.setVisible(False)
			self.label.setLabel(tr(32010))
		else:
			try:
				self.bluez.adapter_scan_on(self.adapter.id)
			except Exception as e:
				opthandle(e)
			self.label.setLabel(tr(32003))

	def config_discover(self, adapter):
		log("config_discover")
		self.discover.setVisible(adapter.Discovering)

	#
	#	device list
	#

	def get_name_status(self, device):
		if device.Icon is None and  \
			not xbmcaddon.Addon().getSettingBool("showunknown"):
				log("no icon, skip %s" % device.Name)
				return None,None

		name = device.Name
		if name is None:
			name = tr(32007)
			status = device.Address
		else:
			status = tr(32002)
			if device.Connected:
				status = tr(32000)
			elif device.Paired:
				status = tr(32001)
			elif self.remove:
				log("skip remove")
				return None,None
		return name,status

	def add_to_list(self, device, name, status):
		log("create item: %s" % name)
		item = ListItem(name, status)
		item.setArt({ "icon": self.icon_path + "blueicons/%s.png" % device.Icon })

		self.list.addItem(item)
		self.items_by_id[device.id] = (item,device,len(self.items))
		self.items.append((item,device))

	def fill_device_list(self):
		log("fill_device_list")
		try:
			selid = self.items[self.list.getSelectedPosition()][1].id
		except IndexError:
			selid = None
		except Exception as e:
			selid = None
			handle(e)
		log("fill_device_list 2")
		self.list.reset()
		self.items = []
		self.items_by_id = {}

		if self.adapter is None or self.adapter.Powered is False:
			self.blueset.setVisible(False)
			return
		log("fill_device_list 3")

		for device in self.bluez.get_device_list():
			name,status = self.get_name_status(device)
			if name is None:
				continue

			self.add_to_list(device,name,status)

			if (selid is not None) and (selid in self.items_by_id.keys()):
				self.list.selectItem(self.items_by_id[selid][2])
			else:
				self.list.selectItem(0)
		self.blueset.setVisible(False)

	#
	# handle messages from bluez
	#

	def on_adapter_new(self,objid):
		log("on_adapter_new")
		if self.adapter is None:
			self.adapter = self.bluez.adapters[objid]
			self.config_adapter(self.adapter)
			self.bluez.adapter_scan_on(self.adapter.id)
			self.setFocusId(2010);

	def on_adapter_remove(self,objid):
		log("on_adapter_remove")
		if self.adapter.id == objid:
			self.adapter = None
			self.config_no_adapter()

	def on_device_new(self,objid):
		log("on_device_new")
		if objid in self.items_by_id.keys():
			return
		device = self.bluez.devices[objid]

		name,status = self.get_name_status(device)
		if name is None:
			return

		self.add_to_list(device,name,status)

	def on_device_remove(self,objid):
		log("on_device_remove")
		try:
			index = self.items_by_id[objid][2]
		except KeyError:
			return

		self.items.pop(index)
		self.items_by_id.pop(objid,None)
		self.list.removeItem(index)

	def on_adapter_change(self, objid, changes):
		log("on_adapter_change %s" % changes)
		adapter = self.bluez.adapters[objid]
		if self.adapter is None:
			return
		if adapter.id != self.adapter.id:
			return
		if "Powered" in changes:
			self.config_adapter(adapter)
			self.fill_device_list()
		if "Discovering" in changes:
			self.config_discover(adapter)

	def on_device_change(self, objid, _):
		log("on_device_change")
		item,device,_ = self.items_by_id[objid]
		name,status = self.get_name_status(device)
		if name is None:
			return
		item.setLabel2(status)

	def on_adapter_scan(self, adapters):
		log("on_adapter_scan")
		if not adapters:
			self.config_no_adapter()
		else:
			self.config_adapter(adapters[0])

	def on_device_scan(self, _):
		log("on_device_scan")
		self.fill_device_list()

	def on_start_done(self, adapters):
		log("on_start_done")
		#called after bluez initialization
		if not adapters:
			log("has no adapter")
			self.config_no_adapter()
		else:
			log("has adapter")
			self.config_adapter(adapters[0])
		self.fill_device_list()

	#
	# dialog action handling
	#

	def setEnabled(self, enabled):
		self.list.setEnabled(enabled)
		self.radio.setEnabled(enabled)

	def end_gui(self):
		log("end_gui")
		try:
			self.running = False
			self.bluez.adapter_scan_off(self.adapter.id)
		except Exception as e:
			handle(e)

		self.bluez.stop()
		self.close()

	def on_list_click(self):
		log("on_list_click")
		if not self.running:
			return

		self.setEnabled(False)

		self.action_in_progress = True
		self.discover.setVisible(False)
		self.blueset.setVisible(True)
		try:
			device = self.items[self.list.getSelectedPosition()][1]

			if device.Paired:
				if self.remove:
					self.bluez.remove(device.id)
				else:
					if device.Connected:
						self.bluez.disconnect(device.id)
					else:
						self.bluez.connect(device.id)
			else:
				self.bluez.pair(device.id)
				self.bluez.connect(device.id)
		except DBusError as e:
			log(e.args[0])
		except Exception as e:
			opthandle(e)

		self.blueset.setVisible(False)
		self.discover.setVisible(True)
		self.setEnabled(True)
		self.setFocusId(2000);
		log("on_list_click: done")

	def on_radio_click(self):
		log("on_radio_click")
		if not self.running:
			return
		try:
			if self.adapter is None:
				return

			self.blueset.setVisible(True)
			if self.adapter.Powered:
				self.bluez.adapter_power_off(self.adapter.id)
			else:
				self.bluez.adapter_power_on(self.adapter.id)
				self.bluez.adapter_scan_on(self.adapter.id)

		except Exception as e:
			opthandle(e)

	def ok_pressed(self):
		focus = self.getFocusId();
		if focus == 3000:
			self.end_gui()
		if focus == 2000:
			self.on_list_click()
		if focus == 2010:
			self.on_radio_click()

	def onAction( self, action ):
		log("action id %s" % action.getId())

		#OK pressed
		if action.getId() in [7, 100]:
			self.ok_pressed()

		#Cancel
		if action.getId() in [92,10,18]:
			self.end_gui()
