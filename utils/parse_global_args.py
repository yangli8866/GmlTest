# coding=utf-8
import time
import re
# from util import Utils
from utils import Utils


class ParseGlobal:

    def scan_global_arrs(self, text):
        # 解析出全局变量名
        # step1:解析出被{{}}括起来的变量名
        s = re.findall(r'{{(.+?)}}', text)
        global_arrs_names = [x for x in s if x.isupper()]
        return global_arrs_names

    def named_global_arrs(self, global_arrs_names):
        # 为每个global命名
        global_arrs = {}
        x = 1
        for i in set(global_arrs_names):
            global_arrs[i] = 'gml_auto_arr_' + time.strftime("%H%M%S", time.localtime()) + str(x)
            x += 1
        return global_arrs

    def replace_global_in_text(self, text, global_arrs):
        # 将text中的全局变量{{}}都替换为对应的名字
        for k, v in global_arrs.items():
            old = '${{' + k + '}}'
            text = text.replace(old, v)
        return text

    def parse_global(self, text):
        global_arrs_names = self.scan_global_arrs(text)
        global_arrs = self.named_global_arrs(global_arrs_names)
        text = self.replace_global_in_text(text, global_arrs)
        return text


if __name__ == '__main__':
    parse_global = ParseGlobal()
    text = Utils.read_file_info('../test.yml')
    text = parse_global.parse_global(text)
    print(text)
