import os
import logging
import shutil

logging.basicConfig(level=logging.INFO)


class SetUpEnv:
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


    def setup_build_file(self):
        """
            delete exists file
        """
        # delete test cases
        tests_list = os.listdir(self.root_path + '/tests')
        for i in tests_list:
            if 'test_' in i:
                os.remove(self.root_path + '/tests/' + i)
                logging.info('{}文件被删除了'.format('/tests/' + i))
        
        if os.path.exists(os.path.join(self.root_path, 'data')):
            # delete merged yamls
            yaml_path = self.root_path + '/data/test_yamls/'
            if os.path.exists(yaml_path):
                yaml_list = os.listdir(yaml_path)
                for i in yaml_list:
                    if '.yaml' in i:
                        os.remove(yaml_path + i)
                        logging.info('{}文件被删除了'.format('/data/test_yamls/' + i))
            # delete repo
            gml_repo_path = self.root_path + '/data/test_repo'
            if os.path.exists(gml_repo_path):
                shutil.rmtree(gml_repo_path)


    def clone_gml_yaml(self,repo_url,repo_branch):
        os.mkdir(self.root_path + '/data/test_repo')
        os.chdir(self.root_path + '/data/test_repo')
        cmd = 'git clone ' + repo_url + ' -b ' + repo_branch
        print(f'cmd:{cmd}')
        os.system(cmd)
        os.system('ls')



if __name__ == '__main__':
    s = SetUpEnv()
    # s.clone_gml_yaml()
    # s.setup_build_file()