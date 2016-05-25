import microgear.client as client
import time
import logging

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

client.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
    logging.debug("Now I am connected with netpie")

def subscription(topic,message):
    logging.debug(topic+" "+message)

client.setname("doraemon")
client.on_connect = connection
client.on_message = subscription
client.subscribe("/mails")

client.connect(False)

while True:
    client.chat("doraemon","Hello world."+str(int(time.time())))
    time.sleep(2)
