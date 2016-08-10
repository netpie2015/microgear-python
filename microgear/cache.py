import os
import json
import sys

def get_item(key):
    try:
        return json.loads(open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),key), "rb").read().decode('UTF-8'))["_"]
    except (IOError, ValueError):
        return None

def set_item(key,value):
    open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),key), "wb").write(json.dumps({"_": value}).encode('UTF-8'))
    return value

def delete_item(key):
	if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),key)):
		os.remove(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),key))
