from urllib.request import urlopen
import re

def get_collection(url):
	html = urlopen(url)
	text = html.read().decode('utf-8', 'ignore')
	qu_an = re.compile(r'((?<="/question/\d{6}">)(.*?)(?=</a></h2>))|((?<="/question/\d{7}">)(.*?)(?=</a></h2>))|((?<="/question/\d{8}">)(.*?)(?=</a></h2>))|((?<=<textarea class="content hidden">)(.*?)(?=<span class="answer-date-link-wrap">))', re.S)
	obj = re.findall(qu_an, text)
	next_page = re.findall(r'\?page=\d{1,}(?=">下一页)', text)
	f = open('zhihu.txt', 'w', encoding = 'utf-8')
	for each in obj:
		answer = re.sub(r'&lt;(.+?)&gt;','\n',each[6])
		f.write(each[4] + answer)
		f.write('\n---------------\n')
	f.close()
	return next_page

number = '67808231'
url = 'https://www.zhihu.com/collection/'
url = url + number
page = ''
while True:
	next_page = get_collection(url + page)
	if next_page == None:
		break
	else:
		page = next_page[0]
		input('press Enter key to continue ...\n')
