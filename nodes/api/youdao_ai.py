import hashlib
import json
import os
import time
import uuid
from ..constants import get_project_name, get_project_category, project_root
import requests

YOUDAO_URL = 'https://openapi.youdao.com/api'
NODE_CATEGORY = get_project_category("api")

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()

def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)

class YoudaoTranslator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "to_lang": (["en", "zh-CHS"], {"default": "en"}),
            },
        }

    NAME = get_project_name('youdao_translator')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    def doWork(self, to_lang, text):
        q = text

        try:
            config_path = os.path.join(project_root, 'properties.json')
            with open(config_path, 'r') as f:
                key_dict = json.load(f)
                app_key = key_dict.get('youdao_ai_app_key')
                app_secret = key_dict.get('youdao_ai_app_secret')
        except:
            print("failed to load properties")
            pass

        data = {}
        data['from'] = 'auto'
        data['to'] = to_lang
        data['signType'] = 'v3'
        curtime = str(int(time.time()))
        data['curtime'] = curtime
        salt = str(uuid.uuid1())
        signStr = app_key + truncate(q) + salt + curtime + app_secret
        sign = encrypt(signStr)
        data['appKey'] = app_key
        data['q'] = q
        data['salt'] = salt
        data['sign'] = sign
        data['vocabId'] = ""

        response = do_request(data)
        # print(response.text)
        responseJson = json.loads(response.text)
        return {"result": (responseJson['translation'][0],)}
