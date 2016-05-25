from threading import Thread
from queue import Queue
from crawler import Crawler
from pybloom import BloomFilter
import time, os

class ProgrammeeThread(Thread):
	global queue
	global bf
	global f1
	global f2
	def __init__(self, user):
		super().__init__()
		self.crawler = Crawler(user)
		f1.write(user + '\n')

	def run(self):
		girl = self.crawler.get_girl()
		if girl != None:
			fos = self.crawler.get_all_followees()
			if fos != None:
				for each in fos:
					if not each in bf:
						bf.add(each)
						queue.put(each)

def initialize_bf():
	f = open('searched', 'r')
	while True:
		user = f.readline()
		if len(user) == 0:
			break
		user = user[:-1]
		bf.add(user)

def initialize_queue():
	global queue
	global bf
	directory = 'programmee'
	users = os.listdir(directory)
	for each in users:
		bf.add(each)
		queue.put(each)

if __name__ == '__main__':
	start = time.time()
	end = time.time()
	threads = []
	queue = Queue()
	bf = BloomFilter(capacity=1000000, error_rate=0.001)
	initialize_bf()
	initialize_queue()
	f1 = open('searched', 'a')
	f2 = open('qsize', 'w')
	while not queue.empty():
		threads.clear()
		for i in range(0, 5):
			if queue.empty():
				break
			user = queue.get()
			t = ProgrammeeThread(user)
			threads.append(t)
		for each in threads:
			each.start()
			time.sleep(0.2)
		for each in threads:
			each.join()
		end = time.time()
		print(queue.qsize())
		if end - start > 300:
			start = time.time()
			f2.write(str(queue.qsize()) + '\n')
