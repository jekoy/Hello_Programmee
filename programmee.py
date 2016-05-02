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
		S =  '用户名: ' + self.user + '\n'
		S += '姓名:   ' + self.name + '\n'
		S += '个签:   ' + self.bio + '\n'
		S += '简介:   ' + self.content + '\n'
		S += '教育:   ' + self.education + '\n'
		S += '教育+:  ' + self.education_extra + '\n'
		S += '行业:   ' + self.business + '\n'
		S += '公司:   ' + self.employment + '\n'
		S += '职位:   ' + self.position + '\n'
		S += '提问:   ' + str(self.asks) + '\n'
		S += '回答:   ' + str(self.answers) + '\n'
		S += '被赞同: ' + str(self.agree) + '\n'
		S += '被感谢: ' + str(self.thanks) + '\n'
		S += '被收藏: ' + str(self.favorites) + '\n'
		S += '收藏夹: ' + str(self.collections) + '\n'
		S += '关注了: ' + str(self.followees) + '\n'
		S += '关注者: ' + str(self.followers) + '\n\n\n'
		return S

	def save(self):
		with open(self.user, 'w') as f:
			f.write(str(self))
			f.close()
