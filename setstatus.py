#!/usr/bin/python
import sys,xmpp,common
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-b", "--bot", dest="bot", default="me", help="IDREF of bot in config file")
parser.add_option("-m", "--me", dest="me", default="me", help="IDREF of human in config file")
parser.add_option("-r", "--resource", dest="resource", help="IDREF of human in config file")
parser.add_option("-s", "--status", type="choice",dest="status", default="online", choices=("chat","online","away","xa","dnd","invisible","offline"),help="Status")
parser.add_option("-p", "--priority", type="int",dest="priority", default="5", help="Priority")
parser.add_option("-e", "--message", dest="message", default="", help="Status Message")
(options, args) = parser.parse_args()

config = common.getConfig()
try:
	bot_jid=xmpp.protocol.JID(config("//user[@id='%s']/jid/text()"%(options.bot))[0].nodeValue + '/statussetter')
	bot_passwd = config("//user[@id='%s']/password/text()"%(options.bot))[0].nodeValue
	me_jid=xmpp.protocol.JID(config("//user[@id='%s']/jid/text()"%(options.me))[0].nodeValue + '/%s'%options.resource)
except:
	print 'Could not find proper nodes in config file (Looked for bot \'%s\')'%(options.bot)
	sys.exit();

def main():
	client = xmpp.Client(bot_jid.getDomain(),debug=[])
	client.connect()
	client.auth(bot_jid.getNode(), bot_passwd)
	# client.sendInitPresence()
	node_xml = """
		<iq type=\"set\" to=\"%s\" id=\"aac8a\" >
		<command xmlns=\"http://jabber.org/protocol/commands\" node=\"http://jabber.org/protocol/rc#set-status\" >
		<x xmlns=\"jabber:x:data\" type=\"submit\" >
		<field type=\"hidden\" var=\"FORM_TYPE\" >
		<value>http://jabber.org/protocol/rc</value>
		</field>
		<field type=\"list-single\" var=\"status\" >
		<value>%s</value>
		</field>
		<field type=\"text-single\" var=\"status-priority\" >
		<value>%s</value>
		</field>
		<field type=\"text-multi\" var=\"status-message\" >
		<value>%s</value>
		</field>
		</x>
		</command>
		</iq>
	"""%(me_jid,options.status, options.priority, options.message)
	status_node = xmpp.simplexml.XML2Node(node_xml)
	status_iq = xmpp.protocol.Iq(node=status_node)
	client.send(status_iq)

if __name__=="__main__":
	main()
