from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import os, sys, subprocess, time, re, json, requests

class Zhihu_Crawler(object):
	def __init__(self, user, password):
		'''
			初始化知乎爬虫

		'''
		self.session = requests.session()
		self.session.headers = {
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
		self.session.data = {
			'email': user,
			'password': password,
			'rememberme': 'true',
    	}

	def __self_id(self):
		'''
			获取用户知乎 id

		'''
		html  = self.session.get('https://www.zhihu.com')
		regex = re.compile(r'(?<=user_hash":")(.*?)(?=")', re.S)
		Id    = re.search(regex, html.text)
		return Id.group(0)

	def __self_name(self):
		'''
			获取用户知乎昵称

			返回昵称
		'''
		html = self.session.get('http://www.zhihu.com')
		text = bs(html.text, 'html.parser')
		name = text.find('span', {'class':'name'})
		return name.get_text()

	def __save_cookies(self, file):
		'''
			保存 cookies 于当前目录

		'''
		f = open(file, 'w')
		print(self.session.cookies)
		json.dump(self.session.cookies.get_dict(), f)
		f.close()

	def __load_cookies(self, file):
		'''
			加载 cookies

		'''
		f = open(file, 'r')
		cookies = json.load(f)
		f.close()
		return cookies

	def __verify_captcha(self):
		'''
			输入验证码

		'''
		print('使用验证码登录中...')
		url = 'http://www.zhihu.com/captcha.gif'
		captcha = self.session.get(url)
		f = open('captcha.gif', 'wb')
		f.write(captcha.content)
		f.close()
		subprocess.call('captcha.gif', shell = True)
		print('请输入验证码:')
		captcha = input('')
		os.remove('captcha.gif')
		return captcha

	def __get_xsrf(self):
		'''
			获取 _xsrf

		'''
		html = self.session.get('https://www.zhihu.com')
		text = bs(html.text, 'html.parser').find('input', {'name': '_xsrf'})
		xsrf = text.attrs['value']
		return xsrf

	def __get_collection_title(self, url):
		'''
			获取收藏夹名称

			返回收藏夹名称
		'''
		html = self.session.get(url)
		text = bs(html.text, 'html.parser')
		title = text.find('h2', \
			{'class':'zm-item-title zm-editable-content'})
		title = re.sub(r'\\|/|\"|\?|\*|\:|\<|\>|\||\n|\s', '', \
			title.get_text())
		return title

	def __get_collection(self, url, number):
		'''
			获取某个收藏夹，并将内容写入以收藏夹名为目录的文件夹

			无返回类型
		'''
		title = self.__get_collection_title(url)
		print('    收藏夹 << '+ title + ' >>')
		page_index = 1
		page = ''
		if not os.path.exists(title):
			os.mkdir(title)
		while True:
			f = open(title + os.sep + str(page_index) + '.txt', \
				'w', encoding='utf-8')
			html = self.session.get(url + page)
			text = bs(html.text, 'html.parser')
			questions = self.__get_questions(text)
			answers = self.__get_answer(text)
			self.__store_collection(f, question, answer)
			print(url + page)
			print('  page %d completed' % page_index)
			page = re.search(r'\?page=\d+(?=">下一页)', text.decode())
			page_index = page_index + 1
			if page == None:
				break
			else:
				page = page.group(0)
		print('\n第 %d' %number + ' 个收藏夹 << '+ title +' >> 已加载完毕\n')
		f.close()

	def __get_questions(self, text):
		'''
			在单个页面内获取所有问题及其序列号，组成元组列表并返回

		'''
		questions = []
		content = text.findAll('h2', \
			{'class':re.compile(r'zm-item-title')})
		nu_re = re.compile(r'(?<=question/)\d+')
		content = content[1:]
		for each in content:
			question = each.get_text()[:-1]
			number = re.search(nu_re, each.decode()).group(0)
			questions.append([number, question])
		return questions

	def __get_answer(self, text):
		'''
			在单个页面内获取所有回答及其问题序列号，组成元组列表并返回

		'''
		answers = []
		content = text.findAll('textarea', {'class':'content hidden'})
		nu_re = re.compile(r'(?<=question/)\d+')
		for each in content:
			answer = each.get_text()
			number = re.search(nu_re, each.decode()).group(0)
			answers.append([number, answer])
		return answers

	def __store_pic(self, title, url):
		'''
			保存图片

		'''
		html = urlopen(url)
		index = 1
		suffix = '.' + url.split('.')[-1]
		f_name = title + str(index) + suffix
		while os.path.exists(f_name):
			index = index + 1
			f_name = title + str(index) + suffix
		with open(f_name, 'wb') as f:
			f.write(html.read())
			f.close()

	def __answer_filter(self, title, answer):
		'''
			对回答进行内容过滤，清除换行符、html标记对；保存图片

			返回过滤后的答案
		'''
		print(answer)
		p_re = re.compile(r'(?<=img src=")(.*?)(?=")', re.S)
		for url in pics:
			self.__store_pic(title, 'https' + url)
		answer = re.sub('<(.*?)>', ' ', answer)			# 过滤 html 标记对
		return answer

	def __store_collection(self, file, question, answer):
		'''
			存储问题与对应的答案于某个文件

			无返回类型
		'''
		j = 0
		for q_elem in questions:
			while True:
				if answers[j][0] == q_elem[0]:
					file.write('\n-------------------------\n' + \
						q_elem[1] + '\n-------------------------\n')
					if len(q_elem[1]) > 28:
						q_elem[1] = q_elem[1][0:28]
					answer = self.__filter_answer(q_elem[1], answers[j][1])
					file.write(answer)
					j = j + 1
				else:
					break

	def __store_partial_collection(self, file, question, answer, size):
		'''
			存储部分问题与答案于某个文件，用于更新收藏夹

			无返回类型
		'''
		j = 0
		for q_elem in questions:
			while True:
				if answers[j][0] == q_elem[0]:
					file.write('\n-------------------------\n' + \
						q_elem[1] + '\n-------------------------\n')
					if len(q_elem[1]) > 28:
						q_elem[1] = q_elem[1][0:28]
					answer = self.__filter_answer(q_elem[1], answers[j][1])
					file.write(answer)
					j = j + 1
					if j == size:
						return
				else:
					break

	def __update(self, collection, count):
		'''
			更新某个收藏夹一定数量的内容

			无返回类型
		'''
		url = 'http://www.zhihu.com/collection/' + collection
		title = self.__get_collection_title(url)
		page_index = 1
		page = ''
		size = 0
		while True:
			file = open(title + '.txt', 'w', encoding='utf-8')
			print('文件名 %s' % title)
			html = self.session.get(url + page)
			text = bs(html.text, 'html.parser')
			questions = self.__get_questions(text)
			answers   = self.__get_answer(text)
			size = len(answers)
			number = 0
			if size >= count:
				number = count
			else:
				number = size
			count -= number
			self.__store_partial_collection(file, questions, answers, number)
			if count == 0:
				break
			page = re.search(r'\?page=\d+(?=">下一页)', text.decode())
			page_index = page_index + 1
			if page == None:
				break
			else:
				page = page.group(0)
		print('收藏夹 << '+ title +' >> 已更新完毕\n')

	def login(self):
		'''
			登录知乎：
				若 cookies 存在，则直接登录，
				否则使用验证码登录
		'''
		f_cookies = 'cookies'		# cookies 文件
		# 使用 cookies 登录
		if os.path.exists(f_cookies):
			print('cookies已存在，直接登录中...')
			cookies = self.__load_cookies(f_cookies)
			self.session.cookies.update(cookies)
			name = self.__self_name()
			print('用户 %s 登录成功' % name)
			return

		# 使用验证码登录
		_xsrf = self.__get_xsrf()
		login_data['_xsrf'] = _xsrf

		captcha = self.__verify_captcha()
		login_data['captcha'] = captcha

		html = self.session.post('https://www.zhihu.com/login/email')
		if html.json()['r'] == 0:
			print('    登录成功 :)\n\n')
			self.__save_cookies(f_cookies)
		else:
			print('    登录失败 :(')
			print(html.json()['msg'])
			sys.exit()
			# return None

	def get_hash_id(self, people):
		'''
			获取某个用户的知乎 id

		'''
		html = self.session.get('https://www.zhihu.com/people/' \
			+ people + '/followees')
		hash_id = re.search(r'(?<=hash_id&quot;: &quot;)(.*?)(?=&quot;)', \
			html.text)
		# print(hash_id.group(0))
		return hash_id.group(0)

	def get_followees_number(self, people):
		'''
			获取某个用户的关注者数目

			返回关注者数量
		'''
		url = 'http://www.zhihu.com/people/' + people + '/followees'
		html = self.session.get(followee_url)
		text = bs(html.text, 'html.parser')
		info = text.find('span', {'class':'zm-profile-section-name'})
		match = re.search(r'\d+', info.get_text())
		followees = int(match.group(0))
		return followees

	def get_all_followees(self, people):
		'''
			获取某个用户的所有关注者，名字形式为用户网页昵称
			每次获取 20 个，置于 users 列表

			返回所有关注者
		'''
		users = []
		_xsrf = self.__get_xsrf()
		hash_id = self.get_hash_id(people)
		followees = self.get_followees_number(people)
		self.session.headers['Referer'] = 'http://ww.zhihu.com/people/' \
			+ people + '/followees'
		url = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
		end = followees + 1
		for index in range(0, end, 20):
			params = json.dumps({'order_by':'created', \
				 'offset':index, 'hash_id':hash_id})
			# params ='{"offset":' + str(index) + ',"order_by":"created","hash_id":'+ hash_id +'}'
			data = {
		        'method': 'next',
		        'params': params,
		        '_xsrf':  _xsrf,
		    }
			html = self.session.post(url, data=data)
			text = bs(''.join(html.json()['msg']), 'html.parser')
			content = text.findAll('h2', {'class':'zm-list-content-title'})
			regex = re.compile(r'(?<=people/)(.*?)(?=")')
			for each in content:
				followee = re.search(regex, each.decode())
				users.append(followee.group(0))
		return followees

	def get_all_followees_collections(self, people):
		'''
			获取某个用户所有关注者的所有收藏夹

		'''
		followees = self.get_all_followees(people)
		end = len(followees)
		print(people + ' 共有 %d 个关注者\n' % end)
		for i in range(0, end):
			print('第 %d 个关注者的收藏夹\n' % (i + 1))
			self.store_all_collections(followees[i])
			print('第 %d 个关注者的收藏夹加载完毕\n' % (i + 1))

	def get_all_collections(self, people):
		'''
			获取某个用户的所有收藏夹

			返回所有收藏夹号码组成的列表
		'''
		collections = []
		page = ''
		base_url = 'http://www.zhihu.com/people/' + people + '/collections'
		while True:
			html = self.session.get(url + page)
			text = bs(html.text, 'html.parser')
			collection_page = text.findAll('a', \
				{'href':re.compile(r'/collection/\d+'), \
				'data-za-c':'collection'})
			for each in collection_page:
				collections.append(each.attrs['href'] \
					.replace('/collection/', ''))
			page = re.search(r'\?page=\d+(?=">下一页)', text.decode())
			if page == None:
				break
		return collections

	def store_all_collections(self, people):
		'''
			获取并存储某个用户所有的收藏夹

		'''
		print('开始加载所有 %s 的收藏夹 ...\n' % people)
		parent_dir = os.getcwd()
		if not os.path.exists(people):
			os.mkdir(people)
		else:
			return
		os.chdir(people)
		collections = self.get_all_collections(people)
		end = len(collections)
		if end == 0:
			print(people +' 没有收藏夹 :(\n')
		else:
			print(people + ' 有 %d 个收藏夹 :)\n' % end)
			for i in range(0, end):
				url = 'https://www.zhihu.com/collection/' + collection
				self.__get_collection(url, i + 1)
		os.chdir(parent_dir)

	def update_collections(self):
		html = self.session.get('http://www.zhihu.com/collections')
		text = bs(html.text, 'html.parser')
		# 所有收藏夹
		collections = text.findAll('h2', {'class':'zm-item-title'})
		collection_re = re.compile(r'(?<=collection/)\d+')
		update_re = re.compile(r'(?<=<span class="zg-num">)(\d+)(?=</span>)')
		num = 0
		for each in collections:
			s = str(each)
			# 收藏夹的序列号
			collection = re.search(collection_re, s)
			# 收藏夹更新数量
			count = re.search(update_re, s)
			if collection != None and count != None:
				c = collection.group(0)
				n = int(count.group(0))
				print(c, n)
				self.__update(c, n)
				num = num + 1
				print('第 %d 个收藏夹更新完毕\n' % num)
		print('共更新 %d 个' % num)
		print('所有收藏夹已更新完毕 :)')


user = '770778010@qq.com'
password = 'xupeng'
spider = Zhihu_Crawler(user, password)
spider.login()
