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

class Ximalaya:
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
	
	def toDownList(self):
		'''生成待下载的文件列表'''
		if 'sound' in self.url:                                 # 解析单条音频文件
			trackId = self.url[self.url.rfind('/') + 1:]
			return self.analyze(trackId, 0)
		else:
			for pUrl in self.getPage():                         # 解析每个专辑页面中的所有音频文件地址
				try:
					response = requests.get(pUrl, headers=self.urlheader).text
				except Exception as msg:
					print(u'分页请求失败!', msg)
					return FAIL
				else:
					idsReg = re.compile(r'sound_ids="(.+?)"')
					idsRes = idsReg.findall(response)
					idsList = [j for j in idsRes[0].split(',')]
					seq = 0
					for trackId in idsList:
						seq = seq + 1
						if self.analyze(trackId, seq) == FAIL:
							return FAIL
					return SUCCESS
	
	def analyze(self, trackId, seq):
		'''解析音频文件地址'''
		trackUrl = 'http://www.ximalaya.com/tracks/%s.json' % trackId
		try:
			response = requests.get(trackUrl, headers=self.urlheader).text
		except Exception:
			print(trackUrl + u'解析失败!')
			with open('analyze-false.txt', 'ab+') as falseAnalyze:
				falseAnalyze.write(trackUrl + '\n')
			return FAIL
		else:
			jsonobj = json.loads(response)
			title = jsonobj['title']
			fileUrl = (jsonobj['play_path']).encode('gbk')
			fileName = title.strip() + '.m4a'
			rec = re.compile(r'[ ;:]')
			fileNameFormat = (self.formatSeq(seq) + rec.sub('',fileName)).encode('gbk')         # 去除空格、分号等
			print(fileNameFormat + ', ' + fileUrl)
			with open('download-list.txt', 'a+') as downloadListFile:
				downloadListFile.write('%s|%s\n' % (fileNameFormat, fileUrl))
			return SUCCESS
	
	def formatSeq(self, seq):
		if seq == 0:
			print(seq)
			return ''
		elif 0 < seq < 10:
			print(seq)
			return ('00' + str(seq) + '.')
		elif 9 < seq < 100:
			print(seq)
			return ('0' + str(seq) + '.')
		else:
			print(seq)
			return (str(seq) + '.')
	
	def getPage(self):
		'''获取分页数'''
		pageList = []                                           # 保存分页数
		try:
			response = requests.get(self.url, headers=self.urlheader).text
		except Exception as msg:
			print(u'网页打开出错,请检查!', msg)
		else:
			regList = [
				re.compile(r"class=\"pagingBar_wrapper\" url=\"(.*?)\""),
				re.compile(r"<a href='(/\d+/album/\d+\?page=\d+)' data-page='\d+'")
			]
			for reg in regList:
				pageList.extend(reg.findall(response))
		if pageList:
			return ['http://www.ximalaya.com' + x for x in pageList[:-1]]
		else:
			return [self.url]
	
if __name__ == '__main__':
	print('=' * 64)
	print(' ' * 23 + u'喜马拉雅FM批量下载' + ' ' * 23)
	print('=' * 64)
	if len(sys.argv) != 2:
		print(u'用法: ' + os.path.basename(sys.argv[0]) + u' 待下载专辑主页地址')
		print(u'实例: ' + os.path.basename(sys.argv[0]) + ' http://www.ximalaya.com/28757246/album/2842242?feed=reset')
		sys.exit()
	ximalaya = Ximalaya(sys.argv[1])
	if ximalaya.toDownList() == SUCCESS:
		print('-' * 64)
		print(' ' * 28 + u'分析成功' + ' ' * 28)
		print('-' * 64)
	else:
		print('-' * 64)
		print(' ' * 28 + u'分析失败' + ' ' * 28)
		print('-' * 64)
