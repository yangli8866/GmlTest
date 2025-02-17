import yaml
from utils import ReadYaml


class YamlCheck:
    def __init__(self):
        self.error_msg = {}

    def yaml_check(self, root_yaml_path, yaml_tree):
        # 初始化error msg
        self.ini_error_msg(root_yaml_path, yaml_tree)
        r = ReadYaml(root_yaml_path)
        # 检查根yaml
        root_yaml_content = r.read_yaml(root_yaml_path)
        # print(root_yaml_content)
        # 检查根yaml必填节点
        root_yaml_necessary_node = ['setup_module']
        self.check_contain_node(root_yaml_content, root_yaml_necessary_node, root_yaml_path)
        # 检查seup_module下step数
        self.check_key_number(root_yaml_content['setup_module'], 'step', root_yaml_path, 'setup_module')
        # 检查根yaml的节点是否重名
        self.check_duplicate_node(root_yaml_path)
        father_yaml_path = []
        child_yaml_path = []
        for k, v in yaml_tree.items():
            father_yaml_path.append(k)
            for i in range(len(v)):
                child_yaml_path.append(v[i][i + 1])
        # 检查父yaml
        for f in father_yaml_path:
            father_yaml_content = r.read_yaml(f + '/daily_build.yaml')
            if 'setup_class' in father_yaml_content:
                self.check_contain_node(father_yaml_content, ['setup_class'], f)
                self.check_key_number(father_yaml_content['setup_class'], 'step', f, 'setup_class')
            self.check_duplicate_node(f + '/daily_build.yaml')

        for c in child_yaml_path:
            self.check_duplicate_node(c)
            child_yaml_content = r.read_yaml(c)
            self.check_contain_node(child_yaml_content, ['case'], c)
            all_case_name = []
            for each_case in child_yaml_content['case']:

                if self.check_contain_node(each_case, ['casename'], c):
                    all_case_name.append(each_case['casename'])
                    if self.check_contain_node(each_case, ['casestep'], c):
                        self.check_key_number(each_case['casestep'], 'step', c, each_case['casename'])
                    if self.check_contain_node(each_case, ['except'], c):
                        self.check_key_number(each_case['except'], 'msg', c, each_case['casename'])
            for case_name in all_case_name:
                if all_case_name.count(case_name) > 1:
                    self.error_msg_append('casename【{}】重名'.format(case_name), c)

        last_error_msg = ''
        for k, v in self.error_msg.items():
            if v:
                s = "{}文件中的错误有:{}\n".format(k, v)
                last_error_msg += s
        if last_error_msg:
            raise Exception(last_error_msg)

    # 判断content_dict的keys，即节点名是否在check_node_list中，如果在判断节点值是否为空
    def check_contain_node(self, content_dict, check_node_list, path):
        flag = True
        for check_node in check_node_list:
            if check_node in content_dict.keys():
                check_node_value = content_dict[check_node]
                if not check_node_value:
                    self.error_msg_append('节点{}值为空'.format(check_node), path)
                    flag = False
            else:
                self.error_msg_append('缺少节点{}'.format(check_node), path)
                flag = False
        return flag

    # 判断content_dict中key数是否从1递增
    def check_key_number(self, content_dict, key, path, father_node=''):
        if key + '1' not in content_dict:
            self.error_msg_append('{}节点缺失{}'.format(father_node, key + '1'), path)
        actually_key_num = ''.join(content_dict.keys()).count(key)
        except_key_list = [key + str(_) for _ in range(1, actually_key_num + 1)]
        for except_key in except_key_list:
            if except_key in content_dict:
                if not content_dict[except_key]:
                    self.error_msg_append('{}节点{}值为空'.format(father_node, except_key), path)
            else:
                self.error_msg_append('{}节点{}缺失'.format(father_node, except_key), path)

    def error_msg_append(self, msg, path):
        self.error_msg[path].append(msg)

    def ini_error_msg(self, root_yaml_path, yaml_tree):
        self.error_msg[root_yaml_path] = []
        for father_yaml_path, child_yamls in yaml_tree.items():
            self.error_msg[father_yaml_path] = []
            for child_yaml in child_yamls:
                for num, child_yaml_path in child_yaml.items():
                    self.error_msg[child_yaml_path] = []

    def check_duplicate_node(self,yaml_path):
        # 放在这里判断节点数字有误的原因：
        # 如果yaml中节点名字一样时，会该名字节点的最后一个值读出来，不会报错
        # 所以需要判断文件中本身的有效step数和msg数时多少，然后在和yaml.dump出来的step节点、msg节点数做比较，如果不一致，说明节点名字有重复
        with open(yaml_path, 'r') as f:
            content_list = f.readlines()
        with open(yaml_path, 'r') as f:
            yaml_content = yaml.load(f, Loader=yaml.FullLoader)
        step_num_content = self.count_start_keyword_in_list(content_list, 'step')
        msg_num_content = self.count_start_keyword_in_list(content_list, 'msg')
        step_num_parse_yaml = self.count_keyword_in_dict(yaml_content, 'step')
        msg_num_parse_yaml = self.count_keyword_in_dict(yaml_content, 'msg')
        if step_num_content != step_num_parse_yaml:
            raise Exception('{}文件中step后面的数字有重复，请检查'.format(yaml_path))
        if msg_num_content != msg_num_parse_yaml:
            raise Exception('{}文件中msg后面的数字有重复，请检查'.format(yaml_path))

    def count_start_keyword_in_list(self,content_list,count_msg):
        keyword_num_content_in_list = 0
        for c in content_list:
            c = c.strip()
            if c.startswith(count_msg):
                keyword_num_content_in_list += 1
        return keyword_num_content_in_list

    def count_keyword_in_dict(self,content_dict,count_msg):
        keyword_num_content_in_dict = 0
        for k1,v1 in content_dict.items():
            if isinstance(v1, dict):
                for k2,v2 in v1.items():
                    if count_msg in k2:
                        keyword_num_content_in_dict+=1
            if isinstance(v1, list):
                for x in v1:
                    if isinstance(x,dict):
                        for k2,v2 in x.items():
                            if isinstance(v2,dict):
                                for k3,v3 in v2.items():
                                    if count_msg in k3:
                                        keyword_num_content_in_dict += 1
        return keyword_num_content_in_dict

if __name__ == '__main__':
    yaml_checker = YamlCheck()
    yaml_root_path = '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/daily_build.yaml'
    yaml_tree = {'/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas':
                 [{1: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/darts/daily_build.yaml'},
                     {2: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/bignas/daily_build.yaml'},
                      # {3: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/spos/daily_build.yaml'},
                      # {4: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/zennas/daily_build.yaml'},
                      # {5: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/detnas/daily_build.yaml'},
                      # {6: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/cream/daily_build.yaml'},
                      # {7: '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/nas/nsganet/daily_build.yaml'}
                      ]
                 }
    yaml_checker.yaml_check(yaml_root_path, yaml_tree)
