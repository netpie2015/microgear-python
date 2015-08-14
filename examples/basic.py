import microgear.client as microgear
import time

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

microgear.create(gearkey,gearsecret,appid)

def connection():
	print "Now I am connected with netpie"

def subscription(topic,message):
	microgear.chat("nobita","Hello world. "+str(int(time.time())))
	print topic+" "+message


microgear.setname("doraemon", subscription)
microgear.on_connect = connection
microgear.subscribe("/mails", subscription)

microgear.connect()
