# comfyUI-tool-2lab

# 项目介绍 
增强comfyUI系统能力

# 后台配置 
调用api时，一般要配置api相关的apiId和apiKey。首先，把 properties_template.json 改名为 properties.json，然后在 properties.json 中填写你在各平台的apiId和apiKey

# 技术依赖 
## ChatGLM
pip install zhipuai
## openAI & Azure OpenAI
pip install openai
### Azure
需要在Azure OpenAI Studio中预先注册和配置deployment (https://oai.azure.com/portal)

# 例子 example
见 example 目录

## GPT3.5
![workflows/gpt35-chat-example.png](example/gpt35-chat-example.png)
## GPT4 vision
![workflows/gpt-vision-example.png](example/gpt-vision-example.png)
## Azure GPT3.5
![workflows/Azure-gpt35-chat-example.png](example/Azure-gpt35-chat-example.png)
## 百度翻译 baidu translator
![workflows/baidu-translate-example.png](example/baidu-translate-example.png)
## 有道翻译 youdao translator
![workflows/youdao-translate-example.png](example/youdao-translate-example.png)
