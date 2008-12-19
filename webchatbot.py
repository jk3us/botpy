#!/usr/bin/python
import sys,common
from time import time,sleep
from xmpp import protocol,Client
from threading import Thread
from optparse import OptionParser
from pysqlite2 import dbapi2 as sqlite

parser = OptionParser()
parser.add_option("-b", "--bot", dest="bot", default="bot", help="IDREF of bot in config file")
parser.add_option("-m", "--me", dest="me", default="me", help="IDREF of human in config file")
(options, args) = parser.parse_args()

config=common.getConfig()
try:
	bot_jid =  protocol.JID(config("//user[@id='%s']/jid/text()"%(options.bot))[0].nodeValue)
	bot_passwd =  config("//user[@id='%s']/password/text()"%(options.bot))[0].nodeValue
	human_jid =  protocol.JID(config("//user[@id='%s']/jid/text()"%(options.me))[0].nodeValue)
except:
	print 'Could not find proper nodes in config file (Looked for bot \'%s\', \'%s\')'%(options.bot, options.me)
	print sys.exc_info()[0]
	sys.exit();

class bot(Thread):
	connected = False
	def __init__(self,resource):
		self.resource=resource
		Thread.__init__(self)
	def getMessage(self,client,message):
		send_jid = protocol.JID(message.getFrom())
		rcpt_jid = protocol.JID(message.getTo())
		if send_jid.bareMatch(human_jid):
			cur = con.cursor()
			cur.execute('INSERT INTO messages (resource_id, tofrom, time, message) VALUES (?, 0, ?, ?)', (rcpt_jid.getResource(), time(),message.getBody()))
		self.activity = time()
	def makeBot(self,resource):
		client = Client(bot_jid.getDomain(), debug=[])
		client.connect()
		client.auth(bot_jid.getNode(),bot_passwd,self.resource)
		client.sendInitPresence()
		client.RegisterHandler('message',self.getMessage)
		return client
	def sendMessage(self,message):
		self.client.send(protocol.Message(human_jid,message,'chat'))
		self.activity = time()
	def run(self):
		self.client = self.makeBot(self.resource)
		self.connected = True;
		self.activity = time()


con = sqlite.connect(config("//db/text()")[0].nodeValue, isolation_level=None)
con.row_factory = sqlite.Row
cur = con.cursor()
cur.execute('DELETE FROM messages')
bots = {}
last_time = 0
last_clear = 0
while True:
	cur = con.cursor()
	cur.execute('SELECT * FROM messages WHERE tofrom=1 AND time > ? ORDER BY time ASC',(last_time,))
	for row in cur:
		resource = row['resource_id']
		last_time = max(last_time,row['time'])
		if not bots.has_key(resource):
			bots[resource] = bot(resource)
			bots[resource].start()
		while not bots[resource].connected:
			sleep(1)
		bots[resource].sendMessage(row['message'])
	for resource,abot in bots.items():
		if abot.client.Process() == 0:
			del bots[resource]
		if bots[resource].activity < time() - 300:
			bots[resource].client.disconnect()
			del bots[resource]
	if last_clear < time() - 60:
		cur = con.cursor()
		cur.execute('delete from messages where resource_id not in (select distinct(resource_id) FROM messages WHERE time > ?)',(time()-3600,))
		last_clear = time()
	sleep(.25)
