# Python 3.6.3

import requests
import json
import sys
import re
import os
import importlib
import urllib3

importlib.reload(sys)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUCCESS = 1
FAIL = 0


class Ximalaya:
    def __init__(self, url):
        self.url = url  # 传入的专辑URL
        self.urlheader = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.url,
            'Cookie': '_ga=GA1.2.1628478964.1476015684; _gat=1',
        }

    def download_list(self):
        """生成待下载的文件列表

        :return:
        """
        if re.search(r'\d+/\d+', self.url):  # 解析单条音频文件
            track_id = self.url[self.url.rfind(r'/') + 1:]
            return self.analyze(track_id, 0)
        else:
            page_list = self.get_page()
            if not page_list:
                return FAIL
            seq = 0
            for pUrl in page_list:  # 解析每个专辑页面中的所有音频文件地址
                try:
                    response = requests.get(pUrl, headers=self.urlheader, verify=False).text
                except Exception as msg:
                    print(u'分页请求失败!', msg)
                    return FAIL
                if response:
                    # with open('.\web_backup\download_list.html', 'w', encoding='utf-8') as f:
                    #     f.write(response)
                    ids_reg = re.compile(r'<div class="text rC5T"><a title=".+?" href="(.+?)">')
                    ids_res = ids_reg.findall(response)
                    # print(ids_res)
                    ids_list = [j[j.rfind('/') + 1:] for j in ids_res]
                    for track_id in ids_list:
                        seq += 1
                        try:
                            self.analyze(track_id, seq)
                        except Exception as e:
                            print(e)
                else:
                    return FAIL
            return SUCCESS

    def analyze(self, track_id, seq):
        """解析音频文件地址

        :param track_id:
        :param seq:
        :return:
        """
        track_url = 'https://www.ximalaya.com/revision/play/tracks?trackIds=%s' % track_id
        # track_url = 'https://www.ximalaya.com/revision/play/tracks?trackIds=54000100'
        try:
            response = requests.get(track_url, headers=self.urlheader, verify=False).text
        except Exception as e:
            print(track_url + '解析失败!', e)
            with open('analyze_false.txt', 'ab+') as false_analyze:
                false_analyze.write(track_url + '\n')
            raise Exception('analyze fail')
        if response:
            jsonobj = json.loads(response)
            title = jsonobj['data']['tracksForAudioPlay'][0]['trackName']
            file_url = jsonobj['data']['tracksForAudioPlay'][0]['src']
            file_name = title.strip() + '.m4a'
            rec = re.compile(r'[ ;:|]')
            file_name_format = self.format_seq(seq) + rec.sub('', file_name)  # 去除空格、分号等
            print(file_name_format + ', ' + file_url)
            with open('download_list.txt', 'a+', encoding='gbk') as download_list_file:
                download_list_file.write('%s|%s\n' % (file_name_format, file_url))
        else:
            raise Exception('analyze fail')

    @staticmethod
    def format_seq(seq):
        """

        :param seq:
        :return:
        """
        if seq == 0:
            return ''
        elif 0 < seq < 10:
            return '00' + str(seq) + '.'
        elif 9 < seq < 100:
            return '0' + str(seq) + '.'
        else:
            return str(seq) + '.'

    def get_page(self):
        """获取分页数

        :return:
        """
        page_list = []  # 保存分页数
        try:
            response = requests.get(self.url, headers=self.urlheader, verify=False).text
        except Exception as msg:
            print(u'网页打开出错,请检查!', msg)
            return []
        if response:
            # with open('.\web_backup\get_page.html', 'w', encoding='utf-8') as f:
            #     f.write(response)
            reg_list = [re.compile(r'<li class="page-item.*?tthf"><a class="page-link tthf" href="(.+?)">')]
            for reg in reg_list:
                page_list.extend(reg.findall(response))
            if page_list:
                return ['http://www.ximalaya.com' + x for x in page_list]
            else:
                return [self.url]
        else:
            return []


if __name__ == '__main__':
    print('=' * 64)
    print(' ' * 23 + u'喜马拉雅FM批量下载' + ' ' * 23)
    print('=' * 64)
    if len(sys.argv) != 2:
        print(u'用法: ' + os.path.basename(sys.argv[0]) + u' 待下载专辑主页地址')
        print(u'实例: ' + os.path.basename(sys.argv[0]) + ' https://www.ximalaya.com/renwen/11021595/')
        sys.exit()
    ximalaya = Ximalaya(sys.argv[1])
    # Now: https://www.ximalaya.com/renwen/11021595/
    # Old: http://www.ximalaya.com/28757246/album/2842242?feed=reset
    if ximalaya.download_list() == SUCCESS:
        print('-' * 64)
        print(' ' * 28 + u'分析成功' + ' ' * 28)
        print('-' * 64)
    else:
        print('-' * 64)
        print(' ' * 28 + u'分析失败' + ' ' * 28)
        print('-' * 64)
