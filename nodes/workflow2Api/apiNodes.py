import json
import os
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import folder_paths
import torch
import hashlib
from ..common.fields import BOOL_TRUE, BOOL_FALSE
import comfy.sd
import comfy.utils
from ..constants import get_project_name, get_project_category, project_root, userKey_file
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args

NODE_CATEGORY = get_project_category("workflow2Api")

class AnyType(str):
  def __ne__(self, __value: object) -> bool:
    return False

any = AnyType("*")

class InputImage:
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

    NAME = get_project_name('InputImage')
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

class InputSeed:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "export": BOOL_TRUE,
        },
        }

    NAME = get_project_name('InputSeed')
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
    NAME = get_project_name('OutputText')
    CATEGORY = NODE_CATEGORY
    FUNCTION = "doWork"
    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True

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

        return {"ui": {"text": text}, "result": (text,)}

class OutputImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"images": ("IMAGE", ),
                     "filename_prefix": ("STRING", {"default": "2lab/img"})},
                     "metadata": (["disable","enable"],),
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    NAME = get_project_name('OutputImage')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ()
    FUNCTION = "doWork"
    OUTPUT_NODE = True

    def doWork(self, images, filename_prefix="2lab/img",metadata="disable", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        print("filename_prefix = ",filename_prefix)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        print("full_output_folder = ",full_output_folder)
        print("filename = ",filename)
        print("counter = ",counter)
        print("subfolder = ",subfolder)
        print("filename_prefix = ",filename_prefix)
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if (not args.disable_metadata) and (metadata=="enable"):
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, }

class InputUserKey:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                "userKey": ("STRING", {"default": '', "multiline": False}),
            },
        }

    NAME = get_project_name('InputUserKey')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ()
    FUNCTION = "doWork"
    OUTPUT_NODE = True

    def doWork(self, userKey):
        if userKey is None or userKey == '':
            raise ValueError('please input user key')
        else:
            # 如果覆盖userKey不为空，覆盖userKey
            with open(userKey_file, 'w', encoding='utf-8') as file:
                # 写入文本
                file.write(userKey)
        return { "ui": { "userKey": userKey }, }

class PublishWorkflow:
    def __init__(s):
        pass
    @classmethod
    def INPUT_TYPES(c):
        return {
            "required": {
                "trigger": (any, {}),
                "id": ("STRING", {"default": "workflowId", "multiline": False}),
                "name": ("STRING", {"default": "文生图", "multiline": False}),
                "desc": ("STRING", {"default": "", "multiline": False}),
                "publish": BOOL_FALSE,
            },
        }

    NAME = get_project_name('PublishWorkflow')
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("BOOL","STRING",)
    RETURN_NAMES = ("publish","id",)
    FUNCTION = "doWork"
    OUTPUT_NODE = True

    def doWork(self, id, name, desc, publish, trigger=None):
        text = ''
        if publish:
            text = f'项目正在发布中，请到弹出窗口中查看绘图界面。如果没有弹出窗口，请检查是否被浏览器拦截。弹出窗口如果显示工作流不存在，是因为后台处理需要几分钟，请耐心等待。如果遇到其他问题，请请到http://www.2lab.cn/pb/contactus 咨询技术支持。'
        else:
            text = '项目未发布。如果要发布本工作流到网页，请把参数publish设为True'

        return {"ui": {"text": [text, ]}, "result": (publish, id,)}

class AvailableCheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"ckpt_name": (["sd15/2d/counterfeitV30_v30",
                                            "sd15/3d/hellonijicute25d_V13g",
                                            "sd15/dreamshaper_8",
                                            "sd15/real/majicmixRealistic_v7",
                                            "sd15/real/majicmixSombre_v20",
                                            "sdxl/2d/animagineXLV31_v31",
                                            "sdxl/2d/counterfeitxl_v25",
                                            "sdxl/3d/dynavisionXLAllInOneStylized_releaseV0610Bakedvae",
                                            "sdxl/3d/samaritan3dCartoon_v40SDXL",
                                            "sdxl/dreamshaperXL_lightningDPMSDE",
                                            "sdxl/dreamshaperXL_v21TurboDPMSDE",
                                            "sdxl/real/realisticStockPhoto_v10",
                                            "svd/svd",
                                            "svd/svd_xt",],),
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
