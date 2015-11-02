import os
import json

def get_item(key):
    try:
        return json.loads(open(os.path.join(os.getcwd(),key), "rb").read().decode('UTF-8'))["_"]
    except (IOError, ValueError):
        return None

def set_item(key,value):
    open(os.path.join(os.getcwd(),key), "wb").write(json.dumps({"_": value}).encode('UTF-8'))
    return value

def delete_item(key):
	if os.path.isfile(os.path.join(os.getcwd(),key)):
		os.remove(key)
