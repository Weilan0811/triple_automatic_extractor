import argparse
import json
import time

from llms.applications.scoring_prompts import TEXT_EVAL_GENERAL_PROMPT_PATTERN, PROMPT_SIMPLE, PROMPT_SIMPLEST, TEXT_EVAL_GENERAL_PROMPT_PATTERN_CHINESE, CHECK_PROMPT
from llms.applications.tmp_utils import set_logger
from llms.remote import RemoteLLMs
from llms.remote.ChatGPT import ChatGPTLLM
from llms.remote.MyLlama2 import LocalLlama


class ScoringAgent:
    def __init__(self, log, llm_model: RemoteLLMs, task_name: str, prompt_pattern: str,
                 language: str, task_definition: str, guidance: list,
                 steps: list, examples: list, relations: dict, output: dict):
        """

        :param log: 输出log文件
        :param llm_model: 给定一个RemoteLLMs的实例化对象
        :param task_name: 任务名称
        :param prompt_pattern: prompt模板
        :param language: 任务使用语言
        :param task_definition: 任务描述
        :param guidance: 任务指南
        :param steps: 任务步骤
        :param examples: 任务实例
        :param output: 任务输出
        """
        self.logger = log
        self.llm_model = llm_model
        self.prompt_pattern = prompt_pattern

        # 处理任务步骤
        for i, step in enumerate(steps):
            steps[i] = "%d. %s" % (i + 1, step)
        self.step = "\n".join(steps)

        for i, guide in enumerate(guidance):
            guidance[i] = "%d. %s" % (i + 1, guide)
        self.guidance = "\n".join(guidance)

        # 处理为json
        self.examples = json.dumps(examples, ensure_ascii=False, indent=4)
        self.relations = json.dumps(relations, ensure_ascii=False, indent=4)
        self.output = json.dumps(output, ensure_ascii=False)

        self.para = {
            "{{TASK_NAME}}": task_name,
            "{{Language}}": language,
            "{{MORE_TASK_DEFINITION}}": task_definition,
            "{{STEPS}}": self.step,
            "{{GUIDANCE}}": self.guidance,
            "{{In-Context Examples}}": self.examples,
            "{{Relations}}": self.relations,
            "{{Output}}": self.output
        }

    def judge_a_case(self, case_data: dict, mod=1):
        """
        输入内容，应用prompt模板获取输出

        :param case_data: 模型输入
        :param mod: 解析模式
        """
        self.logger.info(f"input sentence: {case_data['{{TGT_VALUE}}']}")
        prompt = self.llm_model.fit_case(pattern=self.prompt_pattern, data=case_data, meta_dict=self.para)
        # self.logger.info(f"prompt: {prompt}")
        contexts = self.llm_model.create_prompt(prompt)
        result = self.llm_model.request_llm(contexts)
        if mod == 1:
            result = self.extract_scores(result[-1]["content"])
        else:
            result = self.extract_scores2(result[-1]["content"])
        return result

    def extract_scores(self, last_response: str):
        """
        解析提取到的三元组信息

        :param last_response: 大模型返回的原始输出
        """
        check_prompt = self.llm_model.create_prompt(CHECK_PROMPT.replace("{{TGT_VALUE}}", last_response))
        last_response = self.llm_model.request_llm(check_prompt)[-1]['content']
        origin = last_response.strip(" \t\n'[Output][输出]`").strip(" \t\n'[Output][输出]`")
        # origin = origin.replace('\n', '').replace('\t', '').replace(' ', '')
        try:
            dictionary = json.loads(origin)
            self.logger.info(f"entities: {dictionary['entities']}")
            self.logger.info(f"triples: {dictionary['triples']}")
            return dictionary['triples']
        except json.decoder.JSONDecodeError:
            # 第一重修正
            try:
                origin = origin.replace("\n", "").replace("\t", "")
                dictionary = json.loads(origin)
                self.logger.info(f"entities: {dictionary['entities']}")
                self.logger.info(f"triples: {dictionary['triples']}")
                return dictionary['triples']
            except json.decoder.JSONDecodeError:
                # 第二重修正（可能要套智能体了）
                try:
                    origin = origin.replace("\"\"", "\"")
                    origin = origin.replace("\"(", "[").replace(")", "]")
                    origin = origin.replace("(", "[")
                    dictionary = json.loads(origin)
                    self.logger.info(f"entities: {dictionary['entities']}")
                    self.logger.info(f"triples: {dictionary['triples']}")
                    return dictionary['triples']
                except json.decoder.JSONDecodeError:
                    return origin
        except KeyError:
            return origin

    def extract_scores2(self, last_response: str):
        """
        解析提取到的三元组信息

        :param last_response: 大模型返回的原始输出
        """
        origin = last_response.strip(" \t\n'[Output][SC]`").strip(" \t\n'[Output][SC]`")
        # origin = origin.replace('\n', '').replace('\t', '').replace(' ', '')
        try:
            dictionary = json.loads(origin)
            self.logger.info(f"sentence: {dictionary['sentence']}")
            return dictionary['sentence']
        except json.decoder.JSONDecodeError:
            return origin
        except KeyError:
            return origin


def send_request(args, logger, sentence):
    # 定义一个Agent
    if args.model == "gpt":
        chat_gpt = ChatGPTLLM(args.config_path)
    else:
        chat_gpt = LocalLlama(args.config_path)

    # 定义参数
    if args.prompt_language == "en":
        task_name = "Common Sense Knowledge Triple Extraction"
        language = "Chinese"
        task_definition = '''You need to extract the knowledge in the given sentence as triple. You should
            recognize the named entities in the sentence and infer the relation between these entities.'''

        steps = [
            "Read the sentence given in the [Input] and recognize the named entities as [Entity].",
            "Infer the relation between the entities you recognized before as [Relation].",
            "Output the triple in the form of '(subject, relation, object)'"
        ]

        guidance = [
            "You should strictly follow the [Steps] step by step.",
            "Some relations and their definition are given in [Relations]. You should use the suitable relation in "
            "[Relations] as [Relation] if possible",
            "There are some examples in [Examples] to help you judgement, but notice that the relation in these "
            "examples may not in [Relations]. You should strictly obey the rule mentioned before."
        ]

        relations = {
            "邻近": "This relation describe the short distance between two place. such as (北京, 邻近, 天津).",
            "位于": "This relation describe one place is contained in another place. such as (昆明, 位于, 云南)."
        }
    else:
        task_name = "常识知识三元组抽取"
        language = "中文"
        task_definition = ""

        steps = [
            "读取[Input]中给出的句子，并识别出其中的命名实体作为[Entity]。",
            "推断你之前识别出的实体之间的关系，作为[Relation]。",
            "以'(subject, relation, object)'的形式输出三元组。"
        ]

        guidance = [
            "你应该严格按照[Steps]的步骤进行操作。",
            "一些关系及其定义在[Relations]中给出。如果可能的话，你应该在[Relations]中选择合适的关系作为[Relation]。",
            "在[Examples]中有一些示例可以帮助你进行判断，但请注意，这些示例中的关系可能不在[Relations]中。你应该严格遵守之前提到的规则。"
        ]

        relations = {
            "邻近": "这个关系描述了两个地点之间的近距离。例如：(北京, 邻近, 天津)。",
            "位于": "这个关系描述了一个地点包含在另一个地点内。例如：(昆明, 位于, 云南)。"
        }

    output = {
        "entities": ["[Entity]", "..."],
        "triples": ["([Entity], [Relation], [Entity])", "..."]
    }

    # 示例
    examples = [
        {
            "Input": {
                "sentence": "九玄珠是在纵横中文网连载的一部小说，作者是龙马"
            },
            "Output": {
                "entities": ["九玄珠", "纵横中文网", "龙马"],
                "triples": ["(九玄珠, 连载网站, 纵横中文网)", "(九玄珠, 作者, 龙马)"]
            }
        },
        {
            "Input": {
                "sentence": "在兴义市区期间，入住的是富康国际酒店。从兴义机场到市中心的富康国际酒店打车不过十来分钟。"
            },
            "Output": {
                "entities": ["兴义", "富康国际酒店", "兴义机场"],
                "triples": ["(兴义机场, 位于, 兴义)", "(富康国际酒店, 位于, 兴义)",
                            "(兴义机场, 邻近, 富康国际酒店)"]
            }
        }
    ]

    case_data = {
        "{{TGT}}": "sentence",
        "{{TGT_VALUE}}": sentence
    }

    # 提取三元组
    if args.prompt == "simple":
        prompt = PROMPT_SIMPLEST
    elif args.prompt == "medium":
        prompt = PROMPT_SIMPLE
    else:
        if args.prompt_language == "en":
            prompt = TEXT_EVAL_GENERAL_PROMPT_PATTERN
        else:
            prompt = TEXT_EVAL_GENERAL_PROMPT_PATTERN_CHINESE
    sc = ScoringAgent(logger, chat_gpt, task_name, prompt,
                      language, task_definition, guidance, steps, examples, relations, output)
    triples = sc.judge_a_case(case_data)
    return triples


if __name__ == '__main__':
    # https://platform.openai.com/docs/api-reference

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, default="../remote/configs/wsx_gpt35.json")
    parser.add_argument("--prompt_language", type=str, default="zh")
    args = parser.parse_args()

    # 定义一个Logger
    logger = set_logger("tmp.log")

    # 定义一个Agent
    chat_gpt = ChatGPTLLM(args.config_path)

    # 定义参数
    if args.prompt_language == "en":
        task_name = "Common Sense Knowledge Triple Extraction"
        language = "Chinese"
        task_definition = '''You need to extract the knowledge in the given sentence as triple. You should
        recognize the named entities in the sentence and infer the relation between these entities.'''

        steps = [
            "Read the sentence given in the [Input] and recognize the named entities as [Entity].",
            "Infer the relation between the entities you recognized before as [Relation].",
            "Output the triple in the form of '(subject, relation, object)'"
        ]

        guidance = [
            "You should strictly follow the [Steps] step by step.",
            "Some relations and their definition are given in [Relations]. You should use the suitable relation in "
            "[Relations] as [Relation]. If you do not find any suitable in [Relations], output the suitable relation.",
            "There are some examples in [Examples] to help you judgement, but notice that the relation in these "
            "examples may not in [Relations]. You should strictly obey the rule mentioned before."
        ]

        relations = {
            "邻近": "This relation describe the short distance between two place. such as (北京, 邻近, 天津).",
            "位于": "This relation describe one place is contained in another place. such as (昆明, 位于, 云南)."
        }

    else:
        task_name = "常识知识三元组抽取"
        language = "中文"
        task_definition = ""

        steps = [
            "读取[Input]中给出的句子，并识别出其中的命名实体作为[Entity]。",
            "推断你之前识别出的实体之间的关系，作为[Relation]。",
            "以'(subject, relation, object)'的形式输出三元组。"
        ]

        guidance = [
            "你应该严格按照[Steps]的步骤进行操作。",
            "一些关系及其定义在[Relations]中给出。如果可能的话，你应该在[Relations]中选择合适的关系作为[Relation]。",
            "在[Examples]中有一些示例可以帮助你进行判断，但请注意，这些示例中的关系可能不在[Relations]中。你应该严格遵守之前提到的规则。"
        ]

        relations = {
            "邻近": "这个关系描述了两个地点之间的近距离。例如：(北京, 邻近, 天津)。",
            "位于": "这个关系描述了一个地点包含在另一个地点内。例如：(昆明, 位于, 云南)。"
        }

    output = {
        "entities": ["[Entity]", "..."],
        "triples": ["([Entity], [Relation], [Entity])", "..."]
    }

    # 示例
    examples = [
        {
            "Input": {
                "sentence": "九玄珠是在纵横中文网连载的一部小说，作者是龙马"
            },
            "Output": {
                "entities": ["九玄珠", "纵横中文网", "龙马"],
                "triples": ["(九玄珠, 连载网站, 纵横中文网)", "(九玄珠, 作者, 龙马)"]
            }
        },
        {
            "Input": {
                "sentence": "在兴义市区期间，入住的是富康国际酒店。从兴义机场到市中心的富康国际酒店打车不过十来分钟。"
            },
            "Output": {
                "entities": ["兴义", "富康国际酒店", "兴义机场"],
                "triples": ["(兴义机场, 位于, 兴义)", "(富康国际酒店, 位于, 兴义)", "(兴义机场, 邻近, 富康国际酒店)"]
            }
        }
    ]

    while True:
        # 输入数据
        time.sleep(2)
        sentence = input("请输入需要进行知识抽取的句子（输入0退出）: ")
        if sentence == "0":
            break
        case_data = {
            "{{TGT}}": "sentence",
            "{{TGT_VALUE}}": sentence
        }
        # 提取三元组
        sc = ScoringAgent(logger, chat_gpt, task_name, TEXT_EVAL_GENERAL_PROMPT_PATTERN,
                          language, task_definition, guidance, steps, examples, relations, output)
        triples = sc.judge_a_case(case_data)
        print("提取到的三元组如下：")
        if isinstance(triples, list):
            for triple in triples:
                print(triple)
        else:
            print(triples)
