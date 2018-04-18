import logging
import json
import microgear
from microgear import cache
import time
import re
import paho.mqtt.client as mqtt
import threading
import os
import sys
import requests
import certifi

def do_nothing(arg1=None, arg2=None):
    pass

subscribe_list = []
current_subscribe_list = []
current_id = None
publish_list = []
block_loop = False

on_present = do_nothing
on_absent = do_nothing
on_connect = do_nothing
on_message = do_nothing
on_error = do_nothing
on_warning = do_nothing
on_info = do_nothing
on_disconnect = do_nothing
config_list = {}

def create(gearkey,gearsecret, appid="", args = {}):
    if 'debugmode' in args:
        logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        )
    else:
        logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        )
    microgear.gearalias = args.get('alias',"")[0:16]
    if 'scope' in args:
        matchScope = re.match( r'^(\w+:[a-zA-Z\/]+,*)+$', args['scope'])
        if matchScope:
            microgear.scope = args["scope"]
        else:
            microgear.scope = ""
            logging.warning("Specify scope is not valid")

    microgear.gearkey = gearkey
    microgear.gearsecret = gearsecret
    microgear.appid = appid

def client_on_connect(client, userdata, rc):
    global block
    microgear.state = True
    logging.info("Connected with result code "+str(rc))
    if rc == 0 :
        on_connect()
        auto_subscribeAndpublish()
    elif rc == 1 :
        logging.warning("Unable to connect: Incorrect protocol version.")
    elif rc == 2 :
        logging.warning("Unable to connect: Invalid client identifier.")
    elif rc == 3 :
        logging.warning("Unable to connect: Server unavailable.")
    elif rc == 4 :
        unsubscribe(current_id)
        microgear.mqtt_client.disconnect()
        on_info("Invalid credential.")
        logging.info("Unable to connect: Invalid credential, requesting new one")
        resettoken()
        connect(block_loop)
    elif rc == 5 :
        on_warning("Not authorised.")
        logging.warning("Unable to connect: Not authorised.")
    else:
        logging.warning("Unable to connect: Unknown reason")

def client_on_publish(client, userdata, mid):
    #Publish callback
    pass

def client_on_message(client, userdata, msg):
    topics = msg.topic.split("/")
    if msg.topic != "@info" and msg.topic != "@error":
        if topics[2] == "&present":
            on_present(str(msg.payload))
        elif topics[2] == "&absent":
            on_absent(str(msg.payload))
        elif '&id' in topics[2]:
            #controll message
            pass
        else:
            on_message(msg.topic,str(msg.payload))
    elif msg.topic == "@info":
        on_info(str(msg.payload))
    elif msg.topic == "@error":
        on_error(str(msg.payload))

def client_on_subscribe(client, userdata, mid, granted_qos):
    ## TODO: Check subscribe fail
    pass

def client_on_disconnect(client, userdata, rc):
    if rc!=0:
        microgear.state = False
        on_disconnect()
        logging.info("Diconnected with result code "+str(rc))

def connect(block=False):
    global block_loop
    block_loop = block
    global current_subscribe_list
    global current_id
    times = 1
    while not microgear.accesstoken:
        get_token()
        time.sleep(times)
        times = times+10
    microgear.mqtt_client = mqtt.Client(microgear.accesstoken["token"])
    current_id = '/&id/'+str(microgear.accesstoken["token"])+'/#'
    current_subscribe_list.append('/&id/'+str(microgear.accesstoken["token"])+'/#')
    endpoint = microgear.accesstoken["endpoint"].split("//")[1].split(":")
    username = microgear.gearkey+"%"+str(int(time.time()))
    password = hmac(microgear.accesstoken["secret"]+"&"+microgear.gearsecret,microgear.accesstoken["token"]+"%"+username)
    microgear.mqtt_client.username_pw_set(username,password)
    if microgear.securemode:
        microgear.mqtt_client.tls_set(certifi.where())
        microgear.mqtt_client.connect(endpoint[0],int(microgear.gbsport), 60)
    else:
        microgear.mqtt_client.connect(endpoint[0],int(microgear.gbport), 60)
    microgear.mqtt_client.on_connect = client_on_connect
    microgear.mqtt_client.on_message = client_on_message
    microgear.mqtt_client.on_publish = client_on_publish
    microgear.mqtt_client.on_subscribe = client_on_subscribe
    microgear.mqtt_client.on_disconnect = client_on_disconnect

    if(block):
        microgear.mqtt_client.loop_forever()
    else:
        microgear.mqtt_client.loop_start()
        while True:
            time.sleep(2)
            break

def auto_subscribeAndpublish():
    global publish_list
    global current_subscribe_list
    if microgear.mqtt_client:
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&present")
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&absent")
        for topic in current_subscribe_list :
            microgear.mqtt_client.subscribe(topic)
            logging.info("Auto subscribe "+topic)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

    if microgear.mqtt_client :
        for topic in publish_list :
            microgear.mqtt_client.publish(topic[0],topic[1],retain=topic[2].get('retain',False))
            publish_list = []
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def subscribe_thread(topic,qos=0):
    if microgear.mqtt_client :
        logging.info("Auto subscribe "+topic)
        microgear.mqtt_client.subscribe(topic,qos)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def subscribe(topic,qos=0):
    global subscribe_list
    global current_subscribe_list
    threads = []
    if "/"+microgear.appid+topic not in current_subscribe_list:
        current_subscribe_list.append("/"+microgear.appid+topic)

    if microgear.mqtt_client:
        t = threading.Thread(target=subscribe_thread, args=("/"+microgear.appid+topic,qos))
        threads.append(t)
        t.start()
    else:
        subscribe_list.append("/"+microgear.appid+topic)

def unsubscribe(topic):
    global current_subscribe_list
    global current_id
    if microgear.mqtt_client:
        if topic == current_id:
            current_subscribe_list.remove(current_id)
            microgear.mqtt_client.unsubscribe(current_id)
        if "/"+microgear.appid+topic in current_subscribe_list:
            current_subscribe_list.remove("/"+microgear.appid+topic)
            microgear.mqtt_client.unsubscribe("/"+microgear.appid+topic)
        logging.info("Auto unsubscribe "+topic)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def publish_thread(topic,message,args = {}):
    qos = 0
    retain = False

    if 'qos' in args:
        gos = args['qos']

    if 'retain' in args:
        retain = args['retain']

    if microgear.mqtt_client :
        microgear.mqtt_client.publish(topic,message,qos=qos,retain=retain)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def publish(topic,message,args = {}):
    global publish_list
    threads = []
    if microgear.mqtt_client:
        t = threading.Thread(target=publish_thread, args=("/"+microgear.appid+topic,message,args))
        threads.append(t)
        t.start()
    else:
        publish_list.append(["/"+microgear.appid+topic,message,args])

def setname(topic):
    logging.warning("Deprecated soon: Please consider using setalias()")
    microgear.gearname = topic
    subscribe("/gearname/"+topic)

def setalias(alias):
    publish("/@setalias/"+alias,"")

def chat(topic,message):
    publish("/gearname/"+topic,message)

def readstream(stream, filter):
    publish('/@readstream/'+stream,'{"filter":"'+filter+'"}')

def writestream(stream,data):
    publish('/@writestream/'+stream,'{"data":'+data+'}')

def pushOwner(message):
    if type(message) is dict:
        logging.info("push notification json")
        json = "{"
        for key in message:
            json += "\""+str(key)+"\""+":"+str(message[key])+","
        json = json[:len(json)-1] + "}"
        publish("/@push/owner",json)
    else:
        logging.info("push notification message")
        publish("/@push/owner",message)

def get_token():
    logging.info("Check stored token.")
    cached = cache.get_item("microgear-"+microgear.gearkey+".cache")
    if cached:
        if cached.get("accesstoken"):
            if not cached.get("key"):
                cached["key"] = microgear.gearkey
                cache.set_item("microgear-"+microgear.gearkey+".cache", cached)
            microgear.accesstoken = cached.get("accesstoken")
            for name,value in microgear.accesstoken.items():
                microgear.accesstoken[name] = str(value)
            endpoint = microgear.accesstoken.get("endpoint").split("//")[1].split(":")
            microgear.gearexaddress = endpoint[0]
            microgear.gearexport = endpoint[1]
        elif cached.get("requesttoken"):
            get_accesstoken(cached)
        else:
            get_requesttoken(cached)
    else:
        cached = cache.set_item("microgear-"+microgear.gearkey+".cache", {"key": microgear.gearkey})

def get_requesttoken(cached):
    logging.info("Requesting a request token.")
    path=""
    url="" 
    if len(microgear.gearalias):
        verifier = microgear.gearalias
        path = '/oauth2/authorize?'+"response_type=code&client_id=" + microgear.gearkey + "&scope=appid:" + microgear.appid +" "+"alias:" +microgear.gearalias+ "&state=mgrev:" + microgear.mgrev;
    else:
        verifier = microgear.mgrev
        path = '/oauth2/authorize?'+"response_type=code&client_id=" + microgear.gearkey + "&scope=appid:" + microgear.appid +"&state=mgrev:" + microgear.mgrev;
    
    if microgear.securemode:
        url = "https://"+microgear.gearauthsite+":"+microgear.gearapisecureport+path;
    else:
        url = "http://"+microgear.gearauthsite+":"+microgear.gearapiport+path;
    response = requests.get(url)
    response = response.url.split("code=")
    if len(response)==2:
        cached["requesttoken"] = {"token": response[1],"secret": None,"verifier": verifier}
        cache.set_item("microgear-"+microgear.gearkey+".cache", cached)
        microgear.requesttoken = cached["requesttoken"]
        get_accesstoken(cached)
    else:
        on_error("Request token is not issued, please check your appkey and appsecret.")
        logging.error("Request token is not issued, please check your appkey and appsecret.")

def get_accesstoken(cached):
    microgear.requesttoken = cached.get("requesttoken")
    logging.info("Already has request token.")
    logging.info("Requesting an access token.")
    verifier = ""
    url = ""
    path = "/oauth2/token?grant_type=authorization_code&code=" + microgear.requesttoken.get("token") + "&client_id=" + microgear.gearkey + "&client_secret=" + microgear.gearsecret + "&state=mgrev:" + microgear.mgrev;
    if microgear.securemode:
        url = "https://"+microgear.gearauthsite+":"+microgear.gearapisecureport+path;
    else:
        url = "http://"+microgear.gearauthsite+":"+microgear.gearapiport+path;
    response = requests.post(url)
    if response.status_code==200:
        datajson = json.loads(response.text)
        token = datajson['access_token'].split(':')
        revokecode = hmac(token[1]+"&"+microgear.gearsecret,token[0]).replace('/','_')
        cached["requesttoken"] = None
        cached["accesstoken"] = {
            "token": token[0],
            "secret": token[1],
            "endpoint": datajson['endpoint'],
            "revokecode": revokecode
        }
        flag = datajson['flag']
        if flag == "P":
            cache.set_item("microgear-"+microgear.gearkey+".cache", cached)
        elif flag == "S":
            cache.set_item("microgear-"+microgear.gearkey+".cache", {})
        microgear.accesstoken = cached["accesstoken"]
    else:
        resettoken()
        on_error("Access token is not issued, please check your consumerkey and consumersecret.")
        logging.error("Access token is not issued, please check your consumerkey and consumersecret.")


def hmac(key, message):
    import base64
    import hmac
    import hashlib

    hash = hmac.new(key.encode('utf-8'),message.encode('utf-8'), hashlib.sha1).digest()
    password = base64.encodestring(hash)
    password = password.strip()

    return password.decode('utf-8')

def resettoken():
    cached = cache.get_item("microgear-"+microgear.gearkey+".cache")
    if cached :
        microgear.accesstoken = cached.get("accesstoken",{})
        if "revokecode" in microgear.accesstoken :
            path = "/api/revoke/"+microgear.accesstoken["token"]+"/"+microgear.accesstoken["revokecode"]
            url = ""
            if microgear.securemode:
                url = "https://"+microgear.gearauthsite+":"+microgear.gearapisecureport+path;
            else:
                url = "http://"+microgear.gearauthsite+":"+microgear.gearapiport+path;
            response = requests.get(url)
            if response.status_code==200:
                cache.delete_item("microgear-"+microgear.gearkey+".cache")
            else:
                on_error("Reset token error.")
                logging.error("Reset token error.")
        else:
            cache.delete_item("microgear-"+microgear.gearkey+".cache")
            logging.warning("Token is still, please check your key on Key Management.")
        microgear.accesstoken = None

def disconnect():
    microgear.mqtt_client.disconnect();

def writeFeed(feedid,data,feedkey=""):
    if len(feedid)>0 and type(data) is dict:
        json = "{"
        for key in data:
            json += "\""+str(key)+"\""+":"+str(data[key])+","
        json = json[:len(json)-1] + "}"
        if feedkey == "":
            publish("/@writefeed/"+feedid,json)
        else:
            publish("/@writefeed/"+feedid+"/"+feedkey,json)
        logging.info(json)
    else:
        logging.info("Invalid parameters, please try again")

def setConfig(key,value):
    if(key=="GEARAUTH"):
        config_list["GEARAUTH"] = value
        microgear.gearauthsite = value

def getConfig(key):
    return config_list[key]

def useTLS(boolean):
    microgear.securemode = boolean

def connected():
    return micrgear.state



