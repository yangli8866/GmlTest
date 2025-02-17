# coding=utf-8

from SSHLibrary.library import SSHLibrary as SSH
import time
import logging
from main import run_configs

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

class Client:
    def __init__(self) -> None:
        pass

    def connect(self):
        pass

    def executor(self):
        pass


class SSHClient:

    def __init__(self):
        self.ssh = SSH()

    # 连接：先login到跳板机，然后write 【ssh ***@10.5.36.31】，进入集群机器（因为跳板机可以免密登录到集群）
    def connnect(self,ip0='10.121.*.237', user0='***', password0='***'):
        user1 = run_configs[1]['login_ursername']
        ip1 = run_configs[3]['run_cluster']
        self.ssh.open_connection(ip0)
        self.ssh.login(user0, password0)
        self.ssh.write("ssh " + user1 + "@" + ip1)
        time.sleep(3)
        r = self.ssh.read()
        print(r)
        return r

    def executor(self, cmd, max_wait=30):
        print("*****开始执行{}命令*****".format(cmd))
        self.ssh.write(cmd)
        time.sleep(5)
        s = self.ssh.read()
        for _ in range(max_wait):

            s += self.ssh.read()
            # logging.info("*****s += self.ssh.read()之后的s是：{}***".format(s))
            if run_configs[1]['login_ursername'] in s.split(') [')[-1]:
                break
            time.sleep(60)
            print("*****等60秒，命令还没有结束*****\n")
        print("*****s现在是：{}***".format(s))
        print("*****命令结束*****\n")
        return s



class AuctionClient:
    def __init__(self):
        # 记录登陆的信息
        pass

    def connect(self):
        # 登陆对应集群
        pass

    def executor(self, job_start_cmd):
        # job_start_cmd 撰写成闲时队列所需的格式, 并且提交
        pass
