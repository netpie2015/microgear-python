import os
import json

class Cache():
    """Cache for stored token"""
    def __init__(self, key):
        self.key = key

    def get_item():
        try:
            return json.loads(open(os.path.join(os.getcwd(),self.key), "rb").read())
        except Exception, e:
            return None

    def set_item(value):
        open(os.path.join(os.getcwd(),self.key), "wb").write(json.dumps(value))
        return value
