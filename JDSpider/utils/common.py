# _*_ coding:utf-8 _*_
__author__ = 'iszoop'
__date__ = '2018/7/12 20:27'
import hashlib
import re

def get_md5(url):
    #将url转换为MD5码
    if isinstance(url,str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    #从字符串中提取数字
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

if __name__ == "__main__":
    print(get_md5("http://jobbole.com".encode("utf-8")))

