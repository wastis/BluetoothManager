#!/usr/bin/python3

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

import dbussy as dbus
from dbussy import DBUS

class BlueZDBus:
	def __init__(self):
		self.bus_name = 'org.bluez'

	def connect(self):
		self.conn = dbus.Connection.bus_get(DBUS.BUS_SYSTEM, private = False)

	def get_all(self, object_path, interface_name):
		request = dbus.Message.new_method_call \
		(
			destination = dbus.valid_bus_name(self.bus_name),
			path = dbus.valid_path(object_path),
			iface = DBUS.INTERFACE_PROPERTIES,
			method = "GetAll"
		)
		request.append_objects("s", dbus.valid_interface(interface_name))
		reply = self.conn.send_with_reply_and_block(request)
		values = reply.expect_return_objects("a{sv}")[0]
		return values

	def get(self, object_path, interface_name, p_name):
		request = dbus.Message.new_method_call (
			destination = dbus.valid_bus_name(self.bus_name),
			path = dbus.valid_path(object_path),
			iface = DBUS.INTERFACE_PROPERTIES,
			method = "Get"
		)
		request.append_objects("ss", dbus.valid_interface(interface_name),p_name)
		reply = self.conn.send_with_reply_and_block(request)

		return reply.expect_return_objects("v")[0][1]

	def set(self, interface, object_path, p_name, *p_val):
		request = dbus.Message.new_method_call (
			destination = dbus.valid_bus_name(self.bus_name),
			path = object_path,
			iface = DBUS.INTERFACE_PROPERTIES,
			method = "Set"
		)
		request.append_objects("ssv", dbus.valid_interface(interface),p_name, p_val)
		self.conn.send_with_reply_and_block(request)

	def call_func(self, interface, object_path, func, *args):
		request = dbus.Message.new_method_call (
			destination = dbus.valid_bus_name(self.bus_name),
			path = dbus.valid_path(object_path),
			iface = dbus.valid_bus_name(interface),
			method = func
		)
		if len(args) > 0:
			request.append_objects(*args)
		reply = self.conn.send_with_reply_and_block(request).all_objects

		if   len(reply) == 0 :return None
		elif len(reply) == 1 :return reply[0]
		else:	return reply

	def introspect(self, object_path ):
		request = dbus.Message.new_method_call(
				destination = dbus.valid_bus_name(self.bus_name),
				path = object_path,
				iface = DBUS.INTERFACE_INTROSPECTABLE,
				method = "Introspect"
			)

		reply = self.conn.send_with_reply_and_block(request)
		return reply.expect_return_objects("s")[0]
