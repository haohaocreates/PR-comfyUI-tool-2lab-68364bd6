import hashlib
import json
import requests
from ..constants import get_project_name, get_project_category, project_root, read_user_key

api_server_url = "http://api.factx.cn/api/v4";

NODE_CATEGORY = get_project_category("api")

class FactxResponse:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data

def submit(command: str, data: str) -> FactxResponse:
    print(command)
    print(data)

    submitUrl = (api_server_url + "/i?c={}").format(command);
    headers = {
        'content-type': 'application/json;charset=utf-8',
    }
    response = requests.post(submitUrl, headers=headers, data=data)
    print(response.text)

    factxResponse = json.loads(response.text)
    print(factxResponse)
    return factxResponse

class ChatGLM:
    NAME = get_project_name('ChatGLM')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
        }

    def doWork(self,  prompt):
        command = "app_factxApi_ChatGLM_GPT"
        userKey = read_user_key()
        if userKey == "":
            raise Exception("还没设置userKey")
        paramMap = {
            'userKey': userKey,
            "prompt": prompt,
        }
        responseJson = submit(command, json.dumps(paramMap))
        if responseJson['success']==True:
            result = responseJson['data']['result']
            result = result.strip()
            if result.startswith('"') and result.endswith('"'):
                result =  result[1:-1].strip()
            return {"result": (result,)}
        else:
            return {"result": (responseJson['message'],)}

    @classmethod
    def IS_CHANGED(s, prompt):
        m = hashlib.sha256()
        m.update(prompt)
        return m.digest().hex()

class AzureOpenaiGPT:
    NAME = get_project_name('AzureOpenaiGPT')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "deployment": ("KEY", {"multiline": False, "default": ""}),
            },
        }

    def doWork(self,  prompt, deployment):
        command = "app_factxApi_Azure_GPT"
        userKey = read_user_key()
        if userKey == "":
            raise Exception("还没设置userKey")
        paramMap = {
            'userKey': userKey,
            "prompt": prompt,
            "deployment": deployment
        }
        responseJson = submit(command, json.dumps(paramMap))
        if responseJson['success']==True:
            translate_result = responseJson['data']['result']
            return {"result": (translate_result,)}
        else:
            return {"result": (responseJson['message'],)}

    @classmethod
    def IS_CHANGED(s, prompt,deployment):
        m = hashlib.sha256()
        m.update(prompt+deployment)
        return m.digest().hex()

class BaiduTranslator:
    NAME = get_project_name('BaiduTranslator')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "to_lang": (["en", "zh"], {"default": "en"}),
            },
        }

    def doWork(self,  to_lang, text):
        command = "app_factxApi_baidu_translator"
        userKey = read_user_key()
        if userKey == "":
            raise Exception("还没设置userKey")
        paramMap = {
            'userKey': userKey,
            "to_lang": to_lang,
            "text": text
        }
        responseJson = submit(command, json.dumps(paramMap))
        if responseJson['success']==True:
            translate_result = responseJson['data']['result']
            return {"result": (translate_result,)}
        else:
            return {"result": (responseJson['message'],)}

    @classmethod
    def IS_CHANGED(s, to_lang, text):
        m = hashlib.sha256()
        m.update(to_lang+text)
        return m.digest().hex()

class YoudaoTranslator:
    NAME = get_project_name('YoudaoTranslator')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "to_lang": (["en", "zh-CHS"], {"default": "en"}),
            },
        }

    def doWork(self,  to_lang, text):
        command = "app_factxApi_youdao_translator"
        userKey = read_user_key()
        if userKey == "":
            raise Exception("还没设置userKey")
        paramMap = {
            'userKey': userKey,
            "to_lang": to_lang,
            "text": text
        }
        responseJson = submit(command, json.dumps(paramMap))
        if responseJson['success']==True:
            translate_result = responseJson['data']['result']
            return {"result": (translate_result,)}
        else:
            return {"result": (responseJson['message'],)}

    @classmethod
    def IS_CHANGED(s, to_lang, text):
        m = hashlib.sha256()
        m.update(to_lang+text)
        return m.digest().hex()