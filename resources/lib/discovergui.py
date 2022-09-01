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
from threading import Thread, Lock
from time import sleep

from bluezsignal import BlueZSignal
from bluezinterface import BlueZInterface

addon = xbmcaddon.Addon()
def tr(lid):
	return addon.getLocalizedString(lid)

class DiscoverGui(  xbmcgui.WindowXMLDialog  ):
	def __init__( self, *_args, **kwargs ):
		self.cwd = _args[1]
		self.remove = kwargs["remove"]

		self.icon_path = self.cwd + "resources/skins/Default/media/"
		self.lock = Lock()

		self.adapter_id = None
		self.bluez = BlueZInterface()
		self.bzs = BlueZSignal(self.bluez, self.on_change)

	def onInit( self ):
		self.list = self.getControl(2000)
		self.discover = self.getControl(1000)
		self.blueset = self.getControl(1001)
		self.radio = self.getControl(2010)
		self.label = self.getControl(2021)

		self.label.setLabel(tr(32004))

		self.list.reset()
		self.rot = 0

		Thread(target = self.rotate).start()
		Thread(target = self.init_bt).start()

	def rotate(self):
		self.running = True
		while(self.running):
			self.rot += 1
			if self.rot == 6:
				self.rot = 0

			self.discover.setImage(self.icon_path + "rotation/rot%d.png" % self.rot)
			self.blueset.setImage(self.icon_path + "rotation/rot%d.png" % self.rot)
			sleep(0.02)

	def init_bt(self):
		log("start bt")

		try:
			if self.init_adapter():
				self.on_change()
			self.bzs.start()

		except Exception as e:
			handle(e)

	def init_adapter(self):
		log("init_adapter")
		self.bluez.scan_objects()

		adapters = self.bluez.get_adapter_list()
		if not adapters:
			log("no adapter found")
			self.label.setLabel(tr(32008))
			self.blueset.setVisible(False)
			self.discover.setVisible(False)
			self.radio.setEnabled(False)
			self.radio.setLabel("")
			self.adapter_id = None
			return False

		else:
			adapter = adapters[0]
			self.adapter_id = adapter["id"]
			self.radio.setLabel(adapter["Name"])
			self.radio.setEnabled(True)

			if adapter["Powered"]:
				self.radio.setSelected(True)
				if not self.remove:
					try:
						self.bluez.adapter_scan_on(self.adapter_id)
					except Exception as e:
						opthandle(e)
					self.discover.setVisible(True)
					self.label.setLabel(tr(32003))
				else:
					self.discover.setVisible(False)
					self.label.setLabel(tr(32010))

			else:
				self.radio.setSelected(False)
				self.discover.setVisible(False)
				self.label.setLabel(tr(32004))

			self.blueset.setVisible(False)
			return True

	def get_selected(self):
		try:
			item = self.list.getSelectedItem()
		except Exception:
			selected = "None"
		else:
			if item is None:
				selected = "None"
			else:
				selected = item.getLabel()
				if selected == tr(32007):
					selected = item.getLabel2()
		return selected

	def on_change(self):
		self.lock.acquire()
		log("on_change")

		try:
			if not self.adapter_id:
				if not self.init_adapter():
					self.lock.release()
					return
			elif not self.bluez.adapters:
				#adapter removed
				if not self.init_adapter():
					self.lock.release()
					return

		except Exception as e:
			handle(e)
			self.lock.release()
			return

		if not self.radio.isSelected():
			self.list.reset()
			self.lock.release()
			return

		selected = self.get_selected()

		try:
			self.devices = self.bluez.get_device_list()
			self.list.reset()
		except Exception as e:
			handle(e)
			self.lock.release()
			return

		try:
			self.device_lookup = {}
			index = 0
			sel_index = 0

			for device in self.devices:
				if "Icon" in device:
					icon = device["Icon"]
				else:
					icon = None

				if not icon and  \
					not xbmcaddon.Addon().getSettingBool("showunknown"):
						log("no icon, skip " + device["Name"])
						continue

				name = device["Name"]
				log("disc: found device: " + name)

				if name == "Unknown":
					name = tr(32007)
					status = device["address"]
					key = status
					if status == selected:
						sel_index = index
				else:
					key = name
					if name == selected:
						sel_index = index

					status = tr(32002)
					if device["Connected"]:
						status = tr(32000)
					elif device["Paired"]:
						status = status = tr(32001)
					elif self.remove:
						log("skip remove")
						continue

				log("create item: " + name)
				item = ListItem(name, status)
				item.setArt({ "icon": self.icon_path + "blueicons/%s.png" % icon })
				index = index + 1

				self.list.addItem(item)
				self.device_lookup[key]= device

			self.list.selectItem(sel_index)
		except Exception as e:
			handle(e)

		self.lock.release()

	def end_gui(self):
		try:
			self.running = False
			if self.radio.isSelected() and not self.remove:
				self.bluez.adapter_scan_off(self.adapter_id)
			self.bzs.stop()
		except Exception as e:
			handle(e)

		self.close()

	def on_list_click(self):
		self.blueset.setVisible(True)
		try:
			device = self.device_lookup[self.get_selected()]
			if device["Paired"]:
				if self.remove:
					self.bluez.remove(device["id"])
				else:
					if device["Connected"]:
						self.bluez.disconnect(device["id"])
					else:
						log("connect: " + device["Name"])
						self.bluez.connect(device["id"])
			else:
				self.bluez.pair(device["id"])
				self.bluez.connect(device["id"])
		except Exception as e:
			opthandle(e)

		self.bluez.scan_objects()
		self.on_change()
		self.blueset.setVisible(False)
		self.setFocusId(2000);

	def on_radio_click(self):
		try:
			if self.radio.isSelected():
				self.bluez.adapter_power_on(self.adapter_id)
				if not self.remove:
					self.discover.setVisible(True)
					self.label.setLabel(tr(32003))
					self.bluez.adapter_scan_on(self.adapter_id)
				else:
					self.label.setLabel(tr(32010))

				self.bluez.scan_objects()
				self.on_change()
			else:
				self.list.reset()
				if not self.remove:
					self.bluez.adapter_scan_off(self.adapter_id)
				self.bluez.adapter_power_off(self.adapter_id)
				self.discover.setVisible(False)
				self.label.setLabel(tr(32004))

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
		#OK pressed
		if action.getId() in [7, 100]:
			self.ok_pressed()

		#Cancel
		if action.getId() in [92,10]:
			self.end_gui()
