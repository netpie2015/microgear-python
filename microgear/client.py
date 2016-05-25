import logging
import json
import oauth2 as oauth
import microgear
from microgear import cache
try:
    from urllib.parse import urlencode
    from urllib.parse import unquote
    from urllib.parse import parse_qs
except ImportError:
    from urllib import urlencode
    from urllib import unquote
    from urlparse import parse_qs
import httplib2
import random
import time
import re
import string
import paho.mqtt.client as mqtt
import threading

def do_nothing(arg1=None, arg2=None):
    pass

subscribe_list = []
current_subscribe_list = []
current_id =None
publish_list = []
block_loop = False
on_disconnect = do_nothing
on_present = do_nothing
on_absent = do_nothing
on_connect = do_nothing
on_message = do_nothing
on_error = do_nothing
on_warning = do_nothing
on_info = do_nothing

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
    logging.debug("Connected with result code "+str(rc))
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
    if topics[2] == "&present":
        on_present(str(msg.payload))
    elif topics[2] == "&absent":
        on_absent(str(msg.payload))
    elif '&id' in topics[2]:
        #controll message
        pass
    else:
        on_message(msg.topic,str(msg.payload))

def client_on_subscribe(client, userdata, mid, granted_qos):
    ## TODO: Check subscribe fail
    pass

def client_on_disconnect(client, userdata, rc):
    on_disconnect()
    if rc!=0:
        logging.debug("Diconnected with result code "+str(rc))

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
    microgear.mqtt_client.connect(endpoint[0], int(endpoint[1]), 60)

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
    if len(microgear.gearalias):
        setalias(microgear.gearalias)
    if microgear.mqtt_client:
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&present")
        microgear.mqtt_client.subscribe("/"+microgear.appid+"/&absent")
        for topic in current_subscribe_list :
            microgear.mqtt_client.subscribe(topic)
            logging.debug("Auto subscribe "+topic)
    
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



def subscribe_thread(topic):
    if microgear.mqtt_client :
        logging.debug("Auto subscribe "+topic)
        microgear.mqtt_client.subscribe(topic)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def subscribe(topic):
    global subscribe_list
    global current_subscribe_list
    threads = []
    if "/"+microgear.appid+topic not in current_subscribe_list:
        current_subscribe_list.append("/"+microgear.appid+topic)

    if microgear.mqtt_client:
        t = threading.Thread(target=subscribe_thread, args=("/"+microgear.appid+topic,))
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
        logging.debug("Auto unsubscribe "+topic)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def publish_thread(topic,message,retain=False):
    if microgear.mqtt_client :
        microgear.mqtt_client.publish(topic,message,retain=retain)
    else:
        on_error("Microgear currently is not available.")
        logging.error("Microgear currently is not available.")

def publish(topic,message,retain=False):
    global publish_list
    threads = []
    if microgear.mqtt_client:
        t = threading.Thread(target=publish_thread, args=("/"+microgear.appid+topic,message,retain))
        threads.append(t)
        t.start()
    else:
        publish_list.append(["/"+microgear.appid+topic,message,{'retain': retain}])

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

def get_token():
    logging.debug("Check stored token.")
    cached = cache.get_item("microgear.cache")
    if cached:
        if cached.get("accesstoken"):
            if not cached.get("key"):
                cached["key"] = microgear.gearkey
                cache.set_item("microgear.cache", cached)
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
        cached = cache.set_item("microgear.cache", {"key": microgear.gearkey})

def get_requesttoken(cached):
    logging.debug("Requesting a request token.")
    consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
    client = oauth.Client(consumer)
    if len(microgear.gearalias):
        verifier = microgear.gearalias
    else:
        verifier = microgear.mgrev
    headers = {}
    method = "POST"
    params = {'oauth_callback': "scope=%s&mgrev=%s&appid=%s&verifier=%s" % (microgear.scope, microgear.mgrev, microgear.appid, verifier)}
    req = oauth.Request.from_consumer_and_token(consumer, http_method=method,
            http_url=microgear.gearauthrequesttokenendpoint, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    headers.update(req.to_header(realm="NETPIE"))
    h = httplib2.Http(".cache")
    resp, content = h.request(microgear.gearauthrequesttokenendpoint, method=method,
            headers=headers)
    parsed_resp = parse_qs(content.decode(encoding='UTF-8'))
    if resp.status == 200:
        cached["requesttoken"] = {
            "token": parsed_resp['oauth_token'][0],
            "secret": parsed_resp['oauth_token_secret'][0],
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
    logging.debug("Already has request token.")
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
    parsed_resp = parse_qs(content.decode(encoding='UTF-8'))
    if resp.status == 200:
        revokecode = hmac(parsed_resp['oauth_token_secret'][0]+"&"+microgear.gearsecret,parsed_resp['oauth_token'][0]).replace('/','_')
        cached["requesttoken"] = None
        cached["accesstoken"] = {
            "token": parsed_resp['oauth_token'][0],
            "secret": parsed_resp['oauth_token_secret'][0],
            "endpoint": parsed_resp['endpoint'][0],
            "revokecode": revokecode
        }
        flag = parsed_resp.get('flag',["P"])
        if flag[0] == "P":
            cache.set_item("microgear.cache", cached)
        elif flag[0] == "S":
            cache.set_item("microgear.cache", {})
        microgear.accesstoken = cached["accesstoken"]
    else:
        resettoken()
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
        microgear.accesstoken = cached.get("accesstoken",{})
        if "revokecode" in microgear.accesstoken :
            path = "/api/revoke/"+microgear.accesstoken["token"]+"/"+microgear.accesstoken["revokecode"]
            h = httplib2.Http(".cache")
            resp, content = h.request(gearauthsite+path, method="GET")
            if(resp.status==200):
                cache.delete_item("microgear.cache")
            else:
                on_error("Reset token error.")
                logging.error("Reset token error.")
        else:
            cache.delete_item("microgear.cache")
            logging.warning("Token is still, please check your key on Key Management.")
        microgear.accesstoken = None
