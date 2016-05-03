import os

class Programmee():
	def __init__(self, user='None'):
		self.user            =  user
		self.name            = 'None'
		self.bio             = 'None'
		self.content         = 'None'
		self.education       = 'None'
		self.education_extra = 'None'
		self.business        = 'None'
		self.employment      = 'None'
		self.position        = 'None'
		self.asks            = 0
		self.answers         = 0
		self.agree           = 0
		self.thanks          = 0
		self.favorites       = 0
		self.collections     = 0
		self.followees       = 0
		self.followers       = 0

	def __str__(self):
		info =  '用户名: ' + self.user + '\n'
		info += '姓名:   ' + self.name + '\n'
		info += '个签:   ' + self.bio + '\n'
		info += '简介:   ' + self.content + '\n'
		info += '教育:   ' + self.education + '\n'
		info += '教育+:  ' + self.education_extra + '\n'
		info += '行业:   ' + self.business + '\n'
		info += '公司:   ' + self.employment + '\n'
		info += '职位:   ' + self.position + '\n'
		info += '提问:   ' + str(self.asks) + '\n'
		info += '回答:   ' + str(self.answers) + '\n'
		info += '被赞同: ' + str(self.agree) + '\n'
		info += '被感谢: ' + str(self.thanks) + '\n'
		info += '被收藏: ' + str(self.favorites) + '\n'
		info += '收藏夹: ' + str(self.collections) + '\n'
		info += '关注了: ' + str(self.followees) + '\n'
		info += '关注者: ' + str(self.followers) + '\n'
		return info

	def save(self):
		with open('programmee' + os.sep + self.user, 'w') as f:
			f.write(str(self))
			f.close()
