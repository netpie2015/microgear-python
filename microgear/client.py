import logging
from urlparse import urlparse
import json
import oauth2 as oauth
import microgear
import cache

def create(gearkey,gearsecret, appid, args = {}):
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
    cached = Cache("microgear.cache")
    if not cached:
        cached = cache.set_item("microgear.cache", {})
        accesstoken = cached.get('accesstoken')
    if accesstoken:
        endpoint = urlparse(accesstoken.get("endpoint"))
        gearexaddress = endpoint.host
        gearexport = endpoint.port
    else:
    if accesstoken and accesstoken.get("requesttoken"):
        requesttoken = accesstoken.get("requesttoken")
        #send requesttoken to obtain accesstoken
        logging.debug("already has request token")
        logging.debug(json.dump(requesttoken))
        logging.debug("Requesting an access token.")
        token = oauth.Token(key=requesttoken.get("token"), secret=requesttoken.get("secret"))
        consumer = oauth.Consumer(key=gearkey, secret=gearsecret)
        resp, content = client.request(GEARAUTHACCESSTOKENENDPOINT, "POST", body=urllib.urlencode(body))
        print content
        cached["accesstoken"] = {
        "token": access_token.token,
        "secret": access_token.secret,
        "appkey": results.appkey,
        "endpoint": results.endpoint
        }
        cache.set_item("microgear.cache", cached)
        accesstoken = cached["accesstoken"]
    else:
        logging.debug("Requesting a request token.")
        print gearkey,gearsecret
        consumer = oauth.Consumer(key=gearkey, secret=gearsecret)
        resp, content = client.request(GEARAUTHREQUESTTOKENENDPOINT, "POST", body=urllib.urlencode(body))
        cached["requesttoken"] = {
        "token": token.token,
        "secret": token.secret,
        "verifier": verifier
        }
        cache.set_item("microgear.cache", cached)
        requesttoken = cached["requesttoken"]
