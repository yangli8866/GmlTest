#!/usr/bin/env python
# coding=utf-8

import yaml
import logging
import os

logging.basicConfig(level=logging.ERROR)


class YamlParse:
    def __init__(self):
        self.error_msg = []

    def check_child_node(self, father_node, child_node, confirm_msg):
        """
        stepN和msgN这种节点后数字和值的校验
        校验数字N必须从1开始连续的证书，每个节点必须有值
        :param confirm_msg: 要校验的字段，例如：step或者msg
        :param father_node: 一级节点，其实只是为了logging，知道出错以后是哪个父节点下的子节点出了问题
        :param child_node: 要校验的stepN和msgN这种节点的父节点的值，例如：{'step1':'AAA','step2':'BBB'}
        :return:
        """
        confirm_msg_num = str(child_node.keys()).count(confirm_msg)
        for i in range(1, confirm_msg_num + 1):
            # 检查节点后的数字N
            s = confirm_msg + str(i)
            if s not in child_node.keys():
                self.error_msg.append('{} 这个节点下的 {} 节点后数字有误，请检查'.format(father_node, confirm_msg))
                continue
            # 检查节点是否有值
            if not child_node[s]:
                self.error_msg.append('{} 这个节点下的 {} 节点后缺失值，请检查'.format(father_node, confirm_msg))

    def check_requird_node(self, actural_node, requird_node_key, case_name='', father_node=''):
        """
        检查actural_node中的节点是否包含所有的必填节点requird_node_key
        :param actural_node: 要检查的节点
        :param requird_node_key: 必须含有的节点列表
        :param case_name: 如果是case节点的话，传入casename方便追溯到底是哪个case有问题
        :param father_node: 父节点，为了一些二级节点能方便追溯到底是哪个一级节点有问题
        :return:
        """
        flag = 0
        for i in requird_node_key:
            # 字段是否为空检查
            if i not in actural_node.keys():
                if case_name:
                    self.error_msg.append("{} 这个case节点下的 {} 节点缺失".format(case_name, i))
                else:
                    self.error_msg.append("{} {} 节点缺失".format(father_node, i))
                flag += 1
                continue
            # 字段值是否为空检查
            if not actural_node[i]:
                if case_name:
                    self.error_msg.append("{} 这个case节点下的 {}  的值缺失".format(case_name, i))
                else:
                    self.error_msg.append("{} {} 节点的值缺失".format(father_node, i))
                flag += 1
        if flag == 0:
            return True
        else:
            return False

    def yaml_parses(self, config_path):
        with open(config_path, 'r') as f:
            logging.info('config文件开始解析····')
            yaml_content = yaml.load(f, Loader=yaml.FullLoader)
            print(yaml_content)
            requird_case_child_node = ['casename', 'casestep', 'except']

            # step1：一级节点必填项检查：
            requird_father_node = ['workspace', 'cluster', 'pat', 'case']
            self.check_requird_node(yaml_content, requird_father_node)

            # step2：一级节点非必填项值的检查：
            father_not_nessary = list(set(yaml_content.keys()).difference(set(requird_father_node)))

            if len(father_not_nessary):
                self.check_requird_node(yaml_content, father_not_nessary)

            # step3：有二级节点的，进行二级节点的检查
            for k, v in yaml_content.items():
                if isinstance(v, dict) or isinstance(v, list):
                    # step4：case节点的子节点的必填字段检查
                    if k == 'case':
                        for each_case in v:
                            # 判断case这个一级节点下的必填二级节点
                            if self.check_requird_node(each_case, ['casename']):
                                casename = each_case['casename']
                                if self.check_requird_node(each_case, ['casestep'], casename):
                                    if 'step1' in each_case['casestep'].keys():
                                        self.check_child_node(casename, each_case['casestep'], 'step')
                                    else:
                                        self.error_msg.append('{} 这个case的下 casestep 的子节点缺少step1，请检查'.format(casename))
                                if self.check_requird_node(each_case, ['except'], casename):
                                    if 'msg1' in each_case['except'].keys():
                                        self.check_child_node(casename, each_case['except'], 'msg')
                                    else:
                                        self.error_msg.append('{} 这个case的下 except 的子节点缺少msg1，请检查'.format(casename))
                            # 判断case这个一级节点下的非必填二级节点下的子节点：
                            not_nessary = list(set(each_case.keys()).difference(set(requird_case_child_node)))

                            for n in not_nessary:
                                if isinstance(each_case[n], dict) or isinstance(each_case[n], list):
                                    step_num = ''.join(each_case[n].keys()).count('step')
                                    steps = ['step' + str(_) for _ in range(1, step_num + 1)]
                                    self.check_requird_node(each_case[n], steps,
                                                               father_node=casename + '这个case下的' + n)
                                    # 非case节点的一级节点，检查该节点子节点的except节点规范
                                    if 'except' in each_case[n]:
                                        if self.check_requird_node(each_case[n], ['except'],
                                                                      father_node=casename + '这个case下的' + n):
                                            if 'msg1' not in each_case[n]['except'].keys():
                                                self.error_msg.append('{}这个case下的{}这个节点的except下的msg节点有误，请检查'.format(
                                                    casename, n))
                                            else:
                                                self.check_child_node(casename + '这个case下的' + n, each_case[n]['except'],
                                                                         'msg')
                    else:
                        # 非case节点的一级节点，检查该节点子节点的step、except节点规范
                        step_num = ''.join(v.keys()).count('step')
                        steps = ['step' + str(_) for _ in range(1, step_num + 1)]
                        self.check_requird_node(v, steps, father_node=k)
                        # 非case节点的一级节点，检查该节点子节点的except节点规范
                        if 'except' in v.keys():
                            if 'msg1' not in v['except'].keys():
                                self.error_msg.append('{}这个节点的except下的msg节点有误，请检查'.format(k))
                            else:
                                self.check_child_node(k, v['except'], 'msg')
            if len(self.error_msg) > 0:
                raise Exception(self.error_msg)
            logging.info('config文件解析完成····,内容是：')
            logging.info(yaml_content)
            return yaml_content


if __name__ == '__main__':
    path = '../test.yml'
    parser = YamlParse()
    yaml_condig = parser.yaml_parses(path)
