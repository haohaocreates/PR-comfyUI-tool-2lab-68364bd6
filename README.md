# comfyUI-tool-2lab

# 项目介绍 
为comfyUI集成非绘画类的能力，包括数据、算法、视频处理、大模型等，方便搭建更强大的工作流

# 后台配置 
调用api时，一般要配置api相关的apiId和apiKey。首先，把 properties_template.json 改名为 properties.json，然后在 properties.json 中填写你在各平台的apiId和apiKey

# 参数输入 
所有节点都同时允许前台和后台输入apiId和apiKey
- 前台：在comfyui节点上输入apiId和apiKey，优点是使用方便
- 后台：在properties.py中填写apiId和apiKey，优点是分享workflow时不会泄露apiId和apiKey

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
