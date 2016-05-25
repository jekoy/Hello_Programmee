import requests, re, json, time, subprocess, os, sys
from bs4 import BeautifulSoup as soup
from programmee import Programmee

class Crawler():
	def __init__(self, user):
		self.user = user
		self.session	  = requests.session()
		# cookies 文件名称
		self.cookie_file  = 'cookies'
		# 知乎主页
		self.base_url     = 'https://www.zhihu.com'
		# 知乎用户页面
		self.people_url   = self.base_url + '/people/'
		# 知乎关注者页面
		self.fo_url = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
		self.session.data = {
			'email':'770778010@qq.com',
			'password':'xupeng',
			'remember_me':'true',
		}
		self.session.headers = headers = {
			'User-Agent':
				'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) \
				 Gecko/20100101 Firefox/44.0',
			# 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
			# 'Accept-Encoding': 'gzip, deflate, br',
			'Host':'www.zhihu.com',
			'Referer': 'http://www.zhihu.com/',
			# 'Connection': 'keep-alive',
		}

		# 用户信息正则表达式
		self.info_re = re.compile(r'(?<=>)\d+(?=<)')
		# 用户 hash id 正则表达式
		self.hash_re = \
			re.compile(r'(?<=hash_id&quot;: &quot;)(.*?)(?=&quot;)')
		# 知乎女程序员判定正则表达式
		self.pro_re = re.compile(u'程序|CS|计算机|软件|代码|前端| \
			阿里|腾讯|百度|网易|Google|Microsoft|Facebook')

	def __load_cookies(self):
		'''
			加载 cookies

		'''
		with open(self.cookie_file, 'r') as f:
			cookies = json.load(f)
			f.close()
		return cookies

	def __get_site(self, url):
		text  = None
		count = 0
		while count < 3:
			try:
				html = self.session.get(url, timeout=3)
				if html.status_code == 200:
					text = html.text
					break
			except requests.exceptions.RequestException:
				pass
			count += 1
			time.sleep(1)
		return text

	def __post_site(self, url, data):
		text  = None
		count = 0
		while count < 3:
			try:
				html = self.session.post(url, data=data)
				if html.status_code == 200:
					text = ''.join(html.json()['msg'])
					break
			except requests.exceptions.RequestException:
				print(html.status_code)
			count += 1
			time.sleep(1)
			print(html.status_code)
		return text

	def __get_xsrf(self):
		'''
			获取网站 _xsrf

		'''
		text = self.__get_site(self.base_url)
		if text == None:
			return None
		info = soup(text, 'html.parser').find('input', {'name': '_xsrf'})
		_xsrf = info.attrs['value']
		return _xsrf

	def __get_argument(self, url):
		'''
			获取用户 hash id 和 关注者人数, 并返回

		'''
		text = self.__get_site(url)
		if text == None:
			return None, None
		info_hash = re.search(self.hash_re, text)
		hash_id = info_hash.group(0)

		text = soup(text, 'html.parser')
		info_fo = text.find('span', {'class':'zm-profile-section-name'})
		match = re.search(r'\d+', info_fo.get_text())
		followee_number = int(match.group(0))
		return hash_id, followee_number

	def __verify_girl(self, text):
		info = text.find('input', {'class':'female'})
		if info.get('checked') != None:
			return True
		else:
			return False

	def get_all_followees(self):
		'''
			获取某个用户的所有关注者并置于列表, 然后返回

		'''
		url = self.people_url + self.user + '/followees'
		_xsrf = self.__get_xsrf()
		hash_id, followee_number = self.__get_argument(url)
		if  hash_id == None or \
			followee_number == None or \
			_xsrf == None:
			return
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
			msg = self.__post_site(self.fo_url, data)
			if msg == None:
				continue
			text = soup(msg, 'html.parser')
			content = text.findAll('h2', {'class':'zm-list-content-title'})
			regex = re.compile(r'(?<=people/)(.*?)(?=")')
			for each in content:
				info = re.search(regex, each.decode())
				followee = info.group(0)
				users.append(followee)
		return users

	def __self_name(self):
		html = self.session.get('http://www.zhihu.com')
		text = soup(html.text, 'html.parser')
		name = text.find('span', {'class':'name'})
		return name.get_text()

	def get_girl(self):
		'''
			获取单个账号的信息

		'''
		self.session.cookies.update(self.__load_cookies())
		url = self.people_url + self.user + '/about'
		text = self.__get_site(url)
		if text == None:
			print('info not retrieved :(')
			return
		text = soup(text, 'html.parser')
		r = self.__verify_girl(text)
		if r == False:
			return

		girl = Programmee(self.user)
		# 昵称
		content = text.find('a', {'class':'name'})
		if content != None:
			girl.name = content.get_text()

		flag = False

		# 个签
		content = text.find('span', {'class':'bio'})
		if content != None:
			girl.bio = content.get_text()
			if re.search(self.pro_re, girl.bio) != None:
				flag = True

		# 简介
		content = text.find('span', {'class':'content'})
		if content != None:
			girl.content = content.get_text().replace('填写个人简介', 'None')
			if re.search(self.pro_re, girl.content) != None:
				flag = True

		# 教育
		content = text.find('span', {'class':'education item'})
		if content != None:
			girl.education = content.get_text().replace('填写教育信息','None')
			if re.search(self.pro_re, girl.education) != None:
				flag = True

		# 教育+
		content = text.find('span', {'class':'education-extra item'})
		if content != None:
			girl.education_extra = content.get_text()
			if re.search(self.pro_re, girl.education_extra) != None:
				flag = True

		# 行业
		content = text.find('span', {'class':'business item'})
		if content != None:
			girl.business = content.get_text().replace('填写行业', 'None')
			if re.search(self.pro_re, girl.business) != None:
				flag = True

		# 职业
		content = text.find('span', {'class':'employment item'})
		if content != None:
			girl.employment = content.get_text().replace('填写公司信息','None')
			if re.search(self.pro_re, girl.employment) != None:
				flag = True

		# 职位
		content = text.find('span', {'class':'position item'})
		if content != None:
			girl.position = content.get_text().replace('填写职位', 'None')
			if re.search(self.pro_re, girl.position) != None:
				flag = True

		if flag == False:
			return None

		# 记录
		div = text.find('div', {'class':'profile-navbar clearfix'})
		content = div.decode()
		nums = re.findall(self.info_re, content)
		girl.asks = int(nums[0])
		girl.answers = int(nums[1])
		girl.collections = int(nums[3])

		div = text.find('div', {'class':'zm-profile-module-desc'})
		content = div.decode()
		nums = re.findall(self.info_re, content)
		girl.agree = int(nums[0])
		girl.thanks = int(nums[1])
		girl.favorites = int(nums[2])

		div = text.find('div',{'class':'zm-profile-side-following zg-clear'})
		content = div.decode()
		nums = re.findall(self.info_re, content)
		girl.followees = int(nums[0])
		girl.followers = int(nums[1])

		self.__save_girl(girl)
		# print(girl)
		return girl

	def __save_girl(self, girl):
		print('save ' + girl.user)
		girl.save()
