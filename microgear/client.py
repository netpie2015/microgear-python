import logging
import json
import oauth2 as oauth
import microgear
from microgear import cache
try:
    from urllib.parse import urlencode
    from urllib.parse import unquote
except ImportError:
    from urllib import urlencode
    from urllib import unquote
import httplib2
import random
import time
import re
import string
import paho.mqtt.client as mqtt
import threading
try:
    import httplib.client as httplib
except ImportError:
    import httplib

def do_nothing(arg1=None, arg2=None):
    pass

subscribe_list = []
publish_list = []
on_disconnect = do_nothing
on_present = do_nothing
on_absent = do_nothing
on_connect = do_nothing
on_message = do_nothing
on_error = do_nothing
on_reject = do_nothing

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
    logging.debug("Connected with result code "+str(rc))
    if rc == 0 :
        on_connect()
        auto_subscribeAndpublish()
    elif rc == 1 :
        on_reject("Incorrect protocol version.")
        logging.warning("Incorrect protocol version.")
    elif rc == 2 :
        on_reject("Invalid client identifier.")
        logging.warning("Invalid client identifier.")
    elif rc == 3 :
        on_reject("Server unavailable.")
        logging.warning("Server unavailable.")
    elif rc == 4 :
        on_reject("Bad username or password.")
        logging.warning("Bad username or password.")
    elif rc == 5 :
        on_reject("Not authorised.")
        logging.warning("Not authorised.")
    else:
        on_reject("Unknown reason")
        logging.warning("Unknown reason")

def client_on_message(client, userdata, msg):
    topics = msg.topic.split("/")
    if topics[2] == "&present":
        on_present(str(msg.payload))
    elif topics[2] == "&absent":
        on_absent(str(msg.payload))
    else:
        on_message(msg.topic,str(msg.payload))

def client_on_subscribe(client, userdata, mid, granted_qos):
    ## TODO: Check subscribe fail
    pass

def client_on_disconnect(client, userdata, rc):
    microgear.mqtt_client = None
    on_disconnect()
    logging.debug("Diconnected with result code "+str(rc))

def connect(block=False):
    global subscribe_list
    times = 1
    while not microgear.accesstoken:
        get_token()
        time.sleep(times)
        times = times+10
    microgear.mqtt_client = mqtt.Client(microgear.accesstoken["token"])
    subscribe_list.append('/&id/'+str(microgear.accesstoken["token"])+'/#')
    endpoint = microgear.accesstoken["endpoint"].split("//")[1].split(":")
    username = microgear.gearkey+"%"+str(int(time.time()))
    password = hmac(microgear.accesstoken["secret"]+"&"+microgear.gearsecret,microgear.accesstoken["token"]+"%"+username)
    microgear.mqtt_client.username_pw_set(username,password)
    microgear.mqtt_client.connect(endpoint[0], int(endpoint[1]), 60)

    microgear.mqtt_client.on_connect = client_on_connect
    microgear.mqtt_client.on_message = client_on_message
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
    global subscribe_list
    if microgear.mqtt_client:
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&present")
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&absent")
        for topic in subscribe_list :
            microgear.mqtt_client.subscribe(topic)
            logging.debug("Auto subscribe "+topic )
            subscribe_list = []
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")
    if microgear.mqtt_client :
        for topic in publish_list :
            microgear.mqtt_client.publish(topic[0],topic[1])
            publish_list = []
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")


def subscribe_thread(topic):
    if microgear.mqtt_client :
        logging.debug("Auto subscribe "+topic)
        microgear.mqtt_client.subscribe(topic)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def subscribe(topic):
    global subscribe_list
    threads = []
    if microgear.mqtt_client:
        t = threading.Thread(target=subscribe_thread, args=("/"+microgear.appid+topic,))
        threads.append(t)
        t.start()
    else:
        subscribe_list.append("/"+microgear.appid+topic)

def publish_thread(topic,message):
    if microgear.mqtt_client :
        microgear.mqtt_client.publish(topic,message)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def publish(topic,message):
    global publish_list
    threads = []
    if microgear.mqtt_client:
        t = threading.Thread(target=publish_thread, args=("/"+microgear.appid+topic,message,))
        threads.append(t)
        t.start()
    else:
        publish_list.append(["/"+microgear.appid+topic,message])

def setname(topic):
    microgear.gearname = topic
    subscribe("/gearname/"+topic)

def chat(topic,message):
    publish("/gearname/"+topic,message)

def readstream(stream, filter):
    publish('/@readstream/'+stream,'{"filter":"'+filter+'"}')

def writestream(stream,data):
    publish('/@writestream/'+stream,'{"data":'+data+'}')

def get_token():
    logging.debug("Check stored token.")
    cached = cache.get_item("microgear.cache")
    if cached == None:
        cached = cache.set_item("microgear.cache", {})
    else:
        microgear.accesstoken = cached["accesstoken"]
        for name,value in microgear.accesstoken.items():
            microgear.accesstoken[name] = str(value)

    if microgear.accesstoken:
        endpoint = microgear.accesstoken.get("endpoint").split("//")[1].split(":")
        microgear.gearexaddress = endpoint[0]
        microgear.gearexport = endpoint[1]
    else:
        if cached.get("requesttoken"):
            get_accesstoken(cached)
        else:
            get_requesttoken(cached)

def get_requesttoken(cached):
    logging.debug("Requesting a request token.")
    consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
    client = oauth.Client(consumer)
    verifier = ''.join(random.sample(string.ascii_lowercase+string.digits,8))
    headers = {}
    method = "POST"
    params = {'oauth_callback': "scope=%s&appid=%s&verifier=%s" % (microgear.scope, microgear.appid, verifier)}
    req = oauth.Request.from_consumer_and_token(consumer, http_method=method,
            http_url=microgear.gearauthrequesttokenendpoint, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    headers.update(req.to_header(realm="NETPIE"))
    h = httplib2.Http(".cache")
    resp, content = h.request(microgear.gearauthrequesttokenendpoint, method=method,
            headers=headers)
    content = content.decode('UTF-8')
    matchContent = re.match( r'oauth_token=(.*?)&oauth_token_secret=(.*?).*', content)
    if matchContent:
        contents = content.split("&")
        cached["requesttoken"] = {
            "token": contents[0].split("=")[1],
            "secret": contents[1].split("=")[1],
            "verifier": verifier
        }
        cache.set_item("microgear.cache", cached)
        microgear.requesttoken = cached["requesttoken"]
        get_accesstoken(cached)
    else:
        on_error("Request token is not issued, please check your appkey and appsecret.")
        logging.error("Request token is not issued, please check your appkey and appsecret.")

def get_accesstoken(cached):
    microgear.requesttoken = cached.get("requesttoken")
    #send requesttoken to obtain accesstoken
    logging.debug("Already has request token.")
    #logging.debug(json.dumps(microgear.requesttoken))
    logging.debug("Requesting an access token.")
    token = oauth.Token(key=microgear.requesttoken.get("token"), secret=microgear.requesttoken.get("secret"))
    consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
    client = oauth.Client(consumer, token)
    params = { "oauth_verifier": microgear.requesttoken["verifier"]}
    headers = {}
    method = "POST"
    req = oauth.Request.from_consumer_and_token(consumer, token=token, http_method=method,
            http_url=microgear.gearauthaccesstokenendpoint, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
    headers.update(req.to_header(realm="NETPIE"))
    h = httplib2.Http(".cache")
    resp, content = h.request(microgear.gearauthaccesstokenendpoint, method=method,
            headers=headers)
    content = content.decode('UTF-8')
    matchContent = re.match( r'endpoint=(.*?)&oauth_token=(.*?)&oauth_token_secret=(.*?).*', content)
    if matchContent:
        contents = content.split("&")
        revokecode = hmac(contents[2].split("=")[1]+"&"+microgear.gearsecret,contents[1].split("=")[1]).replace('/','_')
        cached["accesstoken"] = {
            "token": contents[1].split("=")[1],
            "secret": contents[2].split("=")[1],
            "endpoint": unquote(contents[0].split("=")[1]),
            "revokecode": revokecode
        }
        cache.set_item("microgear.cache", cached)
        microgear.accesstoken = cached["accesstoken"]
    else:
        on_error("Access token is not issued, please check your consumerkey and consumersecret.")
        logging.error("Access token is not issued, please check your consumerkey and consumersecret.")

def hmac(key, message):
    import base64
    import hmac
    import hashlib
    import urllib

    hash = hmac.new(key.encode('utf-8'),message.encode('utf-8'), hashlib.sha1).digest()
    password = base64.encodestring(hash)
    password = password.strip()

    return password.decode('utf-8')

def resettoken():
    cached = cache.get_item("microgear.cache")
    if cached :
        microgear.accesstoken = cached["accesstoken"]
        if "revokecode" in microgear.accesstoken :
            path = "/api/revoke/"+microgear.accesstoken["token"]+"/"+microgear.accesstoken["revokecode"]
            conn = httplib.HTTPConnection("gearauth.netpie.io", 8080)
            conn.request("GET", path)
            r1 = conn.getresponse()
            if(r1.status==200):
                cache.delete_item("microgear.cache")
            else:
                on_error("Reset token error.")
                logging.error("Reset token error.")
        else:
            cache.delete_item("microgear.cache")
            logging.warning("Token is still, please check your key on Key Management.")
        microgear.accesstoken = None
