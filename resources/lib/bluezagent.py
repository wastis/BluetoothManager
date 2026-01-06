from log import log
import xbmcaddon

class BlueZAgentHandler:
	def __init__(self, blueZ):
		self.blueZ = blueZ

	def RequestPinCode(self, message, device):
		log(f"Pairing request from {device}")
		pin = xbmcaddon.Addon().getSettingString("pairingpin")
		self.blueZ.return_func(message, "s", pin)

	def RequestPasskey(self, message, device):
		log(f"Passkey request from {device}")
		pin = xbmcaddon.Addon().getSettingString("pairingpin")
		# Convert PIN to integer passkey (0-999999)
		try:
			passkey = int(pin) if pin.isdigit() else 0
		except:
			passkey = 0
		self.blueZ.return_func(message, "u", passkey)

	def DisplayPasskey(self, message, device, passkey, entered):
		log(f"Display passkey {passkey} for {device} (entered: {entered})")
		# Just acknowledge, no user interaction needed in headless mode
		self.blueZ.return_func(message)

	def DisplayPinCode(self, message, device, pincode):
		log(f"Display PIN {pincode} for {device}")
		# Just acknowledge, no user interaction needed in headless mode
		self.blueZ.return_func(message)

	def RequestConfirmation(self, message, device, passkey):
		log(f"Confirmation request for {device} with passkey {passkey}")
		# Auto-confirm in headless mode
		self.blueZ.return_func(message)

	def RequestAuthorization(self, message, device):
		log(f"Authorization request from {device}")
		# Auto-authorize
		self.blueZ.return_func(message)

	def Release(self, message):
		self.blueZ.return_func(message)

	def AuthorizeService(self, message, device, uuid):
		log(f"Service authorization for {device} UUID {uuid}")
		self.blueZ.return_func(message)

	def Cancel(self, message):
		log("Pairing cancelled")
		self.blueZ.return_func(message)

class BlueZAgent:
	def __init__(self, blueZ):
		self.blueZ = blueZ
		self.agent_path = '/org/kodi/btagent'

	def Start(self):
		value = self.blueZ.call_func("org.bluez.AgentManager1", "/org/bluez", "RegisterAgent", "os", self.agent_path, "KeyboardDisplay")
		log(f"result RegisterAgent {value}")
		self.blueZ.call_func("org.bluez.AgentManager1", "/org/bluez", "RequestDefaultAgent", "o", self.agent_path )
		log(f"result RequestDefaultAgent {value}")

	def Stop(self):
		value = self.blueZ.call_func("org.bluez.AgentManager1", "/org/bluez", "UnregisterAgent", "o", self.agent_path)
		log(f"result UnregisterAgent {value}")
