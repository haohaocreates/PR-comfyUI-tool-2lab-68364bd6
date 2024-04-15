import json
import os
from PIL import Image, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths
import torch
import hashlib
from ..common.fields import BOOL_TRUE, BOOL_FALSE
import comfy.sd
import comfy.utils
from ..constants import get_project_name, get_project_category, project_root

NODE_CATEGORY = get_project_category("workflow2Api")

config_path = os.path.join(project_root, 'properties.json')
with open(config_path, 'r') as f:
    key_dict = json.load(f)
    workerKey = key_dict.get('2lab_key')
    print(f'2lab_key = {workerKey}')

class AnyType(str):
  """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

  def __ne__(self, __value: object) -> bool:
    return False


any = AnyType("*")


class DisplayAny:
  """Display any data node."""

  NAME = get_project_name('DisplayAny')
  CATEGORY = NODE_CATEGORY

  @classmethod
  def INPUT_TYPES(cls):  # pylint: disable = invalid-name, missing-function-docstring
    return {
      "required": {
        "source": (any, {}),
      },
    }

  RETURN_TYPES = ()
  FUNCTION = "main"
  OUTPUT_NODE = True

  def main(self, source=None):
    value = 'None'
    if source is not None:
      try:
        value = json.dumps(source)
      except Exception:
        try:
          value = str(source)
        except Exception:
          value = 'source exists, but could not be serialized.'

    return {"ui": {"text": (value,)}}
class ShowText1:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",},
        }

    INPUT_IS_LIST = True
    NAME = get_project_name('show_text1')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string1",)
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True
    FUNCTION = "doWork"

    def doWork(self, text, unique_id=None, extra_pnginfo=None):
        if unique_id is not None and extra_pnginfo is not None:
            if not isinstance(extra_pnginfo, list):
                print("Error: extra_pnginfo is not a list")
            elif (
                not isinstance(extra_pnginfo[0], dict)
                or "workflow" not in extra_pnginfo[0]
            ):
                print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
            else:
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"] if str(x["id"]) == str(unique_id[0])),
                    None,
                )
                if node:
                    node["widgets_values"] = [text]
        return {"ui": {"url": [text, ]}, "result": (text,)}

class ShowText2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    NAME = get_project_name('show_text2')
    CATEGORY = NODE_CATEGORY

    def notify(self, text, unique_id=None, extra_pnginfo=None):
        if unique_id is not None and extra_pnginfo is not None:
            if not isinstance(extra_pnginfo, list):
                print("Error: extra_pnginfo is not a list")
            elif (
                not isinstance(extra_pnginfo[0], dict)
                or "workflow" not in extra_pnginfo[0]
            ):
                print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
            else:
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"] if str(x["id"]) == str(unique_id[0])),
                    None,
                )
                if node:
                    node["widgets_values"] = [text]

        return {"ui": {"text": text}, "result": (text,)}

class ShowText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    NAME = get_project_name('show_text')
    CATEGORY = NODE_CATEGORY

    def notify(self, text, unique_id=None, extra_pnginfo=None):
        if unique_id is not None and extra_pnginfo is not None:
            if not isinstance(extra_pnginfo, list):
                print("Error: extra_pnginfo is not a list")
            elif (
                not isinstance(extra_pnginfo[0], dict)
                or "workflow" not in extra_pnginfo[0]
            ):
                print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
            else:
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"] if str(x["id"]) == str(unique_id[0])),
                    None,
                )
                if node:
                    node["widgets_values"] = [text]

        return {"ui": {"text": text}, "result": (text,)}

class LoadImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True}),
                     "desc": ("STRING", {"default": "图片", "multiline": False}),
                     "export": BOOL_TRUE,
                     },
                }

    NAME = get_project_name('LoadImage')
    CATEGORY = NODE_CATEGORY

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"

    def load_image(self, image, desc, export):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)
        output_images = []
        output_masks = []
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


class Seed:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "export": BOOL_TRUE,
        },
        }

    NAME = get_project_name('Seed')
    CATEGORY = NODE_CATEGORY

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "doWork"
    OUTPUT_NODE = True

    @staticmethod
    def doWork(seed, export):
        return seed,


class InputInt:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "int": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "desc": ("STRING", {"default": "", "multiline": False}),
            "export": BOOL_TRUE,
        },
        }

    NAME = get_project_name('InputInt')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("INT", "FLOAT", "STRING",)
    RETURN_NAMES = ("int", "float", "text",)
    FUNCTION = "doWork"

    @staticmethod
    def doWork(int, desc, export):
        return int, float(int), str(int)


class InputFloat:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "float": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "desc": ("STRING", {"default": "", "multiline": False}),
            "export": BOOL_TRUE,
        },
        }

    NAME = get_project_name('InputFloat')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("FLOAT", "INT", "STRING",)
    RETURN_NAMES = ("float", "int", "text",)
    FUNCTION = "doWork"

    @staticmethod
    def doWork(float, desc, export):
        return float, int(float), str(float)


class InputText:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"default": "", "multiline": True}),
            "type": (["prompt", "word", "seg"], {"default": "prompt"}),
            "desc": ("STRING", {"default": "", "multiline": False}),
            "export": BOOL_TRUE,
        },
        }

    NAME = get_project_name('InputText')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"

    @staticmethod
    def doWork(text, type, desc, export):
        return text,


class OutputText:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "outputTexts": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
        },
        }

    NAME = get_project_name('OutputText')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("outputTexts",)
    FUNCTION = "doWork"

    def doWork(self, outputStrings=None, ):
        return outputStrings,


class OutputImage:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "outputImages": ("IMAGE",),
        },
        }

    NAME = get_project_name('OutputImage')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("outputImages",)
    FUNCTION = "doWork"

    def doWork(self, outputImages=None):
        return outputImages,


class OutputVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "outputVideos": ("VIDEO",),
        },
        }

    NAME = get_project_name('OutputVideo')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("outputVideos",)
    FUNCTION = "doWork"

    def doWork(self, outputVideos=None):
        return outputVideos,


class PublishWorkflow:
    userKey = 'initKey'
    def __init__(s):
        pass
        # print(f'PublishWorkflow __init__')
        # try:
        #     config_path = os.path.join(project_root, 'properties.json')
        #     with open(config_path, 'r') as f:
        #         key_dict = json.load(f)
        #         s.userKey = key_dict.get('2lab_key')
        #         print(f'2lab_key = {s.userKey}')
        # except:
        #     raise Exception('在properties.json中没有找到2lab_key')
    @classmethod
    def INPUT_TYPES(c):
        return {
            "required": {
                "trigger": (any, {}),
                "userKey": ("STRING", {"default": workerKey, "multiline": False}),
                "id": ("STRING", {"default": "txt2img", "multiline": False}),
                "name": ("STRING", {"default": "文生图", "multiline": False}),
                "desc": ("STRING", {"default": "", "multiline": False}),
                "publish": BOOL_FALSE,
            },

        }

    NAME = get_project_name('PublishWorkflow')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "doWork"
    OUTPUT_NODE = True

    def doWork(self, userKey, id, name, desc, publish, trigger=None):
        print(f"trigger = {trigger}")
        print(f"userKey = {userKey}")
        text = ''
        if userKey is None or userKey == '':
            text = '找不到userKey。请在配置文件properties.json中输入2lab_key。如果没有2lab_key，请到http://www.2lab.cn/pb/applyKey申请。'
        elif publish:
            text = '项目发布成功。请到弹出窗口中查看绘图界面（后台处理需要几分钟，请稍等）'
        else:
            text = '项目未发布。如果需要发布项目到网页，请把publish设为True'

        return {"ui": {"text": [text, ]}, "result": (text,)}


class AvailableCheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"ckpt_name": (["sd15/dreamshaper_8.safetensors",
                                            "sd15/2d/counterfeitV30_v30.safetensors",
                                            "sd15/2d/revAnimated_v2Rebirth.safetensors",
                                            "sd15/3d/hellonijicute25d_V13g.safetensors",
                                            "sd15/real/epicphotogasm_ultimateFidelity.safetensors",
                                            "sd15/real/leosamsFilmgirlUltra_ultraBaseModel.safetensors",
                                            "sd15/real/majicmixRealistic_v7.safetensors",
                                            "sd15/real/majicmixSombre_v20.safetensors",
                                            "sd15/real/realisticVisionV60B1_v60B1VAE",
                                            "sdxl/dreamshaperXL_lightningDPMSDE.safetensors",
                                            "sdxl/dreamshaperXL_v21TurboDPMSDE.safetensors.safetensors",
                                            "sdxl/juggernautXL_v9Rdphoto2Lightning",
                                            "sdxl/juggernautXL_v9Rundiffusionphoto2.safetensors",
                                            "sdxl/2d/animagineXLV31_v31.safetensors",
                                            "sdxl/2d/counterfeitxl_v25.safetensors",
                                            "sdxl/2d/元气动漫_2D_2.5D_V1.0.safetensors",
                                            "sdxl/3d/dynavisionXLAllInOneStylized_releaseV0610Bakedvae.safetensors",
                                            "sdxl/3d/MR 3DQ _SDXL V0.2.safetensors",
                                            "sdxl/3d/samaritan3dCartoon_v40SDXL.safetensors",
                                            "sdxl/3d/starlightXLAnimated_v3.safetensors",
                                            "sdxl/real/leosamsHelloworldXL_hw50EulerALightning.safetensors"],),
                             }
                }

    NAME = get_project_name('AvailableCheckpointLoader')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    def load_checkpoint(self, ckpt_name, output_vae=True, output_clip=True):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)

        print("ckpt_path:", ckpt_path)
        if not ckpt_path:
            raise ValueError('file not exists : ' + ckpt_name)

        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True,
                                                    embedding_directory=folder_paths.get_folder_paths("embeddings"))
        return out[:3]


class AvailableVAELoader:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"vae_name": (["vae-ft-mse-840000-ema-pruned.safetensors",
                                           "sdxl_vae.safetensors",
                                           "clearvae_v23.safetensors",
                                           "vae-ft-mse-840000-ema-pruned.safetensors"],)}}

    NAME = get_project_name('AvailableVAELoader')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("VAE",)
    FUNCTION = "load_vae"

    def load_vae(self, vae_name):
        vae_path = folder_paths.get_full_path("vae", vae_name)
        sd = comfy.utils.load_torch_file(vae_path)
        vae = comfy.sd.VAE(sd=sd)
        return (vae,)
