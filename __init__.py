import filecmp
import shutil
import os
import sys
import __main__

from .nodes.constants import PROJECT_NAME
from .nodes.properties_loader import LoadProperties
from .nodes.direct.baidu_translator import DirectBaiduTranslator
from .nodes.direct.youdao_ai import DirectYoudaoTranslator
from .nodes.direct.openai_gpt import OpenaiGPT
from .nodes.direct.azure_gpt import DirectAzureOpenaiGpt
from .nodes.direct.chatglm_gpt import DirectChatGLMGpt
from .nodes.api.llm import BaiduTranslator, YoudaoTranslator, AzureOpenaiGPT, ChatGlmGPT

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
    DirectAzureOpenaiGpt.NAME: DirectAzureOpenaiGpt,
    DirectChatGLMGpt.NAME: DirectChatGLMGpt,
    DirectBaiduTranslator.NAME: DirectBaiduTranslator,
    DirectYoudaoTranslator.NAME: DirectYoudaoTranslator,

    BaiduTranslator.NAME: BaiduTranslator,
    YoudaoTranslator.NAME: YoudaoTranslator,
    AzureOpenaiGPT.NAME: AzureOpenaiGPT,
    ChatGlmGPT.NAME: ChatGlmGPT,
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
    LoadProperties.NAME: "read properties 读取本地参数",
    OpenaiGPT.NAME: "OpenAI chatGPT",

    DirectAzureOpenaiGpt.NAME: "Azure OpenAI GPT",
    DirectChatGLMGpt.NAME: "ChatGLM chatGPT 智谱AI",
    DirectBaiduTranslator.NAME: "Baidu translator 百度翻译",
    DirectYoudaoTranslator.NAME: "Youdao translator 有道翻译",

    BaiduTranslator.NAME: "Baidu translator 百度翻译 (Factx API)",
    YoudaoTranslator.NAME: "Youdao translator 有道翻译 (Factx API)",
    AzureOpenaiGPT.NAME: "Azure OpenAI GPT (Factx API)",
    ChatGlmGPT.NAME: "ChatGLM chatGPT 智谱AI (Factx API)",
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]