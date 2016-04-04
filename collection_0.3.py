from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import os
import time

class Zhihu_Crawler(object):
	def __init__(self, url):
		self.url = url

	def get_all_collections(self):
		dir_ = re.search(r'(?<=people/)(.*?)(?=/)', self.url).group(0)
		print('开始加载所有 %s 的收藏夹 ...\n' % dir_)
		if not os.path.exists(dir_):
			os.mkdir(dir_)
		os.chdir(dir_)
		print(self.url)
		html = urlopen(self.url)
		text = BeautifulSoup(html, 'html.parser')
		collection_pages = text.findAll('a', \
			{'href':re.compile(r'/collection/\d{1,}'), 'data-za-c':'collection'})
		end = len(collection_pages)
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
		a_end = len(answer) - 1
		re_question_number = re.compile(r'\d{1,}', re.S)
		re_answer_number = re.compile(r'(?<=question/)\d{1,}', re.S)
		j = 0
		for i in range(0, q_end):
			question_nu = re.search(re_question_number, question[i].decode())
			while True:
				q_string = question[i].get_text()
				a_string = answer[j].get_text()
				answer_nu = re.search(re_answer_number, answer[j].decode())
				if answer_nu.group(0) != question_nu.group(0):
					break
				file.write('\n-------------------------\n' + \
					q_string + '\n-------------------------\n')
				file.write(a_string.replace('<br>', '\n'))
				j = j + 1
				if j < a_end:
					answer_nu = re.search(re_answer_number, answer[j].decode())
					if answer_nu.group(0) != question_nu.group(0):
						break
				else:
					break
# viview
# dodoru
people = 'dandanjie'
url = 'https://www.zhihu.com/people/' + people + '/collections'
spider = Zhihu_Crawler(url)
spider.get_all_collections()
