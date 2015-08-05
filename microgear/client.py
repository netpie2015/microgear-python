import logging
from urlparse import urlparse
import json
import oauth2 as oauth
import microgear
import cache
import urllib
import random
import time

def create(gearkey,gearsecret, appid="", args = {}):
    if 'debugmode' in args:
        logging.basicConfig(level=logging.DEBUG)

    microgear.gearkey = gearkey
    microgear.gearsecret = gearsecret

    microgear.appid = appid
    microgear.gearname = None

    microgear.accesstoken = None
    microgear.requesttoken = None
    microgear.client = None
    microgear.scope = args.get("scope") or ""

    microgear.gearexaddress = None
    microgear.gearexport = None

    microgear.subscriptions = []
    microgear.callbacks = {}

def connect():
    get_token()


def get_token():
    logging.debug("Check stored token")
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
            microgear.requesttoken = cached.get("requesttoken")
            #send requesttoken to obtain accesstoken
            logging.debug("already has request token")
            logging.debug(json.dumps(microgear.requesttoken))
            logging.debug("Requesting an access token.")
            token = oauth.Token(key=microgear.requesttoken.get("token"), secret=microgear.requesttoken.get("secret"))
            consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
            client = oauth.Client(consumer, token)
            params = { "oauth_verifier": microgear.requesttoken["verifier"]}
            resp, content = client.request(microgear.gearauthaccesstokenendpoint, "POST", body=urllib.urlencode(params))
            contents = content.split("&")
            cached["accesstoken"] = {
            "token": contents[1].split("=")[1],
            "secret": contents[2].split("=")[1],
            "endpoint": urllib.unquote(contents[0].split("=")[1]).decode('utf8') 
            }
            cache.set_item("microgear.cache", cached)
            microgear.accesstoken = cached["accesstoken"]
        else:
            logging.debug("Requesting a request token.")
            consumer = oauth.Consumer(key=microgear.gearkey, secret=microgear.gearsecret)
            client = oauth.Client(consumer)
            verifier = random.getrandbits(32)
            params = {'oauth_callback': "scope=%s&appid=%s&verifier=%s" % (microgear.scope, microgear.appid, verifier)}
            resp, content = client.request(microgear.gearauthrequesttokenendpoint, "POST", body=urllib.urlencode(params) )
            contents = content.split("&")
            cached["requesttoken"] = {
            "token": contents[0].split("=")[1],
            "secret": contents[1].split("=")[1],
            "verifier": verifier
            }
            cache.set_item("microgear.cache", cached)
            requesttoken = cached["requesttoken"]