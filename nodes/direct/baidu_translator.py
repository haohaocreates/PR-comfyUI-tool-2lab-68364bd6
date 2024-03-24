import hashlib
import json
import os
import time
import requests
from ..constants import get_project_name, get_project_category, project_root

url_api_baidu_translator = "http://api.fanyi.baidu.com/api/trans/vip/translate" # 百度翻译API的URL

NODE_CATEGORY = get_project_category("llm")

class DirectBaiduTranslator:


    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "to_lang": (["en", "zh"], {"default": "en"}),
            },
        }

    NAME = get_project_name('baidu_translator')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    def doWork(self, to_lang, text):
        from_lang = "auto"     # 源语言自动识别
        salt = str(int(time.time()))

        try:
            config_path = os.path.join(project_root, 'properties.json')
            with open(config_path, 'r') as f:
                key_dict = json.load(f)
                app_id = key_dict.get('baidu_tranlator_app_id')
                api_key = key_dict.get('baidu_tranlator_security_key')
        except:
            print("failed to load properties")
            pass

        if app_id is None:
            raise ValueError('baidu api id not found')
        if api_key is None:
            raise ValueError('baidu api key not found')

        signStr = app_id + text + str(salt) + api_key
        sign = hashlib.md5(signStr.encode()).hexdigest()

        # 设置请求头，其中appid和secret需要替换为你自己的值
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }
        # 设置请求参数
        data = {
            "q": text,  # 要翻译的文本
            "from": from_lang,  # 源语言，例如"en"表示英文
            "to": to_lang,  # 目标语言，例如"zh"表示中文
            "appid": app_id,  # 替换为你的百度翻译API App ID
            "salt": salt,  # 随机数，用于签名加密
            "sign": sign,  # 替换为你的百度翻译API签名
        }
        # print(data)

        translate_result = ""
        try:
            # 发送POST请求
            response = requests.post(url_api_baidu_translator, headers=headers, data=data)
            responseJson = response.json()  # 解析JSON响应

            # 检查是否翻译成功
            if "error_code" not in responseJson:
                translate_result = responseJson["trans_result"][0]["dst"]  # 获取翻译结果
            else:
                # raise ValueError(responseJson)
                translate_result = "baidu translate fail : "+json.dumps(responseJson)

        except Exception as e:
            print(e.with_traceback())
            translate_result = "baidu translator server fail"

        return {"result": (translate_result,)}

NODE_CLASS_MAPPINGS = {
    DirectBaiduTranslator.NAME: DirectBaiduTranslator,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    DirectBaiduTranslator.NAME: "Baidu translator 百度翻译",
}
