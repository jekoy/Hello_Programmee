import requests, json, time, re
from bs4 import BeautifulSoup as soup

class Follow():
	def __init__(self, user):
		self.user = user
		self.session	  = requests.session()
		# cookies 文件名称
		self.cookie_file  = 'cookies'
		self.base_url		  = 'https://www.zhihu.com'
		# 知乎用户页面
		self.people_url = 'https://www.zhihu.com/people/'
		self.follow_url = 'https://www.zhihu.com/node/MemberFollowBaseV2'
		self.session.data    = { }
		self.session.headers = {
			'User-Agent':
				'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, \
				 like Gecko) Chrome/33.0.1750.117 Safari/537.36 MyIE',
			'Host':'www.zhihu.com',
			'Origin':'https://www.zhihu.com',
			'X-Requested-With':'XMLHttpRequest'
		}

	def __load_cookies(self):
		with open(self.cookie_file, 'r') as f:
			cookies = json.load(f)
			f.close()
		return cookies

	def __get_xsrf(self):
		text = self.__get_site(self.base_url)
		if text == None:
			return None
		info = soup(text, 'html.parser').find('input', {'name': '_xsrf'})
		_xsrf = info.attrs['value']
		return _xsrf

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

	def __get_hash(self):
		text = self.__get_site(self.url)
		if text == None:
			return None
		info_hash = re.search(u'(?<=data-id=")(.*?)(?=")', text)
		hash_id = info_hash.group(0)
		return hash_id

	def follow(self):
		count = 0
		while count < 3:
			try:
				html = self.session.post(self.follow_url)
				if html.status_code == 200:
					print('follow ' + self.user)
					break
			except requests.exceptions.RequestException:
				print(html.status_code)
			count += 1
			time.sleep(3)
			print(html.status_code)

	def follow_her(self):
		self.session.cookies.update(self.__load_cookies())
		self.url = self.people_url + self.user
		hash_id = self.__get_hash()
		if hash_id == None:
			print('failed to get user hash id :(')
			return
		_xsrf = self.__get_xsrf()
		self.session.data['method'] = 'follow_member'
		self.session.data['params'] = json.dumps({'hash_id': hash_id})
		self.session.data['_xsrf']  = _xsrf
		self.session.headers['Referer'] = self.url
		self.follow()

if __name__ == '__main__':
	with open('follow', 'r') as f:
		while True:
			user = f.readline()
			if len(user) == 0:
				break
			c = Follow(user[:-1])
			c.follow_her()
			time.sleep(3)
		f.close()
