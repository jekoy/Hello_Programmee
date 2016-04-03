from urllib.request import urlopen
import re

def get_collection(url):
	html = urlopen(url)
	text = html.read().decode('utf-8', 'ignore')
	text = text.replace('&lt;br&gt;', '\n')
	text = text.replace('&lt;/b&gt;', '\n')
	text = text.replace('&lt;b&gt;', '\n')
	pattern = re.compile(r'((?<=<h2 class="zm-item-title"><a target="_blank" href="/question/\d{7}">)(.*?)(?=</a></h2>))|((?<=<h2 class="zm-item-title"><a target="_blank" href="/question/\d{8}">)(.*?)(?=</a></h2>))|((?<=<textarea class="content hidden">)(.*?)(?=<span class="answer-date-link-wrap">))', re.S)
	obj = re.findall(pattern, text)
	next_page = re.findall(r'\?page=\d{1,}(?=">下一页)', text)
	f = open('temp.txt', 'w', encoding = 'utf-8')
	for each in obj:
	    f.write(each[0] + each[2] + each[4])
	    f.write('\n---------------\n')
	f.close()
	return next_page

number = '28944253'
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

