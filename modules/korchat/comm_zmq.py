#!/usr/bin/env python3

import threading
import zmq

class P2Pcom(threading.Thread):
	def __init__(self, callback):
		threading.Thread.__init__(self)
		self.context = zmq.Context()
		self.socket = None
		self.isOpened = False
		self.callbackFunc = callback

	def open(self, dest, port="9770"):
		self.socket = self.context.socket(zmq.PAIR)
		if dest:
			# I am client
			self.socket.connect("tcp://%s:%s" % (dest, port))
		else:
			# I am server
			self.socket.bind("tcp://*:%s" % port)
		self.isOpened = True

		self.start()
		return True

	def close(self):
		self.socket.close()
		self.isOpened = False

	def send(self, msg):
		if not self.socket:
			return False
		self.socket.send(msg)
		return True

	def run(self):
		while self.isOpened:
			try:
				msg = self.socket.recv()

				self.callbackFunc(msg)
			except:
				self.isOpened = False
				break