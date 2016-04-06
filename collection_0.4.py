from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import time

class Zhihu_Crawler(object):
	def __init__(self, url):
		self.url = url

	def login(self):
		headers = {
			'User-Agent' :
			'Mozilla/5.0 (Windows NT 6.1, WOW64) AppleWebKit/537.36 (KHTML, like \
			Gecko) Chrome/47.0.2526.80 Safari/537.36 QQBrowser/9.3.6873.400',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN, zh; q=0.8',
			'Host': 'www.zhihu.com',
			'Referer': 'http://www.zhihu.com/',
			'Connection': 'keep-alive'
		}
		login_data = {
			'email': 'email',
			'password': 'password',
			'rememberme': 'true',
    	}

		html = urlopen('https://www.zhihu.com')
		text = BeautifulSoup(html, 'html.parser').find('input', {'name': '_xsrf'})
		_xsrf = text.attrs['value']
		login_data['_xsrf'] = _xsrf

		# captcha = session.get('http://www.zhihu.com/captcha.gif')
		# f = open('captcha.gif', 'wb')
		# for line in captcha.iter_content(10):
		#     f.write(line)
		# f.close()
		# print('打开文件\'captcha.gif\'')
		# print ('输入验证码:')
		# captcha_str = input()
		# login_data['captcha'] = captcha_str
		session = requests.session()
		html = session.post('https://www.zhihu.com/login/email', \
			headers = headers, data = login_data)
		if html.status_code == 200:
			print('--- 登录成功 --- :)')
			return html.cookies
		else:
			print('--- 登录失败 --- :(')
			return None

	def get_all_collections(self,cookies):
		dir_ = re.search(r'(?<=people/)(.*?)(?=/)', self.url).group(0)
		print('开始加载所有 %s 的收藏夹 ...\n' % dir_)
		if not os.path.exists(dir_):
			os.mkdir(dir_)
		os.chdir(dir_)
		# print(self.url)
		session = requests.session()
		html = session.get(self.url, cookies = cookies)
		text = BeautifulSoup(html.text, 'html.parser')
		collection_pages = text.findAll('a', \
			{'href':re.compile(r'/collection/\d+'), 'data-za-c':'collection'})
		end = len(collection_pages)
		if end == 0:
			print('\n用户没有收藏夹 :(')
			return
		print('用户共有 %d 个收藏夹' % end)
		for i in range(0, end):
			collection = collection_pages[i].attrs['href']
			self.url = 'https://www.zhihu.com' + collection
			self.get_collection()
			print('第 %d 个收藏夹加载完毕\n\n\n' % (i + 1))
			time.sleep(1)

	def get_collection_title(self):
		html = urlopen(self.url)
		text = BeautifulSoup(html, 'html.parser')
		title = text.find('h2', {'class':'zm-item-title zm-editable-content'})
		return title.get_text().replace('\n', '')

	def get_collection(self):
		title = self.get_collection_title()
		print('    收藏夹 << '+ title + ' >>\n')
		page_index = 1
		page = ''
		file_name = title
		if not os.path.exists(file_name):
			os.mkdir(file_name)
		while True:
			f = open(file_name + os.sep + str(page_index) + '.txt', \
				'w', encoding = 'utf-8')
			html = urlopen(self.url + page)
			text = BeautifulSoup(html, 'html.parser')
			question = text.findAll('a', {'href':re.compile(r'/question/\d{1,}$')})
			answer = text.findAll('textarea', {'class':'content hidden'})
			self.store_collection(f, question, answer)
			print(self.url + page)
			print('  第 %d 页' % page_index + '加载完毕')
			page = re.search(r'\?page=\d{1,}(?=">下一页)', text.decode())
			page_index = page_index + 1
			if page == None:
				break
			else:
				page = page.group(0)
		print('\n收藏夹 < '+ title + ' > 已加载完毕')
		f.close()

	def store_collection(self, file, question, answer):
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

people = 'Unc-P'
url = 'https://www.zhihu.com/people/' + people + '/collections'
spider = Zhihu_Crawler(url)
cookies = spider.login()
if cookies != None:
	spider.get_all_collections(cookies)
else:
	sys.exit()
