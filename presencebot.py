#!/usr/bin/python
import sys,os,xmpp,common
from time import time
from optparse import OptionParser
from pysqlite2 import dbapi2 as sqlite

parser = OptionParser()
parser.add_option("-b", "--bot", dest="bot", default="bot", help="IDREF of bot in config file")
(options, args) = parser.parse_args()

config = common.getConfig()
try:
	bot_jid=xmpp.protocol.JID(config("//user[@id='%s']/jid/text()"%(options.bot))[0].nodeValue + '/presencebot')
	bot_passwd = config("//user[@id='%s']/password/text()"%(options.bot))[0].nodeValue
except:
	print 'Could not find proper nodes in config file (Looked for bot \'%s\')'%(options.bot)
	sys.exit();

presence_db = sqlite.connect(config("//db/text()")[0].nodeValue,isolation_level=None)
tune_db = sqlite.connect(config("//db/text()")[0].nodeValue,isolation_level=None)

def main():
	cur = presence_db.cursor()
	# cur.execute('DELETE FROM presence')
	client = xmpp.Client(bot_jid.getDomain(), debug=[])
	client.connect()
	client.auth(bot_jid.getNode(), bot_passwd, bot_jid.getResource())
	client.sendInitPresence()
	client.RegisterHandler('presence', do_presence)
	client.RegisterHandler('message', do_message)
	while step(client):
		pass
	print 'Presensebot has exited'

def step(c):
	try:
		r = c.Process(1)
	except KeyboardInterrupt:
		return 0
	return r

def do_presence(client,message):
		node = unicode(message.getFrom().getNode()).encode('utf-8')
		domain = unicode(message.getFrom().getDomain()).encode('utf-8')
		resource = unicode(message.getFrom().getResource()).encode('utf-8')
		priority = unicode(message.getPriority()).encode('utf-8')
		type = unicode(message.getType()).encode('utf-8')
		status = unicode(message.getStatus()).encode('utf-8')
		show = unicode(message.getShow()).encode('utf-8')

		cur = presence_db.cursor()
		cur.execute('select count(*) from presence where node=? AND domain=? AND resource=?',(node,domain,resource))
		if cur.fetchone()[0] >= 1:
			query = 'UPDATE presence SET priority=?,type=?,status=?,show=? WHERE node=? AND domain=? AND resource=?'
			cur.execute(query, (priority,type,status,show,node,domain,resource))
		else:
			query = 'INSERT INTO presence (node,domain,resource,priority,type,status,show) VALUES (?,?,?,?,?,?,?)'
			cur = presence_db.cursor()
			cur.execute(query, (node,domain,resource,priority,type,status,show))

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
		cur.execute(query, (service, node, time(), artist, title, source, track, length))
		tune_db.commit()

if __name__=='__main__':
	main()
