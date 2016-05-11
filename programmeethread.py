from threading import Thread
from queue import Queue
from crawler import Crawler
from pybloom import BloomFilter
import time, os


class ProgrammeeThread(Thread):
	global signal
	global queue
	global bf
	def __init__(self, user):
		super().__init__()
		signal += 1
		print(signal)
		self.crawler = Crawler(user, signal)

	def run(self):
		print(self.crawler.user)
		girl = self.crawler.get_girl()
		if girl != None:
			fos = self.crawler.get_all_followees()
			if fos != None:
				for each in fos:
					if not each in bf:
						bf.add(each)
						queue.put(each)

signal =
queue = Queue()
bf = BloomFilter(capacity=100000, error_rate=0.001)

def initialize():
	global queue
	global bf
	directory = 'programmee'
	users = os.listdir(directory)
	for each in users:
		bf.add(each)
		queue.put(each)

# initialize()
# queue.put('cici')
# threads = []

t = ProgrammeeThread('zong-hua')
t.run()

while not queue.empty():
	t = ProgrammeeThread(queue.get())
	t.run()

# while not queue.empty():
# 	threads.clear()
# 	for i in range(0, 5):
# 		if queue.empty():
# 			break
# 		user = queue.get()
# 		t = ProgrammeeThread(user)
# 		threads.append(t)
# 		# print(queue.qsize())
# 		# t.run()
# 	for each in threads:
# 		each.start()
# 	for each in threads:
# 		each.join()
