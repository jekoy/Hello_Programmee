from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import os

def get_collection_title(url):
	html = urlopen(url)
	text = BeautifulSoup(html, 'html.parser')
	title = text.find('h2', {'class':'zm-item-title zm-editable-content'})
	return title.get_text().replace('\n', '')

def get_collection(url):
	title = get_collection_title(url)
	print('收藏夹 << '+ title + ' >>\n')
	page_index = 1
	page = ''
	file_name = title
	if not os.path.exists(file_name):
		os.mkdir(file_name)
	while True:
		f = open(file_name + os.sep + str(page_index) + '.txt', 'w', encoding = 'utf-8')
		html = urlopen(url + page)
		text = BeautifulSoup(html, 'html.parser')
		question = text.findAll('a', {'href':re.compile(r'/question/\d{1,}$')})
		answer = text.findAll('textarea', {'class':'content hidden'})
		store_collection(f, question, answer)
		print(url + page)
		print('  第 %d 页' % page_index + '加载完毕')
		page = re.search(r'\?page=\d{1,}(?=">下一页)', text.decode())
		page_index = page_index + 1
		if page == None:
			break
		else:
			page = page.group(0)
	print('\n收藏夹 < '+ title + ' > 已加载完毕')
	f.close()

def store_collection(file, question, answer):
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

number = '67808231'
url = 'https://www.zhihu.com/collection/' + number
get_collection(url)
