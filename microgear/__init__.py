import logging
__version__ = '0.0.1'



gearauthsite = "http://gearauth.netpie.io:8080"
gearauthrequesttokenendpoint = gearauthsite+"/oauth/request_token"
gearauthaccesstokenendpoint = gearauthsite+"/oauth/access_token"

gearkey = None
gearsecret = None
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