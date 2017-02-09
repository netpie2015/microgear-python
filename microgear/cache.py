import os
import json
import sys


CURRENT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))


def get_item(key):
    """Return content in cached file in JSON format"""
    CACHED_KEY_FILE = os.path.join(CURRENT_DIR, key)

    try:
        return json.loads(open(CACHED_KEY_FILE, "rb").read().decode('UTF-8'))["_"]
    except (IOError, ValueError):
        return None


def set_item(key,value):
    """Write JSON content from value argument to cached file and return"""
    CACHED_KEY_FILE = os.path.join(CURRENT_DIR, key)

    open(CACHED_KEY_FILE, "wb").write(json.dumps({"_": value}).encode('UTF-8'))

    return value


def delete_item(key):
    """Delete cached file if present"""
    CACHED_KEY_FILE = os.path.join(CURRENT_DIR, key)

    if os.path.isfile(CACHED_KEY_FILE):
        os.remove(CACHED_KEY_FILE)

