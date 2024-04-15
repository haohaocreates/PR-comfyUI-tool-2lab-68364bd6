import filecmp
import shutil
import os
import sys
import __main__

from .nodes.constants import PROJECT_NAME
from .nodes.properties_loader import LoadProperties
from .nodes.api.baidu_translator import BaiduTranslator
from .nodes.api.youdao_ai import YoudaoTranslator
from .nodes.api.openai_gpt import OpenaiGPT
from .nodes.api.azure_gpt import AzureOpenaiGpt
from .nodes.api.chatglm_gpt import ChatGLMGpt
from .nodes.api.llm import FactxApiBaiduTranslator, FactxApiYoudaoTranslator, FactxApiAzureOpenaiGPT, FactxApiChatGlmGPT
from .nodes.workflow2Api.apiNodes import LoadImage, Seed, InputInt, InputFloat, InputText, PublishWorkflow, AvailableCheckpointLoader,AvailableVAELoader,OutputText,OutputImage,OutputVideo,DisplayAny,ShowText2,ShowText1,ShowText
python = sys.executable

# User extension files in custom_nodes
project_name = PROJECT_NAME
extentions_folder = os.path.join(os.path.dirname(os.path.realpath(__main__.__file__)),"web" + os.sep + "extensions" + os.sep + project_name)
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
    LoadProperties.NAME: LoadProperties,
    OpenaiGPT.NAME: OpenaiGPT,
    AzureOpenaiGpt.NAME: AzureOpenaiGpt,
    ChatGLMGpt.NAME: ChatGLMGpt,
    BaiduTranslator.NAME: BaiduTranslator,
    YoudaoTranslator.NAME: YoudaoTranslator,
    FactxApiBaiduTranslator.NAME: FactxApiBaiduTranslator,
    FactxApiYoudaoTranslator.NAME: FactxApiYoudaoTranslator,
    FactxApiAzureOpenaiGPT.NAME: FactxApiAzureOpenaiGPT,
    FactxApiChatGlmGPT.NAME: FactxApiChatGlmGPT,

    AvailableCheckpointLoader.NAME: AvailableCheckpointLoader,
    AvailableVAELoader.NAME: AvailableVAELoader,
    LoadImage.NAME: LoadImage,
    Seed.NAME: Seed,
    InputInt.NAME:  InputInt,
    InputFloat.NAME: InputFloat,
    InputText.NAME: InputText,
    OutputText.NAME: OutputText,
    OutputImage.NAME: OutputImage,
    OutputVideo.NAME: OutputVideo,
    PublishWorkflow.NAME: PublishWorkflow,

    DisplayAny.NAME: DisplayAny,
    ShowText2.NAME: ShowText2,
    ShowText1.NAME: ShowText1,
    ShowText.NAME: ShowText,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    LoadProperties.NAME: "read properties 读取本地参数",
    OpenaiGPT.NAME: "OpenAI chatGPT",
    AzureOpenaiGpt.NAME: "Azure OpenAI GPT",
    ChatGLMGpt.NAME: "ChatGLM chatGPT 智谱AI",
    BaiduTranslator.NAME: "Baidu translator 百度翻译",
    YoudaoTranslator.NAME: "Youdao translator 有道翻译",
    FactxApiBaiduTranslator.NAME: "Baidu translator 百度翻译 (Factx API)",
    FactxApiYoudaoTranslator.NAME: "Youdao translator 有道翻译 (Factx API)",
    FactxApiAzureOpenaiGPT.NAME: "Azure OpenAI GPT (Factx API)",
    FactxApiChatGlmGPT.NAME: "ChatGLM chatGPT 智谱AI (Factx API)",

    AvailableCheckpointLoader.NAME: "load available checkpoint 载入可用的模型",
    AvailableVAELoader.NAME: "load available vae 载入可用的VAE",
    LoadImage.NAME: "load image 读入图片",
    Seed.NAME: "seed 生成随机数",
    InputInt.NAME: "input int 输入整数",
    InputFloat.NAME: "input float 输入浮点数",
    InputText.NAME: "input Text 输入文本",
    OutputText.NAME: "mark text output nodes 标注文字输出节点",
    OutputImage.NAME: "mark image output nodes 标注图片输出节点",
    OutputVideo.NAME: "mark video output nodes 标注视频输出节点",
    PublishWorkflow.NAME: "publish to 2lab 发布到2lab服务器",

    DisplayAny.NAME: "DisplayAny",
    ShowText.NAME: "ShowText",
    ShowText2.NAME: "ShowText2",
    ShowText1.NAME: "ShowText1",

}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]