import os, re

dst = open('follow', 'w')

l = os.listdir('programmee')

os.chdir('programmee')

for each in l:
	with open(each, 'r') as f:
			while True:
				s = f.readline()
				if len(s) == 0:
					break
				if s.startswith('用户名:'):
					user = re.sub(r' |\n', '', s.split(':')[1])
				if s.startswith('关注者:'):
					follower = re.sub(r' |\n', '', s.split(':')[1])
					if int(follower) >= 500:
						dst.write(user + '\n')
			f.close()