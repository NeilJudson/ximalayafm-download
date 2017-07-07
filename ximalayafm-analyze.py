#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Version: Python 3.6.0

import requests
import json
import sys
import re
import os

if sys.version[0] == '2':
	reload(sys)
	sys.setdefaultencoding('utf-8')
elif sys.version[0] == '3':
	import importlib
	importlib.reload(sys)

SUCCESS = 1
FAIL = 0

class ximalaya:
	def __init__(self, url):
		self.url = url                                          # 传入的专辑URL
		self.urlheader = {
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'X-Requested-With': 'XMLHttpRequest',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Referer': self.url,
			'Cookie': '_ga=GA1.2.1628478964.1476015684; _gat=1',
		}

	def getpage(self):
		'''获取分页数'''
		pagelist = []                                           # 保存分页数
		try:
			response = requests.get(self.url, headers=self.urlheader).text
		except Exception as msg:
			print(u'网页打开出错,请检查!', msg)
		else:
			reg_list = [
				re.compile(r"class=\"pagingBar_wrapper\" url=\"(.*?)\""),
				re.compile(r"<a href='(/\d+/album/\d+\?page=\d+)' data-page='\d+'")
			]
			for reg in reg_list:
				pagelist.extend(reg.findall(response))
		if pagelist:
			return ['http://www.ximalaya.com' + x for x in pagelist[:-1]]
		else:
			return [self.url]

	def analyze(self, trackid, seq):
		'''解析真实mp3地址'''
		trackurl = 'http://www.ximalaya.com/tracks/%s.json' % trackid
		try:
			response = requests.get(trackurl, headers=self.urlheader).text
		except Exception:
			print(trackurl + '解析失败!')
			with open('analyze-false.txt', 'ab+') as false_analyze:
				false_analyze.write(trackurl + '\n')
			return FAIL
		else:
			jsonobj = json.loads(response)
			title = jsonobj['title']
			mp3 = (jsonobj['play_path']).encode('gbk')
			filename = title.strip() + '.mp3'
			rec = re.compile(r'[ ;:]')
			if seq == 0:
				filename_format = (rec.sub('',filename)).encode('gbk')                          # 去除空格、分号等
			else:
				filename_format = (str(seq) + '.' + rec.sub('',filename)).encode('gbk')         # 去除空格、分号等
			print(filename_format + ', ' + mp3)
			with open('download-list.txt', 'a+') as mp3file:
				mp3file.write('%s|%s\n' % (filename_format, mp3))
			return SUCCESS

	def todownlist(self):
		'''生成待下载的文件列表'''
		if 'sound' in self.url:                                 # 解析单条mp3
			trackid = self.url[self.url.rfind('/') + 1:]
			return self.analyze(trackid, 0)
		else:
			for purl in self.getpage():                         # 解析每个专辑页面中的所有mp3地址
				try:
					response = requests.get(purl, headers=self.urlheader).text
				except Exception as msg:
					print(u'分页请求失败!', msg)
					return FAIL
				else:
					ids_reg = re.compile(r'sound_ids="(.+?)"')
					ids_res = ids_reg.findall(response)
					idslist = [j for j in ids_res[0].split(',')]
					seq = 0
					for trackid in idslist:
						seq = seq + 1
						if self.analyze(trackid, seq) == FAIL:
							return FAIL
					return SUCCESS

if __name__ == '__main__':
	print('=' * 64)
	print(' ' * 23 + u'喜马拉雅FM批量下载' + ' ' * 23)
	print('=' * 64)
	if len(sys.argv) != 2:
		print(u'用法: ' + os.path.basename(sys.argv[0]) + u' 待下载专辑主页地址')
		print(u'实例: ' + os.path.basename(sys.argv[0]) + ' http://www.ximalaya.com/28757246/album/2842242?feed=reset')
		sys.exit()
	ximalaya = ximalaya(sys.argv[1])
	if ximalaya.todownlist() == SUCCESS:
		print('-' * 64)
		print(' ' * 28 + u'分析成功' + ' ' * 28)
		print('-' * 64)
	else:
		print('-' * 64)
		print(' ' * 28 + u'分析失败' + ' ' * 28)
		print('-' * 64)
