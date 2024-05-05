import argparse
import json
import logging
import requests
from llms.remote import RemoteLLMs


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, default="configs/llama.json")
    args = parser.parse_args()
    return args


class LocalLlama(RemoteLLMs):
    def init_local_client(self):
        self.headers = {'Content-Type': 'application/json'}

    def create_prompt(self, current_query, context=None):
        if context is None:
            context = []
        context.append(
            {
                "prompt": current_query,
                "n_predict": 512
            }
        )
        return context

    def request_llm(self, context, seed=1234, sleep_time=1, repeat_times=0):
        while True:
            try:
                result = requests.post(
                    url=self.args.url,
                    data=json.dumps(context[-1]),
                    headers=self.headers
                )
                context.append(result.text)
                return context
            except Exception as e:
                # 捕捉未预料的异常，考虑是否终止循环或做其他处理
                logging.error(f"An unexpected error occurred: {str(e)}")
                raise e


if __name__ == '__main__':
    # https://platform.openai.com/docs/api-reference
    args = read_args()
    chat_gpt = LocalLlama(args.config_path)
    chat_gpt.interactive_dialogue()
