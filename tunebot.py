#!/usr/bin/python
import sys,time,os,xmpp,common
from pysqlite2 import dbapi2 as sqlite

config=common.getConfig()
bot_jid =  xmpp.protocol.JID(config("//user[@id='bot']/jid/text()")[0].nodeValue + '/tunebot')
bot_passwd =  config("//user[@id='bot']/password/text()")[0].nodeValue
tune_db = sqlite.connect(config("//db/text()")[0].nodeValue,isolation_level=None)

def main():
	client = xmpp.Client(bot_jid.getDomain(), debug=[])
	client.connect()
	client.auth(bot_jid.getNode(), bot_passwd, bot_jid.getResource())
	client.sendInitPresence()
	client.RegisterHandler('message', do_message)
	while step(client):
		pass

def step(c):
	try:
		c.Process(1)
	except KeyboardInterrupt:
		return 0
	return 1

def do_message(client,message):
	if len(message.getTags('event')) > 0 and message.getTags('event')[0].getNamespace() == 'http://jabber.org/protocol/pubsub#event':
		service = message.getFrom().__str__()
		node = message.getTags('event')[0].getTags('items')[0].getAttr('node').__str__()
		artist = title = source = track = ''
		length = 0
		tune = message.getTags('event')[0].getTags('items')[0].getTags('item')[0].getTags('tune')[0]
		if tune.getNamespace() != 'http://jabber.org/protocol/tune':
			return
		for child in tune.getChildren():
			if child.getName() == 'artist':
				artist = child.getData()
			elif child.getName() == 'title':
				title = child.getData()
			elif child.getName() == 'source':
				source = child.getData()
			elif child.getName() == 'track':
				track = child.getData()
			elif child.getName() == 'length':
				length = child.getData()
		query = 'INSERT INTO tunes (service,node, time, artist, title, source, track, length) VALUES (?,?,?,?,?,?,?,?)'
		cur = tune_db.cursor()
		cur.execute(query, (service, node, time.time(), artist, title, source, track, length))
		tune_db.commit()

if __name__=='__main__':
	#main()
	print 'this has been swallowed by presencebot'
