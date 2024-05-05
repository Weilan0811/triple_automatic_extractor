# **基于大语言模型的批量三元组抽取**

正文

## **使用方法**

正文

## **参数说明**

正文

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

