# https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/cf2772fab0af5573da775e7437e6acdca424f26e/modules/generation_parameters_copypaste.py#L211
import re
import json
import webuiapi
# from pydantic import BaseModel, Field

re_param_code = r'\s*(\w[\w \-/]+):\s*("(?:\\.|[^\\"])+"|[^,]*)(?:,|$)'
re_imagesize = re.compile(r"^(\d+)x(\d+)$")
re_param = re.compile(re_param_code)

class SDTools:
    def __init__(self, host:str= '127.0.0.1', port:int=7860, username:str=None, password:str=None, use_https:bool=False):
        self.api = webuiapi.WebUIApi(host=host, port=port, use_https=use_https)
        if username is not None:
            self.api.set_auth(username, password)
        self.models = self.api.util_get_model_names()
        self.default_model = 'v1-5-pruned'
        self.sytles = self.api.get_prompt_styles()

    
    def txt2img(self, prompt:str, styles=[]):
        res = self.parse_generation_parametes(prompt)
        result = self.api.txt2img(styles=["万能通用"],
                                  batch_size=1,
                                  **res,
                                )
        return result.image


    @staticmethod
    def unquote(text):
        if len(text) == 0 or text[0] != '"' or text[-1] != '"':
            return text

        try:
            return json.loads(text)
        except Exception:
            return text

    def parse_generation_parametes(self, x:str):
        res = {}
        prompt = ""
        negative_prompt = ""

        done_with_prompt = False

        *lines, lastline = x.strip().split("\n")
        if len(re_param.findall(lastline)) < 3:
            lines.append(lastline)
            lastline = ''

        for line in lines:
            line = line.strip()
            if line.startswith("Negative prompt:"):
                done_with_prompt = True
                line = line[16:].strip()
            if done_with_prompt:
                negative_prompt += ("" if negative_prompt == "" else "\n") + line
            else:
                prompt += ("" if prompt == "" else "\n") + line

        res["prompt"] = prompt
        res["negative_prompt"] = negative_prompt
        temp = {}
        for k, v in re_param.findall(lastline):
            try:
                if v[0] == '"' and v[-1] == '"':
                    v = self.unquote(v)
                temp[k] = v
            except Exception:
                print(f"Error parsing \"{k}: {v}\"", Exception)

        
        if "Steps" in temp: res["steps"] = temp["Steps"]
        if "Sampler" in temp: res["sampler_name"] = temp['Sampler']
        if "CFG scale" in temp: res["cfg_scale"] = temp["CFG scale"]
        if "Seed" in temp: res["seed"] = temp["Seed"]
        if "Size" in temp:
            m = re_imagesize.match(temp["Size"])
            res["width"] = m.group(1)
            res["height"] = m.group(2)

        if "Denoising strength" in temp: res["denoising_strength"] = temp["Denoising strength"]
        # if "Clip skip" in temp: res["Clip skip"] = temp["Clip skip"]
        if "Model" in temp: 
            for model in self.models:
                if temp["Model"] in model:
                    # set model (find closest match)
                    self.api.util_set_model(temp["Model"])
        else:
            self.api.util_set_model(self.default_model)
            
        if "Hires upscaler" in temp: 
            res["enable_hr"] = True
            # Hires checkpoint 被固定为 Use same checkpoint
            if "Hires steps" in temp: res["hr_second_pass_steps"] = temp["Hires steps"]
            if "Hires upscale" in temp: res["hr_scale"] = str(float(temp["Hires upscale"]))
            if "Hires upscaler" in temp: res["hr_upscaler"] = temp["Hires upscaler"]
            if "Hires resize" in temp:
                m = re_imagesize.match(temp["Hires resize"])
                res["hr_resize_x"] = m.group(1)
                res["hr_resize_y"] = m.group(2)     
        # Missing CLIP skip means it was set to 1 (the default)

        res['adetailer'] = []
        if "ADetailer model" in temp:
            ads1 = webuiapi.ADetailer(ad_model=temp["ADetailer model"],
                                    ad_prompt=temp["ADetailer prompt"] if "ADetailer prompt" in temp else "",
                                    ad_negative_prompt=temp["ADetailer negative prompt"] if "ADetailer Negative prompt" in temp else "",
                                    ad_mask_blur=temp["ADetailer mask blur"] if "ADetailer mask blur" in temp else 4,
                                    ad_confidence=temp["ADetailer confidence"] if "ADetailer confidence" in temp else 0.3,
                                    ad_dilate_erode=temp["ADetailer dilate erode"] if "ADetailer dilate erode" in temp else 4,
                                    ad_inpaint_only_masked=temp["ADetailer inpaint only masked"] if "ADetailer inpaint only masked" in temp else True,
                                    ad_inpaint_only_masked_padding=temp["ADetailer inpaint padding"] if "ADetailer inpaint padding" in temp else 32,
                                    ad_denoising_strength=temp["ADetailer denoising strength"] if "ADetailer denoising strength" in temp else 0.4,
                                    ad_controlnet_model=temp["ADetailer ControlNet model"] if "ADetailer ControlNet model" in temp else "None",
                                    ad_controlnet_module=temp["ADetailer ControlNet module"] if "ADetailer ControlNet module" in temp else "None",
                                    ad_controlnet_weight=temp["ADetailer ControlNet weight"] if "ADetailer ControlNet weight" in temp else 1.0,
                                    ad_controlnet_guidance_start=temp["ADetailer ControlNet guidance start"] if "ADetailer ControlNet guidance start" in temp else 0.0,
                                    ad_controlnet_guidance_end=temp["ADetailer ControlNet guidance end"] if "ADetailer ControlNet guidance end" in temp else 1.0
                                    )
            res['adetailer'].append(ads1)
        if "ADetailer model 2nd" in temp:
            ads2 = webuiapi.ADetailer(ad_model=temp["ADetailer model 2nd"],
                                    ad_prompt=temp["ADetailer prompt 2nd"] if "ADetailer prompt 2nd" in temp else "",
                                    ad_negative_prompt=temp["ADetailer negative prompt 2nd"] if "ADetailer Negative prompt 2nd" in temp else "",
                                    ad_mask_blur=temp["ADetailer mask blur 2nd"] if "ADetailer mask blur 2nd" in temp else 4,
                                    ad_confidence=temp["ADetailer confidence 2nd"] if "ADetailer confidence 2nd" in temp else 0.3,
                                    ad_dilate_erode=temp["ADetailer dilate erode 2nd"] if "ADetailer dilate erode 2nd" in temp else 4,
                                    ad_inpaint_only_masked=temp["ADetailer inpaint only masked 2nd"] if "ADetailer inpaint only masked 2nd" in temp else True,
                                    ad_inpaint_only_masked_padding=temp["ADetailer inpaint padding 2nd"] if "ADetailer inpaint padding 2nd" in temp else 32,
                                    ad_denoising_strength=temp["ADetailer denoising strength 2nd"] if "ADetailer denoising strength 2nd" in temp else 0.4,
                                    ad_controlnet_model=temp["ADetailer ControlNet model 2nd"] if "ADetailer ControlNet model 2nd" in temp else "None",
                                    ad_controlnet_module=temp["ADetailer ControlNet module 2nd"] if "ADetailer ControlNet module 2nd" in temp else "None",
                                    ad_controlnet_weight=temp["ADetailer ControlNet weight 2nd"] if "ADetailer ControlNet weight 2nd" in temp else 1.0,
                                    ad_controlnet_guidance_start=temp["ADetailer ControlNet guidance start 2nd"] if "ADetailer ControlNet guidance start 2nd" in temp else 0.0,
                                    ad_controlnet_guidance_end=temp["ADetailer ControlNet guidance end 2nd"] if "ADetailer ControlNet guidance end 2nd" in temp else 1.0
                                    )
            res['adetailer'].append(ads2)
        if "ADetailer model 3rd" in temp:
            ads3 = webuiapi.ADetailer(ad_model=temp["ADetailer model 3rd"],
                                    ad_prompt=temp["ADetailer prompt 3rd"] if "ADetailer prompt 3rd" in temp else "",
                                    ad_negative_prompt=temp["ADetailer negative prompt 3rd"] if "ADetailer Negative prompt 3rd" in temp else "",
                                    ad_mask_blur=temp["ADetailer mask blur 3rd"] if "ADetailer mask blur 3rd" in temp else 4,
                                    ad_confidence=temp["ADetailer confidence 3rd"] if "ADetailer confidence 3rd" in temp else 0.3,
                                    ad_dilate_erode=temp["ADetailer dilate erode 3rd"] if "ADetailer dilate erode 3rd" in temp else 4,
                                    ad_inpaint_only_masked=temp["ADetailer inpaint only masked 3rd"] if "ADetailer inpaint only masked 3rd" in temp else True,
                                    ad_inpaint_only_masked_padding=temp["ADetailer inpaint padding 3rd"] if "ADetailer inpaint padding 3rd" in temp else 32,
                                    ad_denoising_strength=temp["ADetailer denoising strength 3rd"] if "ADetailer denoising strength 3rd" in temp else 0.4,
                                    ad_controlnet_model=temp["ADetailer ControlNet model 3rd"] if "ADetailer ControlNet model 3rd" in temp else "None",
                                    ad_controlnet_module=temp["ADetailer ControlNet module 3rd"] if "ADetailer ControlNet module 3rd" in temp else "None",
                                    ad_controlnet_weight=temp["ADetailer ControlNet weight 3rd"] if "ADetailer ControlNet weight 3rd" in temp else 1.0,
                                    ad_controlnet_guidance_start=temp["ADetailer ControlNet guidance start 3rd"] if "ADetailer ControlNet guidance start 3rd" in temp else 0.0,
                                    ad_controlnet_guidance_end=temp["ADetailer ControlNet guidance end 3rd"] if "ADetailer ControlNet guidance end 3rd" in temp else 1.0
                                    )
            res['adetailer'].append(ads3)
        
        return res
