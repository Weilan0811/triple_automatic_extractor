TEXT_EVAL_GENERAL_PROMPT_PATTERN = """
[Task Description] 
Here is a point-wise {{TASK_NAME}} task. All [Input] are in {{Language}}.
Your are required to acted as a professional native-speaker human annotator to evaluate the given {{TGT}} in [Input].
{{MORE_TASK_DEFINITION}}
Your evaluation should follow the [Step] and [Guidance]. 
The output format should follow the [Output Format].

[Step]
{{STEPS}}

[Guidance]
You should strictly follow my guidance:
{{GUIDANCE}}
If you break my guidance, you will be penalized.

[Examples]
{{In-Context Examples}}

[Relations]
{{Relations}}

[Output Format]
Your output should strictly follow this format and can be directly decoded by Python:
'''
{{Output}}
'''

[Input]
'''
{
    "{{TGT}}": {{TGT_VALUE}}
}
'''
 
"""

TEXT_EVAL_GENERAL_PROMPT_PATTERN_CHINESE = """
[任务描述]
你是一位中文语言分析师，接下来你需要完成常识知识三元组的抽取任务。
你需要对[输入]中的中文语句进行分析，提取出其中的实体，并判断这些实体之间的关系。
在任务中，你需要严格遵守[任务步骤]和[任务要求]。
你需要严格按照[输出模板]的要求给出输出。

[任务步骤]
{{STEPS}}

[任务要求]
你必须严格遵守以下要求，否则你会受到严重惩罚：
{{GUIDANCE}}

[示例]
{{In-Context Examples}}

[关系限定]
{{Relations}}

[输出格式]
你的输出应严格遵循此格式，并且可以直接通过Python进行解码：
'''
{{Output}}
'''

[输入]
'''
{
    "{{TGT}}": {{TGT_VALUE}}
}
'''
"""

PROMPT_SIMPLE = """
[任务描述] 
    您是一位中文语言分析师，您要完成常识知识三元组抽取任务。
[输出格式] 
您需要输出可以被Python直接解析的json字符串：
'''
{{Output}}
'''
[关系限定]
{
    "位于": 描述一个地点包含于另外一个地点之内。例如"(昆明, 位于, 云南)";
    "邻近": 描述一个地点与另一个地点之间的距离较近。例如"(北京, 邻近, 天津)"
}
[样例]
{
    输入："在兴义市区期间，入住的是富康国际酒店。从兴义机场到市中心的富康国际酒店打车不过十来分钟。";
    输出：["(兴义机场, 位于, 兴义)", "(富康国际酒店, 位于, 兴义)", "(兴义机场, 邻近, 富康国际酒店)"]
}
[要求]
    您必须严格遵守以下要求，否则会被惩罚。 
    1.您需要从[输入]给定的句子中识别出所有的"实体"，并判断这些"实体"的"关系"，严格按照[输出格式]中给定的形式输出。
    2.您输出的"关系"必须是[关系限定]中给出的关系，如果您实在找不到合适的关系，请自行表示关系。
    3.您可以参考[样例]中给出的输入输出进行输出。
[输入]
'''
    {{TGT_VALUE}}
'''
"""

PROMPT_SIMPLEST = """
请以("实体", "关系", "实体")的格式从下列句子中抽取常识知识三元组：{{TGT_VALUE}}
"""

DATA_GENERATE_PROMPT = """
[Task Description] 
Here is a point-wise {{TASK_NAME}} task. All [Input] are in {{Language}}.
Your are required to acted as a professional native-speaker human annotator to evaluate the given {{TGT}} in [Input].
{{MORE_TASK_DEFINITION}}
Your evaluation should follow the [Step] and [Guidance]. 
The output format should follow the [Output Format].

[Step]
{{STEPS}}

[Guidance]
You should strictly follow my guidance:
{{GUIDANCE}}
If you break my guidance, you will be penalized.

[Examples]
[
        {
            "输入": {
                triples: ['(高楼, 具有, 地标性)', '(高楼, 吸引, 游客)', '(高楼, 吸引, 建筑爱好者)', '(高楼, 具有, 上海中心大厦)', '(高楼, 具有, 哈利法塔)']
            },
            "输出": {
                "sentence": "昆明，被誉为春城，以其四季如春的气候和丰富的自然景观吸引着无数游客，其中滇池和西山更是成为了昆明的标志性景点。"
            }
        }
]

[Output Format]
Your output should strictly follow this format and can be directly decoded by Python:
'''
{{Output}}
'''

[Input]
'''
{
    "{{TGT}}": {{TGT_VALUE}}
}
'''
"""

CHECK_PROMPT = """
[任务描述]
你是一位博识学家，接下来你需要依据常识知识检查三元组表达知识的正确性。
你需要对[输入]中的所有三元组进行分析，找出其中的错误，对三元组进行修正或舍弃。
在任务中，你需要严格遵守[任务步骤]和[任务要求]。
你需要严格按照[输出模板]的要求给出输出。

[任务步骤]
1. 发现所有格式为"([Entity], [Relation], [Entity])"的三元组知识；
2. 发现在这些三元组知识中存在的常识错误并修正，无法修正则删除对应三元组。例如"(昆明, 位于, 滇池)"存在常识错误，应该修正为"(滇池, 位于, 昆明)"
3. 发现在这些三元组知识中存在的逻辑错误并修正，无法修正则删除对应三元组。例如"(美国, 起源地, 兔女郎)"存在逻辑错误，应改为"(兔女郎, 起源地, 美国)"

[任务要求]
你必须严格遵守以下要求，否则你会受到严重惩罚：
1. 你需要严格按照[任务步骤]完成任务
2. 你需要严格按照[输出格式]的要求输出
3. 你必须保证输出的三元组中不会出现常识性错误

[输出格式]
你的输出应严格与[输入]相同，不包含任何额外信息。

[输入]
'''
{{TGT_VALUE}}
'''

"""