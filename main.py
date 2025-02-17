import sys

from utils.create_tests import CreateTestFile
from common.yaml_check import *
import os

logging.basicConfig(level=logging.ERROR)


def parse_args():
    pass

run_configs = [
        {'workspace': '~/gml_daily/gml'},
        {'login_ursername': '***'},
        {'login_password': '***'},
        {'run_cluster': '10.5.36.31'},
        {'run_pat': 'pat_dev'},
        {'source_env': 'source pt1.6.0 mmcv=1.4.6'},
        {'branch':'master'}
    ]

# 程序入口
def main():

    current_path = os.path.dirname(os.path.abspath(__file__))
    # 获取参数
    for i in range(len(sys.argv) - 1):
        k = list(run_configs[i].keys())
        if i == 5:
            run_configs[i][k[0]] = ' '.join(sys.argv[i + 1:])
            break
        run_configs[i][k[0]] = sys.argv[i + 1]
    logging.info(f'run_configs:{run_configs}')

    # 删除已有tests、merged yaml、repo files文件
    setup_tool = SetUpEnv()
    setup_tool.setup_build_file()

    # clone repo
    repo_url = 'git@gitlab.sz.sensetime.com:parrotsDL-sz/gml.git'
    repo_branch = run_configs[6]['branch']
    print(f'repo_branch:{repo_branch}')
    setup_tool.clone_gml_yaml(repo_url,repo_branch)

    # 递归便利import，获取yaml tree
    yaml_root_path = current_path + '/data/test_repo/gml/'
    print(f'current_path:{current_path}')
    daily_bild_path = yaml_root_path + 'configs/daily_build.yaml'
    r = ReadYaml(yaml_root_path)
    yaml_tree = r.yaml_tree(daily_bild_path)

    # 校验yaml文件是否符合规范
    checker = YamlCheck()
    checker.yaml_check(daily_bild_path, yaml_tree)

    # merge yaml
    merged_yaml_path = current_path + '/data/test_yamls/all_daily.yaml'
    os.makedirs(current_path + '/data/test_yamls', exist_ok=True)
    if not os.path.exists(merged_yaml_path):
        os.mknod(merged_yaml_path)
    r.merge_yaml(daily_bild_path, merged_yaml_path,yaml_tree)

    # 将merged的yaml转化为pytest文件
    tests_path = current_path + '/tests/test_all_cases.py'
    setup_test_file_path = current_path + '/data/pytest_file_setup.txt'
    if not os.path.exists(setup_test_file_path):
        os.mknod(setup_test_file_path)
    with open(setup_test_file_path, 'w') as f:
        f.write("# -*- coding:utf-8 -*-\nimport pytest\nimport os\nimport time\nimport allure\n\n\nfrom common.utils.util import Utils\nfrom common.utils import ssh_clinet\n\nssh = ssh_clinet.SSHClient()")
    creater = CreateTestFile()
    yaml_config = r.read_yaml(merged_yaml_path)
    creater.write_test_file(yaml_config, tests_path, setup_test_file_path,run_configs)

if __name__ == '__main__':
    main()
