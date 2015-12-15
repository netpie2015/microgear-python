import logging
__version__ = '1.1.10'

gearauthsite = "http://gearauth.netpie.io:8080"
gearauthrequesttokenendpoint = gearauthsite+"/api/rtoken"
gearauthaccesstokenendpoint = gearauthsite+"/api/atoken"

mgrev = "PY11j"
gearkey = None
gearsecret = None
gearalias = None
appid = None
gearname = None
accesstoken = None
requesttoken = None
client = None
scope = ""
gearexaddress = None
gearexport = None
mqtt_client = None
logger = logging.getLogger("python-microgear")
