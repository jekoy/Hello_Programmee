import requests, os, json, subprocess, re, sys, time
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
from info import Girl_Info

class Crawler():
	def __init__(self, user, password):
		self.session	  = requests.session()
		# cookies 文件名称
		self.cookie_file  = 'cookies'
		# 知乎主页
		self.base_url     = 'https://www.zhihu.com'
		# 知乎邮箱登陆页面
		self.login_url    = self.base_url + '/login/email'
		# 知乎用户页面
		self.people_url   = self.base_url + '/people/'
		# 知乎关注者页面
		self.fo_url = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
		self.session.data = {
			'email': user,
			'password': password,
			'remember_me': 'true'
		}
		self.session.headers = {
			'User-Agent':
				'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) \
				 Gecko/20100101 Firefox/44.0',
			# 'content-type': 'application/json',
			'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, deflate, br',
			'Host':'www.zhihu.com',
			'Referer': 'http://www.zhihu.com/',
			'Connection': 'keep-alive',
		}
		# 用户信息正则表达式
		self.info_re = re.compile(r'(?<=>)\d+(?=<)')
		# 用户 hash id 正则表达式
		self.hash_re = \
			re.compile(r'(?<=hash_id&quot;: &quot;)(.*?)(?=&quot;)')

	def __self_name(self):
		'''
			获取自己的昵称

		'''
		html  = self.session.get(self.base_url)
		text = bs(html.text, 'html.parser')
		info = text.find('span', {'class':'name'})
		name = info.get_text()
		return name

	def __load_cookies(self):
		'''
			加载 cookies

		'''
		with open(self.cookie_file, 'r') as f:
			cookies = json.load(f)
			f.close()
		return cookies

	def __get_xsrf(self):
		'''
			获取网站 _xsrf

		'''
		html = self.session.get(self.base_url)
		print(html.text)
		text = bs(html.text, 'html.parser').find('input', {'name': '_xsrf'})
		_xsrf = text.attrs['value']
		return _xsrf

	def login(self):
		'''
			登陆知乎

		'''
		print('加载 cookies 登陆中 ... ;)')
		self.session.cookies.update(self.__load_cookies())
		print('欢迎, ' + self.__self_name() + ' :)\n')

	def __get_argument(self, url):
		'''
			获取用户 hash id 和 关注者人数, 并返回

		'''
		html = self.session.get(url)
		text = html.text
		# print(text)
		info_hash = re.search(self.hash_re, text)
		hash_id = info_hash.group(0)

		text = bs(text, 'html.parser')
		info_fo = text.find('span', {'class':'zm-profile-section-name'})
		match = re.search(r'\d+', info_fo.get_text())
		followee_number = int(match.group(0))
		return hash_id, followee_number

	def get_all_followees(self, people):
		'''
			获取某个用户的所有关注者并置于列表, 然后返回

		'''
		url = self.people_url + people + '/followees'
		_xsrf = self.__get_xsrf()
		hash_id, followee_number = self.__get_argument(url)
		end = followee_number + 1
		self.session.headers['Referer'] = url
		users = []
		for index in range(0, end, 20):
			params = json.dumps({'offset':index, \
				'order_by':'created', 'hash_id':hash_id})
			data = {
		        'method': 'next',
		        'params': params,
		        '_xsrf':  _xsrf,
		    }
			html = self.session.post(self.fo_url, data=data)
			text = bs(''.join(html.json()['msg']), 'html.parser')
			content = text.findAll('h2', {'class':'zm-list-content-title'})
			regex = re.compile(r'(?<=people/)(.*?)(?=")')
			for each in content:
				info = re.search(regex, each.decode())
				followee = info.group(0)
				# print(followee)
				users.append(followee)
		return users

	def get_info(self, people):
		'''
			获取单个账号的信息

		'''
		url = self.people_url + people + '/about'
		html = self.session.get(url)
		text = bs(html.text, 'html.parser')
		girl = Girl_Info(people)
		print(str(text))
		# 昵称
		content = text.find('a', {'class':'name'})
		if content != None:
			girl.name = content.get_text()

		# 个签
		content = text.find('span', {'class':'bio'})
		if content != None:
			girl.bio = content.get_text()

		# 简介
		content = text.find('span', {'class':'content'})
		if content != None:
			girl.content = content.get_text().replace('填写个人简介', 'None')

		# 教育
		content = text.find('span', {'class':'education item'})
		if content != None:
			girl.education = content.get_text().replace('填写教育信息','None')

		# 教育+
		content = text.find('span', {'class':'education-extra item'})
		if content != None:
			girl.education_extra = content.get_text()

		# 行业
		content = text.find('span', {'class':'business item'})
		if content != None:
			girl.business = content.get_text().replace('填写行业', 'None')

		# 职业
		content = text.find('span', {'class':'employment item'})
		if content != None:
			girl.employment = content.get_text().replace('填写公司信息','None')

		# 职位
		content = text.find('span', {'class':'position item'})
		if content != None:
			girl.position = content.get_text().replace('填写职位', 'None')

		# 记录
		div = text.find('div', {'class':'profile-navbar clearfix'})
		if div != None:
			content = div.decode()
			nums = re.findall(self.info_re, content)
			girl.asks = int(nums[0])
			girl.answers = int(nums[1])
			girl.collections = int(nums[3])

		div = text.find('div', {'class':'zm-profile-module-desc'})
		if div != None:
			content = div.decode()
			nums = re.findall(self.info_re, content)
			girl.agree = int(nums[0])
			girl.thanks = int(nums[1])
			girl.favorites = int(nums[2])

		div = text.find('div',{'class':'zm-profile-side-following zg-clear'})
		if div != None:
			content = div.decode()
			nums = re.findall(self.info_re, content)
			girl.followees = int(nums[0])
			girl.followers = int(nums[1])
		print(girl)
		return girl

crawler = Crawler('770778010@qq.com', 'xupeng')
crawler.login()
followees =  crawler.get_all_followees('Unc-P')
f = open('Unc-P.txt', 'w')
for each in followees:
	print(each)
	info = crawler.get_info(each)
	f.write(info.str() + '\n\n')
	time.sleep(1)
f.close()
