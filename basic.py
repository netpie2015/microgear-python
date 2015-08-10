import microgear.client as microgear
import time


microgear.create("qDDwMaHEXfBiXmL","vNoswuhfqjxWSm0GR7cycGPniekw03","piedemo")

def connection():
	microgear.chat("htmlgear","test"+str(int(time.time())))
	print "Now I am connected with netpie"

def subscription(topic,message):
	microgear.chat("htmlgear","ok i see"+str(int(time.time())))
	print topic+" "+message


microgear.setname("python")
microgear.on_connect(connection)

microgear.on_subscribe("python",subscription)

microgear.connect()
