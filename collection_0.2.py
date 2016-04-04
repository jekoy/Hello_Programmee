from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def get_collection(url):
	html = urlopen(url)
	text = BeautifulSoup(html, 'html.parser')
	question = text.findAll('a', {'href':re.compile(r'/question/\d{1,}$')})
	answer = text.findAll('textarea', {'class':'content hidden'})
	store_collection(question, answer)

def store_collection(question, answer):
	f = open('collection.txt', 'w', encoding = 'utf-8')
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
			f.write(q_string + '\n-------------------------\n')
			f.write(a_string.replace('<br>', '\n'))
			j = j + 1
			if j < a_end:
				answer_nu = re.search(re_answer_number, answer[j].decode())
				if answer_nu.group(0) != question_nu.group(0):
					break
			else:
				break
	f.close()

number = '67808231'
url = 'https://www.zhihu.com/collection/' + number
page = ''
get_collection(url + page)
