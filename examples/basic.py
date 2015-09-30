import microgear.client as client
import time

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

client.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
	print "Now I am connected with netpie"

def subscription(topic,message):
  	print topic+" "+message
  	client.chat("nobita","Hey guy."+str(int(time.time())))

client.setname("doraemon")
client.on_connect = connection
client.on_message = subscription
client.subscribe("/mails")

client.connect(False)

while True:
    client.chat("doraemon","Hello world."+str(int(time.time())))
    time.sleep(2)