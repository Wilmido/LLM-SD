# LLM + Stable Diffusion
在不改变LLM的原始能力情况下，通过调用sd webui api，让LLM“具有”绘图的能力.
While preserving the inherent abilities of LLM, the incorporation of the SD WebUI API empowers LLM to draw pictures.
本项目支持在输入文本中指定negative prompt, sd和lora模型等。
This project supports specifying negative prompts, sd and lora models in text.

## Introduction
这个项目是基于[webuiapi](https://github.com/mix1009/sdwebuiapi)的二次开发，使用[AUTOMATIC1111/webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)。
This project is based on [webuiapi](https://github.com/mix1009/sdwebuiapi) using [AUTOMATIC1111/webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

本项目实现了prompt解析部分，能够在输入的时候指定sd模型，lora等生成参数。在LangChain Agent部分，实现了通过识别特定触发词来决定执行的工具。
The project has successfully implemented the prompt parsing component, allowing for the specification of SD models, Lora, and other generation parameters during input. Moreover, in the LangChain Agent section, tools are implemented that determine execution by recognizing specific trigger words.

## How it works?
在[demo.ipynb](demo.ipynb)中实现了两种场景，第一种是直接用**chain**的形式进行关键词判断;另外一种则是通过**langchain Agent**使用自定义工具来调用。通过判断输入文本的是否具有触发词来决定是绘图还是聊天。
Two cases are implemented in [demo.ipynb](demo.ipynb), the first is a direct keyword determination with **LLM chain**; the other is invoked using a custom tool via **langchain Agent**. By determining whether the input text has a trigger word to determine LLM whether to draw or chat.

具体来说是以下步骤：
Specifically the following steps:
1. 判断用户输入文本是否存在特定Trigger词来判断是否需要文生图 
   Determine whether a specific Trigger word exists in the user's input text to determine whether the text2img is needed.
2. 用户输入文本的解析成sd的prompt
   The user input text is parsed into sd prompt.
3. 调用sd的api生成对应的图片。
   Call the api of sd webui to generate the corresponding images.

# Getting Start
## Setup
- 在开始之前请确保已经运行了stable diffusion webui，并且使用 “--api”模式启动你的stable diffusion，`set COMMANDLINE_ARGS=--api`
  Make sure you have stable diffusion webui running before you start, and start it with "--api" mode, `set COMMANDLINE_ARGS=--api`
- 安装webuiapi
```shell
$ pip install webuiapi
```
## Example
下面是一个简单的例子，展示promp的样子：
Here's a simple example of what promp looks like:
```python
from sd_tools import SDTools
input = """
Seeing plants and flowers from the ground, view from below, atmospheric dreamscape painting, dream scenery art, highly detailed visionary art, cgi style, vibrant oil painting, splash art, Cozy mystery, masterpiece 8k wallpapper, neoplasticism, Unreal Engine, dramatic lighting
Negative prompt: worst quality, low quality, extra digits,
Steps: 43, Size: 512x512, Seed: 12415920, Sampler: Euler a, CFG scale: 7, Clip skip: 1
"""
tool = SDTools("127.0.0.1", 7860) # host, port
tool.txt2img(input)
``` 
![example](images/output.png)

## Note
- prompt模板对应的关键字均来自 AUTOMATIC1111/stable-diffusion-webui，可以从webui上复制一张生成的图片(或者从civitai上)体验。
  The prompt template corresponds to keywords from AUTOMATIC1111/stable-diffusion-webui, and you can get it from the genrated image by sd webui or [civitai](https://civitai.com/).
  - 要求第一行为prompt(没有prompt关键词)，之后负向提示词的开头为“Negative prompt:”
    Requires the first line to be prompt (no prompt keyword), followed by the negative prompt that begins with "Negative prompt:"
  - 提示词都不限定行数。但是最后一行必须是所有和模型相关的参数，**即使没有也必须要为空**
    None of the prompts limit the number of lines. But the last line must be all the parameters related to the model, **it must be empty even if there are none**
- 关于Style参数，由于一般通过webui的png info获取的prompt已经涵盖了对应的提示词，因此style参数作废。
  Regarding the Style parameter, the style parameter is invalidated because the prompts obtained through the sdwebui png info already cover the corresponding prompt words.
- 设置trigger的原因在于基于用户输入文本的意图来判断用户是否画图，非常依赖LLM本身的能力。本项目初衷即是让所有LLM都能够使用，所以提出检测文本是否含有trigger来快速进行判断。
The reason for setting a trigger is to determine whether to use the sd based on the intent of the user's input text, which is very dependent on the capabilities of the LLM itself. The original purpose of this project is to enable all LLMs to use it, so I propose to detect whether the text contains a trigger to make a quick judgment.

## Extension support
详情见[webuiapi](https://github.com/mix1009/sdwebuiapi)中`Readmel.md`的Extension support。本项目二次开发的时候封装了一些参数，需要自己修改。
For details, see Extension support of `Readmel.md` in [webuiapi](https://github.com/mix1009/sdwebuiapi). This project encapsulates some parameters, which need to be modified by yourself.
目前能够完全正常使用ADetailer插件，只需要在prompt最后一行添加相应参数即可，见`demo.ipynb`中的例子。
Currently able to use the ADetailer plugin fully functional, just need to add the appropriate parameter to the last line of the prompt, see the example in `demo.ipynb`.

## About this project
<!-- 目前的让LLM实现绘图的方法，一部分是通过安装huggingface的diffuser库，使用pipline绘图。另外就是本项目使用的sd webui的api调用。然而，这些做法只能自定义prompt，无法自定义模型、lora等，不能满足需求，因此建立了本项目-->
本项目对于prompt的处理仍然是最简单的解析，距离打造一个多模态Agent仍非常遥远。
本人对后端一窍不通，sdwebuiapi的很多功能，例如图生图等功能在与LLM对话中没有办法使用。