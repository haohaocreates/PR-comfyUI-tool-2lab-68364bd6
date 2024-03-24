import json
import os

from ..constants import get_project_name, get_project_category, project_root

NODE_CATEGORY = get_project_category("llm")

class DirectChatGLMGpt:


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "model": (["chatglm_turbo",],
                          {"default": "chatglm_turbo"}),
            },
        }

    NAME = get_project_name('ChatGLM_GPT')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("text", )
    FUNCTION = "doWork"

    def doWork(self, api_key, model, prompt):
        try:
            config_path = os.path.join(project_root, 'properties.json')
            with open(config_path, 'r') as f:
                key_dict = json.load(f)
                api_key = key_dict.get('chatGlm_gpt_api_key')
        except:
            print("failed to load properties")
            pass

        # 要使用时才import
        import zhipuai
        zhipuai.api_key = api_key
        messages = [
            {"role": "user", "content": prompt}]
        response = zhipuai.model_api.invoke(
            model=model,
            prompt=messages,
            # prompt=[{"role": "user", "content": "人工智能"}],
            top_p=0.7,
            temperature=0.9,
        )

        if response['code']==200:
            try:
                result = response['data']['choices'][0]['content']
                # print("result = ", result)
                return (result,)
            except:
                print ("chatGlm api failed. chatGlm api 调用失败",)
                pass
        return ("",)