#!/usr/bin/python
import sys,os,mpdclient,xmpp,time,md5
from optparse import OptionParser
sys.path.append('..')
import common

def main():
	parser = OptionParser()
	parser.add_option("-b", "--bot", dest="bot", default="me", help="IDREF of bot in config file")
	parser.add_option("-p", "--pubsub", dest="pubsub", default="tune", help="IDREF of pubsub in config file")
	(options, args) = parser.parse_args()

	config = common.getConfig()
	try:
		bot_jid=xmpp.protocol.JID(config("users/user[@id='%s']/jid/text()"%(options.bot))[0].nodeValue + '/tunepub/mpd')
		bot_passwd = config("users/user[@id='%s']/password/text()"%(options.bot))[0].nodeValue
		pubsub_service = config("pubsub/node[@id='%s']/service/text()"%(options.pubsub))[0].nodeValue
		pubsub_id = config("pubsub/node[@id='%s']/id/text()"%(options.pubsub))[0].nodeValue
	except:
		print 'Could not find proper nodes in config file (Looked for bot \'%s\' and pubsub node \'%s\')'%(options.bot, options.pubsub)
		sys.exit()

	c = None
	last_song = ''
	client = xmpp.Client(bot_jid.getDomain(), debug=[])
	client.connect()
	client.auth(bot_jid.getNode(), bot_passwd)
	while True:
		if c == None:
			try:
				c = mpdclient.MpdController(host="localhost", port=6600)
			except:
				c = None
		if c == None:
			mpd_song = False
		else:
			try:
				mpd_song = c.getCurrentSong()
			except:
				c = None
				mpd_song = False
		try:
			if mpd_song == False:
				raise Exception
			status = c.getStatus()
			title = mpd_song.title
			length = status.totalTime
			artist = mpd_song.artist
			source = mpd_song.path
			if artist == '' and title.count(' - ') > 0:
				parts = title.split(' - ')
				artist = parts[0]
				title = parts[1]
			if last_song != title:
				escape = xmpp.simplexml.XMLescape
				node_id = md5.md5(time.time().__str__()).hexdigest()
				node_xml = "<iq type='set' from='%s' to='%s' id='%s'><pubsub xmlns='http://jabber.org/protocol/pubsub'><publish node='%s'><item id='current'><tune xmlns='http://jabber.org/protocol/tune'><artist>%s</artist><title>%s</title><source>%s</source><length>%s</length></tune></item></publish></pubsub></iq>"%(bot_jid,pubsub_service,node_id,pubsub_id,escape(artist),escape(title),escape(source),length)
				tune_node = xmpp.simplexml.XML2Node(node_xml)
				tune_iq = xmpp.protocol.Iq(node=tune_node)
		except:
			title = 'Stopped'
			if last_song != title:
				node_id = md5.md5(time.time().__str__()).hexdigest()
				node_xml = "<iq type='set' from='%s' to='%s' id='%s'><pubsub xmlns='http://jabber.org/protocol/pubsub'><publish node='%s'><item id='current'><tune xmlns='http://jabber.org/protocol/tune' /></item></publish></pubsub></iq>"%(bot_jid,pubsub_service,node_id,pubsub_id)
				tune_node = xmpp.simplexml.XML2Node(node_xml)
				tune_iq = xmpp.protocol.Iq(node=tune_node)
		if last_song != title:
			client.send(tune_iq)
		last_song = title
		try:
			time.sleep(5)
		except KeyboardInterrupt:
			sys.exit()

if __name__=='__main__':
	main()
