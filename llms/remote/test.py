# import json
#
# a = "{\"triples\":[\"(\"杨幂\",\"是\",\"中国知名的女演员和歌手\"\"),\"(\"杨幂\",\"赢得\",\"广大观众的喜爱\"\"),\"(\"杨幂\",\"参演\",\"多部热播剧\"\"),\"(\"多部热播剧\",\"包括\",\"《欢乐颂》\"\")]}"
# a = a.replace("\"(", "[").replace("\")", "]")
# print(a)
# json = json.loads(a)
# print(json)

import os
import signal
import subprocess
import time


def child_process():
    try:
        # 注册SIGTERM的信号处理程序
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

        # 模拟长时间运行的任务
        while True:
            print("Child process running...")
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # 清理并退出
        print("Child process exiting gracefully...")


def main():
    p = subprocess.Popen()  # 注意：这里是一个简化的示例，通常你会传递一个命令行字符串或列表

    try:
        p.wait()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught in parent. Sending SIGTERM to child.")
        p.terminate()  # 发送SIGTERM信号到子进程
        p.wait()  # 等待子进程退出


if __name__ == "__main__":
    main()
