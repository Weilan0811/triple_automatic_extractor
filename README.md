# **基于大语言模型的批量三元组抽取**

本项目基于GPT远程大模型和Llama本地大模型，设计prompt构造特定功能智能体，实现了批量抽取常识知识三元组的功能。用户可以以特定的格式构造数据集后，使用该项目批量抽取数据集中句子的常识知识三元组信息。

## **使用方法**

### 一、数据集的导入

本项目支持如下格式的.json数据集：

```json
[
    {
        "sentence": "杨幂，是中国知名的女演员和歌手，她凭借着出色的演技和甜美的外貌赢得了广大观众的喜爱，曾经参演过多部热播剧，如《欢乐颂》等。"
    },
]
```

用户可以使用"./dataset/origin.json"中给定的数据集进行测试，也可以自行构造数据集。在"./dataset/create\_dataset.py"中，我们给出了一种使用大模型构造数据集的方法，用户可以参考使用，这里不再过多介绍。

### 二、运行环境加载

用户可以在虚拟环境中使用以下命令配置环境

```bash
pip install -r requirements.txt
```

### 三、运行项目

使用此命令开始批量抽取三元组：

```bash
python main.py --input_path "./dataset/origin.json" --thread_num 3 --save_file
```

## **运行命令参数说明**

*   model: 指定使用的模型，可选项为"gpt"和"lamma"；
*   config\_path: 远程大模型的配置文件所在位置，需要提供大模型API的cdkey等信息；
*   input\_path: 输入数据集存放位置；
*   output\_path: 提取三元组后的文件保存地址；
*   save\_path: 程序断点保存的缓存文件保存路径；
*   log\_path: 程序运行日志保存路径；
*   prompt: 所使用的prompt类型，可选项为"simple", "medium"和"full"，远程大模型推荐使用full，本地大模型推荐使用simple；
*   prompt\_language: 所使用的prompt语言，可选项为"en"和"zh"
*   retries: 抽取异常时最大重试次数，默认为3次
*   thread\_num: 并发抽取的进程数，进程数越高速度越快，但程序的不稳定性也会提高，默认为1即不使用多进程
*   auto\_save\_round: 每个线程在抽取若干条数据后进行自动保存，数值越高程序越稳定，但程序效率越低，默认为5
*   save\_file: 是否需要在自动保存程序状态时保存输出文件

## **附：Llama本地部署指南**

*   ***Llama 2*** 是Meta AI发布的一系列开源语言大模型（LLMs），参数规模有***70亿***、***130亿***等等。
*   以下内容描述模型的获取方式与在 ***Linux Ubuntu*** 环境下的模型本地量化部署流程参考。

### 一、模型获取

*   本项目使用的 Llama 2 系列下的中文预训练模型 ***Atom*** 来自于 [Llama中文社区](https://github.com/LlamaFamily/Llama-Chinese)
*   Atom 系列模型包含Atom-13B、Atom-7B和Atom-1B，其中 ***Atom-7B-Chat*** 为对话场景进行了优化，是具有32k长度的对话模型，并且完全开源支持商用
*   获取链接 [HuggingFace](https://huggingface.co/FlagAlpha/Atom-7B-Chat)

### 二、Linux环境下基于llama.cpp的量化部署

接下来介绍基于[llama.cpp](https://github.com/ggerganov/llama.cpp)的模型量化方法与本地部署步骤，Linux环境下支持本地CPU、GPU推理。运行前请确保：

1.  系统应有 `make` （Linux系统自带）编译工具
2.  建议使用Python 3.10及以上环境
3.  正确安装 **requirements.txt** 中要求的内容

#### 步骤1：克隆并编译llama.cpp

1.  克隆最新版llama.cpp仓库代码

```bash
git clone https://github.com/ggerganov/llama.cpp
```

1.  对llama.cpp进行编译，编译后生成 `./main` 和 `./quantize` 二进制文件,为了使项目能够启用GPU推理，采用了和cuBLAS一起编译的命令如下：

```bash
make LLAMA_CUBLAS=1
```

#### 步骤2：生成量化版本模型

在进行量化版本生成之前，请在llama.cpp项目下新建 `zh-models` 文件夹并且正确将下载的模型置于如下路径结构中：

> 7B
>
> > gitattributes\
> > README.md\
> > config.json\
> > configuration\_atom.py\
> > generation\_config.jsom\
> > model-00001-of-00003.safetensors\
> > model-00002-of-00003.safetensors\
> > model-00003-of-00003.safetensors\
> > model.safetensors.index.json\
> > model\_atom.py\
> > special\_tokens\_map.json\
> > tokenizer.model\
> > tokenizer\_config.json
>
> tokenizer.model

接下来将完整的模型权重转换为GGML的FP16格式，生成路径为 `zh-models/7B/ggml-model-f16.gguf` 。之后可以进一步对FP16模型进行自己需要的格式的量化，如下为8-bit量化代码，生成量化模型文件路径为 `zh-models/7B/ggml-model-q8_0.gguf`。

```bash
python convert.py zh-models/7B/
./quantize ./zh-models/7B/ggml-model-f16.gguf ./zh-models/7B/ggml-model-q8_0.gguf q8_0
```

#### 步骤3.搭建server

llama.cpp可以架设server提供API调用。通过根目录下 `./server` 启动服务，默认监听 `127.0.0.1:8080` 。可以指定模型路径、上下文窗口大小、是否支持GPU解码（指定 `-ngl` 参数）。更多参数设置详见 <https://github.com/ggerganov/llama.cpp/tree/master/examples/server>\
运行以下命令：

```bash
./server -m ./zh-models/7B/ggml-model-q8_0.gguf -c 4096 --host 0.0.0.0 --port 8080 -ngl 999
```

