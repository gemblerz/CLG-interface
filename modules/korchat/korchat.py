#!/usr/bin/env python3

import curses
import dialog
import uuid
import pickle
from comm_zmq import P2Pcom

initial = medial = final = potential_final = ' '
a = b = 0
# formular = (((initial)*588)+((medial)*28)+(final))+44032

order = 0
cho_keymap = {
	'r' : 0,
	'R' : 1,
	's' : 2,
	'e' : 3,
	'E' : 4,
	'f' : 5,
	'a' : 6,
	'q' : 7,
	'Q' : 8,
	't' : 9,
	'T' : 10,
	'd' : 11,
	'w' : 12,
	'W' : 13,
	'c' : 14,
	'z' : 15,
	'x' : 16,
	'v' : 17,
	'g' : 18    
}

jung_keymap = {
    'k' : 0,
    'o' : 1,
    'i' : 2,
    'O' : 3,
    'j' : 4,
    'p' : 5,
    'u' : 6,
    'P' : 7,
    'h' : 8,
    'hk' : 9,
    'ho' : 10,
    'hl' : 11,
    'y' : 12,
    'n' : 13,
    'nj' : 14,
    'np' : 15,
    'nl' : 16,
    'b' : 17,
    'm' : 18,
    'ml' : 19,
    'l' : 20
}

jong_keymap = {
	'' : 0,
	'r' : 1,
	'R' : 2,
	'rt' : 3,
	's' : 4,
	'sw' : 5,
	'sg' : 6,
	'e' : 7,
	'f' : 8,
	'fr' : 9,
	'fa' : 10,
	'fq' : 11,
	'ft' : 12,
	'fx' : 13,
	'fv' : 14,
	'fg' : 15,
	'a' : 16,
	'q' : 17,
	'qt' : 18,
	't' : 19,
	'T' : 20,
	'd' : 21,
	'w' : 22,
	'c' : 23,
	'z' : 24,
	'x' : 25,
	'v' : 26,
	'g' : 27
}

entry = [cho_keymap, jung_keymap, jong_keymap]
jaum = ['q', 'Q', 'w', 'W', 'e', 'E', 'r', 'R', 't', 'T',
		'a', 's', 'd', 'f',
		'z', 'x', 'c', 'v']

moum = ['k', 'i', 'j', 'u', 'h', 'y', 'n', 'b', 'm', 'l', 'o', 'p',
		'ho', 'hp', 'nj']

class answk(object):
	def __init__(self, space = -1):
		self.jamo = ['', '', '']
		self.space = space

	def next(self):
		for i in range(0, 3):
			if self.jamo[i] == '':
				return i
		return len(self.jamo) - 1

	def insert(self, ch):
		if self.space > 0:
			return False

		next_idx = self.next()
		m = entry[next_idx]
		if next_idx == 2:
			if self.jamo[2] == '':
				t = self.jamo[1]
				t += ch
				# support two chars in jungsung
				if t in jung_keymap:
					self.jamo[1] = t
					return True
			# support two chars in jongsung
			else:
				t = self.jamo[2]
				t += ch
				if t in jong_keymap:
					self.jamo[2] = t
					return True
				else:
					return False

		if ch in m:
			self.jamo[next_idx] = ch
			return True
		return False
		
	def rollback(self):
		if self.jamo[2] != '':
			r = self.jamo[2][len(self.jamo[2])-1]
			self.jamo[2] = self.jamo[2][:-1]
			return r

	def cnffur(self):
		if self.space > 0:
			return chr(32)
		han = 0
		try:
			i = cho_keymap[self.jamo[0]]
			m = jung_keymap[self.jamo[1]]
			f = jong_keymap[self.jamo[2]]
			han = (((i)*588)+((m)*28)+(f))+44032
		except Exception as e:
			# print("%s %s %s haha" % (self.jamo[0], self.jamo[1], self.jamo[2]))
			return ""
		return chr(han)

	def __str__(self):
		return self.cnffur()

class korchat(object):
	def __init__(self):
		self.chat_list = []
		self.comm_handler = P2Pcom(self.comm_callback)
		self.scr = curses.initscr()
		self.kill = False

		curses.cbreak(); self.scr.keypad(1)
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
 
		self.width   = self.scr.getmaxyx()[1]
		self.height  = self.scr.getmaxyx()[0]

		self.MAX_CHAT_SIZE = self.height - 8
		self.chat_list_x = 4
		self.chat_list_y = 2
		self.ID = str(uuid.uuid4())
		

	def comm_callback(self, msg):
		# msg = msg.decode('utf-8')
		data = self.deserialize(msg)

		self.chat_list.append(data)
		self.refresh()

	def close(self):
		self.comm_handler.close()
		self.kill = True
		curses.nocbreak(); self.scr.keypad(0)
		curses.endwin()

	def serialize(self, data):
		return pickle.dumps(data)

	def deserialize(self, data):
		return pickle.loads(data)

	def refresh(self):
		l = len(self.chat_list)
		if len(self.chat_list) > self.MAX_CHAT_SIZE:
			self.chat_list = self.chat_list[l - self.MAX_CHAT_SIZE:]

		self.scr.border()
		self.scr.addstr(1, int(self.width / 2) - 6, "korchat v0.1")
		self.scr.addstr(2, 2, "@CHAT:")
		x = self.chat_list_x
		y = self.chat_list_y
		for line in self.chat_list:
			if 'ERROR' in line[0]:
				self.scr.addstr(x, y, line[0], curses.color_pair(1))
			else:
				if line[1] == self.ID:
					y = int(self.width / 2)
				else:
					y = self.chat_list_y
				self.scr.addstr(x, y, line[0])
			x += 1

		self.scr.addstr(self.height - 3, 2, "Type message here; 'exit' to quit")
		self.scr.refresh()

	def parse_command(self, cmd):
		if 'connect' in cmd:
			try:
				addr = cmd.split(' ')[1]
				ret = self.comm_handler.open(addr)
			except Exception as e:
				err = "Conn. Err. %s" % str(e)
				self.chat_list.append(err)

	def loop(self):
		hangul = []

		while not self.kill:
			self.refresh()
			
			sentence = self.scr.getstr(self.height - 2, 2, 60).decode('latin-1')
			# sentence = sentence.strip('\n')
			if sentence == '':
				continue
			elif sentence == 'exit':
				break

			# Take care of commands
			if sentence[0] == '@':
				self.parse_command(sentence[1:])
				continue

			hangul.clear()
			hangul.append(answk())
			
			ch = sentence[0]
			sentence = sentence[1:]
			fail_cnt = 3
			while True:
				if ch == ' ':
					ch = ''
					hangul.append(answk(1))
					hangul.append(answk())
				else:
					last_answk = hangul[-1]
					ret = last_answk.insert(ch)
					if ret:
						ch = ''
						hangul[-1] = last_answk
					else:
						if ch in jung_keymap:
							pre = last_answk.rollback()
							new = answk()
							new.insert(pre)
							hangul.append(new)
						else:
							hangul.append(answk())
						fail_cnt -= 1
						if fail_cnt < 0:
							break
						continue
				
				if not sentence:
					break
				fail_cnt = 3
				ch += sentence[0]
				sentence = sentence[1:]

			result = ""
			for gkswk in hangul:
				rmfwk = gkswk.cnffur()
				if rmfwk != "":
					result += rmfwk
			if fail_cnt < 0:
				result = "ERROR: COULD NOT INTERPRET"
			self.chat_list.append([result, self.ID])
			self.comm_handler.send(self.serialize([result, self.ID]))

if __name__ == '__main__':
	k = korchat()
	try:
		k.loop()
	except (KeyboardInterrupt, Exception) as e:
		raise

	k.close()