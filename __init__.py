import filecmp
import shutil
import os
import json
import sys
import __main__

import requests

from .nodes.constants import PROJECT_NAME,read_user_key
from .nodes.api.llm import BaiduTranslator, YoudaoTranslator, AzureOpenaiGPT, ChatGLM
from .nodes.workflow2Api.apiNodes import InputImage, InputSeed, InputInt, InputFloat, InputText, PublishWorkflow, \
    AvailableCheckpointLoader, AvailableVAELoader, OutputText, OutputImage, InputUserKey

python = sys.executable

# User extension files in custom_nodes
project_name = PROJECT_NAME
extentions_folder = os.path.join(os.path.dirname(os.path.realpath(__main__.__file__)),
                                 "web" + os.sep + "extensions" + os.sep + project_name)
javascript_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

if not os.path.exists(extentions_folder):
    os.mkdir(extentions_folder)

result = filecmp.dircmp(javascript_folder, extentions_folder)

if result.left_only or result.diff_files:
    file_list = list(result.left_only)
    file_list.extend(x for x in result.diff_files if x not in file_list)

    for file in file_list:
        src_file = os.path.join(javascript_folder, file)
        dst_file = os.path.join(extentions_folder, file)
        if os.path.exists(dst_file):
            os.remove(dst_file)
        shutil.copy(src_file, dst_file)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    BaiduTranslator.NAME: BaiduTranslator,
    YoudaoTranslator.NAME: YoudaoTranslator,
    AzureOpenaiGPT.NAME: AzureOpenaiGPT,
    ChatGLM.NAME: ChatGLM,

    AvailableCheckpointLoader.NAME: AvailableCheckpointLoader,
    AvailableVAELoader.NAME: AvailableVAELoader,
    InputImage.NAME: InputImage,
    InputSeed.NAME: InputSeed,
    InputInt.NAME: InputInt,
    InputFloat.NAME: InputFloat,
    InputText.NAME: InputText,
    OutputText.NAME: OutputText,
    OutputImage.NAME: OutputImage,
    InputUserKey.NAME: InputUserKey,
    # OutputVideo.NAME: OutputVideo,
    PublishWorkflow.NAME: PublishWorkflow,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    BaiduTranslator.NAME: "Baidu translator 百度翻译",
    YoudaoTranslator.NAME: "Youdao translator 有道翻译",
    AzureOpenaiGPT.NAME: "Azure OpenAI GPT",
    ChatGLM.NAME: "ChatGLM chatGPT 智谱AI",

    AvailableCheckpointLoader.NAME: "load available checkpoint 载入可用的模型",
    AvailableVAELoader.NAME: "load available vae 载入可用的VAE",

    InputSeed.NAME: "seed 生成随机数",
    InputImage.NAME: "load image 读入图片",
    InputInt.NAME: "input int 输入整数",
    InputFloat.NAME: "input float 输入浮点数",
    InputText.NAME: "input Text 输入文本",
    OutputText.NAME: "output text 输出文字",
    OutputImage.NAME: "output image 输出图片",
    # OutputVideo.NAME: "mark video output nodes 标注视频输出节点",
    InputUserKey.NAME: "input user key 输入用户密钥",
    PublishWorkflow.NAME: "publish to 2lab 发布到2lab服务器",

}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]

import server
from aiohttp import web
import aiohttp


@server.PromptServer.instance.routes.post("/2lab/share")
async def share_2lab(request):
    print("share_2lab")
    # get json data
    json_data = await request.json()
    workflow = json_data['workflow']

    body = {
        'userKey': read_user_key(),
        'workflow': workflow
    }
    print(body)

    url = "https://api.factx.cn/api/v4/i?c=engine_image_upload_workflow";
    print(url)
    headers = {
        'content-type': 'application/json;charset=utf-8',
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    # print(response.text)
    resJson = json.loads(response.text)
    # print(resJson)
    if resJson["success"]:
        resData={
            "share_url":resJson["data"]["url"],
            "msg":''
        }
        return web.json_response(resData, content_type='application/json', status=200)
    else:
        resData={
            "share_url":'',
            "msg":resJson["message"]
        }
        return web.json_response(resData, content_type='application/json', status=200)

