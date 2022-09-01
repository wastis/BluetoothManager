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

from handle import opthandle

class BlueZObject :
	def __init__(self, attr_dict = None):
		for attr in self.attributes: setattr(self, attr, None)
		if attr_dict:
			self.set_attributes(attr_dict)

	def __str__(self):
		r = "{"
		for attr,val in self:
			r = r + " ( %s=%s ) " % (attr,repr(val))
		r = r + "}"
		return r

	def __repr__(self):
		return str(self)

	def __iter__(self):
		for attr in self.attributes:
			val = getattr(self, attr)
			try:  val=val.name
			except AttributeError: pass
			except Exception as e: opthandle(e)
			yield (attr, val)

	def set_attributes(self,attr_dict):
		sig = False
		for key, val in attr_dict.items():
			if key in self.attributes:
				setattr(self, key, val[1])
			if key in self.change_signal:
				sig = True
		return sig

class BlueZAdapter(BlueZObject):
	attributes = ["Address","AddressType","Alias","Class","Discoverable",
				"DiscoverableTimeout","Discovering","Modalias","Name",
				"Pairable","PairableTimeout","Powered"]

	change_signal = ["Discoverable","Discovering","Pairable","Powered"]

class BlueZDevice(BlueZObject):
	attributes = ["Address","AddressType","Name","Alias","Class",
				"Icon","Paired","Trusted","Blocked","LegacyPairing",
				"Connected","Adapter","ServicesResolved"]

	change_signal = ["Paired","Trusted","Connected"]
