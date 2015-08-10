import logging
from urlparse import urlparse
import json
import oauth2 as oauth
import microgear
import cache
import urllib
import random
import time
import re
import string
import paho.mqtt.client as mqtt


def create(gearkey,gearsecret, appid="", args = {}):
    if 'debugmode' in args:
       logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        )
    else:
        logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        )

    microgear.gearkey = gearkey
    microgear.gearsecret = gearsecret

    microgear.appid = appid
    microgear.gearname = None

    microgear.accesstoken = None
    microgear.requesttoken = None
    microgear.client = None
    microgear.scope = ""

    microgear.gearexaddress = None
    microgear.gearexport = None

    microgear.subscriptions = []
    microgear.callbacks = {}
    microgear.subscribe_list = []
    microgear.list_on_subscribe = {}
    microgear.pubilsh_list = []
    microgear.list_on_message = []
    microgear.list_on_connect = []
    microgear.list_on_disconnect = []

def client_on_connect(client, userdata, rc):
    print "Connected with result code "+str(rc)

    if rc == 0 : 
        for func in microgear.list_on_connect:
            func()
        for topic in microgear.pubilsh_list :
            client.publish(topic[0],topic[1])
        for topic in microgear.subscribe_list :
            client.subscribe(topic)
            print "Auto subscribe "+topic 
        for the_key, the_value in microgear.list_on_subscribe.iteritems():
            client.subscribe(the_key)
        

def client_on_message(client, userdata, msg):
    #client.publish("/piedemo/gearname/htmlgear", "ok i see"+str(int(time.time())))
    if len(microgear.list_on_subscribe) > 0 :
        microgear.list_on_subscribe[msg.topic](msg.topic,str(msg.payload))

def client_on_subscribe(client, userdata, mid, granted_qos):
    pass
    
def client_on_disconnect(client, userdata, rc):
    for func in microgear.list_on_disconnect:
        func()
    print "Diconnected with result code "+str(rc)

def connect():
    times = 1
    while not microgear.accesstoken:
        get_token()
        time.sleep(times)
        times = times+1

    mqtt_client = mqtt.Client(microgear.accesstoken["token"])
    endpoint = microgear.accesstoken["endpoint"].split("//")[1].split(":")
    username = microgear.gearkey+"%"+str(int(time.time()))
    password = hmac(microgear.accesstoken["secret"]+"&"+microgear.gearsecret,microgear.accesstoken["token"]+"%"+username)
    mqtt_client.username_pw_set(username,password)
    mqtt_client.connect(endpoint[0], int(endpoint[1]), 60)

    mqtt_client.on_connect = client_on_connect
    mqtt_client.on_message = client_on_message
    mqtt_client.on_subscribe = client_on_subscribe
    mqtt_client.on_disconnect = client_on_disconnect
    
    mqtt_client.loop_forever()


def on_subscribe(topic,func):
    microgear.list_on_subscribe["/piedemo/gearname/"+topic]=func

def on_connect(func):
    microgear.list_on_connect.append(func)

def on_disconnect(func):
    microgear.list_on_disconnect.append(func)

def subscride(topic):
    microgear.subscribe_list.append("/"+microgear.appid+"/gearname/"+topic)

def publish(topic,message):
    microgear.pubilsh_list.append(["/"+microgear.appid+topic,message])

def setname(topic):
    microgear.gearname = topic
    microgear.subscribe_list.append("/"+microgear.appid+"/gearname/"+topic)

def chat(topic,message):
    publish("/gearname/"+topic,message)
        
def get_token():
    logging.info("Check stored token.")
    cached = cache.get_item("microgear.cache")
    if not cached:
        cached = cache.set_item("microgear.cache", {})
        microgear.accesstoken = cached.get('accesstoken') 
    if microgear.accesstoken:
        endpoint = urlparse(accesstoken.get("endpoint"))
        microgear.gearexaddress = endpoint.host
        microgear.gearexport = endpoint.port
    else:
        if cached.get("requesttoken"):
            get_accesstoken(cached)
        else:
            get_requesttoken(cached)


def get_requesttoken(cached):
    logging.info("Requesting a request token.")
    consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
    client = oauth.Client(consumer)
    verifier = ''.join(random.sample(string.lowercase+string.digits,8))
    print verifier
    params = {'oauth_callback': "scope=%s&appid=%s&verifier=%s" % (microgear.scope, microgear.appid, verifier)}
    resp, content = client.request(microgear.gearauthrequesttokenendpoint, "POST", body=urllib.urlencode(params))
    matchContent = re.match( r'oauth_token=(.*?)&oauth_token_secret=(.*?).*', content)
    if matchContent:
        contents = content.split("&")
        cached["requesttoken"] = {
        "token": contents[0].split("=")[1],
        "secret": contents[1].split("=")[1],
        "verifier": verifier
        }
        cache.set_item("microgear.cache", cached)
        requesttoken = cached["requesttoken"]
        get_accesstoken(cached)
    else:
        logging.warning("Request token is not issued, please check your appkey and appsecret.")

def get_accesstoken(cached):
    microgear.requesttoken = cached.get("requesttoken")
    #send requesttoken to obtain accesstoken
    logging.info("Already has request token.")
    #logging.debug(json.dumps(microgear.requesttoken))
    logging.info("Requesting an access token.")
    token = oauth.Token(key=microgear.requesttoken.get("token"), secret=microgear.requesttoken.get("secret"))
    consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
    client = oauth.Client(consumer, token)
    params = { "oauth_verifier": microgear.requesttoken["verifier"]}
    resp, content = client.request(microgear.gearauthaccesstokenendpoint, "POST", body=urllib.urlencode(params))
    matchContent = re.match( r'endpoint=(.*?)&oauth_token=(.*?)&oauth_token_secret=(.*?).*', content)
    if matchContent:
        contents = content.split("&")
        cached["accesstoken"] = {
        "token": contents[1].split("=")[1],
        "secret": contents[2].split("=")[1],
        "endpoint": urllib.unquote(contents[0].split("=")[1]).decode('utf8') 
        }
        cache.set_item("microgear.cache", cached)
        microgear.accesstoken = cached["accesstoken"]
    else:
        logging.warning("Access token is not issued, please check your consumerkey and consumersecret.")


def hmac(key, message):
    import base64
    import hmac
    import hashlib
    import urllib

    hash = hmac.new(key, message, hashlib.sha1).digest()
    password = base64.encodestring(hash)
    password = password.strip()

    return password
