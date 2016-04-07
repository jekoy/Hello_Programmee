from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import subprocess
import time
import json

class Zhihu_Crawler(object):
	def __init__(self):
		pass

	def __save_cookies(self, file, session):
		f = open(file, 'w')
		json.dump(session.cookies.get_dict(), f)
		f.close()

	def __load_cookies(self, file):
		f = open(file, 'r')
		cookies = json.load(f)
		f.close()
		return cookies

	def login(self):
		session = requests.session()
		f_cookies = 'cookies'
		if os.path.exists(f_cookies):
			print('cookies已存在，直接登录中...')
			print('用户 UncP 已成功登录')
			cookies = self.__load_cookies(f_cookies)
			session.cookies.update(cookies)
			return session.cookies
		headers = {
			'User-Agent' :
			'Mozilla/5.0 (Windows NT 6.1, WOW64) AppleWebKit/537.36 \
			(KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 \
			QQBrowser/9.3.6873.400',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN, zh; q=0.8',
			'Host': 'www.zhihu.com',
			'Referer': 'http://www.zhihu.com/',
			'Connection': 'keep-alive'
		}
		login_data = {
			'email': '',
			'password': '',
			'rememberme': 'true',
    	}

		html = urlopen('https://www.zhihu.com')
		text = bs(html, 'html.parser').find('input', {'name': '_xsrf'})
		_xsrf = text.attrs['value']
		login_data['_xsrf'] = _xsrf

		print('使用验证码登录中...')
		captcha = session.get('http://www.zhihu.com/captcha.gif')
		f = open('captcha.gif', 'wb')
		f.write(captcha.content)
		f.close()
		subprocess.call('captcha.gif', shell = True)
		captcha_str = input('请输入验证码：')
		login_data['captcha'] = captcha_str
		os.remove('captcha.gif')

		html = session.post('https://www.zhihu.com/login/email', \
			 headers = headers, data = login_data)
		if html.json()['r'] == 0:
			print('    登录成功 :)\n\n')
			self.__save_cookies(f_cookies, session)
			return session.cookies
		else:
			print('    登录失败 :(')
			print(html.json()['msg'])
			return None

	def get_all_followees(self, people, cookies):
		url = 'http://www.zhihu.com/people/' + people + '/followees'
		user = re.search(r'(?<=people/)(.*?)(?=/)', url).group(0)
		print('开始获取用户 %s 的所有关注者 ...\n' % user)
		session = requests.session()
		html = session.get(url, cookies = cookies)
		text = html.text
		followees = re.findall(\
			r'(?<=href="https://www.zhihu.com/people/)(.*?)(?=")', text)
		# if followees == 0:
		# 	print('用户 %s 没有关注任何人 :(' % user)
		# else:
		# 	print('用户 %s 关注了以下用户\n' % user)
		# 	# print(len(followees))
		# 	# for each in followees:
		# 	# 	print(each)
		return followees

	def get_all_followees_collections(self, people, cookies):
		followees = self.get_all_followees(people, cookies)
		end = len(followees)
		print(people + ' 共有 %d 个关注者\n' % end)
		for i in range(0, end):
			print('开始加载第 %d 个关注者的收藏夹\n' % (i + 1))
			self.get_all_collections(followees[i], cookies)
			print('第 %d 个关注者的收藏夹加载完毕\n' % (i + 1))

	def get_all_collections(self, people, cookies):
		url = 'http://www.zhihu.com/people/' + people + '/collections'
		dir_ = re.search(r'(?<=people/)(.*?)(?=/)', url).group(0)
		print('开始加载所有 %s 的收藏夹 ...\n' % dir_)
		if not os.path.exists(dir_):
			os.mkdir(dir_)
		else:
			return
		parent_dir = os.getcwd()
		os.chdir(dir_)
		session = requests.session()
		html = session.get(url, cookies = cookies)
		text = bs(html.text, 'html.parser')
		collection_pages = text.findAll('a', \
			{'href':re.compile(r'/collection/\d+'), \
			'data-za-c':'collection'})
		end = len(collection_pages)
		if end == 0:
			print(people +' 没有收藏夹 :(\n')
		else:
			print(people + ' 有 %d 个收藏夹 :)\n' % end)
			for i in range(0, end):
				collection = collection_pages[i].attrs['href']
				self.url = 'https://www.zhihu.com' + collection
				self.__get_collection(i + 1)
				# time.sleep(1)
		os.chdir(parent_dir)

	def __get_collection_title(self):
		html = urlopen(self.url)
		text = bs(html, 'html.parser')
		title = text.find('h2', \
			{'class':'zm-item-title zm-editable-content'})
		return title.get_text().replace('\n', '')

	def __get_collection(self, number):
		title = self.__get_collection_title()
		print('    收藏夹 << '+ title + ' >>')
		page_index = 1
		page = ''
		file_name = title
		if not os.path.exists(file_name):
			os.mkdir(file_name)
		while True:
			f = open(file_name + os.sep + str(page_index) + '.txt', \
				'w', encoding = 'utf-8')
			html = urlopen(self.url + page)
			text = bs(html, 'html.parser')
			question = text.findAll('a', \
				{'href':re.compile(r'/question/\d{1,}$')})
			answer = text.findAll('textarea', {'class':'content hidden'})
			self.__store_collection(f, question, answer)
			print(self.url + page)
			print('  page %d completed' % page_index)
			page = re.search(r'\?page=\d{1,}(?=">下一页)', text.decode())
			page_index = page_index + 1
			if page == None:
				break
			else:
				page = page.group(0)
		print('\n第 %d' %number + ' 个收藏夹 << '+ title +' >> 已加载完毕\n')
		f.close()

	def __store_collection(self, file, question, answer):
		q_end = len(question)
		a_end = len(answer)
		re_question_number = re.compile(r'\d{1,}', re.S)
		re_answer_number = re.compile(r'(?<=question/)\d{1,}', re.S)
		j = 0
		for i in range(0, q_end):
			question_nu = re.search(re_question_number, question[i].decode())
			q_string = question[i].get_text()
			while j != a_end:
				answer_nu = re.search(re_answer_number, answer[j].decode())
				if answer_nu.group(0) != question_nu.group(0):
					break
				a_string = re.sub(r'&lt;(.*?)&gt;', '\n', answer[j].get_text())
				file.write('\n-------------------------\n' + \
					q_string + '\n-------------------------\n')
				file.write(a_string.replace('<br>', '\n'))
				j = j + 1

spider = Zhihu_Crawler()
cookies = spider.login()
if cookies != None:
	people = 'Unc-P'
	spider.get_all_followees_collections(people, cookies)
	# spider.get_all_collections('dodoru', cookies)
else:
	sys.exit()
