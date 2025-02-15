import yaml
import os
import logging
from collections import OrderedDict

logging.basicConfig(level=logging.INFO)


class ReadYaml:
    current_path = os.path.abspath('.')
    father_tree_yaml = []


    def __init__(self,yaml_root_path):
        self.yaml_root_path = yaml_root_path

    def read_yaml(self, path):
        with open(path, 'r') as f:
            yaml_content = yaml.load(f, Loader=yaml.FullLoader)
        return yaml_content




    def find_inport_file(self, daily_bild_path):
        """
        递归找到yaml_root_path下的所有的yaml,append到self.father_tree_yaml中
        """

        info = self.read_yaml(daily_bild_path)
        if 'Import' in info:
            for i in info['Import']:
                path = self.yaml_root_path + i
                self.father_tree_yaml.append(path)
                self.find_inport_file(path)

    def yaml_tree(self,daily_bild_path):
        """
        生成一颗带层级关系的yaml tree
        yaml_tree格式：
        {
        one_father_yaml_path:[{1,first_yaml_child}],
        anther_father_yaml_path:[{1,first_yaml_child},{2,second_yaml_child}]
        }
        """
        # 遍历获取所有yaml文件
        self.find_inport_file(daily_bild_path)
        yaml_tree = {}

        # 根据路径判断父yaml、子yaml，并组成yaml_tree
        for f in self.father_tree_yaml:
            f = '/'.join(f.split('/')[:-1])
            yaml_tree[f] = []
            num = 1
            for i in self.father_tree_yaml:
                yaml_path = '/'.join(i.split('/')[:-1])
                if f in yaml_path and f != yaml_path:
                    child_path = {num: i}
                    yaml_tree[f].append(child_path)
                    num += 1
        pop_list = []
        for k,v in yaml_tree.items():
            if len(v) == 0:
                pop_list.append(k)
        for _ in pop_list:
            yaml_tree.pop(_)
        logging.info(f'yaml_tree:{yaml_tree}')
        return yaml_tree

    def merge_yaml(self, setup_yaml_path, merged_yaml_path, yaml_tree):
        """
        根据入参merge为一个新的总的yaml：
        setup_yaml_path：第一个入口的daily_bulid.yaml文件，如：'/data/test_repo/gml/configs/daily_build.yaml'
        merged_yaml_path： merge完成后生成的文件：如： '/data/test_yamls/all_daily.yaml'
        yaml_tree： 要merge的所有的yaml，如：
            {
                one_father_yaml_path:[{1,first_yaml_child}],
                anther_father_yaml_path:[{1,first_yaml_child},{2,second_yaml_child}]
            }
        """
        with open(merged_yaml_path, 'a+') as f:

            # 只有在setup_yaml_path才解析setup_module字段
            if 'setup_module' in self.read_yaml(setup_yaml_path):
                all_yaml_setup_module = {'setup_module': self.read_yaml(setup_yaml_path)['setup_module']}
                yaml.dump(all_yaml_setup_module, f, sort_keys=False)

            # 遍历yaml_tree的所有yaml
            # k为父yaml的path，v为父yaml下子yaml的序列和path
            for k,v in yaml_tree.items():

                # 解析父yaml的setup_class，只有父yaml才有setup_class
                if 'setup_class' in self.read_yaml(k+'/daily_build.yaml'):
                    setup_name = 'setup_class_' + k.split('/')[-1]
                    all_yaml_setup_class = {setup_name: self.read_yaml(k+'/daily_build.yaml')['setup_class']}
                    yaml.dump(all_yaml_setup_class, f, sort_keys=False)

                # 准备解析子yaml
                cases_name = 'case_' + k.split('/')[-1]
                all_yaml_case_data = {cases_name: []}
                num = 1

                # 遍历开始解析子yaml
                for i in v:
                    chile_path = i[num]
                    print(chile_path)
                    num += 1
                    father_case_name = chile_path.split('/')[-3] + '_' + chile_path.split('/')[-2]
                    cases = self.read_yaml(chile_path)['case']
                    for j in range(len(cases)):
                        cases[j]['casename'] = father_case_name + '_' + cases[j]['casename']
                        all_yaml_case_data[cases_name].append(cases[j])

                f.write(cases_name + ':\n')
                yaml.dump(all_yaml_case_data[cases_name], f, sort_keys=False)


if __name__ == '__main__':
    r = ReadYaml()
    setup_path = '/Users/liyang8/PycharmProjects/gmltest/data/test_repo/gml/configs/daily_build.yaml'
    merged_yaml_path = '/Users/liyang8/PycharmProjects/gmltest/data/all_daily.yaml'
    yaml_tree = r.yaml_tree(setup_path)


