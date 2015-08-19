import microgear.client as client
import time

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
	print "Now I am connected with netpie"

def subscription(topic,message):
	client.chat("nobita","Hello world. "+str(int(time.time())))
	print topic+" "+message

client.setname("doraemon", subscription)
client.on_connect = connection

client.subscribe("/mails", subscription)

client.connect()
