# -*- coding: utf-8 -*-
import time
import os
from gtest.utils.read_yaml import *


class CreateTestFile:
    tmux_window = []
    order = 1

    def __init__(self):
        self.run_time = time.strftime("%m%d%H%M", time.localtime())
        self.log_path = "/mnt/lustre/share/gmllog/" + self.run_time

    def write_into_testfile(self, pytest_file_path, content):
        with open(pytest_file_path, 'a+') as f:
            f.write(content)

    def read_pytest_fixture(self, yaml_config, pytest_file_path, setup_test_file_path):
        self.log_path = "/mnt/lustre/share/gmllog/pytest_log_" + self.run_time
        with open(pytest_file_path, 'a+') as f:
            with open(setup_test_file_path, "r") as f1:
                s = f1.readlines()
                for r in s:
                    if "dailyfilename" in r:
                        r = r.replace("dailyfilename", "pytest_log_" + self.run_time)
                    f.write(r)
        test_class_match = {'all_cases':{}}
        keys = yaml_config.keys()
        for k in keys:
            if 'case_' in k:
                cases = test_class_match['all_cases']
                class_name = k.split('case_')[-1]
                cases[class_name] = {}
                cases[class_name]['cases'] = yaml_config[k]
                setup_class_name = 'setup_class_' + class_name
                if setup_class_name in keys:
                    cases[class_name]['setup_class'] = yaml_config[setup_class_name]
                else:
                    cases[class_name]['setup_class'] = {}
                teardown_class_name = 'teardown_class_' + class_name
                if teardown_class_name in keys:
                    cases[class_name]['teardown_class'] = yaml_config[teardown_class_name]
            elif 'setup_module' in k:
                test_class_match['setup_module'] = yaml_config['setup_module']
            elif 'teardown_module' in k:
                test_class_match['teardown_module'] = yaml_config['teardown_module']
        return test_class_match

    def write_test_file(self, yaml_config, pytest_file_path, setup_test_file_path,run_configs=[]):
        yaml_config = self.read_pytest_fixture(yaml_config, pytest_file_path, setup_test_file_path)
        if 'setup_module' in yaml_config.keys():
            self.write_fixture_class("setup_module", yaml_config['setup_module'], pytest_file_path)
        if 'teardown_module' in yaml_config.keys():
            self.write_fixture_class("teardown_module", yaml_config['teardown_module'], pytest_file_path)
        if 'all_cases' in yaml_config.keys():
            for k, v in yaml_config['all_cases'].items():
                class_setup_content = '\n\n\nclass Test' + k + ':'
                self.write_into_testfile(pytest_file_path,class_setup_content)
                if 'setup_class' in v:
                    test_class_setup_class = v['setup_class']
                    self.write_fixture_class('setup_class',test_class_setup_class, pytest_file_path,'        ',run_configs =run_configs)
                test_class_cases = v['cases']
                for i in test_class_cases:
                    self.write_cases_class(i, pytest_file_path,run_configs=run_configs)
                    CreateTestFile.order += 1
        self.edit_file_by_config(run_configs, pytest_file_path)

    def write_allure_desc(self, msg, keyword, log_path, taskname,run_configs=None):
        if run_configs is None:
            run_configs = []
        last_step_log_path = self.get_last_log_path(msg, keyword, log_path, taskname)
        decorators_allure_desc = "\n    @allure.description('这个case结果log文件都在集群{}这个文件中：{}')".format(run_configs[3]['run_cluster'],last_step_log_path)
        return decorators_allure_desc

    def get_last_log_path(self, msg, keyword, log_path, taskname):
        key_num = str(msg.keys()).count(keyword)
        step = 0
        for i in range(1, key_num + 1):
            cli = str(msg[keyword + str(i)])
            log_file_name = log_path + "/" + taskname
            if keyword == "step":
                if "wait" in cli:
                    continue
                else:
                    step = i
        last_step_log_path = log_file_name + '_step' + str(step) + '.txt'
        return last_step_log_path

    def write_cases_class(self, case_info, pytest_file_path,spacing='        ',run_configs=None):
        if run_configs is None:
            run_configs = []
        case_name = self.create_case_name(case_info["casename"])
        decorators_order = "\n\n    @pytest.mark.run(order={})".format(str(CreateTestFile.order))
        decorators_allure_title = "\n    @allure.title('{}')".format(case_name)
        decorators_allure_desc = self.write_allure_desc(case_info["casestep"], "step", self.log_path, case_name,run_configs)
        case_define = "\n    def test_" + case_name + "(self):"
        case_execute = self.keyword_str_join(case_info["casestep"], "step", self.log_path, case_name,spacing,run_configs)
        case_assert = self.keyword_str_join(case_info["except"], "msg", self.log_path, case_name,spacing,run_configs)
        self.write_into_testfile(pytest_file_path,decorators_order + decorators_allure_title + decorators_allure_desc + case_define + case_execute + case_assert)

    def create_case_name(self, name):
        special_single = ["?", "*", "-", " ", "/", "\\", "'", '"', ","]
        for s in special_single:
            name = name.replace(s, '_')
        return "_".join([_ for _ in name.split("_") if len(_) > 0])

    def write_fixture_class(self, fixture_name, fixture_info, pytest_file_path,spacing='',run_configs=None):
        if run_configs is None:
            run_configs = []
        # 写入fixture函数的拼接字符串
        fixture_info_msg_define = ''
        if fixture_name == 'setup_module':
            spacing = '    '
            fixture_info_msg_define = "\ndef setup_module():\n" + spacing + "ssh.connnect()\n" + spacing + "ssh.executor('export HISTTIMEFORMAT=" + '"%Y-%m-%d %H:%M:%S $ "' + "')\n" + spacing + "ssh.executor('cd /mnt/lustre/share/gmllog && mkdir " + "pytest_log_" + self.run_time + " && cd ~ && rm -rf gml_daily/GML_data/')\n" + spacing + "ssh.executor('tmux kill-server')"
        elif fixture_name == 'setup_class':
            spacing = '        '
            fixture_info_msg_define = "\n\n    def setup_class(self):\n" + spacing + "ssh.executor('cd " + run_configs[0]['workspace'] + "')"
        fixture_info_msg_execute = self.keyword_str_join(fixture_info, "step", self.log_path, fixture_name, spacing,run_configs)
        fixture_info_msg_assert = ''
        if 'except' in fixture_info.keys():
            fixture_info_msg_assert = self.keyword_str_join(fixture_info["except"], "msg", self.log_path, fixture_name, spacing,run_configs)

        self.write_into_testfile(pytest_file_path, fixture_info_msg_define + fixture_info_msg_execute + fixture_info_msg_assert)


    def keyword_str_join(self, msg, keyword, log_path, taskname, spacing,run_configs=None):
        """
        :param msg: 假设传入【{'step1': 'source pat_latest','step2': 'ls', 'except': {'msg1': '请注意:该环境'}}
        :param filename: 举例：【ssh.executor('source pat_latest >>filename 2>&1')】结果输出重定向到的位置
        :return: 返回拼接好的字符串，举例：【ssh.executor('source pat_latest >>/mnt/lustre/share/gmllog/03011939/setup.txt 2>&1')】
        """
        if run_configs is None:
            run_configs = []
        key_num = str(msg.keys()).count(keyword)
        s = ""
        for i in range(1, key_num + 1):
            cli = str(msg[keyword + str(i)])
            if "${{taskname}}" in cli:
                cli = cli.replace("${{taskname}}", taskname + self.run_time)
            elif "${{casename}}" in cli:
                cli = cli.replace("${{casename}}", taskname)

            filename = log_path + "/" + taskname
            if keyword == "step":
                if "wait" in cli:
                    t = int(cli.split("(")[-1].split("s)")[0])
                    s += '\n' + spacing + 'time.sleep({})'.format(str(t))
                    s += "\n" + spacing + "print('现在的准确时间是：{}'.format(time.strftime('%m%d%H%M', time.localtime())))"
                    continue
                executor_cli = cli + ' &> ' + filename + '_step' + str(i) + '.txt'
                if 'setarg(' in cli:
                    s += '\n' + spacing + 'Utils.get_result_from_consule(ssh, """' + executor_cli + '""")'
                elif 'tmux' in cli:
                    if taskname not in CreateTestFile.tmux_window:
                        s += self.tmux_setup(taskname,run_configs=run_configs)
                    tmux_cli = cli.split('(')[-1].split(')')[0]
                    executor_cli = 'tmux send-keys -t ' + taskname + " '" + tmux_cli + "'" + ' C-m'
                    s += '\n' + spacing + 'ssh.executor("""' + executor_cli + '""")'
                elif "${{" in cli and 'setarg(' not in cli:
                    s = CreateTestFile.replace_set_params(s, executor_cli)
                else:
                    s += '\n' + spacing + 'ssh.executor("""' + executor_cli + '""")'
                s += "\n" + spacing + "print('现在的准确时间是：{}'.format(time.strftime('%m%d%H%M', time.localtime())))"
            elif keyword == 'msg':
                s += "\n" + spacing + "assert Utils.assert_result_in_logpath(ssh, '" + cli + "', '" + filename + "')"
        return s

    def tmux_setup(self, tmux_name, spacing='        ',run_configs=None):
        if run_configs is None:
            run_configs = []
        # step1:起tmux窗口
        tmux_step1 = 'tmux new -s ' + tmux_name
        CreateTestFile.tmux_window.append(tmux_name)
        # 切回主窗口
        tmux_step2 = 'tmux detach'
        # 从主窗口发送命令给 tmux_name 窗口,source 环境
        tmux_step3 = "tmux send-keys -t " + tmux_name + " '" + run_configs[5]['source_env'] + "' C-m"

        tmux_step4 = "tmux send-keys -t " + tmux_name + " 'cd " + run_configs[0]['workspace'] + "/demo' C-m"
        tmux_steps = [tmux_step1, tmux_step2, tmux_step3, tmux_step4]
        ts = ''
        for t in tmux_steps:
            ts += '\n' + spacing + 'ssh.executor("""' + t + '""", max_wait=3)'
            ts += "\n" + spacing + "print('现在的准确时间是：{}'.format(time.strftime('%m%d%H%M', time.localtime())))"
        return ts

    @classmethod
    def replace_set_params(cls, s, cli, spacing='        '):
        s += '\n' + spacing + 'cli = """' + cli + '"""'
        s += '\n' + spacing + 'global_arg = Utils.get_json_value()'
        s += '\n' + spacing + 'print(global_arg)'
        s += '\n' + spacing + 'for k,v in global_arg.items():'
        s += '\n' + spacing*2 + 'if k in cli:'
        s += '\n' + spacing*3 + 'cli = cli.replace("${{" + k + "}}",v)'
        s += '\n' + spacing + 'ssh.executor(cli)'
        return s

    def edit_file_by_config(self,configs,file_path):
        file_content = ''
        with open(file_path, "r") as f:
            file_content = f.read()

        for c in configs:
            print(c)
            for k,v in c.items():
                if k == 'login_ursername' and v != 'platform.tester.s.01':
                    file_content = file_content.replace('platform.tester.s.01',v)

                if k == 'login_password' and v != 'sense@1234':
                    file_content = file_content.replace('sense@1234',v)
                if k == 'branch' and v != 'master':
                    old_clone_msg = 'git clone git@gitlab.sz.sensetime.com:parrotsDL-sz/gml.git '
                    new_clone_msg = 'git clone git@gitlab.sz.sensetime.com:parrotsDL-sz/gml.git -b ' + v + ' '
                    file_content = file_content.replace(old_clone_msg, new_clone_msg)
                if k =='workspace':
                    old_value = '${' + k + "}"
                    new_value = v
                    file_content = file_content.replace( old_value, new_value)
                    if v != '~/gml_daily/gml':
                        file_content = file_content.replace('~/gml_daily/gml', v)
                if k == 'run_pat' and v != 'pat_dev':
                    file_content = file_content.replace('pat_dev', v)

        with open(file_path, "w") as f:
            f.write(file_content)


class CreateWeeklyTestFile:
    pass


if __name__ == '__main__':
    setup_path = '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/daily_build.yaml'
    merged_yaml_path = '/Users/liyang8/PycharmProjects/gmltest/data/all_daily.yaml'
    tests_path = '/Users/liyang8/PycharmProjects/gmltest/tests/test_all_cases.py'
    setup_test_file_path = '/Users/liyang8/PycharmProjects/gmltest/data/pytest_file_setup.txt'
    # creater = r.read_yaml(merged_yaml_path)
    # run_configs = CreateTestFile()
    # r = ReadYaml()
    yaml_config = [
        {'workspace': '~/gml_daily/gml'},
        {'login_ursername': 'platform.tester.s.01'},
        {'login_password': 'sense@1234'},
        {'run_cluster': '10.5.36.31'},
        {'run_pat': 'pat_dev'},
        {'source_env': 'source pt1.6.0 mmcv=1.4.6'}
    ]
    # creater.write_test_file(yaml_config, tests_path, setup_test_file_path,run_configs)
    creater = CreateTestFile()
    creater.replace_config(yaml_config,tests_path)
