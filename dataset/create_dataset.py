import argparse
import tqdm
import json
import random

from llms.applications.scoring import ScoringAgent
from llms.applications.tmp_utils import set_logger
from llms.remote.ChatGPT import ChatGPTLLM
from llms.applications.scoring_prompts import DATA_GENERATE_PROMPT
OUTPUT_PATH = './origin.json'
ERROR_PATH = './error.json'
SAVE_PATH = './save.json'
topics = {
    "历史名人": "孔子",
    "历史事件": "诺曼底登陆",
    "职业身份": "消防员",
    "食物": "饺子",
    "菜名": "荔枝肉",
    "交通工具": "汽车",
    "城市县镇": "昆明市",
    "旅游景点": "滇池",
    "建筑": "卢浮宫",
    "科技产品": "手机",
    "知名品牌": "苹果",
    "文体活动": "街舞",
    "现代明星": "何炅",
    "货币经济": "货币乘数",
    "二次元人物": "刻晴",
    "动物": "猫",
    "植物": "含羞草",
    "自然景观": "闪电",
    "抽象概念": "友谊"
}
given_topics = {}
try:
    with open(SAVE_PATH, 'r', encoding='utf-8') as f:
        given_topics = json.load(f)
except FileNotFoundError:
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, default="../llms/remote/configs/wsx_gpt35.json")
    parser.add_argument("--prompt_language", type=str, default="en")
    args = parser.parse_args()

    # 定义一个Logger
    logger = set_logger("tmp.log")

    # 定义一个Agent
    chat_gpt = ChatGPTLLM(args.config_path)

    task_name = "Sentence Generation"
    language = "Chinese"
    task_definition = '''You need to generate sentences based on the given topic. The sentence you generate 
    must contain a certain amount of knowledge or information.'''

    steps = [
        "Base on the 'topic' given in [Input], generate several sentences as [SC] with certain amount of knowledge or "
        "information."
    ]

    guidance = [
        "You should strictly follow the [Steps] step by step.",
        "The sentence you generate must contain a certain amount of knowledge or information.",
        "There are some examples in [Examples] to help you judgement."
    ]

    output = {
        "sentence": "[SC]"
    }

    relations = {}

    # 示例
    examples = [
        {
            "Input": {
                "topic": "昆明"
            },
            "Output": {
                "sentence": "昆明，被誉为春城，以其四季如春的气候和丰富的自然景观吸引着无数游客，其中滇池和西山更是成为了昆明的标志性景点。"
            }
        }
    ]

    cnt = 500
    data = []
    errors = []
    try:
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(ERROR_PATH, 'r', encoding='utf-8') as f:
            errors = json.load(f)
    except FileNotFoundError:
        pass
    sc = ScoringAgent(logger, chat_gpt, task_name, DATA_GENERATE_PROMPT,
                      language, task_definition, guidance, steps, examples, relations, output)
    try:
        for i in tqdm.tqdm(range(cnt)):
            n = list(topics.keys())[random.randint(0,18)]
            v = topics[n]
            wl = ""
            try:
                for item in given_topics[n]:
                    wl += item + "，"
            except KeyError:
                pass
            q = f"""你是汉语词语大师，接下来我们将玩一个游戏。请遵守游戏规则，否则你将输掉游戏。
            [游戏规则] 
            1. 请随机给出一个属于"{n}"类别的词语；
            2. 你能且只能给出一个名词；
            3. 名词只能使用中文；
            4. 你所给出的词语不能是以下这些词语及他们的同义词：{wl}；
            5. 你需要直接输出这个名词，不能输出其他额外信息。
            """
            contexts = chat_gpt.create_prompt(q)
            topic = chat_gpt.request_llm(contexts)[-1]['content'].strip("。")
            logger.info(f"topic: {topic}")
            case_data = {
                "{{TGT}}": "topic",
                "{{TGT_VALUE}}": topic
            }
            sentence = sc.judge_a_case(case_data, mod=2)
            if isinstance(sentence, str):
                temp = {"sentence": sentence}
                data.append(temp)
            else:
                errors.append(sentence)
            cnt += 1
            try:
                if topic not in given_topics[n]:
                    given_topics[n].append(topic)
            except KeyError:
                given_topics[n] = [topic]
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(given_topics, f, indent=4, ensure_ascii=False)
    with open(ERROR_PATH, 'w', encoding='utf-8') as f:
        json.dump(errors, f, indent=4, ensure_ascii=False)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

