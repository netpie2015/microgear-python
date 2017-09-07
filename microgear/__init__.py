import logging
__version__ = '1.2.6'

gearauthsite = "ga.netpie.io"
gearapiport = '8080';
gearapisecureport = '8081';
gbport = '1883';
gbsport = '8883';
gearauthrequesttokenendpoint = gearauthsite+"/api/rtoken"
gearauthaccesstokenendpoint = gearauthsite+"/api/atoken"

mgrev = "PY11k"
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
securemode = False
state = False
