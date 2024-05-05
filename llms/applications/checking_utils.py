import os
import argparse
import json
import pickle
import threading

from llms.applications.scoring import send_request
from llms.applications.tmp_utils import set_logger


class CheckingUtils:
    def __init__(self, args, data):
        self.args = args
        self.logger = set_logger(self.args.log_path)
        self.index = []
        self.result = data
        self.save_path = os.path.join(self.args.save_path, "save.pkl")
        try:
            with open(self.save_path, 'rb') as f:
                ans = input("检测到保存的进度文件，是否重载进度？(y/n)")
                while ans[0] not in ['y', 'Y', 'n', 'N']:
                    ans = input("请输入'y'或'n'")
                if ans[0] in ['y', 'Y']:
                    state_dict = pickle.load(f)
                    self.__dict__.update(state_dict)
        except FileNotFoundError:
            pass

    def worker(self, sentences, start):
        try:
            for i, sentence in enumerate(sentences):
                if self.index[start + i] == 1:
                    continue
                tri = send_request(self.args, self.logger, sentence['sentence'])
                try:
                    self.result[start + i]['triples'] = tri
                except Exception as e:
                    self.result[start + i]['triples'] = tri
                self.index[start + i] = 1
                # 自动定期保存（应对强制中断）
                if i % self.args.auto_save_round == 0:
                    self.save_state()
                    if self.args.save_file:
                        with open(self.args.output_path, 'w', encoding='utf-8') as f:
                            json.dump(self.result, f, ensure_ascii=False, indent=4)
                # if i == 40:
                #     raise FileNotFoundError
        except KeyboardInterrupt:
            self.save_state()
        except Exception as e:
            self.save_state()

    def save_state(self):
        with open(self.save_path, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def run(self, data):
        if len(self.index) == 0:
            self.index = [0] * len(data)
        if self.args.thread_num == 1:
            self.worker(data, 0)
        else:
            # 划分多进程数据
            data_list = []
            spliter = int(len(data) / self.args.thread_num)
            for i in range(self.args.thread_num):
                if i == 0:
                    try:
                        data_list.append(data[:spliter])
                    except IndexError as e:
                        data_list.append(data)
                elif i == self.args.thread_num - 1:
                    data_list.append(data[spliter * i:])
                else:
                    data_list.append(data[spliter * i:spliter * (i + 1)])

            # 多线程request
            try:
                thread_pool = []
                for i in range(self.args.thread_num):
                    t = threading.Thread(target=self.worker, args=(data_list[i], spliter * i), name=f"Thread-{i + 1}")
                    thread_pool.append(t)
                    t.start()
                for i in range(args.thread_num):
                    thread_pool[i].join()
            except KeyboardInterrupt:
                self.save_state()
            except Exception as e:
                self.save_state()
        with open(self.args.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)


# if __name__ == '__main__':
#     # 声明参数
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--model", type=str, default="gpt")
#     parser.add_argument("--config_path", type=str, default="./llms/remote/configs/gpt35.json")
#     parser.add_argument("--input_path", type=str, default="./dataset/origin.json")
#     parser.add_argument("--output_path", type=str, default="./result/result.json")
#     parser.add_argument("--save_path", type=str, default="./result/save.pkl")
#     parser.add_argument("--prompt", type=str, default="full")
#     parser.add_argument("--prompt_language", type=str, default="en")
#     parser.add_argument("--thread_num", type=int, default=1)
#     parser.add_argument("--auto_save_round", type=int, default=5)
#     parser.add_argument("--save_file", action="store_true")
#     args = parser.parse_args()
#
#     # 打开文件
#     try:
#         with open(args.input_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except Exception as e:
#         exit(-1)
#
#     cu = CheckingUtils(args, data)
#     cu.run(data)
