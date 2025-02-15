# coding=utf-8
import time
import logging
import os
import json
from gtest.utils.ssh_clinet import SSHClient

logging.basicConfig(level=logging.ERROR)


class Utils:
    path = os.path.dirname(os.path.dirname(__file__))
    par_path = os.path.abspath(os.path.join(path, os.pardir))

    @classmethod
    def assert_result_in_logfile(cls, ssh, expected_results, actually_log_file_path, largest_wait=1400,
                                 spacing_time=20):
        time.sleep(largest_wait % spacing_time)
        for _ in range(largest_wait // spacing_time):
            time.sleep(spacing_time)
            result = ssh.executor('grep -c "' + expected_results + '" ' + actually_log_file_path)
            r = result.split('\r\n')
            logging.info(r)
            if int(r[-2]) > 0:
                return True
        return False

    @classmethod
    def assert_result_in_logpath(cls, ssh, expected_results, actually_log, largest_wait=100,
                                 spacing_time=20):
        # actually_log_file_path传如：~/gmllog/test_nasdaily_03302143/bignas_supernet_train
        # cli = """ls ~/gmllog/test_daily_hpo_03301116/ | grep MOCK_PAVI0 > log3.txt && awk -F step '{print $2}' log3.txt | awk -F '.txt' '{print $1}' | awk 'BEGIN {max=1} {if ($1+0>max+0) max=$1} END {print max}'"""
        actually_log_file_path = actually_log.split('/')
        case_name = actually_log_file_path.pop()
        actually_log_file_path = '/'.join(actually_log_file_path)
        cli = "ls " + actually_log_file_path + " | grep ^" + case_name + " > " + case_name + "_log.txt "
        ssh.executor(cli)
        cli2 = "awk -F step '{print $2}' " + case_name + "_log.txt | awk -F '.txt' '{print $1}' | awk 'BEGIN {max=1} {if ($1+0>max+0) max=$1} END {print max}'"
        step_no_res = Utils.get_execute_result(ssh, cli2)
        actually_log_file = actually_log_file_path + "/" + case_name + "_step" + step_no_res + ".txt"
        for _ in range(30):
            result = ssh.executor('tail -3 ' + actually_log_file)
            if 'Current PHX_PRIORITY is' in result:
                time.sleep(10)
                print('在等资源····')
            else:
                break
        time.sleep(largest_wait % spacing_time)
        for _ in range(largest_wait // spacing_time):
            time.sleep(spacing_time)
            result = ssh.executor('grep -c "' + expected_results + '" ' + actually_log_file)
            r = result.split('\r\n')
            logging.info(r)
            if int(r[-2]) > 0:
                return True
        return False

    @classmethod
    def get_execute_result(cls, ssh, cmd):
        res = ssh.executor(cmd)
        r = res.split('\r\n')
        if r[-2]:
            return r[-2]

    @classmethod
    def get_result_from_consule(cls, ssh, cli):
        # """setarg(${{FILENAME}},find . -name '*lyhe*') &> ~/gmllog/03250056/find_fine_name_step1.txt"""
        arg_name = cli.split('{{')[1].split('}}')[0]
        shell_commd = cli.split('}},')[1].replace(')', '')
        ssh.executor(shell_commd)
        result_file = cli.split('&> ')[1]
        result = ssh.executor('head -1 ' + result_file)
        if '\r\n' in result:
            arg_value = result.split('\r\n')[-2]
            if arg_value:
                Utils.append_content(Utils.par_path + '/data/global_arg.json', arg_name, arg_value)
            else:
                Utils.append_content(Utils.par_path + '/data/global_arg.json', arg_name, ' ')

    @classmethod
    def append_content(cls, path, k, v):
        with open(path, 'r') as f:
            s = f.readlines()
        old_value = ''.join(s)
        new_value = eval(old_value)
        new_value[k] = str(v)
        x = str(new_value)
        x = x.replace("'", '"')
        x = x.replace("'", '"')
        with open(path, 'w') as f:
            f.write(x)

    @classmethod
    def get_json_value(cls, path=''):
        if path == '':
            path = Utils.par_path + '/data/global_arg.json'
        with open(path, 'r') as f:
            s = f.readlines()
        old_value = ''.join(s)
        new_value = eval(old_value)
        return new_value

    @classmethod
    def read_file_info(cls, path):
        with open(path, 'r') as f:
            data = f.readlines()
        return ''.join(data)

    def write_test_file_info(self, file_name, file_content):
        path = '../test/' + file_name + '.py'
        with open(path, "a") as f:
            f.write(file_content)


    @classmethod
    def setup_env(cls):
        # 清空config文件
        with open(Utils.par_path + '/data/global_arg.json', 'w') as f:
            f.write("{}")


if __name__=='__main__':
    u = Utils()
    print(u.path)

