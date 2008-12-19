#!/usr/bin/python
# $Id: xsend.py,v 1.1 2004/06/20 09:45:09 snakeru Exp $
import sys,os,time,cgi
from pysqlite2 import dbapi2 as sqlite
from optparse import OptionParser
from xml import xpath
from xml.dom.minidom import parseString,parse

def getConfig():
	homedir = os.path.expanduser('~');
	config = parse('%s/.botpy/config.xml'%(homedir))
	config.documentElement.normalize()
	return lambda x:xpath.Evaluate(x,config.documentElement)
	
config=getConfig()
db_file = config("//db/text()")[0].nodeValue;

def send(resource,text):
	if resource == 'debug':
		return
	con = sqlite.connect(db_file,isolation_level=None);
	cur = con.cursor()
	query = 'INSERT INTO messages (resource_id, tofrom, time, message) VALUES (?, 1, ?, ?)'
	cur.execute(query, (resource, time.time(),text))
	con.commit()
	con.close()

def getConversation(resource,last=0):
	send('debug','getting Conversation')
	con = sqlite.connect(db_file,isolation_level=None);
	send('debug','db start')
	con.row_factory = sqlite.Row
	start = time.time()
	if last > 0:
		while True:
			cur = con.cursor()
			cur.execute('SELECT count(time) FROM messages WHERE resource_id=? AND round(time) > round(?)', (resource,last))
			news = cur.fetchone()[0]
			if (news > 0) or (start + 10 <= time.time()):
				break
			time.sleep(.25)
	query = 'SELECT * FROM messages WHERE resource_id = ? ORDER BY time ASC'
	cur = con.cursor()
	cur.execute(query,(resource,))
	convo = []
	for message in cur.fetchall():
		seconds = message['time']
		timestamp = time.strftime("%I:%M:%S", time.localtime(message['time']))
		if (message['tofrom'] == 0):
			fromme  = 'Me'
			fromyou = ''
		else:
			fromme  = ''
			fromyou = 'You'
		# tofrom = ['Me','You'][message['tofrom']]
		body = cgi.escape(message['message'])
		message = (seconds,timestamp,fromme,fromyou,body)
		convo.append(message)
	con.close()
	send('debug','convo finished')
	return convo
	

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Syntax: send.py JID text"
		sys.exit(0)
	resource=sys.argv[1]
	text=' '.join(sys.argv[2:])
	send(resource, text)
