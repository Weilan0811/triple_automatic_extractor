import argparse
import json

from llms.applications.checking_utils import CheckingUtils

if __name__ == '__main__':
    # 声明参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gpt", help="调用模型名称（gpt or lamma）")
    parser.add_argument("--config_path", type=str, default="./llms/remote/configs/wsx_gpt35.json", help="配置文件路径")
    parser.add_argument("--input_path", type=str, default="./dataset/origin.json", help="待处理数据集路径")
    parser.add_argument("--output_path", type=str, default="./result/result.json", help="保存数据保存路径")
    parser.add_argument("--save_path", type=str, default="./result", help="自动保存路径")
    parser.add_argument("--log_path", type=str, default="./logs/temp.log", help="日志保存路径")
    parser.add_argument("--prompt", type=str, default="full", help="使用的prompt类型")
    parser.add_argument("--prompt_language", type=str, default="en", help="使用的prompt语言")
    parser.add_argument("--thread_num", type=int, default=1, help="进程数")
    parser.add_argument("--auto_save_round", type=int, default=5, help="自动保存程序运行状态的轮数")
    parser.add_argument("--save_file", action="store_true", help="保存文件状态时是否需要保存文件")
    args = parser.parse_args()

    # 打开文件
    try:
        with open(args.input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        exit(-1)

    cu = CheckingUtils(args, data)
    cu.run(data)
