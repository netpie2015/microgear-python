import logging
__version__ = '1.1.9'

gearauthsite = "http://gearauth.netpie.io:8080"
gearauthrequesttokenendpoint = gearauthsite+"/api/rtoken"
gearauthaccesstokenendpoint = gearauthsite+"/api/atoken"

mgrv = "PY11i;"
gearkey = None
gearsecret = None
gearlabel = None
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
