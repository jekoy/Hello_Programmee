from threading import Thread
from queue import Queue
from crawler import Crawler
from pybloom import BloomFilter

class ProgremmeeThread(Thread):
	def __init__(self, queue, girl):
		super.__init__()
		self.crawler = Crawler()
		self.queue = queue
		self.girl  = girl

	def run(self):
		girl = self.crawler.get_girl(girl)
		if girl != None:
			fos = self.crawler.get_all_followees(girl.user)
			for each in fos:
				self.queue.put(each)

bf = BloomFilter(capacity=100000, error_rate=0.01)
queue = Queue()
threads = []

for i in range(0, 2):
	t = ProgremmeeThread(queue, '')
